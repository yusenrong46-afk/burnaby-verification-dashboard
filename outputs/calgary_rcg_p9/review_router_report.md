# Review Router

This file consolidates triage, evidence repair, and audit into one review queue. It does not verify rules.

## Summary

- Review rules: 348

### Action Buckets

- `operator_review`: 175
- `rerun_with_evidence_bundle`: 99
- `fix_candidate_or_rule_family_mapping`: 38
- `human_legal_review`: 17
- `defer_low_priority`: 15
- `scope_review`: 2
- `condition_evidence_needed`: 1
- `semantic_guardrail_review`: 1

### Likelihood

- `plausible`: 210
- `likely_correct`: 66
- `weak`: 58
- `likely_wrong_or_noise`: 14

### Top Support Gaps

- `pipeline5_text_candidate_requires_review`: 338
- `operator_not_supported`: 163
- `upstream_extraction_requested_review`: 67
- `rule_object_not_supported`: 52
- `unresolved_exception_cue`: 30
- `applies_to_not_supported`: 25
- `rule_family_direction_mismatch`: 18
- `text_condition_not_supported`: 7
- `constraint_scope_not_supported`: 2
- `allowance_trigger_threshold`: 1

### Recommendations

- Keep 1 close semantic matches blocked until their guardrail mismatch is resolved.
- Keep 17 exception/conflict rules in human legal review.

## Top 25 Review Routes

