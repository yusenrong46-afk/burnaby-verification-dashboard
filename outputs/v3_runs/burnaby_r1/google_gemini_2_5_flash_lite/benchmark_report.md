# burnaby_r1 Benchmark Report

## Quality Gates

- PASS: `verified_precision_is_1`
- PASS: `false_verified_is_0`
- PASS: `false_approval_is_0`
- PASS: `retrieval_recall_at_least_0_95`
- PASS: `verified_or_review_recall_at_least_0_90`
- PASS: `verified_source_support_failures_is_0`
- FAIL: `proposal_decision_accuracy_is_1`
- FAIL: `proposal_case_accuracy_is_1`
- FAIL: `proposal_field_expectations_match`

## Rule Metrics

- Gold rules: 40
- Candidate rules: 103
- Verified rules: 84
- Review rules: 19
- Rejected rules: 0
- Not-used / traceability-only rules: 0
- Candidate recall: 0.47
- Verified recall: 0.85
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

- `pipeline5_text_candidate_requires_review`: 17
- `rule_family_direction_mismatch`: 5
- `applies_to_not_supported`: 4
- `rule_object_not_supported`: 4
- `operator_not_supported`: 2
- `text_condition_not_supported`: 2
- `constraint_scope_not_supported`: 1
- `range_bound_not_maximum`: 1
- `unresolved_exception_cue`: 1

## Evidence Quality

- Evidence units: 103
- Mean evidence quality score: 0.72
- Candidate/evidence match rate: 1.00
- Candidate value grounding rate: 1.00
- Candidate unit grounding rate: 1.00
- Table context completion rate: 1.00

## Proof / Bayesian-Lite Triage

- Proof trace completion rate: 1.00
- Supported claims: 796
- Refuted claims: 0
- Not-enough-info claims: 28
- Mean evidence strength: 0.86
- High-priority review rules: 1
- Table proof rules: 81
- Complete table proofs: 37
- Partial table proofs: 44
- Refuted table proofs: 0
- Proof/decision mismatches: 0

### Top Evidence Quality Issues

- `missing_bbox`: 81
- `evidence_text_not_in_source_context`: 81

## Proposal Metrics

- Proposal cases: 10
- Decision accuracy: 0.80
- Case accuracy including expected fields: 0.50
- False approvals: 0
- False rejections: 0
- Field expectation mismatches: 5
- Needs review decisions: 6

## Missed Gold Rules


## Proposal Results

- FAIL: `approved_verified_core_flat` -> needs_review (expected needs_review)
- FAIL: `approved_verified_core_sloping_exact` -> needs_review (expected approved)
- FAIL: `reject_flat_roof_height` -> needs_review (expected rejected)
- PASS: `reject_front_rear_separation` -> rejected (expected rejected)
- PASS: `reject_accessory_rear_yard` -> needs_review (expected needs_review)
- PASS: `needs_review_lane_yard` -> rejected (expected rejected)
- PASS: `needs_review_rear_principal_rear_yard` -> needs_review (expected needs_review)
- FAIL: `needs_review_fire_access` -> rejected (expected rejected)
- FAIL: `needs_review_heritage_coverage` -> needs_review (expected needs_review)
- PASS: `approve_all_verified_setbacks_and_separations` -> approved (expected approved)
