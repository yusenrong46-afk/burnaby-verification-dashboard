"""Streamlit dashboard for Burnaby verifier outputs."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

# Streamlit is imported inside main() (so the module stays import-safe and `st` is
# injected for testability). For module-level CACHE DECORATORS we also grab a
# reference here; when Streamlit is unavailable the shim degrades to a no-op so
# the module still imports (e.g. headless tests). Streamlit re-executes the script
# every rerun, so plain module dicts won't persist — st.cache_* is the right tool.
try:  # pragma: no cover - streamlit present in every real run target
    import streamlit as _ST
except Exception:  # pragma: no cover
    _ST = None


def _cache_data(**kwargs: Any):
    if _ST is not None:
        return _ST.cache_data(**kwargs)
    return lambda fn: fn


ROOT = Path(__file__).resolve().parents[1]


def _load_dotenv(path: Path) -> None:
    """Load ``KEY=VALUE`` pairs from a local ``.env`` into ``os.environ``.

    The verifier's extraction layer reads ``OPENROUTER_API_KEY`` from ``.env``;
    the dashboard's bylaw chatbot reuses the SAME key so the chat works out of
    the box locally with no extra setup. Never overrides an already-set
    environment variable or a Streamlit secret, and never raises.
    """
    try:
        if not path.exists():
            return
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, _, value = stripped.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:  # pragma: no cover - dotenv loading must never break the app
        pass


_load_dotenv(ROOT / ".env")

# Default chat model for the bylaw assistant when OpenRouter is the provider.
# google/gemini-3.1-flash-lite is fast, cheap, and confirmed available on
# OpenRouter; override with the BYLAW_RAG_MODEL secret/env var.
DEFAULT_BYLAW_CHAT_MODEL = "google/gemini-3.1-flash-lite"

OUTPUTS_ROOT = ROOT / "outputs"
OUTPUT_DIR_SUFFIX = "_slim_pipeline5_registry"
NATIVE_RUN_ROOTS = ("m7_runs", "v3_runs", "v2_runs")
NATIVE_RUN_LABELS = {"m7_runs": "M7", "v3_runs": "V3", "v2_runs": "V2"}
PRODUCT_RUN_ROOTS = ("m7_runs", "v3_runs")
# Pipeline 9 (graph-RAG extraction) verifier outputs sit next to the P5
# registries as <city>_p9/. Same verifier, second upstream — the dashboard
# treats them as another selectable "city" so reviewers see the P9 lane.
P9_DIR_SUFFIX = "_p9"
DEFAULT_OUTPUT_DIR = OUTPUTS_ROOT / "m7_runs" / "burnaby_r1" / "google_gemini_3_1_flash_lite"
MVP_REPORT_PATH = OUTPUTS_ROOT / "mvp_verification" / "mvp_report.json"
M4_SOURCE_AUDIT_PATH = OUTPUTS_ROOT / "topdown_validation" / "m4_source_pdf_audit.json"
REFERENCE_DIR_SUFFIXES = (
    OUTPUT_DIR_SUFFIX,
    f"{OUTPUT_DIR_SUFFIX}_v21",
    P9_DIR_SUFFIX,
    f"{P9_DIR_SUFFIX}_v21",
)
SOURCE_DOCUMENT_URL = "https://www.burnaby.ca/sites/default/files/acquiadam/2024-07/R1Small-Scale-Multi-Unit-Housing-District.pdf"
SOURCE_DOCUMENT_URLS = {
    "burnaby_r1": SOURCE_DOCUMENT_URL,
    "calgary_rcg": "https://www.calgary.ca/content/dam/www/pda/pd/documents/calgary-land-use-bylaw-1p2007/land-use-bylaw-1p2007.pdf",
    "vancouver_rs": "https://former.vancouver.ca/commsvcs/BYLAWS/zoning/sec11.pdf",
}

# Color semantics used across the whole dashboard. Presentation only.
STATUS_COLORS = {
    "verified": "#1a7f37",
    "review": "#9a6700",
    "rejected": "#cf222e",
    "not_used": "#57606a",
}

# Active source-document URL for the selected city (module-level so the
# many detail panels stay simple). Falls back to the Burnaby PDF.
_ACTIVE_SOURCE = {"url": SOURCE_DOCUMENT_URL, "label": "source bylaw PDF"}


PLAIN_LABELS = {
    "verified": "Verified",
    "review": "Needs review",
    "review_needed": "Needs review",
    "rejected": "Rejected",
    "not_used": "Not used",
    "human_legal_review": "Needs legal review",
    "operator_review": "Check direction words",
    "rerun_with_evidence_bundle": "Try stronger evidence",
    "retry_with_better_evidence": "Try stronger evidence",
    "condition_evidence_needed": "Find condition evidence",
    "scope_review": "Check legal scope",
    "semantic_guardrail_review": "Meaning looks close, but support is missing",
    "semantic_duplicate_review": "Possible duplicate",
    "fix_candidate_or_rule_family_mapping": "Fix extracted rule type",
    "defer_low_priority": "Lower priority",
    "missing_applies_to": "Missing what the rule applies to",
    "missing_condition_evidence": "Missing condition evidence",
    "missing_scope_evidence": "Missing scope evidence",
    "general_review": "General review",
    "operator_uncertain": "Direction word is unclear",
    "near_verified_table_context": "Near verified table wording",
    "text_candidate_needs_consensus": "Only one text source supports it",
    "unresolved_exception": "Possible exception or qualifier",
    "possible_rule_object_mismatch": "Possible wrong rule type",
    "upstream_review_requested": "Extractor asked for review",
    "plausible": "Plausible",
    "likely_correct": "Likely correct",
    "weak": "Weak support",
    "likely_wrong_or_noise": "Likely wrong or noise",
    "guardrail_blocked_low_similarity": "Not close enough to verified rules",
    "high_confidence_near_duplicate": "Likely duplicate",
    "close_semantic_match": "Close meaning match",
    "no_close_semantic_match": "No close meaning match",
    "operator_not_supported": "Direction word not proven",
    "scope_not_supported": "Scope not proven",
    "applies_to_not_supported": "Applies-to text not proven",
    "condition_not_supported": "Condition not proven",
    "unit_not_supported": "Unit not proven",
    "value_not_supported": "Number not proven",
    "rule_object_not_supported": "Rule type not proven",
    "rag_context_mismatch": "Extractor text did not match the source page",
    "pass": "Pass",
    "fail-closed": "Fail-closed",
    "scope mismatch": "Scope mismatch",
    "unsafe / needs fix": "Unsafe / needs fix",
    "needs review": "Needs review",
    "missing": "Missing",
    "mvp_safety_ready": "Safety ready",
    "native_m7": "Native M7",
    "native_v3": "Native V3",
    "native_v2": "Native V2",
    "legacy_p5": "Pipeline 5 reference",
    "legacy_p9": "Pipeline 9 reference",
    "legacy_internal_registry": "Internal registry reference",
    "burnaby_r1": "Burnaby R1",
    "vancouver_rs": "Vancouver RS",
    "calgary_rcg": "Calgary RCG",
}


HELP_TEXT = {
    "human_legal_review": "The evidence may be real, but the rule depends on legal interpretation, an exception, or a condition that the verifier should not guess.",
    "operator_review": "The number is present, but the source text does not safely prove whether it is a minimum, maximum, or exact requirement.",
    "rerun_with_evidence_bundle": "There may be enough source text if several nearby evidence snippets are combined, but it still must pass the deterministic verifier.",
    "retry_with_better_evidence": "The candidate may be correct, but the current evidence packet is too weak. Find a stronger source passage first.",
    "condition_evidence_needed": "The candidate depends on a condition, qualifier, exception, or branch that needs explicit source support.",
    "scope_review": "The candidate may use the right number but for the wrong legal scope, object, or building type.",
    "semantic_guardrail_review": "The meaning resembles a verified rule, but similarity is advisory only and cannot approve it.",
    "semantic_duplicate_review": "This may already be covered by a verified rule. Check before adding another rule.",
    "fix_candidate_or_rule_family_mapping": "The extractor likely assigned the wrong rule family, such as treating a definition as a numeric zoning rule.",
    "defer_low_priority": "This item is probably outside the current numeric verification contract or has weak support.",
    "fail-closed": "The verifier avoided unsafe approvals, but too many true rules may still be stuck in review.",
    "scope mismatch": "The extractor produced many candidates outside the verifier's current numeric zoning contract.",
    "unsafe / needs fix": "At least one false verified rule or false approval was found. Treat this output as unsafe until fixed.",
    "pass": "The benchmark gates passed for the current contract.",
    "native_m7": "Current native exhaustive extraction path. RAG finds evidence; deterministic verification still decides.",
    "native_v3": "Previous native extraction reference. Kept for comparison.",
    "native_v2": "Older native extraction reference. Kept for comparison.",
    "legacy_p5": "Legacy structured-registry reference. Kept for comparison, not the current product path.",
    "legacy_p9": "Legacy graph-RAG reference. Kept for comparison, not the current product path.",
}


RAW_VALUE_COLUMNS = {
    "rule_id",
    "source_rule_id",
    "matched_verified",
    "semantic_match",
    "evidence_id",
    "current_evidence",
    "best_evidence",
    "original_evidence",
    "retry_evidence",
    "bundle_ids",
    "file",
    "path",
    "url",
    "quote",
    "evidence",
    "source_window",
    "value",
    "unit",
    "score",
    "confidence",
    "count",
    "rows",
}

# Retrieval depth for the bylaw chatbot. The grounded LLM only sees what is
# retrieved, so too-shallow retrieval makes it answer "the sections do not say"
# even when the bylaw does. Modern chat models (the OpenRouter default has a 1M
# context window) easily absorb a generous, section-grounded context, so we
# retrieve broadly and let the model find the relevant clause.
RAG_CHAT_TOP_K = 8
# Two-stage retrieval: BM25/RRF is recall-oriented but its ordering buries the
# decisive clause among many same-topic sections (e.g. the canonical R-CG height
# question puts the 11.0 m clause §541(1) at ~rank 24 behind a dozen other
# "building height" hits). So we retrieve a BROAD candidate set and, when an
# OpenRouter key is available, rerank the shortlist with a cross-encoder
# (cohere/rerank-4-fast) down to RAG_CHAT_TOP_K. No key / any rerank error falls
# back to the BM25/RRF order — never raises, never starves the LLM context.
RAG_RERANK_CANDIDATES = 30
RAG_CONTEXT_CHAR_LIMIT = 18000
RAG_CONTEXT_PER_HIT_LIMIT = 2400

RAG_QUERY_SYNONYMS = {
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


def native_run_root(output_dir: Path) -> str | None:
    """Return m7_runs/v3_runs/v2_runs for a native model output dir."""
    try:
        root = output_dir.parent.parent.name
    except IndexError:
        return None
    return root if root in NATIVE_RUN_ROOTS else None


def m55_run_id(output_dir: Path) -> str:
    try:
        if output_dir.parent.parent.name == "m7_measure":
            return output_dir.parent.name
    except IndexError:
        return ""
    return ""


def native_lane_for_dir(output_dir: Path) -> str | None:
    root = native_run_root(output_dir)
    if root is None:
        return None
    return f"native_{NATIVE_RUN_LABELS[root].lower()}"


def native_label_for_dir(output_dir: Path) -> str:
    root = native_run_root(output_dir)
    return NATIVE_RUN_LABELS.get(str(root), "Native")


def preferred_reference_dir(stem: str, suffix: str, outputs_root: Path | None = None) -> Path:
    """Prefer refreshed v21 reference artifacts, then fall back to old names."""
    outputs_root = outputs_root or OUTPUTS_ROOT
    versioned = outputs_root / f"{stem}{suffix}_v21"
    if versioned.exists():
        return versioned
    return outputs_root / f"{stem}{suffix}"


def discover_city_output_dirs(outputs_root: Path = OUTPUTS_ROOT) -> list[Path]:
    """Return city output dirs that contain verified_rules.json, sorted by name.

    Any new city (e.g. calgary) appears automatically once its
    `<city>_..._slim_pipeline5_registry/verified_rules.json` exists on disk.
    """
    if not outputs_root.is_dir():
        return []
    standard = [
        path
        for path in outputs_root.iterdir()
        if path.is_dir()
        and path.name.endswith(REFERENCE_DIR_SUFFIXES)
        and (path / "verified_rules.json").exists()
    ]
    native_runs = []
    for root_name in NATIVE_RUN_ROOTS:
        native_root = outputs_root / root_name
        if not native_root.is_dir():
            continue
        for city_dir in native_root.iterdir():
            if not city_dir.is_dir():
                continue
            for model_dir in city_dir.iterdir():
                if model_dir.is_dir() and (model_dir / "verified_rules.json").exists():
                    native_runs.append(model_dir)
    m55_runs = []
    m55_root = outputs_root / "m7_measure"
    if m55_root.is_dir():
        for run_dir in m55_root.iterdir():
            if not run_dir.is_dir():
                continue
            for city_dir in run_dir.iterdir():
                if city_dir.is_dir() and (city_dir / "verified_rules.json").exists():
                    m55_runs.append(city_dir)
    return sorted([*standard, *native_runs, *m55_runs], key=lambda path: str(path))


def discover_product_output_dirs(outputs_root: Path = OUTPUTS_ROOT) -> list[Path]:
    """Return only the demo product path and its direct predecessor.

    The workspace keeps V2/P5/P9 artifacts for audit and regression work, but
    the final dashboard selector should stay focused: current M7 plus the V3
    run it was built from.
    """
    if not outputs_root.is_dir():
        return []
    product_runs = []
    for root_name in PRODUCT_RUN_ROOTS:
        native_root = outputs_root / root_name
        if not native_root.is_dir():
            continue
        for city_dir in native_root.iterdir():
            if not city_dir.is_dir():
                continue
            # Model-agnostic: pick the newest model dir present per city (the M7
            # default is google_gemini_3_1_flash_lite; '3_1' sorts after '2_5').
            # Hardcoding the 2.5 slug here was a rename miss that hid the M7 product.
            model_dirs = sorted(
                (md for md in city_dir.iterdir() if md.is_dir() and (md / "verified_rules.json").exists()),
                key=lambda md: md.name,
                reverse=True,
            )
            if model_dirs:
                product_runs.append(model_dirs[0])
    order = {root: index for index, root in enumerate(PRODUCT_RUN_ROOTS)}
    return sorted(product_runs, key=lambda path: (order.get(path.parent.parent.name, 99), city_stem_from_dir(path)))


def city_key_from_dir(output_dir: Path) -> str:
    """Return the city prefix for an output dir, e.g. burnaby_r1_... -> burnaby."""
    if m55_run_id(output_dir):
        return output_dir.name.split("_")[0].lower()
    if native_run_root(output_dir):
        return output_dir.parent.name.split("_")[0].lower()
    return output_dir.name.split("_")[0].lower()


def city_stem_from_dir(output_dir: Path) -> str:
    """Return the full city stem, e.g. burnaby_r1_slim_pipeline5_registry ->
    burnaby_r1 and vancouver_rs_p9 -> vancouver_rs.

    The short ``city_key`` ('burnaby') is right for centroids and labels but
    WRONG for artifact paths — every on-disk artifact uses the full stem
    ('burnaby_r1'), which is why path lookups must come through here.
    """
    name = output_dir.name
    if m55_run_id(output_dir):
        return name
    if native_run_root(output_dir):
        return output_dir.parent.name
    for suffix in (f"{OUTPUT_DIR_SUFFIX}_v21", OUTPUT_DIR_SUFFIX, f"{P9_DIR_SUFFIX}_v21", P9_DIR_SUFFIX):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def bylaw_index_path(output_dir: Path) -> Path | None:
    """Resolve the bylaw-RAG index for an output dir.

    A P5 registry carries its own index; a P9 run borrows the sibling P5
    registry's index for the SAME city stem (same bylaw corpus). Previously
    this path was built from the short city_key, which never matched a real
    directory — the legal-context expander silently rendered nothing.
    """
    own = output_dir / "bylaw_rag_index.json"
    if own.exists():
        return own
    sibling = OUTPUTS_ROOT / f"{city_stem_from_dir(output_dir)}{OUTPUT_DIR_SUFFIX}" / "bylaw_rag_index.json"
    if sibling.exists():
        return sibling
    source_corpus = ROOT / "benchmark" / "source_corpus" / city_stem_from_dir(output_dir) / "rag_index.json"
    if source_corpus.exists():
        return source_corpus
    return None


def city_label_from_dir(output_dir: Path) -> str:
    """Human-readable label for the sidebar selector, e.g. 'Burnaby R1'."""
    run_id = m55_run_id(output_dir)
    if run_id:
        stem = city_stem_from_dir(output_dir)
        parts = [part for part in stem.split("_") if part]
        base = parts[0].capitalize() + (" " + " ".join(part.upper() for part in parts[1:]) if parts[1:] else "")
        if run_id.startswith("m7"):
            label = "M7"
        elif run_id.startswith(("m56", "m6")):
            label = "M6"
        else:
            label = "M5.5"
        return f"{label} {run_id} — {base}"
    native_root = native_run_root(output_dir)
    if native_root:
        stem = city_stem_from_dir(output_dir)
        parts = [part for part in stem.split("_") if part]
        base = parts[0].capitalize() + (" " + " ".join(part.upper() for part in parts[1:]) if parts[1:] else "")
        if native_root == "m7_runs":
            return f"Current M7 \u2014 {base}"
        if native_root == "v3_runs":
            return f"Previous V3 \u2014 {base}"
        return f"{NATIVE_RUN_LABELS[native_root]} reference \u2014 {base}"
    is_p9 = output_dir.name.endswith(P9_DIR_SUFFIX) or output_dir.name.endswith(f"{P9_DIR_SUFFIX}_v21")
    stem = city_stem_from_dir(output_dir)
    parts = [part for part in stem.split("_") if part]
    if not parts:
        return output_dir.name
    label = parts[0].capitalize() + (" " + " ".join(part.upper() for part in parts[1:]) if parts[1:] else "")
    return f"{label} — Pipeline 9" if is_p9 else label


def source_document_url_for_output(output_dir: Path, data: dict[str, Any]) -> str:
    """Return the best source-PDF URL for the selected city output."""
    _ = data
    return SOURCE_DOCUMENT_URLS.get(city_stem_from_dir(output_dir), SOURCE_DOCUMENT_URL)


def load_output_data(output_dir: Path) -> dict[str, Any]:
    """Load all dashboard source files from one verifier output directory."""
    # The dashboard is intentionally read-only. It consumes generated JSON
    # reports and never calls Gemini, reruns verification, or mutates outputs.
    return {
        "output_dir": output_dir,
        "validation": _read_json(output_dir / "validation_report.json", {}),
        "benchmark": _read_json(output_dir / "benchmark_report.json", {}),
        "intelligence": _read_json(output_dir / "evidence_intelligence.json", {"items": [], "summary": {}}),
        "repair": _read_json(output_dir / "evidence_repair_suggestions.json", {"suggestions": []}),
        "rerun": _read_json(output_dir / "evidence_rerun_report.json", {"attempts": [], "verified_after_rerun": []}),
        "bundle_rerun": _read_json(output_dir / "evidence_bundle_rerun_report.json", {"attempts": [], "promotion_ready": []}),
        "safe_tuning": _read_json(output_dir / "safe_verifier_tuning_candidates.json", {"items": [], "candidate_count": 0}),
        "router": _read_json(output_dir / "review_router.json", {"items": [], "summary": {}}),
        "resolution": _read_json(output_dir / "review_resolution.json", {"items": [], "summary": {}}),
        "rule_graph": _read_json(output_dir / "rule_graph.json", {"nodes": [], "edges": [], "summary": {}}),
        "semantic": _read_json(output_dir / "semantic_review_report.json", {"items": [], "summary": {}}),
        "bundle_promotion": _read_json(output_dir / "bundle_promotion_report.json", {"promoted_rules": []}),
        "source_repair": _read_json(output_dir / "source_repair_report.json", {"items": [], "status_counts": {}}),
        "review_assistant_packets": _read_json(output_dir / "review_assistant_packets.json", {"items": []}),
        "coverage_report": _read_json(output_dir / "coverage_report.json", {}),
        "rule_slot_ledger": _read_json(output_dir / "rule_slot_ledger.json", {}),
        "slot_audit": _read_json(output_dir / "slot_audit.json", {}),
        "m55_reconciliation": _read_json(output_dir / "m4_m55_reconciliation.json", {}),
        "evidence_units": _read_json(output_dir / "evidence_units.json", []),
        "verified": _read_json(output_dir / "verified_rules.json", []),
        "review": _read_json(output_dir / "review_needed.json", []),
        "rejected": _read_json(output_dir / "rejected_rules.json", []),
        "not_used": _read_json(output_dir / "not_used.json", []),
        "rule_candidates": _read_json(output_dir / "rule_candidates.json", []),
        "preflight": _read_json(output_dir / "pipeline5_extraction_preflight.json", {}),
        "model_cost": _read_json(output_dir / "model_cost_report.json", {}),
        "source_summary": _read_json(output_dir / "source_summary.json", {}),
        "examiner": _read_json(output_dir / "llm_examiner_report.json", {}),
        "examiner_suggestions": _read_json(output_dir / "llm_examiner_suggestions.json", {"items": []}),
        "examiner_rerun": _read_json(output_dir / "llm_examiner_rerun_plan.json", {"actions": []}),
    }


def output_bucket_counts(data: dict[str, Any]) -> dict[str, int]:
    """KPI bucket counts that match the lists the dashboard actually renders.

    The triage tables, matrix and funnel are built from the loaded bucket lists
    (verified_rules.json, review_needed.json, ...), so the KPI must count THOSE
    lists. A validation_report.json ``bucket_counts`` can drift out of sync with
    the on-disk artifacts; using it as the headline let the "Needs review" KPI
    disagree with the review table beneath it. The validation counts are now only
    a fallback for a bucket whose list was not loaded at all.
    """
    validation_counts = ((data.get("validation") or {}).get("bucket_counts") or {})
    live = {
        "verified": data.get("verified"),
        "review_needed": data.get("review"),
        "rejected": data.get("rejected"),
        "not_used": data.get("not_used"),
    }
    counts = {
        bucket: len(items) if isinstance(items, list) else int(validation_counts.get(bucket) or 0)
        for bucket, items in live.items()
    }
    # UI code historically used both names. Keep the canonical artifact bucket
    # (`review_needed`) and the shorter display alias (`review`) in sync.
    counts["review"] = counts.get("review_needed", 0)
    return counts


# Funnel stage semantics. FIELD_GAPS are per-field proof failures (the words,
# number, unit, or direction could not be grounded in the cited evidence);
# POLICY_GAPS hold a fully-proven rule for a human by policy. A review rule
# with any FIELD_GAP dies at the "fields proven" stage; one held only by
# POLICY_GAPS is a parking lot, not a loss — the funnel renders it as "held".
FIELD_GAPS = frozenset(
    {
        "value_not_found_in_evidence",
        "unit_not_found_in_evidence",
        "operator_not_supported",
        "applies_to_not_supported",
        "constraint_scope_not_supported",
        "rule_object_not_supported",
        "rule_object_not_canonical",
        "rule_object_unit_not_compatible",
        "non_numeric_value_for_numeric_rule",
        "text_condition_not_supported",
        "table_applies_to_not_supported",
        "table_condition_not_supported",
        "table_rule_object_not_supported",
        "table_operator_refuted",
        "rule_family_direction_mismatch",
        "cross_family_value_collision",
        "source_evidence_id_not_found",
    }
)
POLICY_GAPS = frozenset(
    {
        "pipeline5_text_candidate_requires_review",
        "table_cell_candidate_requires_review",
        "table_evidence_candidate_requires_review",
        "table_fallback_candidate_requires_review",
        "table_column_not_target_scope",
        "unresolved_exception_cue",
        "allowance_trigger_threshold",
        "upstream_extraction_requested_review",
    }
)


def _gap_codes(rule: dict[str, Any]) -> list[str]:
    gaps = rule.get("support_gaps")
    if not gaps:
        gaps = rule.get("review_reasons") or []
    return [str(gap) for gap in gaps]


def _top_reasons(
    rules: list[dict[str, Any]],
    limit: int = 3,
    only: frozenset[str] | None = None,
) -> list[tuple[str, int]]:
    # ``only`` scopes the story to the gate being explained: a review rule
    # carries BOTH field and policy gaps, and each stage should show its own.
    counts = Counter(
        code
        for rule in rules
        for code in _gap_codes(rule)
        if only is None or code in only
    )
    return [(_plain_label(code), count) for code, count in counts.most_common(limit)]


def funnel_stages(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Candidate -> verified funnel rows. Pure data; rendering happens later.

    Stages: extracted -> inside verification scope (- not_used) -> evidence-backed
    (- rejected) -> fields proven (- review rules with FIELD_GAPS) ->
    verified (- review rules held by policy only). Counts reconcile with the
    bucket files by construction; if the candidate file is missing the first
    stage falls back to the bucket sum so the funnel never lies.
    """
    verified = data.get("verified") or []
    review = data.get("review") or []
    rejected = data.get("rejected") or []
    not_used = data.get("not_used") or []
    bucket_total = len(verified) + len(review) + len(rejected) + len(not_used)
    candidates = data.get("rule_candidates") or []
    total = len(candidates) or bucket_total

    field_held = [rule for rule in review if set(_gap_codes(rule)) & FIELD_GAPS]
    policy_held = [rule for rule in review if not (set(_gap_codes(rule)) & FIELD_GAPS)]

    stages = [
        {
            "stage": "extracted",
            "label": "Candidates extracted",
            "count": total,
            "dropped": 0,
            "outflow_status": "",
            "top_reasons": [],
        },
        {
            "stage": "in_contract",
            "label": "Inside verification scope",
            "count": total - len(not_used),
            "dropped": len(not_used),
            "outflow_status": "not_used",
            "top_reasons": _top_reasons(not_used),
        },
        {
            "stage": "evidence_backed",
            "label": "Evidence-backed (not contradicted)",
            "count": total - len(not_used) - len(rejected),
            "dropped": len(rejected),
            "outflow_status": "rejected",
            "top_reasons": _top_reasons(rejected, only=FIELD_GAPS),
        },
        {
            "stage": "fields_proven",
            "label": "Every field proven",
            "count": len(verified) + len(policy_held),
            "dropped": len(field_held),
            "outflow_status": "review",
            "top_reasons": _top_reasons(field_held, only=FIELD_GAPS),
        },
        {
            "stage": "verified",
            "label": "Verified",
            "count": len(verified),
            "dropped": len(policy_held),
            "outflow_status": "held",
            "top_reasons": _top_reasons(policy_held, only=POLICY_GAPS),
        },
    ]
    if total != bucket_total and candidates:
        stages[0]["note"] = (
            f"{total} extracted candidates vs {bucket_total} decided rules — "
            "some candidates merge before decision."
        )
    return stages


MATRIX_COLUMNS: list[tuple[str, str]] = [
    ("rowhouse", "Rowhouse (1\u20133 units)"),
    ("ssmu_1_2", "SSMU 1\u20132 units"),
    ("ssmu_3_4", "SSMU 3\u20134 units"),
    ("ssmu_5_6_ftn", "SSMU 5\u20136 units (FTN only)"),
]

_FOOTNOTE_SUFFIX_RE = re.compile(r"\s*\.\d+\s*$")


def gold_path_for(output_dir: Path, root: Path = ROOT) -> Path | None:
    """Gold rules file for an output dir's city stem, or None."""
    path = root / "benchmark" / "gold" / f"{city_stem_from_dir(output_dir)}_gold_rules.json"
    return path if path.exists() else None


def applicability_buckets(rule: dict[str, Any]) -> set[str]:
    """Map a rule onto the Burnaby 101.4 matrix columns.

    Prefers the verifier's structured ``applicability`` block (selectors with
    dwelling_type + unit_range); degrades to text-parsing applies_to/condition
    for rules that predate it. A rule with no dwelling-type signal spans ALL
    columns — that is how 101.4 actually reads (building-scoped rows like the
    setbacks apply to every dwelling-type column).
    """
    buckets: set[str] = set()
    block = rule.get("applicability") or {}
    for selector in block.get("selectors") or []:
        dwelling = selector.get("dwelling_type")
        unit_range = selector.get("unit_range") or {}
        low, high = unit_range.get("min"), unit_range.get("max")
        exact = unit_range.get("exact")
        if dwelling == "rowhouse":
            buckets.add("rowhouse")
        elif dwelling == "small_scale_multi_unit" or low is not None or exact is not None:
            if (low, high) == (1, 2):
                buckets.add("ssmu_1_2")
            elif (low, high) == (3, 4) or exact in (3, 4):
                buckets.add("ssmu_3_4")
            elif (low, high) == (5, 6) or exact in (5, 6):
                buckets.add("ssmu_5_6_ftn")
            elif exact in (1, 2):
                buckets.add("ssmu_1_2")
            elif dwelling:
                buckets.update({"ssmu_1_2", "ssmu_3_4", "ssmu_5_6_ftn"})
    if buckets:
        return buckets

    text = _FOOTNOTE_SUFFIX_RE.sub("", f"{rule.get('applies_to') or ''}; {rule.get('condition') or ''}").lower()
    if "rowhouse" in text:
        buckets.add("rowhouse")
    if "1 to 2" in text:
        buckets.add("ssmu_1_2")
    if "3 to 4" in text:
        buckets.add("ssmu_3_4")
    if "5 to 6" in text or "frequent transit" in text or "ftn" in text:
        buckets.add("ssmu_5_6_ftn")
    if buckets:
        return buckets
    return {key for key, _ in MATRIX_COLUMNS}


def _matrix_row_key(rule: dict[str, Any]) -> tuple[str, str]:
    family = str(rule.get("rule_object") or "")
    scope = str(rule.get("constraint_scope") or "")
    text = f"{rule.get('applies_to') or ''} {rule.get('condition') or ''}".lower()
    qualifier = ""
    if family in {"height", "storeys"}:
        for role in ("front", "rear", "accessory"):
            if role in text or role in scope:
                qualifier = role
                break
        if family == "height":
            if "sloping" in text:
                qualifier += " sloping"
            elif "flat" in text:
                qualifier += " flat"
    elif family == "setback":
        qualifier = scope.replace("_", " ")
    elif family == "building_separation":
        qualifier = scope.replace("_", " ")
    return (family, qualifier.strip())


_MATRIX_ROW_ORDER = [
    "dwelling_units", "lot_area", "lot_coverage", "impervious_surface",
    "height", "storeys", "setback", "building_separation",
]


def matrix_cells(
    verified: list[dict[str, Any]],
    review: list[dict[str, Any]],
    gold_rules: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the 101.4 matrix grid: rows = regulations, cols = dwelling buckets.

    Cell precedence: verified > review > gold-only "missing" > "n/a". A cell
    is only ever called MISSING when a gold row claims it should exist —
    absence of gold means no claim, rendered honestly as n/a.
    """
    cells: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}

    def add(rule: dict[str, Any], status: str) -> None:
        family = str(rule.get("rule_object") or "")
        if family not in _MATRIX_ROW_ORDER:
            return
        row_key = _matrix_row_key(rule)
        for bucket in applicability_buckets(rule):
            slot = cells.setdefault(row_key, {}).get(bucket)
            rank = {"verified": 0, "review": 1, "missing": 2}
            if slot is None or rank[status] < rank[slot["status"]]:
                value = f"{rule.get('value') or ''} {rule.get('unit') or ''}".strip()
                reason = ""
                if status == "review":
                    reason = _plain_join((rule.get("support_gaps") or [])[:2])
                if status == "missing":
                    reason = "in gold, not yet proven"
                cells.setdefault(row_key, {})[bucket] = {
                    "status": status,
                    "text": value or status,
                    "rule_id": str(rule.get("rule_id") or rule.get("gold_id") or ""),
                    "reason": reason,
                }

    for rule in verified:
        add(rule, "verified")
    for rule in review:
        add(rule, "review")
    for gold in gold_rules:
        add(gold, "missing")

    rows = []
    for row_key in sorted(cells, key=lambda key: (_MATRIX_ROW_ORDER.index(key[0]), key[1])):
        family, qualifier = row_key
        label = _plain_label(family) + (f" \u2014 {qualifier}" if qualifier else "")
        rows.append(
            {
                "label": label,
                "cells": [
                    cells[row_key].get(bucket, {"status": "na", "text": "n/a", "rule_id": "", "reason": ""})
                    for bucket, _ in MATRIX_COLUMNS
                ],
            }
        )
    return {"columns": [label for _, label in MATRIX_COLUMNS], "rows": rows}


def matrix_table_html(grid: dict[str, Any]) -> str:
    """Render the matrix grid as themed HTML (pure string, testable)."""
    head = "".join(f"<th>{html.escape(column)}</th>" for column in grid["columns"])
    body_rows = []
    for row in grid["rows"]:
        cells = []
        for cell in row["cells"]:
            title = html.escape(f"{cell.get('rule_id') or ''} {cell.get('reason') or ''}".strip())
            cells.append(
                f"<td><span class='matrix-cell status-{cell['status']}' title='{title}'>"
                f"{html.escape(str(cell['text']))}</span></td>"
            )
        body_rows.append(f"<tr><td class='row-label'>{html.escape(row['label'])}</td>{''.join(cells)}</tr>")
    return (
        "<table class='matrix-table'><thead><tr><th>Regulation</th>"
        + head
        + "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table>"
    )


def coverage_rows(
    data: dict[str, Any],
    gold_rules: list[dict[str, Any]],
    benchmark: dict[str, Any],
) -> list[dict[str, Any]]:
    """Per-family coverage: candidates -> buckets -> gold coverage."""
    metrics = (benchmark or {}).get("rule_metrics", {})
    matched_verified = {m.get("gold_id") for m in metrics.get("matched_verified", []) if isinstance(m, dict)}
    matched_review = {m.get("gold_id") for m in metrics.get("matched_review", []) if isinstance(m, dict)}

    families: dict[str, dict[str, Any]] = {}

    def slot(family: str) -> dict[str, Any]:
        return families.setdefault(
            family,
            {"family": family, "candidates": 0, "verified": 0, "review": 0,
             "rejected": 0, "not_used": 0, "gold": 0, "gold_verified": 0,
             "gold_review": 0, "hold_reasons": Counter()},
        )

    for candidate in data.get("rule_candidates") or []:
        slot(str(candidate.get("rule_object") or "?"))["candidates"] += 1
    for bucket in ("verified", "review", "rejected", "not_used"):
        for rule in data.get(bucket) or []:
            entry = slot(str(rule.get("rule_object") or "?"))
            entry[bucket] += 1
            if bucket == "review":
                for gap in _gap_codes(rule)[:1]:
                    entry["hold_reasons"][gap] += 1
    for gold in gold_rules:
        entry = slot(str(gold.get("rule_object") or "?"))
        entry["gold"] += 1
        if gold.get("gold_id") in matched_verified:
            entry["gold_verified"] += 1
        elif gold.get("gold_id") in matched_review:
            entry["gold_review"] += 1

    rows = []
    for family, entry in sorted(families.items(), key=lambda item: -item[1]["candidates"]):
        top = entry["hold_reasons"].most_common(1)
        rows.append(
            {
                "family": _plain_label(family),
                "candidates": entry["candidates"],
                "verified": entry["verified"],
                "review": entry["review"],
                "rejected": entry["rejected"],
                "not_used": entry["not_used"],
                "top_hold_reason": _plain_label(top[0][0]) if top else "",
                "gold": entry["gold"],
                "gold_verified": entry["gold_verified"],
                "gold_review": entry["gold_review"],
                "coverage": (entry["gold_verified"] / entry["gold"]) if entry["gold"] else None,
            }
        )
    return rows


def gold_gap_rows(benchmark: dict[str, Any], gold_rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Each gold rule the verifier has NOT proven, with where it sits."""
    metrics = (benchmark or {}).get("rule_metrics", {})
    matched_verified = {m.get("gold_id"): m for m in metrics.get("matched_verified", []) if isinstance(m, dict)}
    matched_review = {m.get("gold_id"): m for m in metrics.get("matched_review", []) if isinstance(m, dict)}
    missing_entirely = set(metrics.get("missed_verified_or_review_gold_rule_ids") or [])
    rows = []
    for gold in gold_rules:
        gold_id = str(gold.get("gold_id") or "")
        if gold_id in matched_verified:
            continue
        if gold_id in missing_entirely:
            status, detail = "absent", "no candidate covers this rule \u2014 upstream extraction gap"
        elif gold_id in matched_review:
            status, detail = "review", f"covered in review as {matched_review[gold_id].get('rule_id')}"
        else:
            status, detail = "unproven", "not matched by any verified rule"
        rows.append(
            {
                "gold_id": gold_id,
                "family": _plain_label(str(gold.get("rule_object") or "")),
                "claim": f"{_operator_short(gold.get('operator'))} {gold.get('value') or ''} {gold.get('unit') or ''}".strip(),
                "applies_to": str(gold.get("applies_to") or ""),
                "status": status,
                "detail": detail,
            }
        )
    return rows


def city_comparison_rows(outputs_root: Path = OUTPUTS_ROOT) -> list[dict[str, Any]]:
    """One row per city x lane for the portfolio grid."""
    rows = []
    for output_dir in discover_city_output_dirs(outputs_root):
        native_lane = native_label_for_dir(output_dir) if native_run_root(output_dir) else None
        is_p9 = output_dir.name.endswith(P9_DIR_SUFFIX) or output_dir.name.endswith(f"{P9_DIR_SUFFIX}_v21")
        lane = native_lane or ("P9" if is_p9 else "P5")
        benchmark = _read_json(output_dir / "benchmark_report.json", {})
        summary = _read_json(output_dir / "slim_summary.json", {})
        metrics = benchmark.get("rule_metrics", {})
        rows.append(
            {
                "city": city_label_from_dir(output_dir).replace(" \u2014 Pipeline 9", ""),
                "lane": lane,
                "output_dir": str(output_dir),
                "candidates": summary.get("candidate_rule_count"),
                "verified": metrics.get("verified_rule_count"),
                "review": metrics.get("review_rule_count"),
                "precision": metrics.get("verified_precision"),
                "gold_recall": metrics.get("verified_gold_recall"),
                "false_verified": metrics.get("false_verified_count"),
                "gate_status": pipeline_gate_status(summary, benchmark),
            }
        )
    rows.sort(key=lambda row: (row["city"], row["lane"]))
    return rows


# Plotly defaults shared by every chart; a plain dict so tests can pin it
# without importing plotly. Charts degrade to the HTML bar rows when plotly
# is not installed — the dashboard keeps its runs-with-base-deps guarantee.
PLOTLY_LAYOUT = {
    "font": {"family": "Inter, -apple-system, sans-serif", "size": 13, "color": "#1f2328"},
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "colorway": ["#0969da", "#1a7f37", "#9a6700", "#cf222e", "#57606a", "#8250df"],
    "margin": {"l": 8, "r": 8, "t": 28, "b": 36},
    "xaxis": {"gridcolor": "#eef1f4", "zerolinecolor": "#d0d7de"},
    "yaxis": {"gridcolor": "#eef1f4", "zerolinecolor": "#d0d7de"},
    "hoverlabel": {"bgcolor": "#1f2328"},
    "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02},
}


def _themed_plotly(st: Any, figure_builder: Any) -> bool:
    """Render a plotly figure with the shared layout; False -> caller falls back."""
    try:
        import plotly.graph_objects as go  # noqa: F401
    except Exception:
        return False
    try:
        figure = figure_builder()
        figure.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})
        return True
    except Exception as error:  # pragma: no cover - plotting failure is cosmetic
        st.caption(f"Chart unavailable: {error}")
        return False


