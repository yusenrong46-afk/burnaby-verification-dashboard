# Burnaby Verification Dashboard

Run from `Burnaby_prototype`:

```bash
streamlit run dashboard/streamlit_app.py --server.port 8502
```

Default source folder:

```text
outputs/burnaby_r1_slim_pipeline5_registry/
```

The dashboard reads generated verifier outputs only. It does not call an LLM and
does not change verification decisions.

Main tabs:

- Overview: bucket counts, quality gates, review categories, potential mistakes
- Review Queue: ranked review items with categories and likely-correct scores
- Candidate vs Verified: review candidate compared with closest verified rule
- Evidence Repair: deterministic evidence-repair suggestions
- Evidence Rerun: shadow verifier reruns against stronger suggested evidence,
  including promotion-ready risk screening
- Review Audit: action buckets for reducing review volume
- Verification Structure: file/layer map
- Extraction Preflight: Pipeline 5 notebook readiness
