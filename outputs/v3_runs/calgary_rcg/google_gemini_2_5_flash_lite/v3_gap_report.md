# V3 Gap Report - calgary_rcg

V3 extracts and repairs evidence packs; deterministic verifier decides.

## Summary

| Metric | Value |
|---|---:|
| PDF pages | 1053 |
| Source chunks | 3558 |
| Evidence packs | 500 |
| Candidates | 225 |
| Verified | 10 |
| Review | 28 |
| Rejected | 28 |
| Not used | 159 |
| False verified | 0 |
| Verified/review recall | 1.000 |
| Extraction coverage recall | 1.000 |
| Verifier retention rate | 1.000 |
| Estimated cost | 0.043808 |
| Latency ms | 380201 |
| Extraction errors | 1 |

## V2 Comparison

| Metric | Delta |
|---|---:|
| candidate_rule_count | +96 |
| verified_rule_count | +7 |
| review_rule_count | +12 |
| false_verified_count | +0 |
| verified_or_review_recall | +0.250 |
| extraction_coverage_recall | +0.125 |

## Top Support Gaps

- upstream_extraction_requested_review: 190
- pipeline5_text_candidate_requires_review: 179
- outside_target_section: 177
- enumerated_branch_condition_missing: 80
- constraint_scope_not_supported: 54
- applies_to_not_supported: 48
- rule_object_not_supported: 31
- operator_not_supported: 24
- rule_object_unit_not_compatible: 22
- rule_family_direction_mismatch: 15

## Missed Rule Categories

- unextracted_gold_rule_ids: 0
- verifier_rejected_gold_rule_ids: 0
- not_used_gold_rule_ids: 0
- missed_verified_or_review_gold_rule_ids: 0

## Interpretation

- V3 preserved the false_verified_count = 0 safety target for this city.
- V3 improved verified-or-review recall versus V2.
- Missed-rule IDs are evaluation-only and are not used by V3 runtime extraction.
