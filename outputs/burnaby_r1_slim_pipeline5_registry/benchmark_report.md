# Burnaby R1 Benchmark Report

## Quality Gates

- PASS: `verified_precision_is_1`
- PASS: `false_verified_is_0`
- PASS: `false_approval_is_0`
- PASS: `proposal_decision_accuracy_is_1`
- PASS: `proposal_case_accuracy_is_1`
- PASS: `retrieval_recall_at_least_0_95`
- PASS: `verified_or_review_recall_at_least_0_90`
- PASS: `verified_source_support_failures_is_0`
- PASS: `proposal_field_expectations_match`

## Rule Metrics

- Gold rules: 22
- Candidate rules: 142
- Verified rules: 11
- Review rules: 81
- Rejected rules: 16
- Not-used / traceability-only rules: 34
- Candidate recall: 1.00
- Verified recall: 0.45
- Verified or review recall: 1.00
- Extraction coverage recall (ceiling): 1.00
- Verifier retention rate: 1.00
- Verifier-rejected gold rules: none
- Not-used gold rules: none
- Unextracted gold rules (upstream gap): none
- Verified precision: 1.00
- Retrieval recall: n/a
- False verified rules: 0
- Source support failures: 0

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

## Evidence Quality

- Evidence units: 142
- Mean evidence quality score: 0.81
- Candidate/evidence match rate: 1.00
- Candidate value grounding rate: 0.97
- Candidate unit grounding rate: 1.00
- Table context completion rate: 1.00

## Proof / Bayesian-Lite Triage

- Proof trace completion rate: 1.00
- Supported claims: 955
- Refuted claims: 4
- Not-enough-info claims: 177
- Mean evidence strength: 0.71
- High-priority review rules: 20
- Table proof rules: 61
- Complete table proofs: 6
- Partial table proofs: 55
- Refuted table proofs: 0
- Proof/decision mismatches: 0

### Top Evidence Quality Issues

- `missing_bbox`: 61
- `evidence_text_not_in_source_context`: 61
- `incomplete_table_context`: 26

## Proposal Metrics

- Proposal cases: 10
- Decision accuracy: 1.00
- Case accuracy including expected fields: 1.00
- False approvals: 0
- False rejections: 0
- Field expectation mismatches: 0
- Needs review decisions: 5

## Missed Gold Rules


## Proposal Results

- PASS: `approved_verified_core_flat` -> needs_review (expected needs_review)
- PASS: `approved_verified_core_sloping_exact` -> approved (expected approved)
- PASS: `reject_flat_roof_height` -> rejected (expected rejected)
- PASS: `reject_front_rear_separation` -> rejected (expected rejected)
- PASS: `reject_accessory_rear_yard` -> needs_review (expected needs_review)
- PASS: `needs_review_lane_yard` -> rejected (expected rejected)
- PASS: `needs_review_rear_principal_rear_yard` -> needs_review (expected needs_review)
- PASS: `needs_review_fire_access` -> needs_review (expected needs_review)
- PASS: `needs_review_heritage_coverage` -> needs_review (expected needs_review)
- PASS: `approve_all_verified_setbacks_and_separations` -> approved (expected approved)
