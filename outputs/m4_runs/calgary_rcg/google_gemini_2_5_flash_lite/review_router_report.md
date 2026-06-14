# Review Router

This file consolidates triage, evidence repair, and audit into one review queue. It does not verify rules.

## Summary

- Review rules: 43

### Action Buckets

- `rerun_with_evidence_bundle`: 15
- `fix_candidate_or_rule_family_mapping`: 10
- `operator_review`: 9
- `scope_review`: 6
- `semantic_guardrail_review`: 2
- `defer_low_priority`: 1

### Likelihood

- `plausible`: 20
- `weak`: 15
- `likely_correct`: 8

### Top Support Gaps

- `pipeline5_text_candidate_requires_review`: 40
- `applies_to_not_supported`: 31
- `upstream_extraction_requested_review`: 28
- `enumerated_branch_condition_missing`: 17
- `rule_object_not_supported`: 10
- `operator_not_supported`: 7
- `constraint_scope_not_supported`: 3
- `rule_family_direction_mismatch`: 2
- `coefficient_operand_not_value`: 2

### Recommendations

- Keep 2 close semantic matches blocked until their guardrail mismatch is resolved.

## Top 25 Review Routes

- `calgary_rcg_012` -> `semantic_guardrail_review` / `medium`: Compare the close verified match, but do not relax verification because core legal fields or guardrails disagree. Check upstream_extraction_requested_review in page 396; section 352(4.1); evidence_id m4_pack_0006_ev_002. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_019 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_252` -> `rerun_with_evidence_bundle` / `medium`: Rerun using the evidence bundle; promote only if deterministic verifier passes. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing in page 1030; section 8(3); evidence_id v3_repair_pack_0028_ev_001. Suggested stronger evidence: m4_pack_0001_ev_002. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_019 (score 0.90, blockers none).
- `calgary_rcg_203` -> `rerun_with_evidence_bundle` / `medium`: Rerun using the evidence bundle; promote only if deterministic verifier passes. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing in page 1022; section 8(4); evidence_id m4_pack_0997_ev_001. Suggested stronger evidence: m4_pack_0001_ev_002. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_019 (score 0.90, blockers none).
- `calgary_rcg_006` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, rule_family_direction_mismatch in page 397; section 352(8); evidence_id m4_pack_0002_ev_001. Suggested stronger evidence: m4_pack_0002_ev_002. Semantic match: calgary_rcg_220 (score 0.55, blockers different_direction, different_numeric_value).
- `calgary_rcg_013` -> `rerun_with_evidence_bundle` / `medium`: Rerun using the evidence bundle; promote only if deterministic verifier passes. Check upstream_extraction_requested_review in page 396; section 352(4.1); evidence_id m4_pack_0006_ev_003. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_019 (score 0.97, blockers none).
- `calgary_rcg_230` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, rule_family_direction_mismatch in page 397; section 352(8); evidence_id v3_repair_pack_0009_ev_001. Suggested stronger evidence: m4_pack_0002_ev_001. Semantic match: calgary_rcg_220 (score 0.55, blockers different_direction, different_numeric_value).
- `calgary_rcg_218` -> `semantic_guardrail_review` / `medium`: Compare the close verified match, but do not relax verification because core legal fields or guardrails disagree. Check pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing in page 396; section 352(3.2); evidence_id m4_pack_0001_v3_clause_ev_001. Suggested stronger evidence: m4_pack_0001_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_219 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_011` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check upstream_extraction_requested_review in page 396; section 352(4.1); evidence_id m4_pack_0006_ev_001. Semantic match: calgary_rcg_220 (score 1.00, blockers none).
- `calgary_rcg_020` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 396; section 352(5); evidence_id m4_pack_0012_ev_001. Suggested stronger evidence: m4_pack_0006_ev_001. Semantic match: calgary_rcg_221 (score 0.71, blockers different_numeric_value, exception_or_override_unresolved).
- `calgary_rcg_241` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 396; section 352(5); evidence_id v3_repair_pack_0018_ev_001. Suggested stronger evidence: m4_pack_0006_ev_001. Semantic match: calgary_rcg_221 (score 0.71, blockers different_numeric_value, exception_or_override_unresolved).
- `calgary_rcg_010` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 396; section 352(3); evidence_id m4_pack_0005_ev_001. Suggested stronger evidence: m4_pack_0001_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_219 (score 0.92, blockers none).
- `calgary_rcg_205` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, applies_to_not_supported in page 1030; section 8(3); evidence_id m4_pack_0999_ev_001. Suggested stronger evidence: m4_pack_0001_ev_002. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_019 (score 0.90, blockers none).
- `calgary_rcg_138` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, applies_to_not_supported in page 1031; section 8(4); evidence_id m4_pack_0384_ev_001. Suggested stronger evidence: m4_pack_0001_ev_002. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_019 (score 0.90, blockers none).
- `calgary_rcg_246` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, applies_to_not_supported in page 1031; section 8(4); evidence_id v3_repair_pack_0024_ev_001. Suggested stronger evidence: m4_pack_0001_ev_002. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_019 (score 0.90, blockers none).
- `calgary_rcg_250` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, applies_to_not_supported in page 1022; section 8(4); evidence_id v3_repair_pack_0027_ev_001. Suggested stronger evidence: m4_pack_0001_ev_002. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_019 (score 0.90, blockers none).
- `calgary_rcg_001` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 396; section 352(3.2); evidence_id m4_pack_0001_ev_001. Suggested stronger evidence: m4_pack_0794_ev_001. Semantic match: calgary_rcg_008 (score 0.91, blockers none).
- `calgary_rcg_224` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 396; section 352(3.2); evidence_id v3_repair_pack_0001_ev_001. Suggested stronger evidence: m4_pack_0794_ev_001. Semantic match: calgary_rcg_008 (score 0.91, blockers none).
- `calgary_rcg_002` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, applies_to_not_supported in page 396; section 352(3.2); evidence_id m4_pack_0001_ev_002. Suggested stronger evidence: m4_pack_0001_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_219 (score 0.70, blockers different_numeric_value).
- `calgary_rcg_003` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, applies_to_not_supported in page 396; section 352(3.2); evidence_id m4_pack_0001_ev_003. Suggested stronger evidence: m4_pack_0001_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_219 (score 0.70, blockers different_numeric_value).
- `calgary_rcg_225` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, applies_to_not_supported in page 396; section 352(3.2); evidence_id v3_repair_pack_0001_ev_002. Suggested stronger evidence: m4_pack_0001_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_219 (score 0.70, blockers different_numeric_value).
- `calgary_rcg_226` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, applies_to_not_supported in page 396; section 352(3.2); evidence_id v3_repair_pack_0001_ev_003. Suggested stronger evidence: m4_pack_0001_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_219 (score 0.70, blockers different_numeric_value).
- `calgary_rcg_007` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, applies_to_not_supported in page 397; section 352(8); evidence_id m4_pack_0002_ev_002. Suggested stronger evidence: m4_pack_0002_ev_001. Semantic match: calgary_rcg_019 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_231` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, applies_to_not_supported in page 397; section 352(8); evidence_id v3_repair_pack_0009_ev_002. Suggested stronger evidence: m4_pack_0002_ev_001. Semantic match: calgary_rcg_019 (score 0.71, blockers different_numeric_value).
- `calgary_rcg_217` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, applies_to_not_supported in page 982; section 8.8.1; evidence_id m4_pack_1391_ev_001. Suggested stronger evidence: m4_pack_1388_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_221 (score 0.27, blockers different_numeric_value, different_rule_object, different_unit).
- `calgary_rcg_125` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, enumerated_branch_condition_missing, applies_to_not_supported in page 472; section 541(2); evidence_id m4_pack_0253_ev_001. Suggested stronger evidence: m4_pack_0253_ev_002. Evidence bundle is safe to rerun through the verifier. Semantic match: calgary_rcg_019 (score 0.71, blockers different_numeric_value).
