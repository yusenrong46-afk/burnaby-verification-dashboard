"""Streamlit dashboard for verifier outputs."""

from __future__ import annotations

import argparse
import html
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "burnaby_r1_slim_pipeline5_registry"


def load_output_data(output_dir: Path) -> dict[str, Any]:
    """Load all dashboard source files from one verifier output directory."""
    # The dashboard is intentionally read-only. It consumes generated JSON
    # reports and never calls Gemini, reruns verification, or mutates outputs.
    router = _read_json(output_dir / "review_router.json", {"items": [], "summary": {}})
    relationships = _read_json(
        output_dir / "rule_relationships.json",
        {"consensus": [], "conflicts": [], "cross_family_collisions": []},
    )
    contract = _read_json(output_dir / "gis_rule_contract.json", {"rules": []})
    summary = _read_json(output_dir / "slim_summary.json", {})
    intelligence_rerun = _read_json(output_dir / "evidence_intelligence_rerun.json", {})
    legacy_rerun = _read_json(
        output_dir / "evidence_rerun_report.json",
        {"mode": "disabled", "attempts": [], "verified_after_rerun": []},
    )
    return {
        "output_dir": output_dir,
        "summary": summary,
        "validation": _read_json(output_dir / "validation_report.json", {}),
        "benchmark": _read_json(output_dir / "benchmark_report.json", {}),
        "router": router,
        "repair": _read_json(output_dir / "evidence_repair_suggestions.json", {"suggestions": []}),
        "semantic": _read_json(
            output_dir / "semantic_retrieval.json",
            {"mode": "missing", "backend": "missing", "suggestions": [], "summary": {}},
        ),
        "intelligence": _read_json(
            output_dir / "evidence_intelligence.json",
            {"mode": "missing", "items": [], "summary": {}},
        ),
        "rerun": intelligence_rerun or legacy_rerun,
        "extraction_feedback": _read_json(output_dir / "extraction_feedback.json", {"items": [], "summary": {}}),
        "evidence_units": _read_json(output_dir / "evidence_units.json", []),
        "verified": _read_json(output_dir / "verified_rules.json", []),
        "review": _read_json(output_dir / "review_needed.json", []),
        "rejected": _read_json(output_dir / "rejected_rules.json", []),
        "not_used": _read_json(output_dir / "not_used.json", []),
        "relationships": relationships,
        "contract": contract,
        "source_info": _source_info(contract, summary),
    }