def _funnel_view(st: Any, data: dict[str, Any]) -> None:
    """Where do candidates die? One funnel + the reasons at each gate."""
    stages = funnel_stages(data)
    st.markdown("#### Where candidates die")
    st.caption(
        "Each stage is a verification gate. Rules held for review are a parking "
        "lot, not a loss — they wait for evidence or a human, never auto-promote."
    )

    def _build():
        import plotly.graph_objects as go

        return go.Figure(
            go.Funnel(
                y=[row["label"] for row in stages],
                x=[row["count"] for row in stages],
                textinfo="value+percent initial",
                marker={"color": ["#0969da", "#218bff", "#54aeff", "#2da44e", "#1a7f37"]},
                connector={"line": {"color": "#d0d7de", "width": 1}},
            )
        )

    if not _themed_plotly(st, _build):
        for row in stages:
            share = row["count"] / max(stages[0]["count"], 1)
            st.markdown(
                f"<div class='bar-row'><span>{html.escape(row['label'])}</span>"
                f"<div class='bar-track'><div class='bar-fill' style='width:{share * 100:.1f}%'></div></div>"
                f"<b>{row['count']}</b></div>",
                unsafe_allow_html=True,
            )
    outflows = [row for row in stages if row["dropped"]]
    if outflows:
        columns = st.columns(len(outflows))
        for column, row in zip(columns, outflows):
            with column:
                status = "review" if row["outflow_status"] == "held" else row["outflow_status"]
                color = STATUS_COLORS.get(status, "#57606a")
                verb = "held for review" if row["outflow_status"] == "held" else row["outflow_status"].replace("_", " ")
                st.markdown(
                    f"<div class='guide-card'><b style='color:{color}'>{row['dropped']} {verb}</b>"
                    + "".join(
                        f"<span style='display:block'>{html.escape(reason)} ({count})</span>"
                        for reason, count in row["top_reasons"]
                    )
                    + "</div>",
                    unsafe_allow_html=True,
                )
    note = stages[0].get("note")
    if note:
        st.caption(note)


def filter_triage_items(
    items: list[dict[str, Any]],
    *,
    categories: list[str],
    priorities: list[str],
    likelihoods: list[str],
    rule_objects: list[str],
) -> list[dict[str, Any]]:
    """Apply dashboard filters to triage rows."""
    filtered = items
    if categories:
        filtered = [item for item in filtered if item.get("review_category") in categories]
    if priorities:
        filtered = [item for item in filtered if item.get("triage_priority") in priorities]
    if likelihoods:
        filtered = [item for item in filtered if item.get("likely_status") in likelihoods]
    if rule_objects:
        filtered = [item for item in filtered if item.get("rule_object") in rule_objects]
    return filtered


def compact_rule_row(rule: dict[str, Any]) -> dict[str, Any]:
    """Return one table row with the fields reviewers need first."""
    return {
        "Rule ID": rule.get("rule_id"),
        "Rule family": _plain_label(rule.get("rule_object")),
        "Scope": _plain_label(rule.get("constraint_scope")),
        "Applies to": _plain_label(rule.get("applies_to")),
        "Direction": _operator_short(rule.get("operator"), rule.get("constraint_type")),
        "Value": rule.get("value"),
        "Unit": rule.get("unit"),
        "Why review": _plain_label(rule.get("review_category")),
        "Urgency": _plain_label(rule.get("triage_priority") or rule.get("review_priority")),
        "Likely outcome": _plain_label(rule.get("likely_status")),
        "Score": rule.get("likely_correct_score"),
        "Missing proof": _plain_join(rule.get("support_gaps", [])[:4]),
    }


def _safety_chip_html(false_verified: int, gate_pass: bool) -> str:
    """Green chip when there are zero false verifies (the safety win); red ONLY
    when a false verify exists, so red stays meaningful (a failed recall gate is
    not a safety failure)."""
    if false_verified > 0:
        return f"<div class='safety-chip safety-alert'>Attention — {false_verified} false verifies</div>"
    suffix = " · quality gate passed" if gate_pass else ""
    return f"<div class='safety-chip safety-ok'>✓ Safe — 0 false verifies{suffix}</div>"


def _coverage_hero(st: Any, data: dict[str, Any], counts: dict[str, int]) -> None:
    slot_metrics = (data.get("slot_audit") or {}).get("slot_metrics") or {}
    coverage = slot_metrics.get("scored_verified_coverage")
    if coverage is None:
        st.markdown(
            "<div class='coverage-hero'><div><span class='pct'>"
            f"{counts.get('verified', 0)}</span> <span class='cap'>verified rules</span></div>"
            "<div class='cap'>Scored coverage is computed in an M5 measurement run; this view shows the "
            "verified rule count.</div></div>",
            unsafe_allow_html=True,
        )
        return
    denom = slot_metrics.get("distinct_scored_legal_slot_count") or 0
    verified = int(slot_metrics.get("scored_verified_slot_count") or 0)
    review = int(slot_metrics.get("scored_review_slot_count") or 0)
    missed = int(slot_metrics.get("scored_missed_slot_count") or 0)
    total = max(verified + review + missed, 1)
    segments = (
        f"<div class='seg seg-verified' style='width:{verified / total * 100:.1f}%'></div>"
        f"<div class='seg seg-review' style='width:{review / total * 100:.1f}%'></div>"
        f"<div class='seg seg-missed' style='width:{missed / total * 100:.1f}%'></div>"
    )
    st.markdown(
        "<div class='coverage-hero'>"
        f"<div><span class='pct'>{html.escape(str(_format_coverage(coverage)))}</span> "
        f"<span class='cap'>of {denom} distinct legal rules proven from source</span></div>"
        f"<div class='coverage-bar'>{segments}</div>"
        "<div class='coverage-key'>"
        f"<span><i style='background:var(--status-verified)'></i>Verified <b>{verified}</b></span>"
        f"<span><i style='background:var(--status-review)'></i>Review <b>{review}</b></span>"
        f"<span><i style='background:var(--status-not-used)'></i>Missed <b>{missed}</b></span>"
        "</div></div>",
        unsafe_allow_html=True,
    )


def _status_mix_bar(st: Any, counts: dict[str, int]) -> None:
    order = [("verified", "Verified"), ("review", "Review"), ("rejected", "Rejected"), ("not_used", "Not used")]
    total = max(sum(int(counts.get(key, 0)) for key, _ in order), 1)
    segments = ""
    for key, label in order:
        n = int(counts.get(key, 0))
        if n <= 0:
            continue
        pct = n / total * 100
        segments += (
            f"<div class='seg {key}' style='width:{pct:.2f}%' title='{label}: {n}'>"
            f"{n if pct > 7 else ''}</div>"
        )
    st.markdown(f"<div class='status-bar'>{segments}</div>", unsafe_allow_html=True)


def _city_display_parts(output_dir: Path) -> dict[str, str]:
    stem = city_stem_from_dir(output_dir)
    if stem == "burnaby_r1":
        return {
            "city": "Burnaby, BC",
            "bylaw": "Burnaby Zoning Bylaw 1965",
            "district": "Division E — R1 District",
            "source_type": "Official PDF + scoped district pages",
        }
    if stem == "vancouver_rs":
        return {
            "city": "Vancouver, BC",
            "bylaw": "Vancouver Zoning and Development By-law",
            "district": "RS Districts",
            "source_type": "Official bylaw section PDF",
        }
    if stem == "calgary_rcg":
        return {
            "city": "Calgary, AB",
            "bylaw": "Calgary Land Use Bylaw 1P2007",
            "district": "R-CG District",
            "source_type": "Full bylaw PDF + district scope",
        }
    label = city_label_from_dir(output_dir)
    return {"city": label, "bylaw": "Zoning bylaw", "district": "Selected district", "source_type": "Committed sources"}


def _source_ref(rule: dict[str, Any]) -> str:
    source = rule.get("source") if isinstance(rule.get("source"), dict) else {}
    page = (
        rule.get("page")
        or source.get("page")
        or source.get("pdf_page")
        or source.get("source_page")
    )
    section = (
        rule.get("section")
        or rule.get("source_section")
        or source.get("section")
        or source.get("section_id")
    )
    parts = []
    if page not in (None, ""):
        parts.append(f"Page {page}")
    if section not in (None, "") and not _looks_internal_id(section):
        parts.append(f"§ {section}")
    if not parts and rule.get("evidence_id"):
        parts.append(str(rule.get("evidence_id")))
    return "<br>".join(html.escape(part) for part in parts) or "Source packet"


def _issue_label(rule: dict[str, Any]) -> str:
    if rule.get("review_category"):
        return _plain_label(rule.get("review_category"))
    gaps = rule.get("support_gaps") or rule.get("review_reasons") or []
    if gaps:
        return _plain_label(gaps[0])
    if rule.get("verification_status"):
        return _plain_label(rule.get("verification_status"))
    return "Needs review"


def _issue_tone(label: str) -> str:
    lowered = str(label).lower()
    if "value" in lowered or "mismatch" in lowered:
        return "issue-red"
    if "table" in lowered or "reference" in lowered:
        return "issue-amber"
    if "scope" in lowered:
        return "issue-blue"
    if "condition" in lowered or "exception" in lowered:
        return "issue-purple"
    return "issue-green"


def _overview_kpi_card(label: str, value: Any, delta: str, note: str, icon: str, tone: str, delta_tone: str) -> str:
    return (
        "<div class='kpi-card'>"
        "<div class='kpi-top'>"
        f"<div class='kpi-icon kpi-{tone}'>{html.escape(icon)}</div>"
        "<div>"
        f"<div class='kpi-label'>{html.escape(label)}</div>"
        f"<div class='kpi-value'>{html.escape(str(value))}</div>"
        f"<div class='kpi-delta {html.escape(delta_tone)}'>{html.escape(delta)}</div>"
        "</div></div>"
        f"<div class='kpi-note'>{html.escape(note)}</div>"
        "</div>"
    )


def _overview_decision_flow(candidates: int, verified: int, review: int, rejected: int) -> str:
    checked = candidates or verified + review + rejected
    checked = max(checked, 0)
    denominator = max(checked, 1)

    def pct(value: int) -> str:
        return f"{(value / denominator) * 100:.1f}%"

    verified_pct = pct(verified)
    review_pct = pct(review)
    rejected_pct = pct(rejected)
    unbucketed = max(0, checked - verified - review - rejected)
    unbucketed_note = (
        f"<span>{unbucketed:,} checked item{'s' if unbucketed != 1 else ''} did not enter a final bucket.</span>"
        if unbucketed
        else "<span>All checked items are accounted for in the three verifier buckets.</span>"
    )
    return f"""
<div class="decision-flow">
  <div class="decision-flow-head">
    <div>
      <h3>Candidate Check Flow</h3>
    </div>
  </div>
  <div class="decision-flow-main">
    <div class="decision-total">
      <span>Items checked</span>
      <b>{checked:,}</b>
    </div>
    <div>
      <div class="decision-strip" aria-label="Verification outcome split">
        <span class="seg verified" style="width:{verified_pct};"></span>
        <span class="seg review" style="width:{review_pct};"></span>
        <span class="seg rejected" style="width:{rejected_pct};"></span>
      </div>
      <div class="decision-branches">
        <div class="decision-branch verified">
          <span>Verified</span>
          <b>{verified:,}</b>
          <small>{verified_pct}. Moves downstream.</small>
        </div>
        <div class="decision-branch review">
          <span>In review</span>
          <b>{review:,}</b>
          <small>{review_pct}. Needs review.</small>
        </div>
        <div class="decision-branch rejected">
          <span>Rejected</span>
          <b>{rejected:,}</b>
          <small>{rejected_pct}. Blocked.</small>
        </div>
      </div>
    </div>
  </div>
  <div class="decision-note">{unbucketed_note}<b>Verified-only rules feed GIS and compliance.</b></div>
</div>
"""


def _overview_filters(st: Any, meta: dict[str, str], source_url: str) -> None:
    columns = st.columns([1.1, 1.55, 1.35, 1.1, .7])
    columns[0].selectbox("City", [meta["city"]], index=0, key="overview_city_filter")
    columns[1].selectbox("Bylaw", [meta["bylaw"]], index=0, key="overview_bylaw_filter")
    columns[2].selectbox("Division / District", [meta["district"]], index=0, key="overview_district_filter")
    columns[3].selectbox("Source Type", [meta["source_type"]], index=0, key="overview_source_filter")
    with columns[4]:
        st.write("")
        st.link_button("Open source", source_url, width="stretch")


