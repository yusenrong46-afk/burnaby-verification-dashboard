# Review Router

This file consolidates triage, evidence repair, and audit into one review queue. It does not verify rules.

## Summary

- Review rules: 28

### Action Buckets

- `operator_review`: 13
- `fix_candidate_or_rule_family_mapping`: 5
- `condition_evidence_needed`: 3
- `semantic_guardrail_review`: 2
- `defer_low_priority`: 2
- `human_legal_review`: 1
- `scope_review`: 1
- `rerun_with_evidence_bundle`: 1

### Likelihood

- `plausible`: 11
- `likely_correct`: 8
- `likely_wrong_or_noise`: 5
- `weak`: 4

### Top Support Gaps

- `text_candidate_requires_review`: 26
- `rule_object_not_supported`: 9
- `rule_family_direction_mismatch`: 8
- `upstream_extraction_requested_review`: 7
- `operator_not_supported`: 7
- `applies_to_not_supported`: 5
- `constraint_scope_not_supported`: 5
- `text_condition_not_supported`: 3
- `range_bound_not_maximum`: 3
- `unresolved_exception_cue`: 2
- `extraction_source_fidelity_hold`: 2

### Recommendations

- Keep 2 close semantic matches blocked until their guardrail mismatch is resolved.
- Keep 1 exception/conflict rules in human legal review.

## Top 25 Review Routes

