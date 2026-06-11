# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `pipeline9_rag`
- Evidence units: 152
- Candidate rules: 428
- Verified rules: 16
- Review needed: 348
- Rejected rules: 56
- Not used / traceability only: 8
- Evidence match rate: 1.00
- Value grounding rate: 0.98
- Table context completion: 0.00
- Evidence repair suggestions: 338
- Suggestions with alternative evidence: 338
- Retry candidates from evidence repair: 307
- Evidence intelligence safe bundle retries: 227
- Evidence rerun attempts: 307
- Promotion-ready shadow reruns: 0
- Evidence bundle rerun attempts: 17
- Promotion-ready bundle reruns: 0
- Guarded bundle promotions: 0
- Rule graph nodes / edges: 1525 / 4344
- Cache hits / misses: 428 / 0
- Semantic high-similarity review items: 1
- Review items potentially promotable after evidence fix: 3
- Safe verifier tuning candidates: 0
- Felt verified-rule CSV rows: 16

## Review Actions

- `retry_with_better_evidence`: 288
- `human_legal_review`: 30
- `evidence_packet_repair_candidate`: 15
- `defer_low_priority`: 9
- `needs_second_source_consensus`: 6

## Top Review / Rejection Reasons

- `pipeline5_text_candidate_requires_review`: 401
- `operator_not_supported`: 186
- `upstream_extraction_requested_review`: 82
- `rule_object_not_supported`: 69
- `rule_family_direction_mismatch`: 56
- `rule_object_unit_not_compatible`: 46
- `unresolved_exception_cue`: 38
- `applies_to_not_supported`: 36
- `value_not_found_in_evidence`: 10
- `text_condition_not_supported`: 8
