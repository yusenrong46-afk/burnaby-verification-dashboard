# Verification Dashboard

Run from `code/burnaby_rule_verification_prototype`:

```bash
streamlit run dashboard/streamlit_app.py --server.port 8502
```

Default source folder:

```text
outputs/burnaby_r1_slim_pipeline5_registry/
```

To inspect another verifier run, pass an output directory:

```bash
streamlit run dashboard/streamlit_app.py -- \
  --output-dir /tmp/vancouver_pipeline6_verifier_span_summary
```

The dashboard reads generated verifier outputs only. It does not call an LLM and
does not change verification decisions.

Main tabs:

- Overview: bucket counts, quality gates, review categories, potential mistakes
- Review Tree: ranked review items with category, action bucket, and reviewer instructions
- Candidate vs Verified: review candidate compared with closest verified rule
- Evidence Intelligence: deduplicated deterministic repair + MiniLM evidence leads
- Extraction Feedback: grouped feedback for upstream extraction fixes
- Advanced Rerun: optional shadow verifier reruns against stronger suggested evidence,
  including promotion-ready risk screening
- Rule Relationships: consensus, conflict, and cross-family diagnostics
- GIS/Felt Export: verified-only downstream contract preview
- Code Explanation: file/layer map
