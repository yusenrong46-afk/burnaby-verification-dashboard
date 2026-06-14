# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `native_v3_rag_llm`
- Evidence units: 32
- Candidate rules: 32
- Verified rules: 12
- Review needed: 11
- Rejected rules: 9
- Not used / traceability only: 0
- Evidence match rate: 1.00
- Value grounding rate: 1.00
- Table context completion: 0.00
- Evidence repair suggestions: 10
- Suggestions with alternative evidence: 10
- Retry candidates from evidence repair: 8
- Evidence intelligence safe bundle retries: 0
- Evidence rerun attempts: 8
- Promotion-ready shadow reruns: 0
- Evidence bundle rerun attempts: 0
- Promotion-ready bundle reruns: 0
- Guarded bundle promotions: 0
- Rule graph nodes / edges: 109 / 536
- Proof DAG sidecar entries: 32
- Cache hits / misses: 0 / 32
- Semantic high-similarity review items: 0
- Review items potentially promotable after evidence fix: 0
- Safe verifier tuning candidates: 0
- Felt verified-rule CSV rows: 12

## Review Actions

- `retry_with_better_evidence`: 8
- `upstream_candidate_issue`: 2
- `defer_low_priority`: 1

## Top Review / Rejection Reasons

- `pipeline5_text_candidate_requires_review`: 19
- `rule_object_not_supported`: 14
- `rule_family_direction_mismatch`: 10
- `rule_object_unit_not_compatible`: 9
- `operator_not_supported`: 6
- `coefficient_operand_not_value`: 6
- `applies_to_not_supported`: 4
- `unresolved_exception_cue`: 4
- `enumerated_branch_condition_missing`: 2
- `unit_not_found_in_evidence`: 1
