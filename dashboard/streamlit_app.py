"""Streamlit dashboard for Burnaby verifier outputs."""

from __future__ import annotations

import argparse
import html
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "burnaby_r1_slim_pipeline5_registry"
SOURCE_DOCUMENT_URL = "https://www.burnaby.ca/sites/default/files/acquiadam/2024-07/R1Small-Scale-Multi-Unit-Housing-District.pdf"


def load_output_data(output_dir: Path) -> dict[str, Any]:
    """Load all dashboard source files from one verifier output directory."""
    # The dashboard is intentionally read-only. It consumes generated JSON
    # reports and never calls Gemini, reruns verification, or mutates outputs.
    return {
        "output_dir": output_dir,
        "validation": _read_json(output_dir / "validation_report.json", {}),
        "benchmark": _read_json(output_dir / "benchmark_report.json", {}),
        "triage": _read_json(output_dir / "review_triage.json", {"items": [], "summary": {}}),
        "repair": _read_json(output_dir / "evidence_repair_suggestions.json", {"suggestions": []}),
        "rerun": _read_json(output_dir / "evidence_rerun_report.json", {"attempts": [], "verified_after_rerun": []}),
        "audit": _read_json(output_dir / "review_audit.json", {"items": [], "summary": {}}),
        "evidence_units": _read_json(output_dir / "evidence_units.json", []),
        "verified": _read_json(output_dir / "verified_rules.json", []),
        "review": _read_json(output_dir / "review_needed.json", []),
        "rejected": _read_json(output_dir / "rejected_rules.json", []),
        "not_used": _read_json(output_dir / "not_used.json", []),
        "consensus": _read_json(output_dir / "rule_consensus.json", []),
        "conflicts": _read_json(output_dir / "rule_conflicts.json", []),
        "preflight": _read_json(output_dir / "pipeline5_extraction_preflight.json", {}),
    }


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

    st.set_page_config(
        page_title="Burnaby Verification Dashboard",
        page_icon="BV",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _style(st)
    data = load_output_data(output_dir)

    st.sidebar.header("Filters")
    st.sidebar.caption(str(output_dir))
    triage_items = data["triage"].get("items", [])
    categories = st.sidebar.multiselect("Review category", _unique(triage_items, "review_category"))
    priorities = st.sidebar.multiselect("Priority", _unique(triage_items, "triage_priority"))
    likelihoods = st.sidebar.multiselect("Likely status", _unique(triage_items, "likely_status"))
    rule_objects = st.sidebar.multiselect("Rule object", _unique(triage_items, "rule_object"))
    _sidebar_guidance(st)
    filtered_items = filter_triage_items(
        triage_items,
        categories=categories,
        priorities=priorities,
        likelihoods=likelihoods,
        rule_objects=rule_objects,
    )

    _render_header(st)
    _render_kpis(st, data, filtered_items)
    _render_guidance(st)

    tabs = st.tabs(
        [
            "Overview",
            "Review Queue",
            "Candidate vs Verified",
            "Evidence Repair",
            "Evidence Rerun",
            "Review Audit",
            "Verification Structure",
            "Extraction Preflight",
        ]
    )
    with tabs[0]:
        _overview_tab(st, data)
    with tabs[1]:
        _review_queue_tab(st, filtered_items)
    with tabs[2]:
        _candidate_compare_tab(st, filtered_items, data["review"], data["verified"])
    with tabs[3]:
        _repair_tab(st, data["repair"])
    with tabs[4]:
        _rerun_tab(st, data["rerun"], data["evidence_units"])
    with tabs[5]:
        _audit_tab(st, data["audit"], data["evidence_units"])
    with tabs[6]:
        _structure_tab(st)
    with tabs[7]:
        _preflight_tab(st, data["preflight"])


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
    _bar_rows(st, data["triage"].get("summary", {}).get("category_counts", []), "name", "count")

    st.subheader("Review Action Buckets")
    _bar_rows(st, data["audit"].get("summary", {}).get("action_counts", []), "name", "count")

    st.subheader("Potential Mistakes")
    flags = Counter(
        flag
        for rule in data["review"]
        for flag in rule.get("potential_mistake_flags", [])
    )
    _bar_table(st, dict(flags.most_common(12)))


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
            "blocking_reason": item.get("blocking_reason"),
            "suggested_fix": item.get("suggested_fix"),
        }
        for item in items[:200]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)


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
                "Use evidence repair or manual review instead.",
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


def _repair_tab(st: Any, repair: dict[str, Any]) -> None:
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
        )
        with st.expander("Raw repair JSON"):
            st.json(item)


