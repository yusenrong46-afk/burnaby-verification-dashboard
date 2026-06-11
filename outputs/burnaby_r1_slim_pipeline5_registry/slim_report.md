# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `pipeline5_registry`
- Evidence units: 142
- Candidate rules: 142
- Verified rules: 30
- Review needed: 63
- Rejected rules: 35
- Not used / traceability only: 14
- Evidence match rate: 1.00
- Value grounding rate: 0.88
- Table context completion: 1.00
- Evidence repair suggestions: 54
- Suggestions with alternative evidence: 54
- Retry candidates from evidence repair: 52
- Evidence intelligence safe bundle retries: 23
- Evidence rerun attempts: 52
- Promotion-ready shadow reruns: 0
- Evidence bundle rerun attempts: 15
- Promotion-ready bundle reruns: 0
- Guarded bundle promotions: 0
- Rule graph nodes / edges: 550 / 1925
- Cache hits / misses: 0 / 142
- Semantic high-similarity review items: 3
- Review items potentially promotable after evidence fix: 4
- Safe verifier tuning candidates: 4
- Felt verified-rule CSV rows: 30

## Review Actions

- `retry_with_better_evidence`: 46
- `human_legal_review`: 6
- `defer_low_priority`: 5
- `safe_verifier_tuning_candidate`: 4
- `needs_second_source_consensus`: 2

## Top Review / Rejection Reasons

- `pipeline5_text_candidate_requires_review`: 75
- `applies_to_not_supported`: 35
- `rule_object_not_supported`: 35
- `operator_not_supported`: 29
- `table_cell_candidate_requires_review`: 27
- `table_evidence_candidate_requires_review`: 27
- `rule_family_direction_mismatch`: 26
- `table_column_not_target_scope`: 19
- `text_condition_not_supported`: 19
- `rule_object_unit_not_compatible`: 15
