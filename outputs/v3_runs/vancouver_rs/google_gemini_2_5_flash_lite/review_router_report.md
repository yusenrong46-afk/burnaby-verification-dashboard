# Review Router

This file consolidates triage, evidence repair, and audit into one review queue. It does not verify rules.

## Summary

- Review rules: 11

### Action Buckets

- `operator_review`: 9
- `semantic_guardrail_review`: 1
- `fix_candidate_or_rule_family_mapping`: 1

### Likelihood

- `plausible`: 5
- `likely_wrong_or_noise`: 5
- `likely_correct`: 1

### Top Support Gaps

- `pipeline5_text_candidate_requires_review`: 10
- `rule_object_not_supported`: 10
- `rule_family_direction_mismatch`: 7
- `operator_not_supported`: 5
- `applies_to_not_supported`: 4
- `coefficient_operand_not_value`: 1

### Recommendations

- Keep 1 close semantic matches blocked until their guardrail mismatch is resolved.

## Top 25 Review Routes

- `vancouver_rs_022` -> `semantic_guardrail_review` / `medium`: Compare the close verified match, but do not relax verification because core legal fields or guardrails disagree. Check coefficient_operand_not_value in page 8; section 11.3.8.2; evidence_id v3_repair_pack_0004_ev_001. Semantic match: vancouver_rs_009 (score 0.71, blockers different_numeric_value).
- `vancouver_rs_011` -> `fix_candidate_or_rule_family_mapping` / `low`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, rule_object_not_supported in page 8; section 11.3.8.6; evidence_id v3_pack_0007_ev_001. Semantic match: vancouver_rs_017 (score 0.69, blockers different_numeric_value).
- `vancouver_rs_004` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch, rule_object_not_supported in page 8; section 11.3.8.7; evidence_id v3_pack_0002_ev_001. Semantic match: vancouver_rs_009 (score 0.54, blockers different_direction, different_numeric_value).
- `vancouver_rs_005` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch, rule_object_not_supported in page 8; section 11.3.8.7; evidence_id v3_pack_0002_ev_002. Suggested stronger evidence: v3_pack_0004_ev_001. Semantic match: vancouver_rs_009 (score 0.54, blockers different_direction, different_numeric_value).
- `vancouver_rs_020` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch, rule_object_not_supported in page 8; section 11.3.8.7; evidence_id v3_repair_pack_0001_ev_001. Semantic match: vancouver_rs_009 (score 0.54, blockers different_direction, different_numeric_value, exception_or_override_unresolved).
- `vancouver_rs_021` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch, rule_object_not_supported in page 8; section 11.3.8.7; evidence_id v3_repair_pack_0001_ev_002. Suggested stronger evidence: v3_pack_0004_ev_001. Semantic match: vancouver_rs_009 (score 0.54, blockers different_direction, different_numeric_value, exception_or_override_unresolved).
- `vancouver_rs_024` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch, operator_not_supported, rule_object_not_supported in page 8; section 11.3.8.6; evidence_id v3_repair_pack_0006_ev_001. Suggested stronger evidence: v3_pack_0003_ev_001. Semantic match: vancouver_rs_017 (score 0.53, blockers different_direction, different_numeric_value, missing_core_evidence).
- `vancouver_rs_013` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, operator_not_supported, rule_object_not_supported in page 8; section 11.3.8.6; evidence_id v3_pack_0007_ev_003. Suggested stronger evidence: v3_pack_0002_ev_001. Semantic match: vancouver_rs_018 (score 0.71, blockers missing_core_evidence).
- `vancouver_rs_026` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch, applies_to_not_supported, operator_not_supported in page 8; section 11.3.8.6; evidence_id v3_repair_pack_0006_ev_003. Suggested stronger evidence: v3_pack_0003_ev_001. Semantic match: vancouver_rs_018 (score 0.71, blockers different_direction, missing_core_evidence).
- `vancouver_rs_012` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, operator_not_supported, rule_object_not_supported in page 8; section 11.3.8.6; evidence_id v3_pack_0007_ev_002. Suggested stronger evidence: v3_pack_0002_ev_001. Semantic match: vancouver_rs_017 (score 0.71, blockers missing_core_evidence).
- `vancouver_rs_025` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch, applies_to_not_supported, operator_not_supported in page 8; section 11.3.8.6; evidence_id v3_repair_pack_0006_ev_002. Suggested stronger evidence: v3_pack_0003_ev_001. Semantic match: vancouver_rs_017 (score 0.71, blockers different_direction, missing_core_evidence).
