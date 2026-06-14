# M4 Gap Report - calgary_rcg

M4 extracts and repairs evidence packs; deterministic verifier decides.

## Summary

| Metric | Value |
|---|---:|
| PDF pages | 1053 |
| Source chunks | 3558 |
| Evidence packs | 1400 |
| M4 numeric clauses | 1106 |
| M4 rule-like numeric clauses | 1044 |
| M4 selected rule-like numeric coverage | 1.000 |
| Candidates | 306 |
| Verified | 11 |
| Review | 43 |
| Rejected | 35 |
| Not used | 217 |
| False verified | 0 |
| Verified/review recall | 1.000 |
| Extraction coverage recall | 1.000 |
| Verifier retention rate | 1.000 |
| Estimated cost | 0.09968 |
| Latency ms | 1052737 |
| Extraction errors | 4 |

## V2 Comparison

| Metric | Delta |
|---|---:|
| candidate_rule_count | +177 |
| verified_rule_count | +8 |
| review_rule_count | +27 |
| false_verified_count | +0 |
| verified_or_review_recall | +0.250 |
| extraction_coverage_recall | +0.125 |

## Top Support Gaps

- upstream_extraction_requested_review: 273
- pipeline5_text_candidate_requires_review: 243
- outside_target_section: 240
- enumerated_branch_condition_missing: 99
- applies_to_not_supported: 93
- constraint_scope_not_supported: 56
- rule_object_not_supported: 50
- operator_not_supported: 38
- rule_object_unit_not_compatible: 24
- rule_family_direction_mismatch: 21

## Missed Rule Categories

- unextracted_gold_rule_ids: 0
- verifier_rejected_gold_rule_ids: 0
- not_used_gold_rule_ids: 1
- missed_verified_or_review_gold_rule_ids: 0

## Interpretation

- M4 preserved the false_verified_count = 0 safety target for this city.
- M4 improved verified-or-review recall versus V2.
- Missed-rule IDs are evaluation-only and are not used by M4 runtime extraction.
