# Verification Dashboard

The dashboard is a reviewer and partner-facing reader for multi-city extraction,
verification, review, GIS, and source-evidence outputs. It includes Burnaby R1,
Calgary RCG, and Vancouver RS in the committed M4 artifact set. It can
optionally call an advisory RAG chatbot, but it never changes decisions,
promotes rules, or writes verifier artifacts.

Run from the project root:

```bash
.venv/bin/python -m streamlit run dashboard/streamlit_app.py --server.port 8502
```

Default city drilldown when a direct `--output-dir` is supplied:

```text
outputs/m4_runs/burnaby_r1/google_gemini_2_5_flash_lite/
```

## v2

- **City selector** — the sidebar lists every `outputs/*_slim_pipeline5_registry/`
  dir and native `outputs/m4_runs/*/*/` dir that contains `verified_rules.json`
  for Burnaby, Calgary, Vancouver, and any future committed city. The landing
  page starts with a multi-city M4 overview; city drilldowns are selected from
  the sidebar. New cities appear automatically once their outputs exist; nothing
  is hardcoded. All loads are city-aware.
- **Sections** — the former flat tab strip is grouped into six top-level
  sections (every original tab is preserved inside one of them):
  `Overview` / `Rules` (Candidate vs Verified, Rule Graph) / `Review` (Review,
  Review Resolution, Semantic Review) / `Evidence & Proof` (Evidence
  Intelligence, Evidence Repair, Evidence Rerun, Bundle Rerun, Bylaw) /
  `GIS & Map` (Map, 3D Envelope, Felt Export) / `System` (Safe Tuning,
  Verification Structure, Extraction Preflight).
- **Map tab** — a pydeck deck centered on the selected city showing a
  representative 30 m x 40 m **demo lot** (not a real parcel) with verified
  setback bands, the buildable footprint extruded to the max verified height,
  and tooltips carrying parameter, value, operator, rule id, and evidence
  quote. Requires the optional extra: `pip install -e .[map]`; without pydeck
  the tab shows an install hint instead.
- **Ask The Bylaw** — renders extracted bylaw sections and includes advisory
  RAG chat. The default hosted model is OpenRouter `openai/gpt-oss-120b` when
  `OPENROUTER_API_KEY` is configured. Retrieval-only mode still works without a
  key.
- **3D envelope** — `scripts/build_envelope_3d.py` writes
  `outputs/<city>.../envelope_3d.html` (self-contained Three.js + OrbitControls
  from CDN) from `buildable_envelope.json`; the dashboard embeds it when the
  file exists and always shows a printable SVG plan-view fallback with setback
  arrows, values, and rule ids.
- **Color semantics (strict, everywhere)** — verified `#1a7f37` (green),
  review `#9a6700` (amber), rejected `#cf222e` (red), not_used `#57606a`
  (grey).

The dashboard still runs with only the base dependency (`streamlit`); pydeck
and the Three.js artifact degrade gracefully with informative messages.

## Chatbot Secrets

```toml
BYLAW_RAG_PROVIDER = "openrouter"
BYLAW_RAG_MODEL = "openai/gpt-oss-120b"
OPENROUTER_API_KEY = "..."
OPENROUTER_APP_TITLE = "BC Zoning Verification Dashboard"
# Optional:
# OPENROUTER_SITE_URL = "https://your-streamlit-app-url.streamlit.app"
```

The chatbot is not part of the verifier. It can explain retrieved bylaw text for
reviewers, but it cannot verify, reject, approve, or write JSON outputs.

## How To Read It

```text
verified
```

Safe, source-supported rules. These are the only rules that should drive GIS.

```text
review_needed
```

Possibly useful rules that need clearer evidence, scope, condition, or legal
review.

```text
rejected
```

Unsafe or contradicted candidates.

```text
not_used
```

Traceability-only or out-of-contract candidates, such as cross-references and
administrative rules.

## Main Pages

```text
Overview
```

Counts, quality gates, review categories, and benchmark results.

```text
Review
```

Single reviewer-facing queue from `review_router.json`. It combines priority,
likely status, action bucket, decision path, plain-English rule/evidence
sentences, and human next step.

```text
Candidate vs Verified
```

Side-by-side sentence view: what a review candidate claims versus the nearest
verified rule.

```text
Evidence Repair
```

Possible stronger evidence snippets. These suggestions are advisory only.

```text
GIS/Felt Export
```

Verified-only GIS contract and map-friendly export preview.

```text
Verification Structure
```

File and layer map explaining how the verifier is organized.

## Guardrail

The dashboard explains decisions. It does not make decisions.

Extraction proposes candidate rules. Deterministic verification decides which
rules are trusted and GIS-safe.
