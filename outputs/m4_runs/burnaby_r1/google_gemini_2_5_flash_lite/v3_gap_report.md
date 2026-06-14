# M4 Gap Report - burnaby_r1

M4 extracts and repairs evidence packs; deterministic verifier decides.

## Summary

| Metric | Value |
|---|---:|
| PDF pages | 7 |
| Source chunks | 93 |
| Evidence packs | 87 |
| M4 numeric clauses | 40 |
| M4 rule-like numeric clauses | 23 |
| M4 selected rule-like numeric coverage | 1.000 |
| Candidates | 101 |
| Verified | 84 |
| Review | 17 |
| Rejected | 0 |
| Not used | 0 |
| False verified | 0 |
| Verified/review recall | 1.000 |
| Extraction coverage recall | 1.000 |
| Verifier retention rate | 1.000 |
| Estimated cost | 0.003131 |
| Latency ms | 124302 |
| Extraction errors | 3 |

## V2 Comparison

| Metric | Delta |
|---|---:|
| candidate_rule_count | +22 |
| verified_rule_count | +34 |
| review_rule_count | +4 |
| false_verified_count | +0 |
| verified_or_review_recall | +0.275 |
| extraction_coverage_recall | +0.150 |

## Top Support Gaps

- pipeline5_text_candidate_requires_review: 15
- rule_family_direction_mismatch: 5
- applies_to_not_supported: 4
- rule_object_not_supported: 2
- text_condition_not_supported: 2
- unresolved_exception_cue: 1

## Missed Rule Categories

- unextracted_gold_rule_ids: 0
- verifier_rejected_gold_rule_ids: 0
- not_used_gold_rule_ids: 0
- missed_verified_or_review_gold_rule_ids: 0

## Interpretation

- M4 preserved the false_verified_count = 0 safety target for this city.
- M4 improved verified-or-review recall versus V2.
- Missed-rule IDs are evaluation-only and are not used by M4 runtime extraction.