- `calgary_rcg_007` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 390; evidence_id calgary_generic_graph_pack_065__page_0390__local_002. Suggested stronger evidence: calgary_generic_graph_pack_066__page_0390__local_003. Semantic match: calgary_rcg_218 (score 0.45, blockers different_direction, different_unit, exception_or_override_unresolved).
- `calgary_rcg_342` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check unresolved_exception_cue in page 504; evidence_id calgary_generic_graph_pack_167__page_0504__local_004. Semantic match: calgary_rcg_316 (score 0.71, blockers exception_or_override_unresolved).
- `calgary_rcg_389` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check upstream_extraction_requested_review, unresolved_exception_cue in page 196; evidence_id calgary_generic_graph_pack_031__page_0196__local_004. Semantic match: calgary_rcg_317 (score 0.70, blockers exception_or_override_unresolved).
- `calgary_rcg_004` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 390; evidence_id calgary_generic_graph_pack_065__page_0390__local_002. Semantic match: calgary_rcg_289 (score 0.40, blockers different_direction, different_unit, exception_or_override_unresolved).
- `calgary_rcg_229` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 395; evidence_id calgary_generic_graph_pack_071__page_0395__local_003. Suggested stronger evidence: calgary_generic_graph_pack_028__page_0195__local_005. Semantic match: calgary_rcg_236 (score 0.57, blockers different_unit, exception_or_override_unresolved).
- `calgary_rcg_205` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 386; evidence_id calgary_generic_graph_pack_064__page_0386__local_002. Suggested stronger evidence: calgary_generic_graph_pack_162__page_0483__local_003. Semantic match: calgary_rcg_353 (score 0.44, blockers different_unit, exception_or_override_unresolved).
- `calgary_rcg_150` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 121; evidence_id calgary_generic_graph_pack_021__page_0121__local_004. Suggested stronger evidence: calgary_generic_graph_pack_186__page_0555__local_004. Semantic match: calgary_rcg_289 (score 0.27, blockers different_rule_object, different_unit, exception_or_override_unresolved).
- `calgary_rcg_151` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 121; evidence_id calgary_generic_graph_pack_021__page_0121__local_004. Suggested stronger evidence: calgary_generic_graph_pack_186__page_0555__local_004. Semantic match: calgary_rcg_289 (score 0.26, blockers different_rule_object, different_unit, exception_or_override_unresolved).
- `calgary_rcg_230` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check upstream_extraction_requested_review, unresolved_exception_cue in page 395; evidence_id calgary_generic_graph_pack_071__page_0395__local_003. Semantic match: calgary_rcg_356 (score 0.30, blockers different_numeric_value, different_rule_object, different_unit, exception_or_override_unresolved).
- `calgary_rcg_240` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check unresolved_exception_cue in page 396; evidence_id calgary_generic_graph_pack_074__page_0396__local_005. Semantic match: calgary_rcg_358 (score 0.40, blockers different_rule_object, different_unit, exception_or_override_unresolved).
- `calgary_rcg_361` -> `condition_evidence_needed` / `high`: Find the clause or table header that proves the condition. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, text_condition_not_supported in page 857; evidence_id calgary_generic_graph_pack_223__page_0857__local_005. Suggested stronger evidence: calgary_generic_graph_pack_063__page_0386__local_004. Semantic match: calgary_rcg_356 (score 0.28, blockers different_numeric_value, different_rule_object, different_unit).
- `calgary_rcg_408` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 397; evidence_id calgary_generic_graph_pack_080__page_0397__local_002. Suggested stronger evidence: calgary_generic_graph_pack_011__page_0080__local_004. Semantic match: calgary_rcg_244 (score 0.29, blockers different_direction, different_rule_object, different_unit, exception_or_override_unresolved).
- `calgary_rcg_005` -> `operator_review` / `high`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported, unresolved_exception_cue in page 390; evidence_id calgary_generic_graph_pack_065__page_0390__local_002. Suggested stronger evidence: calgary_generic_graph_pack_066__page_0390__local_003. Semantic match: calgary_rcg_210 (score 0.61, blockers different_numeric_value, exception_or_override_unresolved, missing_core_evidence).
- `calgary_rcg_206` -> `operator_review` / `high`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported, unresolved_exception_cue in page 386; evidence_id calgary_generic_graph_pack_064__page_0386__local_002. Semantic match: calgary_rcg_244 (score 0.54, blockers different_direction, exception_or_override_unresolved, missing_core_evidence).
- `calgary_rcg_239` -> `scope_review` / `high`: Check row/column/header/prose context for the correct legal scope. Check pipeline5_text_candidate_requires_review, applies_to_not_supported, unresolved_exception_cue in page 396; evidence_id calgary_generic_graph_pack_074__page_0396__local_005. Suggested stronger evidence: calgary_generic_graph_pack_063__page_0386__local_004. Semantic match: calgary_rcg_321 (score 0.42, blockers different_numeric_value, different_rule_object, different_unit, exception_or_override_unresolved).
- `calgary_rcg_343` -> `operator_review` / `high`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported, unresolved_exception_cue in page 504; evidence_id calgary_generic_graph_pack_167__page_0504__local_004. Semantic match: calgary_rcg_234 (score 0.33, blockers different_direction, different_unit, exception_or_override_unresolved, missing_core_evidence).
- `calgary_rcg_207` -> `operator_review` / `high`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported, unresolved_exception_cue in page 386; evidence_id calgary_generic_graph_pack_064__page_0386__local_002. Semantic match: calgary_rcg_244 (score 0.38, blockers different_direction, different_unit, exception_or_override_unresolved, missing_core_evidence).
- `calgary_rcg_194` -> `fix_candidate_or_rule_family_mapping` / `high`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, rule_object_not_supported, unresolved_exception_cue in page 384; evidence_id calgary_generic_graph_pack_061__page_0384__local_002. Suggested stronger evidence: calgary_generic_graph_pack_061__page_0384__local_003. Semantic match: calgary_rcg_292 (score 0.36, blockers different_direction, different_unit, exception_or_override_unresolved).
- `calgary_rcg_222` -> `fix_candidate_or_rule_family_mapping` / `high`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, rule_object_not_supported, unresolved_exception_cue in page 392; evidence_id calgary_generic_graph_pack_068__page_0392__local_003. Suggested stronger evidence: calgary_generic_graph_pack_066__page_0390__local_003. Semantic match: calgary_rcg_218 (score 0.29, blockers different_direction, different_rule_object, different_unit, exception_or_override_unresolved).
- `calgary_rcg_231` -> `operator_review` / `high`: Confirm the legal direction: maximum/minimum/required/permitted. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, operator_not_supported, unresolved_exception_cue in page 395; evidence_id calgary_generic_graph_pack_071__page_0395__local_003. Suggested stronger evidence: calgary_generic_graph_pack_070__page_0395__local_002. Semantic match: calgary_rcg_234 (score 0.16, blockers different_direction, different_rule_object, different_unit, exception_or_override_unresolved, missing_core_evidence).
- `calgary_rcg_335` -> `fix_candidate_or_rule_family_mapping` / `high`: Check whether extraction chose the wrong rule family. Check pipeline5_text_candidate_requires_review, rule_object_not_supported, unresolved_exception_cue in page 504; evidence_id calgary_generic_graph_pack_167__page_0504__local_002. Suggested stronger evidence: calgary_generic_graph_pack_061__page_0384__local_002. Semantic match: calgary_rcg_292 (score 0.35, blockers different_direction, different_unit, exception_or_override_unresolved).
- `calgary_rcg_196` -> `fix_candidate_or_rule_family_mapping` / `high`: Check whether extraction chose the wrong rule family. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, rule_object_not_supported, unresolved_exception_cue in page 384; evidence_id calgary_generic_graph_pack_061__page_0384__local_002. Suggested stronger evidence: calgary_generic_graph_pack_061__page_0384__local_003. Semantic match: calgary_rcg_356 (score 0.36, blockers different_direction, different_unit, exception_or_override_unresolved).
- `calgary_rcg_304` -> `operator_review` / `high`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported, unresolved_exception_cue in page 465; evidence_id calgary_generic_graph_pack_146__page_0465__local_004. Semantic match: calgary_rcg_321 (score 0.15, blockers different_direction, different_rule_object, different_unit, exception_or_override_unresolved, missing_core_evidence).
- `calgary_rcg_305` -> `operator_review` / `high`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, operator_not_supported, unresolved_exception_cue in page 465; evidence_id calgary_generic_graph_pack_146__page_0465__local_004. Semantic match: calgary_rcg_321 (score 0.24, blockers different_direction, different_rule_object, different_unit, exception_or_override_unresolved, missing_core_evidence).
- `calgary_rcg_153` -> `fix_candidate_or_rule_family_mapping` / `high`: Check whether extraction chose the wrong rule family. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review, rule_object_not_supported, unresolved_exception_cue in page 121; evidence_id calgary_generic_graph_pack_021__page_0121__local_004. Semantic match: calgary_rcg_353 (score 0.30, blockers different_rule_object, different_unit, exception_or_override_unresolved).
