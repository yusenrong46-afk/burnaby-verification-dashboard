"""Self-contained hybrid retrieval for the bylaw chatbot — package-free.

This module is a sibling of ``streamlit_app.py`` / ``chat_brain.py`` (imported as
a bare ``import bylaw_retrieval`` under ``streamlit run``) so the chatbot's full
retrieval stack runs on the Streamlit Cloud deploy, where the ``burnaby_prototype``
package is NOT installed.

It is a faithful, dependency-light port of:
- ``burnaby_prototype.bylaw_rag.BylawIndex`` — BM25 (``rank_bm25``) + optional dense
  cosine (pure-Python) fused with Reciprocal Rank Fusion (RRF, k=60), plus parent
  section expansion. The one change: the corpus dense vectors are supplied
  PRECOMPUTED (shipped in a sidecar) so cloud never embeds the corpus at runtime,
  and the query encoder is passed per-call (so a cached index holds no API client).
- ``burnaby_prototype.native_extraction.OpenRouterEmbeddingBackend`` /
  ``OpenRouterReranker`` — pure ``urllib``+``json`` clients.

Advisory only: nothing in the verify path imports this; it never writes outputs.
``tests/test_bylaw_retrieval.py`` pins parity with ``BylawIndex``.
"""

from __future__ import annotations

import json
import math
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

RRF_K = 60  # standard reciprocal-rank-fusion constant (matches bylaw_rag.py)
DEFAULT_EMBEDDING_MODEL = "baai/bge-m3"
DEFAULT_RERANK_MODEL = "cohere/rerank-4-fast"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class RetrievalError(RuntimeError):
    """A retrieval/network call failed (kept package-free; no OpenRouterError import)."""


# --- Query expansion (verbatim from bylaw_rag.py, domain map frozen) ----------
# BM25 is synonym-blind; expansion only ADDS ranking terms, never changes meaning.
_COLLOQUIAL_SYNONYMS: dict[str, tuple[str, ...]] = {
    "tall": ("height",),
    "high": ("height",),
    "taller": ("height",),
    "big": ("floor", "area", "size"),
    "large": ("floor", "area", "size"),
    "size": ("floor", "area"),
    "far": ("setback", "distance"),
    "close": ("setback", "separation", "distance"),
    "distance": ("setback", "separation"),
    "wide": ("width",),
    "floors": ("storeys",),
    "levels": ("storeys",),
    "garage": ("parking",),
}
# Frozen snapshot of bylaw_rag._domain_expansions() (built from the verifier's
# shared UNIT_ALIASES + TEXT_RULE_OBJECT_PATTERNS) so this module needs no package.
_DOMAIN_EXPANSIONS: dict[str, tuple[str, ...]] = {
    "access": ("corridor", "fire"),
    "area": ("floor", "fsr", "gross", "lot", "ratio", "space"),
    "building": ("dwelling", "separation", "suite"),
    "cent": ("per", "percent", "percentage"),
    "corridor": ("access", "fire"),
    "coverage": ("lot",),
    "dwelling": ("building", "separation", "suite", "unit", "units"),
    "fire": ("access", "corridor"),
    "floor": ("area", "fsr", "gross", "ratio", "space"),
    "fsr": ("area", "floor", "ratio", "space"),
    "gross": ("area", "floor"),
    "height": (),
    "impervious": ("surface",),
    "lot": ("area", "coverage"),
    "m": ("meter", "meters", "metre", "metres", "sq", "sqm", "square"),
    "meter": ("m", "meters", "metre", "metres", "sq", "sqm", "square"),
    "meters": ("m", "meter", "metre", "metres", "sq", "sqm", "square"),
    "metre": ("m", "meter", "meters", "metres", "sq", "sqm", "square"),
    "metres": ("m", "meter", "meters", "metre", "sq", "sqm", "square"),
    "per": ("cent", "percent", "percentage"),
    "percent": ("cent", "per", "percentage"),
    "percentage": ("cent", "per", "percent"),
    "permitted": ("use",),
    "ratio": ("area", "floor", "fsr", "space"),
    "separation": ("building", "dwelling", "suite"),
    "setback": ("yard",),
    "space": ("area", "floor", "fsr", "ratio"),
    "sq": ("m", "meter", "meters", "metre", "metres", "sqm", "square"),
    "sqm": ("m", "meter", "meters", "metre", "metres", "sq", "square"),
    "square": ("m", "meter", "meters", "metre", "metres", "sq", "sqm"),
    "storey": ("storeys", "stories", "story"),
    "storeys": ("storey", "stories", "story"),
    "stories": ("storey", "storeys", "story"),
    "story": ("storey", "storeys", "stories"),
    "suite": ("building", "dwelling", "separation"),
    "surface": ("impervious",),
    "unit": ("dwelling", "units"),
    "units": ("dwelling", "unit"),
    "use": ("permitted",),
    "yard": ("setback",),
}


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:\.[0-9]+)*", str(text or "").lower())


