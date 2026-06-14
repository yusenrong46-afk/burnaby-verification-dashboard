# M4 Gap Report - vancouver_rs

M4 extracts and repairs evidence packs; deterministic verifier decides.

## Summary

| Metric | Value |
|---|---:|
| PDF pages | 22 |
| Source chunks | 251 |
| Evidence packs | 173 |
| M4 numeric clauses | 40 |
| M4 rule-like numeric clauses | 38 |
| M4 selected rule-like numeric coverage | 1.000 |
| Candidates | 32 |
| Verified | 12 |
| Review | 11 |
| Rejected | 9 |
| Not used | 0 |
| False verified | 0 |
| Verified/review recall | 1.000 |
| Extraction coverage recall | 1.000 |
| Verifier retention rate | 1.000 |
| Estimated cost | 0.010884 |
| Latency ms | 119897 |
| Extraction errors | 0 |

## V2 Comparison

| Metric | Delta |
|---|---:|
| candidate_rule_count | +18 |
| verified_rule_count | +10 |
| review_rule_count | +3 |
| false_verified_count | +0 |
| verified_or_review_recall | +0.429 |
| extraction_coverage_recall | +0.429 |

## Top Support Gaps

- pipeline5_text_candidate_requires_review: 19
- rule_object_not_supported: 14
- rule_family_direction_mismatch: 10
- rule_object_unit_not_compatible: 9
- coefficient_operand_not_value: 6
- operator_not_supported: 6
- applies_to_not_supported: 4
- unresolved_exception_cue: 4
- enumerated_branch_condition_missing: 2
- unit_not_found_in_evidence: 1

## Missed Rule Categories

- unextracted_gold_rule_ids: 0
- verifier_rejected_gold_rule_ids: 0
- not_used_gold_rule_ids: 0
- missed_verified_or_review_gold_rule_ids: 0

## Interpretation

- M4 preserved the false_verified_count = 0 safety target for this city.
- M4 improved verified-or-review recall versus V2.
- Missed-rule IDs are evaluation-only and are not used by M4 runtime extraction.
