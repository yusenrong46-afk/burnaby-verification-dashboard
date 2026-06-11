# BC Zoning Verification Dashboard

Streamlit deployment package for the verification dashboard. The app is read-only:
it loads committed verifier artifacts from `outputs/` and never reruns extraction,
verification, benchmark evaluation, GIS export, RAG indexing, or LLM review.

## Run Locally

```bash
python -m pip install -r requirements.txt
streamlit run dashboard/streamlit_app.py
```

## Included Outputs

The dashboard discovers output directories automatically when they contain
`verified_rules.json`.

```text
outputs/burnaby_r1_slim_pipeline5_registry/
outputs/burnaby_r1_p9/
outputs/calgary_rcg_slim_pipeline5_registry/
outputs/calgary_rcg_p9/
outputs/vancouver_rs_slim_pipeline5_registry/
outputs/vancouver_rs_p9/
```

## Current Safety Snapshot

```text
Burnaby P5:   verified_precision=1.00, false_verified=0, verified=30
Calgary P5:   verified_precision=1.00, false_verified=0, verified=6
Vancouver P5: verified_precision=1.00, false_verified=0, candidate_recall=0.86
```

Pipeline 9 results are shown for comparison only. Failed gates are labeled in
the dashboard as `fail-closed`, `scope mismatch`, or `unsafe / needs fix`; they
are not presented as passing outputs.

## Reviewer Workflow

- `verified_rules.json` and `gis_rule_contract.json` are the only GIS-safe rule
  sources.
- `review_needed.json`, `source_repair_report.json`, and
  `review_assistant_packets.json` are advisory/debug artifacts for human review.
- The Review Assistant panel is advisory only. It may summarize bounded evidence
  context, but it cannot approve rules or write GIS outputs.
