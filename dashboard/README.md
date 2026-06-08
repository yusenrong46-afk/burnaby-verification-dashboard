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

Main sidebar pages:

- Start Here: plain-English summary, safety state, and recommended workflow
- Results: bucket counts, benchmark gates, and current verifier output
- Review Queue: ranked review items with category, action bucket, and reviewer instructions
- Candidate Compare: review candidate compared with closest verified rule
- Evidence Tools: Evidence Intelligence, deterministic repair, MiniLM retrieval, and shadow reruns
- GIS/Felt Export: verified-only parameter export, map-layer needs, and review blockers
- Code Explanation: file/layer map
- Advanced: extraction feedback plus rule relationship diagnostics
