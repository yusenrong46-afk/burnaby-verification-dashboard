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
- Candidate rules: 32
- Verified rules: 12
- Review rules: 11
- Rejected rules: 9
- Not-used / traceability-only rules: 0
- Candidate recall: 1.00
- Verified recall: 1.00
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

- `pipeline5_text_candidate_requires_review`: 19
- `rule_object_not_supported`: 14
- `rule_family_direction_mismatch`: 10
- `rule_object_unit_not_compatible`: 9
- `coefficient_operand_not_value`: 6
- `operator_not_supported`: 6
- `applies_to_not_supported`: 4
- `unresolved_exception_cue`: 4
- `enumerated_branch_condition_missing`: 2
- `unit_not_found_in_evidence`: 1

## Evidence Quality

- Evidence units: 32
- Mean evidence quality score: 0.98
- Candidate/evidence match rate: 1.00
- Candidate value grounding rate: 1.00
- Candidate unit grounding rate: 0.97
- Table context completion rate: 0.00

## Proof / Bayesian-Lite Triage

- Proof trace completion rate: 1.00
- Supported claims: 212
- Refuted claims: 1
- Not-enough-info claims: 43
- Mean evidence strength: 0.71
- High-priority review rules: 0
- Table proof rules: 0
- Complete table proofs: 0
- Partial table proofs: 0
- Refuted table proofs: 0
- Proof/decision mismatches: 0

### Top Evidence Quality Issues

- `evidence_text_not_in_source_context`: 3

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

