# burnaby_r1 Benchmark Report

## Quality Gates

- FAIL: `verified_precision_is_1`
- PASS: `false_verified_is_0`
- PASS: `false_approval_is_0`
- PASS: `retrieval_recall_at_least_0_95`
- FAIL: `verified_or_review_recall_at_least_0_90`
- PASS: `verified_source_support_failures_is_0`
- FAIL: `proposal_decision_accuracy_is_1`
- FAIL: `proposal_case_accuracy_is_1`
- FAIL: `proposal_field_expectations_match`

## Rule Metrics

- Gold rules: 29
- Candidate rules: 72
- Verified rules: 0
- Review rules: 52
- Rejected rules: 14
- Not-used / traceability-only rules: 6
- Candidate recall: 0.55
- Verified recall: 0.00
- Verified or review recall: 0.59
- Extraction coverage recall (ceiling): 0.76
- Verifier retention rate: 0.77
- Verifier-rejected gold rules: br1_sep_001, br1_sep_002, br1_sep_003, br1_sep_004, br1_setback_006
- Not-used gold rules: br1_sep_001, br1_sep_002, br1_sep_003, br1_sep_004, br1_setback_006
- Unextracted gold rules (upstream gap): br1_fire_001, br1_fire_002, br1_fire_003, br1_heritage_001, br1_heritage_002, br1_heritage_003, br1_units_001
- Verified precision: 0.00
- Retrieval recall: n/a
- False verified rules: 0
- Source support failures: 0

## Top Review / Rejection Reasons

- `pipeline5_text_candidate_requires_review`: 72
- `unresolved_exception_cue`: 32
- `rule_object_unit_not_compatible`: 13
- `rule_family_direction_mismatch`: 10
- `upstream_extraction_requested_review`: 10
- `cross_reference_only`: 9
- `rule_object_not_supported`: 8
- `operator_not_supported`: 7
- `applies_to_not_supported`: 2
- `text_condition_not_supported`: 2

## Evidence Quality

- Evidence units: 12
- Mean evidence quality score: 1.00
- Candidate/evidence match rate: 1.00
- Candidate value grounding rate: 1.00
- Candidate unit grounding rate: 1.00
- Table context completion rate: 0.00

## Proof / Bayesian-Lite Triage

- Proof trace completion rate: 1.00
- Supported claims: 508
- Refuted claims: 1
- Not-enough-info claims: 67
- Mean evidence strength: 0.78
- High-priority review rules: 18
- Table proof rules: 0
- Complete table proofs: 0
- Partial table proofs: 0
- Refuted table proofs: 0
- Proof/decision mismatches: 0

### Top Evidence Quality Issues


## Proposal Metrics

- Proposal cases: 10
- Decision accuracy: 0.40
- Case accuracy including expected fields: 0.30
- False approvals: 0
- False rejections: 0
- Field expectation mismatches: 7
- Needs review decisions: 10

## Missed Gold Rules

- `br1_units_001`
- `br1_setback_006`
- `br1_sep_001`
- `br1_sep_002`
- `br1_sep_003`
- `br1_fire_001`
- `br1_fire_002`
- `br1_fire_003`
- `br1_heritage_001`
- `br1_heritage_002`
- `br1_heritage_003`
- `br1_sep_004`

## Proposal Results

- FAIL: `approved_verified_core_flat` -> needs_review (expected needs_review)
- FAIL: `approved_verified_core_sloping_exact` -> needs_review (expected approved)
- FAIL: `reject_flat_roof_height` -> needs_review (expected rejected)
- FAIL: `reject_front_rear_separation` -> needs_review (expected rejected)
- PASS: `reject_accessory_rear_yard` -> needs_review (expected needs_review)
- FAIL: `needs_review_lane_yard` -> needs_review (expected rejected)
- PASS: `needs_review_rear_principal_rear_yard` -> needs_review (expected needs_review)
- FAIL: `needs_review_fire_access` -> needs_review (expected rejected)
- PASS: `needs_review_heritage_coverage` -> needs_review (expected needs_review)
- FAIL: `approve_all_verified_setbacks_and_separations` -> needs_review (expected approved)
