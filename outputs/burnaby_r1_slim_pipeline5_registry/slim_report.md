# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `pipeline5_registry`
- Evidence units: 142
- Candidate rules: 142
- Verified rules: 11
- Review needed: 81
- Rejected rules: 16
- Not used / traceability only: 34
- Evidence match rate: 1.00
- Value grounding rate: 0.97
- Table context completion: 1.00
- Evidence repair suggestions: 61
- Suggestions with alternative evidence: 61
- Retry candidates from evidence repair: 51
- Evidence rerun shadow verified: 4
- Evidence rerun promotion-ready: 1

## Review Audit Actions

- `retry_with_better_evidence`: 49
- `safe_verifier_tuning_candidate`: 16
- `human_legal_review`: 6
- `needs_second_source_consensus`: 5
- `evidence_packet_repair_candidate`: 3
- `upstream_candidate_issue`: 1
- `defer_low_priority`: 1

## Top Review / Rejection Reasons

- `pipeline5_text_candidate_requires_review`: 79
- `rule_object_not_supported`: 49
- `table_cell_candidate_requires_review`: 46
- `table_evidence_candidate_requires_review`: 46
- `operator_not_supported`: 41
- `applies_to_not_supported`: 38
- `outside_current_rule_contract`: 31
- `text_condition_not_supported`: 29
- `table_column_not_target_scope`: 20
- `table_applies_to_not_supported`: 10
