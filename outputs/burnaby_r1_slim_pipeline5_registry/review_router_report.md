# Review Router

This file consolidates triage, evidence repair, and audit into one review queue. It does not verify rules.

## Summary

- Review rules: 63

### Action Buckets

- `operator_review`: 32
- `rerun_with_evidence_bundle`: 15
- `defer_low_priority`: 6
- `condition_evidence_needed`: 4
- `semantic_duplicate_review`: 2
- `fix_candidate_or_rule_family_mapping`: 2
- `scope_review`: 1
- `human_legal_review`: 1

### Likelihood

- `plausible`: 25
- `weak`: 19
- `likely_correct`: 10
- `likely_wrong_or_noise`: 9

### Top Support Gaps

- `pipeline5_text_candidate_requires_review`: 40
- `text_condition_not_supported`: 24
- `applies_to_not_supported`: 24
- `rule_family_direction_mismatch`: 18
- `operator_not_supported`: 18
- `table_cell_candidate_requires_review`: 15
- `table_evidence_candidate_requires_review`: 15
- `rule_object_not_supported`: 13
- `table_applies_to_not_supported`: 10
- `table_column_not_target_scope`: 9
- `constraint_scope_not_supported`: 4
- `cross_family_value_collision`: 2

### Recommendations

- Use semantic review to close out 2 likely duplicate/degraded extraction items.
- Keep 1 exception/conflict rules in human legal review.

## Top 25 Review Routes

