# Review Triage Report

This report ranks `review_needed` rules. It does not change verification decisions.

## Summary

- Review rules: 66

### Categories

- `missing_condition_evidence`: 21
- `missing_applies_to`: 13
- `operator_uncertain`: 12
- `near_verified_table_context`: 6
- `text_candidate_needs_consensus`: 5
- `general_review`: 4
- `cross_family_conflict`: 2
- `missing_scope_evidence`: 2
- `possible_rule_object_mismatch`: 1

### Likelihood

- `plausible`: 29
- `weak`: 19
- `likely_correct`: 10
- `likely_wrong_or_noise`: 8

### Top Blocking Reasons

- `pipeline5_text_candidate_requires_review`: 42
- `applies_to_not_supported`: 25
- `text_condition_not_supported`: 22
- `operator_not_supported`: 19
- `rule_family_direction_mismatch`: 18
- `table_cell_candidate_requires_review`: 15
- `table_evidence_candidate_requires_review`: 15
- `rule_object_not_supported`: 13
- `table_applies_to_not_supported`: 10
- `table_column_not_target_scope`: 9
- `constraint_scope_not_supported`: 4
- `cross_family_value_collision`: 2

## Top 20 Review Items

- #13 `burnaby_r1_055` setback >= 1.2 m -> `near_verified_table_context` / `likely_correct` score=0.88: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #18 `burnaby_r1_047` setback >= 3.0 m -> `near_verified_table_context` / `likely_correct` score=0.83: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #24 `burnaby_r1_021` dwelling_units <= 3 units -> `near_verified_table_context` / `plausible` score=0.77: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #24 `burnaby_r1_023` dwelling_units <= 2 units -> `near_verified_table_context` / `plausible` score=0.77: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #24 `burnaby_r1_025` dwelling_units <= 4 units -> `near_verified_table_context` / `plausible` score=0.77: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #26 `burnaby_r1_027` dwelling_units <= 6 units -> `near_verified_table_context` / `plausible` score=0.74: Inspect table title, row, column, and cell; consider adding a safe table-scope pattern.
- #27 `burnaby_r1_076` building_separation >= 2.4 m -> `missing_condition_evidence` / `plausible` score=0.73: Find evidence span that includes the material condition, not only the value/unit.
- #30 `burnaby_r1_129` setback >= 2.0 m -> `missing_condition_evidence` / `plausible` score=0.70: Find evidence span that includes the material condition, not only the value/unit.
- #31 `burnaby_r1_130` building_separation allowed reduced  -> `missing_condition_evidence` / `plausible` score=0.69: Find evidence span that includes the material condition, not only the value/unit.
- #32 `burnaby_r1_121` fire_access_corridor allowed   -> `missing_condition_evidence` / `plausible` score=0.68: Find evidence span that includes the material condition, not only the value/unit.
- #34 `burnaby_r1_134` setback allowed   -> `missing_condition_evidence` / `plausible` score=0.67: Find evidence span that includes the material condition, not only the value/unit.
- #34 `burnaby_r1_135` setback allowed   -> `missing_condition_evidence` / `plausible` score=0.66: Find evidence span that includes the material condition, not only the value/unit.
- #35 `burnaby_r1_127` impervious_surface <= 70 % -> `missing_condition_evidence` / `plausible` score=0.65: Find evidence span that includes the material condition, not only the value/unit.
- #45 `burnaby_r1_109` building_separation <= 1.2 m -> `missing_condition_evidence` / `plausible` score=0.56: Find evidence span that includes the material condition, not only the value/unit.
- #49 `burnaby_r1_126` lot_coverage <= 60 % -> `cross_family_conflict` / `weak` score=0.51: Compare sibling rule families sharing the same value; do not auto-pick a winner.
- #72 `burnaby_r1_037` impervious_surface <= 60 % -> `cross_family_conflict` / `likely_wrong_or_noise` score=0.28: Compare sibling rule families sharing the same value; do not auto-pick a winner.
- #112 `burnaby_r1_067` lot_area > 280 m² -> `text_candidate_needs_consensus` / `likely_correct` score=0.87: Look for table or second text source asserting the exact same rule.
- #112 `burnaby_r1_063` dwelling_units allowed   -> `text_candidate_needs_consensus` / `likely_correct` score=0.87: Look for table or second text source asserting the exact same rule.
- #114 `burnaby_r1_071` setback = 1.2 m -> `text_candidate_needs_consensus` / `likely_correct` score=0.85: Look for table or second text source asserting the exact same rule.
- #117 `burnaby_r1_061` dwelling_units >= 2 units -> `general_review` / `likely_correct` score=0.83: Inspect proof trace and support gaps.
