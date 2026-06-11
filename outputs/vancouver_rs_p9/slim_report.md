# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `pipeline9_rag`
- Evidence units: 35
- Candidate rules: 43
- Verified rules: 2
- Review needed: 22
- Rejected rules: 13
- Not used / traceability only: 6
- Evidence match rate: 1.00
- Value grounding rate: 1.00
- Table context completion: 0.00
- Evidence repair suggestions: 21
- Suggestions with alternative evidence: 21
- Retry candidates from evidence repair: 16
- Evidence intelligence safe bundle retries: 2
- Evidence rerun attempts: 16
- Promotion-ready shadow reruns: 0
- Evidence bundle rerun attempts: 0
- Promotion-ready bundle reruns: 0
- Guarded bundle promotions: 0
- Rule graph nodes / edges: 159 / 313
- Cache hits / misses: 0 / 43
- Semantic high-similarity review items: 0
- Review items potentially promotable after evidence fix: 0
- Safe verifier tuning candidates: 0
- Felt verified-rule CSV rows: 2

## Review Actions

- `retry_with_better_evidence`: 15
- `needs_second_source_consensus`: 3
- `evidence_packet_repair_candidate`: 2
- `human_legal_review`: 1
- `defer_low_priority`: 1

## Top Review / Rejection Reasons

- `pipeline5_text_candidate_requires_review`: 40
- `rule_object_not_supported`: 19
- `operator_not_supported`: 12
- `rule_object_unit_not_compatible`: 11
- `outside_current_rule_contract`: 8
- `applies_to_not_supported`: 7
- `rule_family_direction_mismatch`: 7
- `upstream_extraction_requested_review`: 4
- `unresolved_exception_cue`: 4
- `text_condition_not_supported`: 4
