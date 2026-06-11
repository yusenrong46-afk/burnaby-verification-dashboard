# Review Router

This file consolidates triage, evidence repair, and audit into one review queue. It does not verify rules.

## Summary

- Review rules: 52

### Action Buckets

- `defer_low_priority`: 23
- `human_legal_review`: 18
- `operator_review`: 9
- `fix_candidate_or_rule_family_mapping`: 2

### Likelihood

- `plausible`: 40
- `likely_correct`: 9
- `weak`: 2
- `likely_wrong_or_noise`: 1

### Top Support Gaps

- `pipeline5_text_candidate_requires_review`: 52
- `unresolved_exception_cue`: 18
- `upstream_extraction_requested_review`: 8
- `rule_family_direction_mismatch`: 5
- `rule_object_not_supported`: 4
- `operator_not_supported`: 4

### Recommendations

- Keep 18 exception/conflict rules in human legal review.

## Top 25 Review Routes

- `burnaby_r1_018` -> `operator_review` / `high`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch, unresolved_exception_cue in page 1; evidence_id burnaby_generic_graph_pack_004__page_0001__local_006. Suggested stronger evidence: burnaby_generic_graph_pack_002__page_0001__local_004.
- `burnaby_r1_022` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 1; evidence_id burnaby_generic_graph_pack_004__page_0001__local_006. Suggested stronger evidence: burnaby_generic_graph_pack_002__page_0001__local_004.
- `burnaby_r1_023` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 1; evidence_id burnaby_generic_graph_pack_004__page_0001__local_006. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_003.
- `burnaby_r1_033` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_001.
- `burnaby_r1_034` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_001.
- `burnaby_r1_035` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_001.
- `burnaby_r1_036` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_001.
- `burnaby_r1_037` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_001.
- `burnaby_r1_038` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_001.
- `burnaby_r1_039` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_001.
- `burnaby_r1_040` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_001.
- `burnaby_r1_041` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_001.
- `burnaby_r1_043` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_001.
- `burnaby_r1_044` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_001.
- `burnaby_r1_045` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_003.
- `burnaby_r1_053` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_003. Suggested stronger evidence: burnaby_generic_graph_pack_004__page_0001__local_006.
- `burnaby_r1_054` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_003. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_002.
- `burnaby_r1_042` -> `human_legal_review` / `high`: Resolve exception/covenant/notwithstanding wording manually. Check pipeline5_text_candidate_requires_review, unresolved_exception_cue in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_001.
- `burnaby_r1_024` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_001. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_002.
- `burnaby_r1_046` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_003.
- `burnaby_r1_047` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check upstream_extraction_requested_review, pipeline5_text_candidate_requires_review in page 2; evidence_id burnaby_generic_graph_pack_007__page_0002__local_003. Suggested stronger evidence: burnaby_generic_graph_pack_007__page_0002__local_002.
- `burnaby_r1_055` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch in page 4; evidence_id burnaby_generic_graph_pack_009__page_0004__local_001. Suggested stronger evidence: burnaby_generic_graph_pack_009__page_0004__local_002.
- `burnaby_r1_056` -> `operator_review` / `medium`: Confirm the legal direction: maximum/minimum/required/permitted. Check pipeline5_text_candidate_requires_review, rule_family_direction_mismatch in page 4; evidence_id burnaby_generic_graph_pack_009__page_0004__local_001. Suggested stronger evidence: burnaby_generic_graph_pack_009__page_0004__local_002.
- `burnaby_r1_061` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 4; evidence_id burnaby_generic_graph_pack_009__page_0004__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_009__page_0004__local_001.
- `burnaby_r1_063` -> `defer_low_priority` / `medium`: Keep in review until more evidence or a general verifier rule is justified. Check pipeline5_text_candidate_requires_review in page 4; evidence_id burnaby_generic_graph_pack_009__page_0004__local_002. Suggested stronger evidence: burnaby_generic_graph_pack_009__page_0004__local_001.
