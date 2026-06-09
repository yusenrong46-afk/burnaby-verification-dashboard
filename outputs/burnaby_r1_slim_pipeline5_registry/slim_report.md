# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `pipeline5_registry`
- Evidence units: 142
- Candidate rules: 142
- Verified rules: 30
- Review needed: 63
- Rejected rules: 16
- Not used / traceability only: 33
- Evidence match rate: 1.00
- Value grounding rate: 0.97
- Table context completion: 1.00
- Evidence repair suggestions: 56
- Suggestions with alternative evidence: 56
- Retry candidates from evidence repair: 43
- Evidence intelligence safe bundle retries: 22
- Evidence rerun attempts: 43
- Promotion-ready shadow reruns: 0
- Evidence bundle rerun attempts: 18
- Promotion-ready bundle reruns: 3
- Guarded bundle promotions: 3
- Rule graph nodes / edges: 544 / 1931
- Cache hits / misses: 142 / 0
- Semantic high-similarity review items: 3
- Safe verifier tuning candidates: 5
- Felt verified-rule CSV rows: 30

## Review Actions

- `retry_with_better_evidence`: 41
- `evidence_packet_repair_candidate`: 7
- `safe_verifier_tuning_candidate`: 5
- `needs_second_source_consensus`: 4
- `defer_low_priority`: 3
- `human_legal_review`: 2
- `upstream_candidate_issue`: 1

## Top Review / Rejection Reasons

- `pipeline5_text_candidate_requires_review`: 74
- `rule_object_not_supported`: 46
- `operator_not_supported`: 39
- `applies_to_not_supported`: 37
- `text_condition_not_supported`: 30
- `outside_current_rule_contract`: 30
- `table_cell_candidate_requires_review`: 29
- `table_evidence_candidate_requires_review`: 29
- `rule_family_direction_mismatch`: 25
- `table_column_not_target_scope`: 19
