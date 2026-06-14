# Review Router

This file consolidates triage, evidence repair, and audit into one review queue. It does not verify rules.

## Summary

- Review rules: 17

### Action Buckets

- `operator_review`: 5
- `condition_evidence_needed`: 2
- `defer_low_priority`: 2
- `semantic_guardrail_review`: 2
- `scope_review`: 2
- `fix_candidate_or_rule_family_mapping`: 2
- `human_legal_review`: 1
- `rerun_with_evidence_bundle`: 1

### Likelihood

- `plausible`: 10
- `likely_correct`: 7

### Top Support Gaps

- `pipeline5_text_candidate_requires_review`: 15
- `rule_family_direction_mismatch`: 5
- `applies_to_not_supported`: 4
- `text_condition_not_supported`: 2
- `rule_object_not_supported`: 2
- `unresolved_exception_cue`: 1

### Recommendations

- Keep 2 close semantic matches blocked until their guardrail mismatch is resolved.
- Keep 1 exception/conflict rules in human legal review.

## Top 25 Review Routes

- `burnaby_r1_073` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check unresolved_exception_cue in page 2; evidence_id burnaby_r1_matrix_p2_t0_b0_064. Semantic match: burnaby_r1_058 (score 0.59, blockers different_numeric_value, exception_or_override_unresolved).
- `burnaby_r1_005` -> `condition_evidence_needed` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported in page 6; section 101(1); evidence_id m4_pack_0006_ev_003. Suggested stronger evidence: m4_pack_0006_ev_001. Semantic match: burnaby_r1_074 (score 0.71, blockers different_numeric_value).
- `burnaby_r1_098` -> `condition_evidence_needed` / `high`: Find the clause or table header that proves the condition. Check pipeline5_text_candidate_requires_review, text_condition_not_supported in page 6; section 101(1); evidence_id v3_repair_pack_0002_ev_003. Suggested stronger evidence: m4_pack_0006_ev_001. Semantic match: burnaby_r1_074 (score 0.71, blockers different_numeric_value).
- `burnaby_r1_009` -> `rerun_with_evidence_bundle` / `medium`: Rerun using the evidence bundle; promote only if deterministic verifier passes. Check pipeline5_text_candidate_requires_review in page 1; section 101.1; evidence_id m4_pack_0057_ev_001. Suggested stronger evidence: m4_pack_0045_v3_clause_ev_002. Evidence bundle is safe to rerun through the verifier. Semantic match: burnaby_r1_013 (score 0.74, blockers none).
- `burnaby_r1_016` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check rule_family_direction_mismatch in page 2; evidence_id burnaby_r1_matrix_p2_t0_b0_007. Semantic match: burnaby_r1_014 (score 0.60, blockers different_direction, different_numeric_value).
- `burnaby_r1_093` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 1; section 101.2; evidence_id m4_pack_0045_v3_clause_ev_003. Suggested stronger evidence: m4_pack_0045_v3_clause_ev_002. Semantic match: burnaby_r1_080 (score 0.02, blockers different_direction, different_rule_object, different_unit).
- `burnaby_r1_003` -> `semantic_guardrail_review` / `medium`: Compare the close verified match, but do not relax verification because core legal fields or guardrails disagree. Check pipeline5_text_candidate_requires_review in page 6; section 101(1); evidence_id m4_pack_0006_ev_001. Semantic match: burnaby_r1_017 (score 0.71, blockers different_numeric_value).
- `burnaby_r1_008` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch in page 5; section 101(2); evidence_id m4_pack_0044_ev_001. Suggested stronger evidence: v3_repair_pack_0007_ev_001. Semantic match: burnaby_r1_065 (score 0.54, blockers different_direction, different_numeric_value).
- `burnaby_r1_096` -> `semantic_guardrail_review` / `medium`: Compare the close verified match, but do not relax verification because core legal fields or guardrails disagree. Check pipeline5_text_candidate_requires_review in page 6; section 101(1); evidence_id v3_repair_pack_0002_ev_001. Semantic match: burnaby_r1_017 (score 0.71, blockers different_numeric_value).
- `burnaby_r1_101` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch in page 5; section 101(2); evidence_id v3_repair_pack_0007_ev_001. Suggested stronger evidence: m4_pack_0044_ev_001. Semantic match: burnaby_r1_065 (score 0.54, blockers different_direction, different_numeric_value).
- `burnaby_r1_092` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 1; section 101.2; evidence_id m4_pack_0045_v3_clause_ev_002. Suggested stronger evidence: m4_pack_0045_v3_clause_ev_003. Semantic match: burnaby_r1_014 (score 0.05, blockers different_direction, different_rule_object, different_unit).
- `burnaby_r1_001` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 1; section 101.3; evidence_id m4_pack_0002_ev_001. Suggested stronger evidence: m4_pack_0002_ev_002. Semantic match: burnaby_r1_014 (score 0.90, blockers none).
- `burnaby_r1_094` -> `scope_review` / `medium`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported in page 1; section 101.3; evidence_id v3_repair_pack_0001_ev_001. Suggested stronger evidence: m4_pack_0002_ev_001. Semantic match: burnaby_r1_014 (score 0.90, blockers none).
- `burnaby_r1_002` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch, applies_to_not_supported in page 1; section 101.3; evidence_id m4_pack_0002_ev_002. Suggested stronger evidence: m4_pack_0002_ev_001. Semantic match: burnaby_r1_014 (score 0.60, blockers different_direction, different_numeric_value).
- `burnaby_r1_095` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch, applies_to_not_supported in page 1; section 101.3; evidence_id v3_repair_pack_0001_ev_002. Suggested stronger evidence: m4_pack_0002_ev_001. Semantic match: burnaby_r1_014 (score 0.60, blockers different_direction, different_numeric_value).
- `burnaby_r1_007` -> `fix_candidate_or_rule_family_mapping` / `low`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, rule_object_not_supported in page 6; section 101(2); evidence_id m4_pack_0034_ev_002. Suggested stronger evidence: m4_pack_0034_ev_001. Semantic match: burnaby_r1_006 (score 0.67, blockers different_numeric_value).
- `burnaby_r1_100` -> `fix_candidate_or_rule_family_mapping` / `low`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, rule_object_not_supported in page 6; section 101(2); evidence_id v3_repair_pack_0006_ev_002. Suggested stronger evidence: m4_pack_0034_ev_001. Semantic match: burnaby_r1_006 (score 0.67, blockers different_numeric_value).
