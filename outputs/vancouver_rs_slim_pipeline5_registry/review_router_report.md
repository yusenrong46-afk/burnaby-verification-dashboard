# Review Router

This file consolidates triage, evidence repair, and audit into one review queue. It does not verify rules.

## Summary

- Review rules: 15

### Action Buckets

- `operator_review`: 10
- `fix_candidate_or_rule_family_mapping`: 2
- `scope_review`: 1
- `semantic_guardrail_review`: 1
- `defer_low_priority`: 1

### Likelihood

- `likely_wrong_or_noise`: 6
- `plausible`: 5
- `weak`: 2
- `likely_correct`: 2

### Top Support Gaps

- `pipeline5_text_candidate_requires_review`: 15
- `operator_not_supported`: 10
- `rule_object_not_supported`: 8
- `applies_to_not_supported`: 5
- `constraint_scope_not_supported`: 2
- `unresolved_exception_cue`: 1

### Recommendations

- Keep 1 close semantic matches blocked until their guardrail mismatch is resolved.

## Top 25 Review Routes

- `vancouver_rs_036` -> `scope_review` / `high`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, unresolved_exception_cue in page 9.0; evidence_id vancouver_section_11_2026_02__11_3_8_8__0009__unit_001__ev_text_012. Suggested stronger evidence: vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_heading_plus_clause_012_1. Semantic match: vancouver_rs_013 (score 0.57, blockers different_unit, exception_or_override_unresolved).
- `vancouver_rs_005` -> `semantic_guardrail_review` / `medium`: Compare the close verified match, but do not relax verification because core legal fields or guardrails disagree. Check pipeline5_text_candidate_requires_review in page 8.0; evidence_id vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_heading_plus_clause_004_2. Suggested stronger evidence: vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_heading_plus_clause_006_1. Evidence bundle is safe to rerun through the verifier. Semantic match: vancouver_rs_007 (score 0.64, blockers different_unit).
- `vancouver_rs_024` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 9.0; evidence_id vancouver_section_11_2026_02__11_3_8_8__0009__unit_001__ev_text_002. Suggested stronger evidence: vancouver_section_11_2026_02__11_3_8_8__0009__unit_001__ev_heading_plus_clause_006_2. Semantic match: vancouver_rs_007 (score 0.47, blockers different_direction, different_unit).
- `vancouver_rs_028` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported in page 9.0; evidence_id vancouver_section_11_2026_02__11_3_8_8__0009__unit_001__ev_text_006. Semantic match: vancouver_rs_007 (score 0.47, blockers different_direction, different_unit, missing_core_evidence).
- `vancouver_rs_027` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported in page 9.0; evidence_id vancouver_section_11_2026_02__11_3_8_8__0009__unit_001__ev_text_005. Suggested stronger evidence: vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_heading_plus_clause_012_1. Evidence bundle is safe to rerun through the verifier. Semantic match: vancouver_rs_013 (score 0.55, blockers different_numeric_value, missing_core_evidence).
- `vancouver_rs_001` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported in page 8.0; evidence_id vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_text_002. Semantic match: vancouver_rs_007 (score 0.34, blockers different_direction, different_unit, missing_core_evidence).
- `vancouver_rs_016` -> `fix_candidate_or_rule_family_mapping` / `low`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, rule_object_not_supported in page 8.0; evidence_id vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_heading_plus_clause_014_1. Semantic match: vancouver_rs_013 (score 0.38, blockers different_direction, different_numeric_value, different_rule_object).
- `vancouver_rs_017` -> `fix_candidate_or_rule_family_mapping` / `low`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, rule_object_not_supported in page 8.0; evidence_id vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_heading_plus_clause_014_2. Semantic match: vancouver_rs_013 (score 0.33, blockers different_direction, different_numeric_value, different_rule_object).
- `vancouver_rs_003` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, constraint_scope_not_supported, operator_not_supported in page 8.0; evidence_id vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_text_004. Suggested stronger evidence: vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_heading_plus_clause_004_1. Semantic match: vancouver_rs_007 (score 0.23, blockers different_direction, different_rule_object, different_unit, missing_core_evidence).
- `vancouver_rs_025` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported, rule_object_not_supported in page 9.0; evidence_id vancouver_section_11_2026_02__11_3_8_8__0009__unit_001__ev_text_003. Suggested stronger evidence: vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_heading_plus_clause_004_2. Semantic match: vancouver_rs_007 (score 0.37, blockers different_direction, different_unit, missing_core_evidence).
- `vancouver_rs_026` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported, rule_object_not_supported in page 9.0; evidence_id vancouver_section_11_2026_02__11_3_8_8__0009__unit_001__ev_text_004. Suggested stronger evidence: vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_heading_plus_clause_004_2. Semantic match: vancouver_rs_007 (score 0.33, blockers different_direction, different_unit, missing_core_evidence).
- `vancouver_rs_018` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, operator_not_supported, rule_object_not_supported in page 8.0; evidence_id vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_text_015. Suggested stronger evidence: vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_heading_plus_clause_014_1. Semantic match: vancouver_rs_013 (score 0.38, blockers different_direction, different_numeric_value, different_rule_object, missing_core_evidence).
- `vancouver_rs_019` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, operator_not_supported, rule_object_not_supported in page 8.0; evidence_id vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_text_016. Suggested stronger evidence: vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_heading_plus_clause_014_2. Semantic match: vancouver_rs_013 (score 0.33, blockers different_direction, different_numeric_value, different_rule_object, missing_core_evidence).
- `vancouver_rs_020` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, operator_not_supported, rule_object_not_supported in page 8.0; evidence_id vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_text_017. Semantic match: vancouver_rs_013 (score 0.31, blockers different_direction, different_numeric_value, different_rule_object, missing_core_evidence).
- `vancouver_rs_009` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, constraint_scope_not_supported, operator_not_supported in page 8.0; evidence_id vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_text_008. Suggested stronger evidence: vancouver_section_11_2026_02__11_3_7_1__0008__unit_001__ev_heading_plus_clause_006_2. Evidence bundle is safe to rerun through the verifier. Semantic match: vancouver_rs_007 (score 0.71, blockers missing_core_evidence).
