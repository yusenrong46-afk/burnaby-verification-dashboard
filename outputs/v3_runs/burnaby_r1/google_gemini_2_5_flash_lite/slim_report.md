# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `native_v3_rag_llm`
- Evidence units: 103
- Candidate rules: 103
- Verified rules: 84
- Review needed: 19
- Rejected rules: 0
- Not used / traceability only: 0
- Evidence match rate: 1.00
- Value grounding rate: 1.00
- Table context completion: 1.00
- Evidence repair suggestions: 17
- Suggestions with alternative evidence: 17
- Retry candidates from evidence repair: 15
- Evidence intelligence safe bundle retries: 2
- Evidence rerun attempts: 15
- Promotion-ready shadow reruns: 1
- Evidence bundle rerun attempts: 2
- Promotion-ready bundle reruns: 0
- Guarded bundle promotions: 0
- Rule graph nodes / edges: 417 / 1788
- Proof DAG sidecar entries: 103
- Cache hits / misses: 100 / 3
- Semantic high-similarity review items: 2
- Review items potentially promotable after evidence fix: 3
- Safe verifier tuning candidates: 0
- Felt verified-rule CSV rows: 84

## Review Actions

- `retry_with_better_evidence`: 15
- `needs_second_source_consensus`: 2
- `human_legal_review`: 1
- `defer_low_priority`: 1

## Top Review / Rejection Reasons

- `pipeline5_text_candidate_requires_review`: 17
- `rule_family_direction_mismatch`: 5
- `applies_to_not_supported`: 4
- `rule_object_not_supported`: 4
- `text_condition_not_supported`: 2
- `operator_not_supported`: 2
- `unresolved_exception_cue`: 1
- `range_bound_not_maximum`: 1
- `constraint_scope_not_supported`: 1