- `burnaby_r1_055` -> `semantic_duplicate_review` / `high`: Compare against the verified match; if it is only a duplicate or degraded extraction, keep it out of GIS instead of tuning the verifier. Check table_cell_candidate_requires_review, table_evidence_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0049. Semantic match: burnaby_r1_054 (score 0.92, blockers none).
- `burnaby_r1_047` -> `defer_low_priority` / `high`: Keep in review until more evidence or a general verifier rule is justified. Check table_cell_candidate_requires_review, table_evidence_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0043. Semantic match: burnaby_r1_049 (score 0.79, blockers none).
- `burnaby_r1_021` -> `defer_low_priority` / `high`: Keep in review until more evidence or a general verifier rule is justified. Check table_cell_candidate_requires_review, table_evidence_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0020__api_02. Semantic match: burnaby_r1_062 (score 0.66, blockers different_numeric_value).
- `burnaby_r1_023` -> `defer_low_priority` / `high`: Keep in review until more evidence or a general verifier rule is justified. Check table_cell_candidate_requires_review, table_evidence_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0021__api_02. Semantic match: burnaby_r1_062 (score 0.62, blockers different_numeric_value).
- `burnaby_r1_025` -> `defer_low_priority` / `high`: Keep in review until more evidence or a general verifier rule is justified. Check table_cell_candidate_requires_review, table_evidence_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0022__api_02. Semantic match: burnaby_r1_062 (score 0.66, blockers different_numeric_value).
- `burnaby_r1_129` -> `rerun_with_evidence_bundle` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported in page 6; evidence_id pipeline5_merged_rule_0123. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_050 (score 0.64, blockers different_numeric_value, exception_or_override_unresolved).
- `burnaby_r1_130` -> `rerun_with_evidence_bundle` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported in page 6; evidence_id pipeline5_merged_rule_0124. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_075 (score 0.46, blockers different_direction, different_unit, exception_or_override_unresolved).
- `burnaby_r1_121` -> `condition_evidence_needed` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported in page 6; evidence_id pipeline5_merged_rule_0115. Suggested stronger evidence: pipeline5_merged_rule_0079. Semantic match: burnaby_r1_120 (score 0.40, blockers different_direction, different_unit, exception_or_override_unresolved).
- `burnaby_r1_134` -> `condition_evidence_needed` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported in page 6; evidence_id pipeline5_merged_rule_0128. Suggested stronger evidence: pipeline5_merged_rule_0106__api_01. Semantic match: burnaby_r1_050 (score 0.32, blockers different_direction, different_unit, exception_or_override_unresolved).
- `burnaby_r1_135` -> `condition_evidence_needed` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported in page 6; evidence_id pipeline5_merged_rule_0129. Suggested stronger evidence: pipeline5_merged_rule_0106__api_01. Semantic match: burnaby_r1_001 (score 0.30, blockers different_rule_object, exception_or_override_unresolved).
- `burnaby_r1_127` -> `rerun_with_evidence_bundle` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported in page 6; evidence_id pipeline5_merged_rule_0121. Suggested stronger evidence: pipeline5_merged_rule_0120. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_062 (score 0.27, blockers different_numeric_value, different_rule_object, different_unit, exception_or_override_unresolved).
- `burnaby_r1_027` -> `rerun_with_evidence_bundle` / `high`: Find the clause or table header that proves the condition. Check text_condition_not_supported, table_cell_candidate_requires_review, table_evidence_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0023__api_02. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_062 (score 0.71, blockers none).
- `burnaby_r1_109` -> `operator_review` / `high`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, text_condition_not_supported, rule_family_direction_mismatch, applies_to_not_supported in page 5; evidence_id pipeline5_merged_rule_0104. Suggested stronger evidence: pipeline5_merged_rule_0105. Semantic match: burnaby_r1_059 (score 0.69, blockers different_direction, different_numeric_value).
- `burnaby_r1_126` -> `condition_evidence_needed` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported, cross_family_value_collision in page 6; evidence_id pipeline5_merged_rule_0120. Suggested stronger evidence: pipeline5_merged_rule_0121. Semantic match: burnaby_r1_062 (score 0.27, blockers different_numeric_value, different_rule_object, different_unit, exception_or_override_unresolved).
- `burnaby_r1_037` -> `scope_review` / `high`: Check row/column/header/prose context for the correct legal scope. Check applies_to_not_supported, table_applies_to_not_supported, table_column_not_target_scope, table_cell_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0033. Suggested stronger evidence: pipeline5_merged_rule_0120. Semantic match: burnaby_r1_062 (score 0.29, blockers different_numeric_value, different_rule_object, different_unit).
- `burnaby_r1_063` -> `rerun_with_evidence_bundle` / `medium`: Rerun using the evidence bundle; promote only if deterministic verifier passes. Check pipeline5_text_candidate_requires_review in page 1; evidence_id pipeline5_merged_rule_0057. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_062 (score 0.50, blockers different_direction, different_unit).
- `burnaby_r1_067` -> `human_legal_review` / `medium`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0061. Semantic match: burnaby_r1_028 (score 0.49, blockers different_direction, different_numeric_value, exception_or_override_unresolved).
- `burnaby_r1_071` -> `semantic_duplicate_review` / `medium`: Compare against the verified match; if it is only a duplicate or degraded extraction, keep it out of GIS instead of tuning the verifier. Check pipeline5_text_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0065. Suggested stronger evidence: pipeline5_merged_rule_0048__api_01. Semantic match: burnaby_r1_054 (score 0.92, blockers none).
- `burnaby_r1_060` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check rule_family_direction_mismatch in page 4; evidence_id pipeline5_merged_rule_0054. Semantic match: burnaby_r1_062 (score 0.56, blockers different_direction, different_numeric_value).
- `burnaby_r1_061` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check rule_family_direction_mismatch in page 4; evidence_id pipeline5_merged_rule_0055. Semantic match: burnaby_r1_062 (score 0.57, blockers different_direction, different_numeric_value).
- `burnaby_r1_087` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 4; evidence_id pipeline5_merged_rule_0082. Semantic match: burnaby_r1_001 (score 0.60, blockers different_direction).
- `burnaby_r1_077` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch in page 4; evidence_id pipeline5_merged_rule_0072__api_01. Suggested stronger evidence: pipeline5_merged_rule_0073. Semantic match: burnaby_r1_062 (score 0.57, blockers different_direction, different_numeric_value).
- `burnaby_r1_113` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch in page 5; evidence_id pipeline5_merged_rule_0107. Suggested stronger evidence: pipeline5_merged_rule_0106__api_01. Semantic match: burnaby_r1_050 (score 0.57, blockers different_direction, different_numeric_value).
- `burnaby_r1_111` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 5; evidence_id pipeline5_merged_rule_0106__api_01. Semantic match: burnaby_r1_051 (score 0.35, blockers different_direction, different_numeric_value, different_unit).
- `burnaby_r1_019` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check rule_family_direction_mismatch, table_column_not_target_scope, table_cell_candidate_requires_review, table_evidence_candidate_requires_review in page 1; evidence_id pipeline5_merged_rule_0019. Suggested stronger evidence: pipeline5_merged_rule_0061. Semantic match: burnaby_r1_018 (score 0.53, blockers different_direction, different_numeric_value).
