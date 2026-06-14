# Review Router

This file consolidates triage, evidence repair, and audit into one review queue. It does not verify rules.

## Summary

- Review rules: 28

### Action Buckets

- `rerun_with_evidence_bundle`: 8
- `fix_candidate_or_rule_family_mapping`: 7
- `scope_review`: 6
- `operator_review`: 4
- `semantic_guardrail_review`: 2
- `defer_low_priority`: 1

### Likelihood

- `plausible`: 12
- `weak`: 9
- `likely_correct`: 7

### Top Support Gaps

- `pipeline5_text_candidate_requires_review`: 25
- `applies_to_not_supported`: 21
- `upstream_extraction_requested_review`: 13
- `enumerated_branch_condition_missing`: 12
- `rule_object_not_supported`: 7
- `rule_family_direction_mismatch`: 3
- `coefficient_operand_not_value`: 2
- `constraint_scope_not_supported`: 1
- `operator_not_supported`: 1

### Recommendations

- Keep 2 close semantic matches blocked until their guardrail mismatch is resolved.

## Top 25 Review Routes

- `calgary_rcg_013` -> `semantic_guardrail_review` / `medium`: Compare the close verified match, but do not relax verification because core legal fields or guardrails disagree. Check upstream_extraction_requested_review in page 396; section 352(4.1); evidence_id v3_pack_0006_ev_002. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_019 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_014` -> `rerun_with_evidence_bundle` / `medium`: Rerun using the evidence bundle; promote only if deterministic verifier passes. Check upstream_extraction_requested_review in page 396; section 352(4.1); evidence_id v3_pack_0006_ev_003. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_019 (score 0.97, blockers none).
- `calgary_rcg_129` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, rule_family_direction_mismatch in page 397; section 352(8); evidence_id v3_repair_pack_0009_ev_001. Suggested stronger evidence: v3_pack_0002_ev_001. Semantic match: calgary_rcg_119 (score 0.55, blockers different_direction, different_numeric_value).
- `calgary_rcg_006` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, rule_family_direction_mismatch in page 397; section 352(8); evidence_id v3_pack_0002_ev_001. Suggested stronger evidence: v3_pack_0002_ev_002. Semantic match: calgary_rcg_019 (score 0.54, blockers different_direction, different_numeric_value).
- `calgary_rcg_117` -> `semantic_guardrail_review` / `medium`: Compare the close verified match, but do not relax verification because core legal fields or guardrails disagree. Check pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing in page 396; section 352(3.2); evidence_id v3_pack_0001_v3_clause_ev_001. Suggested stronger evidence: v3_pack_0001_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_118 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_012` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check upstream_extraction_requested_review in page 396; section 352(4.1); evidence_id v3_pack_0006_ev_001. Semantic match: calgary_rcg_119 (score 1.00, blockers none).
- `calgary_rcg_008` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, rule_family_direction_mismatch in page 397; section 352(8); evidence_id v3_pack_0002_ev_003. Suggested stronger evidence: v3_pack_0002_ev_001. Semantic match: calgary_rcg_009 (score 0.57, blockers different_direction, different_numeric_value).
- `calgary_rcg_020` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 396; section 352(5); evidence_id v3_pack_0012_ev_001. Suggested stronger evidence: v3_pack_0006_ev_001. Semantic match: calgary_rcg_120 (score 0.71, blockers different_numeric_value, exception_or_override_unresolved).
- `calgary_rcg_141` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 396; section 352(5); evidence_id v3_repair_pack_0018_ev_001. Suggested stronger evidence: v3_pack_0006_ev_001. Semantic match: calgary_rcg_120 (score 0.71, blockers different_numeric_value, exception_or_override_unresolved).
- `calgary_rcg_011` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 396; section 352(3); evidence_id v3_pack_0005_ev_001. Suggested stronger evidence: v3_pack_0001_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_118 (score 0.92, blockers none).
- `calgary_rcg_136` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 396; section 352(3); evidence_id v3_repair_pack_0014_ev_001. Suggested stronger evidence: v3_pack_0001_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_118 (score 0.92, blockers none).
- `calgary_rcg_001` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 396; section 352(3.2); evidence_id v3_pack_0001_ev_001. Suggested stronger evidence: v3_pack_0374_ev_001. Semantic match: calgary_rcg_009 (score 0.91, blockers none).
- `calgary_rcg_123` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 396; section 352(3.2); evidence_id v3_repair_pack_0001_ev_001. Suggested stronger evidence: v3_pack_0374_ev_001. Semantic match: calgary_rcg_009 (score 0.91, blockers none).
- `calgary_rcg_002` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, applies_to_not_supported in page 396; section 352(3.2); evidence_id v3_pack_0001_ev_002. Suggested stronger evidence: v3_pack_0001_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_118 (score 0.70, blockers different_numeric_value).
- `calgary_rcg_003` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, applies_to_not_supported in page 396; section 352(3.2); evidence_id v3_pack_0001_ev_003. Suggested stronger evidence: v3_pack_0001_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_118 (score 0.70, blockers different_numeric_value).
- `calgary_rcg_124` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, applies_to_not_supported in page 396; section 352(3.2); evidence_id v3_repair_pack_0001_ev_002. Suggested stronger evidence: v3_pack_0001_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_118 (score 0.70, blockers different_numeric_value).
- `calgary_rcg_125` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, applies_to_not_supported in page 396; section 352(3.2); evidence_id v3_repair_pack_0001_ev_003. Suggested stronger evidence: v3_pack_0001_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_118 (score 0.70, blockers different_numeric_value).
- `calgary_rcg_130` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, applies_to_not_supported in page 397; section 352(8); evidence_id v3_repair_pack_0009_ev_002. Suggested stronger evidence: v3_pack_0002_ev_001. Semantic match: calgary_rcg_019 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_007` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, applies_to_not_supported in page 397; section 352(8); evidence_id v3_pack_0002_ev_002. Suggested stronger evidence: v3_pack_0002_ev_001. Semantic match: calgary_rcg_019 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_223` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, applies_to_not_supported in page 472; section 541(2); evidence_id v3_repair_pack_0078_ev_001. Suggested stronger evidence: v3_repair_pack_0078_ev_002. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_019 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_174` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, applies_to_not_supported, operator_not_supported in page 1041; section 8(2); evidence_id v3_repair_pack_0047_ev_002. Suggested stronger evidence: v3_pack_0111_ev_002. Semantic match: calgary_rcg_019 (score 0.71, blockers different_numeric_value, missing_core_evidence).
- `calgary_rcg_224` -> `fix_candidate_or_rule_family_mapping` / `low`: Check whether extraction chose the wrong rule family. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, applies_to_not_supported, rule_object_not_supported in page 472; section 541(2); evidence_id v3_repair_pack_0078_ev_002. Suggested stronger evidence: v3_repair_pack_0078_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_019 (score 0.70, blockers different_numeric_value).
- `calgary_rcg_004` -> `fix_candidate_or_rule_family_mapping` / `low`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, rule_object_not_supported, coefficient_operand_not_value in page 396; section 352(3.2); evidence_id v3_pack_0001_ev_004. Suggested stronger evidence: v3_pack_0113_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_121 (score 0.22, blockers different_numeric_value, different_rule_object, different_unit).
- `calgary_rcg_021` -> `fix_candidate_or_rule_family_mapping` / `low`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, applies_to_not_supported, rule_object_not_supported in page 397; section 352(7); evidence_id v3_pack_0013_ev_001. Suggested stronger evidence: v3_pack_0004_ev_001. Semantic match: calgary_rcg_118 (score 0.23, blockers different_numeric_value, different_rule_object, different_unit).
- `calgary_rcg_126` -> `fix_candidate_or_rule_family_mapping` / `low`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, rule_object_not_supported, coefficient_operand_not_value in page 396; section 352(3.2); evidence_id v3_repair_pack_0001_ev_004. Suggested stronger evidence: v3_pack_0113_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_121 (score 0.22, blockers different_numeric_value, different_rule_object, different_unit).
