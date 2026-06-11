# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `pipeline5_registry`
- Evidence units: 24
- Candidate rules: 24
- Verified rules: 6
- Review needed: 14
- Rejected rules: 4
- Not used / traceability only: 0
- Evidence match rate: 1.00
- Value grounding rate: 1.00
- Table context completion: 0.00
- Evidence repair suggestions: 14
- Suggestions with alternative evidence: 14
- Retry candidates from evidence repair: 14
- Evidence intelligence safe bundle retries: 10
- Evidence rerun attempts: 14
- Promotion-ready shadow reruns: 1
- Evidence bundle rerun attempts: 10
- Promotion-ready bundle reruns: 1
- Guarded bundle promotions: 0
- Rule graph nodes / edges: 87 / 366
- Cache hits / misses: 0 / 24
- Semantic high-similarity review items: 1
- Review items potentially promotable after evidence fix: 0
- Safe verifier tuning candidates: 0
- Felt verified-rule CSV rows: 6

## Review Actions

- `retry_with_better_evidence`: 11
- `human_legal_review`: 3

## Top Review / Rejection Reasons

- `pipeline5_text_candidate_requires_review`: 18
- `applies_to_not_supported`: 13
- `operator_not_supported`: 7
- `constraint_scope_not_supported`: 7
- `unresolved_exception_cue`: 4
- `rule_object_unit_not_compatible`: 4
