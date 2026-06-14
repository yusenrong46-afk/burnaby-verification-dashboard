# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `native_v3_rag_llm`
- Evidence units: 225
- Candidate rules: 225
- Verified rules: 10
- Review needed: 28
- Rejected rules: 28
- Not used / traceability only: 159
- Evidence match rate: 1.00
- Value grounding rate: 0.98
- Table context completion: 0.00
- Evidence repair suggestions: 25
- Suggestions with alternative evidence: 25
- Retry candidates from evidence repair: 25
- Evidence intelligence safe bundle retries: 13
- Evidence rerun attempts: 25
- Promotion-ready shadow reruns: 0
- Evidence bundle rerun attempts: 13
- Promotion-ready bundle reruns: 0
- Guarded bundle promotions: 0
- Rule graph nodes / edges: 593 / 1490
- Proof DAG sidecar entries: 225
- Cache hits / misses: 225 / 0
- Semantic high-similarity review items: 6
- Review items potentially promotable after evidence fix: 4
- Safe verifier tuning candidates: 0
- Felt verified-rule CSV rows: 10

## Review Actions

- `retry_with_better_evidence`: 25
- `defer_low_priority`: 3

## Top Review / Rejection Reasons

- `upstream_extraction_requested_review`: 190
- `pipeline5_text_candidate_requires_review`: 179
- `outside_target_section`: 177
- `enumerated_branch_condition_missing`: 80
- `constraint_scope_not_supported`: 54
- `applies_to_not_supported`: 48
- `rule_object_not_supported`: 31
- `operator_not_supported`: 24
- `rule_object_unit_not_compatible`: 22
- `rule_family_direction_mismatch`: 15
