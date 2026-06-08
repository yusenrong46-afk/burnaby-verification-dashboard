"""Public Streamlit dashboard for Burnaby verifier outputs.

This deployment is intentionally read-only. It explains verifier outputs for
classmates, reviewers, and GIS/Felt collaborators without exposing every internal
artifact as a first-screen concern.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "burnaby_r1_slim_pipeline5_registry"


BUCKET_HELP = {
    "verified": "Safe, source-supported rules. These are the only rules eligible for GIS/Felt logic.",
    "review_needed": "Plausible rules that still need stronger evidence, clearer scope, or legal review.",
    "rejected": "Contradicted or unsafe candidates. These should not be used downstream.",
    "not_used": "Traceability/process artifacts or rules outside the current GIS contract.",
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
        page_title=dashboard_title(data),
        page_icon="BV",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css(st)

    page = render_sidebar(st, data, output_dir)
    render_header(st, data)

    if page == "Overview":
        render_overview(st, data)
    elif page == "Triage":
        render_triage(st, data)
    elif page == "Candidate vs Evidence":
        render_candidate_vs_evidence(st, data)
    elif page == "Recheck Passes":
        render_recheck_passes(st, data)
    elif page == "Review Workbench":
        render_review_workbench(st, data)
    elif page == "Evidence Leads":
        render_evidence_leads(st, data)
    elif page == "GIS/Felt Handoff":
        render_gis_handoff(st, data)
    else:
        render_raw_and_code(st, data)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_output_data(output_dir: Path) -> dict[str, Any]:
    contract = read_json(output_dir / "gis_rule_contract.json", {"rules": []})
    summary = read_json(output_dir / "slim_summary.json", {})
    return {
        "output_dir": output_dir,
        "summary": summary,
        "validation": read_json(output_dir / "validation_report.json", {}),
        "benchmark": read_json(output_dir / "benchmark_report.json", {}),
        "verified": read_json(output_dir / "verified_rules.json", []),
        "review": read_json(output_dir / "review_needed.json", []),
        "rejected": read_json(output_dir / "rejected_rules.json", []),
        "not_used": read_json(output_dir / "not_used.json", []),
        "router": read_json(output_dir / "review_router.json", {"items": [], "summary": {}}),
        "intelligence": read_json(output_dir / "evidence_intelligence.json", {"items": [], "summary": {}}),
        "rerun": read_json(output_dir / "evidence_intelligence_rerun.json", {"attempts": []}),
        "repair": read_json(output_dir / "evidence_repair_suggestions.json", {"suggestions": []}),
        "relationships": read_json(output_dir / "rule_relationships.json", {}),
        "extraction_feedback": read_json(output_dir / "extraction_feedback.json", {"items": [], "summary": {}}),
        "gis_felt": read_json(output_dir / "gis_felt_export.json", {"constraints": [], "buildable_area_parameters": {}}),
        "contract": contract,
        "source": {
            "city": contract.get("city") or summary.get("city") or "Burnaby",
            "zone": contract.get("zone") or summary.get("zone") or "R1",
            "document": contract.get("source_document") or summary.get("source_document") or "source bylaw document",
            "url": contract.get("source_url") or summary.get("source_url") or "",
        },
    }


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def dashboard_title(data: dict[str, Any]) -> str:
    source = data.get("source", {})
    return f"{source.get('city', 'Bylaw')} {source.get('zone', '')} Verification".strip()


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------


def render_sidebar(st: Any, data: dict[str, Any], output_dir: Path) -> str:
    st.sidebar.markdown("### Verification Dashboard")
    st.sidebar.caption("Read-only verifier output review")
    page = st.sidebar.radio(
        "Go to",
        [
            "Overview",
            "Triage",
            "Candidate vs Evidence",
            "Recheck Passes",
            "Evidence Leads",
            "GIS/Felt Handoff",
            "Raw + Code",
        ],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Current Run")
    counts = bucket_counts(data)
    st.sidebar.metric("Verified", counts.get("verified", 0))
    st.sidebar.metric("Review needed", counts.get("review_needed", 0))
    st.sidebar.caption(str(output_dir))

    st.sidebar.markdown("---")
    st.sidebar.markdown("### How to read this")
    st.sidebar.markdown(
        """
1. **Overview** tells you what is safe now.
2. **Triage** shows review categories and priorities.
3. **Candidate vs Evidence** compares claim meaning against the cited evidence.
4. **Recheck Passes** shows which review items passed a shadow rerun.
5. **GIS/Felt Handoff** is the downstream-safe map export.
"""
    )
    return page


def render_header(st: Any, data: dict[str, Any]) -> None:
    source = data.get("source", {})
    benchmark = data.get("benchmark", {})
    metrics = benchmark.get("rule_metrics", {})
    proposal = benchmark.get("proposal_metrics", {})
    title = dashboard_title(data)
    document = source.get("document") or "source bylaw document"
    st.markdown(
        f"""
