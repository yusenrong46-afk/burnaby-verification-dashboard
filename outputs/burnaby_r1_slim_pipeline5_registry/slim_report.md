# Slim Verification Report

```text
Pipeline 5/6 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `pipeline5_registry`
- City / zone: `Burnaby / R1`
- Source document: `R1Small-Scale-Multi-Unit-Housing-District.pdf`
- Evidence units: 142
- Candidate rules: 142
- Verified rules: 18
- Review needed: 81
- Rejected rules: 20
- Not used / traceability only: 23
- Evidence match rate: 1.00
- Value grounding rate: 0.97
- Table context completion: 1.00
- Evidence repair suggestions: 61
- Suggestions with alternative evidence: 61
- Retry candidates from evidence repair: 37
- Evidence rerun mode: `disabled`
- Evidence rerun verified: 0
- Evidence rerun promotion-ready: 0
- Semantic retrieval backend: `fallback_lexical`
- Semantic retrieval suggestions: 74
- High-confidence semantic matches: 18
- Evidence intelligence items: 81
- Evidence intelligence no-suggestion items: 3
- Evidence intelligence rerun attempts: 47
- Evidence intelligence promotion-ready: 1
- Extraction feedback rows: 104
- GIS/Felt constraints: 18
- GIS/Felt buildable-area parameters: 16
- GIS/Felt review blockers: 81

## Review Router Actions

- `retry_with_better_evidence`: 35
- `safe_verifier_tuning_candidate`: 28
- `needs_second_source_consensus`: 7
- `defer_low_priority`: 6
- `human_legal_review`: 5

## Top Review / Rejection Reasons

- `text_candidate_requires_review`: 76
- `table_cell_candidate_requires_review`: 44
- `table_evidence_candidate_requires_review`: 44
- `operator_not_supported`: 41
- `applies_to_not_supported`: 36
- `rule_object_not_supported`: 31
- `text_condition_not_supported`: 28
- `table_column_not_target_scope`: 19
- `outside_current_rule_contract`: 18
- `table_applies_to_not_supported`: 10