- `burnaby_r1_092` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check unresolved_exception_cue in page 2; evidence_id burnaby_r1_matrix_p2_t0_b0_064. Semantic match: burnaby_r1_077 (score 0.59, blockers different_numeric_value, exception_or_override_unresolved).
- `burnaby_r1_006` -> `condition_evidence_needed` / `high`: Find the clause or table header that proves the condition. Check text_candidate_requires_review, text_condition_not_supported in page 6; section 101(1); evidence_id m4_pack_0006_ev_002. Suggested stronger evidence: m4_pack_0006_ev_001. Semantic match: burnaby_r1_041 (score 0.71, blockers exception_or_override_unresolved).
- `burnaby_r1_007` -> `condition_evidence_needed` / `high`: Find the clause or table header that proves the condition. Check text_candidate_requires_review, text_condition_not_supported in page 6; section 101(1); evidence_id m4_pack_0006_ev_003. Suggested stronger evidence: m4_pack_0006_ev_001. Semantic match: burnaby_r1_093 (score 0.71, blockers different_numeric_value).
- `burnaby_r1_005` -> `condition_evidence_needed` / `high`: Find the clause or table header that proves the condition. Check text_candidate_requires_review, text_condition_not_supported in page 6; section 101(1); evidence_id m4_pack_0006_ev_001. Semantic match: burnaby_r1_036 (score 0.71, blockers different_numeric_value, exception_or_override_unresolved).
- `burnaby_r1_018` -> `scope_review` / `high`: Check row/column/header/prose context for the correct legal scope. Check text_candidate_requires_review, applies_to_not_supported, unresolved_exception_cue in page 5; section 101(2); evidence_id m4_pack_0021_ev_001. Suggested stronger evidence: m4_pack_0008_ev_001. Semantic match: burnaby_r1_046 (score 0.71, blockers different_numeric_value, exception_or_override_unresolved).
- `burnaby_r1_035` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check rule_family_direction_mismatch in page 2; evidence_id burnaby_r1_matrix_p2_t0_b0_007. Semantic match: burnaby_r1_001 (score 0.60, blockers different_direction, different_numeric_value).
- `burnaby_r1_028` -> `semantic_guardrail_review` / `medium`: Compare the close verified match, but do not relax verification because core legal fields or guardrails disagree. Check text_candidate_requires_review in page 4; section 101(1); evidence_id m4_pack_0058_ev_001. Semantic match: burnaby_r1_001 (score 0.71, blockers different_numeric_value).
- `burnaby_r1_020` -> `semantic_guardrail_review` / `medium`: Compare the close verified match, but do not relax verification because core legal fields or guardrails disagree. Check text_candidate_requires_review in page 5; section 101(1); evidence_id m4_pack_0025_ev_002. Suggested stronger evidence: m4_pack_0025_ev_001. Semantic match: burnaby_r1_096 (score 0.71, blockers different_numeric_value).
- `burnaby_r1_008` -> `fix_candidate_or_rule_family_mapping` / `medium`: Extraction flagged this candidate for review; investigate and correct it upstream before rerun. Check upstream_extraction_requested_review, text_candidate_requires_review in page 5; section 101(1); evidence_id m4_pack_0008_ev_001. Suggested stronger evidence: m4_pack_0008_ev_002. Semantic match: burnaby_r1_011 (score 0.70, blockers different_numeric_value).
- `burnaby_r1_009` -> `fix_candidate_or_rule_family_mapping` / `medium`: Extraction flagged this candidate for review; investigate and correct it upstream before rerun. Check upstream_extraction_requested_review, text_candidate_requires_review in page 5; section 101(1); evidence_id m4_pack_0008_ev_002. Suggested stronger evidence: m4_pack_0008_ev_001. Semantic match: burnaby_r1_011 (score 0.90, blockers none).
- `burnaby_r1_112` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check text_candidate_requires_review in page 1; section 101.2; evidence_id m4_pack_0045_v3_clause_ev_003. Suggested stronger evidence: m4_pack_0045_v3_clause_ev_002. Semantic match: burnaby_r1_099 (score 0.02, blockers different_direction, different_rule_object, different_unit).
- `burnaby_r1_002` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check text_candidate_requires_review, rule_family_direction_mismatch in page 1; section 101.3; evidence_id m4_pack_0002_ev_002. Suggested stronger evidence: m4_pack_0002_ev_001. Semantic match: burnaby_r1_001 (score 0.63, blockers different_direction, different_numeric_value).
- `burnaby_r1_026` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check text_candidate_requires_review, rule_family_direction_mismatch in page 5; section 101(2); evidence_id m4_pack_0044_ev_001. Suggested stronger evidence: m4_pack_0025_ev_003. Semantic match: burnaby_r1_084 (score 0.54, blockers different_direction, different_numeric_value).
- `burnaby_r1_111` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check text_candidate_requires_review in page 1; section 101.2; evidence_id m4_pack_0045_v3_clause_ev_002. Suggested stronger evidence: m4_pack_0045_v3_clause_ev_003. Semantic match: burnaby_r1_033 (score 0.05, blockers different_direction, different_rule_object, different_unit).
- `burnaby_r1_027` -> `rerun_with_evidence_bundle` / `medium`: Check row/column/header/prose context for the correct legal scope. Check text_candidate_requires_review, applies_to_not_supported in page 1; section 101.1; evidence_id m4_pack_0057_ev_001. Suggested stronger evidence: m4_pack_0045_v3_clause_ev_002. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_032 (score 0.74, blockers none).
- `burnaby_r1_016` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check text_candidate_requires_review, rule_family_direction_mismatch, applies_to_not_supported, rule_object_not_supported in page 4; section 101(1); evidence_id m4_pack_0018_ev_003. Suggested stronger evidence: m4_pack_0018_ev_002. Semantic match: burnaby_r1_045 (score 0.54, blockers different_direction, different_numeric_value).
- `burnaby_r1_010` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check upstream_extraction_requested_review, text_candidate_requires_review, operator_not_supported, range_bound_not_maximum in page 4; section 101(1); evidence_id m4_pack_0017_ev_001. Suggested stronger evidence: m4_pack_0008_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_011 (score 0.71, blockers different_numeric_value, missing_core_evidence).
- `burnaby_r1_012` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check upstream_extraction_requested_review, extraction_source_fidelity_hold, text_candidate_requires_review, operator_not_supported in page 4; section 101(1); evidence_id m4_pack_0017_ev_003. Suggested stronger evidence: burnaby_r1_matrix_p2_t0_b0_001. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_011 (score 0.71, blockers different_numeric_value, missing_core_evidence).
- `burnaby_r1_013` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check upstream_extraction_requested_review, extraction_source_fidelity_hold, text_candidate_requires_review, operator_not_supported in page 4; section 101(1); evidence_id m4_pack_0017_ev_004. Suggested stronger evidence: m4_pack_0045_v3_clause_ev_002. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_011 (score 0.71, blockers different_numeric_value, missing_core_evidence).
- `burnaby_r1_019` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check text_candidate_requires_review, rule_family_direction_mismatch, operator_not_supported in page 5; section 101(1); evidence_id m4_pack_0025_ev_001. Semantic match: burnaby_r1_106 (score 0.61, blockers different_direction, different_numeric_value, missing_core_evidence).
- `burnaby_r1_024` -> `fix_candidate_or_rule_family_mapping` / `low`: Check whether extraction chose the wrong rule family. Check text_candidate_requires_review, rule_object_not_supported in page 6; section 101(2); evidence_id m4_pack_0034_ev_002. Suggested stronger evidence: m4_pack_0034_ev_001. Semantic match: burnaby_r1_023 (score 0.70, blockers different_numeric_value).
- `burnaby_r1_003` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check upstream_extraction_requested_review, text_candidate_requires_review, operator_not_supported, rule_object_not_supported in page 4; section 101(1); evidence_id m4_pack_0004_ev_001. Suggested stronger evidence: m4_pack_0008_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_011 (score 0.70, blockers different_numeric_value, missing_core_evidence).
- `burnaby_r1_004` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check upstream_extraction_requested_review, text_candidate_requires_review, operator_not_supported, rule_object_not_supported in page 4; section 101(1); evidence_id m4_pack_0004_ev_002. Suggested stronger evidence: m4_pack_0008_ev_001. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_011 (score 0.71, blockers missing_core_evidence).
- `burnaby_r1_022` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check text_candidate_requires_review, rule_family_direction_mismatch, constraint_scope_not_supported, rule_object_not_supported in page 5; section 101(1); evidence_id m4_pack_0025_ev_004. Suggested stronger evidence: m4_pack_0044_ev_001. Semantic match: burnaby_r1_096 (score 0.60, blockers different_direction, different_numeric_value).
- `burnaby_r1_021` -> `operator_review` / `low`: Confirm the legal direction: maximum/minimum/required/permitted. Check text_candidate_requires_review, rule_family_direction_mismatch, constraint_scope_not_supported, rule_object_not_supported in page 5; section 101(1); evidence_id m4_pack_0025_ev_003. Suggested stronger evidence: m4_pack_0044_ev_001. Semantic match: burnaby_r1_106 (score 0.55, blockers different_direction, different_numeric_value).
