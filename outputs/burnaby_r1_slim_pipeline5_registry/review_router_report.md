# Review Router

This file consolidates triage, evidence repair, and audit into one review queue. It does not verify rules.

## Summary

- Review rules: 63

### Action Buckets

- `operator_review`: 30
- `rerun_with_evidence_bundle`: 17
- `scope_review`: 5
- `condition_evidence_needed`: 3
- `fix_candidate_or_rule_family_mapping`: 3
- `human_legal_review`: 2
- `semantic_guardrail_review`: 1
- `semantic_duplicate_review`: 1
- `defer_low_priority`: 1

### Likelihood

- `plausible`: 25
- `weak`: 19
- `likely_correct`: 10
- `likely_wrong_or_noise`: 9

### Top Support Gaps

- `pipeline5_text_candidate_requires_review`: 41
- `applies_to_not_supported`: 24
- `text_condition_not_supported`: 18
- `rule_family_direction_mismatch`: 18
- `rule_object_not_supported`: 16
- `table_cell_candidate_requires_review`: 13
- `table_evidence_candidate_requires_review`: 13
- `operator_not_supported`: 12
- `table_applies_to_not_supported`: 10
- `table_column_not_target_scope`: 9
- `unresolved_exception_cue`: 4
- `cross_family_value_collision`: 2

### Recommendations

- Use semantic review to close out 1 likely duplicate/degraded extraction items.
- Keep 1 close semantic matches blocked until their guardrail mismatch is resolved.
- Keep 2 exception/conflict rules in human legal review.

## Top 25 Review Routes

