# Burnaby R1 Rule Verification Prototype

This project is a verification-first prototype for Burnaby R1 zoning rules.
Zihao's Pipeline 5 proposes extracted rules; this verifier checks whether each
candidate is actually supported by its cited evidence before it can enter the
GIS rule contract.

```text
Zihao Pipeline 5 final_rule_registry.json
        -> Pipeline 5 adapter
        -> deterministic verifier
        -> verified / review_needed / rejected / not_used
        -> verified-only compatibility contract + benchmark
```

## Core Idea

Extraction proposes rules. Verification proves rules. GIS receives only
verified, source-supported rules. Uncertain rules go to review.

The verifier checks each candidate field by field:

```text
value, unit, operator, rule object, applies_to, scope, condition, exception
```

For table evidence, the verifier also uses a lightweight TabVer-style proof from
the table title, row header, column header, and cell value. Confidence and
Bayesian-lite evidence strength are only used for review triage; they never
override deterministic support checks.

## Run

From this folder:

```bash
python3 scripts/run_pipeline5_extraction.py
python3 scripts/run_slim_verifier.py
python3 benchmark/evaluate_benchmark.py \
  --output-dir outputs/burnaby_r1_slim_pipeline5_registry
```

MiniLM semantic retrieval is optional but recommended for review triage. Install
and run it with the same Python environment:

```bash
python3 -m pip install -r requirements-minilm.txt
python3 scripts/run_slim_verifier.py
```

If `sentence-transformers` is not installed, the verifier still runs safely and
uses lexical fallback suggestions. Verification decisions are unchanged either
way.

The default input is Zihao Pipeline 5:

```text
../w2025-data599-capstone-projects-green-metrics-technology/code/
  prototype_pipeline_5/outputs/burnaby/rule_extraction/final_rule_registry.json
```

`scripts/run_pipeline5_extraction.py` checks whether the Pipeline 5 notebook can
be executed locally. A fresh extraction requires `GEMINI_API_KEY`, Jupyter /
nbconvert, and the Gemini SDK. If those are present, run:

```bash
python3 scripts/run_pipeline5_extraction.py --execute
```

## Output Files

The final demo output is:

```text
outputs/burnaby_r1_slim_pipeline5_registry/
```

Important files:

```text
verified_rules.json          rules proven by cited evidence
review_needed.json           plausible or useful rules that need human review
rejected_rules.json          candidates contradicted or unsafe
not_used.json                cross-references or out-of-contract rules kept for audit
gis_rule_contract.json       verified-only compatibility export
benchmark_report.json        machine-readable benchmark metrics
benchmark_report.md          readable benchmark summary
validation_report.json       compact dashboard-ready validation split
evidence_quality_report.json evidence packet quality diagnostics
review_router.json           unified review tree with category, priority, and next action
review_router_report.md      readable review-router summary
evidence_repair_suggestions.json  deterministic evidence-repair suggestions
evidence_repair_report.md    readable evidence-repair summary
semantic_retrieval.json      MiniLM evidence-ranking suggestions for review rules
semantic_retrieval_report.md readable MiniLM retrieval summary
evidence_intelligence.json   deduplicated repair + MiniLM review evidence queue
evidence_intelligence_report.md readable combined evidence-intelligence summary
evidence_intelligence_rerun.json deterministic shadow reruns from evidence intelligence
evidence_intelligence_rerun_report.md readable combined rerun summary
promotion_ready.json         shadow-verified reruns ready for manual promotion review
extraction_feedback.json     upstream candidate/evidence-span feedback
extraction_feedback_report.md readable upstream feedback summary
evidence_rerun_report.json   optional shadow rerun results when enabled
evidence_rerun_report.md     optional readable shadow-rerun summary
evidence_rerun_verified.json optional shadow-verified reruns, not auto-promoted
evidence_rerun_promotion_ready.json optional reruns passing promotion risk screen
pipeline5_extraction_preflight.json  Pipeline 5 execution readiness check
rule_relationships.json      reporting-only consensus, conflicts, and collisions
slim_summary.json            run summary and top review reasons
pipeline_diagram.mmd         Mermaid pipeline diagram
benchmark_diagram.mmd        Mermaid benchmark diagram
```

GIS should consume only:

```text
outputs/burnaby_r1_slim_pipeline5_registry/gis_rule_contract.json
```

## Current Benchmark

Current Pipeline 5 baseline:

```text
candidate_recall = 1.00
extraction_coverage_recall = 1.00
verifier_retention_rate = 1.00
verified_gold_recall = 0.45
verified_or_review_recall = 1.00
verified_precision = 1.00
false_verified_count = 0
false_approval_count = 0
source_support_failures = 0
proposal_decision_accuracy = 1.00
proof_decision_mismatch_count = 0
verified_rules = 18
review_needed = 81
rejected_rules = 20
not_used_rules = 23
semantic_retrieval_suggestions = 77
semantic_retrieval_high_confidence = 23
```

The safety profile is strong: no false verified rules, no false approvals, and
no verified source-support failures. Proposal decisions also match the current
GIS contract benchmark. The latest Pipeline 5 registry now covers every gold
rule either as verified or review-needed:

```text
verified_or_review_recall = 1.00
target = 0.90
```

The next product work is to raise verified recall while keeping the same safety
gates. Pipeline 5/6 text-block rules can now verify when they have deterministic
span proof and independent source consensus; text rules with unsupported
material conditions remain in `review_needed.json`. Stage 2 now includes a
MiniLM semantic retrieval layer and a shadow evidence-rerun path. MiniLM ranks
likely better evidence spans for review rules, but it does not verify rules by
similarity score. The deterministic verifier remains the trust gate.

## Dashboard

The review dashboard reads the output folder and shows benchmark gates, review
router categories, candidate-vs-verified comparisons, the combined Evidence
Intelligence queue, deterministic shadow-rerun results, extraction feedback,
rule-relationship diagnostics, verifier structure, and Pipeline 5/6 source
status.

```bash
streamlit run dashboard/streamlit_app.py --server.port 8502
```

## Project Map

```text
benchmark/      gold rules, proposal cases, evaluator
configs/        Burnaby R1 verifier config
dashboard/      Streamlit review/verification dashboard
docs/           presentation-ready explanations and final plan
outputs/        final Pipeline 5 demo outputs
schemas/        GIS contract schema
scripts/        runner for the slim verifier
src/            adapter, verifier, proof helpers, compliance checker
tests/          unit tests for verifier, adapter, and evidence quality
```

## Key Files

```text
scripts/run_slim_verifier.py
src/burnaby_prototype/zihao_adapter.py
src/burnaby_prototype/verification.py
src/burnaby_prototype/table_natural_logic.py
src/burnaby_prototype/rule_claims.py
src/burnaby_prototype/slim_pipeline.py
src/burnaby_prototype/compliance.py
benchmark/evaluate_benchmark.py
```

For a line-by-line walkthrough of the verification layer, see:

```text
docs/verification_layer_deep_dive.md
```

## Safety Gates

The benchmark goals that must stay true are:

```text
verified_precision = 1.00
false_verified_count = 0
false_approval_count = 0
verified_source_support_failed_count = 0
proof_decision_mismatch_count = 0
```

If a rule is uncertain, it belongs in `review_needed.json`, not
`verified_rules.json`.