def _source_info(contract: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    """Return source-document metadata for generic bylaw lookup guidance."""
    return {
        "city": contract.get("city") or summary.get("city") or "",
        "zone": contract.get("zone") or summary.get("zone") or "",
        "document": contract.get("source_document") or summary.get("source_document") or "source bylaw document",
        "url": contract.get("source_url") or summary.get("source_url") or "",
    }


def _dashboard_title(source_info: dict[str, Any]) -> str:
    """Build a concise dashboard title from run metadata."""
    city = str(source_info.get("city") or "").strip()
    zone = str(source_info.get("zone") or "").strip()
    if city and zone:
        return f"{city} {zone} Verification Dashboard"
    if city:
        return f"{city} Verification Dashboard"
    return "Verification Dashboard"


def filter_triage_items(
    items: list[dict[str, Any]],
    *,
    categories: list[str],
    priorities: list[str],
    likelihoods: list[str],
    rule_objects: list[str],
) -> list[dict[str, Any]]:
    """Apply dashboard filters to triage rows."""
    filtered = items
    if categories:
        filtered = [item for item in filtered if item.get("review_category") in categories]
    if priorities:
        filtered = [item for item in filtered if item.get("triage_priority") in priorities]
    if likelihoods:
        filtered = [item for item in filtered if item.get("likely_status") in likelihoods]
    if rule_objects:
        filtered = [item for item in filtered if item.get("rule_object") in rule_objects]
    return filtered


def compact_rule_row(rule: dict[str, Any]) -> dict[str, Any]:
    """Return one table row with the fields reviewers need first."""
    return {
        "rule_id": rule.get("rule_id"),
        "rule_object": rule.get("rule_object"),
        "scope": rule.get("constraint_scope"),
        "applies_to": rule.get("applies_to"),
        "operator": rule.get("operator"),
        "value": rule.get("value"),
        "unit": rule.get("unit"),
        "category": rule.get("review_category"),
        "priority": rule.get("triage_priority") or rule.get("review_priority"),
        "likely": rule.get("likely_status"),
        "score": rule.get("likely_correct_score"),
        "gaps": ", ".join(str(gap) for gap in rule.get("support_gaps", [])[:4]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args, _ = parser.parse_known_args()
    output_dir = Path(args.output_dir).expanduser()

    try:
        import streamlit as st
    except ModuleNotFoundError as exc:
        raise SystemExit("Streamlit is not installed. Run `pip install -r requirements.txt`.") from exc

    data = load_output_data(output_dir)

    st.set_page_config(
        page_title=_dashboard_title(data["source_info"]),
        page_icon="BV",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _style(st)

    st.sidebar.header("Filters")
    st.sidebar.caption(str(output_dir))
    router_items = data["router"].get("items", [])
    categories = st.sidebar.multiselect("Review category", _unique(router_items, "review_category"))
    priorities = st.sidebar.multiselect("Priority", _unique(router_items, "triage_priority"))
    likelihoods = st.sidebar.multiselect("Likely status", _unique(router_items, "likely_status"))
    rule_objects = st.sidebar.multiselect("Rule object", _unique(router_items, "rule_object"))
    _sidebar_guidance(st)
    filtered_items = filter_triage_items(
        router_items,
        categories=categories,
        priorities=priorities,
        likelihoods=likelihoods,
        rule_objects=rule_objects,
    )

    _render_header(st, data["source_info"], data)
    _render_kpis(st, data, filtered_items)
    _render_guidance(st)

    tabs = st.tabs(
        [
            "Overview",
            "Pipeline Flow",
            "Results",
            "Review Tree",
            "Candidate vs Verified",
            "Evidence Intelligence",
            "Extraction Feedback",
            "Rule Relationships",
            "GIS/Felt Export",
            "Code Explanation",
            "Advanced Rerun",
        ]
    )
    with tabs[0]:
        _overview_tab(st, data)
    with tabs[1]:
        _pipeline_flow_tab(st)
    with tabs[2]:
        _results_tab(st, data)
    with tabs[3]:
        _review_tree_tab(st, filtered_items, data["evidence_units"], data["source_info"])
    with tabs[4]:
        _candidate_compare_tab(st, filtered_items, data["review"], data["verified"])
    with tabs[5]:
        _intelligence_tab(st, data["intelligence"], data["source_info"])
    with tabs[6]:
        _extraction_feedback_tab(st, data["extraction_feedback"])
    with tabs[7]:
        _relationships_tab(st, data["relationships"])
    with tabs[8]:
        _export_tab(st, data["contract"], data["verified"])
    with tabs[9]:
        _structure_tab(st)
    with tabs[10]:
        _rerun_tab(st, data["rerun"], data["evidence_units"], data["source_info"])


def _overview_tab(st: Any, data: dict[str, Any]) -> None:
    validation = data["validation"]
    benchmark = data["benchmark"]
    counts = validation.get("bucket_counts", {})
    _action_summary(st, data)
    left, right = st.columns([1, 1])
    with left:
        st.subheader("Bucket Mix")
        _bar_table(st, counts)
    with right:
        st.subheader("Quality Gates")
        gates = benchmark.get("quality_gates", {}).get("gates", {})
        rows = [{"gate": key, "passed": value} for key, value in gates.items()]
        st.table(rows)

    st.subheader("Review Categories")
    _bar_rows(st, data["router"].get("summary", {}).get("category_counts", []), "name", "count")

    st.subheader("Review Action Buckets")
    _bar_rows(st, data["router"].get("summary", {}).get("action_counts", []), "name", "count")

    st.subheader("Evidence Span Issues")
    st.caption("These explain when the cited evidence is too narrow, such as a list item without its parent clause.")
    _bar_rows(st, data["router"].get("summary", {}).get("span_issue_counts", []), "name", "count")

    st.subheader("Evidence Intelligence")
    semantic = data.get("semantic", {})
    intelligence = data.get("intelligence", {})
    st.caption("Evidence Intelligence merges deterministic repair and MiniLM retrieval. It does not verify rules.")
    _bar_table(
        st,
        {
            "intelligence_items": intelligence.get("item_count", 0),
            "repair_and_semantic": intelligence.get("summary", {}).get("merged_repair_and_semantic_count", 0),
            "semantic_only": intelligence.get("summary", {}).get("semantic_only_count", 0),
            "no_auto_suggestion": intelligence.get("summary", {}).get("no_auto_suggestion_count", 0),
        },
    )

    st.subheader("Potential Mistakes")
    flags = Counter(
        flag
        for rule in data["review"]
        for flag in rule.get("potential_mistake_flags", [])
    )
    _bar_table(st, dict(flags.most_common(12)))


def _pipeline_flow_tab(st: Any) -> None:
    st.subheader("Pipeline Flow")
    st.caption("This dashboard is read-only. It explains how extraction output is routed; it does not approve rules.")
    st.markdown(
        """
<div class="flow-strip">
  <div><b>1</b><span>Pipeline 5/6 registry</span></div>
  <div><b>2</b><span>Adapter</span></div>
  <div><b>3</b><span>Evidence quality</span></div>
  <div><b>4</b><span>Deterministic verifier</span></div>
  <div><b>5</b><span>Decision policy</span></div>
  <div><b>6</b><span>Review router</span></div>
  <div><b>7</b><span>Verified-only export</span></div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.code(
        """Pipeline 5/6 registry
-> zihao_adapter.py
-> evidence quality diagnostics
-> verification.py + support_checks/text_span_proof/table_natural_logic
-> decision_policy.py
-> verified / review_needed / rejected / not_used
-> review_router.py + evidence_repair.py + rule_relationships.py
-> semantic_retrieval.py (MiniLM ranking only)
-> evidence_intelligence.py (deduplicated review evidence queue)
-> evidence_intelligence_rerun.py (shadow deterministic rerun)
-> extraction_feedback.py (upstream extraction guidance)
-> gis_rule_contract.json""",
        language="text",
    )


def _results_tab(st: Any, data: dict[str, Any]) -> None:
    st.subheader("Results")
    validation = data.get("validation", {})
    benchmark = data.get("benchmark", {})
    counts = validation.get("bucket_counts", {})
    left, right = st.columns([1, 1])
    with left:
        st.markdown("### Output Buckets")
        _bar_table(st, counts)
        st.markdown(
            """
- `verified`: source-supported and eligible for downstream export.
- `review_needed`: plausible but incomplete or ambiguous.
- `rejected`: contradicted or unsafe malformed candidate.
- `not_used`: valid extraction artifact but outside the current verification contract.
"""
        )
    with right:
        st.markdown("### Benchmark Snapshot")
        metrics = benchmark.get("rule_metrics", {})
        proposal = benchmark.get("proposal_metrics", {})
        rows = [
            {"metric": "verified_precision", "value": _metric_display(metrics.get("verified_precision"))},
            {"metric": "false_verified_count", "value": _metric_display(metrics.get("false_verified_count"), decimals=0)},
            {"metric": "verified_or_review_recall", "value": _metric_display(metrics.get("verified_or_review_recall"))},
            {"metric": "false_approval_count", "value": _metric_display(proposal.get("false_approval_count"), decimals=0)},
            {"metric": "proposal_decision_accuracy", "value": _metric_display(proposal.get("proposal_decision_accuracy"))},
        ]
        st.table(rows)


def _review_tree_tab(
    st: Any,
    items: list[dict[str, Any]],
    evidence_units: list[dict[str, Any]],
    source_info: dict[str, Any],
) -> None:
    _review_queue_tab(st, items)
    if not items:
        return
    selected = st.selectbox("Review detail", [item["rule_id"] for item in items], key="review_tree_detail")
    item = next(item for item in items if item["rule_id"] == selected)
    evidence = _evidence_by_id(evidence_units, item.get("source_evidence_id"))
    _detail_sentence_panel(
        st,
        "Review tree in plain English",
        _router_detail_sentences(item),
        evidence,
        item,
        source_info,
    )
    with st.expander("Raw review router JSON"):
        st.json(item)


def _review_queue_tab(st: Any, items: list[dict[str, Any]]) -> None:
    st.subheader(f"Review Queue ({len(items)})")
    rows = [
        {
            "rank": item.get("review_rank"),
            "rule_id": item.get("rule_id"),
            "category": item.get("review_category"),
            "priority": item.get("triage_priority"),
            "likely": item.get("likely_status"),
            "score": item.get("likely_correct_score"),
            "rule_object": item.get("rule_object"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "span_issue": item.get("span_issue_type"),
            "blocking_reason": item.get("blocking_reason"),
            "suggested_fix": item.get("suggested_fix"),
        }
        for item in items[:200]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)


def _relationships_tab(st: Any, relationships: dict[str, Any]) -> None:
    st.subheader("Rule Relationships")
    st.caption("Consensus and conflict reports are diagnostics only. They never promote a rule to verified.")
    consensus = relationships.get("consensus", [])
    conflicts = relationships.get("conflicts", [])
    collisions = relationships.get("cross_family_collisions", [])
    cols = st.columns(3)
    cols[0].metric("Consensus groups", len(consensus))
    cols[1].metric("Conflicts", len(conflicts))
    cols[2].metric("Cross-family collisions", len(collisions))
    st.markdown("### Consensus")
    st.dataframe(_display_rows(consensus[:200]), width="stretch", hide_index=True)
    st.markdown("### Conflicts")
    st.dataframe(_display_rows(conflicts[:200]), width="stretch", hide_index=True)
    st.markdown("### Cross-Family Collisions")
    st.dataframe(_display_rows(collisions[:200]), width="stretch", hide_index=True)


def _extraction_feedback_tab(st: Any, feedback: dict[str, Any]) -> None:
    """Render upstream extraction/evidence-span feedback."""
    items = feedback.get("items", [])
    summary = feedback.get("summary", {})
    st.subheader(f"Extraction Feedback ({len(items)})")
    st.caption("Concrete upstream fixes for candidate generation and evidence-span packaging.")
    cols = st.columns(3)
    cols[0].metric("Review Feedback", feedback.get("review_feedback_count", 0))
    cols[1].metric("Not-Used Feedback", feedback.get("not_used_feedback_count", 0))
    cols[2].metric("Promotion-Ready Leads", summary.get("promotion_ready_feedback_count", 0))

    left, right = st.columns([1, 1])
    with left:
        st.markdown("### Feedback Categories")
        _bar_rows(st, summary.get("feedback_category_counts", []), "name", "count")
    with right:
        st.markdown("### Upstream Actions")
        _bar_rows(st, summary.get("upstream_action_counts", []), "name", "count")

    if not items:
        st.info("No extraction feedback rows found.")
        return

    category_filter = st.multiselect("Feedback category", _unique(items, "feedback_category"))
    action_filter = st.multiselect("Upstream action", _unique(items, "upstream_action"))
    visible = items
    if category_filter:
        visible = [item for item in visible if item.get("feedback_category") in category_filter]
    if action_filter:
        visible = [item for item in visible if item.get("upstream_action") in action_filter]

    rows = [
        {
            "rule_id": item.get("rule_id"),
            "bucket": item.get("bucket"),
            "category": item.get("feedback_category"),
            "upstream_action": item.get("upstream_action"),
            "rule_object": item.get("rule_object"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "best_evidence": item.get("best_evidence_id"),
            "rerun_decision": item.get("rerun_decision"),
            "promotion_ready": item.get("promotion_ready"),
        }
        for item in visible[:300]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    selected = st.selectbox("Feedback detail", [item["rule_id"] for item in visible])
    item = next(item for item in visible if item["rule_id"] == selected)
    st.markdown("### Feedback Detail")
    _detail_sentence_panel(
        st,
        "Upstream extraction guidance",
        [
            f"Rule `{item.get('rule_id')}` is in `{item.get('bucket')}`.",
            f"Feedback category: `{item.get('feedback_category')}`.",
            f"Recommended upstream action: `{item.get('upstream_action')}`.",
            f"Instruction: {item.get('instruction')}",
            f"Rerun decision: `{item.get('rerun_decision') or 'not rerun'}`. Promotion ready: `{item.get('promotion_ready')}`.",
        ],
        {"evidence_id": item.get("best_evidence_id")},
        item,
        {"document": "source bylaw document"},
    )
    with st.expander("Raw extraction feedback JSON"):
        st.json(item)


def _export_tab(st: Any, contract: dict[str, Any], verified_rules: list[dict[str, Any]]) -> None:
    st.subheader("GIS/Felt Export Preview")
    st.caption("Only verified rules appear in the compatibility contract. Review, rejected, and not-used rules are excluded.")
    st.metric("Exported verified rules", len(contract.get("rules", verified_rules)))
    rows = [compact_rule_row(rule) for rule in contract.get("rules", verified_rules)[:200]]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    with st.expander("Raw gis_rule_contract.json"):
        st.json(contract)


def _candidate_compare_tab(
    st: Any,
    triage_items: list[dict[str, Any]],
    review_rules: list[dict[str, Any]],
    verified_rules: list[dict[str, Any]],
) -> None:
    st.subheader("Candidate vs Verified")
    st.caption("Use this view to compare the candidate claim against the closest already-verified rule before deciding whether to tune the verifier or repair evidence.")
    if not triage_items:
        st.info("No review items match the current filters.")
        return
    options = [item["rule_id"] for item in triage_items]
    selected_id = st.selectbox("Review rule", options)
    review_rule = _by_rule_id(review_rules, selected_id)
    triage_item = next((item for item in triage_items if item["rule_id"] == selected_id), {})
    verified_rule = _by_rule_id(verified_rules, triage_item.get("similar_verified_rule_id"))

    st.markdown("### Sentence-Level Claim Comparison")
    sentence_left, sentence_right = st.columns(2)
    with sentence_left:
        _sentence_card(
            st,
            "Review candidate claim",
            _rule_sentence(review_rule),
            "review",
            "Generated from the candidate's normalized fields.",
        )
    with sentence_right:
        if verified_rule:
            _sentence_card(
                st,
                "Closest verified claim",
                _rule_sentence(verified_rule),
                "verified",
                f"Similarity score: {triage_item.get('similar_verified_score')}",
            )
        else:
            _sentence_card(
                st,
                "Closest verified claim",
                "No verified comparison rule was found for this review item.",
                "neutral",
                "Use Evidence Intelligence or manual review instead.",
            )

    if verified_rule:
        st.markdown("#### Field Differences")
        st.dataframe(_display_rows(_field_comparison_rows(review_rule, verified_rule)), width="stretch", hide_index=True)

    left, right = st.columns(2)
    with left:
        st.markdown("### Review Candidate")
        st.table([compact_rule_row(review_rule)])
        st.markdown("#### Evidence")
        st.code(_source_text(review_rule), language="text")
        st.markdown("#### Suggested Fix")
        st.write(triage_item.get("suggested_fix"))
    with right:
        st.markdown("### Closest Verified Rule")
        if verified_rule:
            st.table([compact_rule_row(verified_rule)])
            st.markdown(f"Similarity score: `{triage_item.get('similar_verified_score')}`")
            st.code(_source_text(verified_rule), language="text")
        else:
            st.info("No verified comparison rule found.")


def _intelligence_tab(st: Any, intelligence: dict[str, Any], source_info: dict[str, Any]) -> None:
    """Render the deduplicated evidence intelligence queue."""
    items = intelligence.get("items", [])
    summary = intelligence.get("summary", {})
    st.subheader(f"Evidence Intelligence ({len(items)})")
    st.caption(
        "This page merges deterministic evidence repair and MiniLM semantic retrieval. "
        "It covers every review rule, but it cannot verify or promote rules by score."
    )
    metric_cols = st.columns(5)
    metric_cols[0].metric("Covered Review Rules", summary.get("review_rule_count", len(items)))
    metric_cols[1].metric("Repair + MiniLM", summary.get("merged_repair_and_semantic_count", 0))
    metric_cols[2].metric("MiniLM Only", summary.get("semantic_only_count", 0))
    metric_cols[3].metric("No Auto Suggestion", summary.get("no_auto_suggestion_count", 0))
    metric_cols[4].metric("Direct Verify", str(summary.get("direct_verification_allowed", False)))
    st.info(intelligence.get("verification_guardrail") or "Evidence intelligence is report-only.")

    if not items:
        st.info("No evidence intelligence items were produced for this run.")
        return

    action_filter = st.multiselect("Action", _unique(items, "recommended_action"))
    source_filter = st.multiselect("Intelligence source", _unique(items, "intelligence_source"))
    visible = items
    if action_filter:
        visible = [item for item in visible if item.get("recommended_action") in action_filter]
    if source_filter:
        visible = [item for item in visible if item.get("intelligence_source") in source_filter]

    rows = [
        {
            "rule_id": item.get("rule_id"),
            "action": item.get("recommended_action"),
            "source": item.get("intelligence_source"),
            "confidence": item.get("confidence"),
            "rule_object": item.get("rule_object"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "best_evidence": item.get("best_evidence_id"),
            "category": item.get("review_category"),
            "priority": item.get("priority"),
            "direct_verify": item.get("can_verify_directly"),
            "no_suggestion_reason": item.get("no_suggestion_reason"),
        }
        for item in visible[:250]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)

    selected = st.selectbox("Evidence intelligence detail", [item["rule_id"] for item in visible])
    item = next(item for item in visible if item["rule_id"] == selected)
    _detail_sentence_panel(
        st,
        "Evidence intelligence in plain English",
        _intelligence_detail_sentences(item, summary),
        _intelligence_evidence_for_lookup(item),
        item,
        source_info,
    )
    st.markdown("#### Candidate vs Suggested Evidence")
    left, right = st.columns(2)
    with left:
        _sentence_card(
            st,
            "Review candidate claim",
            item.get("candidate_sentence") or _rule_sentence(item),
            "review",
            "Structured review candidate converted to a sentence.",
        )
    with right:
        _sentence_card(
            st,
            "Best evidence lead",
            item.get("best_evidence_sentence") or "No automatic evidence lead is available.",
            "neutral",
            f"Source: {item.get('intelligence_source')} | action: {item.get('recommended_action')}",
        )
    with st.expander("Raw evidence intelligence JSON"):
        st.json(item)


def _repair_tab(st: Any, repair: dict[str, Any], source_info: dict[str, Any]) -> None:
    suggestions = repair.get("suggestions", [])
    st.subheader(f"Evidence Repair Suggestions ({len(suggestions)})")
    rows = []
    for item in suggestions[:200]:
        top = item.get("top_evidence", [{}])[0] if item.get("top_evidence") else {}
        rows.append(
            {
                "rule_id": item.get("rule_id"),
                "can_retry": item.get("can_retry_verification"),
                "confidence": item.get("best_repair_confidence"),
                "rule_object": item.get("rule_object"),
                "value": item.get("value"),
                "unit": item.get("unit"),
                "current_evidence": item.get("current_evidence_id"),
                "best_evidence": top.get("evidence_id"),
                "repairable_fields": ", ".join(item.get("repairable_fields", [])),
                "match_reasons": ", ".join(top.get("match_reasons", [])),
            }
        )
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if suggestions:
        selected = st.selectbox("Suggestion detail", [item["rule_id"] for item in suggestions])
        item = next(item for item in suggestions if item["rule_id"] == selected)
        top_evidence = item.get("top_evidence", [{}])[0] if item.get("top_evidence") else {}
        _detail_sentence_panel(
            st,
            "Evidence repair in plain English",
            _repair_detail_sentences(item, top_evidence),
            top_evidence,
            item,
            source_info,
        )
        with st.expander("Raw repair JSON"):
            st.json(item)


def _semantic_tab(st: Any, semantic: dict[str, Any], source_info: dict[str, Any]) -> None:
    suggestions = semantic.get("suggestions", [])
    st.subheader(f"MiniLM Semantic Retrieval ({len(suggestions)})")
    st.caption(
        "This page ranks semantically similar evidence spans for review items. "
        "Similarity is not proof; use it to find better evidence, then rerun deterministic verification."
    )
    metric_cols = st.columns(4)
    metric_cols[0].metric("Backend", semantic.get("backend", "missing"))
    metric_cols[1].metric("Suggestions", semantic.get("suggestion_count", len(suggestions)))
    metric_cols[2].metric("High Confidence", semantic.get("high_confidence_count", 0))
    model_label = str(semantic.get("model") or "none").split("/")[-1]
    metric_cols[3].metric("Model", model_label)
    if semantic.get("backend_message"):
        st.info(str(semantic.get("backend_message")))
    if not suggestions:
        st.info("No semantic retrieval suggestions were produced for this run.")
        return

    rows = []
    for item in suggestions[:250]:
        top = item.get("top_matches", [{}])[0] if item.get("top_matches") else {}
        rows.append(
            {
                "rule_id": item.get("rule_id"),
                "action": item.get("recommended_action"),
                "score": item.get("best_combined_score"),
                "rule_object": item.get("rule_object"),
                "value": item.get("value"),
                "unit": item.get("unit"),
                "current_evidence": item.get("current_evidence_id"),
                "best_evidence": top.get("evidence_id"),
                "semantic": top.get("semantic_score"),
                "field_bonus": top.get("field_bonus"),
                "reasons": ", ".join(top.get("match_reasons", [])),
            }
        )
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)

    selected = st.selectbox("Semantic match detail", [item["rule_id"] for item in suggestions])
    item = next(item for item in suggestions if item["rule_id"] == selected)
    top_match = item.get("top_matches", [{}])[0] if item.get("top_matches") else {}
    _detail_sentence_panel(
        st,
        "Semantic retrieval in plain English",
        _semantic_detail_sentences(item, top_match, semantic),
        top_match,
        item,
        source_info,
    )
    st.markdown("#### Candidate vs Evidence Sentences")
    sentence_left, sentence_right = st.columns(2)
    with sentence_left:
        _sentence_card(
            st,
            "Review candidate meaning",
            item.get("candidate_sentence") or _rule_sentence(item),
            "review",
            "Structured candidate fields converted to a sentence.",
        )
    with sentence_right:
        _sentence_card(
            st,
            "Best semantic evidence",
            top_match.get("evidence_sentence") or "No evidence sentence available.",
            "neutral",
            f"Combined score: {top_match.get('combined_score')}",
        )
    with st.expander("Raw semantic retrieval JSON"):
        st.json(item)


def _rerun_tab(
    st: Any,
    rerun: dict[str, Any],
    evidence_units: list[dict[str, Any]],
    source_info: dict[str, Any],
) -> None:
    attempts = rerun.get("attempts", [])
    verified = rerun.get("verified_after_rerun", [])
    st.subheader("Evidence Rerun")
    st.caption("Shadow-mode verifier reruns. These do not automatically promote rules into verified_rules.json.")
    metric_cols = st.columns(6)
    metric_cols[0].metric("Attempts", rerun.get("attempt_count", len(attempts)))
    metric_cols[1].metric("Verified After Rerun", rerun.get("verified_after_rerun_count", len(verified)))
    metric_cols[2].metric("Promotion Ready", rerun.get("promotion_ready_count", 0))
    metric_cols[3].metric("Still Review", rerun.get("review_after_rerun_count", 0))
    metric_cols[4].metric("Rejected", rerun.get("rejected_after_rerun_count", 0))
    metric_cols[5].metric("Skipped", rerun.get("skipped_count", 0))

    summary_left, summary_right = st.columns([1, 1])
    with summary_left:
        st.markdown("### Rerun Decisions")
        _bar_rows(st, rerun.get("retry_decision_counts", []), "name", "count")
    with summary_right:
        st.markdown("### Promotion Risk Flags")
        risk_rows = rerun.get("risk_flag_counts", [])
        if risk_rows:
            _bar_rows(st, risk_rows, "name", "count")
        else:
            st.caption("No risk flags reported.")

    if not attempts:
        st.info("No evidence rerun attempts found.")
        return

    left, middle, right = st.columns([1, 1, 1])
    decisions = left.multiselect("Decision", _unique(attempts, "retry_decision"))
    rule_objects = middle.multiselect("Rule object", _unique(attempts, "rule_object"))
    only_ready = right.checkbox("Promotion-ready only")
    visible = attempts
    if decisions:
        visible = [item for item in visible if item.get("retry_decision") in decisions]
    if rule_objects:
        visible = [item for item in visible if item.get("rule_object") in rule_objects]
    if only_ready:
        visible = [item for item in visible if item.get("promotion_ready")]

    ready_rows = [
        {
            "rule_id": item.get("original_rule_id"),
            "rule_object": item.get("rule_object"),
            "scope": item.get("constraint_scope"),
            "operator": item.get("operator"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "retry_evidence": item.get("retry_evidence_id"),
            "confidence": _rerun_confidence(item),
        }
        for item in attempts
        if item.get("promotion_ready")
    ]
    if ready_rows:
        st.markdown("### Promotion-Ready Shadow Verifications")
        st.dataframe(_display_rows(ready_rows), width="stretch", hide_index=True)

    rows = [
        {
            "rule_id": item.get("original_rule_id"),
            "decision": item.get("retry_decision"),
            "rule_object": item.get("rule_object"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "original_evidence": item.get("original_evidence_id"),
            "retry_evidence": item.get("retry_evidence_id"),
            "confidence": _rerun_confidence(item),
            "promotion_ready": item.get("promotion_ready"),
            "risk_flags": ", ".join(item.get("promotion_risk_flags", [])),
            "gaps": ", ".join(item.get("retry_support_gaps", [])[:4]),
        }
        for item in visible[:250]
    ]
    st.markdown(f"### Rerun Attempts ({len(visible)})")
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if visible:
        selected = st.selectbox("Rerun detail", [item["original_rule_id"] for item in visible])
        item = next(item for item in visible if item["original_rule_id"] == selected)
        evidence = _evidence_by_id(evidence_units, item.get("retry_evidence_id"))
        _detail_sentence_panel(
            st,
            "Evidence rerun in plain English",
            _rerun_detail_sentences(item),
            evidence,
            item,
            source_info,
        )
        with st.expander("Raw rerun JSON"):
            st.json(item)


def _structure_tab(st: Any) -> None:
    st.subheader("Verification Layer Structure")
    st.code(
        """Pipeline 5/6 final_rule_registry.json
  -> zihao_adapter.py
  -> slim_pipeline.py
       evidence_contract.py
  -> verification.py
       deterministic support checks
       text_span_proof.py
       table_natural_logic.py
       decision_policy.py
  -> verified / review / rejected / not_used
  -> evidence_repair.py
  -> semantic_retrieval.py (MiniLM ranking only)
  -> evidence_intelligence.py
  -> evidence_intelligence_rerun.py
  -> extraction_feedback.py
  -> review_router.py
  -> rule_relationships.py
  -> evidence_rerun.py (optional)
  -> dashboard""",
        language="text",
    )
    rows = [
        {"layer": "Adapter", "file": "zihao_adapter.py", "purpose": "Normalize Pipeline 5/6 registry into candidates and evidence packets."},
        {"layer": "Domain schema", "file": "domain_schema.py", "purpose": "Shared generic zoning families, unit aliases, and operator vocabulary."},
        {"layer": "Verifier", "file": "verification.py", "purpose": "Field-level support checks and final support gaps."},
        {"layer": "Text span proof", "file": "text_span_proof.py", "purpose": "Prose evidence proof for value, unit, operator, scope, condition."},
        {"layer": "Table proof", "file": "table_natural_logic.py", "purpose": "Table title/row/column/cell proof."},
        {"layer": "Decision policy", "file": "decision_policy.py", "purpose": "Map support gaps to verified/review/rejected/not_used."},
        {"layer": "Review router", "file": "review_router.py", "purpose": "One review tree with category, priority, next action, and reviewer instructions."},
        {"layer": "Evidence repair", "file": "evidence_repair.py", "purpose": "Find stronger existing evidence for review rules."},
        {"layer": "Semantic retrieval", "file": "semantic_retrieval.py", "purpose": "Use MiniLM similarity to rank possible evidence spans for review rules; never verifies by score."},
        {"layer": "Evidence intelligence", "file": "evidence_intelligence.py", "purpose": "Deduplicate repair and MiniLM leads into one report-only reviewer queue with explicit guardrails."},
        {"layer": "Evidence intelligence rerun", "file": "evidence_intelligence_rerun.py", "purpose": "Run selected evidence leads through the deterministic verifier in shadow mode."},
        {"layer": "Extraction feedback", "file": "extraction_feedback.py", "purpose": "Translate review/not-used outcomes into concrete upstream extraction fixes."},
        {"layer": "Rule relationships", "file": "rule_relationships.py", "purpose": "Report consensus, conflicts, and cross-family collisions without verifying rules."},
        {"layer": "Evidence rerun", "file": "evidence_rerun.py", "purpose": "Optional shadow rerun against stronger evidence."},
    ]
    st.table(rows)


def _render_kpis(st: Any, data: dict[str, Any], filtered_items: list[dict[str, Any]]) -> None:
    validation = data["validation"]
    benchmark = data["benchmark"]
    metrics = benchmark.get("rule_metrics", {})
    proposal = benchmark.get("proposal_metrics", {})
    counts = validation.get("bucket_counts", {})
    router_counts = _named_counts(data.get("router", {}).get("summary", {}).get("action_counts", []))
    rerun = data.get("rerun", {})
    intelligence_summary = data.get("intelligence", {}).get("summary", {})
    # These KPI cards put the two most actionable review-reduction paths in the
    # first screen: alternate evidence and safe verifier tuning.
    evidence_leads = max(
        0,
        int(intelligence_summary.get("review_rule_count", 0) or 0)
        - int(intelligence_summary.get("no_auto_suggestion_count", 0) or 0),
    )
    cards = [
        ("Verified", counts.get("verified", 0), "Source-supported rules", "good"),
        ("Review", counts.get("review_needed", 0), "Needs evidence or scope work", "warn"),
        ("Filtered Review", len(filtered_items), "Visible after sidebar filters", "neutral"),
        ("Better Evidence", router_counts.get("retry_with_better_evidence", 0), "Retry candidates", "action"),
        ("Evidence Leads", evidence_leads, "Repair + MiniLM suggestions", "action"),
        ("Rerun Ready", rerun.get("promotion_ready_count", 0), "Manual promotion review", "good"),
        ("Verifier Tuning", router_counts.get("safe_verifier_tuning_candidate", 0), "Generalizable rule fixes", "neutral"),
        ("Precision", _metric_display(metrics.get("verified_precision")), "Verified rule precision", "good"),
        ("False Approvals", _metric_display(proposal.get("false_approval_count"), decimals=0), "Safety gate", "good"),
    ]
    cards_html = "".join(
        f"<div class='metric metric-{html.escape(tone)}'>"
        f"<div class='metric-label'>{html.escape(label)}</div>"
        f"<div class='metric-value'>{html.escape(str(value))}</div>"
        f"<div class='metric-caption'>{html.escape(caption)}</div>"
        "</div>"
        for label, value, caption, tone in cards
    )
    st.markdown(f"<div class='metric-grid'>{cards_html}</div>", unsafe_allow_html=True)


def _render_header(st: Any, source_info: dict[str, Any], data: dict[str, Any]) -> None:
    """Render a compact product-style header for the review console."""
    title = _dashboard_title(source_info)
    document = str(source_info.get("document") or "source bylaw document").strip()
    validation = data.get("validation", {})
    benchmark = data.get("benchmark", {})
    counts = validation.get("bucket_counts", {})
    metrics = benchmark.get("rule_metrics", {})
    proposal = benchmark.get("proposal_metrics", {})
    st.markdown(
        f"""
<div class="app-header">
  <div class="header-main">
    <div class="eyebrow">Verification Review Console</div>
    <h1>{html.escape(title)}</h1>
    <p>Inspect review rules from {html.escape(document)}, compare candidate claims against verified rules, and identify the safest path to reduce review volume.</p>
  </div>
  <div class="header-status-grid">
    <div class="status-pill status-good"><span>Precision</span><b>{html.escape(_metric_display(metrics.get("verified_precision")))}</b></div>
    <div class="status-pill status-good"><span>False approvals</span><b>{html.escape(_metric_display(proposal.get("false_approval_count"), decimals=0))}</b></div>
    <div class="status-pill status-neutral"><span>Candidates</span><b>{html.escape(str(sum(int(v or 0) for v in counts.values())))}</b></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_guidance(st: Any) -> None:
    """Show the main reviewer workflow without hiding it in documentation."""
    st.markdown(
        """
<div class="guidance-grid">
  <div class="guide-card"><b>1. Start with filters</b><span>Use category, priority, likely status, and rule object to narrow the review queue.</span></div>
  <div class="guide-card"><b>2. Compare meaning</b><span>Open Candidate vs Verified and read the sentence-level claim comparison before checking tables.</span></div>
  <div class="guide-card"><b>3. Pick the next action</b><span>Use Review Tree, Evidence Intelligence, and optional Rerun to decide whether the issue is evidence, verifier tuning, or legal review.</span></div>
</div>
""",
        unsafe_allow_html=True,
    )


def _sidebar_guidance(st: Any) -> None:
    """Keep short usage instructions visible near the filters."""
    with st.sidebar.expander("How to use this dashboard", expanded=False):
        st.markdown(
            """
1. Filter the review queue to one category or rule object.
2. Use `Candidate vs Verified` to compare the generated rule sentence with the closest verified rule sentence.
3. If the meaning matches, check whether `Review Tree`, `Evidence Intelligence`, or optional `Advanced Rerun` says it is safe to tune.
4. If the issue involves exceptions, conflicts, or legal scope, keep it in human review.
"""
        )


def _action_summary(st: Any, data: dict[str, Any]) -> None:
    """Surface the highest-value review-volume reduction paths."""
    router_counts = _named_counts(data.get("router", {}).get("summary", {}).get("action_counts", []))
    rerun = data.get("rerun", {})
    cards = [
        (
            "Retry with better evidence",
            router_counts.get("retry_with_better_evidence", 0),
            "Repair evidence packets before changing verifier logic.",
        ),
        (
            "Safe verifier tuning",
            router_counts.get("safe_verifier_tuning_candidate", 0),
            "Candidates likely need general rule-pattern support.",
        ),
        (
            "Promotion-ready reruns",
            rerun.get("promotion_ready_count", 0),
            "Shadow reruns that passed conservative promotion checks.",
        ),
    ]
    html_cards = []
    for title, value, body in cards:
        html_cards.append(
            "<div class='action-card'>"
            f"<div class='action-value'>{html.escape(str(value))}</div>"
            f"<div class='action-title'>{html.escape(title)}</div>"
            f"<p>{html.escape(body)}</p>"
            "</div>"
        )
    st.markdown("<div class='action-grid'>" + "".join(html_cards) + "</div>", unsafe_allow_html=True)


def _sentence_card(st: Any, title: str, sentence: str, tone: str, caption: str = "") -> None:
    """Render one plain-language rule claim."""
    st.markdown(
        "<div class='sentence-card sentence-{}'>"
        "<div class='sentence-title'>{}</div>"
        "<p>{}</p>"
        "<span>{}</span>"
        "</div>".format(
            html.escape(tone),
            html.escape(title),
            html.escape(sentence),
            html.escape(str(caption or "")),
        ),
        unsafe_allow_html=True,
    )


def _rule_sentence(rule: dict[str, Any]) -> str:
    """Convert a structured rule into a reviewer-readable sentence.

    This is intentionally deterministic. It explains the current normalized
    fields and does not infer legal meaning beyond operator wording.
    """
    if not rule:
        return "No rule is available."

    rule_object = _humanize(rule.get("rule_object")) or "rule"
    scope = _clean_scope_prefix(_humanize(rule.get("constraint_scope")), rule_object)
    applies_to = str(rule.get("applies_to") or "").strip()
    subject = applies_to or "The relevant proposal item"
    condition = str(rule.get("condition") or "").strip()
    exception = str(rule.get("exception") or "").strip()

    value = rule.get("value")
    unit = str(rule.get("unit") or "").strip()
    value_text = _format_value_unit(value, unit)
    operator_phrase = _operator_phrase(rule.get("operator"), rule.get("constraint_type"), value_text)

    scope_phrase = f" for {_articleless(scope)}" if scope else ""
    sentence = f"{subject}: {rule_object}{scope_phrase} {operator_phrase}"
    if condition:
        sentence += f" when {condition}"
    if exception:
        sentence += f", except {exception}"
    return sentence.rstrip(" .") + "."


def _operator_phrase(operator: Any, constraint_type: Any, value_text: str) -> str:
    """Map machine operators to concise natural-language wording."""
    text = f"{operator or ''} {constraint_type or ''}".lower()
    if any(token in text for token in ("<=", "maximum", "max", "not_exceed")):
        return f"must be no more than {value_text}"
    if any(token in text for token in (">=", "minimum", "min", "at_least")):
        return f"must be at least {value_text}"
    if ">" in text:
        return f"must be more than {value_text}"
    if "<" in text:
        return f"must be less than {value_text}"
    if any(token in text for token in ("allowed", "permitted")):
        return "is permitted" if not value_text else f"is permitted with value {value_text}"
    if "required" in text:
        return "is required" if not value_text else f"is required above {value_text}"
    if value_text:
        return f"has value {value_text}"
    return "is claimed"


def _field_comparison_rows(candidate: dict[str, Any], verified: dict[str, Any]) -> list[dict[str, Any]]:
    """Build a compact candidate-vs-verified field comparison table."""
    rows = []
    for field, label in [
        ("rule_object", "Rule object"),
        ("constraint_scope", "Scope"),
        ("applies_to", "Applies to"),
        ("operator", "Operator"),
        ("value", "Value"),
        ("unit", "Unit"),
        ("condition", "Condition"),
        ("exception", "Exception"),
    ]:
        candidate_value = _clean_value(candidate.get(field))
        verified_value = _clean_value(verified.get(field))
        rows.append(
            {
                "field": label,
                "review_candidate": candidate_value,
                "verified_rule": verified_value,
                "matches": "yes" if candidate_value == verified_value else "no",
            }
        )
    return rows


def _detail_sentence_panel(
    st: Any,
    title: str,
    sentences: list[str],
    evidence: dict[str, Any],
    rule_like: dict[str, Any],
    source_info: dict[str, Any],
) -> None:
    """Render human-readable detail plus bylaw lookup instructions."""
    st.markdown(f"### {title}")
    html_sentences = []
    for index, sentence in enumerate(sentences, start=1):
        html_sentences.append(
            "<div class='detail-sentence'>"
            f"<b>{index}.</b><span>{html.escape(sentence)}</span>"
            "</div>"
        )
    st.markdown("".join(html_sentences), unsafe_allow_html=True)
    _bylaw_lookup_panel(st, evidence, rule_like, source_info)


def _repair_detail_sentences(item: dict[str, Any], top_evidence: dict[str, Any]) -> list[str]:
    """Explain one evidence repair suggestion in plain English."""
    gaps = _list_text(item.get("support_gaps", []))
    repair_fields = _list_text(item.get("repairable_fields", []))
    match_reasons = _list_text(top_evidence.get("match_reasons", []))
    evidence_id = top_evidence.get("evidence_id") or "no suggested evidence"
    confidence = _display_value(item.get("best_repair_confidence"))
    return [
        f"Candidate claim: {_rule_sentence(item)}",
        f"The original evidence `{item.get('current_evidence_id')}` kept this rule in review because of: {gaps}.",
        f"The best suggested evidence is `{evidence_id}` with repair confidence {confidence}.",
        f"The repair mainly targets: {repair_fields}. Match reasons: {match_reasons}.",
        "This page suggests better evidence only; it does not itself promote the rule into verified output.",
    ]


def _intelligence_detail_sentences(item: dict[str, Any], summary: dict[str, Any]) -> list[str]:
    """Explain one combined evidence-intelligence row in plain English."""
    source = item.get("intelligence_source") or "unknown"
    action = item.get("recommended_action") or "manual_review"
    confidence = _display_value(item.get("confidence"))
    best_evidence = item.get("best_evidence_id") or "no automatic evidence lead"
    no_suggestion = item.get("no_suggestion_reason") or "not applicable"
    return [
        f"Candidate claim: {item.get('candidate_sentence') or _rule_sentence(item)}",
        f"Evidence intelligence source: `{source}`. This combines deterministic repair and MiniLM retrieval when both are available.",
        f"Best evidence lead: `{best_evidence}` with confidence {confidence}. Recommended action: `{action}`.",
        f"No-suggestion reason: {no_suggestion}.",
        f"Guardrail: {item.get('verification_guardrail')}",
        f"Human instruction: {item.get('human_instruction')}",
    ]


def _intelligence_evidence_for_lookup(item: dict[str, Any]) -> dict[str, Any]:
    """Convert an intelligence row into evidence-like fields for lookup UI."""
    return {
        "evidence_id": item.get("best_evidence_id"),
        "page": item.get("best_evidence_page"),
        "evidence_type": item.get("best_evidence_type"),
        "evidence_quote": item.get("best_evidence_quote"),
        "evidence_text": item.get("best_evidence_quote"),
    }


def _semantic_detail_sentences(
    item: dict[str, Any],
    top_match: dict[str, Any],
    semantic: dict[str, Any],
) -> list[str]:
    """Explain one semantic retrieval suggestion in plain English."""
    backend = semantic.get("backend") or "unknown"
    score = _display_value(item.get("best_combined_score"))
    evidence_id = top_match.get("evidence_id") or "no suggested evidence"
    reasons = _list_text(top_match.get("match_reasons", []))
    return [
        f"Candidate claim: {item.get('candidate_sentence') or _rule_sentence(item)}",
        f"The `{backend}` semantic layer found `{evidence_id}` as the closest evidence candidate with combined score {score}.",
        f"Match reasons: {reasons}. The semantic score is {top_match.get('semantic_score')} and deterministic field bonus is {top_match.get('field_bonus')}.",
        f"Recommended action: {item.get('recommended_action') or 'human_review'}.",
        "This is a retrieval suggestion only. The rule should become verified only after deterministic checks prove value, unit, operator, scope, condition, and exception status.",
    ]


def _rerun_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one shadow rerun result in plain English."""
    decision = str(item.get("retry_decision") or "unknown")
    gaps = _list_text(item.get("retry_support_gaps", [])) or "none"
    risk_flags = _list_text(item.get("promotion_risk_flags", [])) or "none"
    promotion = "promotion-ready" if item.get("promotion_ready") else "not promotion-ready"
    return [
        f"Candidate claim: {_rule_sentence(item)}",
        f"The rerun replaced original evidence `{item.get('original_evidence_id')}` with retry evidence `{item.get('retry_evidence_id')}` from `{item.get('intelligence_source') or 'evidence_repair'}`.",
        f"The deterministic verifier returned `{decision}` with support gaps: {gaps}.",
        f"The shadow result is {promotion}. Promotion risk flags: {risk_flags}.",
        f"Recommendation: {item.get('promotion_recommendation') or 'inspect before promotion'}.",
    ]


def _rerun_confidence(item: dict[str, Any]) -> Any:
    """Support both legacy repair reruns and Evidence Intelligence reruns."""
    return item.get("confidence", item.get("repair_confidence"))


def _router_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one review-router item in plain English."""
    action = item.get("action_bucket") or "unclassified"
    category = item.get("review_category") or "uncategorized"
    likely = item.get("likely_status") or "unknown"
    score = _display_value(item.get("likely_correct_score"))
    gaps = _list_text(item.get("support_gaps", []))
    next_step = _sentence_fragment(item.get("next_step") or "inspect the evidence before changing verifier logic")
    instruction = _sentence_fragment(item.get("human_instruction") or "compare candidate and evidence directly")
    return [
        f"Candidate claim: {item.get('candidate_sentence') or _rule_sentence(item)}",
        f"Evidence sentence: {item.get('evidence_sentence') or 'No evidence sentence was attached.'}",
        f"The router category is `{category}` and the next-action bucket is `{action}`.",
        f"The likely status is `{likely}` with score {score}. Blocking gaps: {gaps}.",
        f"Span issue type: `{item.get('span_issue_type') or 'none'}`.",
        f"Evidence-span diagnosis: {item.get('evidence_span_diagnosis') or 'No specific span issue was detected.'}",
        f"Required evidence context: {item.get('required_evidence_context') or 'Attach local evidence that proves value, unit, operator, scope, and condition together.'}",
        f"Upstream fix: {item.get('upstream_fix') or 'No upstream span repair is suggested from structure alone.'}",
        f"Next human action: {next_step}. Human instruction: {instruction}.",
    ]


def _bylaw_lookup_panel(
    st: Any,
    evidence: dict[str, Any],
    rule_like: dict[str, Any],
    source_info: dict[str, Any],
) -> None:
    """Tell a reviewer how to find and verify the rule in the source bylaw."""
    page = evidence.get("page") or rule_like.get("page")
    quote = _quote_from_evidence(evidence)
    search_phrase = _search_phrase(rule_like, quote)
    document = str(source_info.get("document") or "source bylaw document").strip()
    city = str(source_info.get("city") or "").strip()
    zone = str(source_info.get("zone") or "").strip()
    source_url = str(source_info.get("url") or "").strip()
    source_label = " ".join(part for part in (city, zone, document) if part).strip() or document

    st.markdown("#### How to find this in the source document")
    page_text = f"page `{page}`" if page not in (None, "") else "the cited section/page from the evidence packet"
    open_step = (
        f"Open the [{source_label}]({source_url})."
        if source_url
        else f"Open `{source_label}` from the source files for this verifier run. No source URL was recorded in the contract."
    )
    st.markdown(
        f"""
1. {open_step}
2. Go to {page_text}. If the PDF page number is offset, use text search instead.
3. Search for the phrase below, then compare the candidate's value, unit, operator, scope, and condition against the bylaw wording.
4. If the passage contains words like `except`, `subject to`, `notwithstanding`, `unless`, or a covenant condition, keep the rule in human review unless the condition is explicitly modeled.
"""
    )
    st.code(search_phrase or "Search by rule object, value, unit, and applies_to fields.", language="text")
    if quote:
        st.markdown("#### Evidence quote")
        st.code(_short_display_quote(quote), language="text")


def _quote_from_evidence(evidence: dict[str, Any]) -> str:
    """Return the most useful evidence text available for reviewers."""
    return str(
        evidence.get("evidence_quote")
        or evidence.get("evidence_text")
        or evidence.get("source_context")
        or ""
    ).strip()


def _search_phrase(rule_like: dict[str, Any], quote: str) -> str:
    """Choose a short search phrase for the PDF find box."""
    if quote:
        cleaned = " ".join(quote.split())
        words = cleaned.split()
        return " ".join(words[:16])
    parts = [
        rule_like.get("rule_object"),
        rule_like.get("applies_to"),
        rule_like.get("value"),
        rule_like.get("unit"),
    ]
    return " ".join(str(part) for part in parts if part not in (None, ""))


def _short_display_quote(value: str, limit: int = 420) -> str:
    """Keep bylaw evidence quotes readable inside Streamlit."""
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _evidence_by_id(evidence_units: list[dict[str, Any]], evidence_id: Any) -> dict[str, Any]:
    """Find an evidence packet by id for bylaw lookup instructions."""
    return next((item for item in evidence_units if item.get("evidence_id") == evidence_id), {})


def _list_text(values: Any) -> str:
    """Format lists without exposing raw JSON syntax in summary sentences."""
    if not values:
        return "none"
    if isinstance(values, str):
        return values
    return ", ".join(str(value) for value in values)


def _sentence_fragment(value: Any) -> str:
    """Return text that can be safely embedded before a final period."""
    return str(value or "").strip().rstrip(".")


def _bar_table(st: Any, counts: dict[str, Any]) -> None:
    rows = [{"name": key, "count": value} for key, value in counts.items()]
    _bar_rows(st, rows, "name", "count")


def _bar_rows(st: Any, rows: list[dict[str, Any]], label_key: str, value_key: str) -> None:
    if not rows:
        st.caption("No data.")
        return
    max_value = max(float(row.get(value_key) or 0) for row in rows) or 1.0
    html_rows = []
    for row in rows:
        label = html.escape(str(row.get(label_key) or ""))
        value = float(row.get(value_key) or 0)
        width = int((value / max_value) * 100)
        html_rows.append(
            f"<div class='bar-row'><span>{label}</span><div class='bar-track'><div class='bar-fill' style='width:{width}%'></div></div><b>{int(value)}</b></div>"
        )
    st.markdown("\n".join(html_rows), unsafe_allow_html=True)


def _style(st: Any) -> None:
    st.markdown(
        """
<style>
html, body, [class*="css"] {font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;}
.stApp {background:#f5f7fb;}
.block-container {padding-top: 1.25rem; padding-bottom: 3rem; max-width: 1540px;}
section[data-testid="stSidebar"] {background:#111827;}
section[data-testid="stSidebar"] * {color:#f8fafc;}
section[data-testid="stSidebar"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {color:#111827;}
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] p {color:#cbd5e1;}
section[data-testid="stSidebar"] div[data-testid="stExpander"] {border-color:#374151; background:#172033;}
h2, h3 {color:#111827; letter-spacing:0;}
h3 {margin-top:1.35rem;}
.app-header {display:grid; grid-template-columns:minmax(0,1fr) 360px; gap:18px; align-items:stretch; border:1px solid #d7dee8; border-radius:8px; padding:22px 24px; background:#ffffff; margin-bottom:14px; box-shadow:0 12px 30px rgba(15,23,42,.07);}
.header-main {border-left:4px solid #2563eb; padding-left:16px;}
.app-header h1 {font-size:32px; line-height:1.12; margin:3px 0 8px; color:#0f172a; letter-spacing:0; font-weight:780;}
.app-header p {margin:0; color:#526070; font-size:15px; max-width:900px;}
.eyebrow {font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:#2563eb; font-weight:760;}
.header-status-grid {display:grid; grid-template-columns:1fr; gap:8px;}
.status-pill {display:flex; align-items:center; justify-content:space-between; border-radius:8px; padding:10px 12px; border:1px solid #d9e2ec; background:#f8fafc;}
.status-pill span {font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:#64748b; font-weight:760;}
.status-pill b {font-size:18px; color:#111827;}
.status-good {border-left:4px solid #15803d;}
.status-neutral {border-left:4px solid #2563eb;}
.metric-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(148px,1fr)); gap:11px; margin:12px 0 20px;}
.metric {position:relative; border:1px solid #d7dde5; border-radius:8px; padding:13px 14px 12px; background:#fff; box-shadow:0 4px 14px rgba(15,23,42,.045); min-height:104px; overflow:hidden;}
.metric:before {content:""; position:absolute; top:0; left:0; right:0; height:4px; background:#64748b;}
.metric-good:before {background:#15803d;}
.metric-warn:before {background:#b45309;}
.metric-action:before {background:#2563eb;}
.metric-neutral:before {background:#64748b;}
.metric-label {font-size:10px; line-height:1.25; color:#64748b; text-transform:uppercase; font-weight:780; overflow-wrap:normal;}
.metric-value {font-size:28px; font-weight:800; color:#0f172a; margin-top:5px;}
.metric-caption {font-size:12px; line-height:1.25; color:#667085; margin-top:4px;}
.guidance-grid, .action-grid {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:12px 0 20px;}
.guide-card, .action-card {border:1px solid #d9e0e8; border-radius:8px; background:#fff; padding:14px 15px; box-shadow:0 4px 14px rgba(15,23,42,.04);}
.guide-card {border-left:4px solid #2563eb;}
.guide-card b {display:block; color:#172033; margin-bottom:5px;}
.guide-card span, .action-card p {color:#5d6875; font-size:14px; margin:0;}
.action-card {border-top:4px solid #0f766e;}
.action-value {font-size:30px; font-weight:800; color:#0f766e;}
.action-title {font-weight:760; color:#172033; margin:1px 0 4px;}
.sentence-card {border:1px solid #d9e0e8; border-radius:8px; padding:15px 16px; min-height:142px; background:#fff; box-shadow:0 4px 14px rgba(15,23,42,.04);}
.sentence-card p {font-size:17px; line-height:1.45; color:#111827; margin:8px 0 10px;}
.sentence-card span {font-size:12px; color:#667085;}
.sentence-title {font-size:12px; text-transform:uppercase; letter-spacing:.06em; font-weight:780;}
.sentence-review {border-top:4px solid #b45309;}
.sentence-verified {border-top:4px solid #15803d;}
.sentence-neutral {border-top:4px solid #64748b;}
.detail-sentence {display:grid; grid-template-columns:28px 1fr; gap:8px; border:1px solid #d9e0e8; border-radius:8px; background:#fff; padding:11px 13px; margin:7px 0; box-shadow:0 2px 8px rgba(15,23,42,.035);}
.detail-sentence b {color:#2563eb;}
.detail-sentence span {color:#172033; line-height:1.45;}
.bar-row {display:grid; grid-template-columns:minmax(160px,250px) 1fr 52px; gap:12px; align-items:center; margin:8px 0; padding:7px 9px; background:#fff; border:1px solid #e3e8ef; border-radius:8px;}
.bar-row span {color:#344054; font-size:14px; font-weight:620;}
.bar-row b {color:#172033; text-align:right;}
.bar-track {height:12px; background:#edf2f7; border-radius:999px; overflow:hidden; border:1px solid #e2e8f0;}
.bar-fill {height:100%; background:#2563eb;}
.flow-strip {display:grid; grid-template-columns:repeat(7,minmax(0,1fr)); gap:10px; margin:14px 0 20px;}
.flow-strip div {position:relative; border:1px solid #d9e0e8; border-radius:8px; background:#fff; padding:12px 12px; min-height:92px; overflow:hidden; box-shadow:0 4px 14px rgba(15,23,42,.035);}
.flow-strip div:after {content:""; position:absolute; left:-80%; top:0; width:55%; height:100%; background:linear-gradient(90deg,transparent,rgba(37,99,235,.10),transparent); animation:flowPulse 2.8s ease-in-out infinite;}
.flow-strip b {display:inline-flex; width:24px; height:24px; align-items:center; justify-content:center; border-radius:999px; background:#dbeafe; color:#1d4ed8; margin-bottom:8px;}
.flow-strip span {display:block; font-size:13px; color:#172033; font-weight:650; line-height:1.3;}
@keyframes flowPulse {0%{left:-80%;} 55%{left:135%;} 100%{left:135%;}}
div[data-testid="stDataFrame"] {border:1px solid #d9e0e8; border-radius:8px; overflow:hidden; box-shadow:0 4px 14px rgba(15,23,42,.035);}
div[data-testid="stExpander"] {border:1px solid #d9e0e8; border-radius:8px; background:#fff;}
div[data-testid="stTabs"] button[role="tab"] {border-radius:8px 8px 0 0; padding:10px 12px; font-weight:680;}
div[data-testid="stTabs"] button[aria-selected="true"] {background:#ffffff; border-bottom:3px solid #2563eb; color:#0f172a;}
div[data-testid="stMetric"] {background:#fff; border:1px solid #d9e0e8; border-radius:8px; padding:12px 14px; box-shadow:0 4px 14px rgba(15,23,42,.035);}
table {border-radius:8px; overflow:hidden;}
code, pre {border-radius:8px;}
@media (max-width: 900px) {
  .metric-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
  .app-header {grid-template-columns:1fr;}
  .guidance-grid, .action-grid {grid-template-columns:1fr;}
  .flow-strip {grid-template-columns:1fr;}
  .bar-row {grid-template-columns:1fr;}
}
</style>
""",
        unsafe_allow_html=True,
    )


def _unique(items: list[dict[str, Any]], key: str) -> list[str]:
    return sorted({str(item.get(key)) for item in items if item.get(key) not in (None, "")})


def _named_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {str(row.get("name")): int(row.get("count") or 0) for row in rows}


def _by_rule_id(rules: list[dict[str, Any]], rule_id: Any) -> dict[str, Any]:
    return next((rule for rule in rules if rule.get("rule_id") == rule_id), {})


def _source_text(rule: dict[str, Any]) -> str:
    source = rule.get("source", {}) if isinstance(rule.get("source"), dict) else {}
    return str(source.get("evidence_text") or source.get("source_context") or "")


def _humanize(value: Any) -> str:
    return str(value or "").replace("_", " ").strip()


def _articleless(value: str) -> str:
    return value.strip()


def _format_value_unit(value: Any, unit: str) -> str:
    if value in (None, ""):
        return ""
    text = str(value).strip()
    return f"{text} {unit}".strip()


def _clean_scope_prefix(scope: str, rule_object: str) -> str:
    """Avoid duplicate display wording such as ``site site width``."""
    scope = scope.strip()
    rule_object = rule_object.strip()
    if scope and rule_object.startswith(f"{scope} "):
        return ""
    return scope


def _clean_value(value: Any) -> str:
    return str(value or "").strip()


def _display_rows(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Convert mixed JSON values into stable Streamlit table strings."""
    return [{key: _display_value(value) for key, value in row.items()} for row in rows]


def _display_value(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    if value in (None, ""):
        return ""
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)


def _metric_display(value: Any, *, decimals: int = 2) -> str:
    """Format benchmark metrics without fabricating scores for non-gold runs."""
    if value in (None, ""):
        return "n/a"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
