# Review Triage Report

This report ranks `review_needed` rules. It does not change verification decisions.

## Summary

- Review rules: 81

### Categories

- `missing_condition_evidence`: 21
- `near_verified_table_context`: 16
- `missing_applies_to`: 13
- `operator_uncertain`: 12
- `text_candidate_needs_consensus`: 9
- `unresolved_exception`: 4
- `missing_scope_evidence`: 3
- `cross_family_conflict`: 2
- `possible_rule_object_mismatch`: 1

### Likelihood

- `plausible`: 35
- `weak`: 23
- `likely_correct`: 15
- `likely_wrong_or_noise`: 8

### Top Blocking Reasons

- `pipeline5_text_candidate_requires_review`: 44
- `table_cell_candidate_requires_review`: 31
- `table_evidence_candidate_requires_review`: 31
- `applies_to_not_supported`: 25
- `text_condition_not_supported`: 22
- `operator_not_supported`: 20
- `rule_object_not_supported`: 14
- `table_applies_to_not_supported`: 10
- `table_column_not_target_scope`: 10
- `unresolved_exception_cue`: 4
- `constraint_scope_not_supported`: 4
- `cross_family_value_collision`: 2

## Top 20 Review Items

- #13 `burnaby_r1_055` setback >= 1.2 m -> `near_verified_table_context` / `likely_correct` score=0.88: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #18 `burnaby_r1_041` storeys <= 2.5 storeys -> `near_verified_table_context` / `likely_correct` score=0.83: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #18 `burnaby_r1_047` setback >= 3.0 m -> `near_verified_table_context` / `likely_correct` score=0.83: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #18 `burnaby_r1_040` storeys <= 3 storeys -> `near_verified_table_context` / `likely_correct` score=0.82: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #18 `burnaby_r1_038` height <= 10 m -> `near_verified_table_context` / `likely_correct` score=0.82: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #18 `burnaby_r1_039` height <= 9.5 m -> `near_verified_table_context` / `likely_correct` score=0.82: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #19 `burnaby_r1_056` building_separation >= 2.4 m -> `near_verified_table_context` / `likely_correct` score=0.82: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #22 `burnaby_r1_018` lot_area >= 281 m² -> `near_verified_table_context` / `likely_correct` score=0.78: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #23 `burnaby_r1_061` dwelling_units >= 2 units -> `near_verified_table_context` / `plausible` score=0.77: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #23 `burnaby_r1_060` dwelling_units >= 1 units -> `near_verified_table_context` / `plausible` score=0.77: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #24 `burnaby_r1_021` dwelling_units <= 3 units -> `near_verified_table_context` / `plausible` score=0.77: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #24 `burnaby_r1_023` dwelling_units <= 2 units -> `near_verified_table_context` / `plausible` score=0.77: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #24 `burnaby_r1_025` dwelling_units <= 4 units -> `near_verified_table_context` / `plausible` score=0.77: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #24 `burnaby_r1_051` setback >= 3.0 m -> `unresolved_exception` / `plausible` score=0.76: Resolve exception/override wording before promotion.
- #24 `burnaby_r1_052` setback >= 1.5 m -> `unresolved_exception` / `plausible` score=0.76: Resolve exception/override wording before promotion.
- #25 `burnaby_r1_053` setback >= 0 m -> `unresolved_exception` / `plausible` score=0.75: Resolve exception/override wording before promotion.
- #25 `burnaby_r1_054` setback >= 1.2 m -> `unresolved_exception` / `plausible` score=0.75: Resolve exception/override wording before promotion.
- #26 `burnaby_r1_027` dwelling_units <= 6 units -> `near_verified_table_context` / `plausible` score=0.74: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #27 `burnaby_r1_001` permitted_use allowed Permitted  -> `near_verified_table_context` / `plausible` score=0.73: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #27 `burnaby_r1_076` building_separation >= 2.4 m -> `missing_condition_evidence` / `plausible` score=0.73: Find evidence span that includes the material condition, not only the value/unit.
