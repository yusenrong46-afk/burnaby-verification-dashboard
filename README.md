# BC Zoning Verification Dashboard

Streamlit deployment package for the **M7** multi-city verification dashboard. The app
is a read-only communication layer for reviewers and project partners: it
explains committed extraction, verification, review, GIS, and RAG artifacts from
`outputs/` for Burnaby, Calgary, and Vancouver, but it never reruns extraction,
verification, benchmark evaluation, GIS export, or RAG indexing.

M7 is the generational release: one consolidated matrix-aware pipeline on
`google/gemini-3.1-flash-lite`, four-tab "Civic Console" UI with count drill-downs,
and a reranked bylaw chatbot. The deterministic verifier remains the sole authority
(precision 1.0, zero false-verified on the benchmarked in-contract lanes).

The `Ask The Bylaw` tab is an advisory RAG chatbot. It retrieves committed bylaw
index sections first, sends bounded context to OpenRouter `google/gemini-3.1-flash-lite`
only when a secret key is configured, and falls back to retrieval-only mode
otherwise. Chat answers never verify rules, approve proposals, or write GIS outputs.

Cloud app:
https://yusenrong46-afk-burnaby-verificat-dashboardstreamlit-app-rcvryj.streamlit.app/

## Run Locally

```bash
python -m pip install -r requirements.txt
streamlit run dashboard/streamlit_app.py
```

## Included Outputs

The dashboard discovers output directories automatically when they contain
`verified_rules.json`.

```text
outputs/m7_runs/burnaby_r1/google_gemini_3_1_flash_lite/
outputs/m7_runs/calgary_rcg/google_gemini_3_1_flash_lite/
outputs/m7_runs/vancouver_rs/google_gemini_3_1_flash_lite/
outputs/m7_measure/m7_gemini31_final_20260616/<city>/
outputs/mvp_verification/mvp_report.json
```

The default landing page is the multi-city M7 overview (Summary · Review Queue ·
GIS Handoff · Ask the Bylaw). Use the sidebar selector to switch cities; every
count tile drills down to the exact rules behind it.

## Current Safety Snapshot

```text
Burnaby M7:   candidates=144, verified=87, review=57, verified_precision=1.00, false_verified=0
Vancouver M7: candidates=56,  verified=10, review=31, verified_precision=1.00, false_verified=0
Calgary M7:   candidates=150, verified=29, review=42, verified_precision=1.00, false_verified=0
```

M7 is the current product path: a consolidated matrix-aware extraction pipeline
(deterministic table cells + rule-signal sweep + repair) on
`google/gemini-3.1-flash-lite`, with the district page-scope fix. The deterministic
verifier was never loosened — recall gains come from better extraction. Across all
three benchmarked in-contract lanes: precision 1.0, zero false-verified, adversarial
ALL BLOCKED. Verified accuracy was confirmed against the actual bylaw PDFs (a
ground-truth audit), and a verification-recall "rescue" that injected false-verifies
was reverted — the verifier sits at its safe recall ceiling.

Recall here is *verified-or-review against a curated in-contract gold set*, not
full-bylaw completeness. Failed gates are labeled `fail-closed`, `scope mismatch`,
or `unsafe / needs fix`; they are not presented as passing outputs.

## Reviewer Workflow

- `verified_rules.json` is the raw verifier audit trail. `gis_rule_contract.json`
  is the deduplicated GIS-safe contract and includes a `deduplication` block.
- `review_needed.json`, `source_repair_report.json`, and
  `review_assistant_packets.json` are advisory/debug artifacts for human review.
- Extraction proposes candidate rules; deterministic verification decides which
  rules become trusted outputs.
- The M6 Too Much / Too Little panel explains count trust: unsupported verified
  rules mean too much; scored review/missed slots mean conservative coverage.
- The Review Assistant panel is advisory only. It may summarize bounded evidence
  context, but it cannot approve rules or write GIS outputs.

## Optional RAG Chat LLM

Set Streamlit Cloud secrets:

```toml
BYLAW_RAG_PROVIDER = "openrouter"
BYLAW_RAG_MODEL = "google/gemini-3.1-flash-lite"
OPENROUTER_API_KEY = "..."
OPENROUTER_APP_TITLE = "BC Zoning Verification Dashboard"
# Optional:
# OPENROUTER_SITE_URL = "https://your-streamlit-app-url.streamlit.app"
```

The dashboard also supports fallback providers through `BYLAW_RAG_PROVIDER =
"openai"`, `"gemini"`, or `"anthropic"` if the matching provider key is present.
Secrets must stay in Streamlit Cloud settings; do not commit them.

<!-- deploy: M7 @ 2026-06-17T06:57Z (commit triggers Streamlit Cloud rebuild from main) -->
