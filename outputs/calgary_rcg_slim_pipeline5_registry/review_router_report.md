# Review Router

This file consolidates triage, evidence repair, and audit into one review queue. It does not verify rules.

## Summary

- Review rules: 14

### Action Buckets

- `operator_review`: 6
- `rerun_with_evidence_bundle`: 6
- `scope_review`: 2

### Likelihood

- `plausible`: 7
- `weak`: 6
- `likely_wrong_or_noise`: 1

### Top Support Gaps

- `pipeline5_text_candidate_requires_review`: 14
- `applies_to_not_supported`: 10
- `operator_not_supported`: 6
- `constraint_scope_not_supported`: 6
- `unresolved_exception_cue`: 3

### Recommendations

- No immediate recommendation.

## Top 25 Review Routes

- `calgary_rcg_014` -> `scope_review` / `high`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, unresolved_exception_cue in page 396; section 352(5); evidence_id local_merged_rule_0014. Suggested stronger evidence: local_merged_rule_0015. Semantic match: calgary_rcg_011 (score 0.29, blockers different_numeric_value, different_rule_object, different_unit, exception_or_override_unresolved).
- `calgary_rcg_015` -> `scope_review` / `high`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, unresolved_exception_cue in page 396; section 352(5); evidence_id local_merged_rule_0015. Suggested stronger evidence: local_merged_rule_0014. Semantic match: calgary_rcg_011 (score 0.28, blockers different_numeric_value, different_rule_object, different_unit, exception_or_override_unresolved).
- `calgary_rcg_001` -> `operator_review` / `high`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported, unresolved_exception_cue in page 395; section 351(2); evidence_id local_merged_rule_0001. Suggested stronger evidence: local_merged_rule_0002. Semantic match: calgary_rcg_011 (score 0.28, blockers different_numeric_value, different_rule_object, different_unit, exception_or_override_unresolved, missing_core_evidence).
- `calgary_rcg_007` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 396; section 352(3.2); evidence_id local_merged_rule_0007. Suggested stronger evidence: local_merged_rule_0008. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_006 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_009` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 396; section 352(3.2); evidence_id local_merged_rule_0009. Suggested stronger evidence: local_merged_rule_0007. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_006 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_013` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, constraint_scope_not_supported in page 396; section 352(4.1); evidence_id local_merged_rule_0013. Suggested stronger evidence: local_merged_rule_0010. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_010 (score 0.88, blockers none).
- `calgary_rcg_022` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, constraint_scope_not_supported in page 398; section 358(3); evidence_id local_merged_rule_0022. Suggested stronger evidence: local_merged_rule_0017. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_004 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_018` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, constraint_scope_not_supported in page 397; section 352(8); evidence_id local_merged_rule_0018. Suggested stronger evidence: local_merged_rule_0017. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_004 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_019` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, constraint_scope_not_supported in page 397; section 352(8); evidence_id local_merged_rule_0019. Suggested stronger evidence: local_merged_rule_0017. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_004 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_024` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported in page 399; section 360(3); evidence_id local_merged_rule_0024. Suggested stronger evidence: local_merged_rule_0023. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_010 (score 0.71, blockers different_numeric_value, missing_core_evidence).
- `calgary_rcg_023` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported in page 399; section 360(2); evidence_id local_merged_rule_0023. Suggested stronger evidence: local_merged_rule_0024. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_010 (score 0.71, blockers different_numeric_value, missing_core_evidence).
- `calgary_rcg_017` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported in page 397; section 352(8); evidence_id local_merged_rule_0017. Suggested stronger evidence: local_merged_rule_0018. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_004 (score 0.71, blockers different_numeric_value, missing_core_evidence).
- `calgary_rcg_012` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, constraint_scope_not_supported, operator_not_supported in page 396; section 352(4.1); evidence_id local_merged_rule_0012. Suggested stronger evidence: local_merged_rule_0011. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_010 (score 0.71, blockers different_numeric_value, missing_core_evidence).
- `calgary_rcg_005` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, constraint_scope_not_supported, operator_not_supported in page 395; section 352(1); evidence_id local_merged_rule_0005. Suggested stronger evidence: local_merged_rule_0004. Semantic match: calgary_rcg_004 (score 0.71, blockers different_numeric_value, missing_core_evidence).
