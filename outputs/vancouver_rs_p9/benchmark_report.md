# vancouver_rs Benchmark Report

## Quality Gates

- PASS: `verified_precision_is_1`
- PASS: `false_verified_is_0`
- PASS: `false_approval_is_0`
- PASS: `retrieval_recall_at_least_0_95`
- PASS: `verified_or_review_recall_at_least_0_90`
- PASS: `verified_source_support_failures_is_0`

## Rule Metrics

- Gold rules: 7
- Candidate rules: 43
- Verified rules: 2
- Review rules: 22
- Rejected rules: 13
- Not-used / traceability-only rules: 6
- Candidate recall: 0.57
- Verified recall: 0.29
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

- `pipeline5_text_candidate_requires_review`: 40
- `rule_object_not_supported`: 19
- `operator_not_supported`: 12
- `rule_object_unit_not_compatible`: 11
- `outside_current_rule_contract`: 8
- `applies_to_not_supported`: 7
- `rule_family_direction_mismatch`: 7
- `text_condition_not_supported`: 4
- `unresolved_exception_cue`: 4
- `upstream_extraction_requested_review`: 4

## Evidence Quality

- Evidence units: 35
- Mean evidence quality score: 1.00
- Candidate/evidence match rate: 1.00
- Candidate value grounding rate: 1.00
- Candidate unit grounding rate: 0.95
- Table context completion rate: 0.00

## Proof / Bayesian-Lite Triage

- Proof trace completion rate: 1.00
- Supported claims: 273
- Refuted claims: 2
- Not-enough-info claims: 69
- Mean evidence strength: 0.68
- High-priority review rules: 1
- Table proof rules: 0
- Complete table proofs: 0
- Partial table proofs: 0
- Refuted table proofs: 0
- Proof/decision mismatches: 0

### Top Evidence Quality Issues


## Proposal Metrics

- Proposal cases: 0
- Decision accuracy: 0.00
- Case accuracy including expected fields: 0.00
- False approvals: 0
- False rejections: 0
- Field expectation mismatches: 0
- Needs review decisions: 0

## Missed Gold Rules


## Proposal Results

