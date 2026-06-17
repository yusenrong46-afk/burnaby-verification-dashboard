# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `native_v3_rag_llm`
- Evidence units: 112
- Candidate rules: 112
- Verified rules: 84
- Review needed: 28
- Rejected rules: 0
- Not used / traceability only: 0
- Evidence match rate: 1.00
- Value grounding rate: 1.00
- Table context completion: 1.00
- Evidence repair suggestions: 26
- Suggestions with alternative evidence: 26
- Retry candidates from evidence repair: 23
- Evidence intelligence safe bundle retries: 6
- Evidence rerun attempts: 23
- Promotion-ready shadow reruns: 0
- Evidence bundle rerun attempts: 7
- Promotion-ready bundle reruns: 1
- Guarded bundle promotions: 1
- Rule graph nodes / edges: 460 / 2099
- Proof DAG sidecar entries: 112
- Cache hits / misses: 0 / 112
- Semantic high-similarity review items: 3
- Review items potentially promotable after evidence fix: 1
- Safe verifier tuning candidates: 0
- Felt verified-rule CSV rows: 83

## Review Actions

- `retry_with_better_evidence`: 22
- `evidence_packet_repair_candidate`: 2
- `human_legal_review`: 2
- `needs_second_source_consensus`: 1
- `defer_low_priority`: 1

## Top Review / Rejection Reasons

- `text_candidate_requires_review`: 26
- `rule_object_not_supported`: 9
- `rule_family_direction_mismatch`: 8
- `upstream_extraction_requested_review`: 7
- `operator_not_supported`: 7
- `constraint_scope_not_supported`: 5
- `applies_to_not_supported`: 5
- `range_bound_not_maximum`: 3
- `text_condition_not_supported`: 3
- `extraction_source_fidelity_hold`: 2