def expand_query_terms(question: str) -> list[str]:
    """Return the question's tokens plus deterministic vocabulary expansions."""
    tokens = tokenize(question)
    expanded = list(tokens)
    seen = set(tokens)
    for token in tokens:
        for extra in (*_COLLOQUIAL_SYNONYMS.get(token, ()), *_DOMAIN_EXPANSIONS.get(token, ())):
            if extra not in seen:
                seen.add(extra)
                expanded.append(extra)
    return expanded


def _normalized(vector: Any) -> list[float]:
    values = [float(v) for v in vector]
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


QueryEncoder = Callable[[str], list[float]]


class HybridBylawIndex:
    """BM25 + optional precomputed-dense, fused with RRF. Package-free.

    ``corpus_vectors`` are the precomputed (un-normalized is fine) embeddings for
    each chunk, in chunk order. The dense leg only runs when both ``corpus_vectors``
    were supplied at build time AND a ``query_encoder`` is passed at query time —
    so the built index holds no API client and is safe to cache across sessions.
    """

    def __init__(self, chunks: list[dict[str, Any]], *, corpus_vectors: list[list[float]] | None = None) -> None:
        self.chunks = list(chunks)
        self._token_sets = [set(tokenize(chunk["text"])) for chunk in self.chunks]
        self._bm25 = None
        if self.chunks:
            try:
                from rank_bm25 import BM25Okapi

                self._bm25 = BM25Okapi([tokenize(chunk["text"]) for chunk in self.chunks])
            except Exception:
                self._bm25 = None  # BM25 unavailable -> dense-only / empty; never crash
        self._dense_vectors: list[list[float]] | None = None
        if corpus_vectors and self.chunks and len(corpus_vectors) == len(self.chunks):
            try:
                self._dense_vectors = [_normalized(v) for v in corpus_vectors]
            except Exception:
                self._dense_vectors = None

    @property
    def has_dense(self) -> bool:
        return self._dense_vectors is not None

    def _bm25_ranks(self, question: str) -> dict[int, int]:
        if self._bm25 is None:
            return {}
        query_tokens = expand_query_terms(question)
        scores = self._bm25.get_scores(query_tokens)
        query_set = set(query_tokens)
        # Eligibility by token OVERLAP (not score>0): on tiny corpora BM25's IDF can
        # go negative for common terms and silently drop genuine matches.
        eligible = [index for index, tokens in enumerate(self._token_sets) if tokens & query_set]
        order = sorted(eligible, key=lambda i: (-scores[i], str(self.chunks[i]["chunk_id"])))
        return {index: rank + 1 for rank, index in enumerate(order)}

    def _dense_ranks(self, question: str, query_encoder: QueryEncoder | None) -> dict[int, int] | None:
        if self._dense_vectors is None or query_encoder is None:
            return None
        try:
            query = _normalized(query_encoder(question))
        except Exception:
            return None
        sims = [sum(q * d for q, d in zip(query, vector)) for vector in self._dense_vectors]
        order = sorted(range(len(sims)), key=lambda i: (-sims[i], str(self.chunks[i]["chunk_id"])))
        return {index: rank + 1 for rank, index in enumerate(order)}

    def search(self, question: str, *, top_k: int = 5, query_encoder: QueryEncoder | None = None) -> list[dict[str, Any]]:
        """Top-k chunks with RRF-fused scores and per-signal ranks."""
        if not self.chunks:
            return []
        bm25_rank = self._bm25_ranks(question)
        dense_rank = self._dense_ranks(question, query_encoder)
        fused: list[tuple[float, dict[str, Any], dict[str, Any]]] = []
        for index, chunk in enumerate(self.chunks):
            score = 0.0
            signals: dict[str, Any] = {}
            if index in bm25_rank:
                score += 1.0 / (RRF_K + bm25_rank[index])
                signals["bm25_rank"] = bm25_rank[index]
            if dense_rank is not None and index in dense_rank:
                score += 1.0 / (RRF_K + dense_rank[index])
                signals["dense_rank"] = dense_rank[index]
            if score > 0.0:
                fused.append((score, chunk, signals))
        fused.sort(key=lambda item: (-item[0], str(item[1]["chunk_id"])))
        return [
            {**chunk, "score": round(score, 6), "signals": signals}
            for score, chunk, signals in fused[:top_k]
        ]

    def ask(self, question: str, *, top_k: int = 5, query_encoder: QueryEncoder | None = None) -> list[dict[str, Any]]:
        """search() + parent-section expansion: full legal context per hit."""
        hits = self.search(question, top_k=top_k, query_encoder=query_encoder)
        by_section: dict[str, list[dict[str, Any]]] = {}
        for chunk in self.chunks:
            if chunk.get("section"):
                by_section.setdefault(chunk["section"], []).append(chunk)
        results = []
        for hit in hits:
            section = hit.get("section") or ""
            siblings = by_section.get(section, [])
            expanded = "\n".join(sib["text"] for sib in siblings) if len(siblings) > 1 else hit["text"]
            results.append({**hit, "section_text": expanded})
        return results


