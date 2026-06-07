# Review Router

This report classifies review-needed rules by next action. It does not verify rules.

## Action Buckets

- `retry_with_better_evidence`: 35
- `safe_verifier_tuning_candidate`: 28
- `needs_second_source_consensus`: 7
- `defer_low_priority`: 6
- `human_legal_review`: 5

## Recommendations

- Start with 35 rules that can be rerun against stronger evidence.
- Audit 28 near-verified rules for general verifier tuning.
- Keep 5 exception/conflict rules in human legal review.

## Top Support Gaps

- `text_candidate_requires_review`: 41
- `table_cell_candidate_requires_review`: 36
- `table_evidence_candidate_requires_review`: 36
- `applies_to_not_supported`: 24
- `text_condition_not_supported`: 22
- `operator_not_supported`: 20
- `table_column_not_target_scope`: 13
- `rule_object_not_supported`: 12
- `table_applies_to_not_supported`: 10
- `constraint_scope_not_supported`: 5
- `unresolved_exception_cue`: 3
- `cross_family_value_collision`: 2

## Evidence Span Issues

- `none`: 64
- `enumerated_subclause_without_parent`: 16
- `exception_fragment_needs_parent_scope`: 1

## Top 25 Items

- `burnaby_r1_071` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.90: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_046` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.80: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_113` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.83: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_076` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.78: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_019` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.71: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_127` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.70: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_135` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.71: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_026` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.64: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_028` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.66: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_070` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.64: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_086` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.66: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_022` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.60: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_024` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.60: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_064` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.62: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_075` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.59: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_105` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.58: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_109` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.59: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_030` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.55: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_032` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.55: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_034` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.55: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_036` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.55: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_029` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.52: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_066` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.50: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_122` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.48: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
- `burnaby_r1_123` -> `retry_with_better_evidence` category=`better_evidence_needed` score=0.48: Rerun the same candidate against the suggested stronger evidence, then require deterministic proof again.
