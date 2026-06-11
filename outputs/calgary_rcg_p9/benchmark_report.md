# calgary_rcg Benchmark Report

## Quality Gates

- FAIL: `verified_precision_is_1`
- FAIL: `false_verified_is_0`
- PASS: `false_approval_is_0`
- PASS: `retrieval_recall_at_least_0_95`
- FAIL: `verified_or_review_recall_at_least_0_90`
- PASS: `verified_source_support_failures_is_0`

## Rule Metrics

- Gold rules: 8
- Candidate rules: 428
- Verified rules: 16
- Review rules: 348
- Rejected rules: 56
- Not-used / traceability-only rules: 8
- Candidate recall: 0.62
- Verified recall: 0.25
- Verified or review recall: 0.75
- Extraction coverage recall (ceiling): 0.75
- Verifier retention rate: 1.00
- Verifier-rejected gold rules: none
- Not-used gold rules: none
- Unextracted gold rules (upstream gap): cal_height_side_edge_001, cal_setback_front_deemed_001
- Verified precision: 0.25
- Retrieval recall: n/a
- False verified rules: 12
- Source support failures: 0

## Top Review / Rejection Reasons

- `pipeline5_text_candidate_requires_review`: 401
- `operator_not_supported`: 186
- `upstream_extraction_requested_review`: 82
- `rule_object_not_supported`: 69
- `rule_family_direction_mismatch`: 56
- `rule_object_unit_not_compatible`: 46
- `unresolved_exception_cue`: 38
- `applies_to_not_supported`: 36
- `value_not_found_in_evidence`: 10
- `outside_current_rule_contract`: 8

## Evidence Quality

- Evidence units: 152
- Mean evidence quality score: 0.99
- Candidate/evidence match rate: 1.00
- Candidate value grounding rate: 0.98
- Candidate unit grounding rate: 0.74
- Table context completion rate: 0.00

## Proof / Bayesian-Lite Triage

- Proof trace completion rate: 1.00
- Supported claims: 2987
- Refuted claims: 14
- Not-enough-info claims: 423
- Mean evidence strength: 0.76
- High-priority review rules: 30
- Table proof rules: 0
- Complete table proofs: 0
- Partial table proofs: 0
- Refuted table proofs: 0
- Proof/decision mismatches: 0

### Top Evidence Quality Issues

- `evidence_text_not_in_source_context`: 9

## Proposal Metrics

- Proposal cases: 0
- Decision accuracy: 0.00
- Case accuracy including expected fields: 0.00
- False approvals: 0
- False rejections: 0
- Field expectation mismatches: 0
- Needs review decisions: 0

## Missed Gold Rules

- `cal_height_side_edge_001`
- `cal_setback_front_deemed_001`

## Proposal Results

