# V3 Gap Report - burnaby_r1

V3 extracts and repairs evidence packs; deterministic verifier decides.

## Summary

| Metric | Value |
|---|---:|
| PDF pages | 7 |
| Source chunks | 93 |
| Evidence packs | 75 |
| Candidates | 103 |
| Verified | 84 |
| Review | 19 |
| Rejected | 0 |
| Not used | 0 |
| False verified | 0 |
| Verified/review recall | 1.000 |
| Extraction coverage recall | 1.000 |
| Verifier retention rate | 1.000 |
| Estimated cost | 0.002688 |
| Latency ms | 28432 |
| Extraction errors | 2 |

## V2 Comparison

| Metric | Delta |
|---|---:|
| candidate_rule_count | +24 |
| verified_rule_count | +34 |
| review_rule_count | +6 |
| false_verified_count | +0 |
| verified_or_review_recall | +0.275 |
| extraction_coverage_recall | +0.150 |

## Top Support Gaps

- pipeline5_text_candidate_requires_review: 17
- rule_family_direction_mismatch: 5
- applies_to_not_supported: 4
- rule_object_not_supported: 4
- operator_not_supported: 2
- text_condition_not_supported: 2
- constraint_scope_not_supported: 1
- range_bound_not_maximum: 1
- unresolved_exception_cue: 1

## Missed Rule Categories

- unextracted_gold_rule_ids: 0
- verifier_rejected_gold_rule_ids: 0
- not_used_gold_rule_ids: 0
- missed_verified_or_review_gold_rule_ids: 0

## Interpretation

- V3 preserved the false_verified_count = 0 safety target for this city.
- V3 improved verified-or-review recall versus V2.
- Missed-rule IDs are evaluation-only and are not used by V3 runtime extraction.
