# BC Zoning Verification Dashboard

Streamlit deployment package for the M6 multi-city verification dashboard. The app
is a read-only communication layer for reviewers and project partners: it
explains committed extraction, verification, review, GIS, and RAG artifacts from
`outputs/` for Burnaby, Calgary, and Vancouver, but it never reruns extraction,
verification, benchmark evaluation, GIS export, or RAG indexing.

The `Source Evidence > Ask The Bylaw` page is an advisory RAG chatbot. It
retrieves committed bylaw index sections first, sends bounded context to
OpenRouter GPT-OSS-120B only when a secret key is configured, and falls back to
retrieval-only mode otherwise. Chat answers never verify rules, approve
proposals, or write GIS outputs.

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
outputs/m5_runs/m6_final_*/<city>/
outputs/m5_runs/m56_hardened_20260616/<city>/
outputs/burnaby_r1_slim_pipeline5_registry/
outputs/burnaby_r1_p9/
outputs/calgary_rcg_slim_pipeline5_registry/
outputs/calgary_rcg_p9/
outputs/vancouver_rs_slim_pipeline5_registry/
outputs/vancouver_rs_p9/
outputs/m4_runs/burnaby_r1/google_gemini_2_5_flash_lite/
outputs/m4_runs/calgary_rcg/google_gemini_2_5_flash_lite/
outputs/m4_runs/vancouver_rs/google_gemini_2_5_flash_lite/
outputs/mvp_verification/mvp_report.json
```

The default landing page is the multi-city M4 overview. Use the sidebar
`City / version` selector to drill into M6 measured runs for final count audit,
or into Burnaby R1, Calgary RCG, or Vancouver RS M4/V3 runs for comparison.

## Current Safety Snapshot

```text
Burnaby M4:   candidates=101, verified=84, review=17, verified_precision=1.00, false_verified=0
Vancouver M4: candidates=32,  verified=12, review=11, verified_precision=1.00, false_verified=0
Calgary M4:   candidates=306, verified=11, review=43, verified_precision=1.00, false_verified=0
```

M4 is the current product path. V3/Pipeline 5/Pipeline 9 artifacts are retained
only as predecessor or comparison context. Failed gates are labeled in the
dashboard as `fail-closed`, `scope mismatch`, or `unsafe / needs fix`; they are
not presented as passing outputs.

M6 is the final release wrapper: it uses M5.6 scored slot measurement to answer
whether the project is verifying too much or too little. The scored legal
denominator is the reviewer-facing count authority; raw numeric slots are shown
only as an advisory over-count guardrail.

## Reviewer Workflow

- `verified_rules.json` and `gis_rule_contract.json` are the only GIS-safe rule
  sources.
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
BYLAW_RAG_MODEL = "openai/gpt-oss-120b"
OPENROUTER_API_KEY = "..."
OPENROUTER_APP_TITLE = "BC Zoning Verification Dashboard"
# Optional:
# OPENROUTER_SITE_URL = "https://your-streamlit-app-url.streamlit.app"
```

The dashboard also supports fallback providers through `BYLAW_RAG_PROVIDER =
"openai"`, `"gemini"`, or `"anthropic"` if the matching provider key is present.
Secrets must stay in Streamlit Cloud settings; do not commit them.
