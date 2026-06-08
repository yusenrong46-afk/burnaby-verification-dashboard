# Verification Dashboard

This Streamlit dashboard is a read-only product view of the verifier outputs. It is designed for classmates, reviewers, and GIS/Felt collaborators, not as an internal JSON explorer.

Run locally from this deployment repo:

```bash
streamlit run dashboard/streamlit_app.py --server.port 8502
```

Default source folder:

```text
outputs/burnaby_r1_slim_pipeline5_registry/
```

Main pages:

- Overview: safety state, output buckets, and recommended next actions.
- Review Workbench: review queue table plus selected-rule detail in side-by-side columns.
- Evidence Leads: evidence repair / semantic lead queue for reducing review volume.
- GIS/Felt Handoff: verified-only parameters, constraints, map layers, and review blockers.
- Raw + Code: technical file map and raw JSON for debugging.

Important boundary:

```text
verified = safe for downstream export
review_needed = plausible but not proven
rejected = unsafe or contradicted
not_used = traceability/out-of-contract artifact
```

The dashboard does not verify rules, call an LLM, mutate outputs, or touch GIS files.