def _rerun_tab(st: Any, rerun: dict[str, Any], evidence_units: list[dict[str, Any]]) -> None:
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
            "confidence": item.get("repair_confidence"),
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
            "confidence": item.get("repair_confidence"),
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
        )
        with st.expander("Raw rerun JSON"):
            st.json(item)


def _audit_tab(st: Any, audit: dict[str, Any], evidence_units: list[dict[str, Any]]) -> None:
    items = audit.get("items", [])
    st.subheader(f"Review Audit ({len(items)})")
    st.caption("Action buckets explain what kind of work should reduce review volume. They do not change verification decisions.")
    # Filter by next-action bucket so the reviewer can focus on one workflow:
    # evidence retry, verifier tuning, legal review, upstream issue, etc.
    actions = st.multiselect("Action bucket", _unique(items, "action_bucket"))
    if actions:
        items = [item for item in items if item.get("action_bucket") in actions]
    rows = [
        {
            "rule_id": item.get("rule_id"),
            "action": item.get("action_bucket"),
            "category": item.get("review_category"),
            "likely": item.get("likely_status"),
            "score": item.get("likely_correct_score"),
            "rule_object": item.get("rule_object"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "can_retry": item.get("can_retry_verification"),
            "repair_evidence": item.get("best_repair_evidence_id"),
            "next_step": item.get("next_step"),
        }
        for item in items[:250]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    recommendations = audit.get("summary", {}).get("recommendations", [])
    if recommendations:
        st.markdown("### Recommendations")
        for recommendation in recommendations:
            st.write(f"- {recommendation}")
    if items:
        selected = st.selectbox("Audit detail", [item["rule_id"] for item in items])
        item = next(item for item in items if item["rule_id"] == selected)
        evidence = _evidence_by_id(evidence_units, item.get("best_repair_evidence_id"))
        _detail_sentence_panel(
            st,
            "Review audit in plain English",
            _audit_detail_sentences(item),
            evidence,
            item,
        )
        with st.expander("Raw audit JSON"):
            st.json(item)


def _structure_tab(st: Any) -> None:
    st.subheader("Verification Layer Structure")
    st.code(
        """Pipeline 5 final_rule_registry.json
  -> zihao_adapter.py
  -> slim_pipeline.py
  -> verification.py
       deterministic support checks
       text_span_proof.py
       table_natural_logic.py
       decision_policy.py
  -> verified / review / rejected / not_used
  -> review_triage.py
  -> evidence_repair.py
  -> evidence_rerun.py
  -> review_audit.py
  -> dashboard""",
        language="text",
    )
    rows = [
        {"layer": "Adapter", "file": "zihao_adapter.py", "purpose": "Normalize Pipeline 5 registry into candidates and evidence packets."},
        {"layer": "Verifier", "file": "verification.py", "purpose": "Field-level support checks and final support gaps."},
        {"layer": "Text span proof", "file": "text_span_proof.py", "purpose": "Prose evidence proof for value, unit, operator, scope, condition."},
        {"layer": "Table proof", "file": "table_natural_logic.py", "purpose": "Table title/row/column/cell proof."},
        {"layer": "Decision policy", "file": "decision_policy.py", "purpose": "Map support gaps to verified/review/rejected/not_used."},
        {"layer": "Review triage", "file": "review_triage.py", "purpose": "Rank review queue and identify likely mistakes."},
        {"layer": "Evidence repair", "file": "evidence_repair.py", "purpose": "Find stronger existing evidence for review rules."},
        {"layer": "Evidence rerun", "file": "evidence_rerun.py", "purpose": "Rerun repairable candidates against stronger evidence in shadow mode."},
        {"layer": "Review audit", "file": "review_audit.py", "purpose": "Group review rules by next action: repair evidence, tune verifier, legal review, or upstream issue."},
    ]
    st.table(rows)


def _preflight_tab(st: Any, preflight: dict[str, Any]) -> None:
    st.subheader("Pipeline 5 Extraction Preflight")
    if not preflight:
        st.info("No preflight report found.")
        st.code(
            "python3 scripts/run_pipeline5_extraction.py "
            "--report-json outputs/burnaby_r1_slim_pipeline5_registry/pipeline5_extraction_preflight.json",
            language="bash",
        )
        return
    checks = preflight.get("checks", {})
    st.table([{"check": key, "status": "OK" if value else "MISSING"} for key, value in checks.items()])
    if preflight.get("can_use_saved_registry"):
        st.success("Saved Pipeline 5 registry found. The verifier can run from this saved extraction output.")
    else:
        st.error("Saved registry missing: " + ", ".join(preflight.get("saved_registry_blockers", [])))

    execution_blockers = preflight.get("execution_blockers") or preflight.get("blockers") or []
    if execution_blockers:
        st.warning("Full notebook execution still needs: " + ", ".join(execution_blockers))
    else:
        st.success("Pipeline 5 notebook execution is ready.")
    st.json({
        key: preflight.get(key)
        for key in ("pipeline5_dir", "notebook", "final_registry", "can_use_saved_registry", "can_execute")
    })


def _render_kpis(st: Any, data: dict[str, Any], filtered_items: list[dict[str, Any]]) -> None:
    validation = data["validation"]
    benchmark = data["benchmark"]
    metrics = benchmark.get("rule_metrics", {})
    proposal = benchmark.get("proposal_metrics", {})
    counts = validation.get("bucket_counts", {})
    audit_counts = _named_counts(data.get("audit", {}).get("summary", {}).get("action_counts", []))
    rerun = data.get("rerun", {})
    # These KPI cards put the two most actionable review-reduction paths in the
    # first screen: alternate evidence and safe verifier tuning.
    cards = [
        ("Verified", counts.get("verified", 0)),
        ("Review", counts.get("review_needed", 0)),
        ("Filtered Review", len(filtered_items)),
        ("Better Evidence", audit_counts.get("retry_with_better_evidence", 0)),
        ("Rerun Ready", rerun.get("promotion_ready_count", 0)),
        ("Verifier Tuning", audit_counts.get("safe_verifier_tuning_candidate", 0)),
        ("Precision", f"{metrics.get('verified_precision', 0):.2f}"),
        ("False Approvals", proposal.get("false_approval_count", 0)),
    ]
    cards_html = "".join(
        f"<div class='metric'><div class='metric-label'>{html.escape(label)}</div>"
        f"<div class='metric-value'>{html.escape(str(value))}</div></div>"
        for label, value in cards
    )
    st.markdown(f"<div class='metric-grid'>{cards_html}</div>", unsafe_allow_html=True)


def _render_header(st: Any) -> None:
    """Render a compact product-style header for the review console."""
    st.markdown(
        """
<div class="app-header">
  <div>
    <div class="eyebrow">Verification Review Console</div>
    <h1>Burnaby Verification Dashboard</h1>
    <p>Inspect review rules, compare candidate claims against verified rules, and identify the safest path to reduce review volume.</p>
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
  <div class="guide-card"><b>3. Pick the next action</b><span>Use Evidence Repair, Evidence Rerun, and Review Audit to decide whether the issue is evidence, verifier tuning, or legal review.</span></div>
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
3. If the meaning matches, check whether `Evidence Rerun` or `Review Audit` says it is safe to tune.
4. If the issue involves exceptions, conflicts, or legal scope, keep it in human review.
"""
        )


def _action_summary(st: Any, data: dict[str, Any]) -> None:
    """Surface the highest-value review-volume reduction paths."""
    audit_counts = _named_counts(data.get("audit", {}).get("summary", {}).get("action_counts", []))
    rerun = data.get("rerun", {})
    cards = [
        (
            "Retry with better evidence",
            audit_counts.get("retry_with_better_evidence", 0),
            "Repair evidence packets before changing verifier logic.",
        ),
        (
            "Safe verifier tuning",
            audit_counts.get("safe_verifier_tuning_candidate", 0),
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
    scope = _humanize(rule.get("constraint_scope"))
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
    _bylaw_lookup_panel(st, evidence, rule_like)


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


def _rerun_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one shadow rerun result in plain English."""
    decision = str(item.get("retry_decision") or "unknown")
    gaps = _list_text(item.get("retry_support_gaps", [])) or "none"
    risk_flags = _list_text(item.get("promotion_risk_flags", [])) or "none"
    promotion = "promotion-ready" if item.get("promotion_ready") else "not promotion-ready"
    return [
        f"Candidate claim: {_rule_sentence(item)}",
        f"The rerun replaced original evidence `{item.get('original_evidence_id')}` with retry evidence `{item.get('retry_evidence_id')}`.",
        f"The deterministic verifier returned `{decision}` with support gaps: {gaps}.",
        f"The shadow result is {promotion}. Promotion risk flags: {risk_flags}.",
        f"Recommendation: {item.get('promotion_recommendation') or 'inspect before promotion'}.",
    ]


def _audit_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one review audit item in plain English."""
    action = item.get("action_bucket") or "unclassified"
    likely = item.get("likely_status") or "unknown"
    score = _display_value(item.get("likely_correct_score"))
    gaps = _list_text(item.get("support_gaps", []))
    repair_evidence = item.get("best_repair_evidence_id") or "none"
    action_reason = _sentence_fragment(item.get("action_reason") or "no action reason recorded")
    next_step = _sentence_fragment(
        item.get("next_step")
        or "inspect the evidence and decide whether this needs evidence repair, verifier tuning, or legal review"
    )
    return [
        f"Candidate claim: {_rule_sentence(item)}",
        f"The audit bucket is `{action}` because: {action_reason}.",
        f"The likely status is `{likely}` with score {score}. Blocking gaps: {gaps}.",
        f"Suggested repair evidence: {repair_evidence}.",
        f"Next human action: {next_step}.",
    ]


def _bylaw_lookup_panel(st: Any, evidence: dict[str, Any], rule_like: dict[str, Any]) -> None:
    """Tell a reviewer how to find and verify the rule in the source bylaw."""
    page = evidence.get("page") or rule_like.get("page")
    quote = _quote_from_evidence(evidence)
    search_phrase = _search_phrase(rule_like, quote)

    st.markdown("#### How to find this in the bylaw")
    page_text = f"page `{page}`" if page not in (None, "") else "the cited section/page from the evidence packet"
    st.markdown(
        f"""
1. Open the [Burnaby R1 bylaw PDF]({SOURCE_DOCUMENT_URL}).
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
.block-container {padding-top: 1.5rem; max-width: 1500px;}
.app-header {border:1px solid #d9e0e8; border-radius:8px; padding:18px 20px; background:linear-gradient(180deg,#ffffff,#f7fafc); margin-bottom:14px;}
.app-header h1 {font-size:30px; line-height:1.15; margin:2px 0 6px; color:#172033; letter-spacing:0;}
.app-header p {margin:0; color:#526070; font-size:15px;}
.eyebrow {font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:#2563eb; font-weight:700;}
.metric-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(118px,1fr)); gap:10px; margin:12px 0 18px;}
.metric {border:1px solid #d7dde5; border-radius:8px; padding:13px 14px; background:#fff; box-shadow:0 1px 2px rgba(15,23,42,.04); min-height:86px;}
.metric-label {font-size:10px; line-height:1.25; color:#5d6875; text-transform:uppercase; font-weight:700; overflow-wrap:normal;}
.metric-value {font-size:25px; font-weight:750; color:#111827;}
.guidance-grid, .action-grid {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:12px 0 20px;}
.guide-card, .action-card {border:1px solid #d9e0e8; border-radius:8px; background:#fff; padding:14px 15px;}
.guide-card b {display:block; color:#172033; margin-bottom:5px;}
.guide-card span, .action-card p {color:#5d6875; font-size:14px; margin:0;}
.action-value {font-size:28px; font-weight:760; color:#0f766e;}
.action-title {font-weight:720; color:#172033; margin:1px 0 4px;}
.sentence-card {border:1px solid #d9e0e8; border-radius:8px; padding:15px 16px; min-height:142px; background:#fff; box-shadow:0 1px 2px rgba(15,23,42,.04);}
.sentence-card p {font-size:17px; line-height:1.45; color:#111827; margin:8px 0 10px;}
.sentence-card span {font-size:12px; color:#667085;}
.sentence-title {font-size:12px; text-transform:uppercase; letter-spacing:.06em; font-weight:760;}
.sentence-review {border-top:4px solid #d97706;}
.sentence-verified {border-top:4px solid #0f766e;}
.sentence-neutral {border-top:4px solid #64748b;}
.detail-sentence {display:grid; grid-template-columns:28px 1fr; gap:8px; border:1px solid #d9e0e8; border-radius:8px; background:#fff; padding:11px 13px; margin:7px 0;}
.detail-sentence b {color:#2563eb;}
.detail-sentence span {color:#172033; line-height:1.45;}
.bar-row {display:grid; grid-template-columns:minmax(160px,240px) 1fr 52px; gap:12px; align-items:center; margin:7px 0;}
.bar-row span {color:#344054; font-size:14px;}
.bar-row b {color:#172033; text-align:right;}
.bar-track {height:13px; background:#edf2f7; border-radius:999px; overflow:hidden; border:1px solid #e2e8f0;}
.bar-fill {height:100%; background:linear-gradient(90deg,#2563eb,#0f766e);}
div[data-testid="stDataFrame"] {border:1px solid #d9e0e8; border-radius:8px; overflow:hidden;}
div[data-testid="stExpander"] {border:1px solid #d9e0e8; border-radius:8px;}
@media (max-width: 900px) {
  .metric-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
  .guidance-grid, .action-grid {grid-template-columns:1fr;}
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


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
