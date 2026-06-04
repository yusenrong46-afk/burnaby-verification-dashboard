# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `pipeline5_registry`
- Evidence units: 142
- Candidate rules: 142
- Verified rules: 27
- Review needed: 66
- Rejected rules: 16
- Not used / traceability only: 33
- Evidence match rate: 1.00
- Value grounding rate: 0.97
- Table context completion: 1.00
- Evidence repair suggestions: 58
- Suggestions with alternative evidence: 58
- Retry candidates from evidence repair: 48

## Review Audit Actions

- `retry_with_better_evidence`: 46
- `safe_verifier_tuning_candidate`: 6
- `evidence_packet_repair_candidate`: 4
- `needs_second_source_consensus`: 4
- `defer_low_priority`: 3
- `human_legal_review`: 2
- `upstream_candidate_issue`: 1

## Top Review / Rejection Reasons

- `pipeline5_text_candidate_requires_review`: 76
- `rule_object_not_supported`: 46
- `operator_not_supported`: 40
- `applies_to_not_supported`: 38
- `outside_current_rule_contract`: 30
- `table_cell_candidate_requires_review`: 29
- `table_evidence_candidate_requires_review`: 29
- `text_condition_not_supported`: 28
- `rule_family_direction_mismatch`: 25
- `table_column_not_target_scope`: 19
