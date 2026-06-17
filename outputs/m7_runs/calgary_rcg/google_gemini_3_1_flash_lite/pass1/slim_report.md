# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `native_v3_rag_llm`
- Evidence units: 84
- Candidate rules: 84
- Verified rules: 21
- Review needed: 23
- Rejected rules: 13
- Not used / traceability only: 27
- Evidence match rate: 1.00
- Value grounding rate: 0.94
- Table context completion: 0.00
- Evidence repair suggestions: 19
- Suggestions with alternative evidence: 19
- Retry candidates from evidence repair: 18
- Evidence intelligence safe bundle retries: 15
- Evidence rerun attempts: 18
- Promotion-ready shadow reruns: 0
- Evidence bundle rerun attempts: 18
- Promotion-ready bundle reruns: 4
- Guarded bundle promotions: 4
- Rule graph nodes / edges: 293 / 875
- Proof DAG sidecar entries: 84
- Cache hits / misses: 0 / 84
- Semantic high-similarity review items: 5
- Review items potentially promotable after evidence fix: 0
- Safe verifier tuning candidates: 0
- Felt verified-rule CSV rows: 20

## Review Actions

- `retry_with_better_evidence`: 18
- `defer_low_priority`: 3
- `human_legal_review`: 1
- `upstream_candidate_issue`: 1

## Top Review / Rejection Reasons

- `text_candidate_requires_review`: 57
- `upstream_extraction_requested_review`: 44
- `extraction_source_fidelity_hold`: 38
- `outside_target_section`: 29
- `rule_object_not_supported`: 28
- `operator_not_supported`: 22
- `applies_to_not_supported`: 16
- `enumerated_branch_condition_missing`: 16
- `constraint_scope_not_supported`: 11
- `rule_family_direction_mismatch`: 8
