# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `pipeline9_rag`
- Evidence units: 12
- Candidate rules: 72
- Verified rules: 0
- Review needed: 52
- Rejected rules: 14
- Not used / traceability only: 6
- Evidence match rate: 1.00
- Value grounding rate: 1.00
- Table context completion: 0.00
- Evidence repair suggestions: 52
- Suggestions with alternative evidence: 52
- Retry candidates from evidence repair: 36
- Evidence intelligence safe bundle retries: 1
- Evidence rerun attempts: 36
- Promotion-ready shadow reruns: 0
- Evidence bundle rerun attempts: 0
- Promotion-ready bundle reruns: 0
- Guarded bundle promotions: 0
- Rule graph nodes / edges: 230 / 638
- Cache hits / misses: 0 / 72
- Semantic high-similarity review items: 0
- Review items potentially promotable after evidence fix: 21
- Safe verifier tuning candidates: 0
- Felt verified-rule CSV rows: 0

## Review Actions

- `retry_with_better_evidence`: 18
- `human_legal_review`: 18
- `needs_second_source_consensus`: 15
- `evidence_packet_repair_candidate`: 1

## Top Review / Rejection Reasons

- `pipeline5_text_candidate_requires_review`: 72
- `unresolved_exception_cue`: 32
- `rule_object_unit_not_compatible`: 13
- `rule_family_direction_mismatch`: 10
- `upstream_extraction_requested_review`: 10
- `cross_reference_only`: 9
- `rule_object_not_supported`: 8
- `operator_not_supported`: 7
- `applies_to_not_supported`: 2
- `text_condition_not_supported`: 2
