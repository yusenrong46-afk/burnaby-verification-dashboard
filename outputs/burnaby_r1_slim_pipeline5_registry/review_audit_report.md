# Review Audit

This audit groups review rules by the work needed to reduce review volume. It does not verify rules.

## Action Buckets

- `retry_with_better_evidence`: 46
- `safe_verifier_tuning_candidate`: 6
- `evidence_packet_repair_candidate`: 4
- `needs_second_source_consensus`: 4
- `defer_low_priority`: 3
- `human_legal_review`: 2
- `upstream_candidate_issue`: 1

## Recommendations

- Start with 46 rules that can be rerun against stronger evidence.
- Audit 6 near-verified rules for safe general verifier/table-scope tuning.
- Repair evidence attachments for 4 rules before changing verifier logic.
- Keep 2 exception/conflict rules in human legal review.
- Return 1 likely extraction/normalization mistakes upstream.

## Top Support Gaps

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

## Top 25 Action Items

- `burnaby_r1_076` -> `retry_with_better_evidence` score=0.73 repair=pipeline5_merged_rule_0050: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_129` -> `retry_with_better_evidence` score=0.70 repair=pipeline5_merged_rule_0043: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_121` -> `retry_with_better_evidence` score=0.68 repair=pipeline5_merged_rule_0079: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_134` -> `retry_with_better_evidence` score=0.67 repair=pipeline5_merged_rule_0106__api_01: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_135` -> `retry_with_better_evidence` score=0.66 repair=pipeline5_merged_rule_0106__api_01: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_127` -> `retry_with_better_evidence` score=0.65 repair=pipeline5_merged_rule_0120: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_109` -> `retry_with_better_evidence` score=0.56 repair=pipeline5_merged_rule_0105: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_071` -> `retry_with_better_evidence` score=0.85 repair=pipeline5_merged_rule_0048__api_01: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_113` -> `retry_with_better_evidence` score=0.79 repair=pipeline5_merged_rule_0106__api_01: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_077` -> `retry_with_better_evidence` score=0.78 repair=pipeline5_merged_rule_0073: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_028` -> `retry_with_better_evidence` score=0.72 repair=pipeline5_merged_rule_0018: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_095` -> `retry_with_better_evidence` score=0.72 repair=pipeline5_merged_rule_0041: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_019` -> `retry_with_better_evidence` score=0.72 repair=pipeline5_merged_rule_0061: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_046` -> `retry_with_better_evidence` score=0.71 repair=pipeline5_merged_rule_0041: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_086` -> `retry_with_better_evidence` score=0.70 repair=pipeline5_merged_rule_0079: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_029` -> `retry_with_better_evidence` score=0.57 repair=pipeline5_merged_rule_0018: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_030` -> `retry_with_better_evidence` score=0.55 repair=pipeline5_merged_rule_0061: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_022` -> `retry_with_better_evidence` score=0.63 repair=pipeline5_merged_rule_0072__api_01: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_024` -> `retry_with_better_evidence` score=0.63 repair=pipeline5_merged_rule_0054: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_026` -> `retry_with_better_evidence` score=0.61 repair=pipeline5_merged_rule_0054: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_070` -> `retry_with_better_evidence` score=0.60 repair=pipeline5_merged_rule_0072__api_01: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_064` -> `retry_with_better_evidence` score=0.58 repair=pipeline5_merged_rule_0061: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_075` -> `retry_with_better_evidence` score=0.55 repair=pipeline5_merged_rule_0068__api_01: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_105` -> `retry_with_better_evidence` score=0.54 repair=pipeline5_merged_rule_0101: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_066` -> `retry_with_better_evidence` score=0.51 repair=pipeline5_merged_rule_0061: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.

## Top Items By Action Bucket


### `retry_with_better_evidence`

