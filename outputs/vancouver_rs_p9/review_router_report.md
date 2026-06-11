# Review Router

This file consolidates triage, evidence repair, and audit into one review queue. It does not verify rules.

## Summary

- Review rules: 22

### Action Buckets

- `operator_review`: 10
- `defer_low_priority`: 6
- `fix_candidate_or_rule_family_mapping`: 3
- `scope_review`: 1
- `rerun_with_evidence_bundle`: 1
- `human_legal_review`: 1

### Likelihood

- `plausible`: 10
- `weak`: 5
- `likely_wrong_or_noise`: 4
- `likely_correct`: 3

### Top Support Gaps

- `pipeline5_text_candidate_requires_review`: 21
- `operator_not_supported`: 9
- `rule_object_not_supported`: 7
- `applies_to_not_supported`: 5
- `upstream_extraction_requested_review`: 2
- `unresolved_exception_cue`: 1
- `rule_family_direction_mismatch`: 1
- `text_condition_not_supported`: 1

### Recommendations

- Keep 1 exception/conflict rules in human legal review.

## Top 25 Review Routes

- `vancouver_rs_035` -> `scope_review` / `high`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, unresolved_exception_cue in page 9; evidence_id vancouver_generic_graph_pack_009__page_0009__local_012. Suggested stronger evidence: vancouver_generic_graph_pack_009__page_0009__local_010. Semantic match: vancouver_rs_020 (score 0.71, blockers different_numeric_value, exception_or_override_unresolved).
- `vancouver_rs_027` -> `rerun_with_evidence_bundle` / `medium`: Rerun using the evidence bundle; promote only if deterministic verifier passes. Check pipeline5_text_candidate_requires_review in page 9; evidence_id vancouver_generic_graph_pack_009__page_0009__local_003. Suggested stronger evidence: vancouver_generic_graph_pack_006__page_0008__local_005. Evidence bundle is safe to rerun through the verifier. Semantic match: vancouver_rs_021 (score 0.27, blockers different_direction, different_rule_object, different_unit).
- `vancouver_rs_009` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 18; evidence_id vancouver_generic_graph_pack_022__page_0018__local_010. Semantic match: vancouver_rs_021 (score 0.13, blockers different_direction, different_rule_object, different_unit).
- `vancouver_rs_022` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check upstream_extraction_requested_review in page 8; evidence_id vancouver_generic_graph_pack_007__page_0008__local_013. Semantic match: vancouver_rs_021 (score 0.33, blockers different_numeric_value, different_rule_object, different_unit).
- `vancouver_rs_005` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 10; evidence_id vancouver_generic_graph_pack_014__page_0010__local_002. Semantic match: vancouver_rs_021 (score 0.18, blockers different_direction, different_rule_object, different_unit).
- `vancouver_rs_012` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 8; evidence_id vancouver_generic_graph_pack_007__page_0008__local_002. Suggested stronger evidence: vancouver_generic_graph_pack_007__page_0008__local_003. Semantic match: vancouver_rs_021 (score 0.16, blockers different_direction, different_rule_object, different_unit).
- `vancouver_rs_015` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 8; evidence_id vancouver_generic_graph_pack_007__page_0008__local_007. Suggested stronger evidence: vancouver_generic_graph_pack_006__page_0008__local_005. Semantic match: vancouver_rs_020 (score 0.37, blockers different_rule_object, different_unit).
- `vancouver_rs_001` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 8; evidence_id vancouver_generic_graph_pack_006__page_0008__local_005. Semantic match: vancouver_rs_021 (score 0.22, blockers different_direction, different_rule_object, different_unit).
- `vancouver_rs_030` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch in page 9; evidence_id vancouver_generic_graph_pack_009__page_0009__local_007. Suggested stronger evidence: vancouver_generic_graph_pack_009__page_0009__local_004. Semantic match: vancouver_rs_021 (score 0.34, blockers different_direction, different_rule_object, different_unit, exception_or_override_unresolved).
- `vancouver_rs_033` -> `human_legal_review` / `medium`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review in page 9; evidence_id vancouver_generic_graph_pack_009__page_0009__local_010. Suggested stronger evidence: vancouver_generic_graph_pack_007__page_0008__local_007. Semantic match: vancouver_rs_020 (score 0.42, blockers different_rule_object, different_unit, exception_or_override_unresolved).
- `vancouver_rs_041` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported in page 9; evidence_id vancouver_generic_graph_pack_009__page_0009__local_018. Suggested stronger evidence: vancouver_generic_graph_pack_009__page_0009__local_013. Semantic match: vancouver_rs_020 (score 0.65, blockers different_numeric_value, exception_or_override_unresolved, missing_core_evidence).
- `vancouver_rs_042` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported in page 9; evidence_id vancouver_generic_graph_pack_009__page_0009__local_019. Suggested stronger evidence: vancouver_generic_graph_pack_009__page_0009__local_013. Semantic match: vancouver_rs_020 (score 0.65, blockers different_numeric_value, exception_or_override_unresolved, missing_core_evidence).
- `vancouver_rs_010` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported in page 9; evidence_id vancouver_generic_graph_pack_011__page_0009__local_020. Semantic match: vancouver_rs_021 (score 0.16, blockers different_direction, different_rule_object, different_unit, missing_core_evidence).
- `vancouver_rs_011` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported in page 9; evidence_id vancouver_generic_graph_pack_011__page_0009__local_020. Semantic match: vancouver_rs_021 (score 0.17, blockers different_direction, different_rule_object, different_unit, missing_core_evidence).
- `vancouver_rs_040` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported in page 9; evidence_id vancouver_generic_graph_pack_009__page_0009__local_017. Suggested stronger evidence: vancouver_generic_graph_pack_009__page_0009__local_013. Semantic match: vancouver_rs_021 (score 0.24, blockers different_direction, different_rule_object, different_unit, missing_core_evidence).
- `vancouver_rs_028` -> `fix_candidate_or_rule_family_mapping` / `low`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, rule_object_not_supported in page 9; evidence_id vancouver_generic_graph_pack_009__page_0009__local_004. Suggested stronger evidence: vancouver_generic_graph_pack_009__page_0009__local_003. Evidence bundle is safe to rerun through the verifier. Semantic match: vancouver_rs_021 (score 0.23, blockers different_direction, different_rule_object, different_unit).
- `vancouver_rs_019` -> `fix_candidate_or_rule_family_mapping` / `low`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, rule_object_not_supported in page 8; evidence_id vancouver_generic_graph_pack_007__page_0008__local_011. Suggested stronger evidence: vancouver_generic_graph_pack_006__page_0008__local_005. Semantic match: vancouver_rs_021 (score 0.24, blockers different_direction, different_rule_object, different_unit).
- `vancouver_rs_036` -> `fix_candidate_or_rule_family_mapping` / `low`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, text_condition_not_supported, rule_object_not_supported in page 9; evidence_id vancouver_generic_graph_pack_009__page_0009__local_013. Suggested stronger evidence: vancouver_generic_graph_pack_009__page_0009__local_012. Semantic match: vancouver_rs_021 (score 0.22, blockers different_direction, different_rule_object, different_unit, exception_or_override_unresolved).
- `vancouver_rs_004` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, applies_to_not_supported, operator_not_supported in page 8; evidence_id vancouver_generic_graph_pack_006__page_0008__local_017. Suggested stronger evidence: vancouver_generic_graph_pack_006__page_0008__local_015. Semantic match: vancouver_rs_020 (score 0.30, blockers different_direction, different_numeric_value, different_rule_object, missing_core_evidence).
- `vancouver_rs_002` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, operator_not_supported, rule_object_not_supported in page 8; evidence_id vancouver_generic_graph_pack_006__page_0008__local_015. Suggested stronger evidence: vancouver_generic_graph_pack_006__page_0008__local_016. Semantic match: vancouver_rs_020 (score 0.39, blockers different_direction, different_numeric_value, different_rule_object, missing_core_evidence).
- `vancouver_rs_003` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, operator_not_supported, rule_object_not_supported in page 8; evidence_id vancouver_generic_graph_pack_006__page_0008__local_016. Suggested stronger evidence: vancouver_generic_graph_pack_006__page_0008__local_015. Semantic match: vancouver_rs_020 (score 0.31, blockers different_direction, different_numeric_value, different_rule_object, missing_core_evidence).
- `vancouver_rs_016` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, operator_not_supported, rule_object_not_supported in page 8; evidence_id vancouver_generic_graph_pack_007__page_0008__local_008. Suggested stronger evidence: vancouver_generic_graph_pack_006__page_0008__local_005. Semantic match: vancouver_rs_020 (score 0.37, blockers different_numeric_value, different_rule_object, different_unit, missing_core_evidence).
