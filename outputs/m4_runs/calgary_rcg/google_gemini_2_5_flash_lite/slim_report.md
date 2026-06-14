# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `native_v3_rag_llm`
- Evidence units: 306
- Candidate rules: 306
- Verified rules: 11
- Review needed: 43
- Rejected rules: 35
- Not used / traceability only: 217
- Evidence match rate: 1.00
- Value grounding rate: 0.97
- Table context completion: 0.00
- Evidence repair suggestions: 40
- Suggestions with alternative evidence: 40
- Retry candidates from evidence repair: 40
- Evidence intelligence safe bundle retries: 28
- Evidence rerun attempts: 40
- Promotion-ready shadow reruns: 0
- Evidence bundle rerun attempts: 28
- Promotion-ready bundle reruns: 0
- Guarded bundle promotions: 0
- Rule graph nodes / edges: 844 / 1988
- Proof DAG sidecar entries: 306
- Cache hits / misses: 0 / 306
- Semantic high-similarity review items: 11
- Review items potentially promotable after evidence fix: 3
- Safe verifier tuning candidates: 0
- Felt verified-rule CSV rows: 11

## Review Actions

- `retry_with_better_evidence`: 40
- `defer_low_priority`: 3

## Top Review / Rejection Reasons

- `upstream_extraction_requested_review`: 273
- `pipeline5_text_candidate_requires_review`: 243
- `outside_target_section`: 240
- `enumerated_branch_condition_missing`: 99
- `applies_to_not_supported`: 93
- `constraint_scope_not_supported`: 56
- `rule_object_not_supported`: 50
- `operator_not_supported`: 38
- `rule_object_unit_not_compatible`: 24
- `rule_family_direction_mismatch`: 21
