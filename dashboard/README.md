# Verification Dashboard

The dashboard is a reader for verifier outputs. It does not call an LLM, change
decisions, or promote rules.

Run from the project root:

```bash
.venv/bin/python -m streamlit run dashboard/streamlit_app.py --server.port 8502
```

Default output folder:

```text
outputs/burnaby_r1_slim_pipeline5_registry/
```

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