def _overview_verification_status_panel(st: Any, data: dict[str, Any], counts: dict[str, int]) -> None:
    benchmark = data.get("benchmark") or {}
    metrics = benchmark.get("rule_metrics") or {}
    precision = metrics.get("verified_precision")
    precision_text = f"{float(precision):.0%}" if isinstance(precision, (int, float)) else "not measured"
    false_verified = int(metrics.get("false_verified_count") or 0)
    source_failures = int(metrics.get("verified_source_support_failed_count") or 0)
    source_tone = "ok" if source_failures == 0 else "bad"
    false_tone = "ok" if false_verified == 0 else "bad"
    st.markdown(
        f"""
<div class="console-card">
  <div class="trust-status-head">
    <div>
      <div class="trust-title">Safety Gates</div>
      <span>The numbers above are only useful if these gates stay clean.</span>
    </div>
    <b>Precision {html.escape(precision_text)}</b>
  </div>
  <div class="trust-mini-grid">
    <div class="trust-mini {false_tone}"><span>False verified</span><b>{false_verified}</b><small>must stay zero</small></div>
    <div class="trust-mini {source_tone}"><span>Source failures</span><b>{source_failures}</b><small>must stay zero</small></div>
    <div class="trust-mini ok"><span>GIS boundary</span><b>verified</b><small>review items stay out</small></div>
    <div class="trust-mini ok"><span>Decision rule</span><b>source</b><small>evidence decides</small></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _overview_review_queue(st: Any, data: dict[str, Any]) -> None:
    review = list(data.get("review") or [])
    visible = review[:6]
    rows = []
    for rule in visible:
        issue = _issue_label(rule)
        priority = _plain_label(rule.get("triage_priority") or rule.get("review_priority") or "medium")
        priority_tone = "issue-red" if priority.lower() == "high" else "issue-amber" if priority.lower() == "medium" else "issue-green"
        rows.append(
            "<tr>"
            f"<td><b>{html.escape(_plain_label(rule.get('rule_object')))}</b><br>{html.escape(_format_value_unit(rule.get('value'), str(rule.get('unit') or '')))}</td>"
            f"<td><span class='issue-pill {_issue_tone(issue)}'>{html.escape(issue)}</span></td>"
            f"<td>{_source_ref(rule)}</td>"
            f"<td><span class='issue-pill {priority_tone}'>{html.escape(priority or 'Medium')}</span></td>"
            "</tr>"
        )
    if not rows:
        rows.append("<tr><td colspan='4'>No review-needed rules for this selection.</td></tr>")
    st.markdown(
        f"""
<div class="console-card">
  <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;margin-bottom:10px;">
    <h3 style="margin:0;">Review Queue <span class="issue-pill issue-amber">{len(review)}</span></h3>
    <span style="font-size:12px;color:#16884a;font-weight:760;">View all in Review Queue</span>
  </div>
  <table class="table-lite">
    <thead><tr><th>Rule Candidate</th><th>Issue</th><th>Source</th><th>Priority</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <div class="pager"><span>Showing 1–{min(len(review), 6)} of {len(review)}</span><span>‹</span><b>1</b><span>2</span><span>3</span><span>›</span></div>
</div>
""",
        unsafe_allow_html=True,
    )


def _overview_source_coverage(st: Any, data: dict[str, Any]) -> None:
    source = data.get("source_summary") or {}
    corpus = source.get("m4_source_corpus") or {}
    coverage = corpus.get("selected_rule_like_numeric_coverage")
    pct = float(coverage) * 100 if coverage is not None else 0.0
    if pct <= 0:
        chunks = int(source.get("source_chunk_count") or 0)
        packs = int(source.get("evidence_pack_count") or 0)
        pct = min(100.0, (packs / max(chunks, 1)) * 100) if chunks else 0.0
    st.markdown("<div class='console-card'><h3>Source Coverage</h3>", unsafe_allow_html=True)
    try:
        import plotly.graph_objects as go

        fig = go.Figure(
            go.Pie(
                values=[pct, max(0.0, 100.0 - pct)],
                hole=.68,
                marker={"colors": ["#1f9d55", "#e8eef0"]},
                textinfo="none",
                sort=False,
            )
        )
        fig.update_layout(
            **{**PLOTLY_LAYOUT, "height": 210, "showlegend": False, "margin": {"l": 0, "r": 0, "t": 4, "b": 4}},
            annotations=[{"text": f"<b>{pct:.0f}%</b><br>covered", "showarrow": False, "font": {"size": 18, "color": "#111827"}}],
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    except Exception:
        st.metric("Source coverage", f"{pct:.0f}%")
    st.markdown(
        f"""
<div class="source-row"><span>Source chunks</span><div class="source-bar"><span style="width:100%;"></span></div></div>
<div class="source-row"><span>Evidence packs</span><div class="source-bar"><span style="width:{min(100, pct):.0f}%;"></span></div></div>
<div style="font-size:12px;color:#6b7280;margin-top:8px;">{int(source.get('source_chunk_count') or 0)} chunks · {int(source.get('evidence_pack_count') or 0)} evidence packs · {int(source.get('page_count') or 0)} scoped pages</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _overview_quality_chart(st: Any, data: dict[str, Any]) -> None:
    benchmark = data.get("benchmark") or {}
    metrics = benchmark.get("rule_metrics") or {}
    precision = float(metrics.get("verified_precision") or 0.0)
    recall = float(metrics.get("verified_or_review_recall") or metrics.get("release_candidate_recall") or 0.0)
    source_support = 1.0 if int(metrics.get("verified_source_support_failed_count") or 0) == 0 else 0.0
    st.markdown("<div class='console-card'><h3>Verification Quality</h3>", unsafe_allow_html=True)
    try:
        import plotly.graph_objects as go

        labels = ["Precision", "Recall", "Source support"]
        values = [precision, recall, source_support]
        fig = go.Figure(
            go.Scatter(
                x=labels,
                y=values,
                mode="lines+markers",
                line={"color": "#1f9d55", "width": 3},
                marker={"size": 9, "color": ["#1f9d55", "#2f73b7", "#1f9d55"]},
            )
        )
        fig.update_yaxes(range=[0, 1.05], tickformat=".0%")
        fig.update_layout(**{**PLOTLY_LAYOUT, "height": 210, "margin": {"l": 4, "r": 4, "t": 8, "b": 28}, "showlegend": False})
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    except Exception:
        st.metric("Verified precision", f"{precision:.0%}")
        st.metric("Verified-or-review recall", f"{recall:.0%}")
    st.markdown(
        f"<div style='font-size:12px;color:#6b7280;'>Precision {precision:.0%} · verified-or-review recall {recall:.0%} · false verified {int(metrics.get('false_verified_count') or 0)}</div></div>",
        unsafe_allow_html=True,
    )


def _overview_gis_status(st: Any, data: dict[str, Any], output_dir: Path) -> None:
    contract = _read_json(output_dir / "gis_rule_contract.json", {})
    rules = contract.get("rules", []) if isinstance(contract, dict) else []
    dedup = contract.get("deduplication", {}) if isinstance(contract, dict) else {}
    verified = len(data.get("verified") or [])
    ready = len(rules) or verified
    pending = len(data.get("review") or [])
    merged = int(dedup.get("duplicate_merged_count") or max(0, verified - ready))
    st.markdown(
        f"""
<div class="console-card">
  <h3>GIS Handoff</h3>
  <div class="gis-flow">
    <div class="gis-node ok"><span>Verified rows from verifier</span><b>{verified}</b></div>
    <div class="gis-node"><span>Deduplicated GIS constraints</span><b>{ready}</b></div>
    <div class="gis-node warn"><span>Pending review</span><b>{pending}</b></div>
  </div>
  <div style="font-size:12px;color:#6b7280;margin-top:10px;">{merged} verified row{'s' if merged != 1 else ''} merged as duplicates for GIS export.</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _overview_safety_strip(data: dict[str, Any], output_dir: Path) -> str:
    benchmark = data.get("benchmark") or {}
    metrics = benchmark.get("rule_metrics") or {}
    precision = metrics.get("verified_precision")
    precision_text = f"{float(precision):.0%}" if isinstance(precision, (int, float)) else "not measured"
    false_verified = int(metrics.get("false_verified_count") or 0)
    source_failures = int(metrics.get("verified_source_support_failed_count") or 0)
    contract = _read_json(output_dir / "gis_rule_contract.json", {})
    dedup = contract.get("deduplication", {}) if isinstance(contract, dict) else {}
    merged = int(dedup.get("duplicate_merged_count") or 0)
    return f"""
<div class="overview-safety-strip">
  <div><span>Verified precision</span><b>{html.escape(precision_text)}</b></div>
  <div><span>False verified</span><b>{false_verified}</b></div>
  <div><span>Source failures</span><b>{source_failures}</b></div>
  <div><span>GIS duplicates merged</span><b>{merged}</b></div>
</div>
"""


def _overview_next_steps_html() -> str:
    steps = [
        ("Review differences", "Open Human Review when a candidate looks close to a verified rule."),
        ("Check repair impact", "Open Repair Evidence to see which evidence gaps improved and which still block promotion."),
        ("Handoff verified-only", "Open GIS Handoff when you need the deduplicated map-ready rules."),
    ]
    cards = []
    for title, body in steps:
        cards.append(
            "<div class='next-step-card'>"
            f"<b>{html.escape(title)}</b>"
            f"<span>{html.escape(body)}</span>"
            "</div>"
        )
    return "<div class='next-step-grid'>" + "".join(cards) + "</div>"


def _overview_chat_panel(st: Any, data: dict[str, Any], output_dir: Path, *, centered: bool = False) -> None:
    index_path = bylaw_index_path(output_dir)
    city_stem = city_stem_from_dir(output_dir)
    chat_key = f"overview::{_rag_chat_key(city_stem)}"
    st.session_state.setdefault(chat_key, [])
    history = st.session_state[chat_key]
    shell_class = "console-card ask-card ask-card-centered" if centered else "console-card ask-card"
    st.markdown(
        f"""
<div class="{shell_class}">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <h3 style="margin:0;">Ask the Bylaw</h3>
    <span class="mode-pill live">source grounded</span>
  </div>
  <div class="ask-intro">Ask a bylaw question after checking the verification result. The answer uses source chunks and cannot approve or edit rules.</div>
""",
        unsafe_allow_html=True,
    )
    if index_path is None:
        st.info("No bylaw retrieval index found for this city.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    with st.form(f"overview_ask_form_{city_stem}", clear_on_submit=True):
        ask_col, send_col = st.columns([0.82, 0.18], gap="small")
        with ask_col:
            question = st.text_input(
                "Ask a bylaw question...",
                placeholder="Ask a bylaw question...",
                label_visibility="collapsed",
            )
        with send_col:
            submitted = st.form_submit_button("Ask", width="stretch")
    if submitted and question.strip():
        with st.spinner("Reading the bylaw…"):
            _bylaw_chat_respond(st, question.strip(), index_path, chat_key, data)
        st.rerun()

    suggestions = _bylaw_suggestions(data, limit=3)
    if suggestions:
        st.markdown("<div class='prompt-row-label'>Prompt library</div>", unsafe_allow_html=True)
        prompt_columns = st.columns(len(suggestions), gap="small")
        for index, suggestion in enumerate(suggestions):
            with prompt_columns[index]:
                if st.button(suggestion, key=f"overview_prompt_{city_stem}_{index}", width="stretch"):
                    with st.spinner("Reading the bylaw…"):
                        _bylaw_chat_respond(st, suggestion, index_path, chat_key, data)
                    st.rerun()
    if history:
        st.markdown("<div class='prompt-row-label'>Recent answer</div>", unsafe_allow_html=True)
        for message in history[-2:]:
            role = "chat-user" if message.get("role") == "user" else "chat-assistant"
            st.markdown(f"<div class='chat-bubble {role}'>{html.escape(str(message.get('content') or ''))}</div>", unsafe_allow_html=True)
        latest = history[-1] if history and history[-1].get("role") == "assistant" else None
        if latest:
            # Render the verification card + any embedded tables (the headline
            # features — previously dark here because content-only bubbles + no data).
            for card in (latest.get("rule_cards") or []):
                _render_verification_card(st, card)
            for table in (latest.get("tables") or []):
                _render_chat_table(st, table)
            sources = latest.get("sources") or []
            if sources:
                hit = sources[0]
                loc = _clean_section_label(hit.get("section") or hit.get("chunk_id"), hit.get("page")) or "source section"
                st.markdown(f"<div class='source-cite'><b>Source cited</b><br>{html.escape(str(loc))}</div>", unsafe_allow_html=True)
            for i, (label, fq) in enumerate(_followup_chips(latest)):
                if st.button(label, key=f"overview_fup_{city_stem}_{len(history)}_{i}", width="stretch"):
                    with st.spinner("Reading the bylaw…"):
                        _bylaw_chat_respond(st, fq, index_path, chat_key, data)
                    st.rerun()
    st.caption("Advisory only. Verification decisions stay with the deterministic verifier.")
    st.markdown("</div>", unsafe_allow_html=True)


def _overview_console_page(st: Any, data: dict[str, Any], output_dir: Path, source_url: str) -> None:
    meta = _city_display_parts(output_dir)
    counts = output_bucket_counts(data)
    benchmark = data.get("benchmark") or {}
    metrics = benchmark.get("rule_metrics") or {}
    candidates = len(data.get("rule_candidates") or []) or int(metrics.get("candidate_rule_count") or 0)
    verified = int(counts.get("verified") or 0)
    review = int(counts.get("review") or 0)
    rejected = int(counts.get("rejected") or 0)

    st.markdown(
        """
<div class="overview-titlebar">
  <div>
    <h1>Zoning Bylaw Verification Overview</h1>
    <p>Start with the verification result, then ask the bylaw. Details stay in the focused pages on the left.</p>
  </div>
  <div class="overview-actions">
    <span>Local preview</span><span class="live-dot"></span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div class="selection-summary">
  <div><b>{html.escape(meta["city"])}</b><span>{html.escape(meta["bylaw"])} · {html.escape(meta["district"])}</span></div>
  <a href="{html.escape(source_url)}" target="_blank">Open official source</a>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(_overview_decision_flow(candidates, verified, review, rejected), unsafe_allow_html=True)

    _overview_chat_panel(st, data, output_dir, centered=True)

    st.markdown(
        "<div class='overview-band-title'>Run guardrails</div>"
        "<p class='overview-band-copy'>A compact safety check. The detailed audit lives in Quality Audit.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(_overview_safety_strip(data, output_dir), unsafe_allow_html=True)
    st.markdown(
        "<div class='overview-band-title'>Next best actions</div>",
        unsafe_allow_html=True,
    )
    st.markdown(_overview_next_steps_html(), unsafe_allow_html=True)


def _verified_rules_page(st: Any, data: dict[str, Any]) -> None:
    st.caption("Open a group instead of scrolling through the full verified-rule set.")
    rules = data.get("verified") or []
    group_choice = st.radio(
        "Group verified rules by",
        ["Rule family", "Source page"],
        horizontal=True,
        label_visibility="collapsed",
        key="verified_group_mode",
    )
    mode = "source_page" if group_choice == "Source page" else "rule_family"
    _grouped_rule_sentence_list(
        st,
        rules,
        group_mode=mode,
        show_gap=False,
        key_prefix="verified_rules",
        per_group_limit=8,
    )


def _source_library_page(st: Any, data: dict[str, Any], source_url: str) -> None:
    st.markdown("<div class='section-head'>Source Library</div>", unsafe_allow_html=True)
    st.markdown("<p class='section-sub'>Committed source material and evidence packets used by the dashboard.</p>", unsafe_allow_html=True)
    source = data.get("source_summary") or {}
    cards = [
        ("Source chunks", source.get("source_chunk_count", 0), "sections available to retrieval"),
        ("Evidence packs", source.get("evidence_pack_count", 0), "bounded support packets"),
        ("Scoped pages", source.get("page_count", 0), "source pages represented"),
    ]
    html_cards = "".join(_overview_kpi_card(label, value, note, note, "□", "blue", "info") for label, value, note in cards)
    st.markdown(f"<div class='kpi-grid'>{html_cards}</div>", unsafe_allow_html=True)
    st.link_button("Open official source PDF", source_url)
    evidence = data.get("evidence_units") or []
    if evidence:
        rows = [
            {
                "Evidence ID": item.get("evidence_id"),
                "Page": item.get("page"),
                "Section": item.get("section"),
                "Type": item.get("evidence_type"),
                "Quote": _short_display_quote(_quote_from_evidence(item), 180),
            }
            for item in evidence[:80]
        ]
        st.dataframe(_display_rows(rows), width="stretch", hide_index=True)


def _analytics_page(st: Any, data: dict[str, Any]) -> None:
    st.markdown("<div class='section-head'>Analytics</div>", unsafe_allow_html=True)
    st.markdown("<p class='section-sub'>Quality, status mix, and verification-flow diagnostics.</p>", unsafe_allow_html=True)
    counts = output_bucket_counts(data)
    _status_mix_bar(st, counts)
    _overview_quality_chart(st, data)
    _funnel_view(st, data)


def _settings_page(st: Any, source_url: str) -> None:
    st.markdown("<div class='section-head'>Settings</div>", unsafe_allow_html=True)
    st.markdown("<p class='section-sub'>Read-only dashboard configuration. No verifier outputs are changed here.</p>", unsafe_allow_html=True)
    status = _bylaw_llm_status(st)
    st.table(
        [
            {"setting": "Dashboard mode", "value": "Read-only local preview"},
            {"setting": "Chat provider", "value": status.get("provider")},
            {"setting": "Chat model", "value": status.get("model") or "retrieval only"},
            {"setting": "Official source", "value": source_url},
        ]
    )


def _rules_drilldown(st, data: dict[str, Any]) -> None:
    """Make every decision count explorable: one expander per bucket that opens
    the exact rules behind the number (rule id, family, direction, value, unit,
    section/page). Answers 'click Verified -> show me those rules.'"""
    buckets = [
        ("Verified", data.get("verified", [])),
        ("Needs review", data.get("review", [])),
        ("Rejected", data.get("rejected", [])),
        ("Not used", data.get("not_used", [])),
    ]
    if not any(rules for _, rules in buckets):
        return
    st.markdown("##### Browse the rules behind these numbers")
    st.caption("Open a bucket to see the exact rules it counts.")
    for label, rules in buckets:
        if not rules:
            continue
        with st.expander(f"{label} — {len(rules)} rule{'s' if len(rules) != 1 else ''}", expanded=False):
            _rule_sentence_list(st, rules, show_gap=(label in ("Needs review", "Rejected")))


def _summary_tab(st: Any, data: dict[str, Any]) -> None:
    benchmark = data.get("benchmark", {})
    metrics = benchmark.get("rule_metrics", {})
    gates = benchmark.get("quality_gates", {})
    counts = output_bucket_counts(data)
    false_verified = int(metrics.get("false_verified_count", 0) or 0)
    st.markdown(_safety_chip_html(false_verified, bool(gates.get("passed"))), unsafe_allow_html=True)
    _coverage_hero(st, data, counts)

    slot_metrics = (data.get("slot_audit") or {}).get("slot_metrics") or {}
    coverage = slot_metrics.get("scored_verified_coverage")
    coverage_display = _format_coverage(coverage) if coverage is not None else "—"
    kpis = [
        ("Verified", counts.get("verified", 0), "verified", "proven against source text"),
        ("Needs review", counts.get("review", 0), "review", "never auto-approved"),
        ("Verified coverage", coverage_display, "verified", "of in-scope legal rules"),
        ("False verifies", false_verified, "verified" if false_verified == 0 else "rejected", "must stay at 0"),
    ]
    cards = "".join(
        f"<div class='metric metric-{tone}'><div class='metric-label'>{html.escape(label)}</div>"
        f"<div class='metric-value'>{html.escape(str(value))}</div>"
        f"<div style='font-size:11px;color:var(--ink-soft);margin-top:4px;'>{html.escape(sub)}</div></div>"
        for label, value, tone, sub in kpis
    )
    st.caption("Each tile below is also explorable — open a bucket under the bar to see its exact rules.")
    st.markdown(f"<div class='metric-grid'>{cards}</div>", unsafe_allow_html=True)
    _status_mix_bar(st, counts)
    _rules_drilldown(st, data)
    _action_summary(st, data)
    with st.expander("How rules flow through the verifier", expanded=False):
        _funnel_view(st, data)
    with st.expander("How we got these numbers", expanded=False):
        _count_audit_panel(st, data)
        _not_used_explanation(st, data)


def _review_queue_tab(st: Any, data: dict[str, Any], output_dir: Path, triage_items: list[dict[str, Any]]) -> None:
    st.caption("Rules the verifier could not prove. Pick one item, see why it is held, then open details only when needed.")
    with st.expander("Narrow the review queue", expanded=False):
        columns = st.columns(4)
        with columns[0]:
            categories = st.multiselect("Why it needs review", _unique(triage_items, "review_category"), format_func=_plain_label)
        with columns[1]:
            priorities = st.multiselect("Urgency", _unique(triage_items, "triage_priority"), format_func=_plain_label)
        with columns[2]:
            likelihoods = st.multiselect("Likely outcome", _unique(triage_items, "likely_status"), format_func=_plain_label)
        with columns[3]:
            rule_objects = st.multiselect("Rule family", _unique(triage_items, "rule_object"), format_func=_plain_label)
    filtered_items = filter_triage_items(
        triage_items,
        categories=categories,
        priorities=priorities,
        likelihoods=likelihoods,
        rule_objects=rule_objects,
    )
    evidence_by_id = {str(unit.get("evidence_id")): unit for unit in data["evidence_units"]}
    _candidate_compare_tab(st, filtered_items, data["review"], data["verified"], output_dir, evidence_by_id)

    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-head' style='font-size:16px;'>Optional drill-downs</div>", unsafe_allow_html=True)
    st.caption("Open these only when you need the full queue, source packet, or routing table.")
    drill_left, drill_mid, drill_right = st.columns(3)
    show_grouped = drill_left.toggle("Show grouped worklist", value=False, key="review_show_grouped_worklist")
    show_source = drill_mid.toggle("Show source packet", value=False, key="review_show_source_packet")
    show_table = drill_right.toggle("Show routing table", value=False, key="review_show_routing_table")

    if show_grouped:
        n = len(filtered_items)
        st.markdown(
            f"<div class='section-head' style='font-size:15px;'>Grouped worklist - {n} rule{'s' if n != 1 else ''}</div>",
            unsafe_allow_html=True,
        )
        group_choice = st.radio(
            "Group review worklist by",
            ["Issue type", "Rule family", "Priority"],
            horizontal=True,
            label_visibility="collapsed",
            key="review_group_mode",
        )
        mode = {
            "Issue type": "issue",
            "Rule family": "rule_family",
            "Priority": "priority",
        }[group_choice]
        _grouped_rule_sentence_list(
            st,
            filtered_items,
            group_mode=mode,
            show_gap=True,
            key_prefix="review_worklist",
            per_group_limit=8,
        )

    if show_source:
        _review_assistant_tab(st, data["review_assistant_packets"], data["review"], output_dir, evidence_by_id)

    if show_table:
        _review_router_tab(st, data["router"])


def _gis_handoff_tab(st: Any, data: dict[str, Any], output_dir: Path) -> None:
    felt = _read_json(output_dir / "gis_felt_export.json", {})
    contract_path = output_dir / "gis_rule_contract.json"
    felt_path = output_dir / "gis_felt_export.json"
    constraints = felt.get("constraints", []) if isinstance(felt, dict) else []
    if not constraints and not contract_path.exists():
        st.info(
            "No GIS export for this run yet. The verified-only GIS contract and felt export are written "
            "next to the verified rules when the pipeline runs."
        )
        return
    export_counts = felt.get("export_counts", {}) if isinstance(felt, dict) else {}
    ready = sum(1 for constraint in constraints if constraint.get("gis_ready"))
    st.caption(
        "Verified-only, deduplicated, geometry-tagged rules ready for the map. "
        "These are the only rules that should drive GIS."
    )
    cards = [
        ("Verified rules", export_counts.get("verified_rule_count", len(constraints)), "verified", "source-supported"),
        ("GIS constraints", export_counts.get("gis_constraint_count", len(constraints)), "verified", "deduplicated for the map"),
        ("Map-ready", ready, "verified", "drawable: number + geometry"),
    ]
    html_cards = "".join(
        f"<div class='metric metric-{tone}'><div class='metric-label'>{html.escape(label)}</div>"
        f"<div class='metric-value'>{html.escape(str(value))}</div>"
        f"<div style='font-size:11px;color:var(--ink-soft);margin-top:4px;'>{html.escape(sub)}</div></div>"
        for label, value, tone, sub in cards
    )
    st.markdown(f"<div class='metric-grid'>{html_cards}</div>", unsafe_allow_html=True)
    contract = _read_json(contract_path, {})
    contract_rules = contract.get("rules", []) if isinstance(contract, dict) else (contract or [])
    if not contract_rules:
        # Fallback: map felt constraints (value_numeric, no string value) to rule-shaped dicts.
        contract_rules = [{**constraint, "value": constraint.get("value_numeric")} for constraint in constraints]
    if contract_rules:
        st.markdown("<div class='section-head' style='font-size:16px;'>Verified GIS rules</div>", unsafe_allow_html=True)
        st.caption("Every verified rule in plain English. Download the machine-readable contract below.")
        _rule_sentence_list(st, contract_rules)
    download_columns = st.columns(2)
    if contract_path.exists():
        download_columns[0].download_button(
            "Download gis_rule_contract.json",
            contract_path.read_text(encoding="utf-8"),
            file_name="gis_rule_contract.json",
            mime="application/json",
        )
    if felt_path.exists():
        download_columns[1].download_button(
            "Download gis_felt_export.json",
            felt_path.read_text(encoding="utf-8"),
            file_name="gis_felt_export.json",
            mime="application/json",
        )


def _sidebar_status_legend(st: Any) -> None:
    st.sidebar.markdown(
        "<div style='display:flex;gap:6px;flex-wrap:wrap;margin:8px 0 2px;'>"
        "<span class='status-pill status-verified'>Verified</span>"
        "<span class='status-pill status-review'>Review</span>"
        "<span class='status-pill status-rejected'>Rejected</span>"
        "<span class='status-pill status-not_used'>Not used</span>"
        "</div>",
        unsafe_allow_html=True,
    )


_ADVANCED_VIEWS = (
    "(none)",
    "Coverage vs gold",
    "Pipeline comparison",
    "Evidence repair",
    "Shadow reruns",
    "Engineering details",
)


def _sidebar_advanced(st: Any) -> str:
    with st.sidebar.expander("Advanced & diagnostics", expanded=False):
        return st.radio(
            "Engineering view",
            _ADVANCED_VIEWS,
            key="adv_view",
            help="Diagnostic artifacts for engineers; not part of the reviewer workflow. Renders below the tabs.",
        )


def _render_advanced_view(st: Any, view: str, data: dict[str, Any], output_dir: Path) -> None:
    if view == "Coverage vs gold":
        _coverage_tab(st, data, output_dir)
    elif view == "Pipeline comparison":
        _pipeline_comparison_tab(st, output_dir)
    elif view == "Evidence repair":
        _repair_tab(st, data["repair"])
    elif view == "Shadow reruns":
        _rerun_tab(st, data["rerun"], data["evidence_units"])
    elif view == "Engineering details":
        _advanced_tab(st, data, output_dir)


def _diagnostics_page(st: Any, data: dict[str, Any], output_dir: Path) -> None:
    """Engineering & audit views, now a normal nav page (was the below-tabs door)."""
    st.markdown("<div class='section-head'>Diagnostics</div>", unsafe_allow_html=True)
    st.markdown(
        "<p class='section-sub'>Engineering & audit views — not part of the reviewer workflow.</p>",
        unsafe_allow_html=True,
    )
    options = list(_ADVANCED_VIEWS[1:])  # skip "(none)"
    view = st.radio("View", options, horizontal=True, key="diag_view", label_visibility="collapsed")
    st.divider()
    _render_advanced_view(st, view, data, output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args, _ = parser.parse_known_args()
    cli_output_dir = Path(args.output_dir).expanduser().resolve()

    try:
        import streamlit as st
    except ModuleNotFoundError as exc:
        raise SystemExit("Streamlit is not installed. Run `pip install -r requirements.txt`.") from exc

    st.set_page_config(
        page_title="BC Zoning Verification Dashboard",
        page_icon="BV",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _style(st)

    # City selector: scan outputs/ for any *_slim_pipeline5_registry dir with
    # verified_rules.json. New cities appear automatically; nothing is hardcoded.
    city_dirs = discover_product_output_dirs()
    if (
        cli_output_dir.is_dir()
        and cli_output_dir not in city_dirs
        and native_run_root(cli_output_dir) in PRODUCT_RUN_ROOTS
    ):
        city_dirs = [*city_dirs, cli_output_dir]
    if not city_dirs:
        st.error(f"No verifier output directories found under `{OUTPUTS_ROOT}`.")
        return
    st.sidebar.markdown(
        """
<div class="sidebar-brand">
  <div class="brand-mark">BV</div>
  <div class="brand-title">Bylaw Verification<br>Dashboard</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("<div class='nav-title'>Current run</div>", unsafe_allow_html=True)
    default_index = 0
    for index, path in enumerate(city_dirs):
        if city_stem_from_dir(path) == "burnaby_r1":
            default_index = index
            break
    selection = st.sidebar.selectbox(
        "City output",
        city_dirs,
        index=default_index,
        format_func=city_label_from_dir,
        label_visibility="collapsed",
        help="Pick a current M7 city output. The dashboard remains read-only.",
    )
    output_dir = selection
    city_key = city_key_from_dir(output_dir)
    city_label = city_label_from_dir(output_dir)

    data = load_output_data(output_dir)
    source_url = source_document_url_for_output(output_dir, data)
    _ACTIVE_SOURCE["url"] = source_url
    _ACTIVE_SOURCE["label"] = f"{city_label} bylaw PDF"

    # Reviewer queue source (filters now live inline on the Review Queue tab).
    triage_items = data["review"]

    st.sidebar.markdown(
        f"""
<div class="sidebar-run">
  <span>Source document</span>
  <a href="{html.escape(source_url)}" target="_blank">Open official PDF</a>
</div>
""",
        unsafe_allow_html=True,
    )

    pipeline_nav = [
        ("0 Results + Chat", "Overview"),
        ("1 Source Documents", "Source Documents"),
        ("2 Verified Rules", "Verified Rules"),
        ("3 Human Review", "Human Review"),
        ("4 Repair Evidence", "Repair Evidence"),
        ("5 GIS Handoff", "GIS Handoff"),
        ("6 Quality Audit", "Quality Checks"),
    ]
    nav_lookup = dict(pipeline_nav)
    st.sidebar.markdown("<div class='nav-title'>Pipeline order</div>", unsafe_allow_html=True)
    nav_label = st.sidebar.radio(
        "Pipeline",
        [label for label, _ in pipeline_nav],
        key="primary_nav",
        label_visibility="collapsed",
    )
    nav = nav_lookup[nav_label]
    st.sidebar.markdown(
        """
<div class="pipeline-note">
  <b>One rule</b>
  <span>Verified items move forward. Uncertain items stay in review.</span>
</div>
""",
        unsafe_allow_html=True,
    )

    if nav == "Overview":
        _overview_console_page(st, data, output_dir, source_url)
    else:
        _render_header(st, city_label, section=nav)

    if nav == "Verified Rules":
        _verified_rules_page(st, data)
    elif nav == "Human Review":
        _review_queue_tab(st, data, output_dir, triage_items)
    elif nav == "Repair Evidence":
        _repair_page(st, data)
    elif nav == "Source Documents":
        _source_library_page(st, data, source_url)
    elif nav == "GIS Handoff":
        _gis_handoff_tab(st, data, output_dir)
    elif nav == "Quality Checks":
        _analytics_page(st, data)


def count_audit_status(slot_audit: dict[str, Any]) -> str:
    metrics = (slot_audit or {}).get("slot_metrics") or {}
    if not metrics:
        return "not available"
    unsupported = int(metrics.get("unsupported_verified_rule_count") or 0)
    unresolved_duplicates = int(metrics.get("duplicate_verified_slot_count") or 0)
    mapping_rate = float(metrics.get("verified_slot_mapping_rate") or 0)
    if unsupported or unresolved_duplicates or mapping_rate < 1.0:
        return "too much risk"
    review = int(metrics.get("scored_review_slot_count", metrics.get("review_slot_count")) or 0)
    missed = int(metrics.get("scored_missed_slot_count", metrics.get("missed_slot_count")) or 0)
    if review or missed:
        return "safe but conservative"
    return "balanced"


def _format_coverage(value: Any) -> Any:
    if isinstance(value, (int, float)):
        return f"{round(float(value) * 100)}%"
    return value


def count_audit_summary_rows(slot_audit: dict[str, Any], reconciliation: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    metrics = (slot_audit or {}).get("slot_metrics") or {}
    reconciliation = reconciliation or {}
    if not metrics:
        return []
    safety_and_delta = [
        {"metric": "Duplicate merged", "value": metrics.get("duplicate_merged_count"), "meaning": "not counted twice"},
        {"metric": "Unsupported verified", "value": metrics.get("unsupported_verified_rule_count"), "meaning": "must be zero"},
        {
            "metric": "Verified slot delta from M4",
            "value": reconciliation.get("effective_verified_slot_count_delta"),
            "meaning": "unique verified-slot change",
        },
    ]
    # M5.6: lead with the scored denominator (in-contract, recognized-family,
    # corpus-derived, deduped to distinct legal rules). The raw ledger stays
    # visible but is labelled an advisory over-count ceiling, not a legal total.
    if metrics.get("distinct_scored_legal_slot_count") is not None:
        return [
            {"metric": "Scored legal slots", "value": metrics.get("distinct_scored_legal_slot_count"), "meaning": "in-contract distinct legal rules (honest denominator)"},
            {"metric": "Verified coverage", "value": _format_coverage(metrics.get("scored_verified_coverage")), "meaning": "scored slots that are verified"},
            {"metric": "Scored verified", "value": metrics.get("scored_verified_slot_count"), "meaning": "distinct legal rules proven"},
            {"metric": "Scored review-only", "value": metrics.get("scored_review_slot_count"), "meaning": "safe, awaiting proof"},
            {"metric": "Scored missed", "value": metrics.get("scored_missed_slot_count"), "meaning": "actionable backlog"},
            {"metric": "Raw rule slots (advisory)", "value": metrics.get("total_rule_slots"), "meaning": "loose over-count ceiling, not a legal total"},
            {"metric": "Unique verified slots", "value": metrics.get("effective_verified_slot_count"), "meaning": "deduplicated verifier output"},
            *safety_and_delta,
        ]
    return [
        {"metric": "Rule slots", "value": metrics.get("total_rule_slots"), "meaning": "source-derived denominator"},
        {"metric": "Raw verified rules", "value": metrics.get("verified_rule_count"), "meaning": "verifier output rows"},
        {"metric": "Unique verified slots", "value": metrics.get("effective_verified_slot_count"), "meaning": "deduplicated count"},
        {"metric": "Review slots", "value": metrics.get("review_slot_count"), "meaning": "safe but not fully proven"},
        {"metric": "Candidate-only slots", "value": metrics.get("candidate_only_slot_count"), "meaning": "extracted but not proven"},
        {"metric": "Missed slots", "value": metrics.get("missed_slot_count"), "meaning": "no mapped candidate yet"},
        *safety_and_delta,
    ]


def _count_audit_panel(st: Any, data: dict[str, Any]) -> None:
    slot_audit = data.get("slot_audit") or {}
    rows = count_audit_summary_rows(slot_audit, data.get("m55_reconciliation") or {})
    if not rows:
        st.info("M6 slot audit not found for this output. Run the measurement layer to answer too much vs too little precisely.")
        return
    status = count_audit_status(slot_audit)
    st.markdown("#### Too Much / Too Little")
    st.caption(
        "This panel leads with the M6 scored legal denominator and keeps raw slots as an advisory over-count. "
        "Unsupported verified rules mean too much; scored review or missed slots mean conservative coverage."
    )
    st.markdown(f"<div class='trust-note'><b>Count status:</b> {html.escape(_plain_label(status))}</div>", unsafe_allow_html=True)
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)


def _not_used_explanation(st: Any, data: dict[str, Any]) -> None:
    not_used = data.get("not_used") or []
    if not not_used:
        return
    reason_counts = Counter(
        str(gap)
        for rule in not_used
        for gap in (rule.get("support_gaps") or [])
    )
    family_counts = Counter(str(rule.get("rule_object") or "unknown") for rule in not_used)
    if reason_counts.get("outside_target_section"):
        explanation = (
            "These candidates came from the full bylaw but outside the configured target sections. "
            "They are kept for audit and review, not trusted as verified rules."
        )
    else:
        explanation = "These candidates are retained for traceability but are outside the current verified-rule output contract."
    st.markdown("#### Out-of-scope candidates")
    st.caption(explanation)
    rows = [
        {"type": "Reason", "name": _plain_label(name), "count": count}
        for name, count in reason_counts.most_common(6)
    ] + [
        {"type": "Rule family", "name": _plain_label(name), "count": count}
        for name, count in family_counts.most_common(6)
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)


def _advanced_tab(st: Any, data: dict[str, Any], output_dir: Path) -> None:
    st.subheader("Advanced Diagnostics")
    st.caption("Engineering and audit views. These explain why the system behaved a certain way; they do not approve rules.")
    diagnostic = st.selectbox(
        "Diagnostic view",
        [
            "Rule Graph",
            "Review Resolution",
            "Semantic Review",
            "Evidence Intelligence",
            "Evidence Bundle Rerun",
            "Safe Verifier Tuning",
            "Run Cost & Source",
            "Shadow Examiner",
            "Verification Structure",
            "Extraction Preflight",
        ],
        help="Keep this section for debugging, tuning, and audit. The main review workflow is in Review Workbench.",
    )
    if diagnostic == "Rule Graph":
        _rule_graph_tab(st, data["rule_graph"])
    elif diagnostic == "Review Resolution":
        _review_resolution_tab(st, data["resolution"])
    elif diagnostic == "Semantic Review":
        _semantic_review_tab(st, data["semantic"])
    elif diagnostic == "Evidence Intelligence":
        _evidence_intelligence_tab(st, data["intelligence"])
    elif diagnostic == "Evidence Bundle Rerun":
        _bundle_rerun_tab(st, data["bundle_rerun"])
    elif diagnostic == "Safe Verifier Tuning":
        _safe_tuning_tab(st, data["safe_tuning"], data["evidence_units"])
    elif diagnostic == "Run Cost & Source":
        _run_cost_source_tab(st, data)
    elif diagnostic == "Shadow Examiner":
        _shadow_examiner_tab(st, data)
    elif diagnostic == "Verification Structure":
        _structure_tab(st)
    elif diagnostic == "Extraction Preflight":
        _preflight_tab(st, data["preflight"])


def pipeline_comparison_rows(output_dir: Path) -> list[dict[str, Any]]:
    """Return native and legacy comparison rows for the selected city stem."""
    stem = city_stem_from_dir(output_dir)
    candidates = [
        ("Native M7", OUTPUTS_ROOT / "m7_runs" / stem / "google_gemini_3_1_flash_lite"),
        ("Native V3", OUTPUTS_ROOT / "v3_runs" / stem / "google_gemini_2_5_flash_lite"),
    ]
    rows: list[dict[str, Any]] = []
    for label, path in candidates:
        if not path.exists():
            continue
        summary = _read_json(path / "slim_summary.json", {})
        benchmark = _read_json(path / "benchmark_report.json", {})
        metrics = benchmark.get("rule_metrics", {})
        cost = _read_json(path / "model_cost_report.json", {})
        gates = benchmark.get("quality_gates", {})
        status = pipeline_gate_status(summary, benchmark)
        rows.append(
            {
                "pipeline": label,
                "path": path.name,
                "candidates": summary.get("candidate_rule_count"),
                "evidence_blocks": summary.get("evidence_unit_count"),
                "verified": summary.get("verified_rule_count"),
                "review": summary.get("review_rule_count"),
                "rejected": summary.get("rejected_rule_count"),
                "not_used": summary.get("not_used_rule_count"),
                "precision": metrics.get("verified_precision"),
                "false_verified": metrics.get("false_verified_count"),
                "verified_or_review_recall": metrics.get("verified_or_review_recall"),
                "estimated_cost": cost.get("estimated_cost_usd"),
                "gate_status": status,
                "status_meaning": HELP_TEXT.get("native_m7" if label == "Native M7" else status, HELP_TEXT.get(status, "")),
            }
        )
    return rows


def pipeline_gate_status(summary: dict[str, Any], benchmark: dict[str, Any]) -> str:
    """Human label for benchmark state; keeps P9 failures honest."""
    if not summary:
        return "missing"
    quality = benchmark.get("quality_gates", {})
    if quality.get("passed") is True:
        return "pass"
    metrics = benchmark.get("rule_metrics", {})
    proposal = benchmark.get("proposal_metrics", {})
    false_verified = int(metrics.get("false_verified_count") or 0)
    false_approval = int(proposal.get("false_approval_count") or metrics.get("false_approval_count") or 0)
    candidates = int(summary.get("candidate_rule_count") or 0)
    verified = int(summary.get("verified_rule_count") or 0)
    review = int(summary.get("review_rule_count") or 0)
    rejected = int(summary.get("rejected_rule_count") or 0)
    not_used = int(summary.get("not_used_rule_count") or 0)
    if false_verified or false_approval:
        return "unsafe / needs fix"
    if verified == 0 and review:
        return "fail-closed"
    if candidates and not_used >= max(1, verified + review + rejected):
        return "scope mismatch"
    return "needs review"


def _pipeline_comparison_tab(st: Any, output_dir: Path) -> None:
    st.subheader("Pipeline Comparison")
    st.caption(
        "M4 is current. V3 is the direct predecessor M4 was built from. "
        "Recall is benchmark recall, not full-bylaw completeness."
    )
    rows = pipeline_comparison_rows(output_dir)
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)


def _run_cost_source_tab(st: Any, data: dict[str, Any]) -> None:
    st.subheader("Run Cost & Source")
    st.caption("Source, retrieval, and cost artifacts are advisory/debug records. The verifier JSON files remain authoritative.")
    source = data.get("source_summary") or {}
    cost = data.get("model_cost") or {}
    if not source and not cost:
        st.info("No source or model-cost artifact found for this output.")
        return
    left, right = st.columns(2)
    with left:
        st.markdown("#### Full-bylaw source cache")
        m4_source = source.get("m4_source_corpus") or {}
        m4_manifest = _read_json(Path(m4_source.get("path") or "") / "manifest.json", {})
        rows = [
            {"metric": "Full PDF pages", "value": m4_manifest.get("page_count")},
            {"metric": "Source chunks", "value": source.get("source_chunk_count")},
            {"metric": "Evidence packs", "value": source.get("evidence_pack_count")},
            {"metric": "Pages with chunks", "value": source.get("page_count")},
            {"metric": "Last page", "value": source.get("last_page")},
            {"metric": "Rule-like numeric clauses", "value": m4_source.get("rule_like_numeric_clause_count")},
            {"metric": "Selected rule-like coverage", "value": m4_source.get("selected_rule_like_numeric_coverage")},
            {"metric": "Discovery version", "value": source.get("discovery_version")},
        ]
        st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
        if source.get("lane_counts"):
            st.markdown("#### Pack lanes")
            _bar_rows(st, source.get("lane_counts", []), "name", "count")
    with right:
        st.markdown("#### Model run cost")
        rows = [
            {"metric": "Model", "value": cost.get("model")},
            {"metric": "Estimated cost", "value": cost.get("estimated_cost_usd")},
            {"metric": "Latency ms", "value": cost.get("latency_ms")},
            {"metric": "Input tokens", "value": cost.get("estimated_input_tokens")},
            {"metric": "Output tokens", "value": cost.get("estimated_output_tokens")},
            {"metric": "Cache hits", "value": cost.get("cache_hit_count")},
            {"metric": "Extraction errors", "value": cost.get("extraction_error_count")},
        ]
        st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
        st.caption(cost.get("pricing_note") or "Cost estimates are advisory.")


def _shadow_examiner_tab(st: Any, data: dict[str, Any]) -> None:
    st.subheader("Shadow Examiner")
    st.caption("Private developer diagnostics. These findings cannot verify, reject, or approve rules.")
    examiner = data.get("examiner") or {}
    if not examiner:
        st.info("No shadow examiner report found for this output.")
        return
    summary = examiner.get("summary", {})
    st.table(
        _display_rows(
            [
                {"metric": "Mode", "value": examiner.get("mode")},
                {"metric": "Model", "value": examiner.get("model")},
                {"metric": "Findings", "value": summary.get("finding_count")},
                {"metric": "False verified", "value": summary.get("false_verified_count")},
                {"metric": "Verified or review recall", "value": summary.get("verified_or_review_recall")},
            ]
        )
    )
    findings = examiner.get("findings", [])
    if findings:
        st.markdown("#### Findings")
        st.dataframe(
            _display_rows(
                [
                    {
                        "severity": item.get("severity"),
                        "category": item.get("category"),
                        "claim": item.get("claim"),
                        "suggested_test": item.get("suggested_test"),
                    }
                    for item in findings
                ]
            ),
            width="stretch",
            hide_index=True,
        )
        selected = st.selectbox("Finding detail", [item.get("finding_id") for item in findings])
        item = next((row for row in findings if row.get("finding_id") == selected), findings[0])
        st.markdown("#### Evidence")
        st.code(str(item.get("evidence") or ""), language="text")
        st.markdown("#### Suggestion")
        st.write(item.get("suggestion") or "")
    rerun = data.get("examiner_rerun") or {}
    if rerun.get("actions"):
        st.markdown("#### Suggested reruns")
        st.dataframe(_display_rows(rerun.get("actions", [])), width="stretch", hide_index=True)


def _packet_by_rule_id(packet_report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("rule_id") or ""): item for item in packet_report.get("items", [])}


def _review_assistant_tab(
    st: Any,
    packet_report: dict[str, Any],
    review_rules: list[dict[str, Any]],
    output_dir: Path,
    evidence_by_id: dict[str, dict[str, Any]],
) -> None:
    st.subheader("Review One Rule")
    st.caption(
        "Pick a held rule, inspect the source evidence, and ask an optional LLM for an explanation. The LLM cannot approve anything."
    )
    packet_by_rule = _packet_by_rule_id(packet_report)
    if not review_rules:
        st.info("No review-needed rules in this output.")
        return
    options = [str(rule.get("rule_id")) for rule in review_rules if rule.get("rule_id")]
    rule_lookup = {str(rule.get("rule_id")): rule for rule in review_rules if rule.get("rule_id")}
    selected_id = st.selectbox(
        "Rule to inspect",
        options,
        key=f"assistant_rule_{output_dir.name}",
        format_func=lambda rule_id: _rule_option_label(rule_lookup.get(str(rule_id), {})),
        help="These are candidates the verifier refused to prove. Pick one to inspect its evidence and missing support.",
    )
    rule = _by_rule_id(review_rules, selected_id)
    packet = packet_by_rule.get(selected_id, {})
    if not packet:
        st.warning("No prebuilt review assistant packet found. Rerun the slim verifier to generate review_assistant_packets.json.")
        packet = _fallback_packet(rule)

    left, right = st.columns([1, 1])
    with left:
        st.markdown("#### Candidate")
        st.markdown(
            f"<div class='sentence-card sentence-review'>{_review_sentence_html(rule)}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("**Fields**")
        st.markdown(_rule_fields_md(rule))
        st.info(packet.get("suggested_next_action") or "Inspect the source evidence before any verifier rerun.")
    with right:
        source = packet.get("source", {})
        st.markdown("#### Source evidence")
        st.caption(
            f"Page {source.get('page') or 'unknown'} · evidence `{source.get('evidence_id') or ''}` · "
            f"context status: {_plain_label(source.get('repair_status') or 'unknown')}"
        )
        st.markdown("*Extractor evidence*")
        st.code(source.get("original_evidence") or _source_text(rule), language="text")
        st.markdown("*Source context added before verification*")
        repaired = source.get("repaired_context")
        if repaired:
            st.code(repaired, language="text")
        else:
            st.caption("No repaired context available.")

    _legal_context_expander(st, output_dir, rule, evidence_by_id)

    st.caption(
        "Want a free-form explanation? Use the **Ask the Bylaw** tab — the source-grounded chatbot "
        "answers questions about this section and cites where it came from. (It is advisory and can "
        "never approve, verify, or change a rule.)"
    )


def _fallback_packet(rule: dict[str, Any]) -> dict[str, Any]:
    source = rule.get("source", {}) if isinstance(rule.get("source"), dict) else {}
    return {
        "rule_id": rule.get("rule_id"),
        "candidate_rule": compact_rule_row(rule),
        "support_gaps": list(rule.get("support_gaps", [])),
        "suggested_next_action": "Inspect the source evidence and rerun deterministic verification only after evidence is repaired.",
        "source": {
            "page": source.get("page"),
            "evidence_id": source.get("evidence_id"),
            "original_evidence": source.get("evidence_text"),
            "repaired_context": source.get("source_context"),
            "repair_status": "fallback",
        },
    }


def proof_trace_lines(rule: dict[str, Any], limit_per_field: int = 140) -> list[str]:
    """Per-field proof labels as short lines for the assistant prompt.

    The assistant previously saw only the rule JSON + gap codes; the proof
    trace is the verifier's actual reasoning ("operator: not_enough_info —
    'the proposed operator is not supported…'") and is what a reviewer needs
    to answer "why is this in review?".
    """
    trace = rule.get("proof_trace") or rule.get("merged_proof_trace") or {}
    lines: list[str] = []
    for claim, item in trace.items():
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "")
        reason = str(item.get("reason") or "")[:limit_per_field]
        if label and label != "supported":
            lines.append(f"{claim}: {label} \u2014 {reason}")
    return lines[:8]


def suggested_review_questions(packet: dict[str, Any]) -> list[str]:
    """Gap-aware question chips for the review assistant."""
    questions = ["Why is this rule in review?"]
    by_gap = {
        "operator_not_supported": "What wording would prove the direction (minimum/maximum)?",
        "applies_to_not_supported": "What nearby text would prove what this applies to?",
        "table_condition_not_supported": "Which condition is the table column carrying?",
        "conditional_cell_condition_missing": "What lot-size branch does this value belong to?",
        "column_qualifier_not_claimed": "What column qualifier is this claim missing?",
        "unresolved_exception_cue": "What exception wording is unresolved here?",
        "pipeline5_text_candidate_requires_review": "What second source would corroborate this rule?",
        "rule_family_direction_mismatch": "Is this bound in the wrong direction for its family?",
    }
    for gap in packet.get("support_gaps") or []:
        question = by_gap.get(str(gap))
        if question and question not in questions:
            questions.append(question)
    return questions[:4]


def _assistant_prompt(packet: dict[str, Any], question: str) -> str:
    context = packet.get("llm_context") or {
        "instruction": "Advisory only. Do not approve or verify.",
        "rule": packet.get("candidate_rule", {}),
        "support_gaps": packet.get("support_gaps", []),
        "original_evidence": (packet.get("source") or {}).get("original_evidence"),
        "repaired_context": (packet.get("source") or {}).get("repaired_context"),
        "suggested_next_action": packet.get("suggested_next_action"),
    }
    trace_lines = proof_trace_lines(packet.get("candidate_rule") or packet)
    proof_block = ("Proof trace (unproven fields):\n" + "\n".join(trace_lines) + "\n") if trace_lines else ""
    return (
        f"{context.get('instruction')}\n\n"
        f"Rule: {json.dumps(context.get('rule', {}), ensure_ascii=False)}\n"
        f"Support gaps: {', '.join(str(gap) for gap in context.get('support_gaps', [])) or 'none'}\n"
        f"{proof_block}"
        f"Original evidence: {context.get('original_evidence') or ''}\n"
        f"Repaired context: {context.get('repaired_context') or ''}\n"
        f"Suggested next action: {context.get('suggested_next_action') or ''}\n\n"
        f"Reviewer question: {question or 'Explain why this item is still in review.'}\n\n"
        "Answer briefly. Cite only the evidence above. Do not say this rule is approved or verified."
    )


def _optional_llm_review_answer(prompt: str) -> str | None:
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    if not api_key:
        return None
    try:  # pragma: no cover - optional interactive network path
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-opus-4-8"),
            max_tokens=700,
            system="You are an advisory zoning review assistant. Never approve or verify rules.",
            messages=[{"role": "user", "content": prompt}],
        )
        return "\n".join(block.text for block in response.content if getattr(block, "type", "") == "text").strip()
    except Exception as error:
        return f"LLM unavailable: {type(error).__name__}: {error}"


def _evidence_intelligence_tab(st: Any, report: dict[str, Any]) -> None:
    items = report.get("items", [])
    st.subheader("Evidence Intelligence")
    st.caption("Rule-centric evidence ranking and bundle suggestions. This page does not verify rules.")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Review Rules", report.get("review_rule_count", len(items)))
    metric_cols[1].metric("Evidence Indexed", report.get("evidence_index_count", 0))
    metric_cols[2].metric("Safe Bundle Retry", report.get("safe_retry_count", 0))
    metric_cols[3].metric("Blocked", report.get("blocked_count", 0))

    summary = report.get("summary", {})
    left, right = st.columns(2)
    with left:
        st.markdown("### Next Actions")
        _bar_rows(st, summary.get("next_action_counts", []), "name", "count")
    with right:
        st.markdown("### Missing Fields")
        _bar_rows(st, summary.get("missing_field_counts", []), "name", "count")

    if not items:
        st.info("No evidence intelligence output found. Rerun the slim verifier.")
        return
    only_safe = st.checkbox("Show safe bundle retry only")
    visible = [item for item in items if item.get("safe_retry")] if only_safe else items
    rows = [
        {
            "rule_id": item.get("rule_id"),
            "safe_retry": item.get("safe_retry"),
            "score": item.get("bundle_score"),
            "next_action": item.get("next_action"),
            "rule_object": item.get("rule_object"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "missing_fields": ", ".join(item.get("bundle_missing_fields", [])),
            "blocked_by": ", ".join(item.get("blocked_by", [])),
        }
        for item in visible[:250]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if visible:
        selected = st.selectbox("Evidence intelligence detail", [item["rule_id"] for item in visible])
        item = next(candidate for candidate in visible if candidate["rule_id"] == selected)
        _detail_sentence_panel(
            st,
            "Evidence intelligence in plain English",
            _intelligence_detail_sentences(item),
            _bundle_display_evidence(item),
            item,
        )
        st.markdown("#### Best Evidence Bundle")
        st.dataframe(_display_rows(_bundle_rows(item)), width="stretch", hide_index=True)
        with st.expander("Raw evidence intelligence JSON"):
            st.json(item)


def _review_router_tab(st: Any, report: dict[str, Any]) -> None:
    items = report.get("items", [])
    st.subheader("Queue Summary")
    st.caption("A plain-language worklist for the rules still in review. These labels guide reviewers; they do not approve rules.")
    summary = report.get("summary", {})
    left, middle, right = st.columns(3)
    with left:
        st.markdown("#### Suggested work")
        _bar_rows(st, summary.get("action_counts", []), "name", "count")
    with middle:
        st.markdown("#### Why held")
        _bar_rows(st, summary.get("category_counts", []), "name", "count")
    with right:
        st.markdown("#### Meaning check")
        _bar_rows(st, summary.get("semantic_review_counts", []), "name", "count")

    if not items:
        st.info("No review router output found. Rerun the slim verifier.")
        return
    actions = st.multiselect("Suggested work", _unique(items, "action_bucket"), format_func=_plain_label)
    categories = st.multiselect("Why held", _unique(items, "review_category"), format_func=_plain_label)
    semantic_classes = st.multiselect("Meaning check", _unique(items, "semantic_review_class"), format_func=_plain_label)
    visible = items
    if actions:
        visible = [item for item in visible if item.get("action_bucket") in actions]
    if categories:
        visible = [item for item in visible if item.get("review_category") in categories]
    if semantic_classes:
        visible = [item for item in visible if item.get("semantic_review_class") in semantic_classes]
    rows = [
        {
            "Rule ID": item.get("rule_id"),
            "Why held": item.get("review_category"),
            "Suggested work": item.get("action_bucket"),
            "Explanation": HELP_TEXT.get(str(item.get("action_bucket") or ""), ""),
            "Urgency": item.get("priority"),
            "Rule family": item.get("rule_object"),
            "Meaning check": item.get("semantic_review_class"),
            "Meaning score": item.get("semantic_score"),
            "Closest verified rule": item.get("semantic_verified_rule_id"),
            "Still missing": ", ".join(item.get("semantic_guardrail_blockers", [])),
            "Evidence bundle safe": item.get("bundle_safe_retry"),
            "Bundle ready": item.get("bundle_rerun_promotion_ready"),
            "Next step": item.get("next_step"),
        }
        for item in visible[:250]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if visible:
        selected = st.selectbox(
            "Queue item detail",
            [item["rule_id"] for item in visible],
            format_func=lambda rule_id: _rule_option_label(next((item for item in visible if item.get("rule_id") == rule_id), {})),
        )
        item = next(candidate for candidate in visible if candidate["rule_id"] == selected)
        _detail_sentence_panel(
            st,
            "Review route in plain English",
            _router_detail_sentences(item),
            {"evidence_quote": item.get("evidence_sentence")},
            item,
        )
        with st.expander("Raw route JSON"):
            st.json(item)


def _review_resolution_tab(st: Any, report: dict[str, Any]) -> None:
    """Show final reviewer-facing resolution labels for remaining review items."""
    items = report.get("items", [])
    st.subheader("Review Resolution")
    st.caption(
        "Final operating labels for the remaining review queue. This page tells a reviewer what kind of work is left; it does not promote rules."
    )
    summary = report.get("summary", {})
    metric_cols = st.columns(4)
    metric_cols[0].metric("Review Rules", report.get("review_rule_count", len(items)))
    metric_cols[1].metric("Evidence-Fix Candidates", summary.get("can_promote_after_evidence_fix_count", 0))
    metric_cols[2].metric("Semantic Duplicates", summary.get("duplicate_or_degraded_count", 0))
    metric_cols[3].metric("Promotable Now", summary.get("promotable_now_count", 0))

    left, right = st.columns(2)
    with left:
        st.markdown("### Resolution Buckets")
        _bar_rows(st, summary.get("resolution_counts", []), "name", "count")
    with right:
        st.markdown("### Next Step Types")
        _bar_rows(st, summary.get("next_step_type_counts", []), "name", "count")

    recommendations = summary.get("recommendations", [])
    if recommendations:
        st.markdown("### Recommended Workflow")
        for item in recommendations:
            st.markdown(f"- {item}")

    if not items:
        st.info("No review resolution output found. Rerun the slim verifier.")
        return
    buckets = st.multiselect("Resolution", _unique(items, "resolution"), format_func=_plain_label)
    next_steps = st.multiselect("Next step type", _unique(items, "next_step_type"), format_func=_plain_label)
    visible = items
    if buckets:
        visible = [item for item in visible if item.get("resolution") in buckets]
    if next_steps:
        visible = [item for item in visible if item.get("next_step_type") in next_steps]

    rows = [
        {
            "rule_id": item.get("rule_id"),
            "resolution": item.get("resolution"),
            "next_step": item.get("next_step_type"),
            "can_promote_after_fix": item.get("can_promote_after_evidence_fix"),
            "rule_object": item.get("rule_object"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "semantic_match": item.get("semantic_verified_rule_id"),
            "semantic_score": item.get("semantic_score"),
            "gaps": ", ".join(item.get("support_gaps", [])[:4]),
            "page": item.get("source_page"),
            "evidence_id": item.get("source_evidence_id"),
            "where": item.get("where_to_find_it"),
        }
        for item in visible[:250]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if visible:
        selected = st.selectbox("Resolution detail", [item["rule_id"] for item in visible])
        item = next(candidate for candidate in visible if candidate["rule_id"] == selected)
        _detail_sentence_panel(
            st,
            "Resolution in plain English",
            _resolution_detail_sentences(item),
            {"evidence_quote": item.get("evidence_sentence"), "page": item.get("source_page")},
            item,
        )
        with st.expander("Raw resolution JSON"):
            st.json(item)


def _bundle_rerun_tab(st: Any, report: dict[str, Any]) -> None:
    attempts = report.get("attempts", [])
    st.subheader("Evidence Bundle Rerun")
    st.caption("Shadow-mode rerun using the best evidence bundle. Bundle score cannot verify a rule by itself.")
    metric_cols = st.columns(6)
    metric_cols[0].metric("Attempts", report.get("attempt_count", len(attempts)))
    metric_cols[1].metric("Verified After Rerun", report.get("verified_after_rerun_count", 0))
    metric_cols[2].metric("Promotion Ready", report.get("promotion_ready_count", 0))
    metric_cols[3].metric("Still Review", report.get("review_after_rerun_count", 0))
    metric_cols[4].metric("Rejected", report.get("rejected_after_rerun_count", 0))
    metric_cols[5].metric("Skipped", report.get("skipped_count", 0))
    if not attempts:
        st.info("No bundle rerun attempts found.")
        return
    only_ready = st.checkbox("Promotion-ready bundle reruns only")
    visible = [item for item in attempts if item.get("promotion_ready")] if only_ready else attempts
    rows = [
        {
            "rule_id": item.get("original_rule_id"),
            "decision": item.get("retry_decision"),
            "ready": item.get("promotion_ready"),
            "score": item.get("bundle_score"),
            "rule_object": item.get("rule_object"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "bundle_ids": ", ".join(str(value) for value in item.get("bundle_evidence_ids", [])),
            "missing": ", ".join(item.get("bundle_missing_fields", [])),
            "risk_flags": ", ".join(item.get("promotion_risk_flags", [])),
            "gaps": ", ".join(item.get("retry_support_gaps", [])[:4]),
        }
        for item in visible[:250]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if visible:
        selected = st.selectbox("Bundle rerun detail", [item["original_rule_id"] for item in visible])
        item = next(candidate for candidate in visible if candidate["original_rule_id"] == selected)
        _detail_sentence_panel(
            st,
            "Bundle rerun in plain English",
            _bundle_rerun_detail_sentences(item),
            {"page": "", "evidence_quote": item.get("bundle_evidence_quote")},
            item,
        )
        with st.expander("Raw bundle rerun JSON"):
            st.json(item)


def _semantic_review_tab(st: Any, report: dict[str, Any]) -> None:
    items = report.get("items", [])
    st.subheader("Semantic Review")
    st.caption("Structured meaning comparison plus optional MiniLM embedding similarity. Advisory only; it cannot clear support gaps.")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Review Rules", report.get("review_rule_count", len(items)))
    metric_cols[1].metric("Verified Rules Compared", report.get("verified_rule_count", 0))
    metric_cols[2].metric("High Similarity", report.get("high_similarity_count", 0))
    embedding = report.get("embedding", {})
    metric_cols[3].metric("Embedding Mode", embedding.get("mode", "unknown"))
    if embedding:
        st.caption(
            f"Embedding backend: {embedding.get('model') or 'none'} "
            f"({ 'available' if embedding.get('available') else embedding.get('reason', 'unavailable') })."
        )
    actions = report.get("summary", {}).get("semantic_action_counts", [])
    if actions:
        st.markdown("### Semantic Next Actions")
        _bar_rows(st, actions, "name", "count")
    if not items:
        st.info("No semantic review report found. Rerun the slim verifier.")
        return
    threshold = st.slider("Minimum meaning score", 0.0, 1.0, 0.70, 0.05)
    visible = [item for item in items if float(item.get("best_semantic_score") or 0.0) >= threshold]
    rows = []
    for item in visible[:250]:
        top = item.get("best_verified_matches", [{}])[0] if item.get("best_verified_matches") else {}
        rows.append(
            {
                "rule_id": item.get("rule_id"),
                "combined_score": item.get("best_combined_semantic_score", item.get("best_semantic_score")),
                "structured_score": item.get("best_structured_score"),
                "embedding_score": item.get("best_embedding_score"),
                "match_type": item.get("semantic_match_type"),
                "action": item.get("semantic_next_action"),
                "matched_verified": top.get("verified_rule_id"),
                "guardrail_blockers": ", ".join(item.get("semantic_guardrail_blockers", [])),
                "reasons": ", ".join(top.get("match_reasons", [])),
                "support_gaps": ", ".join(item.get("support_gaps", [])[:4]),
            }
        )
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if visible:
        selected = st.selectbox("Semantic detail", [item["rule_id"] for item in visible])
        item = next(candidate for candidate in visible if candidate["rule_id"] == selected)
        top = item.get("best_verified_matches", [{}])[0] if item.get("best_verified_matches") else {}
        _detail_sentence_panel(
            st,
            "Semantic review in plain English",
            [
                f"Review rule `{item.get('rule_id')}` has combined semantic score {_display_value(item.get('best_combined_semantic_score', item.get('best_semantic_score')))} against verified rule `{top.get('verified_rule_id')}`.",
                f"Structured score: {_display_value(top.get('structured_score'))}; embedding score: {_display_value(top.get('embedding_score'))}.",
                f"The match reasons are: {_list_text(top.get('match_reasons', []))}.",
                f"Guardrails passed: {_list_text(top.get('semantic_guardrails', []))}. Blockers: {_list_text(top.get('semantic_guardrail_blockers', []))}.",
                f"The verifier still blocks this candidate because of: {_list_text(item.get('support_gaps', []))}.",
                f"Suggested meaning-review action: {_plain_label(item.get('semantic_next_action'))}.",
                "This comparison prioritizes review only. It cannot verify a rule.",
            ],
            {"evidence_quote": json.dumps(item.get("signature", {}), indent=2)},
            item,
        )
        with st.expander("Raw semantic JSON"):
            st.json(item)


def _rule_graph_tab(st: Any, graph: dict[str, Any]) -> None:
    st.subheader("Rule Graph")
    st.caption("Diagnostic graph showing candidates, evidence, canonical keys, verified rules, and review rules. It does not change verification.")
    metric_cols = st.columns(2)
    metric_cols[0].metric("Nodes", graph.get("node_count", len(graph.get("nodes", []))))
    metric_cols[1].metric("Edges", graph.get("edge_count", len(graph.get("edges", []))))
    summary = graph.get("summary", {})
    left, right = st.columns(2)
    with left:
        st.markdown("### Node Types")
        _bar_rows(st, summary.get("node_type_counts", []), "name", "count")
    with right:
        st.markdown("### Edge Types")
        _bar_rows(st, summary.get("edge_type_counts", []), "name", "count")
    edges = graph.get("edges", [])
    if edges:
        edge_types = st.multiselect("Edge type", _unique(edges, "type"), format_func=_plain_label)
        visible = [edge for edge in edges if not edge_types or edge.get("type") in edge_types]
        st.dataframe(_display_rows(visible[:500]), width="stretch", hide_index=True)
    else:
        st.info("No graph output found. Rerun the slim verifier.")


def p9_provenance_summary(rule: dict[str, Any], evidence_by_id: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    """Collect the Pipeline 9 lane for one review rule, or None for P5 rules.

    Pure data (no streamlit) so tests can pin it: provenance identifies where
    the RAG candidate came from (pack, lane, pseudo->original page, upstream
    filter action), and the evidence comparison shows the RAG block text next
    to the re-anchored authentic source window — or flags the mismatch that
    forced the rule to review.
    """
    candidate = rule.get("candidate") or {}
    provenance = candidate.get("p9_provenance") or rule.get("p9_provenance") or {}
    if not provenance:
        return None
    evidence = evidence_by_id.get(str(candidate.get("evidence_id") or rule.get("source_evidence_id") or "")) or {}
    return {
        "pack": provenance.get("rag_pack_id"),
        "lane": provenance.get("rag_lane"),
        "applicability": provenance.get("rag_applicability"),
        "pseudo_page": provenance.get("pseudo_page"),
        "original_page": provenance.get("original_page_number"),
        "filter_action": provenance.get("target_filter_action"),
        "block_id": provenance.get("block_id") or provenance.get("source_id"),
        "rag_text": str(evidence.get("evidence_text") or ""),
        "reanchored": bool(evidence.get("reanchored_to_source")),
        "mismatched": bool(evidence.get("rag_context_mismatch")),
        "source_window": str(evidence.get("source_context") or "") if evidence.get("reanchored_to_source") else "",
    }


def _legal_context_expander(
    st: Any,
    output_dir: Path,
    rule: dict[str, Any],
    evidence_by_id: dict[str, dict[str, Any]] | None = None,
) -> None:
    """Retrieved FULL bylaw sections for a review rule (advisory context).

    The reviewer's recurring question is 'is there a qualifier NEARBY that the
    extractor missed?' — this answers it in place: the rule's own sentence is
    the retrieval query against the city's bylaw-RAG index, and hits come back
    section-expanded (the whole numbered provision, not a fragment).
    """
    lane = p9_provenance_summary(rule, evidence_by_id or {})
    index_path = bylaw_index_path(output_dir)
    if index_path is None and lane is None:
        return
    with st.expander("Nearby bylaw text"):
        if lane:
            st.markdown("**Pipeline 9 source trace**")
            st.caption(
                f"pack `{lane['pack']}` | lane {lane['lane']} ({lane['applicability']}) | "
                f"pseudo page {lane['pseudo_page']} → bylaw page {lane['original_page']} | "
                f"upstream filter: {lane['filter_action']} | block `{lane['block_id']}`"
            )
            if lane["mismatched"]:
                st.warning(
                    "Source mismatch: this extractor block was not found on its claimed source page, so the candidate stays in review."
                )
            if lane["reanchored"] and lane["source_window"]:
                rag_col, source_col = st.columns(2)
                with rag_col:
                    st.markdown("*Extractor text*")
                    st.markdown(
                        f"<div class='bylaw-section'>{html.escape(_short_display_quote(lane['rag_text']))}</div>",
                        unsafe_allow_html=True,
                    )
                with source_col:
                    st.markdown("*Matched source page text*")
                    st.markdown(
                        f"<div class='bylaw-section'>{html.escape(_short_display_quote(lane['source_window']))}</div>",
                        unsafe_allow_html=True,
                    )
            st.caption("Source trace is display-only. Upstream labels never approve a rule.")
        if index_path is None:
            return
        try:
            query = " ".join(
                str(rule.get(field) or "")
                for field in ("rule_object", "applies_to", "constraint_scope", "condition", "value", "unit")
            )
            hits = _cached_bylaw_index(index_path, st).ask(query, top_k=3, query_encoder=_query_encoder(st))
        except Exception as error:  # pragma: no cover - optional dep path
            st.caption(f"Retrieval unavailable: {error}")
            return
        if not hits:
            st.caption("No related sections retrieved.")
            return
        for hit in hits:
            label = hit.get("section") or hit.get("chunk_id")
            st.markdown(
                f"<div class='bylaw-section'><b>[{html.escape(str(label))}]</b><br>"
                f"{html.escape(_short_display_quote(hit.get('section_text') or hit.get('text') or ''))}</div>",
                unsafe_allow_html=True,
            )
        st.caption("Retrieved context only. It cannot change the rule's decision.")


def _review_focus_html(
    triage_item: dict[str, Any],
    review_rule: dict[str, Any],
    verified_rule: dict[str, Any],
    comparison_rows: list[dict[str, Any]],
) -> str:
    changed = [row for row in comparison_rows if str(row.get("matches") or "").lower() != "yes"]
    issue = _plain_label(
        triage_item.get("review_category")
        or triage_item.get("action_bucket")
        or review_rule.get("review_category")
        or "Needs review"
    )
    priority = _plain_label(triage_item.get("triage_priority") or triage_item.get("priority") or "not ranked")
    gaps = _gap_labels(review_rule.get("support_gaps") or triage_item.get("support_gaps"))
    gap_text = ", ".join(gaps[:3]) if gaps else "No coded gap recorded"
    if len(gaps) > 3:
        gap_text += f", +{len(gaps) - 3} more"
    closest = verified_rule.get("rule_id") if verified_rule else None
    closest_text = str(closest) if closest else "No verified match"
    next_step = (
        triage_item.get("suggested_fix")
        or triage_item.get("next_step")
        or triage_item.get("suggested_next_action")
        or "Inspect source evidence before any rerun."
    )
    diff_text = f"{len(changed)} field{'s' if len(changed) != 1 else ''} differ" if comparison_rows else "No comparison available"
    if comparison_rows and not changed:
        diff_text = "No field differences"
    cards = [
        ("Why held", issue, "Verifier could not prove this candidate.", "warn"),
        ("Main gap", gap_text, f"Priority: {priority}", "bad" if gaps else "warn"),
        ("Closest verified", closest_text, diff_text, "ok" if verified_rule else "neutral"),
        ("Next action", str(next_step), "Advisory only; no output changes here.", "action"),
    ]
    html_cards = "".join(
        "<div class='review-focus-card {tone}'>"
        "<span>{label}</span>"
        "<b>{value}</b>"
        "<small>{note}</small>"
        "</div>".format(
            tone=html.escape(tone),
            label=html.escape(label),
            value=html.escape(value),
            note=html.escape(note),
        )
        for label, value, note, tone in cards
    )
    return f"<div class='review-focus-grid'>{html_cards}</div>"


def _candidate_compare_tab(
    st: Any,
    triage_items: list[dict[str, Any]],
    review_rules: list[dict[str, Any]],
    verified_rules: list[dict[str, Any]],
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    evidence_by_id: dict[str, dict[str, Any]] | None = None,
) -> None:
    st.markdown("<div class='section-head' style='font-size:18px;'>Review one candidate</div>", unsafe_allow_html=True)
    st.caption("Compare one held candidate against its closest verified rule. Only differences are shown first.")
    if not triage_items:
        st.info("No review items match the current filters.")
        return
    options = [item["rule_id"] for item in triage_items]
    triage_lookup = {str(item.get("rule_id")): item for item in triage_items}
    selected_id = st.selectbox(
        "Choose a review item",
        options,
        key="review_focus_rule",
        format_func=lambda rule_id: _rule_option_label(triage_lookup.get(str(rule_id), {})),
    )
    review_rule = _by_rule_id(review_rules, selected_id)
    triage_item = next((item for item in triage_items if item["rule_id"] == selected_id), {})
    semantic_match_id = triage_item.get("semantic_verified_rule_id") or review_rule.get("semantic_verified_rule_id")
    lexical_match_id = triage_item.get("similar_verified_rule_id") or review_rule.get("similar_verified_rule_id")
    verified_rule = _by_rule_id(verified_rules, semantic_match_id or lexical_match_id)

    comparison_rows: list[dict[str, Any]] = []
    if verified_rule:
        comparison_rows = _field_comparison_rows(review_rule, verified_rule)
    st.markdown(_review_focus_html(triage_item, review_rule, verified_rule, comparison_rows), unsafe_allow_html=True)

    if verified_rule:
        different_rows = [row for row in comparison_rows if str(row.get("matches") or "").lower() != "yes"]
        matching_rows = [row for row in comparison_rows if str(row.get("matches") or "").lower() == "yes"]
        rows_to_show = different_rows or comparison_rows
        st.markdown("##### Candidate vs verified")
        st.markdown(
            f"<div class='diff-summary'><b>Highlighted differences</b><br>{html.escape(_field_difference_summary(comparison_rows))}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(_field_difference_html(rows_to_show), unsafe_allow_html=True)
        if matching_rows and different_rows:
            with st.expander(f"Open {len(matching_rows)} matching fields", expanded=False):
                st.markdown(_field_difference_html(matching_rows), unsafe_allow_html=True)
        with st.expander("Open full field comparison table", expanded=False):
            st.dataframe(_display_rows(comparison_rows), width="stretch", hide_index=True)
    else:
        st.info("No closest verified rule was found, so this item needs evidence repair or manual review.")

    st.markdown("##### Claim side by side")
    sentence_left, sentence_right = st.columns(2)
    with sentence_left:
        _sentence_card(
            st,
            "Candidate in review",
            _rule_sentence(review_rule),
            "review",
            "Generated from the candidate's normalized fields.",
        )
    with sentence_right:
        if verified_rule:
            _sentence_card(
                st,
                "Closest verified rule",
                _rule_sentence(verified_rule),
                "verified",
                f"Semantic score: {triage_item.get('semantic_score') or review_rule.get('semantic_score') or 'n/a'}; lexical score: {triage_item.get('similar_verified_score')}",
            )
        else:
            _sentence_card(
                st,
                "Closest verified rule",
                "No verified comparison rule was found for this review item.",
                "neutral",
                "Use evidence repair or manual review instead.",
            )

    with st.expander("Open raw fields and evidence", expanded=False):
        left, right = st.columns(2)
        with left:
            st.markdown("##### Candidate in review")
            st.table([compact_rule_row(review_rule)])
            st.markdown("**Evidence**")
            st.code(_source_text(review_rule), language="text")
        with right:
            st.markdown("##### Closest verified rule")
            if verified_rule:
                st.table([compact_rule_row(verified_rule)])
                st.markdown(f"Semantic score: `{triage_item.get('semantic_score') or review_rule.get('semantic_score') or 'n/a'}`")
                st.markdown(f"Lexical score: `{triage_item.get('similar_verified_score')}`")
                st.code(_source_text(verified_rule), language="text")
            else:
                st.info("No verified comparison rule found.")

    _legal_context_expander(st, output_dir, review_rule, evidence_by_id)


def _gap_labels(values: Any) -> list[str]:
    if not values:
        return []
    if isinstance(values, str):
        values = [values]
    return [_plain_label(value) for value in values if value not in (None, "")]


def _compact_label_text(values: Any, *, limit: int = 3, empty: str = "None recorded") -> str:
    labels = _gap_labels(values)
    if not labels:
        return empty
    shown = labels[:limit]
    suffix = f", +{len(labels) - limit} more" if len(labels) > limit else ""
    return ", ".join(shown) + suffix


def _fixed_gaps(original: Any, retry: Any) -> list[str]:
    retry_raw = {str(value) for value in (retry or [])}
    return [_plain_label(value) for value in (original or []) if str(value) not in retry_raw]


def _repair_impact_rows(rerun: dict[str, Any], repair: dict[str, Any]) -> list[dict[str, Any]]:
    attempts = rerun.get("attempts") or []
    rows = []
    for item in attempts:
        original_gaps = item.get("original_support_gaps") or []
        retry_gaps = item.get("retry_support_gaps") or []
        fixed = _fixed_gaps(original_gaps, retry_gaps)
        rows.append(
            {
                "rule_id": item.get("original_rule_id"),
                "claim": _rule_sentence(item),
                "status": _plain_label(item.get("retry_decision")),
                "promotion_ready": bool(item.get("promotion_ready")),
                "fixed": fixed,
                "still_missing": _gap_labels(retry_gaps),
                "original_evidence": item.get("original_evidence_id"),
                "retry_evidence": item.get("retry_evidence_id"),
                "confidence": item.get("repair_confidence") or item.get("best_repair_confidence"),
            }
        )
    if rows:
        return rows
    for item in (repair.get("suggestions") or []):
        rows.append(
            {
                "rule_id": item.get("rule_id"),
                "claim": _rule_sentence(item),
                "status": "Suggested repair",
                "promotion_ready": False,
                "fixed": _gap_labels(item.get("repairable_fields")),
                "still_missing": _gap_labels(item.get("support_gaps")),
                "original_evidence": item.get("current_evidence_id"),
                "retry_evidence": ((item.get("top_evidence") or [{}])[0] or {}).get("evidence_id"),
                "confidence": item.get("best_repair_confidence"),
            }
        )
    return rows


def _repair_impact_html(rows: list[dict[str, Any]], *, limit: int = 8) -> str:
    if not rows:
        return "<div class='empty-note'>No repair impact rows found for this run.</div>"
    cards = []
    for row in rows[:limit]:
        fixed = row.get("fixed") or []
        missing = row.get("still_missing") or []
        tone = "ready" if row.get("promotion_ready") else "fixed" if fixed else "blocked"
        fixed_text = _compact_label_text(fixed, limit=3, empty="No support gap improved yet")
        missing_text = _compact_label_text(missing, limit=3, empty="None recorded")
        cards.append(
            "<div class='repair-card {tone}'>"
            "<div class='repair-card-head'><b>{rule_id}</b><span>{status}</span></div>"
            "<p>{claim}</p>"
            "<div class='repair-columns'>"
            "<div><small>Gaps improved</small><strong>{fixed}</strong></div>"
            "<div><small>Still blocking</small><strong>{missing}</strong></div>"
            "</div>"
            "<div class='repair-foot'>Evidence {original} -> {retry} · confidence {confidence}</div>"
            "</div>".format(
                tone=html.escape(tone),
                rule_id=html.escape(str(row.get("rule_id") or "")),
                status=html.escape(str(row.get("status") or "")),
                claim=html.escape(str(row.get("claim") or "")),
                fixed=html.escape(fixed_text),
                missing=html.escape(missing_text),
                original=html.escape(str(row.get("original_evidence") or "n/a")),
                retry=html.escape(str(row.get("retry_evidence") or "n/a")),
                confidence=html.escape(_display_value(row.get("confidence"))),
            )
        )
    if len(rows) > limit:
        cards.append(
            "<div class='repair-card muted'><div class='repair-card-head'><b>More repair rows</b>"
            f"<span>{len(rows) - limit} more</span></div><p>Use the tables below for the full repair list.</p></div>"
        )
    return "<div class='repair-impact-grid'>" + "".join(cards) + "</div>"


def _repair_flow_html(
    *,
    suggestion_count: int,
    attempt_count: int,
    improved_count: int,
    ready_count: int,
    still_review: int,
    rejected: int,
    verified_after: int,
) -> str:
    steps = [
        ("Suggestions", f"{suggestion_count:,}", "Possible stronger source passages."),
        ("Shadow reruns", f"{attempt_count:,}", "Retested without changing outputs."),
        ("Gaps improved", f"{improved_count:,}", "At least one missing support signal improved."),
        ("Promotion ready", f"{ready_count:,}", "Must still pass deterministic gates."),
    ]
    step_html = "".join(
        "<div class='repair-flow-step'>"
        "<span>{label}</span><b>{value}</b><small>{note}</small>"
        "</div>".format(
            label=html.escape(label),
            value=html.escape(value),
            note=html.escape(note),
        )
        for label, value, note in steps
    )
    status = (
        f"Shadow outcome: {still_review:,} still in review, {rejected:,} rejected, "
        f"{verified_after:,} verified after rerun. Output promotion remains blocked unless the verifier proves source support."
    )
    return f"<div class='repair-flow'>{step_html}</div><div class='repair-status-note'>{html.escape(status)}</div>"


def _repair_focus_html(row: dict[str, Any]) -> str:
    fixed = row.get("fixed") or []
    missing = row.get("still_missing") or []
    fixed_text = _compact_label_text(fixed, limit=3, empty="No support gap improved yet")
    missing_text = _compact_label_text(missing, limit=3, empty="None recorded")
    tone = "ready" if row.get("promotion_ready") else "fixed" if fixed else "blocked"
    if row.get("promotion_ready"):
        decision = "Ready for deterministic promotion check"
    elif fixed:
        decision = "Evidence improved, but still not verified"
    else:
        decision = "Still blocked"
    return (
        "<div class='repair-focus-card {tone}'>"
        "<div class='repair-focus-head'>"
        "<div><span>Selected repair result</span><b>{rule_id}</b></div>"
        "<strong>{decision}</strong>"
        "</div>"
        "<p>{claim}</p>"
        "<div class='repair-columns'>"
        "<div><small>Gaps improved</small><strong>{fixed}</strong></div>"
        "<div><small>Still blocking</small><strong>{missing}</strong></div>"
        "</div>"
        "<div class='repair-foot'>Evidence {original} -> {retry} · confidence {confidence}</div>"
        "</div>".format(
            tone=html.escape(tone),
            rule_id=html.escape(str(row.get("rule_id") or "")),
            decision=html.escape(decision),
            claim=html.escape(str(row.get("claim") or "")),
            fixed=html.escape(fixed_text),
            missing=html.escape(missing_text),
            original=html.escape(str(row.get("original_evidence") or "n/a")),
            retry=html.escape(str(row.get("retry_evidence") or "n/a")),
            confidence=html.escape(_display_value(row.get("confidence"))),
        )
    )


def _repair_page(st: Any, data: dict[str, Any]) -> None:
    repair = data.get("repair") or {"suggestions": []}
    rerun = data.get("rerun") or {"attempts": []}
    suggestions = repair.get("suggestions") or []
    attempts = rerun.get("attempts") or []
    impact_rows = sorted(
        _repair_impact_rows(rerun, repair),
        key=lambda row: (
            not bool(row.get("promotion_ready")),
            -len(row.get("fixed") or []),
            len(row.get("still_missing") or []),
            str(row.get("rule_id") or ""),
        ),
    )
    fixed_count = sum(1 for row in impact_rows if row.get("fixed"))
    ready_count = int(rerun.get("promotion_ready_count") or sum(1 for item in attempts if item.get("promotion_ready")))
    verified_after = int(rerun.get("verified_after_rerun_count") or 0)
    still_review = int(rerun.get("review_after_rerun_count") or 0)
    rejected = int(rerun.get("rejected_after_rerun_count") or 0)

    st.markdown(
        _repair_flow_html(
            suggestion_count=len(suggestions),
            attempt_count=len(attempts),
            improved_count=fixed_count,
            ready_count=ready_count,
            still_review=still_review,
            rejected=rejected,
            verified_after=verified_after,
        ),
        unsafe_allow_html=True,
    )

    if impact_rows:
        selected_index = st.selectbox(
            "Choose a repair result",
            list(range(len(impact_rows))),
            key="repair_focus_row",
            format_func=lambda index: _rule_option_label(
                {
                    "rule_id": impact_rows[index].get("rule_id"),
                    "review_category": impact_rows[index].get("status"),
                    "value": "",
                    "unit": "",
                }
            ),
        )
        st.markdown(_repair_focus_html(impact_rows[selected_index]), unsafe_allow_html=True)
    else:
        st.info("No repair impact rows found for this run.")

    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-head' style='font-size:16px;'>Optional repair drill-downs</div>", unsafe_allow_html=True)
    st.caption("Use these when you need the full evidence table or shadow rerun audit.")
    drill_left, drill_mid, drill_right = st.columns(3)
    show_impacts = drill_left.toggle("Show all repair rows", value=False, key="repair_show_all_impacts")
    show_suggestions = drill_mid.toggle("Show evidence table", value=False, key="repair_show_suggestion_table")
    show_reruns = drill_right.toggle("Show rerun table", value=False, key="repair_show_rerun_table")

    if show_impacts:
        st.markdown(_repair_impact_html(impact_rows, limit=24), unsafe_allow_html=True)
    if show_suggestions:
        _repair_tab(st, repair)
    if show_reruns:
        _rerun_tab(st, rerun, data.get("evidence_units") or [])


def _repair_tab(st: Any, repair: dict[str, Any]) -> None:
    suggestions = repair.get("suggestions", [])
    st.subheader(f"Evidence Repair ({len(suggestions)})")
    st.caption("Find stronger source passages for candidates held in review. A repair suggestion still has to pass the verifier.")
    rows = []
    for item in suggestions[:200]:
        top = item.get("top_evidence", [{}])[0] if item.get("top_evidence") else {}
        rows.append(
            {
                "Rule ID": item.get("rule_id"),
                "Can retry verifier": item.get("can_retry_verification"),
                "Confidence": item.get("best_repair_confidence"),
                "Rule family": item.get("rule_object"),
                "Value": item.get("value"),
                "Unit": item.get("unit"),
                "Current evidence": item.get("current_evidence_id"),
                "Best evidence": top.get("evidence_id"),
                "Fields repair may help": ", ".join(item.get("repairable_fields", [])),
                "Why this evidence matched": ", ".join(top.get("match_reasons", [])),
            }
        )
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if suggestions:
        selected = st.selectbox(
            "Repair detail",
            [item["rule_id"] for item in suggestions],
            format_func=lambda rule_id: _rule_option_label(next((item for item in suggestions if item.get("rule_id") == rule_id), {})),
        )
        item = next(item for item in suggestions if item["rule_id"] == selected)
        top_evidence = item.get("top_evidence", [{}])[0] if item.get("top_evidence") else {}
        _detail_sentence_panel(
            st,
            "Evidence repair in plain English",
            _repair_detail_sentences(item, top_evidence),
            top_evidence,
            item,
        )
        with st.expander("Raw repair JSON"):
            st.json(item)


def _rerun_tab(st: Any, rerun: dict[str, Any], evidence_units: list[dict[str, Any]]) -> None:
    attempts = rerun.get("attempts", [])
    verified = rerun.get("verified_after_rerun", [])
    st.subheader("Shadow Reruns")
    st.caption("Test stronger evidence without changing verified_rules.json. Promotion still requires deterministic proof and benchmark safety.")
    metric_cols = st.columns(6)
    metric_cols[0].metric("Attempts", rerun.get("attempt_count", len(attempts)))
    metric_cols[1].metric("Verified After Rerun", rerun.get("verified_after_rerun_count", len(verified)))
    metric_cols[2].metric("Promotion Ready", rerun.get("promotion_ready_count", 0))
    metric_cols[3].metric("Still Review", rerun.get("review_after_rerun_count", 0))
    metric_cols[4].metric("Rejected", rerun.get("rejected_after_rerun_count", 0))
    metric_cols[5].metric("Skipped", rerun.get("skipped_count", 0))

    if not attempts:
        st.info("No evidence rerun attempts found.")
        return

    left, middle, right = st.columns([1, 1, 1])
    decisions = left.multiselect("Rerun result", _unique(attempts, "retry_decision"), format_func=_plain_label)
    rule_objects = middle.multiselect("Rule family", _unique(attempts, "rule_object"), format_func=_plain_label)
    only_ready = right.checkbox("Passed shadow checks only")
    visible = attempts
    if decisions:
        visible = [item for item in visible if item.get("retry_decision") in decisions]
    if rule_objects:
        visible = [item for item in visible if item.get("rule_object") in rule_objects]
    if only_ready:
        visible = [item for item in visible if item.get("promotion_ready")]

    ready_rows = [
        {
            "Rule ID": item.get("original_rule_id"),
            "Rule family": item.get("rule_object"),
            "Scope": item.get("constraint_scope"),
            "Direction": _operator_short(item.get("operator"), item.get("constraint_type")),
            "Value": item.get("value"),
            "Unit": item.get("unit"),
            "Retry evidence": item.get("retry_evidence_id"),
            "Confidence": item.get("repair_confidence"),
        }
        for item in attempts
        if item.get("promotion_ready")
    ]
    if ready_rows:
        st.markdown("### Passed shadow checks")
        st.dataframe(_display_rows(ready_rows), width="stretch", hide_index=True)

    rows = [
        {
            "Rule ID": item.get("original_rule_id"),
            "Rerun result": item.get("retry_decision"),
            "Rule family": item.get("rule_object"),
            "Value": item.get("value"),
            "Unit": item.get("unit"),
            "Original evidence": item.get("original_evidence_id"),
            "Retry evidence": item.get("retry_evidence_id"),
            "Confidence": item.get("repair_confidence"),
            "Ready for promotion": item.get("promotion_ready"),
            "Risk flags": ", ".join(item.get("promotion_risk_flags", [])),
            "Still missing": ", ".join(item.get("retry_support_gaps", [])[:4]),
        }
        for item in visible[:250]
    ]
    st.markdown(f"### Shadow rerun attempts ({len(visible)})")
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if visible:
        selected = st.selectbox(
            "Shadow rerun detail",
            [item["original_rule_id"] for item in visible],
            format_func=lambda rule_id: _rule_option_label(next((item for item in visible if item.get("original_rule_id") == rule_id), {})),
        )
        item = next(item for item in visible if item["original_rule_id"] == selected)
        evidence = _evidence_by_id(evidence_units, item.get("retry_evidence_id"))
        _detail_sentence_panel(
            st,
            "Evidence rerun in plain English",
            _rerun_detail_sentences(item),
            evidence,
            item,
        )
        with st.expander("Raw rerun JSON"):
            st.json(item)


def _safe_tuning_tab(st: Any, report: dict[str, Any], evidence_units: list[dict[str, Any]]) -> None:
    items = report.get("items", [])
    st.subheader(f"Safe Verifier Tuning ({len(items)})")
    st.caption("Engineering backlog for general verifier improvements. These candidates are not automatically promoted.")
    metric_cols = st.columns(3)
    metric_cols[0].metric("Candidates", report.get("candidate_count", len(items)))
    metric_cols[1].metric("Promotion-Ready Reruns", sum(1 for item in items if item.get("rerun_promotion_ready")))
    metric_cols[2].metric("Tuning Types", len(report.get("tuning_type_counts", [])))

    type_rows = report.get("tuning_type_counts", [])
    if type_rows:
        st.markdown("### Tuning Type Mix")
        _bar_rows(st, type_rows, "name", "count")
    if not items:
        st.info("No safe verifier tuning candidates found.")
        return

    tuning_types = st.multiselect("Tuning type", _unique(items, "tuning_type"), format_func=_plain_label)
    visible = [item for item in items if not tuning_types or item.get("tuning_type") in tuning_types]
    rows = [
        {
            "rule_id": item.get("rule_id"),
            "tuning_type": item.get("tuning_type"),
            "rule_object": item.get("rule_object"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "likely": item.get("likely_status"),
            "score": item.get("likely_correct_score"),
            "rerun_ready": item.get("rerun_promotion_ready"),
            "gaps": ", ".join(item.get("support_gaps", [])[:4]),
        }
        for item in visible[:250]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    selected = st.selectbox("Tuning detail", [item["rule_id"] for item in visible])
    item = next(candidate for candidate in visible if candidate["rule_id"] == selected)
    evidence = _evidence_by_id(evidence_units, item.get("evidence_id") or item.get("rerun_evidence_id"))
    _detail_sentence_panel(
        st,
        "Safe tuning candidate in plain English",
        _safe_tuning_detail_sentences(item),
        evidence,
        item,
    )
    with st.expander("Required tests"):
        for test in item.get("required_tests", []):
            st.write(f"- {test}")
    with st.expander("Guardrails"):
        for guardrail in item.get("guardrails", []):
            st.write(f"- {guardrail}")
    with st.expander("Raw safe-tuning JSON"):
        st.json(item)


def _structure_tab(st: Any) -> None:
    st.subheader("Verification Layer Structure")
    st.code(
        """Pipeline 5 final_rule_registry.json
  -> zihao_adapter.py
  -> slim_pipeline.py
  -> verification.py
       normalization.py
       support_checks.py
       proof_trace.py
       text_span_proof.py
       table_natural_logic.py
       decision_policy.py
  -> verified / review / rejected / not_used
  -> evidence_intelligence.py
  -> rule_graph.py
  -> evidence_bundle_rerun
  -> guarded bundle promotion
  -> semantic_review.py
  -> evidence_repair.py
  -> evidence_rerun.py
  -> safe_tuning.py
  -> review_router.py
  -> dashboard""",
        language="text",
    )
    rows = [
        {"layer": "Adapter", "file": "zihao_adapter.py", "purpose": "Normalize Pipeline 5 registry into candidates and evidence packets."},
        {"layer": "Verifier", "file": "verification.py", "purpose": "Main support-gap loop and final rule objects."},
        {"layer": "Normalization", "file": "normalization.py", "purpose": "Candidate cleanup before support checks; no rule promotion."},
        {"layer": "Support checks", "file": "support_checks.py", "purpose": "Reusable deterministic checks for value, unit, operator, scope, applies_to, and rule family."},
        {"layer": "Proof trace", "file": "proof_trace.py", "purpose": "Human-readable proof traces, review reasons, and proof/decision diagnostics."},
        {"layer": "Text span proof", "file": "text_span_proof.py", "purpose": "Prose evidence proof for value, unit, operator, scope, condition."},
        {"layer": "Table proof", "file": "table_natural_logic.py", "purpose": "Table title/row/column/cell proof."},
        {"layer": "Decision policy", "file": "decision_policy.py", "purpose": "Map support gaps to verified/review/rejected/not_used."},
        {"layer": "Evidence intelligence", "file": "evidence_intelligence.py", "purpose": "Build a rule-centric evidence index, score evidence bundles, and recommend safe shadow reruns."},
        {"layer": "Evidence repair", "file": "evidence_repair.py", "purpose": "Find stronger existing evidence for review rules."},
        {"layer": "Evidence rerun", "file": "evidence_rerun.py", "purpose": "Rerun repairable candidates or bundles against stronger evidence in shadow mode."},
        {"layer": "Bundle promotion", "file": "evidence_rerun.py", "purpose": "Move only deterministic, no-gap, no-risk bundle reruns into verified output."},
        {"layer": "Rule graph", "file": "rule_graph.py", "purpose": "Diagnostic graph linking candidates, evidence packets, canonical keys, verified rules, and review rules."},
        {"layer": "Verification cache", "file": "verification_cache.py", "purpose": "Stable cache keys and hit/miss diagnostics for future incremental multi-bylaw runs."},
        {"layer": "Semantic review", "file": "semantic_review.py", "purpose": "Structured meaning comparison between review and verified rules; advisory only."},
        {"layer": "Safe tuning", "file": "safe_tuning.py", "purpose": "List verifier-tuning candidates with experiments, tests, and guardrails."},
        {"layer": "Review router", "file": "review_router.py", "purpose": "Single review module: triage (rank + likely mistakes), action audit (next-action buckets), and the consolidated reviewer route. Advisory only."},
    ]
    st.table(rows)


def _preflight_tab(st: Any, preflight: dict[str, Any]) -> None:
    st.subheader("Pipeline 5 Extraction Preflight")
    if not preflight:
        st.info("No preflight report found.")
        st.code(
            "python3 scripts/run_pipeline5_extraction.py "
            "--report-json outputs/burnaby_r1_slim_pipeline5_registry/pipeline5_extraction_preflight.json",
            language="bash",
        )
        return
    checks = preflight.get("checks", {})
    st.table([{"check": key, "status": "OK" if value else "MISSING"} for key, value in checks.items()])
    # The preflight script (scripts/run_pipeline5_extraction.py) only emits
    # checks/blockers/can_execute, so the saved-registry status is derived from
    # its saved_final_registry_exists check rather than from keys it never writes.
    if checks.get("saved_final_registry_exists"):
        st.success("Saved Pipeline 5 registry found. The verifier can run from this saved extraction output.")
    else:
        failed_checks = [name for name, passed in checks.items() if not passed]
        st.error("Saved registry missing: " + (", ".join(failed_checks) or "saved_final_registry_exists"))

    execution_blockers = preflight.get("blockers") or []
    if execution_blockers:
        st.warning("Full notebook execution still needs: " + ", ".join(execution_blockers))
    else:
        st.success("Pipeline 5 notebook execution is ready.")
    st.json({
        key: preflight.get(key)
        for key in ("pipeline5_dir", "notebook", "final_registry", "can_execute")
    })


def extract_bylaw_sections(payload: Any) -> list[dict[str, str]]:
    """Normalize an unknown extraction payload into [{title, text}, ...]."""
    title_keys = ("section", "section_id", "id", "anchor", "number", "title", "heading", "name")
    text_keys = ("text", "content", "body", "raw_text", "section_text")

    def _from_dict_item(item: dict[str, Any], fallback_title: str) -> dict[str, str] | None:
        text = next((str(item[key]) for key in text_keys if isinstance(item.get(key), str) and item[key].strip()), "")
        if not text:
            return None
        title = next((str(item[key]) for key in title_keys if item.get(key) not in (None, "")), fallback_title)
        heading = next((str(item[key]) for key in ("title", "heading") if item.get(key) not in (None, "")), "")
        if heading and heading != title:
            title = f"{title} — {heading}"
        return {"title": title, "text": text}

    sections: list[dict[str, str]] = []
    if isinstance(payload, str):
        if payload.strip():
            sections.append({"title": "Extracted text", "text": payload})
    elif isinstance(payload, list):
        for index, item in enumerate(payload, start=1):
            if isinstance(item, dict):
                section = _from_dict_item(item, f"Section {index}")
                if section:
                    sections.append(section)
            elif isinstance(item, str) and item.strip():
                sections.append({"title": f"Section {index}", "text": item})
    elif isinstance(payload, dict):
        nested = payload.get("sections")
        if isinstance(nested, (list, dict)):
            return extract_bylaw_sections(nested if isinstance(nested, list) else [
                {"title": key, **(value if isinstance(value, dict) else {"text": str(value)})}
                for key, value in nested.items()
            ])
        direct = _from_dict_item(payload, "Extracted text")
        if direct:
            sections.append(direct)
        else:
            # Loose {key: text} shape: only accept prose-like values so
            # metadata payloads (urls, hashes, timestamps) are not mistaken
            # for bylaw sections.
            for key, value in payload.items():
                if isinstance(value, str) and len(value.split()) >= 8:
                    sections.append({"title": str(key), "text": value})
                elif isinstance(value, dict):
                    section = _from_dict_item(value, str(key))
                    if section:
                        sections.append(section)
    return sections


def highlight_evidence(section_text: str, quote: str) -> tuple[str, bool]:
    """Mark the cited evidence inside section text via simple substring markup.

    Both sides are whitespace-normalized; progressively shorter quote prefixes
    are tried so truncated evidence quotes still anchor. Returns escaped HTML
    plus whether a match was found.
    """
    normalized = " ".join(str(section_text or "").split())
    words = " ".join(str(quote or "").split()).rstrip(". ").removesuffix("...").split()
    for length in (len(words), 24, 16, 10, 6):
        needle = " ".join(words[:length])
        if len(needle) < 12:
            break
        index = normalized.lower().find(needle.lower())
        if index >= 0:
            end = index + len(needle)
            return (
                html.escape(normalized[:index])
                + "<mark class='evidence-hit'>"
                + html.escape(normalized[index:end])
                + "</mark>"
                + html.escape(normalized[end:]),
                True,
            )
    return html.escape(normalized), False


def _rag_chat_key(city_stem: str) -> str:
    return f"bylaw_rag_chat::{city_stem}"


def _rag_tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:\.[0-9]+)*", str(text or "").lower())


def _rag_query_terms(question: str) -> list[str]:
    tokens = _rag_tokenize(question)
    expanded = list(tokens)
    seen = set(tokens)
    for token in tokens:
        for extra in RAG_QUERY_SYNONYMS.get(token, ()):
            if extra not in seen:
                seen.add(extra)
                expanded.append(extra)
    return expanded


def _retrieval_module() -> Any | None:
    """The package-free hybrid-retrieval module (sibling of streamlit_app.py).

    Ships to the cloud deploy alongside ``chat_brain.py``, so BM25 + dense + rerank
    run there WITHOUT the ``burnaby_prototype`` package. ``None`` only if missing.
    """
    try:
        import bylaw_retrieval

        return bylaw_retrieval
    except Exception:
        return None


def _dashboard_reranker(st: Any | None) -> Any | None:
    """Return a session-cached cross-encoder reranker or ``None``.

    Reuses the SAME ``OPENROUTER_API_KEY`` the dashboard already loaded. ``None``
    means "skip reranking, keep BM25/RRF order". Never raises.
    """
    api_key = _secret_value(st, "OPENROUTER_API_KEY")
    if not api_key:
        return None
    retr = _retrieval_module()
    if retr is None:
        return None
    cache_key = "_bylaw_rag_reranker"
    if st is not None:
        try:
            cached = st.session_state.get(cache_key)
            if cached is not None:
                return cached
        except Exception:
            cached = None
    try:
        reranker = retr.OpenRouterRerank(api_key)
    except Exception:
        return None
    if st is not None:
        try:
            st.session_state[cache_key] = reranker
        except Exception:
            pass
    return reranker


def _dashboard_embedding_backend(st: Any | None) -> Any | None:
    """Return a session-cached dense-embedding client or ``None``.

    Reuses the SAME ``OPENROUTER_API_KEY`` (``baai/bge-m3``). Held per-session
    because it carries the API client; ``None`` means "BM25-only". Never raises.
    """
    api_key = _secret_value(st, "OPENROUTER_API_KEY")
    if not api_key:
        return None
    retr = _retrieval_module()
    if retr is None:
        return None
    cache_key = "_bylaw_rag_embedder"
    if st is not None:
        try:
            cached = st.session_state.get(cache_key)
            if cached is not None:
                return cached
        except Exception:
            pass
    try:
        backend = retr.OpenRouterEmbeddings(api_key)
    except Exception:
        return None
    if st is not None:
        try:
            st.session_state[cache_key] = backend
        except Exception:
            pass
    return backend


def _query_encoder(st: Any | None):
    """A callable ``(question) -> vector`` for the dense leg, or ``None``.

    Passed into the index at SEARCH time (not stored on it) so the cached index
    object holds no API client and is safe to share across sessions."""
    backend = _dashboard_embedding_backend(st)
    if backend is None:
        return None
    return lambda q: backend.encode([q])[0]


def _cached_bylaw_index(index_path: Path, st: Any | None) -> Any:
    """Build (once) and session-cache the section index — self-contained hybrid.

    BM25 + dense (precomputed corpus vectors from the ``bylaw_rag_vectors.json``
    sidecar) fused with RRF. The dense leg costs ONE query-embedding call per
    question (no corpus embedding) and runs on the cloud deploy with no package.
    Client-free (the query encoder is passed at search time) so it is shareable.
    BM25-only when no vectors. Raises only if the module/chunk load fails, so
    ``_dashboard_rag_hits`` can fall back to the standalone reader.
    """
    cache_key = f"_bylaw_section_index::{index_path}"
    if st is not None:
        try:
            cached = st.session_state.get(cache_key)
            if cached is not None:
                return cached
        except Exception:
            pass
    retr = _retrieval_module()
    if retr is None:
        raise RuntimeError("bylaw_retrieval module unavailable")
    payload = _read_json(index_path, {})
    chunks = payload.get("chunks", [])
    vectors = payload.get("vectors")
    if vectors is None:
        sidecar = Path(index_path).with_name("bylaw_rag_vectors.json")
        if sidecar.exists():
            try:
                vectors = _read_json(sidecar, {}).get("vectors")
            except Exception:
                vectors = None
    index = retr.HybridBylawIndex(chunks, corpus_vectors=vectors)
    if st is not None:
        try:
            st.session_state[cache_key] = index
        except Exception:
            pass
    return index


def _rerank_rag_hits(question: str, hits: list[dict[str, Any]], top_k: int, st: Any | None) -> list[dict[str, Any]]:
    """Cross-encoder rerank a broad candidate shortlist down to ``top_k``.

    The reranker scores ``_pack_rerank_text`` which reads ``source_text``; the
    RAG hits carry the full-context clause under ``section_text``/``text``, so we
    expose that as ``source_text`` for scoring only. On no key, empty results, or
    any error we return the original BM25/RRF top-``top_k`` unchanged.
    """
    if len(hits) <= top_k:
        return hits
    reranker = _dashboard_reranker(st)
    if reranker is None:
        return hits[:top_k]
    packs = [
        {**hit, "source_text": str(hit.get("section_text") or hit.get("text") or "")}
        for hit in hits
    ]
    try:
        ranked = reranker.rerank(question, packs, top_n=top_k)
    except Exception:
        return hits[:top_k]
    if not ranked:
        return hits[:top_k]
    # Strip the scoring-only ``source_text`` shim; keep the reranker's score as a
    # signal so the sources table can show why a clause surfaced.
    cleaned: list[dict[str, Any]] = []
    for pack in ranked[:top_k]:
        pack = dict(pack)
        pack.pop("source_text", None)
        score = pack.pop("rerank_score", None)
        if score is not None:
            signals = dict(pack.get("signals") or {})
            signals["rerank_score"] = round(float(score), 6)
            pack["signals"] = signals
        cleaned.append(pack)
    return cleaned


def _dashboard_rag_hits(
    index_path: Path,
    question: str,
    top_k: int = RAG_CHAT_TOP_K,
    st: Any | None = None,
) -> list[dict[str, Any]]:
    """Return bylaw RAG hits with two-stage retrieval and a cloud fallback.

    Stage 1 retrieves a BROAD candidate set (``RAG_RERANK_CANDIDATES``) from the
    existing BM25/RRF index (``bylaw_rag.BylawIndex``) so the decisive clause is
    in the pool even when it ranks well below the ``top_k`` cutoff. Stage 2, when
    an OpenRouter key is available, reranks that shortlist with a cross-encoder
    and keeps the top ``top_k``; otherwise it falls back to the BM25/RRF order.

    The deployment repo intentionally contains only the dashboard and JSON
    outputs, not the full Python package. Locally we use ``bylaw_rag.py`` when it
    is importable; on cloud we read the index JSON directly via the standalone
    lexical retriever. Either path goes through the same rerank stage.
    """
    candidate_k = max(top_k, RAG_RERANK_CANDIDATES)
    try:
        index = _cached_bylaw_index(index_path, st)
        candidates = index.ask(question, top_k=candidate_k, query_encoder=_query_encoder(st))
    except Exception:
        candidates = _standalone_rag_hits(index_path, question, top_k=candidate_k)
    return _rerank_rag_hits(question, candidates, top_k, st)


def _standalone_rag_hits(index_path: Path, question: str, top_k: int = RAG_CHAT_TOP_K) -> list[dict[str, Any]]:
    payload = _read_json(index_path, {})
    chunks = [chunk for chunk in payload.get("chunks", []) if str(chunk.get("text") or "").strip()]
    query_terms = _rag_query_terms(question)
    query_set = set(query_terms)
    if not chunks or not query_set:
        return []

    scored: list[tuple[float, dict[str, Any], set[str]]] = []
    for chunk in chunks:
        text = str(chunk.get("text") or "")
        tokens = set(_rag_tokenize(text))
        overlap = tokens & query_set
        if not overlap:
            continue
        exact_value_bonus = sum(1 for term in query_set if re.fullmatch(r"\d+(?:\.\d+)?", term) and term in tokens)
        score = (len(overlap) + exact_value_bonus) / max(len(query_set), 1)
        scored.append((score, chunk, overlap))
    scored.sort(key=lambda item: (-item[0], str(item[1].get("chunk_id") or "")))

    by_section: dict[str, list[dict[str, Any]]] = {}
    for chunk in chunks:
        section = str(chunk.get("section") or "")
        if section:
            by_section.setdefault(section, []).append(chunk)

    results: list[dict[str, Any]] = []
    for rank, (score, chunk, overlap) in enumerate(scored[:top_k], start=1):
        section = str(chunk.get("section") or "")
        siblings = by_section.get(section, [])
        expanded = "\n".join(str(sib.get("text") or "") for sib in siblings) if len(siblings) > 1 else str(chunk.get("text") or "")
        results.append(
            {
                **chunk,
                "score": round(score, 6),
                "signals": {"standalone_rank": rank, "matched_terms": sorted(overlap)[:12]},
                "section_text": expanded,
            }
        )
    return results


def _bounded_rag_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bounded: list[dict[str, Any]] = []
    remaining = RAG_CONTEXT_CHAR_LIMIT
    for hit in hits:
        text = str(hit.get("section_text") or hit.get("text") or "")
        if remaining <= 0:
            break
        excerpt = text[: min(RAG_CONTEXT_PER_HIT_LIMIT, remaining)]
        remaining -= len(excerpt)
        bounded.append({**hit, "section_text": excerpt, "text": excerpt})
    return bounded


# Internal extraction labels (e.g. "pipeline5_merged_rule_0034", "m4_pack_0002_ev_002")
# leak into the bylaw index text and the model sometimes echoes them as 【…】
# citations. Strip them from BOTH the evidence we feed the model and the answer
# we render, so the user only ever sees clean (§section, p.page) citations.
_INTERNAL_ID_PAT = r"(?:merged_rule|pipeline\d|_pack_|_ev_|native_m\d|_rule_\d)"
_INTERNAL_TOKEN_RE = re.compile(rf"[【\[][^】\]]*?{_INTERNAL_ID_PAT}[^】\]]*?[】\]]", re.IGNORECASE)
_INTERNAL_PAREN_RE = re.compile(rf"\(\s*§?[^)]*?{_INTERNAL_ID_PAT}[^)]*?\)", re.IGNORECASE)
_INTERNAL_BARE_RE = re.compile(rf"§?\s*[A-Za-z0-9_]*{_INTERNAL_ID_PAT}[A-Za-z0-9_]*", re.IGNORECASE)
_CJK_CITE_RE = re.compile(r"【[^】]*】")


def _looks_internal_id(value: Any) -> bool:
    """True when a 'section'/chunk id is really an internal extraction label
    (pipeline5_merged_rule_0034, m4_pack_..._ev_002) rather than a bylaw section."""
    return bool(re.search(_INTERNAL_ID_PAT, str(value or ""), re.IGNORECASE))


def _clean_section_label(section: Any, page: Any) -> str:
    """A human citation label: '§541(1), p.6', or 'p.6' when the only id is an
    internal chunk id, or '' when nothing clean is available. This stops the LLM
    from ever being handed an internal id to cite."""
    sec = "" if _looks_internal_id(section) else str(section or "").strip()
    parts = []
    if sec:
        parts.append(f"§{sec}")
    if page not in (None, ""):
        parts.append(f"p.{page}")
    return ", ".join(parts)


def _strip_internal_tokens(text: str) -> str:
    """Safety net: remove any internal-id citation the model still emits, in
    bracket [【…】], parenthesis (§…), or bare form."""
    if not text:
        return text
    text = _INTERNAL_TOKEN_RE.sub("", text)
    text = _INTERNAL_PAREN_RE.sub("", text)
    text = _CJK_CITE_RE.sub("", text)
    text = _INTERNAL_BARE_RE.sub("", text)
    text = re.sub(r"§\s*(?=p\.)", "", text)  # "(§p.2)" -> "(p.2)" when only a page is known
    text = re.sub(r"\(\s*[,;]?\s*\)", "", text)
    text = re.sub(r"\s+([.,;])", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _grounded_bylaw_prompt(question: str, hits: list[dict[str, Any]]) -> str:
    bounded_hits = _bounded_rag_hits(hits)
    sections = []
    for hit in bounded_hits:
        label = _clean_section_label(hit.get("section") or hit.get("chunk_id"), hit.get("page")) or "unlabeled"
        body = _strip_internal_tokens(str(hit.get("section_text") or hit.get("text") or ""))
        sections.append(f"[{label}] {body}")
    sections_text = "\n\n".join(sections)
    return (
        "You are an advisory zoning-bylaw assistant for human reviewers. Use ONLY the bylaw sections "
        "below — read them, reason across them, and explain the answer in your own clear words. You "
        "never approve, verify, reject, or promote a rule.\n"
        "HOW TO ANSWER:\n"
        "- Lead with the direct answer (the number or limit) in the first sentence, in **bold**.\n"
        "- Then add 1-2 sentences that explain it: combine the relevant sections and note any condition, "
        "exception, or building location/type that changes the answer.\n"
        "- Keep it tight — ≤4 short sentences of plain English, no bullet lists.\n"
        "- Ground every statement; cite each claim in parentheses using the bracket label shown above "
        "its section — e.g. (§541(1), p.6), or just (p.2) when only a page is shown. Never put § before "
        "a page number.\n"
        "- NEVER output rule ids, evidence ids, internal codes, or 【…】 brackets.\n"
        "- If the sections genuinely do not answer the question, say so plainly in one sentence.\n\n"
        f"SECTIONS:\n{sections_text}\n\nQUESTION: {question}"
    )


def _retrieval_only_bylaw_answer(question: str, hits: list[dict[str, Any]]) -> str:
    labels = ", ".join(f"[{hit.get('section') or hit.get('chunk_id')}]" for hit in hits[:3])
    return (
        "I found related bylaw sections, but no deployed LLM key is configured for this dashboard. "
        f"Use the retrieved source sections below ({labels}) to answer the question. "
        "I am not generating a legal answer in retrieval-only mode."
    )


_CARD_TONE = {"verified": "verified", "in_review": "review", "rejected": "review", "not_used": "neutral"}
_CARD_BADGE = {
    "verified": "✓ Verified",
    "in_review": "● In review",
    "rejected": "✗ Rejected",
    "not_used": "— Not used",
}


def _render_verification_card(st: Any, card: dict[str, Any]) -> None:
    """Render one plain-language verification explanation (status, why, where to look)."""
    rule = card.get("rule") or {}
    status = str(card.get("status") or "in_review")
    tone = _CARD_TONE.get(status, "review")
    badge = _CARD_BADGE.get(status, "● In review")
    sentence_html = _review_sentence_html(rule) if status in {"in_review", "rejected"} else f"<div class='rule-text'>{html.escape(_rule_sentence(rule))}</div>"
    st.markdown(
        f"<div class='sentence-card sentence-{tone}'><div class='sentence-title'>{html.escape(badge)}</div>{sentence_html}</div>",
        unsafe_allow_html=True,
    )
    if card.get("verdict_sentence"):
        st.markdown(str(card["verdict_sentence"]))
    why = card.get("why") or []
    if why:
        header = "**Why it was rejected:**" if status == "rejected" else "**Why it's held for review:**"
        st.markdown(header + "\n" + "\n".join(f"- {w}" for w in why))
    if card.get("likely_missing"):
        st.markdown(f"**What would likely clear it:** {card['likely_missing']}")
    wtl = card.get("where_to_look") or {}
    if wtl.get("quote") or wtl.get("page") not in (None, ""):
        loc_parts = []
        if wtl.get("section"):
            loc_parts.append(f"§{wtl['section']}")
        if wtl.get("page") not in (None, ""):
            loc_parts.append(f"p.{wtl['page']}")
        loc_text = ", ".join(loc_parts) or "source"
        quote = str(wtl.get("quote") or "")
        st.markdown(
            f"<div class='citation'><span class='loc'>📍 Where to look — {html.escape(loc_text)}</span><br>{html.escape(quote)}</div>",
            unsafe_allow_html=True,
        )
        if wtl.get("url"):
            st.markdown(f"[Open the source bylaw (PDF) ↗]({wtl['url']})")
    rep = card.get("repair_hint")
    if rep and rep.get("quote"):
        conf = rep.get("confidence")
        conf_txt = f" (match confidence {conf:.0%})" if isinstance(conf, (int, float)) else ""
        page_txt = f" — p.{rep['page']}" if rep.get("page") not in (None, "") else ""
        st.markdown(f"**A stronger source may be{conf_txt}:** “{rep['quote']}”{page_txt}")
    sim = card.get("similar_verified")
    if sim and sim.get("rule"):
        st.markdown(f"**A verified companion rule:** {_rule_sentence(sim['rule'])}")
    if card.get("next_step"):
        st.caption(f"Reviewer next step: {card['next_step']}")
    if card.get("advisory_note"):
        st.caption(card["advisory_note"])


def _render_chat_table(st: Any, table: dict[str, Any]) -> None:
    """Render an embedded data table (rule list or reconstructed dimensional table)."""
    title = str(table.get("title") or "")
    columns = table.get("columns") or []
    rows = table.get("rows") or []
    if not rows:
        return
    display = [{str(col): str(row.get(col, "")) for col in columns} for row in rows]
    st.dataframe(display, width="stretch", hide_index=True)
    if title:
        st.caption(title)


def _render_bylaw_chat_message(st: Any, message: dict[str, Any]) -> None:
    with st.chat_message(message.get("role", "assistant")):
        if message.get("content"):
            st.markdown(message["content"])
        for card in (message.get("rule_cards") or []):
            _render_verification_card(st, card)
        for table in (message.get("tables") or []):
            _render_chat_table(st, table)
        sources = message.get("sources") or []
        if sources:
            with st.expander(f"Sources ({len(sources)})"):
                for index, hit in enumerate(sources, start=1):
                    loc = _clean_section_label(hit.get("section") or hit.get("chunk_id"), hit.get("page")) or "bylaw excerpt"
                    excerpt = _short_display_quote(_strip_internal_tokens(hit.get("section_text") or hit.get("text") or ""), 360)
                    st.markdown(
                        f"<div class='citation'><span class='loc'>[{index}] {html.escape(str(loc))}</span><br>"
                        f"{html.escape(excerpt)}</div>",
                        unsafe_allow_html=True,
                    )


_BYLAW_SUGGESTION_TEMPLATES = {
    ("height", None): "What is the maximum building height?",
    ("setback", "rear_yard"): "What is the rear setback requirement?",
    ("setback", "side_yard"): "What is the side setback requirement?",
    ("setback", "front_yard"): "What is the front setback requirement?",
    ("setback", None): "What setback applies here?",
    ("lot_coverage", None): "What is the maximum lot coverage?",
    ("building_separation", None): "What building separation is required?",
    ("floor_area", None): "What floor area is allowed?",
    ("floor_space_ratio", None): "What is the floor space ratio?",
    ("storeys", None): "How many storeys are permitted?",
    ("lot_area", None): "What is the minimum lot area?",
    ("dwelling_units", None): "How many dwelling units are allowed?",
}

_BYLAW_SUGGESTION_FALLBACK = [
    "What is the maximum building height?",
    "What setbacks apply to the rear and side yards?",
    "What is the maximum lot coverage?",
    "What rules apply to a secondary suite?",
]


def _bylaw_suggestions(data: dict[str, Any], limit: int = 6) -> list[str]:
    """Data-generated chat prompt suggestions (hidden behind the popover).

    Derived from the rule families/scopes actually present in this city's
    verified + review rules, so the hints are never stale hardcoded strings.
    """
    questions: list[str] = []
    seen: set[str] = set()
    rules = list(data.get("verified") or []) + list(data.get("review") or [])
    for rule in rules:
        family = str(rule.get("rule_object") or "")
        scope = str(rule.get("constraint_scope") or "")
        question = _BYLAW_SUGGESTION_TEMPLATES.get((family, scope)) or _BYLAW_SUGGESTION_TEMPLATES.get((family, None))
        if question and question not in seen:
            seen.add(question)
            questions.append(question)
        if len(questions) >= limit:
            break
    for question in _BYLAW_SUGGESTION_FALLBACK:
        if len(questions) >= limit:
            break
        if question not in seen:
            seen.add(question)
            questions.append(question)
    return questions


_CHAT_OUT_OF_SCOPE = (
    "I can only help with this zoning bylaw. Try asking about a specific rule — lot area, "
    "setbacks, height, lot coverage, or dwelling units — or ask why a particular rule is in review."
)
_CHAT_NO_HITS = (
    "I couldn't find a bylaw section for that. Try the bylaw's own terms — setback, height, storey, "
    "lot area, coverage, or suite — or ask why a specific rule is in review."
)


def _chat_brain() -> Any | None:
    """The advisory chat brain (intent routing + verification explanations).

    Tries the installed package first (full features locally, incl. the dense
    rule-corpus index); on the dashboard-only cloud deploy, where the package is
    not installed, it falls back to the byte-identical ``dashboard/chat_brain.py``
    sibling, which is self-contained (no ``burnaby_prototype`` imports) so intent
    routing, verification cards, and tables still work from the deployed JSON.
    Returns ``None`` only if neither is importable (then the chat uses the basic
    retrieval+LLM answer — today's behavior)."""
    try:
        from burnaby_prototype import bylaw_chat

        return bylaw_chat
    except Exception:
        pass
    try:
        import chat_brain  # sibling of streamlit_app.py; on sys.path under `streamlit run`

        return chat_brain
    except Exception:
        return None


def _chat_llm_call(st: Any | None) -> Any | None:
    """A plain ``callable(prompt) -> str`` for the intent router, or ``None``."""
    if not _bylaw_llm_status(st).get("available"):
        return None

    def _call(prompt: str) -> str:
        try:
            return _optional_bylaw_llm_answer(prompt, st, history=None) or ""
        except Exception:
            return ""

    return _call


def _find_by_rule_id(items: Any, rule_id: Any) -> dict[str, Any] | None:
    if not rule_id or not items:
        return None
    for item in items:
        if isinstance(item, dict) and item.get("rule_id") == rule_id:
            return item
    return None


def _cached_rule_index(data: dict[str, Any], st: Any | None, *, tag: str) -> Any | None:
    """Build + session-cache a retrievable index over the verified/review RULES.

    This is the second retrievable source (alongside the bylaw-section index) so
    a question like "why are the setback rules not confirmed?" can semantically
    find the relevant rules even when no exact value is named."""
    brain = _chat_brain()
    retr = _retrieval_module()
    if brain is None or retr is None:
        return None
    cache_key = f"_bylaw_rule_index::{tag}"
    if st is not None:
        try:
            cached = st.session_state.get(cache_key)
            if cached is not None:
                return cached
        except Exception:
            pass
    corpus = brain.build_rule_corpus(data.get("verified") or [], data.get("review") or [])
    if not corpus:
        return None
    try:
        index = retr.HybridBylawIndex(corpus)  # BM25-only (tiny rule corpus)
    except Exception:
        return None
    if st is not None:
        try:
            st.session_state[cache_key] = index
        except Exception:
            pass
    return index


def _answer_grounded(
    st: Any, question: str, query: str, data: dict[str, Any], brain: Any,
    index_path: Path, history: list[dict[str, Any]], intent: str,
) -> dict[str, Any]:
    """Section-grounded LLM answer (specific_rule / definition), with an optional
    verified/review status card when the question names a concrete rule."""
    hits = _dashboard_rag_hits(index_path, query, top_k=RAG_CHAT_TOP_K, st=st)
    if not hits:
        rule = brain.detect_rule_reference(question, data.get("verified") or [], data.get("review") or [])
        if rule is not None:
            return {"role": "assistant", "content": "Here's what I have on that rule:",
                    "rule_cards": [_explain_rule(brain, data, rule)], "intent": intent}
        return {"role": "assistant", "content": _CHAT_NO_HITS, "sources": [], "intent": intent}
    bounded = _bounded_rag_hits(hits)
    prompt = _grounded_bylaw_prompt(question, bounded)
    answer = _optional_bylaw_llm_answer(prompt, st, history=history[-4:]) or _retrieval_only_bylaw_answer(question, bounded)
    message: dict[str, Any] = {"role": "assistant", "content": _strip_internal_tokens(answer), "sources": bounded, "intent": intent}
    if intent == "specific_rule":
        rule = brain.detect_rule_reference(question, data.get("verified") or [], data.get("review") or [])
        if rule is not None:
            message["rule_cards"] = [_explain_rule(brain, data, rule)]
    return message


def _explain_rule(brain: Any, data: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any]:
    """Compose a verification card for one rule, wiring in router/repair/similar context."""
    rid = rule.get("rule_id")
    router_item = _find_by_rule_id((data.get("router") or {}).get("items"), rid)
    repair = _find_by_rule_id((data.get("repair") or {}).get("suggestions"), rid)
    similar_id = (router_item or {}).get("similar_verified_rule_id")
    similar = brain.index_rules_by_id(data.get("verified") or []).get(similar_id) if similar_id else None
    return brain.explain_verification(rule, router_item=router_item, repair_suggestion=repair, similar_verified=similar)


def _answer_why_verification(
    st: Any, question: str, query: str, data: dict[str, Any], brain: Any,
    index_path: Path, history: list[dict[str, Any]],
) -> dict[str, Any]:
    """Explain a rule's verification status in plain language (the headline feature)."""
    verified = data.get("verified") or []
    review = data.get("review") or []
    rule = brain.detect_rule_reference(question, verified, review, prefer="in_review")
    if rule is None:
        index = _cached_rule_index(data, st, tag=str(index_path))
        if index is not None:
            try:
                hits = index.ask(query, top_k=1)
            except Exception:
                hits = []
            if hits and hits[0].get("rule_ref"):
                rule = hits[0]["rule_ref"]
    if rule is None:
        return _answer_grounded(st, question, query, data, brain, index_path, history, "why_verification")
    card = _explain_rule(brain, data, rule)
    # Lead with a warm, plain-language narrative the LLM writes from the card's
    # deterministic facts; the card then carries the evidence + where-to-look.
    narrative = _optional_bylaw_llm_answer(
        brain.verification_narrative_prompt(card, _rule_sentence(rule)),
        st, system=_VERIFY_NARRATIVE_SYSTEM,
    )
    if narrative:
        content = _strip_internal_tokens(narrative)
        card = {**card, "verdict_sentence": "", "why": [], "likely_missing": ""}
    elif card.get("status") == "verified":
        content = f"Good news — that rule is verified. {card.get('verdict_sentence', '')}".strip()
    else:
        content = f"That rule is currently held for review. {card.get('verdict_sentence', '')}".strip()
    return {"role": "assistant", "content": content, "rule_cards": [card], "intent": "why_verification"}


def _answer_list_table(query: str, families: list[str], data: dict[str, Any], brain: Any) -> dict[str, Any]:
    """Embed a table: a reconstructed dimensional bylaw table, or a rule list."""
    verified = data.get("verified") or []
    review = data.get("review") or []
    low = query.lower()
    wants_dim = any(token in low for token in ("dimension", "matrix", "grid", "table of"))
    tables: list[dict[str, Any]] = []
    content = ""
    if wants_dim:
        row_filter = None
        if families:
            fam_words: set[str] = set()
            for fam in families:
                fam_words.update(fam.replace("_", " ").split())
            row_filter = lambda label, fw=fam_words: bool(set(re.findall(r"[a-z]+", label.lower())) & fw)
        tables = brain.reconstruct_dimensional_tables(data.get("evidence_units") or [], row_filter=row_filter)
        if tables:
            content = "Here are the dimensional rules, reconstructed from the bylaw's own tables:"
    if not tables:
        rules = list(verified) + list(review)
        if families:
            fams = set(families)
            filtered = [r for r in rules if str(r.get("rule_object")) in fams]
            rules = filtered or rules
        tables = [brain.rule_list_table(rules)]
        if families:
            label = ", ".join(fam.replace("_", " ") for fam in families)
            content = f"Here are the {label} rules I have for this bylaw (✓ verified and ● in review):"
        else:
            content = "Here are the rules I have for this bylaw (✓ verified and ● in review):"
    return {"role": "assistant", "content": content, "tables": tables, "intent": "list_table"}


_CONCEPT_SYSTEM = (
    "You are a friendly assistant explaining residential zoning and housing concepts in plain language to "
    "homeowners. Give a clear, general, accurate definition with a concrete everyday example. Do NOT claim "
    "what any specific bylaw says — this is a general explanation. Never give legal advice. 2-3 sentences."
)
_VERIFY_NARRATIVE_SYSTEM = (
    "You explain a zoning rule's verification status to a non-expert homeowner in warm, plain language. Use "
    "ONLY the facts provided. Never invent numbers, reasons, or citations, and never output internal codes "
    "or field names."
)
_CONCEPT_NO_LLM = (
    "I can explain zoning concepts in plain language, but no language model is configured here right now. "
    "For a specific number, ask about a rule directly — e.g. “what is the minimum lot area?”"
)


def _answer_definition(st: Any, question: str, query: str, data: dict[str, Any], brain: Any) -> dict[str, Any]:
    """Concept/definition: a general-knowledge explanation (ungrounded, no RAG),
    clearly labelled, with a pointer to the bylaw's specific number when relevant."""
    prompt = (
        f'A user asked: "{question}"\n'
        "Explain, in 2-3 plain sentences for a non-expert homeowner, what this means in residential "
        "zoning/housing. If it is a well-known term (setback, laneway house, FSR, lot coverage, storey, "
        "etc.), define it simply and concretely with an everyday example. Do not cite or claim anything "
        "about a specific bylaw."
    )
    # Concept answers are ungrounded + stable, so cache them per session by the
    # normalized question (repeated "what is a setback?" costs zero extra calls).
    qnorm = " ".join(str(question or "").lower().split())
    cache = None
    try:
        cache = st.session_state.setdefault("_concept_cache", {})
    except Exception:
        cache = None
    answer = cache.get(qnorm) if isinstance(cache, dict) else None
    if not answer:
        answer = _optional_bylaw_llm_answer(prompt, st, system=_CONCEPT_SYSTEM)
        if answer and isinstance(cache, dict):
            cache[qnorm] = answer
    if not answer:
        return {"role": "assistant", "content": _CONCEPT_NO_LLM, "intent": "definition"}
    content = "Here's a general explanation (not specific legal text from this bylaw):\n\n" + _strip_internal_tokens(answer)
    families = brain._families_in(query)
    if families:
        fam = families[0].replace("_", " ")
        content += f"\n\n*To see what **this** bylaw sets for {fam}, ask e.g. “what is the {fam}?”*"
    return {"role": "assistant", "content": content, "intent": "definition"}


def _build_brain_answer(
    st: Any, question: str, index_path: Path, data: dict[str, Any],
    history: list[dict[str, Any]], brain: Any,
) -> dict[str, Any]:
    """Route the question to an intent and build the matching answer payload."""
    verified = data.get("verified") or []
    review = data.get("review") or []
    pre = brain._keyword_route(question, history)
    # Call the LLM router only when it adds value: follow-ups (need pronoun
    # resolution) or an ambiguous/out-of-scope first read. Clear first-turn
    # questions are routed by the deterministic keyword router (cheaper, instant).
    use_llm = bool(history) or pre.get("intent") == "out_of_scope"
    route = brain.reformulate_and_route(
        question, history, llm_call=(_chat_llm_call(st) if use_llm else None)
    )
    intent = route.get("intent")
    query = route.get("standalone_query") or question
    families = route.get("families") or []

    if intent == "out_of_scope":
        return {"role": "assistant", "content": _CHAT_OUT_OF_SCOPE, "intent": intent}
    if intent == "definition":
        return _answer_definition(st, question, query, data, brain)
    if intent == "why_verification" and (verified or review):
        return _answer_why_verification(st, question, query, data, brain, index_path, history)
    if intent == "list_table" and (verified or review or data.get("evidence_units")):
        return _answer_list_table(query, families, data, brain)
    return _answer_grounded(st, question, query, data, brain, index_path, history, intent)


def _build_basic_answer(st: Any, question: str, index_path: Path, history: list[dict[str, Any]]) -> dict[str, Any]:
    """Fallback when the chat brain is unavailable: today's retrieve -> ground -> answer."""
    hits = _dashboard_rag_hits(index_path, question, top_k=RAG_CHAT_TOP_K, st=st)
    if not hits:
        return {"role": "assistant", "content": _CHAT_NO_HITS, "sources": []}
    bounded = _bounded_rag_hits(hits)
    prompt = _grounded_bylaw_prompt(question, bounded)
    answer = _optional_bylaw_llm_answer(prompt, st, history=history[-4:]) or _retrieval_only_bylaw_answer(question, bounded)
    return {"role": "assistant", "content": _strip_internal_tokens(answer), "sources": bounded}


def _bylaw_chat_respond(st: Any, question: str, index_path: Path, chat_key: str, data: dict[str, Any] | None = None) -> None:
    """Run one chat turn and APPEND it to the transcript.

    Routes the question to an intent (knowledge / verification-explanation /
    list-table / out-of-scope) and builds a rich answer (plain text + optional
    rule cards + tables). Falls back to the basic retrieval answer if the brain
    or a branch fails. ADVISORY: never verifies, approves, rejects, or writes."""
    data = data or {}
    st.session_state[chat_key].append({"role": "user", "content": question})
    history = list(st.session_state[chat_key][:-1])
    message: dict[str, Any] | None = None
    brain = _chat_brain()
    if brain is not None:
        try:
            message = _build_brain_answer(st, question, index_path, data, history, brain)
        except Exception:
            message = None
    if message is None:
        message = _build_basic_answer(st, question, index_path, history)
    message["question"] = question
    st.session_state[chat_key].append(message)


def _secret_value(st: Any | None, name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    if st is None:
        return ""
    try:
        secret = st.secrets.get(name, "")
    except Exception:
        return ""
    return str(secret or "")


def _bylaw_llm_status(st: Any | None = None) -> dict[str, Any]:
    preferred = (_secret_value(st, "BYLAW_RAG_PROVIDER") or "").strip().lower()
    openrouter_key = _secret_value(st, "OPENROUTER_API_KEY")
    gemini_key = (
        _secret_value(st, "GEMINI_API_KEY")
        or _secret_value(st, "GOOGLE_API_KEY")
        or _secret_value(st, "GOOGLE_GENAI_API_KEY")
    )
    openai_key = _secret_value(st, "OPENAI_API_KEY")
    anthropic_key = _secret_value(st, "ANTHROPIC_API_KEY") or _secret_value(st, "CLAUDE_API_KEY")

    def _status(provider: str, key: str, model: str) -> dict[str, Any]:
        return {
            "provider": provider,
            "model": _secret_value(st, "BYLAW_RAG_MODEL") or model,
            "available": bool(key),
            "configured": bool(key),
        }

    if preferred in {"openrouter", "open-router"}:
        return _status("openrouter", openrouter_key, DEFAULT_BYLAW_CHAT_MODEL)
    if preferred in {"gemini", "google"}:
        return _status("gemini", gemini_key, _secret_value(st, "GEMINI_MODEL") or "gemini-2.0-flash-lite")
    if preferred in {"openai", "openai-compatible"}:
        return _status("openai", openai_key, _secret_value(st, "OPENAI_MODEL") or "gpt-4o-mini")
    if preferred in {"anthropic", "claude"}:
        return _status("anthropic", anthropic_key, _secret_value(st, "CLAUDE_MODEL") or "claude-3-5-haiku-latest")
    # Auto-detect: OpenRouter first — the project's .env already ships an
    # OPENROUTER_API_KEY (the same key the extraction layer uses), so the chat
    # works out of the box with no extra configuration.
    if openrouter_key:
        return _status("openrouter", openrouter_key, DEFAULT_BYLAW_CHAT_MODEL)
    if gemini_key:
        return _status("gemini", gemini_key, _secret_value(st, "GEMINI_MODEL") or "gemini-2.0-flash-lite")
    if openai_key:
        return _status("openai", openai_key, _secret_value(st, "OPENAI_MODEL") or "gpt-4o-mini")
    if anthropic_key:
        return _status("anthropic", anthropic_key, _secret_value(st, "CLAUDE_MODEL") or "claude-3-5-haiku-latest")
    return {"provider": "none", "model": "", "available": False, "configured": False}


def _optional_bylaw_llm_answer(
    prompt: str,
    st: Any | None = None,
    history: list[dict[str, Any]] | None = None,
    system: str | None = None,
) -> str | None:
    """Answer via the configured provider. ``system`` overrides the default
    grounded system prompt — used for concept/definition answers (general
    knowledge, ungrounded) and the plain-language verification narrative."""
    status = _bylaw_llm_status(st)
    if not status.get("available"):
        return None
    provider = status["provider"]
    if provider == "openrouter":
        return _openrouter_answer(prompt, _secret_value(st, "OPENROUTER_API_KEY"), status["model"], history, system)
    if provider == "gemini":
        key = _secret_value(st, "GEMINI_API_KEY") or _secret_value(st, "GOOGLE_API_KEY") or _secret_value(st, "GOOGLE_GENAI_API_KEY")
        return _gemini_answer(prompt, key, status["model"], system)
    if provider == "openai":
        return _openai_answer(prompt, _secret_value(st, "OPENAI_API_KEY"), status["model"], st, system)
    if provider == "anthropic":
        key = _secret_value(st, "ANTHROPIC_API_KEY") or _secret_value(st, "CLAUDE_API_KEY")
        return _anthropic_answer(prompt, key, status["model"], system)
    return None


_BYLAW_CHAT_SYSTEM = (
    "You are an advisory zoning-bylaw assistant for human reviewers — you never approve, verify, "
    "reject, or promote a rule. Answer only from the provided bylaw excerpts, but read and reason "
    "across them and explain in plain English: lead with the number in **bold**, then a brief why "
    "(≤4 short sentences, no bullet lists). Cite each claim as (§section, p.page) and never output "
    "internal ids, rule ids, or 【…】 tokens."
)


def _openrouter_answer(
    prompt: str,
    api_key: str,
    model: str,
    history: list[dict[str, Any]] | None = None,
    system: str | None = None,
) -> str:
    """Answer via OpenRouter's OpenAI-compatible chat-completions endpoint.

    Prior conversation turns (trimmed) are included so follow-up questions read
    naturally, while the final user message carries the freshly retrieved,
    section-grounded prompt — keeping every answer anchored to source text.
    """
    messages: list[dict[str, str]] = [{"role": "system", "content": system or _BYLAW_CHAT_SYSTEM}]
    for turn in (history or [])[-6:]:
        role = turn.get("role")
        content = turn.get("content")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": str(content)[:1500]})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model or DEFAULT_BYLAW_CHAT_MODEL,
        "temperature": 0.0,
        "max_tokens": 800,
        "messages": messages,
    }
    data = _post_json(
        "https://openrouter.ai/api/v1/chat/completions",
        payload,
        {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/ubco-mds-2025-labs",
            "X-Title": "Bylaw Verification Dashboard",
        },
    )
    if data.get("_error"):
        return f"LLM unavailable: {data['_error']}"
    return str((((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "")).strip() or "The LLM returned no text."


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int = 35) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")[:500]
        return {"_error": f"HTTP {error.code}: {body}"}
    except Exception as error:
        return {"_error": f"{type(error).__name__}: {error}"}


def _gemini_answer(prompt: str, api_key: str, model: str, system: str | None = None) -> str:
    model_name = str(model or "gemini-2.0-flash-lite").removeprefix("models/")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{urllib.parse.quote(model_name, safe='-._~')}:generateContent?key={urllib.parse.quote(api_key)}"
    )
    if system:
        prompt = f"{system}\n\n{prompt}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.0, "maxOutputTokens": 700},
    }
    data = _post_json(url, payload, {})
    if data.get("_error"):
        return f"LLM unavailable: {data['_error']}"
    parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
    text = "\n".join(str(part.get("text") or "") for part in parts).strip()
    return text or "The LLM returned no text."


def _openai_answer(prompt: str, api_key: str, model: str, st: Any | None = None, system: str | None = None) -> str:
    base_url = (_secret_value(st, "OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    payload = {
        "model": model or "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 700,
        "messages": [
            {"role": "system", "content": system or "You answer only from retrieved zoning bylaw excerpts. Never approve or verify rules."},
            {"role": "user", "content": prompt},
        ],
    }
    data = _post_json(f"{base_url}/chat/completions", payload, {"Authorization": f"Bearer {api_key}"})
    if data.get("_error"):
        return f"LLM unavailable: {data['_error']}"
    return str((((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "")).strip() or "The LLM returned no text."


def _anthropic_answer(prompt: str, api_key: str, model: str, system: str | None = None) -> str:
    payload = {
        "model": model or "claude-3-5-haiku-latest",
        "max_tokens": 700,
        "temperature": 0.0,
        "system": system or "You answer only from retrieved zoning bylaw excerpts. Never approve or verify rules.",
        "messages": [{"role": "user", "content": prompt}],
    }
    data = _post_json(
        "https://api.anthropic.com/v1/messages",
        payload,
        {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
    )
    if data.get("_error"):
        return f"LLM unavailable: {data['_error']}"
    blocks = data.get("content") or []
    return "\n".join(str(block.get("text") or "") for block in blocks if block.get("type") == "text").strip() or "The LLM returned no text."


def _followup_chips(message: dict[str, Any]) -> list[tuple[str, str]]:
    """Context-aware next-step chips for the latest answer (label, question).

    Clicking one re-asks via the same ``pending`` mechanism as the suggestion
    chips, so multi-turn stays robust."""
    if not message or message.get("role") != "assistant":
        return []
    intent = message.get("intent")
    if intent == "why_verification":
        chips = [("📋 See all rules as a table", "List all the rules as a table"),
                 ("✅ Which rules are verified?", "List the verified rules as a table")]
    elif intent == "specific_rule":
        chips = [("❓ Why are some rules in review?", "Why are some rules still in review?"),
                 ("📋 See all rules as a table", "List all the rules as a table")]
    elif intent == "list_table":
        chips = [("❓ Why are some still in review?", "Why are some rules still in review?")]
    elif intent == "definition":
        chips = [("📐 What does this bylaw require?", "List all the rules as a table")]
    else:
        chips = []
    return chips[:3]


def _ask_the_bylaw_panel(st: Any, output_dir: Path, data: dict[str, Any] | None = None) -> None:
    """Conversational, source-grounded bylaw assistant — a real LLM chat that
    answers ONLY from retrieved bylaw sections. ADVISORY: it never verifies,
    approves, rejects, edits JSON, or changes GIS outputs."""
    data = data or {}
    index_path = bylaw_index_path(output_dir)
    city_stem = city_stem_from_dir(output_dir)
    city_label = city_label_from_dir(output_dir)
    llm_status = _bylaw_llm_status(st)

    st.markdown("<div class='chat-shell'>", unsafe_allow_html=True)
    mode_pill = (
        f"<span class='mode-pill live'>LLM + RAG · {html.escape(str(llm_status['provider']))}</span>"
        if llm_status.get("available")
        else "<span class='mode-pill'>Retrieval only</span>"
    )
    st.markdown(
        "<div style='display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px;'>"
        "<span class='chat-ribbon'>Advisory · answers come from retrieved bylaw sections · cannot verify, approve, reject, or edit outputs</span>"
        f"{mode_pill}</div>",
        unsafe_allow_html=True,
    )

    if index_path is None:
        st.info(
            "No retrieval index yet — build it with "
            f"`.venv/bin/python scripts/build_rag_index.py --city {city_stem}`."
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    chat_key = _rag_chat_key(city_stem)
    st.session_state.setdefault(chat_key, [])
    history = st.session_state[chat_key]

    head_left, head_right = st.columns([5, 1])
    if head_right.button("↺ New chat", key=f"clear_{chat_key}"):
        st.session_state[chat_key] = []
        history = st.session_state[chat_key]

    if not history:
        st.markdown(
            f"<div class='chat-empty'><h2>Ask about the {html.escape(city_label)} bylaw</h2>"
            "<p>Plain-English questions about setbacks, height, coverage, suites, and parcels. "
            "Every answer cites the section it came from. I can't approve, reject, or change anything.</p></div>",
            unsafe_allow_html=True,
        )

    # Suggested questions as always-visible chips so they reliably load.
    # st.chat_input cannot be pre-filled, so clicking a chip ASKS the question
    # directly — this is also what keeps multi-turn rock-solid (the previous
    # text_input-in-a-form + session_state prefill broke after one question).
    pending = None
    suggestions = _bylaw_suggestions(data)
    if suggestions:
        st.caption("Try one of these — or type your own below:")
        chip_cols = st.columns(min(3, len(suggestions)))
        for index, suggestion in enumerate(suggestions[:6]):
            if chip_cols[index % len(chip_cols)].button(suggestion, key=f"sugg_{city_stem}_{index}", width="stretch"):
                pending = suggestion

    # The conversation renders above; the chat box stays pinned at the bottom and
    # supports as many turns as you like in one conversation.
    for message in history:
        _render_bylaw_chat_message(st, message)
    if history and history[-1].get("role") == "assistant":
        followups = _followup_chips(history[-1])
        if followups:
            fcols = st.columns(len(followups))
            for i, (label, fq) in enumerate(followups):
                if fcols[i].button(label, key=f"fup_{city_stem}_{len(history)}_{i}", width="stretch"):
                    pending = fq
    st.caption("I find the relevant bylaw sections, then read and explain them — every answer cites its section. Advisory only; I can't approve or change a rule.")

    typed = st.chat_input("Ask about the bylaw…", key=f"rag_chat_input_{city_stem}")
    question = typed or pending
    if question:
        q = str(question).strip()
        # Show the question right away, then an animated spinner while the LLM
        # reads the sections, then the answer — so it's clear it's working.
        _render_bylaw_chat_message(st, {"role": "user", "content": q})
        with st.spinner("Reading the bylaw…"):
            _bylaw_chat_respond(st, q, index_path, chat_key, data)
        if history:
            _render_bylaw_chat_message(st, history[-1])
    st.markdown("</div>", unsafe_allow_html=True)


def _bylaw_tab(st: Any, data: dict[str, Any]) -> None:
    """Conversational bylaw assistant — the whole tab is the chat now.

    The former nested sub-tabs (Ask Source / Explain Verified Rule / Why In
    Review / Prompt Library) collapsed into one chat: their example questions
    became the data-generated, hidden ``Need ideas?`` suggestions, and the
    section text now rides along in each answer's collapsed citation cards.
    """
    output_dir = Path(data.get("output_dir") or DEFAULT_OUTPUT_DIR)
    _ask_the_bylaw_panel(st, output_dir, data)


_SECTION_BLURB = {
    "Overview": "The shortest path: verification result first, source-grounded chat second.",
    "Source Documents": "Official bylaw PDFs, scoped source pages, and evidence packets used by the verifier.",
    "Verified Rules": "Source-supported rules that can be used downstream.",
    "Human Review": "One held candidate at a time: why it is blocked, what differs, and what to inspect next.",
    "Repair Evidence": "Shadow evidence checks: what improved, what still blocks verification, and why outputs do not change automatically.",
    "GIS Handoff": "Verified-only, deduplicated rules prepared for GIS use.",
    "Ask the Bylaw": "A source-grounded assistant. It cites sections and can never approve or change a rule.",
    "Quality Checks": "Audit support for source coverage, status mix, and verification-flow diagnostics.",
    "Source Library": "Committed bylaw sources, evidence packets, and source coverage.",
    "Review Queue": "Rules the verifier could not prove — your worklist, each shown as a sentence with the gap in red.",
    "GIS Contract": "Verified-only, geometry-tagged rules ready for GIS handoff.",
    "Analytics": "Quality, status mix, and verification-flow diagnostics.",
    "Settings": "Read-only local dashboard settings.",
    "Diagnostics": "Engineering & audit views — not part of the reviewer workflow.",
}


_SECTION_BADGES = {
    "Source Documents": ("Source evidence", "status-not_used"),
    "Verified Rules": ("Verified-only output", "status-verified"),
    "Human Review": ("Human review", "status-review"),
    "Repair Evidence": ("Shadow only", "status-review"),
    "GIS Handoff": ("GIS handoff", "status-verified"),
    "Quality Checks": ("Quality audit", "status-not_used"),
    "Review Queue": ("Review worklist", "status-review"),
    "Source Library": ("Source evidence", "status-not_used"),
    "GIS Contract": ("GIS handoff", "status-verified"),
    "Analytics": ("Quality diagnostics", "status-not_used"),
    "Ask the Bylaw": ("Advisory chat", "status-review"),
    "Settings": ("Read-only settings", "status-not_used"),
    "Diagnostics": ("Engineering view", "status-not_used"),
}


def _render_header(st: Any, city_label: str = "Burnaby R1", *, portfolio: bool = False, section: str = "") -> None:
    """Compact breadcrumb header: City › Section, so 'where am I' is always visible."""
    if portfolio:
        crumb = "M7 · Portfolio"
        title = city_label
        body = "The current M7 product path. The deterministic verifier is the authority."
        badge_text, badge_class = "Final demo path", "status-verified"
    else:
        crumb = f"M7 · {html.escape(city_label)}" + (f" › <b>{html.escape(section)}</b>" if section else "")
        title = section or f"{city_label} Rule Review"
        body = _SECTION_BLURB.get(section, "")
        badge_text, badge_class = _SECTION_BADGES.get(section, ("Read-only", "status-not_used"))
    st.markdown(
        f"""
<div class="app-header">
  <div>
    <div class="crumb">{crumb}</div>
    <h1>{html.escape(title)}</h1>
    <p>{html.escape(body)}</p>
  </div>
  <div class="status-legend">
    <span class="status-pill {html.escape(badge_class)}">{html.escape(badge_text)}</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _sidebar_guidance(st: Any) -> None:
    """Keep short usage instructions visible near the filters."""
    with st.sidebar.expander("Decision language", expanded=False):
        st.markdown(
            """
- **Verified**: exact source support exists for the rule fields.
- **Review**: plausible, needs a human check.
- **Rejected**: the candidate conflicts with the verifier contract or source support.
- **Not used**: outside the current product scope.
- **Recall**: benchmark recall, not full-bylaw completeness.
"""
        )


def _router_item_row(item: dict[str, Any]) -> dict[str, Any]:
    """One reviewer-queue row: which rule, what it claims, why held, next step."""
    return {
        "Rule ID": item.get("rule_id") or item.get("candidate_id"),
        "Rule family": _humanize(item.get("rule_object")),
        "What it says": _short_display_quote(item.get("candidate_sentence") or "", 150),
        "Why it's held": _plain_label(item.get("review_category") or item.get("blocking_reason") or ""),
        "Next step": _short_display_quote(item.get("human_instruction") or item.get("next_step") or item.get("next_action") or "", 130),
    }


def _action_summary(st: Any, data: dict[str, Any]) -> None:
    """Surface the highest-value review-volume reduction paths.

    Each card's number is the exact set of queued rules in its action buckets,
    and an expander under the cards lists those precise rules (rule id, plain
    claim, why it is held, and the next step) so a reviewer can jump from a
    count straight to the rules behind it.
    """
    items_by_bucket: dict[str, list[dict[str, Any]]] = {}
    for item in data.get("router", {}).get("items", []):
        items_by_bucket.setdefault(str(item.get("action_bucket") or ""), []).append(item)

    categories = [
        (
            "Can improve with better source evidence",
            ("rerun_with_evidence_bundle", "retry_with_better_evidence", "condition_evidence_needed"),
            "Start here. These candidates may be held because the evidence packet is incomplete.",
        ),
        (
            "Need direction-word check",
            ("operator_review",),
            "The number is visible, but the source must prove minimum, maximum, or exact wording.",
        ),
        (
            "Need legal scope review",
            ("human_legal_review", "scope_review"),
            "These involve exceptions, scope, or interpretation. Keep them untrusted unless proven.",
        ),
    ]
    resolved = [
        (title, [rule for bucket in buckets for rule in items_by_bucket.get(bucket, [])], body)
        for title, buckets, body in categories
    ]

    html_cards = []
    for title, rules, body in resolved:
        html_cards.append(
            "<div class='action-card'>"
            f"<div class='action-value'>{len(rules)}</div>"
            f"<div class='action-title'>{html.escape(title)}</div>"
            f"<p>{html.escape(body)}</p>"
            "</div>"
        )
    st.markdown("<div class='action-grid'>" + "".join(html_cards) + "</div>", unsafe_allow_html=True)

    any_rules = any(rules for _, rules, _ in resolved)
    if any_rules:
        st.caption("Open a path to see exactly which rules it covers.")
    for title, rules, _ in resolved:
        if not rules:
            continue
        with st.expander(f"View these {len(rules)} rule{'s' if len(rules) != 1 else ''} · {title}", expanded=False):
            st.dataframe(_display_rows([_router_item_row(rule) for rule in rules]), width="stretch", hide_index=True)


def _sentence_card(st: Any, title: str, sentence: str, tone: str, caption: str = "") -> None:
    """Render one plain-language rule claim."""
    st.markdown(
        "<div class='sentence-card sentence-{}'>"
        "<div class='sentence-title'>{}</div>"
        "<p>{}</p>"
        "<span>{}</span>"
        "</div>".format(
            html.escape(tone),
            html.escape(title),
            html.escape(sentence),
            html.escape(str(caption or "")),
        ),
        unsafe_allow_html=True,
    )


def _rule_sentence(rule: dict[str, Any]) -> str:
    """Convert a structured rule into a reviewer-readable sentence that LEADS
    with the constraint, e.g. "Maximum building height is 10 m for a front
    principal building (sloping roof)." Deterministic; no legal inference.
    """
    if not rule:
        return "No rule is available."

    obj = _humanize(rule.get("rule_object")) or "rule"
    scope = (_humanize(rule.get("constraint_scope")) or "").strip()
    applies = str(rule.get("applies_to") or "").strip()
    condition = str(rule.get("condition") or "").strip()
    exception = str(rule.get("exception") or "").strip()
    value_text = _format_value_unit(rule.get("value"), str(rule.get("unit") or "").strip())
    direction = f"{str(rule.get('operator') or '')} {str(rule.get('constraint_type') or '')}".lower()
    obj_l = obj[:1].lower() + obj[1:]  # keep the object lowercase after "Maximum/Minimum"

    if any(t in direction for t in ("<=", "maximum", "max", "not_exceed")):
        lead = f"Maximum {obj_l} is {value_text}" if value_text else f"{obj_l} has a maximum"
    elif any(t in direction for t in (">=", "minimum", "min", "at_least")):
        lead = f"Minimum {obj_l} is {value_text}" if value_text else f"{obj_l} has a minimum"
    elif ">" in direction:
        lead = f"{obj_l} must be more than {value_text}"
    elif "<" in direction:
        lead = f"{obj_l} must be less than {value_text}"
    elif any(t in direction for t in ("allowed", "permitted")):
        lead = f"{obj_l} is permitted" + (f" ({value_text})" if value_text else "")
    elif "required" in direction:
        lead = f"{obj_l} is required" + (f" ({value_text})" if value_text else "")
    else:
        lead = f"{obj_l} is {value_text}" if value_text else f"{obj_l} is claimed"
    lead = lead[:1].upper() + lead[1:]

    # Drop a "condition" that just restates the object/direction (table headings
    # like "Minimum Lot Area" leak into the condition field).
    obj_words = set(re.findall(r"[a-z0-9]+", obj.lower()))
    cond_words = set(re.findall(r"[a-z0-9]+", condition.lower()))
    if cond_words and cond_words <= (obj_words | {"minimum", "maximum", "min", "max"}):
        condition = ""

    generic = {"the relevant proposal item", "the relevant parcel or proposal item", "lot", ""}
    target = ""
    if scope and scope.lower() not in obj.lower() and obj.lower() not in scope.lower():
        target = scope
    elif applies and applies.lower() not in generic:
        target = applies
    sentence = lead + (f" for {target}" if target else "")
    extras = []
    if target == scope and applies and applies.lower() not in generic and applies.lower() != target.lower():
        extras.append(applies)
    if condition:
        extras.append(condition)
    if extras:
        sentence += " (" + "; ".join(extras) + ")"
    if exception:
        sentence += f", except {exception}"
    return sentence.rstrip(" .") + "."


# Map each support-gap code to the rule FIELD it implicates (reverse of the
# verifier's CLAIM_TO_SUPPORT_GAP) so the review view can paint that field red.
# Inlined here (not imported from burnaby_prototype) so the dashboard stays
# self-contained on Streamlit Cloud, where the package is not installed.
_GAP_FIELD = {
    "value_not_found_in_evidence": "value", "value_bound_to_foreign_unit": "value",
    "column_value_mismatch": "value", "range_bound_not_maximum": "value",
    "coefficient_operand_not_value": "value",
    "unit_not_found_in_evidence": "unit", "rule_object_unit_not_compatible": "unit",
    "operator_not_supported": "operator", "table_operator_refuted": "operator",
    "rule_family_direction_mismatch": "operator",
    "applies_to_not_supported": "applies_to", "table_applies_to_not_supported": "applies_to",
    "applicability_not_grounded": "applies_to",
    "constraint_scope_not_supported": "scope", "table_column_not_target_scope": "scope",
    "column_qualifier_not_claimed": "scope",
    "text_condition_not_supported": "condition", "table_condition_not_supported": "condition",
    "conditional_cell_condition_missing": "condition", "unresolved_exception_cue": "condition",
    "enumerated_branch_condition_missing": "condition", "allowance_trigger_threshold": "condition",
    "rule_object_not_supported": "rule_object", "rule_object_not_canonical": "rule_object",
    "table_rule_object_not_supported": "rule_object", "anchored_row_family_mismatch": "rule_object",
}
_GAP_FIELD_REASON = {
    "value": "the value is not clearly supported by the cited text",
    "unit": "the unit is not supported by the cited text",
    "operator": "the direction (minimum/maximum) is not clearly supported",
    "applies_to": "what it applies to is not grounded in the cited text",
    "scope": "the scope or column is not grounded in the cited text",
    "condition": "a condition or exception still needs review",
    "rule_object": "the rule family is not clearly supported by the cited text",
}


def _gap_fields(rule: dict[str, Any]) -> list[str]:
    """Distinct rule fields implicated by this rule's support gaps, in field order."""
    gaps = rule.get("support_gaps") or []
    order = ["value", "unit", "operator", "applies_to", "scope", "condition", "rule_object"]
    hit = {_GAP_FIELD[g] for g in gaps if g in _GAP_FIELD}
    return [field for field in order if field in hit]


def _gap_reason(rule: dict[str, Any]) -> str:
    """One plain-English 'held because…' line for a review/rejected rule."""
    fields = _gap_fields(rule)
    if fields:
        return "; ".join(_GAP_FIELD_REASON[f] for f in fields)
    gaps = rule.get("support_gaps") or []
    if gaps:
        return _plain_join(gaps[:3])
    return "this candidate needs a human check"


def _field_display_text(rule: dict[str, Any], field: str) -> str:
    if field == "value":
        return _format_value_unit(rule.get("value"), str(rule.get("unit") or "").strip())
    if field == "unit":
        return str(rule.get("unit") or "").strip()
    if field == "applies_to":
        return str(rule.get("applies_to") or "").strip()
    if field == "scope":
        return (_humanize(rule.get("constraint_scope")) or "").strip()
    if field == "rule_object":
        return (_humanize(rule.get("rule_object")) or "").strip()
    if field == "operator":
        direction = f"{str(rule.get('operator') or '')} {str(rule.get('constraint_type') or '')}".lower()
        if any(t in direction for t in ("<=", "max")):
            return "Maximum"
        if any(t in direction for t in (">=", "min")):
            return "Minimum"
    return ""


def _review_sentence_html(rule: dict[str, Any]) -> str:
    """The rule as a sentence with the un-grounded field(s) painted red, plus a
    one-line 'held because…'. Best-effort inline highlight; the reason line is
    the guaranteed-clear part."""
    escaped = html.escape(_rule_sentence(rule))
    for field in _gap_fields(rule):
        text = _field_display_text(rule, field)
        if not text:
            continue
        esc_text = html.escape(text)
        if esc_text and esc_text in escaped:
            escaped = escaped.replace(esc_text, f"<span class='gap-flag'>{esc_text}</span>", 1)
    reason = _gap_reason(rule)
    why = f"<div class='gap-why'>⚠ Held because {html.escape(reason)}.</div>" if reason else ""
    return f"<div class='rule-text'>{escaped}</div>{why}"


def _rule_sentence_list(st: Any, rules: list[dict[str, Any]], *, show_gap: bool = False, limit: int = 400) -> None:
    """Render rules as a numbered list of plain-English sentence cards. When
    show_gap is set, the un-grounded field is highlighted red with a reason."""
    if not rules:
        st.caption("None in this bucket.")
        return
    for index, rule in enumerate(rules[:limit], start=1):
        body = _review_sentence_html(rule) if show_gap else f"<div class='rule-text'>{html.escape(_rule_sentence(rule))}</div>"
        st.markdown(
            f"<div class='rule-card'><span class='rule-num'>{index}</span><div class='rule-body'>{body}</div></div>",
            unsafe_allow_html=True,
        )
    if len(rules) > limit:
        st.caption(f"Showing the first {limit} of {len(rules)} rules.")


def _rule_source_page_label(rule: dict[str, Any]) -> str:
    source = rule.get("source") if isinstance(rule.get("source"), dict) else {}
    page = rule.get("page") or source.get("page") or source.get("pdf_page") or source.get("source_page")
    if page not in (None, ""):
        return f"Page {page}"
    evidence_id = str(rule.get("evidence_id") or "")
    match = re.search(r"(?:page|p)[_-]?(\d+)", evidence_id, re.IGNORECASE)
    if match:
        return f"Page {match.group(1)}"
    return "Source page unknown"


def _rule_priority_label(rule: dict[str, Any]) -> str:
    return _plain_label(rule.get("triage_priority") or rule.get("review_priority") or "medium") or "Medium"


def _rule_group_label(rule: dict[str, Any], group_mode: str) -> str:
    if group_mode == "issue":
        return _issue_label(rule)
    if group_mode == "priority":
        return _rule_priority_label(rule)
    if group_mode == "source_page":
        return _rule_source_page_label(rule)
    return _plain_label(rule.get("rule_object") or rule.get("constraint_scope") or "Other rules") or "Other rules"


def _group_sort_key(group_mode: str, label: str, rules: list[dict[str, Any]]) -> tuple[Any, ...]:
    if group_mode == "priority":
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        return (priority_order.get(label, 9), -len(rules), label)
    if group_mode == "source_page":
        match = re.search(r"\d+", label)
        page = int(match.group(0)) if match else 99999
        return (page, label)
    return (-len(rules), label)


def _rule_groups(rules: list[dict[str, Any]], group_mode: str) -> list[tuple[str, list[dict[str, Any]]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for rule in rules:
        grouped.setdefault(_rule_group_label(rule, group_mode), []).append(rule)
    return sorted(grouped.items(), key=lambda item: _group_sort_key(group_mode, item[0], item[1]))


def _group_summary_html(groups: list[tuple[str, list[dict[str, Any]]]], group_mode: str) -> str:
    if not groups:
        return ""
    title = {
        "issue": "Issue groups",
        "priority": "Priority groups",
        "source_page": "Source page groups",
        "rule_family": "Rule family groups",
    }.get(group_mode, "Rule groups")
    cards = []
    for label, items in groups[:8]:
        cards.append(
            "<div class='group-chip-card'>"
            f"<b>{html.escape(label)}</b>"
            f"<span>{len(items)} rule{'s' if len(items) != 1 else ''}</span>"
            "</div>"
        )
    if len(groups) > 8:
        cards.append(
            "<div class='group-chip-card muted'>"
            f"<b>More groups</b><span>{len(groups) - 8} hidden below</span>"
            "</div>"
        )
    return (
        "<div class='group-summary'>"
        f"<div class='group-summary-title'>{html.escape(title)}</div>"
        "<div class='group-summary-grid'>"
        + "".join(cards)
        + "</div></div>"
    )


def _safe_key_fragment(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:48] or "group"


def _grouped_rule_sentence_list(
    st: Any,
    rules: list[dict[str, Any]],
    *,
    group_mode: str = "rule_family",
    show_gap: bool = False,
    key_prefix: str = "rule_groups",
    per_group_limit: int = 8,
) -> None:
    """Render many rules as grouped expanders so the page stays short."""
    if not rules:
        st.caption("None in this bucket.")
        return
    groups = _rule_groups(rules, group_mode)
    st.markdown(_group_summary_html(groups, group_mode), unsafe_allow_html=True)
    for index, (label, items) in enumerate(groups):
        group_title = f"{label} - {len(items)} rule{'s' if len(items) != 1 else ''}"
        with st.expander(group_title, expanded=False):
            st.caption("Open only the group you need. Large groups show a small preview first.")
            display_limit = min(per_group_limit, len(items))
            if len(items) > per_group_limit:
                show_all = st.checkbox(
                    f"Show all {len(items)} rules in this group",
                    key=f"{key_prefix}_show_all_{index}_{_safe_key_fragment(label)}",
                )
                display_limit = len(items) if show_all else per_group_limit
            _rule_sentence_list(st, items, show_gap=show_gap, limit=display_limit)


def _rule_fields_md(rule: dict[str, Any]) -> str:
    """Vertical key/value list of a rule's fields — readable, never squeezed."""
    pairs = [
        ("Rule family", _humanize(rule.get("rule_object"))),
        ("Scope", _humanize(rule.get("constraint_scope"))),
        ("Applies to", rule.get("applies_to")),
        ("Direction", _operator_short(rule.get("operator"), rule.get("constraint_type"))),
        ("Value", _format_value_unit(rule.get("value"), str(rule.get("unit") or "").strip())),
        ("Condition", rule.get("condition")),
        ("Exception", rule.get("exception")),
    ]
    return "\n".join(f"- **{label}:** {value}" for label, value in pairs if value not in (None, "", "—"))


def _rule_option_label(rule: dict[str, Any]) -> str:
    if not rule:
        return ""
    rule_id = str(rule.get("rule_id") or rule.get("original_rule_id") or "").strip()
    family = _plain_label(rule.get("rule_object"))
    value = _format_value_unit(rule.get("value"), str(rule.get("unit") or ""))
    reason = _plain_label(rule.get("review_category") or rule.get("action_bucket") or rule.get("retry_decision"))
    parts = [part for part in (rule_id, family, value, reason) if part]
    return " | ".join(parts)


def _operator_phrase(operator: Any, constraint_type: Any, value_text: str) -> str:
    """Map machine operators to concise natural-language wording."""
    text = f"{operator or ''} {constraint_type or ''}".lower()
    if any(token in text for token in ("<=", "maximum", "max", "not_exceed")):
        return f"must be no more than {value_text}"
    if any(token in text for token in (">=", "minimum", "min", "at_least")):
        return f"must be at least {value_text}"
    if ">" in text:
        return f"must be more than {value_text}"
    if "<" in text:
        return f"must be less than {value_text}"
    if any(token in text for token in ("allowed", "permitted")):
        return "is permitted" if not value_text else f"is permitted with value {value_text}"
    if "required" in text:
        return "is required" if not value_text else f"is required above {value_text}"
    if value_text:
        return f"has value {value_text}"
    return "is claimed"


def _field_comparison_rows(candidate: dict[str, Any], verified: dict[str, Any]) -> list[dict[str, Any]]:
    """Build a compact candidate-vs-verified field comparison table."""
    rows = []
    for field, label in [
        ("rule_object", "Rule object"),
        ("constraint_scope", "Scope"),
        ("applies_to", "Applies to"),
        ("operator", "Operator"),
        ("value", "Value"),
        ("unit", "Unit"),
        ("condition", "Condition"),
        ("exception", "Exception"),
    ]:
        candidate_value = _clean_value(candidate.get(field))
        verified_value = _clean_value(verified.get(field))
        rows.append(
            {
                "field": label,
                "review_candidate": candidate_value,
                "verified_rule": verified_value,
                "matches": "yes" if candidate_value == verified_value else "no",
            }
        )
    return rows


def _field_difference_html(rows: list[dict[str, Any]]) -> str:
    """Render field-by-field candidate vs verified differences as scannable cards."""
    cards = []
    for row in rows:
        matches = str(row.get("matches") or "").lower() == "yes"
        tone = "match" if matches else "diff"
        status = "Same" if matches else "Different"
        candidate_value = str(row.get("review_candidate") or "blank")
        verified_value = str(row.get("verified_rule") or "blank")
        cards.append(
            "<div class='diff-card {tone}'>"
            "<div class='diff-head'>"
            "<b>{field}</b><span>{status}</span>"
            "</div>"
            "<div class='diff-columns'>"
            "<div><small>Candidate</small><strong>{candidate}</strong></div>"
            "<div><small>Verified</small><strong>{verified}</strong></div>"
            "</div>"
            "</div>".format(
                tone=html.escape(tone),
                field=html.escape(str(row.get("field") or "")),
                status=html.escape(status),
                candidate=html.escape(candidate_value),
                verified=html.escape(verified_value),
            )
        )
    return "<div class='diff-grid'>" + "".join(cards) + "</div>"


def _field_difference_summary(rows: list[dict[str, Any]]) -> str:
    changed = [str(row.get("field")) for row in rows if str(row.get("matches") or "").lower() != "yes"]
    if not changed:
        return "All compared fields match the closest verified rule. If it is still in review, the blocker is likely evidence quality or policy."
    return "Differences found in: " + ", ".join(changed)


def _detail_sentence_panel(
    st: Any,
    title: str,
    sentences: list[str],
    evidence: dict[str, Any],
    rule_like: dict[str, Any],
) -> None:
    """Render human-readable detail plus bylaw lookup instructions."""
    st.markdown(f"### {title}")
    html_sentences = []
    for index, sentence in enumerate(sentences, start=1):
        html_sentences.append(
            "<div class='detail-sentence'>"
            f"<b>{index}.</b><span>{html.escape(sentence)}</span>"
            "</div>"
        )
    st.markdown("".join(html_sentences), unsafe_allow_html=True)
    _bylaw_lookup_panel(st, evidence, rule_like)


def _repair_detail_sentences(item: dict[str, Any], top_evidence: dict[str, Any]) -> list[str]:
    """Explain one evidence repair suggestion in plain English."""
    gaps = _list_text(item.get("support_gaps", []))
    repair_fields = _list_text(item.get("repairable_fields", []))
    match_reasons = _list_text(top_evidence.get("match_reasons", []))
    evidence_id = top_evidence.get("evidence_id") or "no suggested evidence"
    confidence = _display_value(item.get("best_repair_confidence"))
    return [
        f"Candidate claim: {_rule_sentence(item)}",
        f"The original evidence `{item.get('current_evidence_id')}` kept this rule in review because of: {gaps}.",
        f"The best suggested evidence is `{evidence_id}` with repair confidence {confidence}.",
        f"The repair mainly targets: {repair_fields}. Match reasons: {match_reasons}.",
        "This page suggests better evidence only; it does not itself promote the rule into verified output.",
    ]


def _intelligence_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one evidence intelligence item in plain English."""
    missing = _list_text(item.get("bundle_missing_fields", []))
    blocked = _list_text(item.get("blocked_by", []))
    safe = "safe to rerun through the deterministic verifier" if item.get("safe_retry") else "not safe to rerun automatically"
    return [
        f"Candidate claim: {_rule_sentence(item)}",
        f"The best evidence bundle has score {_display_value(item.get('bundle_score'))} and is {safe}.",
        f"The bundle currently supports: {_list_text(item.get('bundle_supported_fields', []))}. Missing fields: {missing}.",
        f"Blocked by: {blocked}.",
        f"Next action: `{item.get('next_action')}`. Bundle sentence: {item.get('bundle_sentence')}",
    ]


def _router_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one decision-tree route in plain English."""
    path = " -> ".join(_plain_label(part) for part in item.get("decision_path", [])) or "no path recorded"
    semantic_match = item.get("semantic_verified_rule_id") or "none"
    semantic_score = _display_value(item.get("semantic_score"))
    semantic_blockers = _list_text(item.get("semantic_guardrail_blockers", [])) or "none"
    return [
        f"Candidate claim: {item.get('candidate_sentence') or _rule_sentence(item)}",
        f"Original evidence says: {item.get('evidence_sentence') or 'no evidence sentence available'}",
        f"The review queue classifies this as {_plain_label(item.get('review_category'))} and suggests: {_plain_label(item.get('action_bucket'))}.",
        f"Meaning check: {_plain_label(item.get('semantic_review_class'))}. Closest verified match: `{semantic_match}` with score {semantic_score}; blockers: {semantic_blockers}.",
        f"Decision path: {path}.",
        f"Human instruction: {item.get('human_instruction')}",
        f"Evidence bundle summary: {item.get('bundle_sentence')}",
    ]


def _resolution_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one review-resolution label in plain English."""
    can_fix = (
        "has a plausible deterministic evidence-fix path"
        if item.get("can_promote_after_evidence_fix")
        else "does not currently have a safe deterministic promotion path"
    )
    semantic = item.get("semantic_verified_rule_id") or "none"
    score = _display_value(item.get("semantic_score"))
    return [
        f"Candidate claim: {item.get('candidate_sentence') or _rule_sentence(item)}",
        f"Original evidence says: {item.get('evidence_sentence') or 'no evidence sentence available'}",
        f"The final resolution is {_plain_label(item.get('resolution'))}, so the next step is {_plain_label(item.get('next_step_type'))}.",
        f"This item {can_fix}. Support gaps: {_list_text(item.get('support_gaps', []))}.",
        f"Closest meaning match: `{semantic}` with score {score}. Still missing: {_list_text(item.get('semantic_guardrail_blockers', []))}.",
        f"Bundle rerun decision: {_plain_label(item.get('bundle_rerun_decision'))} with gaps {_list_text(item.get('bundle_rerun_gaps', []))}.",
        f"Human next step: {item.get('human_next_step')}",
        f"Where to check in the bylaw: {item.get('where_to_find_it')}",
    ]


def _bundle_rerun_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one evidence-bundle rerun result in plain English."""
    decision = _plain_label(item.get("retry_decision") or "unknown")
    ready = "promotion-ready" if item.get("promotion_ready") else "not promotion-ready"
    return [
        f"Candidate claim: {_rule_sentence(item)}",
        f"The rerun used bundle `{item.get('bundle_evidence_id')}` built from: {_list_text(item.get('bundle_evidence_ids', []))}.",
        f"The deterministic verifier returned {decision} with gaps: {_list_text(item.get('retry_support_gaps', []))}.",
        f"The result is {ready}. Risk flags: {_list_text(item.get('promotion_risk_flags', []))}.",
        f"Recommendation: {item.get('promotion_recommendation') or 'keep in review until the verifier and benchmark support promotion'}.",
    ]


def _bundle_display_evidence(item: dict[str, Any]) -> dict[str, Any]:
    """Return one evidence-like object for the bylaw lookup panel."""
    bundle = item.get("best_evidence_bundle", [])
    first = bundle[0] if bundle else {}
    return {
        "page": first.get("page"),
        "evidence_quote": first.get("evidence_quote") or item.get("original_evidence_sentence"),
    }


def _bundle_rows(item: dict[str, Any]) -> list[dict[str, Any]]:
    """Return display rows for a best evidence bundle."""
    return [
        {
            "evidence_id": evidence.get("evidence_id"),
            "page": evidence.get("page"),
            "type": evidence.get("evidence_type"),
            "score": evidence.get("raw_score"),
            "confidence": evidence.get("bundle_confidence"),
            "supported_fields": ", ".join(evidence.get("supported_fields", [])),
            "reasons": ", ".join(evidence.get("match_reasons", [])),
            "quote": evidence.get("evidence_quote"),
        }
        for evidence in item.get("best_evidence_bundle", [])
    ]


def _rerun_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one shadow rerun result in plain English."""
    decision = _plain_label(item.get("retry_decision") or "unknown")
    gaps = _list_text(item.get("retry_support_gaps", [])) or "none"
    risk_flags = _list_text(item.get("promotion_risk_flags", [])) or "none"
    promotion = "promotion-ready" if item.get("promotion_ready") else "not promotion-ready"
    return [
        f"Candidate claim: {_rule_sentence(item)}",
        f"The rerun replaced original evidence `{item.get('original_evidence_id')}` with retry evidence `{item.get('retry_evidence_id')}`.",
        f"The deterministic verifier returned {decision} with support gaps: {gaps}.",
        f"The shadow result is {promotion}. Promotion risk flags: {risk_flags}.",
        f"Recommendation: {item.get('promotion_recommendation') or 'inspect before promotion'}.",
    ]


def _safe_tuning_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one verifier-tuning backlog item in plain English."""
    gaps = _list_text(item.get("support_gaps", []))
    tests = _list_text(item.get("required_tests", []))
    guardrails = _list_text(item.get("guardrails", []))
    rerun = _plain_label(item.get("rerun_decision") or "not rerun")
    rerun_ready = "promotion-ready" if item.get("rerun_promotion_ready") else "not promotion-ready"
    return [
        f"Candidate claim: {_rule_sentence(item)}",
        f"This is a {_plain_label(item.get('tuning_type'))} tuning candidate because the blocking gaps are: {gaps}.",
        f"Proposed experiment: {item.get('proposed_experiment')}",
        f"Evidence rerun status: {rerun}, {rerun_ready}.",
        f"Required validation: {tests}.",
        f"Guardrails that must remain true: {guardrails}.",
    ]


def _bylaw_lookup_panel(st: Any, evidence: dict[str, Any], rule_like: dict[str, Any]) -> None:
    """Tell a reviewer how to find and verify the rule in the source bylaw."""
    page = evidence.get("page") or rule_like.get("page")
    quote = _quote_from_evidence(evidence)
    search_phrase = _search_phrase(rule_like, quote)

    st.markdown("#### How to find this in the bylaw")
    page_text = f"page `{page}`" if page not in (None, "") else "the cited section/page from the evidence packet"
    st.markdown(
        f"""
1. Open the [{_ACTIVE_SOURCE['label']}]({_ACTIVE_SOURCE['url']}).
2. Go to {page_text}. If the PDF page number is offset, use text search instead.
3. Search for the phrase below, then compare the candidate's value, unit, operator, scope, and condition against the bylaw wording.
4. If the passage contains words like `except`, `subject to`, `notwithstanding`, `unless`, or a covenant condition, keep the rule in human review unless the condition is explicitly modeled.
"""
    )
    st.code(search_phrase or "Search by rule object, value, unit, and applies_to fields.", language="text")
    if quote:
        st.markdown("#### Evidence quote")
        st.code(_short_display_quote(quote), language="text")


def _quote_from_evidence(evidence: dict[str, Any]) -> str:
    """Return the most useful evidence text available for reviewers."""
    return str(
        evidence.get("evidence_quote")
        or evidence.get("evidence_text")
        or evidence.get("source_context")
        or ""
    ).strip()


def _search_phrase(rule_like: dict[str, Any], quote: str) -> str:
    """Choose a short search phrase for the PDF find box."""
    if quote:
        cleaned = " ".join(quote.split())
        words = cleaned.split()
        return " ".join(words[:16])
    parts = [
        rule_like.get("rule_object"),
        rule_like.get("applies_to"),
        rule_like.get("value"),
        rule_like.get("unit"),
    ]
    return " ".join(str(part) for part in parts if part not in (None, ""))


def _short_display_quote(value: str, limit: int = 420) -> str:
    """Keep bylaw evidence quotes readable inside Streamlit."""
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _evidence_by_id(evidence_units: list[dict[str, Any]], evidence_id: Any) -> dict[str, Any]:
    """Find an evidence packet by id for bylaw lookup instructions."""
    return next((item for item in evidence_units if item.get("evidence_id") == evidence_id), {})


def _list_text(values: Any) -> str:
    """Format lists without exposing raw JSON syntax in summary sentences."""
    if not values:
        return "none"
    if isinstance(values, str):
        return _plain_label(values)
    return ", ".join(_plain_label(value) for value in values)


def _bar_table(st: Any, counts: dict[str, Any]) -> None:
    rows = [{"name": key, "count": value} for key, value in counts.items()]
    _bar_rows(st, rows, "name", "count")


def _bar_rows(st: Any, rows: list[dict[str, Any]], label_key: str, value_key: str) -> None:
    if not rows:
        st.caption("No data.")
        return
    max_value = max(float(row.get(value_key) or 0) for row in rows) or 1.0
    html_rows = []
    for row in rows:
        raw_label = str(row.get(label_key) or "")
        label = html.escape(_plain_label(raw_label))
        help_text = HELP_TEXT.get(raw_label, "")
        value = float(row.get(value_key) or 0)
        width = int((value / max_value) * 100)
        html_rows.append(
            "<div class='bar-row'>"
            f"<span title='{html.escape(help_text)}'>{label}</span>"
            f"<div class='bar-track'><div class='bar-fill' style='width:{width}%'></div></div>"
            f"<b>{int(value)}</b></div>"
        )
    st.markdown("\n".join(html_rows), unsafe_allow_html=True)


def _style(st: Any) -> None:
    # Design system — "Civic Primer". Three blocks: tokens, chrome, components.
    # STRICT status color semantics (verified green, review amber, rejected
    # red, not_used grey) are reused by every status-coded element below and
    # pinned by tests. De-boxing rule: at most ONE border level visible at a
    # time — cards inside expanders render flat, hairlines instead of frames.
    # Presentation only.
    st.markdown(
        """
<style>
/* ---- tokens ---- */
:root {
  --status-verified: #1a7f37;
  --status-review: #9a6700;
  --status-rejected: #cf222e;
  --status-not-used: #57606a;
  --ink: #1f2328;
  --ink-soft: #57606a;
  --accent: #0969da;
  --accent-strong: #0550ae;
  --lane-p9: #8250df;
  --canvas: #ffffff;
  --subtle: #f6f8fa;
  --line: #d0d7de;
  --hairline: #eaeef2;
}
/* ---- chrome ---- */
#MainMenu, footer, div[data-testid="stDecoration"] {display:none;}
header[data-testid="stHeader"] {background:transparent;}
html, body, [class*="css"] {font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;}
.block-container {padding: 1.25rem 2rem 3rem; max-width: 1280px;}
h1 {font-size:28px;} h2 {font-size:22px;} h3 {font-size:18px;}
h4 {font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:var(--ink-soft); font-weight:700;}
/* ---- components ---- */
.app-header {display:flex; justify-content:space-between; align-items:flex-start; gap:16px; border:0; border-bottom:1px solid var(--hairline); border-radius:0; padding:6px 0 14px; background:transparent; margin-bottom:18px;}
.app-header h1 {font-size:28px; line-height:1.15; margin:2px 0 6px; color:var(--ink); letter-spacing:-.01em;}
.app-header p {margin:0; color:var(--ink-soft); font-size:14px;}
.eyebrow {font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--accent); font-weight:700;}
.status-legend {display:flex; gap:6px; flex-wrap:wrap; justify-content:flex-end;}
.status-pill {font-size:11px; font-weight:700; padding:3px 9px; border-radius:999px; color:#fff; letter-spacing:.02em;}
.status-pill.status-verified, .status-verified-bg {background:var(--status-verified);}
.status-pill.status-review, .status-review-bg {background:var(--status-review);}
.status-pill.status-rejected, .status-rejected-bg {background:var(--status-rejected);}
.status-pill.status-not_used, .status-not_used-bg {background:var(--status-not-used);}
.lane-pill {font-size:11px; font-weight:700; padding:2px 8px; border-radius:999px; color:#fff;}
.lane-pill-p5 {background:var(--accent);}
.lane-pill-p9 {background:var(--lane-p9);}
.gate-pill {font-size:11px; font-weight:700; padding:2px 9px; border-radius:999px; color:#fff;}
.gate-pill-pass {background:var(--status-verified);}
.gate-pill-fail-closed {background:#475569;}
.gate-pill-scope {background:var(--status-review);}
.gate-pill-unsafe {background:var(--status-rejected);}
.gate-pill-review {background:var(--status-not-used);}
.metric-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(118px,1fr)); gap:10px; margin:12px 0 20px;}
.metric {border:1px solid var(--line); border-radius:8px; padding:13px 14px; background:var(--canvas); min-height:86px;}
.metric-verified {border-top:4px solid var(--status-verified);}
.metric-review {border-top:4px solid var(--status-review);}
.metric-rejected {border-top:4px solid var(--status-rejected);}
.metric-not_used {border-top:4px solid var(--status-not-used);}
.metric-label {font-size:10px; line-height:1.25; color:var(--ink-soft); text-transform:uppercase; font-weight:700; overflow-wrap:normal;}
.metric-value {font-size:28px; font-weight:700; color:var(--ink); font-variant-numeric: tabular-nums;}
.hero-grid {display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:10px; margin:8px 0 12px;}
.hero-card {border:1px solid var(--line); border-radius:8px; padding:13px 14px; background:var(--canvas); min-height:108px;}
.hero-card-verified {border-top:4px solid var(--status-verified);}
.hero-card-review {border-top:4px solid var(--status-review);}
.hero-card-rejected {border-top:4px solid var(--status-rejected);}
.hero-card-not_used {border-top:4px solid var(--status-not-used);}
.hero-label {font-size:10px; line-height:1.25; color:var(--ink-soft); text-transform:uppercase; font-weight:700;}
.hero-value {font-size:25px; line-height:1.15; margin-top:8px; color:var(--ink); font-weight:750; font-variant-numeric:tabular-nums;}
.hero-note {font-size:12px; line-height:1.35; margin-top:7px; color:var(--ink-soft);}
.instruction-banner {border-left:4px solid var(--accent); background:var(--subtle); border-radius:0 8px 8px 0; color:var(--ink); padding:11px 14px; margin:10px 0 14px; font-size:14px;}
.timeline {display:grid; grid-template-columns:1fr 28px 1fr 28px 1fr 28px 1fr; align-items:stretch; gap:6px; margin:12px 0 16px;}
.timeline-compact {grid-template-columns:1fr 28px 1fr; max-width:760px;}
.timeline-step {border:1px solid var(--hairline); border-radius:8px; background:var(--canvas); padding:11px 12px; min-height:72px;}
.timeline-step b {display:block; color:var(--ink); font-size:13px;}
.timeline-step span {display:block; color:var(--ink-soft); margin-top:4px; font-size:12px;}
.timeline-active {border-color:var(--status-verified); border-top:4px solid var(--status-verified);}
.timeline-arrow {display:flex; align-items:center; justify-content:center; color:var(--ink-soft); font-weight:700;}
.legend-grid {display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:8px; margin:12px 0 18px;}
.legend-grid div {border:1px solid var(--hairline); border-radius:8px; padding:10px 11px; background:var(--canvas);}
.legend-grid b {display:block; font-size:13px; color:var(--ink);}
.legend-grid span {display:block; margin-top:3px; color:var(--ink-soft); font-size:12px; line-height:1.35;}
.roadmap-grid {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:10px 0 12px;}
.roadmap-card {border:1px solid var(--hairline); border-radius:8px; background:var(--canvas); padding:13px 14px; min-height:104px;}
.roadmap-card b {display:block; color:var(--ink); margin-bottom:5px;}
.roadmap-card span {display:block; color:var(--ink-soft); font-size:14px; line-height:1.4;}
.trust-note {border:1px solid var(--hairline); border-radius:8px; background:var(--subtle); padding:11px 13px; color:var(--ink-soft); font-size:14px; margin:8px 0 12px;}
.guidance-grid, .action-grid {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:12px 0 20px;}
.guide-card, .action-card {border:0; border-radius:8px; background:var(--subtle); padding:14px 15px;}
.guide-card b {display:block; color:var(--ink); margin-bottom:5px;}
.guide-card span, .action-card p {color:var(--ink-soft); font-size:14px; margin:0;}
.action-value {font-size:28px; font-weight:700; color:var(--status-verified); font-variant-numeric: tabular-nums;}
.action-title {font-weight:700; color:var(--ink); margin:1px 0 4px;}
.sentence-card {border:1px solid var(--hairline); border-radius:8px; padding:15px 16px; min-height:142px; background:var(--canvas);}
.sentence-card p {font-size:17px; line-height:1.45; color:var(--ink); margin:8px 0 10px;}
.sentence-card span {font-size:12px; color:var(--ink-soft);}
.sentence-title {font-size:12px; text-transform:uppercase; letter-spacing:.06em; font-weight:700;}
.sentence-review {border-top:4px solid var(--status-review);}
.sentence-verified {border-top:4px solid var(--status-verified);}
.sentence-neutral {border-top:4px solid var(--status-not-used);}
.bylaw-section {border:0; border-left:3px solid var(--line); border-radius:0 8px 8px 0; background:var(--subtle); padding:12px 14px; margin:8px 0; line-height:1.6; color:var(--ink); white-space:pre-wrap; font-family: ui-monospace, "SF Mono", "Roboto Mono", monospace; font-size:13px;}
.bylaw-section h4 {margin:0 0 8px; color:var(--ink); letter-spacing:0; text-transform:none; font-size:14px;}
mark.evidence-hit {background:#fff3bf; border-bottom:2px solid var(--status-review); padding:1px 2px; border-radius:2px;}
.detail-sentence {display:grid; grid-template-columns:28px 1fr; gap:8px; border:0; border-radius:8px; background:var(--subtle); padding:11px 13px; margin:7px 0;}
.detail-sentence b {color:var(--accent);}
.detail-sentence span {color:var(--ink); line-height:1.45;}
.bar-row {display:grid; grid-template-columns:minmax(160px,240px) 1fr 52px; gap:12px; align-items:center; margin:7px 0;}
.bar-row span {color:var(--ink); font-size:14px;}
.bar-row b {color:var(--ink); text-align:right; font-variant-numeric: tabular-nums;}
.bar-track {height:12px; background:var(--subtle); border-radius:999px; overflow:hidden; border:1px solid var(--hairline);}
.bar-fill {height:100%; background:linear-gradient(90deg,var(--accent),var(--accent-strong));}
.matrix-table {width:100%; border-collapse:separate; border-spacing:0; font-size:13px;}
.matrix-table th {text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--ink-soft); padding:8px 10px; border-bottom:2px solid var(--line); background:var(--subtle); position:sticky; top:0;}
.matrix-table td {padding:8px 10px; border-bottom:1px solid var(--hairline); vertical-align:top; line-height:1.4;}
.matrix-table td.row-label {font-weight:600; color:var(--ink); white-space:nowrap;}
.matrix-cell {border-radius:6px; padding:6px 8px; display:block;}
.matrix-cell.status-verified {background:color-mix(in srgb, var(--status-verified) 12%, white); border-left:3px solid var(--status-verified);}
.matrix-cell.status-review {background:color-mix(in srgb, var(--status-review) 12%, white); border-left:3px solid var(--status-review);}
.matrix-cell.status-missing {background:color-mix(in srgb, var(--status-rejected) 8%, white); border-left:3px dashed var(--status-rejected); color:var(--ink-soft);}
.matrix-cell.status-na {color:#b6bec7;}
div[data-testid="stDataFrame"] {border:1px solid var(--hairline); border-radius:8px; overflow:hidden;}
div[data-testid="stExpander"] {border:1px solid var(--hairline); border-radius:8px;}
div[data-testid="stExpander"] .guide-card, div[data-testid="stExpander"] .action-card {background:transparent; padding:8px 0;}
/* ---- redesign: civic console (Summary hero, status bar, safety chip, chat) ---- */
.safety-chip {display:inline-flex; align-items:center; gap:6px; font-size:12px; font-weight:700; padding:4px 11px; border-radius:999px; white-space:nowrap;}
.safety-ok {background:color-mix(in srgb, var(--status-verified) 12%, white); color:var(--status-verified);}
.safety-alert {background:color-mix(in srgb, var(--status-rejected) 12%, white); color:var(--status-rejected);}
.coverage-hero {display:grid; gap:12px; padding:22px 24px; border:1px solid var(--hairline); border-radius:12px; background:var(--canvas); box-shadow:0 1px 2px rgba(31,35,40,.05); margin:6px 0 18px;}
.coverage-hero .pct {font-size:46px; font-weight:750; color:var(--status-verified); line-height:1; font-variant-numeric:tabular-nums;}
.coverage-hero .cap {font-size:13px; color:var(--ink-soft);}
.coverage-bar {height:14px; border-radius:999px; overflow:hidden; display:flex; border:1px solid var(--hairline);}
.coverage-bar .seg {height:100%;}
.coverage-bar .seg-verified {background:var(--status-verified);}
.coverage-bar .seg-review {background:var(--status-review);}
.coverage-bar .seg-missed {background:var(--status-not-used);}
.coverage-key {display:flex; gap:16px; flex-wrap:wrap; font-size:12px; color:var(--ink-soft);}
.coverage-key b {color:var(--ink); font-variant-numeric:tabular-nums;}
.coverage-key i {font-style:normal; display:inline-block; width:10px; height:10px; border-radius:3px; margin-right:5px; vertical-align:middle;}
.status-bar {display:flex; height:34px; border-radius:8px; overflow:hidden; border:1px solid var(--hairline); margin:6px 0 18px;}
.status-bar .seg {display:flex; align-items:center; justify-content:center; color:#fff; font-size:12px; font-weight:700; min-width:0; white-space:nowrap; overflow:hidden;}
.status-bar .seg.verified {background:var(--status-verified);}
.status-bar .seg.review {background:var(--status-review);}
.status-bar .seg.rejected {background:var(--status-rejected);}
.status-bar .seg.not_used {background:var(--status-not-used);}
/* chat — scoped so it never bleeds into other tabs */
.chat-shell {max-width:780px; margin:0 auto;}
.chat-ribbon {font-size:12px; color:var(--ink-soft); background:var(--subtle); border:1px solid var(--hairline); border-radius:999px; padding:7px 14px; display:inline-flex; gap:8px; align-items:center; margin-bottom:6px;}
.chat-ribbon::before {content:'●'; color:var(--accent); font-size:9px;}
.mode-pill {font-size:11px; font-weight:700; padding:3px 9px; border-radius:999px; background:var(--subtle); color:var(--ink-soft);}
.mode-pill.live {background:color-mix(in srgb, var(--status-verified) 12%, white); color:var(--status-verified);}
.chat-empty {text-align:center; color:var(--ink-soft); padding:40px 0 14px;}
.chat-empty h2 {color:var(--ink); font-size:24px; margin:8px 0 6px; letter-spacing:-.01em;}
.chat-empty p {max-width:520px; margin:0 auto; font-size:14px; line-height:1.5;}
.citation {border:0; border-left:3px solid var(--accent); background:var(--subtle); border-radius:0 8px 8px 0; padding:10px 12px; margin:6px 0; font-size:13px; line-height:1.5; color:var(--ink);}
.citation .loc {font-family:ui-monospace,"SF Mono","Roboto Mono",monospace; font-size:11px; color:var(--ink-soft); white-space:nowrap; font-weight:700;}
[data-testid="stChatMessage"] {border:0; box-shadow:none; background:transparent; padding:6px 0;}
[data-testid="stChatInput"] textarea {border-radius:18px;}
/* ---- redesign v2: left-rail nav + numbered rule sentences + red gaps ---- */
.metric, .sentence-card, .coverage-hero, .rule-card {box-shadow:0 1px 2px rgba(31,35,40,.04);}
/* sidebar radio -> nav rail */
section[data-testid="stSidebar"] div[role="radiogroup"] {gap:2px;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
  display:flex; align-items:center; width:100%; padding:9px 12px; margin:0; border-radius:9px;
  font-size:14px; font-weight:600; color:var(--ink-soft); cursor:pointer; transition:background .12s;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {background:var(--subtle); color:var(--ink);}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
  background:color-mix(in srgb, var(--accent) 12%, white); color:var(--accent-strong);
  box-shadow:inset 3px 0 0 var(--accent);}
section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {display:none;} /* hide radio dot */
.nav-title {font-size:11px; text-transform:uppercase; letter-spacing:.09em; color:#8c959f; font-weight:700; margin:6px 0 4px;}
/* breadcrumb header */
.crumb {font-size:12.5px; color:var(--ink-soft); margin-bottom:2px;}
.crumb b {color:var(--accent); font-weight:700;}
/* numbered rule sentence cards */
.rule-card {display:grid; grid-template-columns:32px 1fr; gap:12px; align-items:start;
  border:1px solid var(--hairline); border-radius:12px; padding:13px 16px; margin:8px 0; background:var(--canvas);}
.rule-num {display:flex; align-items:center; justify-content:center; width:28px; height:28px; border-radius:8px;
  background:var(--subtle); color:var(--ink-soft); font-weight:700; font-size:13px; font-variant-numeric:tabular-nums;}
.rule-body {min-width:0;}
.rule-text {font-size:16px; line-height:1.5; color:var(--ink);}
.gap-flag {background:color-mix(in srgb, var(--status-rejected) 14%, white); color:var(--status-rejected);
  font-weight:700; padding:1px 5px; border-radius:5px; border-bottom:2px solid var(--status-rejected);}
.gap-why {margin-top:7px; font-size:13px; color:var(--status-rejected); line-height:1.4;}
.section-head {font-size:20px; font-weight:750; color:var(--ink); letter-spacing:-.01em; margin:2px 0 2px;}
.section-sub {color:var(--ink-soft); font-size:14px; margin:0 0 14px;}
.cite-chip {display:inline-block; font-size:12px; font-weight:700; color:var(--accent-strong);
  background:color-mix(in srgb, var(--accent) 10%, white); border-radius:999px; padding:2px 9px; margin:2px 4px 2px 0;
  font-family:ui-monospace,"SF Mono","Roboto Mono",monospace;}
.group-summary {margin:12px 0 16px;}
.group-summary-title {font-size:12px; text-transform:uppercase; letter-spacing:.08em; color:#66727f; font-weight:800; margin-bottom:8px;}
.group-summary-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px;}
.group-chip-card {background:#fff; border:1px solid #e3e7ea; border-radius:12px; padding:12px 13px; box-shadow:0 8px 18px rgba(15,23,42,.035);}
.group-chip-card b {display:block; color:#101822; font-size:13px; line-height:1.25; margin-bottom:5px;}
.group-chip-card span {display:block; color:#66727f; font-size:12px;}
.group-chip-card.muted {background:#f6f8f7;}
/* ---- presentation overview refresh ---- */
.stApp {background:#f7f8f6;}
section[data-testid="stSidebar"] {background:linear-gradient(180deg,#071016 0%,#0d1a22 62%,#12252c 100%);}
section[data-testid="stSidebar"] * {color:#eaf2ee;}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stCaptionContainer,
section[data-testid="stSidebar"] p {color:#c6d1cf !important;}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {background:rgba(255,255,255,.06); border-color:rgba(255,255,255,.15);}
section[data-testid="stSidebar"] .nav-title {color:#9fb0ad;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {color:#dbe7e3; border-radius:10px; padding:10px 12px;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {background:rgba(255,255,255,.08); color:#fff;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
  background:linear-gradient(90deg,#176c43,#0f5134); color:#fff; box-shadow:none;
}
section[data-testid="stSidebar"] div[data-testid="stExpander"] {border-color:rgba(255,255,255,.12); background:rgba(255,255,255,.04);}
section[data-testid="stSidebar"] .trust-note {background:rgba(255,255,255,.06); border-color:rgba(255,255,255,.12); color:#d7e7df;}
section[data-testid="stSidebar"] .trust-note a {color:#b6f3c6 !important;}
.sidebar-brand {display:grid; grid-template-columns:42px 1fr; gap:12px; align-items:center; margin:4px 0 24px;}
.brand-mark {width:38px; height:38px; border-radius:12px; background:#123325; border:1px solid #52b788; display:flex; align-items:center; justify-content:center; color:#9cf2b7; font-weight:900;}
.brand-title {font-size:16px; font-weight:780; line-height:1.18; color:#fff;}
.sidebar-run {border:1px solid rgba(255,255,255,.12); border-radius:12px; padding:12px 13px; background:rgba(255,255,255,.055); margin:10px 0 18px;}
.sidebar-run b {display:block; font-size:13px; color:#fff; margin-bottom:4px; line-height:1.25;}
.sidebar-run span {display:block; font-size:12px; color:#cfe0dc; margin-bottom:7px;}
.sidebar-run a {font-size:12px; color:#b6f3c6 !important; text-decoration:none; font-weight:700;}
.pipeline-note {border:1px solid rgba(82,183,136,.28); border-radius:12px; padding:12px 13px; background:rgba(28,87,61,.26); margin-top:16px;}
.pipeline-note b {display:block; font-size:12px; color:#b6f3c6; margin-bottom:5px;}
.pipeline-note span {display:block; font-size:12px; line-height:1.45; color:#d7e7df;}
.sidebar-status {border:1px solid rgba(255,255,255,.12); border-radius:12px; padding:14px; background:rgba(28,87,61,.28); margin-top:20px;}
.sidebar-status b {display:block; font-size:13px; color:#b6f3c6; margin-bottom:5px;}
.sidebar-status span {font-size:12px; color:#d7e7df;}
.overview-titlebar {display:flex; align-items:flex-start; justify-content:space-between; gap:22px; margin:0 0 10px;}
.overview-titlebar h1 {font-size:29px; line-height:1.14; letter-spacing:0; margin:0 0 5px; color:#101822;}
.overview-titlebar p {font-size:15px; line-height:1.45; color:#5f6b76; margin:0; max-width:760px;}
.overview-actions {display:flex; gap:10px; align-items:center; color:#5f6b76; font-size:12px; white-space:nowrap;}
.live-dot {display:inline-block; width:8px; height:8px; border-radius:999px; background:#16884a; margin-left:6px;}
.selection-summary {display:flex; align-items:center; justify-content:space-between; gap:18px; background:#ffffff; border:1px solid #e3e7ea; border-radius:14px; padding:12px 16px; margin:0 0 8px; box-shadow:0 8px 20px rgba(15,23,42,.035);}
.selection-summary b {display:block; color:#101822; font-size:14px; margin-bottom:3px;}
.selection-summary span {display:block; color:#64727d; font-size:13px; line-height:1.35;}
.selection-summary a {color:#176c43; font-weight:760; text-decoration:none; font-size:13px; white-space:nowrap;}
.overview-band-title {font-size:16px; font-weight:820; color:#101822; margin:20px 0 3px; letter-spacing:0;}
.overview-band-copy {font-size:14px; line-height:1.42; color:#66727f; margin:0 0 9px; max-width:820px;}
.filter-card, .console-card {background:#fff; border:1px solid #e3e7ea; border-radius:14px; box-shadow:0 10px 26px rgba(15,23,42,.045);}
.filter-card {padding:14px 16px 4px; margin-bottom:12px;}
.console-card {padding:22px; margin-bottom:18px;}
.console-card h3 {font-size:17px; color:#111827; margin:0 0 14px; letter-spacing:0;}
.kpi-grid {display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:16px; margin:16px 0 24px;}
.kpi-card {background:#fff; border:1px solid #e6eaee; border-radius:14px; padding:18px 19px; min-height:132px; box-shadow:0 10px 22px rgba(15,23,42,.05);}
.kpi-top {display:flex; gap:13px; align-items:flex-start;}
.kpi-icon {width:46px; height:46px; border-radius:14px; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:900; font-size:22px;}
.kpi-green {background:#1f9d55;} .kpi-amber {background:#e4a50b;} .kpi-red {background:#df3036;} .kpi-blue {background:#2f659b;}
.kpi-label {font-size:13px; color:#374151; font-weight:720;}
.kpi-value {font-size:31px; line-height:1.05; font-weight:820; color:#0f172a; margin-top:5px; font-variant-numeric:tabular-nums;}
.kpi-delta {font-size:12px; margin-top:6px; font-weight:720;}
.kpi-delta.good {color:#16884a;} .kpi-delta.warn {color:#b77900;} .kpi-delta.bad {color:#cf222e;} .kpi-delta.info {color:#2f659b;}
.kpi-note {font-size:12px; line-height:1.4; color:#6b7280; margin-top:14px;}
.decision-flow {background:#fff; border:1px solid #e3e7ea; border-radius:16px; padding:15px 16px; margin:8px 0 14px; box-shadow:0 12px 28px rgba(15,23,42,.045);}
.decision-flow-head {display:flex; justify-content:space-between; align-items:flex-start; gap:20px; margin-bottom:8px;}
.decision-flow-head h3 {font-size:17px; margin:0; color:#101822; letter-spacing:0;}
.decision-flow-head p {font-size:14px; margin:0; color:#66727f; line-height:1.45;}
.decision-flow-main {display:grid; grid-template-columns:180px minmax(0,1fr); gap:14px; align-items:stretch;}
.decision-total {min-width:0; border:1px solid #d7e2ea; border-radius:14px; padding:12px 14px; background:#f6f9fb; text-align:left; display:flex; flex-direction:column; justify-content:center;}
.decision-total span {display:block; font-size:12px; color:#44515f; font-weight:760; text-transform:uppercase; letter-spacing:.05em;}
.decision-total b {display:block; font-size:34px; line-height:1; color:#0f172a; margin-top:6px; font-variant-numeric:tabular-nums;}
.decision-strip {display:flex; height:12px; overflow:hidden; border-radius:999px; border:1px solid #dfe6e3; background:#eef2f0; margin-bottom:8px;}
.decision-strip .seg {display:block; height:100%;}
.decision-strip .verified {background:#1f9d55;}
.decision-strip .review {background:#e4a50b;}
.decision-strip .rejected {background:#df3036;}
.decision-branches {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px;}
.decision-branch {border:1px solid #e5e9e6; border-radius:13px; padding:10px 12px; background:#fbfcfb; min-height:78px;}
.decision-branch span {display:block; font-size:12px; color:#24313b; font-weight:790; text-transform:uppercase; letter-spacing:.05em;}
.decision-branch b {display:block; font-size:27px; line-height:1; margin:5px 0 5px; font-variant-numeric:tabular-nums; color:#111827;}
.decision-branch small {display:block; color:#66727f; font-size:12px; line-height:1.4;}
.decision-branch.verified {border-color:#b7dfc4; background:#f1fbf4;}
.decision-branch.verified b {color:#166534;}
.decision-branch.review {border-color:#f3dcad; background:#fff9ed;}
.decision-branch.review b {color:#a16207;}
.decision-branch.rejected {border-color:#f4b5b9; background:#fff5f5;}
.decision-branch.rejected b {color:#c4212a;}
.decision-note {display:flex; justify-content:space-between; gap:18px; align-items:center; margin-top:8px; font-size:12px; color:#66727f; line-height:1.4;}
.decision-note b {color:#176c43; white-space:nowrap;}
.overview-safety-strip {display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:6px 0 16px;}
.overview-safety-strip div {border:1px solid #dfe8e2; background:#f5fbf6; border-radius:12px; padding:11px 12px;}
.overview-safety-strip span {display:block; color:#66727f; font-size:11px; font-weight:790; text-transform:uppercase; letter-spacing:.05em;}
.overview-safety-strip b {display:block; color:#14532d; font-size:20px; line-height:1; margin-top:6px; font-variant-numeric:tabular-nums;}
.next-step-grid {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:6px 0 12px;}
.next-step-card {border:1px solid #e3e7ea; border-radius:13px; background:#fff; padding:14px 15px; box-shadow:0 8px 20px rgba(15,23,42,.035);}
.next-step-card b {display:block; color:#101822; font-size:14px; margin-bottom:7px;}
.next-step-card span {display:block; color:#66727f; font-size:13px; line-height:1.45;}
.overview-grid {display:grid; grid-template-columns:minmax(0,1fr) 360px; gap:18px; align-items:start;}
.overview-left-grid {display:grid; grid-template-columns:minmax(0,1.08fr) minmax(0,.92fr); gap:14px;}
.table-lite {width:100%; border-collapse:collapse; font-size:13px;}
.table-lite th {text-align:left; color:#5d6672; font-size:11px; text-transform:uppercase; letter-spacing:.04em; padding:10px 10px; border-bottom:1px solid #e7eaee;}
.table-lite td {padding:14px 10px; border-bottom:1px solid #eef1f3; color:#17202a; vertical-align:top;}
.issue-pill {display:inline-block; border-radius:999px; padding:4px 9px; font-size:11px; font-weight:760;}
.issue-red {background:#fff0f0; color:#c4212a;} .issue-amber {background:#fff6df; color:#a16207;} .issue-blue {background:#edf4ff; color:#1d4ed8;} .issue-purple {background:#f4efff; color:#6d28d9;} .issue-green {background:#eefaf0; color:#166534;}
.pager {display:flex; gap:16px; justify-content:flex-end; color:#6b7280; font-size:12px; margin-top:9px;}
.trust-status-head {display:flex; align-items:flex-start; justify-content:space-between; gap:16px; margin-bottom:14px;}
.trust-title {font-size:17px; line-height:1.2; font-weight:820; color:#111827; letter-spacing:0;}
.trust-status-head span {display:block; color:#66727f; font-size:13px; margin-top:4px;}
.trust-status-head b {display:inline-flex; align-items:center; justify-content:center; min-width:96px; border-radius:999px; padding:7px 12px; background:#eefaf1; color:#166534; font-size:12px; white-space:nowrap;}
.trust-hero {display:grid; grid-template-columns:116px 1fr; gap:14px; align-items:center; border:1px solid #b7dfc4; background:linear-gradient(135deg,#eefaf1,#fbfffc); border-radius:14px; padding:14px 16px; margin-bottom:12px;}
.trust-hero span {display:block; color:#166534; font-size:12px; font-weight:780; text-transform:uppercase; letter-spacing:.05em;}
.trust-hero strong {display:block; color:#14532d; font-size:36px; line-height:1; font-variant-numeric:tabular-nums; margin-top:5px;}
.trust-hero p {margin:0; color:#355342; font-size:14px; line-height:1.45;}
.trust-mini-grid {display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:9px;}
.trust-mini {border:1px solid #e5e9e6; border-radius:11px; padding:10px 12px; background:#fbfcfb; min-height:82px;}
.trust-mini span {display:block; font-size:12px; color:#24313b; font-weight:760;}
.trust-mini b {display:block; font-size:24px; line-height:1; margin:8px 0 4px; color:#111827; font-variant-numeric:tabular-nums;}
.trust-mini small {display:block; font-size:11px; color:#66727f;}
.trust-mini.ok {border-color:#c7e8d0; background:#f2fbf4;}
.trust-mini.ok b {color:#166534;}
.trust-mini.warn {border-color:#f3dcad; background:#fff9ed;}
.trust-mini.warn b {color:#a16207;}
.trust-mini.bad {border-color:#f4b5b9; background:#fff5f5;}
.trust-mini.bad b {color:#c4212a;}
.trust-row {display:grid; grid-template-columns:minmax(0,1fr) 58px minmax(128px,.7fr); gap:12px; align-items:center; border:1px solid #e5e9e6; border-radius:11px; padding:12px 14px; margin:9px 0; background:#fbfcfb;}
.trust-row span {font-size:13px; color:#24313b; font-weight:720;}
.trust-row b {font-size:20px; text-align:right; color:#111827; font-variant-numeric:tabular-nums;}
.trust-row small {font-size:12px; color:#66727f;}
.trust-row.ok {border-color:#c7e8d0; background:#f2fbf4;}
.trust-row.ok b {color:#166534;}
.trust-row.warn {border-color:#f3dcad; background:#fff9ed;}
.trust-row.warn b {color:#a16207;}
.trust-row.bad {border-color:#f4b5b9; background:#fff5f5;}
.trust-row.bad b {color:#c4212a;}
.legend-swatch {display:inline-block; width:12px; height:12px; border-radius:3px; margin-right:7px; vertical-align:-1px;}
.right-rail .console-card {margin-bottom:14px;}
.ask-card-centered {max-width:900px; margin-left:auto; margin-right:auto;}
.ask-intro {background:#eaf3ec; color:#184531; border:1px solid #d4e6d8; border-radius:10px; padding:13px; font-size:13px; line-height:1.5; margin-bottom:14px;}
.prompt-row-label {font-size:11px; text-transform:uppercase; letter-spacing:.08em; color:#66727f; font-weight:820; margin:8px 0 6px;}
.chat-bubble {border-radius:12px; padding:13px 14px; font-size:13px; line-height:1.5; margin:10px 0;}
.chat-user {background:linear-gradient(135deg,#16884a,#0f7040); color:#fff; margin-left:18px;}
.chat-assistant {background:#f8faf8; border:1px solid #e3e7e4; color:#17202a; margin-right:18px;}
.source-cite {border:1px solid #e6eaee; background:#fbfcfb; border-radius:9px; padding:10px 11px; font-size:12px; color:#374151; margin:8px 0;}
.prompt-chip {display:block; width:100%; border:1px solid #e6eaee; background:#fbfcfb; color:#4b5563; border-radius:9px; padding:10px 12px; margin:8px 0; font-size:12px; text-align:left;}
.review-focus-grid {display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin:12px 0 18px;}
.review-focus-card {border:1px solid #e4e8e6; border-radius:12px; background:#fbfcfb; padding:13px 14px; min-height:116px;}
.review-focus-card span {display:block; font-size:11px; color:#66727f; font-weight:820; text-transform:uppercase; letter-spacing:.05em; margin-bottom:7px;}
.review-focus-card b {display:block; color:#111827; font-size:15px; line-height:1.32; margin-bottom:7px; overflow-wrap:anywhere;}
.review-focus-card small {display:block; color:#66727f; font-size:12px; line-height:1.35;}
.review-focus-card.ok {border-color:#c7e8d0; background:#f2fbf4;}
.review-focus-card.ok b {color:#166534;}
.review-focus-card.warn, .review-focus-card.action {border-color:#f3dcad; background:#fff9ed;}
.review-focus-card.warn b, .review-focus-card.action b {color:#8a5800;}
.review-focus-card.bad {border-color:#f4b5b9; background:#fff5f5;}
.review-focus-card.bad b {color:#c4212a;}
.review-focus-card.neutral {background:#f6f8f7;}
.diff-summary {border:1px solid #e3e7ea; background:#fbfcfb; border-radius:10px; padding:10px 12px; color:#374151; font-size:13px; margin:6px 0 10px;}
.diff-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:10px; margin:8px 0 14px;}
.diff-card {border:1px solid #e5e9e6; border-radius:12px; padding:12px 13px; background:#fbfcfb; min-height:118px;}
.diff-card.match {border-color:#c7e8d0; background:#f2fbf4;}
.diff-card.diff {border-color:#f4b5b9; background:#fff5f5;}
.diff-head {display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:9px;}
.diff-head b {font-size:13px; color:#111827;}
.diff-head span {font-size:11px; font-weight:820; border-radius:999px; padding:3px 8px; color:#111827; background:rgba(255,255,255,.72);}
.diff-card.match .diff-head span {color:#166534; background:#e0f5e6;}
.diff-card.diff .diff-head span {color:#c4212a; background:#ffe3e3;}
.diff-columns {display:grid; grid-template-columns:1fr 1fr; gap:8px;}
.diff-columns div {border:1px solid rgba(15,23,42,.08); background:rgba(255,255,255,.68); border-radius:9px; padding:8px;}
.diff-columns small {display:block; color:#66727f; font-size:11px; font-weight:760; margin-bottom:5px;}
.diff-columns strong {display:block; color:#17202a; font-size:13px; line-height:1.35; word-break:break-word;}
.repair-impact-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:12px; margin:8px 0 16px;}
.repair-card {border:1px solid #e5e9e6; border-radius:13px; padding:13px 14px; background:#fbfcfb; min-height:174px;}
.repair-card.fixed {border-color:#c7e8d0; background:#f2fbf4;}
.repair-card.ready {border-color:#9bd6af; background:#eaf8ef;}
.repair-card.blocked {border-color:#f4b5b9; background:#fff5f5;}
.repair-card.muted {background:#f6f8f7;}
.repair-card-head {display:flex; justify-content:space-between; gap:12px; align-items:flex-start; margin-bottom:8px;}
.repair-card-head b {font-size:13px; color:#111827;}
.repair-card-head span {font-size:11px; font-weight:820; border-radius:999px; padding:3px 8px; color:#374151; background:rgba(255,255,255,.74);}
.repair-card p {font-size:13px; line-height:1.42; color:#24313b; margin:0 0 10px;}
.repair-columns {display:grid; grid-template-columns:1fr 1fr; gap:8px;}
.repair-columns div {border:1px solid rgba(15,23,42,.08); background:rgba(255,255,255,.72); border-radius:9px; padding:8px;}
.repair-columns small {display:block; color:#66727f; font-size:11px; font-weight:760; margin-bottom:5px;}
.repair-columns strong {display:block; color:#17202a; font-size:13px; line-height:1.35;}
.repair-card.fixed .repair-columns div:first-child strong,
.repair-card.ready .repair-columns div:first-child strong {color:#166534;}
.repair-card.blocked .repair-columns div:first-child strong {color:#c4212a;}
.repair-foot {font-size:11px; line-height:1.35; color:#66727f; margin-top:9px;}
.repair-flow {display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin:12px 0 10px;}
.repair-flow-step {border:1px solid #e4e8e6; border-radius:12px; background:#fbfcfb; padding:13px 14px; min-height:104px;}
.repair-flow-step span {display:block; font-size:11px; color:#66727f; font-weight:820; text-transform:uppercase; letter-spacing:.05em;}
.repair-flow-step b {display:block; font-size:25px; line-height:1.1; color:#111827; margin:8px 0 5px; font-variant-numeric:tabular-nums;}
.repair-flow-step small {display:block; color:#66727f; font-size:12px; line-height:1.35;}
.repair-status-note {border:1px solid #e4e8e6; background:#f6f8f7; border-radius:10px; color:#374151; font-size:13px; line-height:1.45; padding:11px 13px; margin:0 0 18px;}
.repair-focus-card {border:1px solid #e5e9e6; border-radius:14px; background:#fbfcfb; padding:16px; margin:10px 0 18px;}
.repair-focus-card.fixed {border-color:#c7e8d0; background:#f2fbf4;}
.repair-focus-card.ready {border-color:#9bd6af; background:#eaf8ef;}
.repair-focus-card.blocked {border-color:#f4b5b9; background:#fff5f5;}
.repair-focus-head {display:flex; justify-content:space-between; align-items:flex-start; gap:14px; margin-bottom:10px;}
.repair-focus-head span {display:block; font-size:11px; color:#66727f; font-weight:820; text-transform:uppercase; letter-spacing:.05em; margin-bottom:5px;}
.repair-focus-head b {display:block; color:#111827; font-size:18px; overflow-wrap:anywhere;}
.repair-focus-head strong {font-size:12px; font-weight:820; border-radius:999px; padding:5px 9px; background:rgba(255,255,255,.76); color:#374151; white-space:nowrap;}
.repair-focus-card p {font-size:14px; line-height:1.45; color:#24313b; margin:0 0 12px;}
.empty-note {border:1px solid #e3e7ea; border-radius:12px; padding:13px; color:#66727f; background:#fbfcfb;}
.source-row {display:grid; grid-template-columns:86px 1fr; gap:8px; align-items:center; font-size:13px; margin:9px 0;}
.source-bar {height:9px; background:#eef2f0; border-radius:999px; overflow:hidden;}
.source-bar span {display:block; height:100%; background:#209b55; border-radius:999px;}
.gis-flow {display:grid; gap:10px; margin-top:4px;}
.gis-node {border:1px solid #e5e9e6; border-radius:10px; padding:11px 13px; display:flex; justify-content:space-between; align-items:center; background:#fbfcfb; font-size:13px;}
.gis-node.ok {border-color:#b7dfc4; background:#eefaf1; color:#166534;}
.gis-node.warn {border-color:#f4d6a3; background:#fff8eb; color:#a16207;}
.section-spacer {height:8px;}
@media (max-width: 1100px) {
  .overview-grid {grid-template-columns:1fr;}
  .right-rail {display:block;}
  .kpi-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
  .review-focus-grid, .repair-flow {grid-template-columns:repeat(2,minmax(0,1fr));}
  .overview-left-grid {grid-template-columns:1fr;}
  .block-container {padding-left:1.2rem; padding-right:1.2rem;}
}
@media (max-width: 900px) {
  .metric-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
  .hero-grid, .legend-grid {grid-template-columns:1fr 1fr;}
  .timeline {grid-template-columns:1fr;}
  .timeline-arrow {display:none;}
  .roadmap-grid {grid-template-columns:1fr;}
  .guidance-grid, .action-grid {grid-template-columns:1fr;}
  .bar-row {grid-template-columns:1fr;}
  .overview-titlebar, .selection-summary {display:block;}
  .selection-summary a {display:inline-block; margin-top:10px;}
  .kpi-grid {grid-template-columns:1fr;}
  .decision-flow-head, .decision-note {display:block;}
  .decision-flow-main {grid-template-columns:1fr;}
  .decision-total {text-align:left; margin-top:0;}
  .decision-branches {grid-template-columns:1fr;}
  .overview-safety-strip, .next-step-grid {grid-template-columns:1fr;}
  .review-focus-grid, .repair-flow {grid-template-columns:1fr;}
  .repair-focus-head {display:block;}
  .repair-focus-head strong {display:inline-block; margin-top:8px;}
}
</style>
""",
        unsafe_allow_html=True,
    )


def _coverage_tab(st: Any, data: dict[str, Any], output_dir: Path) -> None:
    """What's missing vs gold, per rule family + the 101.4 matrix."""
    gold_path = gold_path_for(output_dir)
    gold = _read_json(gold_path, []) if gold_path else []
    benchmark = data.get("benchmark") or {}
    report = data.get("coverage_report") or {}

    st.markdown("#### Coverage by rule family")
    st.caption("Gold coverage = hand-checked bylaw rules the verifier has proven. Held rules wait in review; they never auto-promote.")
    rows = coverage_rows(data, gold, benchmark) if gold else report.get("family_rows", [])
    if rows:
        try:
            import pandas as pd

            frame = pd.DataFrame(rows)
            st.dataframe(
                frame,
                hide_index=True,
                width="stretch",
                column_config={
                    "coverage": st.column_config.ProgressColumn(
                        "Gold coverage", min_value=0.0, max_value=1.0, format="percent"
                    )
                },
            )
        except Exception:
            st.table(rows)

    gaps = gold_gap_rows(benchmark, gold)
    if gaps:
        with st.expander(f"Gold rules not yet proven ({len(gaps)})"):
            for gap in gaps:
                color = STATUS_COLORS.get("review" if gap["status"] == "review" else "rejected", "#57606a")
                st.markdown(
                    f"<div class='detail-sentence'><b style='color:{color}'>\u25cf</b>"
                    f"<span><b>{html.escape(gap['gold_id'])}</b> \u2014 {html.escape(gap['family'])} "
                    f"{html.escape(gap['claim'])} ({html.escape(gap['applies_to'])})<br>"
                    f"<small>{html.escape(gap['detail'])}</small></span></div>",
                    unsafe_allow_html=True,
                )
    elif gold:
        st.success("Every gold rule is verified.")

    if city_stem_from_dir(output_dir).startswith("burnaby"):
        st.markdown("#### Bylaw matrix \u2014 101.4 Development Regulations")
        st.caption(
            "Rows are regulations, columns are the bylaw's dwelling-type \u00d7 unit-count "
            "buckets. Green = verified (geometry-bound to its column), amber = held for "
            "review, red dashes = a gold rule not yet proven, grey = no claim."
        )
        grid = matrix_cells(data.get("verified") or [], data.get("review") or [], gold) if gold else report.get("matrix", {})
        if not grid:
            st.info("No matrix coverage report found. Rerun the slim verifier to generate coverage_report.json.")
            return
        st.markdown(matrix_table_html(grid), unsafe_allow_html=True)


def load_mvp_report() -> dict[str, Any]:
    """Load the final-demo product report used by the portfolio landing page."""
    return _read_json(MVP_REPORT_PATH, {})


def load_m4_source_audit() -> dict[str, Any]:
    """Load the source-PDF audit proving M4 used the expected city PDFs."""
    return _read_json(M4_SOURCE_AUDIT_PATH, {})


def _portfolio_metric_card(label: str, value: Any, note: str = "", tone: str = "") -> str:
    tone_class = f" hero-card-{tone}" if tone else ""
    return (
        f"<div class='hero-card{tone_class}'>"
        f"<div class='hero-label'>{html.escape(label)}</div>"
        f"<div class='hero-value'>{html.escape(str(value))}</div>"
        f"<div class='hero-note'>{html.escape(note)}</div>"
        "</div>"
    )


def _city_name(city: Any) -> str:
    return _plain_label(str(city or ""))


def _current_product_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in report.get("current_runs") or []:
        rows.append(
            {
                "city": _city_name(item.get("city")),
                "candidates": item.get("candidate_rule_count"),
                "verified": item.get("verified_rule_count"),
                "review": item.get("review_rule_count"),
                "rejected": item.get("rejected_rule_count"),
                "not_used": item.get("not_used_rule_count"),
                "precision": item.get("verified_precision"),
                "false_verified": item.get("false_verified_count"),
                "recall": item.get("verified_or_review_recall"),
                "status": item.get("status_label"),
            }
        )
    return rows


def _history_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    groups = [
        ("M4 current", report.get("current_runs") or []),
        ("V3 predecessor", report.get("v3_experimental_runs") or []),
    ]
    rows = []
    for group, items in groups:
        for item in items:
            rows.append(
                {
                    "version": group,
                    "city": _city_name(item.get("city")),
                    "lane": _plain_label(item.get("lane")),
                    "candidates": item.get("candidate_rule_count"),
                    "verified": item.get("verified_rule_count"),
                    "review": item.get("review_rule_count"),
                    "rejected": item.get("rejected_rule_count"),
                    "not_used": item.get("not_used_rule_count"),
                    "precision": item.get("verified_precision"),
                    "false_verified": item.get("false_verified_count"),
                    "recall": item.get("verified_or_review_recall"),
                    "status": item.get("status_label"),
                }
            )
    return rows


def _pdf_page_count(report: dict[str, Any], city: str) -> Any:
    for row in report.get("pdf_inventory") or []:
        if row.get("city") == city:
            return row.get("page_count")
    return ""


def _progress_timeline(st: Any) -> None:
    steps = [
        ("V3 predecessor", "foundation run"),
        ("M4 current", "final-demo path"),
    ]
    html_steps = []
    for index, (title, note) in enumerate(steps):
        active = " timeline-active" if index == len(steps) - 1 else ""
        html_steps.append(
            f"<div class='timeline-step{active}'><b>{html.escape(title)}</b><span>{html.escape(note)}</span></div>"
        )
        if index < len(steps) - 1:
            html_steps.append("<div class='timeline-arrow'>\u2192</div>")
    st.markdown(f"<div class='timeline timeline-compact'>{''.join(html_steps)}</div>", unsafe_allow_html=True)


def _plain_bucket_legend(st: Any) -> None:
    st.markdown(
        """
<div class="legend-grid">
  <div><b>Verified</b><span>safe to use</span></div>
  <div><b>Review</b><span>plausible, needs human check</span></div>
  <div><b>Rejected</b><span>unsafe or unsupported</span></div>
  <div><b>Not used</b><span>outside current product scope</span></div>
  <div><b>Recall</b><span>benchmark recall, not full-bylaw completeness</span></div>
</div>
""",
        unsafe_allow_html=True,
    )


def _source_audit_panel(st: Any, report: dict[str, Any]) -> None:
    audit = load_m4_source_audit()
    summary = audit.get("summary") or {}
    if not summary and not report.get("pdf_inventory"):
        st.info("No M4 source-PDF audit artifact found yet.")
        return
    st.markdown("#### Source audit")
    st.caption("This confirms M4 is reading the real bylaw PDFs. Calgary is treated as the full 1,053-page bylaw.")
    rows = []
    if summary:
        for city, row in summary.items():
            rows.append(
                {
                    "city": _city_name(city),
                    "pdf_pages": row.get("pdf_pages"),
                    "verified_rules": row.get("verified_rules"),
                    "cited_pages": ", ".join(str(page) for page in row.get("unique_cited_pages", [])),
                }
            )
    else:
        for row in report.get("pdf_inventory") or []:
            rows.append(
                {
                    "city": _city_name(row.get("city")),
                    "pdf_pages": row.get("page_count"),
                    "verified_rules": "",
                    "cited_pages": "",
                }
            )
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    failure_count = int(audit.get("failure_count") or 0)
    if failure_count:
        st.error(f"Source audit has {failure_count} failure(s). Treat M4 as unsafe until resolved.")
    else:
        st.success("Source audit passed: no source-PDF failures found.")


def _cloud_roadmap_panel(st: Any) -> None:
    st.markdown("#### Cloud roadmap")
    st.caption("Final-demo cloud work should stay secrets-managed and keep the verifier read-only from the dashboard.")
    st.markdown(
        """
<div class="roadmap-grid">
  <div class="roadmap-card"><b>Phase 1</b><span>Streamlit Cloud demo with curated M4 outputs and optional Gemini Flash Lite secrets for reviewer chat.</span></div>
  <div class="roadmap-card"><b>Phase 2</b><span>Containerized app with persistent artifact storage and environment-managed secrets.</span></div>
  <div class="roadmap-card"><b>Phase 3</b><span>Scheduled extraction and verification jobs, artifact versioning, and reviewer login if needed.</span></div>
</div>
""",
        unsafe_allow_html=True,
    )
    with st.expander("Streamlit Cloud secrets for Ask the Bylaw"):
        st.markdown("Use one hosted provider key. The dashboard still works in retrieval-only mode when no key is configured.")
        st.code(
            """BYLAW_RAG_PROVIDER = "gemini"
BYLAW_RAG_MODEL = "gemini-2.0-flash-lite"
GEMINI_API_KEY = "..."  # Streamlit Cloud secret only""",
            language="toml",
        )


def _portfolio_page(st: Any) -> None:
    """M4-first final-demo landing page."""
    report = load_mvp_report()
    if not report:
        st.info(f"No MVP report found at `{MVP_REPORT_PATH}`. Run `scripts/run_consolidated_prototype.py status`.")
        return

    current_rows = _current_product_rows(report)
    city_count = len([row for row in current_rows if row])
    verified_total = sum(int(row.get("verified") or 0) for row in current_rows)
    review_total = sum(int(row.get("review") or 0) for row in current_rows)
    calgary_pages = _pdf_page_count(report, "calgary_rcg") or "unknown"
    calgary_page_label = f"{int(calgary_pages):,} pages" if isinstance(calgary_pages, int) else f"{calgary_pages} pages"
    promoted = "yes" if (report.get("m4_promotion") or {}).get("promoted") else "no"
    cards = [
        _portfolio_metric_card("Current product path", "M7", "Matrix-aware extraction (gemini-3.1) + deterministic verifier", "verified"),
        _portfolio_metric_card("Safety status", _plain_label(report.get("overall_status")), f"M7 promoted: {promoted}", "verified"),
        _portfolio_metric_card("False verified", report.get("current_false_verified_total", 0), "must stay zero", "rejected"),
        _portfolio_metric_card("Cities tested", city_count, f"{verified_total} verified, {review_total} in review", "review"),
        _portfolio_metric_card("Calgary source", calgary_page_label, "full bylaw, district pages scoped", "not_used"),
    ]
    st.markdown("<div class='hero-grid'>" + "".join(cards) + "</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='instruction-banner'><b>Review M4 first.</b> V3 is retained only as the predecessor comparison. "
        "Downstream work must consume verified-only artifacts.</div>",
        unsafe_allow_html=True,
    )
    _progress_timeline(st)
    _plain_bucket_legend(st)

    st.markdown("#### Current M7 result")
    st.caption("These are the current product rows. Recall means benchmark recall, not full-bylaw completeness.")
    st.dataframe(_display_rows(current_rows), width="stretch", hide_index=True)

    def _build():
        import plotly.graph_objects as go

        cities = [row["city"] for row in current_rows]
        figure = go.Figure()
        figure.add_bar(name="Verified", x=cities, y=[row.get("verified") or 0 for row in current_rows], marker_color="#1a7f37")
        figure.add_bar(name="Review", x=cities, y=[row.get("review") or 0 for row in current_rows], marker_color="#9a6700")
        figure.update_layout(barmode="group", title="Current M7 verified and review counts")
        return figure

    if current_rows:
        _themed_plotly(st, _build)

    _source_audit_panel(st, report)
    _cloud_roadmap_panel(st)

    with st.expander("Predecessor comparison: M4 and V3", expanded=False):
        st.caption("Use this section to explain what changed from V3 to M4. It is not the default product path.")
        history = _history_rows(report)
        if history:
            st.dataframe(_display_rows(history), width="stretch", hide_index=True)
        else:
            st.info("No comparison rows found in the MVP report.")
        st.caption("Recall is benchmark recall from curated evaluation cases, not a promise that every bylaw clause was extracted.")

    st.caption("Pick a city in the sidebar to drill into its funnel, coverage gaps, review workbench, and Ask the Bylaw chat.")


def _unique(items: list[dict[str, Any]], key: str) -> list[str]:
    return sorted({str(item.get(key)) for item in items if item.get(key) not in (None, "")})


def _named_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {str(row.get("name")): int(row.get("count") or 0) for row in rows}


def _by_rule_id(rules: list[dict[str, Any]], rule_id: Any) -> dict[str, Any]:
    return next((rule for rule in rules if rule.get("rule_id") == rule_id), {})


def _source_text(rule: dict[str, Any]) -> str:
    source = rule.get("source", {}) if isinstance(rule.get("source"), dict) else {}
    return str(source.get("evidence_text") or source.get("source_context") or "")


def _humanize(value: Any) -> str:
    return _plain_label(value)


def _plain_label(value: Any) -> str:
    """Convert internal ids into reviewer-facing labels."""
    if value in (None, ""):
        return ""
    text = str(value).strip()
    if text in PLAIN_LABELS:
        return PLAIN_LABELS[text]
    if "," in text:
        return ", ".join(_plain_label(part.strip()) for part in text.split(","))
    if " > " in text:
        return " > ".join(_plain_label(part.strip()) for part in text.split(" > "))
    cleaned = text.replace("_", " ").strip()
    if cleaned.isupper():
        return cleaned
    return cleaned[:1].upper() + cleaned[1:]


def _plain_join(values: Any) -> str:
    if not values:
        return "none"
    if isinstance(values, str):
        return _plain_label(values)
    return ", ".join(_plain_label(value) for value in values)


def _operator_short(operator: Any, constraint_type: Any = None) -> str:
    text = f"{operator or ''} {constraint_type or ''}".lower()
    if any(token in text for token in ("<=", "maximum", "max", "not_exceed")):
        return "No more than"
    if any(token in text for token in (">=", "minimum", "min", "at_least")):
        return "At least"
    if ">" in text:
        return "More than"
    if "<" in text:
        return "Less than"
    if "=" in text or "equal" in text:
        return "Exactly"
    return _plain_label(operator or constraint_type or "")


def _format_value_unit(value: Any, unit: str) -> str:
    if value in (None, ""):
        return ""
    text = str(value).strip()
    return f"{text} {unit}".strip()


def _clean_value(value: Any) -> str:
    return str(value or "").strip()


def _display_rows(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Convert mixed JSON values into stable Streamlit table strings."""
    return [
        {
            _display_key(key): _display_table_value(key, value)
            for key, value in row.items()
        }
        for row in rows
    ]


def _display_key(key: Any) -> str:
    return _plain_label(key)


def _display_table_value(key: Any, value: Any) -> str:
    rendered = _display_value(value)
    key_text = str(key).lower()
    if any(raw in key_text for raw in RAW_VALUE_COLUMNS):
        return rendered
    return _plain_label(rendered)


def _display_value(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    if value in (None, ""):
        return ""
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)


@_cache_data(show_spinner=False)
def _read_json_cached(path_str: str, mtime: int) -> Any:
    """Parse a JSON file, cached across reruns + sessions and keyed by mtime so a
    redeploy (new mtime) invalidates. Returns a sentinel-free value or None."""
    try:
        return json.loads(Path(path_str).read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_json(path: Path, default: Any) -> Any:
    """Cached JSON read. ``load_output_data`` reads ~20 files (incl. a 1.5 MB
    verified_rules.json) every rerun; caching here is the biggest per-rerun win."""
    path = Path(path)
    if not path.exists():
        return default
    try:
        mtime = path.stat().st_mtime_ns
    except Exception:
        mtime = 0
    try:
        value = _read_json_cached(str(path), mtime)
    except Exception:
        # No Streamlit runtime (bare import / tests) or cache error -> direct read.
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default if value is None else value


if __name__ == "__main__":
    main()