def load_index(index_path: Any, vectors_path: Any | None = None) -> HybridBylawIndex:
    """Build a HybridBylawIndex from a chunks JSON + an optional vectors sidecar."""
    payload = json.loads(Path(index_path).read_text(encoding="utf-8"))
    chunks = payload.get("chunks", [])
    vectors = payload.get("vectors")
    if vectors is None and vectors_path is None:
        sidecar = Path(index_path).with_name("bylaw_rag_vectors.json")
        if sidecar.exists():
            vectors_path = sidecar
    if vectors is None and vectors_path is not None and Path(vectors_path).exists():
        try:
            vectors = json.loads(Path(vectors_path).read_text(encoding="utf-8")).get("vectors")
        except Exception:
            vectors = None
    return HybridBylawIndex(chunks, corpus_vectors=vectors)


# --- Vendored OpenRouter clients (pure urllib+json) ---------------------------

def _pack_rerank_text(pack: dict[str, Any]) -> str:
    return f"section: {pack.get('section')}\npage: {pack.get('page')}\ntext: {pack.get('source_text')}"


class OpenRouterEmbeddings:
    """Embedding client matching the ``encode(list[str]) -> list[list[float]]`` contract."""

    def __init__(
        self,
        api_key: str,
        *,
        model: str = DEFAULT_EMBEDDING_MODEL,
        base_url: str = OPENROUTER_BASE_URL,
        batch_size: int = 96,
        timeout: int = 90,
    ) -> None:
        if not api_key:
            raise RetrievalError("OPENROUTER_API_KEY is required for embeddings")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.batch_size = batch_size
        self.timeout = timeout

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            payload = self._post_json("/embeddings", {"model": self.model, "input": batch})
            rows = payload.get("data") or []
            rows = sorted(rows, key=lambda row: int(row.get("index", 0)))
            vectors.extend([[float(v) for v in row.get("embedding", [])] for row in rows])
        if len(vectors) != len(texts):
            raise RetrievalError("embedding response count did not match input count")
        return vectors

    def _post_json(self, endpoint: str, body: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{self.base_url}{endpoint}",
            data=json.dumps(body).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:800]
            raise RetrievalError(f"OpenRouter embedding HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise RetrievalError(f"OpenRouter embedding request failed: {exc}") from exc


class OpenRouterRerank:
    """Optional cross-encoder reranker for retrieved packs."""

    def __init__(
        self,
        api_key: str,
        *,
        model: str = DEFAULT_RERANK_MODEL,
        base_url: str = OPENROUTER_BASE_URL,
        timeout: int = 90,
    ) -> None:
        if not api_key:
            raise RetrievalError("OPENROUTER_API_KEY is required for rerank")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def rerank(self, query: str, packs: list[dict[str, Any]], *, top_n: int) -> list[dict[str, Any]]:
        if not packs:
            return []
        body = {
            "model": self.model,
            "query": query,
            "documents": [{"text": _pack_rerank_text(pack)} for pack in packs],
            "top_n": min(top_n, len(packs)),
        }
        request = urllib.request.Request(
            f"{self.base_url}/rerank",
            data=json.dumps(body).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:800]
            raise RetrievalError(f"OpenRouter rerank HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise RetrievalError(f"OpenRouter rerank request failed: {exc}") from exc
        ranked = []
        for result in payload.get("results", []):
            index = int(result.get("index", -1))
            if 0 <= index < len(packs):
                pack = dict(packs[index])
                pack["rerank_score"] = result.get("relevance_score")
                ranked.append(pack)
        return ranked