<div class="hero">
  <div>
    <div class="eyebrow">Verification layer</div>
    <h1>{escape(title)}</h1>
    <p>Candidate rules are checked against cited evidence before anything reaches GIS/Felt. Source: <b>{escape(document)}</b>.</p>
  </div>
  <div class="hero-stats">
    <div><span>Precision</span><b>{fmt_metric(metrics.get('verified_precision'))}</b></div>
    <div><span>False verified</span><b>{fmt_int(metrics.get('false_verified_count'))}</b></div>
    <div><span>False approvals</span><b>{fmt_int(proposal.get('false_approval_count'))}</b></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_overview(st: Any, data: dict[str, Any]) -> None:
    counts = bucket_counts(data)
    gis_counts = data.get("gis_felt", {}).get("export_counts", {})
    intelligence = data.get("intelligence", {}).get("summary", {})
    rerun = data.get("rerun", {})

    st.markdown("## What matters")
    cols = st.columns(4)
    metric_card(cols[0], "Verified", counts.get("verified", 0), "Safe for downstream use", "good")
    metric_card(cols[1], "Review", counts.get("review_needed", 0), "Needs human/evidence work", "warn")
    metric_card(cols[2], "GIS parameters", gis_counts.get("buildable_area_parameter_count", 0), "Map-ready keys", "good")
    metric_card(cols[3], "Promotion leads", rerun.get("promotion_ready_count", 0), "Manual review only", "neutral")

    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.markdown("### Output buckets")
        bucket_rows = [
            {"bucket": name, "count": counts.get(name, 0), "meaning": BUCKET_HELP[name]}
            for name in ["verified", "review_needed", "rejected", "not_used"]
        ]
        st.dataframe(display_rows(bucket_rows), use_container_width=True, hide_index=True, height=210)
        bar_list(st, [{"name": k, "count": v} for k, v in counts.items()], "name", "count")

    with right:
        st.markdown("### Recommended next moves")
        action_counts = named_counts(data.get("router", {}).get("summary", {}).get("action_counts", []))
        st.markdown(
            f"""
<div class="next-actions">
  <div><b>{action_counts.get('retry_with_better_evidence', 0)}</b><span>Retry with better evidence</span><p>Most review items should be fixed by better evidence spans, not looser verification.</p></div>
  <div><b>{action_counts.get('safe_verifier_tuning_candidate', 0)}</b><span>Verifier tuning candidates</span><p>Only tune these if the pattern is general across bylaws.</p></div>
  <div><b>{intelligence.get('no_auto_suggestion_count', 0)}</b><span>No automatic evidence lead</span><p>Likely legal-condition, exception, or manual review cases.</p></div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("## Pipeline in one line")
    st.markdown(
        """
<div class="flow">
  <div>Extraction registry</div><span></span><div>Adapter</div><span></span><div>Evidence checks</div><span></span><div>Verified / Review / Rejected / Not used</div><span></span><div>GIS/Felt verified export</div>
</div>
""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Review workbench
# ---------------------------------------------------------------------------


def render_triage(st: Any, data: dict[str, Any]) -> None:
    """Show the review-router triage breakdown and queue."""
    st.markdown("## Triage")
    st.caption("This page answers: which review items should be handled first, and why?")
    router = data.get("router", {})
    summary = router.get("summary", {})
    items = router.get("items", [])
    if not items:
        st.info("No triage data was found.")
        return

    top = st.columns(4)
    metric_card(top[0], "Review items", len(items), "Total routed to review", "warn")
    metric_card(top[1], "Categories", len(summary.get("category_counts", [])), "Review reason groups", "neutral")
    metric_card(top[2], "High priority", count_name(summary.get("priority_counts", []), "high"), "Review first", "warn")
    metric_card(top[3], "Likely correct", count_name(summary.get("likelihood_counts", []), "likely_correct"), "Good repair candidates", "good")

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("### Review categories")
        bar_list(st, summary.get("category_counts", []), "name", "count")
        st.markdown("### Action buckets")
        bar_list(st, summary.get("action_counts", []), "name", "count")
    with right:
        st.markdown("### Priority")
        bar_list(st, summary.get("priority_counts", []), "name", "count")
        st.markdown("### Top support gaps")
        bar_list(st, summary.get("top_support_gaps", []), "name", "count")

    st.markdown("### Triage queue")
    filters = render_review_filters(st, items)
    visible = apply_review_filters(items, filters)
    if not visible:
        st.warning("No triage rows match the current filters.")
        return
    rows = [review_queue_row(item) for item in visible[:300]]
    st.dataframe(display_rows(rows), use_container_width=True, hide_index=True, height=460)

    selected_id = st.selectbox("Open triage detail", [item.get("rule_id") for item in visible], key="triage_detail")
    selected = next((item for item in visible if item.get("rule_id") == selected_id), visible[0])
    render_review_detail(st, selected, data)


def render_candidate_vs_evidence(st: Any, data: dict[str, Any]) -> None:
    """Show sentence-level candidate claim versus cited evidence."""
    st.markdown("## Candidate vs Evidence")
    st.caption("This page answers: does the extracted candidate mean the same thing as the evidence sentence?")
    items = data.get("router", {}).get("items", [])
    if not items:
        st.info("No candidate/evidence comparison data was found.")
        return

    filters = render_review_filters(st, items)
    visible = apply_review_filters(items, filters)
    if not visible:
        st.warning("No comparison rows match the current filters.")
        return

    selected_id = st.selectbox("Choose review rule", [item.get("rule_id") for item in visible], key="candidate_evidence_rule")
    item = next((row for row in visible if row.get("rule_id") == selected_id), visible[0])
    verified = find_rule(data.get("verified", []), item.get("similar_verified_rule_id"))
    intelligence = find_rule(data.get("intelligence", {}).get("items", []), item.get("rule_id"))

    candidate, evidence = st.columns(2, gap="large")
    with candidate:
        st.markdown("### Candidate claim")
        st.markdown(
            f"""
<div class="contrast-card candidate">
  <span>Generated rule</span>
  <p>{escape(item.get('candidate_sentence') or rule_sentence(item))}</p>
</div>
""",
            unsafe_allow_html=True,
        )
        st.dataframe(display_rows([candidate_field_row(item)]), use_container_width=True, hide_index=True)

    with evidence:
        st.markdown("### Cited evidence")
        st.markdown(
            f"""
<div class="contrast-card evidence">
  <span>Evidence sentence</span>
  <p>{escape(item.get('evidence_sentence') or 'No evidence sentence was attached.')}</p>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown("#### Why it is still review")
        st.warning(item.get("blocking_reason") or list_text(item.get("support_gaps")))

    st.markdown("### Side-by-side meaning check")
    rows = [
        {"question": "Rule object", "candidate": item.get("rule_object"), "evidence / verifier signal": item.get("review_category")},
        {"question": "Value and unit", "candidate": value_unit(item), "evidence / verifier signal": "check exact value and unit in evidence sentence"},
        {"question": "Operator", "candidate": item.get("operator"), "evidence / verifier signal": "look for words like maximum, minimum, more than, required"},
        {"question": "Scope / applies_to", "candidate": item.get("applies_to") or item.get("constraint_scope"), "evidence / verifier signal": item.get("evidence_span_diagnosis")},
        {"question": "Condition / exception", "candidate": item.get("condition"), "evidence / verifier signal": "keep in review if except/subject to/notwithstanding language is unresolved"},
    ]
    st.dataframe(display_rows(rows), use_container_width=True, hide_index=True, height=240)

    lower_left, lower_right = st.columns(2, gap="large")
    with lower_left:
        st.markdown("### Closest verified rule")
        if verified:
            st.success(rule_sentence(verified))
            st.caption(f"Similarity score: {item.get('similar_verified_score')}")
        else:
            st.info("No close verified rule was found.")
    with lower_right:
        st.markdown("### Better evidence lead")
        if intelligence and intelligence.get("best_evidence_id"):
            st.info(f"{intelligence.get('best_evidence_id')} | confidence {display_value(intelligence.get('confidence'))}")
            st.code(short_quote(intelligence.get("best_evidence_quote") or intelligence.get("best_evidence_sentence")), language="text")
        else:
            st.info("No automatic evidence lead for this rule.")

    st.markdown("### Human reviewer instruction")
    st.code(bylaw_lookup_text(item, data), language="text")


def render_recheck_passes(st: Any, data: dict[str, Any]) -> None:
    """Show review candidates that pass when rerun with better evidence."""
    st.markdown("## Recheck Passes")
    st.caption("This page answers: which review rules would pass after rechecking with stronger evidence?")
    rerun = data.get("rerun", {})
    attempts = rerun.get("attempts", [])
    if not attempts:
        st.info("No shadow recheck attempts were found.")
        return

    verified_attempts = [item for item in attempts if item.get("retry_decision") == "verified"]
    promotion_ready = [item for item in attempts if item.get("promotion_ready")]
    still_review = [item for item in attempts if item.get("retry_decision") == "review_needed"]
    rejected = [item for item in attempts if item.get("retry_decision") == "rejected"]

    cols = st.columns(4)
    metric_card(cols[0], "Attempts", len(attempts), "Rules rechecked", "neutral")
    metric_card(cols[1], "Would verify", len(verified_attempts), "Passed deterministic rerun", "good")
    metric_card(cols[2], "Promotion-ready", len(promotion_ready), "No risk flags", "good")
    metric_card(cols[3], "Still blocked", len(still_review) + len(rejected), "Needs review or rejected", "warn")

    st.markdown(
        """
<div class="instruction-card">
  <b>Important guardrail</b>
  <p>These are shadow reruns. A rule should move into <code>verified_rules.json</code> only after manual promotion review confirms the stronger evidence is the correct cited source and no legal condition is missing.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    decision_filter = st.multiselect("Rerun decision", unique(attempts, "retry_decision"))
    ready_only = st.checkbox("Promotion-ready only", value=True)
    visible = attempts
    if decision_filter:
        visible = [item for item in visible if item.get("retry_decision") in decision_filter]
    if ready_only:
        visible = [item for item in visible if item.get("promotion_ready")]

    rows = [recheck_row(item) for item in visible[:300]]
    st.dataframe(display_rows(rows), use_container_width=True, hide_index=True, height=430)

    if not visible:
        st.warning("No recheck rows match the current filters.")
        return

    selected_id = st.selectbox("Open recheck detail", [item.get("original_rule_id") for item in visible])
    item = next((row for row in visible if row.get("original_rule_id") == selected_id), visible[0])
    render_recheck_detail(st, item, data)


def render_review_workbench(st: Any, data: dict[str, Any]) -> None:
    st.markdown("## Review Workbench")
    st.caption("Pick one review item, read why it is blocked, and follow the human instruction.")
    router_items = data.get("router", {}).get("items", [])
    if not router_items:
        st.info("No review-router items were found.")
        return

    filters = render_review_filters(st, router_items)
    visible = apply_review_filters(router_items, filters)
    left, right = st.columns([1.45, 1.0], gap="large")

    with left:
        st.markdown(f"### Queue ({len(visible)})")
        queue_rows = [review_queue_row(item) for item in visible[:250]]
        st.dataframe(display_rows(queue_rows), use_container_width=True, hide_index=True, height=520)

    with right:
        if not visible:
            st.warning("No review rows match the current filters.")
            return
        selected_id = st.selectbox("Open rule detail", [item.get("rule_id") for item in visible])
        item = next((row for row in visible if row.get("rule_id") == selected_id), visible[0])
        render_review_detail(st, item, data)


def render_review_filters(st: Any, items: list[dict[str, Any]]) -> dict[str, list[str]]:
    a, b, c, d = st.columns(4)
    return {
        "category": a.multiselect("Category", unique(items, "review_category")),
        "priority": b.multiselect("Priority", unique(items, "triage_priority")),
        "rule_object": c.multiselect("Rule object", unique(items, "rule_object")),
        "action": d.multiselect("Action", unique(items, "action_bucket")),
    }


def apply_review_filters(items: list[dict[str, Any]], filters: dict[str, list[str]]) -> list[dict[str, Any]]:
    visible = items
    field_map = {
        "category": "review_category",
        "priority": "triage_priority",
        "rule_object": "rule_object",
        "action": "action_bucket",
    }
    for filter_key, field in field_map.items():
        values = filters.get(filter_key, [])
        if values:
            visible = [item for item in visible if str(item.get(field)) in values]
    return visible


def review_queue_row(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "rank": item.get("review_rank"),
        "rule_id": item.get("rule_id"),
        "category": item.get("review_category"),
        "priority": item.get("triage_priority"),
        "action": item.get("action_bucket"),
        "rule": item.get("rule_object"),
        "value": item.get("value"),
        "unit": item.get("unit"),
        "why blocked": item.get("blocking_reason") or first(item.get("support_gaps")),
    }


def candidate_field_row(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "rule_id": item.get("rule_id"),
        "rule": item.get("rule_object"),
        "scope": item.get("constraint_scope"),
        "applies_to": item.get("applies_to"),
        "operator": item.get("operator"),
        "value": item.get("value"),
        "unit": item.get("unit"),
        "condition": item.get("condition"),
    }


def recheck_row(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "original_rule": item.get("original_rule_id"),
        "rerun_rule": item.get("retry_rule_id"),
        "decision": item.get("retry_decision"),
        "promotion_ready": item.get("promotion_ready"),
        "rule": item.get("rule_object"),
        "scope": item.get("constraint_scope"),
        "value": item.get("value"),
        "unit": item.get("unit"),
        "old evidence": item.get("original_evidence_id"),
        "new evidence": item.get("retry_evidence_id"),
        "confidence": item.get("confidence"),
        "risk flags": list_text(item.get("promotion_risk_flags")),
    }


def render_recheck_detail(st: Any, item: dict[str, Any], data: dict[str, Any]) -> None:
    st.markdown("### Recheck detail")
    tone = "good" if item.get("promotion_ready") else "warn"
    st.markdown(
        f"""
<div class="detail-card {escape(tone)}">
  <div class="detail-top"><b>{escape(item.get('original_rule_id'))}</b><span>{escape(item.get('retry_decision'))}</span></div>
  <h3>{escape(rule_sentence(item))}</h3>
  <p><b>Original evidence:</b> {escape(item.get('original_evidence_id'))}</p>
  <p><b>Recheck evidence:</b> {escape(item.get('retry_evidence_id'))}</p>
  <p><b>Recommendation:</b> {escape(item.get('promotion_recommendation') or 'inspect before promotion')}</p>
</div>
""",
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    with left:
        st.markdown("#### Deterministic rerun")
        st.success(f"Decision: {item.get('retry_decision')}")
        st.write(f"Evidence strength: `{display_value(item.get('retry_evidence_strength'))}`")
        st.write(f"Support gaps: `{list_text(item.get('retry_support_gaps')) or 'none'}`")
    with right:
        st.markdown("#### Promotion screen")
        if item.get("promotion_ready"):
            st.success("Promotion-ready after manual source review.")
        else:
            st.warning("Not promotion-ready.")
        st.write(f"Risk flags: `{list_text(item.get('promotion_risk_flags')) or 'none'}`")
    st.markdown("#### What to manually check")
    st.code(
        "Open the recheck evidence ID in the source/evidence files. Confirm it proves the same candidate value, unit, operator, scope, condition, and exception status before promoting.",
        language="text",
    )
    with st.expander("Raw recheck JSON"):
        st.json(item)


def render_review_detail(st: Any, item: dict[str, Any], data: dict[str, Any]) -> None:
    st.markdown("### Selected rule")
    st.markdown(
        f"""
<div class="detail-card">
  <div class="detail-top"><b>{escape(item.get('rule_id'))}</b><span>{escape(item.get('review_category'))}</span></div>
  <h3>{escape(rule_sentence(item))}</h3>
  <p><b>Why not verified:</b> {escape(item.get('blocking_reason') or list_text(item.get('support_gaps')))}</p>
  <p><b>Next action:</b> {escape(item.get('next_step') or item.get('suggested_fix') or 'Inspect the cited evidence manually.')}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    claim, evidence = st.columns(2)
    with claim:
        st.markdown("#### Candidate sentence")
        st.info(item.get("candidate_sentence") or rule_sentence(item))
    with evidence:
        st.markdown("#### Evidence sentence")
        st.warning(item.get("evidence_sentence") or "No evidence sentence was attached.")

    st.markdown("#### Human reviewer instruction")
    st.markdown(item.get("human_instruction") or "Compare the rule value, unit, operator, scope, condition, and exception against the source bylaw.")
    lookup = bylaw_lookup_text(item, data)
    st.code(lookup, language="text")

    with st.expander("Support gaps and raw rule"):
        st.json(item)


# ---------------------------------------------------------------------------
# Evidence leads
# ---------------------------------------------------------------------------


def render_evidence_leads(st: Any, data: dict[str, Any]) -> None:
    st.markdown("## Evidence Leads")
    st.caption("Evidence leads help reviewers find better source spans. They do not verify rules by similarity or confidence.")
    intelligence = data.get("intelligence", {})
    items = intelligence.get("items", [])
    summary = intelligence.get("summary", {})
    rerun = data.get("rerun", {})

    cols = st.columns(4)
    metric_card(cols[0], "Covered", summary.get("review_rule_count", len(items)), "Review rules with a row", "neutral")
    metric_card(cols[1], "Repair + semantic", summary.get("merged_repair_and_semantic_count", 0), "Both methods agree", "good")
    metric_card(cols[2], "No suggestion", summary.get("no_auto_suggestion_count", 0), "Likely legal/manual", "warn")
    metric_card(cols[3], "Rerun-ready", rerun.get("promotion_ready_count", 0), "Still manual promotion", "good")

    if not items:
        st.info("No evidence intelligence rows found.")
        return

    left, right = st.columns([1.4, 1.0], gap="large")
    with left:
        action = st.multiselect("Action", unique(items, "recommended_action"))
        source = st.multiselect("Source", unique(items, "intelligence_source"))
        visible = items
        if action:
            visible = [item for item in visible if item.get("recommended_action") in action]
        if source:
            visible = [item for item in visible if item.get("intelligence_source") in source]
        rows = [
            {
                "rule_id": item.get("rule_id"),
                "action": item.get("recommended_action"),
                "source": item.get("intelligence_source"),
                "confidence": item.get("confidence"),
                "rule": item.get("rule_object"),
                "best evidence": item.get("best_evidence_id"),
                "review category": item.get("review_category"),
            }
            for item in visible[:250]
        ]
        st.dataframe(display_rows(rows), use_container_width=True, hide_index=True, height=520)

    with right:
        selected = st.selectbox("Open evidence lead", [item.get("rule_id") for item in visible])
        item = next((row for row in visible if row.get("rule_id") == selected), visible[0])
        render_evidence_detail(st, item)


def render_evidence_detail(st: Any, item: dict[str, Any]) -> None:
    st.markdown("### Evidence lead detail")
    st.markdown(
        f"""
<div class="detail-card evidence">
  <div class="detail-top"><b>{escape(item.get('rule_id'))}</b><span>{escape(item.get('intelligence_source'))}</span></div>
  <h3>{escape(item.get('candidate_sentence') or rule_sentence(item))}</h3>
  <p><b>Best evidence lead:</b> {escape(item.get('best_evidence_id') or 'None')}</p>
  <p><b>Recommended action:</b> {escape(item.get('recommended_action') or 'manual review')}</p>
  <p><b>Guardrail:</b> Evidence ranking is not verification. Deterministic checks still decide.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown("#### Best evidence quote")
    st.code(short_quote(item.get("best_evidence_quote") or item.get("best_evidence_sentence") or "No quote available."), language="text")
    st.markdown("#### Human instruction")
    st.write(item.get("human_instruction") or "Use this evidence only as a lead, then verify value, unit, operator, scope, condition, and exception status.")
    with st.expander("Raw evidence lead"):
        st.json(item)


# ---------------------------------------------------------------------------
# GIS/Felt
# ---------------------------------------------------------------------------


def render_gis_handoff(st: Any, data: dict[str, Any]) -> None:
    st.markdown("## GIS/Felt Handoff")
    st.caption("This page is the downstream handoff. It contains only verified executable constraints plus warnings for review blockers.")
    gis = data.get("gis_felt", {})
    counts = gis.get("export_counts", {})

    cols = st.columns(4)
    metric_card(cols[0], "Verified rules", counts.get("verified_rule_count", len(data.get("verified", []))), "Input to export", "good")
    metric_card(cols[1], "Constraints", counts.get("gis_constraint_count", 0), "Executable rows", "good")
    metric_card(cols[2], "Parameters", counts.get("buildable_area_parameter_count", 0), "Map keys", "neutral")
    metric_card(cols[3], "Blockers", counts.get("review_blocker_rule_count", 0), "Show as warnings", "warn")

    params = gis.get("buildable_area_parameters", {})
    left, right = st.columns([1.25, 0.95], gap="large")
    with left:
        st.markdown("### Buildable-area parameters")
        rows = [
            {
                "parameter": key,
                "value": value.get("value"),
                "unit": value.get("unit"),
                "operator": value.get("operator"),
                "geometry target": value.get("geometry_target"),
                "source rules": ", ".join(str(x) for x in value.get("source_rule_ids", [])),
                "conditions": ", ".join(str(x) for x in value.get("conditions", [])),
            }
            for key, value in sorted(params.items())
        ]
        st.dataframe(display_rows(rows), use_container_width=True, hide_index=True, height=470)

    with right:
        st.markdown("### What GIS should do")
        st.markdown(
            """
<div class="instruction-card">
  <b>Consume</b><p><code>gis_felt_export.json</code> parameters and constraints.</p>
  <b>Do not consume</b><p>review, rejected, or not-used rules as map logic.</p>
  <b>Show warnings</b><p>Display review blockers where a relevant rule is plausible but not verified.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("### Required map layers")
    st.dataframe(display_rows(gis.get("map_layer_requirements", [])), use_container_width=True, hide_index=True, height=220)

    st.markdown("### Verified constraints")
    constraint_rows = [
        {
            "id": row.get("constraint_id"),
            "parameter": row.get("parameter_key"),
            "target": row.get("geometry_target"),
            "operator": row.get("operator"),
            "value": row.get("value"),
            "unit": row.get("unit"),
            "page": row.get("source_page"),
            "popup": row.get("felt_popup_sentence"),
        }
        for row in gis.get("constraints", [])
    ]
    st.dataframe(display_rows(constraint_rows), use_container_width=True, hide_index=True, height=420)

    blockers = gis.get("review_blockers", {})
    if blockers:
        st.markdown("### Review blockers to show as warnings")
        a, b = st.columns(2)
        with a:
            bar_list(st, blockers.get("category_counts", []), "name", "count")
        with b:
            bar_list(st, blockers.get("action_counts", []), "name", "count")


# ---------------------------------------------------------------------------
# Raw + code
# ---------------------------------------------------------------------------


def render_raw_and_code(st: Any, data: dict[str, Any]) -> None:
    st.markdown("## Raw Outputs + Code Map")
    st.caption("Use this page only when debugging or presenting the technical structure.")

    st.markdown("### Verification layer map")
    code_rows = [
        {"file": "zihao_adapter.py", "purpose": "Normalize Pipeline 5/6 registry into candidates and evidence packets."},
        {"file": "verification.py", "purpose": "Field-level deterministic support checks."},
        {"file": "text_span_proof.py", "purpose": "Proof checks for prose evidence."},
        {"file": "table_natural_logic.py", "purpose": "Proof checks for table title, row, column, and cell."},
        {"file": "decision_policy.py", "purpose": "Maps support gaps to verified/review/rejected/not_used."},
        {"file": "review_router.py", "purpose": "Turns review rules into category, priority, and human next action."},
        {"file": "evidence_intelligence.py", "purpose": "Merges deterministic repair and semantic evidence leads."},
        {"file": "gis_felt_export.py", "purpose": "Verified-only handoff for GIS/Felt."},
    ]
    st.dataframe(display_rows(code_rows), use_container_width=True, hide_index=True)

    raw_name = st.selectbox("Open raw JSON", ["validation", "benchmark", "gis_felt", "router", "intelligence", "contract"])
    st.json(data.get(raw_name, {}))


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def metric_card(container: Any, label: str, value: Any, caption: str, tone: str) -> None:
    container.markdown(
        f"""
<div class="metric-card {escape(tone)}">
  <span>{escape(label)}</span>
  <b>{escape(value)}</b>
  <p>{escape(caption)}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def bar_list(st: Any, rows: list[dict[str, Any]], label_key: str, value_key: str) -> None:
    if not rows:
        st.caption("No data.")
        return
    max_value = max(float(row.get(value_key) or 0) for row in rows) or 1.0
    html_rows = []
    for row in rows:
        label = escape(row.get(label_key))
        value = float(row.get(value_key) or 0)
        width = int((value / max_value) * 100)
        html_rows.append(
            f"<div class='bar-row'><span>{label}</span><div><i style='width:{width}%'></i></div><b>{int(value)}</b></div>"
        )
    st.markdown("".join(html_rows), unsafe_allow_html=True)


def bucket_counts(data: dict[str, Any]) -> dict[str, int]:
    validation_counts = data.get("validation", {}).get("bucket_counts", {})
    if validation_counts:
        return {str(k): int(v or 0) for k, v in validation_counts.items()}
    return {
        "verified": len(data.get("verified", [])),
        "review_needed": len(data.get("review", [])),
        "rejected": len(data.get("rejected", [])),
        "not_used": len(data.get("not_used", [])),
    }


def named_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {str(row.get("name")): int(row.get("count") or 0) for row in rows}


def count_name(rows: list[dict[str, Any]], name: str) -> int:
    return named_counts(rows).get(name, 0)


def find_rule(rows: list[dict[str, Any]], rule_id: Any) -> dict[str, Any]:
    return next((row for row in rows if row.get("rule_id") == rule_id), {})


def unique(items: list[dict[str, Any]], key: str) -> list[str]:
    return sorted({str(item.get(key)) for item in items if item.get(key) not in (None, "")})


def display_rows(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{str(k): display_value(v) for k, v in row.items()} for row in rows]


def display_value(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    if value in (None, ""):
        return ""
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    if isinstance(value, list):
        return ", ".join(str(x) for x in value)
    return str(value)


def fmt_metric(value: Any) -> str:
    if value in (None, ""):
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def fmt_int(value: Any) -> str:
    if value in (None, ""):
        return "0"
    try:
        return str(int(value))
    except (TypeError, ValueError):
        return str(value)


def rule_sentence(rule: dict[str, Any]) -> str:
    subject = str(rule.get("applies_to") or "The proposal item").strip()
    rule_object = humanize(rule.get("rule_object") or "rule")
    scope = humanize(rule.get("constraint_scope") or "")
    operator = operator_phrase(rule.get("operator"), rule.get("constraint_type"), value_unit(rule))
    condition = str(rule.get("condition") or "").strip()
    sentence = f"{subject}: {rule_object}"
    if scope and scope not in rule_object:
        sentence += f" for {scope}"
    sentence += f" {operator}"
    if condition:
        sentence += f" when {condition}"
    return sentence.rstrip(" .") + "."


def operator_phrase(operator: Any, constraint_type: Any, value_text: str) -> str:
    text = f"{operator or ''} {constraint_type or ''}".lower()
    if any(token in text for token in ("<=", "maximum", "max")):
        return f"must be no more than {value_text}".strip()
    if any(token in text for token in (">=", "minimum", "min")):
        return f"must be at least {value_text}".strip()
    if ">" in text:
        return f"must be more than {value_text}".strip()
    if "<" in text:
        return f"must be less than {value_text}".strip()
    if "allowed" in text or "permitted" in text:
        return "is permitted"
    if "required" in text:
        return "is required"
    return f"has value {value_text}".strip()


def value_unit(rule: dict[str, Any]) -> str:
    value = rule.get("value")
    unit = rule.get("unit")
    return " ".join(str(x) for x in (value, unit) if x not in (None, ""))


def bylaw_lookup_text(item: dict[str, Any], data: dict[str, Any]) -> str:
    source = data.get("source", {})
    page = item.get("source_page") or item.get("page") or "cited page"
    phrase = item.get("evidence_sentence") or item.get("candidate_sentence") or rule_sentence(item)
    return (
        f"Document: {source.get('document')}\n"
        f"Page: {page}\n"
        f"Search phrase: {short_quote(phrase, 180)}\n"
        "Check: value, unit, operator, scope/applies_to, condition, and exception wording."
    )


def first(values: Any) -> str:
    if isinstance(values, list) and values:
        return str(values[0])
    return str(values or "")


def list_text(values: Any) -> str:
    if isinstance(values, list):
        return ", ".join(str(v) for v in values)
    return str(values or "")


def short_quote(value: Any, limit: int = 420) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def humanize(value: Any) -> str:
    return str(value or "").replace("_", " ").strip()


def escape(value: Any) -> str:
    import html

    return html.escape(str(value if value is not None else ""))


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------


def inject_css(st: Any) -> None:
    st.markdown(
        """
<style>
:root {--ink:#172033; --muted:#657083; --line:#dbe3ef; --panel:#ffffff; --bg:#f6f8fb; --blue:#2563eb; --green:#15803d; --amber:#b45309; --red:#b91c1c;}
.stApp {background:var(--bg); color:var(--ink);}
.block-container {max-width:1480px; padding-top:1.2rem; padding-left:2rem; padding-right:2rem;}
section[data-testid="stSidebar"] {background:#ffffff; border-right:1px solid var(--line);}
section[data-testid="stSidebar"] * {color:var(--ink);}
section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] p {color:var(--muted);}
section[data-testid="stSidebar"] div[role="radiogroup"] label {border:1px solid var(--line); border-radius:8px; padding:7px 10px; margin:5px 0; background:#f8fafc;}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {background:#eef4ff; border-color:#bcd3ff;}
h1, h2, h3 {letter-spacing:0; color:var(--ink);} h2 {margin-top:.6rem;} h3 {margin-top:1rem;}
.hero {display:grid; grid-template-columns:minmax(0,1fr) 360px; gap:18px; background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:22px 24px; margin-bottom:18px; box-shadow:0 10px 30px rgba(20,31,53,.06);}
.hero h1 {font-size:34px; margin:.1rem 0 .45rem; line-height:1.1;} .hero p {margin:0; color:var(--muted); font-size:15px;}
.eyebrow {font-size:12px; color:var(--blue); text-transform:uppercase; letter-spacing:.08em; font-weight:800;}
.hero-stats {display:grid; grid-template-columns:1fr; gap:8px;} .hero-stats div {display:flex; justify-content:space-between; align-items:center; border:1px solid var(--line); border-left:4px solid var(--green); border-radius:8px; padding:10px 12px; background:#fbfdff;} .hero-stats span {font-size:12px; color:var(--muted); text-transform:uppercase; font-weight:800;} .hero-stats b {font-size:20px;}
.metric-card {background:#fff; border:1px solid var(--line); border-top:4px solid var(--blue); border-radius:10px; padding:14px 16px; min-height:112px; box-shadow:0 6px 20px rgba(20,31,53,.045);} .metric-card.good {border-top-color:var(--green);} .metric-card.warn {border-top-color:var(--amber);} .metric-card.neutral {border-top-color:var(--blue);} .metric-card span {display:block; color:var(--muted); text-transform:uppercase; font-size:11px; font-weight:800;} .metric-card b {display:block; font-size:32px; margin:4px 0; color:var(--ink);} .metric-card p {font-size:13px; color:var(--muted); margin:0; line-height:1.3;}
.next-actions {display:grid; gap:10px;} .next-actions div, .instruction-card, .detail-card {background:#fff; border:1px solid var(--line); border-radius:10px; padding:15px 16px; box-shadow:0 5px 16px rgba(20,31,53,.04);} .next-actions b {font-size:28px; color:var(--blue); margin-right:8px;} .next-actions span {font-weight:800;} .next-actions p, .instruction-card p, .detail-card p {color:var(--muted); margin:.25rem 0 .2rem;}
.flow {display:grid; grid-template-columns:1fr 22px 1fr 22px 1fr 22px 1.5fr 22px 1.2fr; gap:8px; align-items:center;} .flow div {background:#fff; border:1px solid var(--line); border-radius:10px; padding:13px 14px; text-align:center; font-weight:800; min-height:64px; display:flex; align-items:center; justify-content:center;} .flow span:before {content:"→"; color:var(--blue); font-weight:900; font-size:22px;}
.detail-card {border-left:4px solid var(--blue); margin-bottom:12px;} .detail-card.evidence {border-left-color:var(--green);} .detail-card h3 {font-size:18px; line-height:1.35; margin:.65rem 0;} .detail-top {display:flex; justify-content:space-between; gap:12px;} .detail-top span {background:#eef4ff; color:#1d4ed8; border-radius:999px; padding:3px 9px; font-size:12px; font-weight:800;}
.contrast-card {background:#fff; border:1px solid var(--line); border-radius:10px; padding:18px 18px; min-height:170px; box-shadow:0 5px 16px rgba(20,31,53,.04); border-top:4px solid var(--blue);}
.contrast-card.evidence {border-top-color:var(--green);}
.contrast-card.candidate {border-top-color:var(--amber);}
.contrast-card span {display:block; color:var(--muted); text-transform:uppercase; font-size:11px; font-weight:800; margin-bottom:8px;}
.contrast-card p {font-size:17px; line-height:1.45; margin:0; color:var(--ink);}
.bar-row {display:grid; grid-template-columns:minmax(140px,220px) 1fr 48px; gap:10px; align-items:center; margin:7px 0; background:#fff; border:1px solid var(--line); border-radius:8px; padding:8px 10px;} .bar-row span {font-weight:700; color:#334155;} .bar-row div {height:12px; background:#e8eef7; border-radius:999px; overflow:hidden;} .bar-row i {display:block; height:100%; background:var(--blue);} .bar-row b {text-align:right;}
div[data-testid="stDataFrame"] {border:1px solid var(--line); border-radius:10px; overflow:hidden; box-shadow:0 5px 16px rgba(20,31,53,.04);} div[data-testid="stMetric"] {background:#fff; border:1px solid var(--line); border-radius:10px; padding:12px 14px;}
code, pre {border-radius:8px;} div[data-testid="stExpander"] {background:#fff; border:1px solid var(--line); border-radius:10px;}
@media (max-width:900px) {.hero {grid-template-columns:1fr;} .flow {grid-template-columns:1fr;} .flow span {display:none;} .block-container {padding-left:1rem; padding-right:1rem;}}
</style>
""",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