- `burnaby_r1_021` -> `rerun_with_evidence_bundle` / `high`: Rerun using the evidence bundle; promote only if deterministic verifier passes. Check table_cell_candidate_requires_review, table_evidence_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0020__api_02. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_062 (score 0.66, blockers different_numeric_value).
- `burnaby_r1_023` -> `rerun_with_evidence_bundle` / `high`: Rerun using the evidence bundle; promote only if deterministic verifier passes. Check table_cell_candidate_requires_review, table_evidence_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0021__api_02. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_062 (score 0.62, blockers different_numeric_value).
- `burnaby_r1_025` -> `rerun_with_evidence_bundle` / `high`: Rerun using the evidence bundle; promote only if deterministic verifier passes. Check table_cell_candidate_requires_review, table_evidence_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0022__api_02. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_062 (score 0.66, blockers different_numeric_value).
- `burnaby_r1_027` -> `rerun_with_evidence_bundle` / `high`: Rerun using the evidence bundle; promote only if deterministic verifier passes. Check table_cell_candidate_requires_review, table_evidence_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0023__api_02. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_062 (score 0.71, blockers none).
- `burnaby_r1_129` -> `rerun_with_evidence_bundle` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported in page 6; evidence_id pipeline5_merged_rule_0123. Suggested stronger evidence: pipeline5_merged_rule_0118. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_047 (score 0.64, blockers different_numeric_value, exception_or_override_unresolved).
- `burnaby_r1_067` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id pipeline5_merged_rule_0061. Suggested stronger evidence: pipeline5_merged_rule_0058. Semantic match: burnaby_r1_018 (score 0.49, blockers different_direction, different_numeric_value, exception_or_override_unresolved).
- `burnaby_r1_130` -> `condition_evidence_needed` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported in page 6; evidence_id pipeline5_merged_rule_0124. Suggested stronger evidence: pipeline5_merged_rule_0127. Semantic match: burnaby_r1_057 (score 0.44, blockers different_direction, different_unit, exception_or_override_unresolved).
- `burnaby_r1_113` -> `operator_review` / `high`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch, unresolved_exception_cue in page 5; evidence_id pipeline5_merged_rule_0107. Suggested stronger evidence: pipeline5_merged_rule_0106__api_01. Semantic match: burnaby_r1_050 (score 0.57, blockers different_direction, different_numeric_value, exception_or_override_unresolved).
- `burnaby_r1_064` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 1; evidence_id pipeline5_merged_rule_0058. Suggested stronger evidence: pipeline5_merged_rule_0059__api_01. Semantic match: burnaby_r1_018 (score 0.35, blockers different_direction, different_unit, exception_or_override_unresolved).
- `burnaby_r1_134` -> `rerun_with_evidence_bundle` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported in page 6; evidence_id pipeline5_merged_rule_0128. Suggested stronger evidence: pipeline5_merged_rule_0118. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_047 (score 0.32, blockers different_direction, different_unit, exception_or_override_unresolved).
- `burnaby_r1_135` -> `condition_evidence_needed` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported in page 6; evidence_id pipeline5_merged_rule_0129. Suggested stronger evidence: pipeline5_merged_rule_0118. Semantic match: burnaby_r1_001 (score 0.30, blockers different_rule_object, exception_or_override_unresolved).
- `burnaby_r1_127` -> `rerun_with_evidence_bundle` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported in page 6; evidence_id pipeline5_merged_rule_0121. Suggested stronger evidence: pipeline5_merged_rule_0120. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_062 (score 0.27, blockers different_numeric_value, different_rule_object, different_unit, exception_or_override_unresolved).
- `burnaby_r1_126` -> `condition_evidence_needed` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported, cross_family_value_collision in page 6; evidence_id pipeline5_merged_rule_0120. Suggested stronger evidence: pipeline5_merged_rule_0121. Semantic match: burnaby_r1_062 (score 0.27, blockers different_numeric_value, different_rule_object, different_unit, exception_or_override_unresolved).
- `burnaby_r1_128` -> `operator_review` / `high`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, text_condition_not_supported, operator_not_supported, unresolved_exception_cue in page 6; evidence_id pipeline5_merged_rule_0122. Suggested stronger evidence: pipeline5_merged_rule_0118. Semantic match: burnaby_r1_039 (score 0.34, blockers different_direction, different_unit, exception_or_override_unresolved, missing_core_evidence).
- `burnaby_r1_037` -> `scope_review` / `high`: Check row/column/header/prose context for the correct legal scope. Check applies_to_not_supported, table_applies_to_not_supported, table_column_not_target_scope, table_cell_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0033. Suggested stronger evidence: pipeline5_merged_rule_0027. Semantic match: burnaby_r1_062 (score 0.29, blockers different_numeric_value, different_rule_object, different_unit).
- `burnaby_r1_063` -> `semantic_guardrail_review` / `medium`: Compare the close verified match, but do not relax verification because core legal fields or guardrails disagree. Check pipeline5_text_candidate_requires_review in page 1; evidence_id pipeline5_merged_rule_0057. Suggested stronger evidence: pipeline5_merged_rule_0056. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_062 (score 0.50, blockers different_direction, different_unit).
- `burnaby_r1_077` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch in page 4; evidence_id pipeline5_merged_rule_0072__api_01. Suggested stronger evidence: pipeline5_merged_rule_0058. Semantic match: burnaby_r1_062 (score 0.57, blockers different_direction, different_numeric_value).
- `burnaby_r1_071` -> `semantic_duplicate_review` / `medium`: Compare against the verified match; if it is only a duplicate or degraded extraction, keep it out of GIS instead of tuning the verifier. Check pipeline5_text_candidate_requires_review in page 2; evidence_id pipeline5_merged_rule_0065. Suggested stronger evidence: pipeline5_merged_rule_0062. Semantic match: burnaby_r1_054 (score 0.92, blockers none).
- `burnaby_r1_022` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check rule_family_direction_mismatch in page 2; evidence_id pipeline5_merged_rule_0021__api_01. Semantic match: burnaby_r1_062 (score 0.52, blockers different_direction, different_numeric_value).
- `burnaby_r1_024` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check rule_family_direction_mismatch in page 2; evidence_id pipeline5_merged_rule_0022__api_01. Semantic match: burnaby_r1_062 (score 0.56, blockers different_direction, different_numeric_value).
- `burnaby_r1_060` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check rule_family_direction_mismatch in page 4; evidence_id pipeline5_merged_rule_0054. Semantic match: burnaby_r1_062 (score 0.56, blockers different_direction, different_numeric_value).
- `burnaby_r1_061` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check rule_family_direction_mismatch in page 4; evidence_id pipeline5_merged_rule_0055. Semantic match: burnaby_r1_062 (score 0.57, blockers different_direction, different_numeric_value).
- `burnaby_r1_087` -> `rerun_with_evidence_bundle` / `medium`: Rerun using the evidence bundle; promote only if deterministic verifier passes. Check pipeline5_text_candidate_requires_review in page 4; evidence_id pipeline5_merged_rule_0082. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_001 (score 0.60, blockers different_direction).
- `burnaby_r1_026` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check rule_family_direction_mismatch in page 2; evidence_id pipeline5_merged_rule_0023__api_01. Semantic match: burnaby_r1_062 (score 0.53, blockers different_direction, different_numeric_value).
- `burnaby_r1_099` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 5; evidence_id pipeline5_merged_rule_0094. Semantic match: burnaby_r1_001 (score 0.56, blockers different_direction).
