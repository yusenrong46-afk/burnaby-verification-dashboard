# Slim Verification Report

```text
Pipeline 5 candidates/evidence -> deterministic validation -> verified/review/rejected/not_used
```

- Input mode: `vancouver_prototype`
- Evidence units: 41
- Candidate rules: 45
- Verified rules: 5
- Review needed: 15
- Rejected rules: 9
- Not used / traceability only: 16
- Evidence match rate: 1.00
- Value grounding rate: 0.98
- Table context completion: 0.00
- Evidence repair suggestions: 15
- Suggestions with alternative evidence: 15
- Retry candidates from evidence repair: 10
- Evidence intelligence safe bundle retries: 3
- Evidence rerun attempts: 10
- Promotion-ready shadow reruns: 1
- Evidence bundle rerun attempts: 1
- Promotion-ready bundle reruns: 1
- Guarded bundle promotions: 0
- Rule graph nodes / edges: 153 / 302
- Cache hits / misses: 45 / 0
- Semantic high-similarity review items: 0
- Review items potentially promotable after evidence fix: 0
- Safe verifier tuning candidates: 0
- Felt verified-rule CSV rows: 5

## Review Actions

- `retry_with_better_evidence`: 9
- `upstream_candidate_issue`: 3
- `evidence_packet_repair_candidate`: 2
- `human_legal_review`: 1

## Top Review / Rejection Reasons

- `pipeline5_text_candidate_requires_review`: 40
- `rule_object_not_supported`: 27
- `outside_current_rule_contract`: 18
- `operator_not_supported`: 17
- `applies_to_not_supported`: 17
- `rule_object_unit_not_compatible`: 6
- `constraint_scope_not_supported`: 5
- `unresolved_exception_cue`: 4
- `unit_not_found_in_evidence`: 2
- `value_not_found_in_evidence`: 1
