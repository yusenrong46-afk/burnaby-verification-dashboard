# Review Resolution

This report labels what remains in `review_needed.json`. It does not verify rules.

## Summary

- Review rules: 15
- Promotable now: 0
- Can promote after evidence fix: 0

### Resolutions

- `upstream_extraction_issue`: 8
- `operator_or_direction_issue`: 4
- `close_match_but_guardrail_blocked`: 1
- `needs_second_source_consensus`: 1
- `human_legal_review`: 1

## Top 25

- `vancouver_rs_001` -> `operator_or_direction_issue`: Confirm whether the bylaw says minimum, maximum, required, permitted, or an exception to those.
- `vancouver_rs_003` -> `operator_or_direction_issue`: Confirm whether the bylaw says minimum, maximum, required, permitted, or an exception to those.
- `vancouver_rs_005` -> `close_match_but_guardrail_blocked`: The meaning is close, but a core legal field differs. Do not promote unless the mismatch is resolved from source text.
- `vancouver_rs_009` -> `upstream_extraction_issue`: Send this back to extraction/normalization; the cited evidence does not prove the selected rule family.
- `vancouver_rs_016` -> `upstream_extraction_issue`: Send this back to extraction/normalization; the cited evidence does not prove the selected rule family.
- `vancouver_rs_017` -> `upstream_extraction_issue`: Send this back to extraction/normalization; the cited evidence does not prove the selected rule family.
- `vancouver_rs_018` -> `upstream_extraction_issue`: Send this back to extraction/normalization; the cited evidence does not prove the selected rule family.
- `vancouver_rs_019` -> `upstream_extraction_issue`: Send this back to extraction/normalization; the cited evidence does not prove the selected rule family.
- `vancouver_rs_020` -> `upstream_extraction_issue`: Send this back to extraction/normalization; the cited evidence does not prove the selected rule family.
- `vancouver_rs_024` -> `needs_second_source_consensus`: Find table-backed or independent text evidence for the same text candidate before promotion.
- `vancouver_rs_025` -> `upstream_extraction_issue`: Send this back to extraction/normalization; the cited evidence does not prove the selected rule family.
- `vancouver_rs_026` -> `upstream_extraction_issue`: Send this back to extraction/normalization; the cited evidence does not prove the selected rule family.
- `vancouver_rs_027` -> `operator_or_direction_issue`: Confirm whether the bylaw says minimum, maximum, required, permitted, or an exception to those.
- `vancouver_rs_028` -> `operator_or_direction_issue`: Confirm whether the bylaw says minimum, maximum, required, permitted, or an exception to those.
- `vancouver_rs_036` -> `human_legal_review`: Resolve exception, covenant, approval, or notwithstanding language manually.
