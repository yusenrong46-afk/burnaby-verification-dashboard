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
- Candidate rules: 45
- Verified rules: 5
- Review rules: 15
- Rejected rules: 9
- Not-used / traceability-only rules: 16
- Candidate recall: 0.86
- Verified recall: 0.57
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
- `rule_object_not_supported`: 27
- `outside_current_rule_contract`: 18
- `applies_to_not_supported`: 17
- `operator_not_supported`: 17
- `rule_object_unit_not_compatible`: 6
- `constraint_scope_not_supported`: 5
- `unresolved_exception_cue`: 4
- `unit_not_found_in_evidence`: 2
- `non_numeric_value_for_numeric_rule`: 1

## Evidence Quality

- Evidence units: 41
- Mean evidence quality score: 1.00
- Candidate/evidence match rate: 1.00
- Candidate value grounding rate: 0.98
- Candidate unit grounding rate: 0.96
- Table context completion rate: 0.00

## Proof / Bayesian-Lite Triage

- Proof trace completion rate: 1.00
- Supported claims: 287
- Refuted claims: 3
- Not-enough-info claims: 70
- Mean evidence strength: 0.66
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

