# Burnaby R1 Benchmark Report

## Quality Gates

- PASS: `verified_precision_is_1`
- PASS: `false_verified_is_0`
- PASS: `false_approval_is_0`
- PASS: `retrieval_recall_at_least_0_95`
- PASS: `verified_or_review_recall_at_least_0_90`
- PASS: `verified_source_support_failures_is_0`
- PASS: `proposal_decision_accuracy_is_1`
- PASS: `proposal_case_accuracy_is_1`
- PASS: `proposal_field_expectations_match`

## Rule Metrics

- Gold rules: 29
- Candidate rules: 142
- Verified rules: 30
- Review rules: 63
- Rejected rules: 16
- Not-used / traceability-only rules: 33
- Candidate recall: 1.00
- Verified recall: 0.90
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

- `pipeline5_text_candidate_requires_review`: 74
- `rule_object_not_supported`: 46
- `operator_not_supported`: 39
- `applies_to_not_supported`: 37
- `outside_current_rule_contract`: 30
- `text_condition_not_supported`: 30
- `table_cell_candidate_requires_review`: 29
- `table_evidence_candidate_requires_review`: 29
- `rule_family_direction_mismatch`: 25
- `table_column_not_target_scope`: 19

## Evidence Quality

- Evidence units: 142
- Mean evidence quality score: 0.81
- Candidate/evidence match rate: 1.00
- Candidate value grounding rate: 0.97
- Candidate unit grounding rate: 1.00
- Table context completion rate: 1.00

## Proof / Bayesian-Lite Triage

- Proof trace completion rate: 1.00
- Supported claims: 970
- Refuted claims: 4
- Not-enough-info claims: 162
- Mean evidence strength: 0.73
- High-priority review rules: 5
- Table proof rules: 62
- Complete table proofs: 10
- Partial table proofs: 52
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
- Needs review decisions: 4

## Missed Gold Rules


## Proposal Results

- PASS: `approved_verified_core_flat` -> needs_review (expected needs_review)
- PASS: `approved_verified_core_sloping_exact` -> approved (expected approved)
- PASS: `reject_flat_roof_height` -> rejected (expected rejected)
- PASS: `reject_front_rear_separation` -> rejected (expected rejected)
- PASS: `reject_accessory_rear_yard` -> needs_review (expected needs_review)
- PASS: `needs_review_lane_yard` -> rejected (expected rejected)
- PASS: `needs_review_rear_principal_rear_yard` -> needs_review (expected needs_review)
- PASS: `needs_review_fire_access` -> rejected (expected rejected)
- PASS: `needs_review_heritage_coverage` -> needs_review (expected needs_review)
- PASS: `approve_all_verified_setbacks_and_separations` -> approved (expected approved)