- `burnaby_r1_076` -> `retry_with_better_evidence` score=0.73 repair=pipeline5_merged_rule_0050: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_129` -> `retry_with_better_evidence` score=0.70 repair=pipeline5_merged_rule_0043: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_121` -> `retry_with_better_evidence` score=0.68 repair=pipeline5_merged_rule_0079: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_134` -> `retry_with_better_evidence` score=0.67 repair=pipeline5_merged_rule_0106__api_01: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.
- `burnaby_r1_135` -> `retry_with_better_evidence` score=0.66 repair=pipeline5_merged_rule_0106__api_01: Rerun the same candidate against the suggested evidence packet and require deterministic proof again.

### `safe_verifier_tuning_candidate`

- `burnaby_r1_055` -> `safe_verifier_tuning_candidate` score=0.88 repair=none: Inspect whether a general verifier rule or table-scope pattern can be added without weakening safety gates.
- `burnaby_r1_047` -> `safe_verifier_tuning_candidate` score=0.83 repair=none: Inspect whether a general verifier rule or table-scope pattern can be added without weakening safety gates.
- `burnaby_r1_021` -> `safe_verifier_tuning_candidate` score=0.77 repair=none: Inspect whether a general verifier rule or table-scope pattern can be added without weakening safety gates.
- `burnaby_r1_023` -> `safe_verifier_tuning_candidate` score=0.77 repair=none: Inspect whether a general verifier rule or table-scope pattern can be added without weakening safety gates.
- `burnaby_r1_025` -> `safe_verifier_tuning_candidate` score=0.77 repair=none: Inspect whether a general verifier rule or table-scope pattern can be added without weakening safety gates.

### `evidence_packet_repair_candidate`

- `burnaby_r1_130` -> `evidence_packet_repair_candidate` score=0.69 repair=pipeline5_merged_rule_0066: Repair Pipeline 5 evidence attachment or retrieval context, then rerun verification.
- `burnaby_r1_068` -> `evidence_packet_repair_candidate` score=0.60 repair=pipeline5_merged_rule_0106__api_01: Repair Pipeline 5 evidence attachment or retrieval context, then rerun verification.
- `burnaby_r1_073` -> `evidence_packet_repair_candidate` score=0.60 repair=pipeline5_merged_rule_0066: Repair Pipeline 5 evidence attachment or retrieval context, then rerun verification.
- `burnaby_r1_069` -> `evidence_packet_repair_candidate` score=0.59 repair=pipeline5_merged_rule_0106__api_01: Repair Pipeline 5 evidence attachment or retrieval context, then rerun verification.

### `needs_second_source_consensus`

- `burnaby_r1_067` -> `needs_second_source_consensus` score=0.87 repair=pipeline5_merged_rule_0060: Find a second independent evidence packet or table context before allowing this text candidate past review.
- `burnaby_r1_063` -> `needs_second_source_consensus` score=0.87 repair=pipeline5_merged_rule_0093__api_01: Find a second independent evidence packet or table context before allowing this text candidate past review.
- `burnaby_r1_087` -> `needs_second_source_consensus` score=0.81 repair=pipeline5_merged_rule_0001: Find a second independent evidence packet or table context before allowing this text candidate past review.
- `burnaby_r1_111` -> `needs_second_source_consensus` score=0.77 repair=pipeline5_merged_rule_0062: Find a second independent evidence packet or table context before allowing this text candidate past review.

### `human_legal_review`

- `burnaby_r1_126` -> `human_legal_review` score=0.51 repair=pipeline5_merged_rule_0121: Resolve exception, override, or sibling-rule conflict manually before changing verifier behavior.
- `burnaby_r1_037` -> `human_legal_review` score=0.28 repair=pipeline5_merged_rule_0120: Resolve exception, override, or sibling-rule conflict manually before changing verifier behavior.

### `upstream_candidate_issue`

- `burnaby_r1_093` -> `upstream_candidate_issue` score=0.22 repair=pipeline5_merged_rule_0087: Send back to extraction/adapter normalization; do not tune verifier around this case.

### `defer_low_priority`

- `burnaby_r1_061` -> `defer_low_priority` score=0.83 repair=none: Leave in low-priority review until more evidence or a broader bylaw benchmark is available.
- `burnaby_r1_060` -> `defer_low_priority` score=0.82 repair=none: Leave in low-priority review until more evidence or a broader bylaw benchmark is available.
- `burnaby_r1_099` -> `defer_low_priority` score=0.61 repair=pipeline5_merged_rule_0085: Leave in low-priority review until more evidence or a broader bylaw benchmark is available.
