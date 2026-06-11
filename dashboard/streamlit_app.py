"""Streamlit dashboard for Burnaby verifier outputs."""

from __future__ import annotations

import argparse
import html
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_ROOT = ROOT / "outputs"
OUTPUT_DIR_SUFFIX = "_slim_pipeline5_registry"
# Pipeline 9 (graph-RAG extraction) verifier outputs sit next to the P5
# registries as <city>_p9/. Same verifier, second upstream — the dashboard
# treats them as another selectable "city" so reviewers see the P9 lane.
P9_DIR_SUFFIX = "_p9"
DEFAULT_OUTPUT_DIR = OUTPUTS_ROOT / "burnaby_r1_slim_pipeline5_registry"
SOURCE_DOCUMENT_URL = "https://www.burnaby.ca/sites/default/files/acquiadam/2024-07/R1Small-Scale-Multi-Unit-Housing-District.pdf"

# Color semantics used across the whole dashboard. Presentation only.
STATUS_COLORS = {
    "verified": "#1a7f37",
    "review": "#9a6700",
    "rejected": "#cf222e",
    "not_used": "#57606a",
}

# Map centroids keyed by city prefix (first token of the output dir name).
# Used only to center the DEMO map view; they are not parcel data.
CITY_CENTROIDS = {
    "burnaby": (49.2488, -122.9805),
    "vancouver": (49.2827, -123.1207),
    "calgary": (51.0447, -114.0719),
}

# gis_felt_export geometry targets that behave like lot-line setbacks.
LOT_LINE_TARGETS = {
    "front_lot_line": "front",
    "rear_lot_line": "rear",
    "side_lot_line": "side",
    "lane": "lane",
}

# Demo lot used by the map, the 3D envelope, and the SVG fallback.
# It is a representative rectangle, NOT a real parcel.
DEMO_LOT_WIDTH_M = 30.0
DEMO_LOT_DEPTH_M = 40.0

# Active source-document URL for the selected city (module-level so the
# many detail panels stay simple). Falls back to the Burnaby PDF.
_ACTIVE_SOURCE = {"url": SOURCE_DOCUMENT_URL, "label": "source bylaw PDF"}


def discover_city_output_dirs(outputs_root: Path = OUTPUTS_ROOT) -> list[Path]:
    """Return city output dirs that contain verified_rules.json, sorted by name.

    Any new city (e.g. calgary) appears automatically once its
    `<city>_..._slim_pipeline5_registry/verified_rules.json` exists on disk.
    """
    if not outputs_root.is_dir():
        return []
    return sorted(
        path
        for path in outputs_root.iterdir()
        if path.is_dir()
        and (path.name.endswith(OUTPUT_DIR_SUFFIX) or path.name.endswith(P9_DIR_SUFFIX))
        and (path / "verified_rules.json").exists()
    )


def city_key_from_dir(output_dir: Path) -> str:
    """Return the city prefix for an output dir, e.g. burnaby_r1_... -> burnaby."""
    return output_dir.name.split("_")[0].lower()


def city_stem_from_dir(output_dir: Path) -> str:
    """Return the full city stem, e.g. burnaby_r1_slim_pipeline5_registry ->
    burnaby_r1 and vancouver_rs_p9 -> vancouver_rs.

    The short ``city_key`` ('burnaby') is right for centroids and labels but
    WRONG for artifact paths — every on-disk artifact uses the full stem
    ('burnaby_r1'), which is why path lookups must come through here.
    """
    name = output_dir.name
    for suffix in (OUTPUT_DIR_SUFFIX, P9_DIR_SUFFIX):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def bylaw_index_path(output_dir: Path) -> Path | None:
    """Resolve the bylaw-RAG index for an output dir.

    A P5 registry carries its own index; a P9 run borrows the sibling P5
    registry's index for the SAME city stem (same bylaw corpus). Previously
    this path was built from the short city_key, which never matched a real
    directory — the legal-context expander silently rendered nothing.
    """
    own = output_dir / "bylaw_rag_index.json"
    if own.exists():
        return own
    sibling = OUTPUTS_ROOT / f"{city_stem_from_dir(output_dir)}{OUTPUT_DIR_SUFFIX}" / "bylaw_rag_index.json"
    if sibling.exists():
        return sibling
    return None


def city_label_from_dir(output_dir: Path) -> str:
    """Human-readable label for the sidebar selector, e.g. 'Burnaby R1'."""
    is_p9 = output_dir.name.endswith(P9_DIR_SUFFIX)
    stem = city_stem_from_dir(output_dir)
    parts = [part for part in stem.split("_") if part]
    if not parts:
        return output_dir.name
    label = parts[0].capitalize() + (" " + " ".join(part.upper() for part in parts[1:]) if parts[1:] else "")
    return f"{label} — Pipeline 9" if is_p9 else label


def load_output_data(output_dir: Path) -> dict[str, Any]:
    """Load all dashboard source files from one verifier output directory."""
    # The dashboard is intentionally read-only. It consumes generated JSON
    # reports and never calls Gemini, reruns verification, or mutates outputs.
    return {
        "output_dir": output_dir,
        "validation": _read_json(output_dir / "validation_report.json", {}),
        "benchmark": _read_json(output_dir / "benchmark_report.json", {}),
        "intelligence": _read_json(output_dir / "evidence_intelligence.json", {"items": [], "summary": {}}),
        "repair": _read_json(output_dir / "evidence_repair_suggestions.json", {"suggestions": []}),
        "rerun": _read_json(output_dir / "evidence_rerun_report.json", {"attempts": [], "verified_after_rerun": []}),
        "bundle_rerun": _read_json(output_dir / "evidence_bundle_rerun_report.json", {"attempts": [], "promotion_ready": []}),
        "safe_tuning": _read_json(output_dir / "safe_verifier_tuning_candidates.json", {"items": [], "candidate_count": 0}),
        "router": _read_json(output_dir / "review_router.json", {"items": [], "summary": {}}),
        "resolution": _read_json(output_dir / "review_resolution.json", {"items": [], "summary": {}}),
        "rule_graph": _read_json(output_dir / "rule_graph.json", {"nodes": [], "edges": [], "summary": {}}),
        "semantic": _read_json(output_dir / "semantic_review_report.json", {"items": [], "summary": {}}),
        "bundle_promotion": _read_json(output_dir / "bundle_promotion_report.json", {"promoted_rules": []}),
        "source_repair": _read_json(output_dir / "source_repair_report.json", {"items": [], "status_counts": {}}),
        "review_assistant_packets": _read_json(output_dir / "review_assistant_packets.json", {"items": []}),
        "evidence_units": _read_json(output_dir / "evidence_units.json", []),
        "verified": _read_json(output_dir / "verified_rules.json", []),
        "review": _read_json(output_dir / "review_needed.json", []),
        "felt_export": _read_json(output_dir / "felt_export_manifest.json", {}),
        "preflight": _read_json(output_dir / "pipeline5_extraction_preflight.json", {}),
        # v2 additions (additive; every existing key above is unchanged).
        "gis_export": _read_json(output_dir / "gis_felt_export.json", {}),
        "buildable_envelope": _read_json(output_dir / "buildable_envelope.json", {}),
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
    cli_output_dir = Path(args.output_dir).expanduser().resolve()

    try:
        import streamlit as st
    except ModuleNotFoundError as exc:
        raise SystemExit("Streamlit is not installed. Run `pip install -r requirements.txt`.") from exc

    st.set_page_config(
        page_title="BC Zoning Verification Dashboard",
        page_icon="BV",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _style(st)

    # City selector: scan outputs/ for any *_slim_pipeline5_registry dir with
    # verified_rules.json. New cities appear automatically; nothing is hardcoded.
    city_dirs = discover_city_output_dirs()
    if cli_output_dir.is_dir() and cli_output_dir not in city_dirs:
        city_dirs = [*city_dirs, cli_output_dir]
    if not city_dirs:
        st.error(f"No verifier output directories found under `{OUTPUTS_ROOT}`.")
        return
    default_index = next(
        (index for index, path in enumerate(city_dirs) if path == cli_output_dir),
        next((index for index, path in enumerate(city_dirs) if path.name.startswith("burnaby_r1")), 0),
    )
    st.sidebar.header("City")
    output_dir = st.sidebar.selectbox(
        "Verifier output",
        city_dirs,
        index=default_index,
        format_func=city_label_from_dir,
    )
    city_key = city_key_from_dir(output_dir)
    city_label = city_label_from_dir(output_dir)

    data = load_output_data(output_dir)
    source_url = str(data.get("gis_export", {}).get("source_url") or "").strip()
    _ACTIVE_SOURCE["url"] = source_url or SOURCE_DOCUMENT_URL
    _ACTIVE_SOURCE["label"] = f"{city_label} bylaw PDF"

    st.sidebar.header("Filters")
    st.sidebar.caption(str(output_dir))
    # Review annotations now live on review_needed.json; the old standalone
    # triage view duplicated the same queue.
    triage_items = data["review"]
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

    _render_header(st, city_label)
    _render_kpis(st, data, filtered_items)
    _render_guidance(st)

    # v2 layout: the previous flat 14-tab strip is grouped into six top-level
    # sections. Every original tab is preserved inside its section.
    sections = st.tabs(["Overview", "Rules", "Review", "Evidence & Proof", "GIS & Map", "System"])

    with sections[0]:
        _overview_tab(st, data)
        _pipeline_comparison_tab(st, output_dir)

    with sections[1]:
        rule_tabs = st.tabs(["Candidate vs Verified", "Rule Graph"])
        with rule_tabs[0]:
            _candidate_compare_tab(
                st,
                filtered_items,
                data["review"],
                data["verified"],
                output_dir,
                {str(unit.get("evidence_id")): unit for unit in data["evidence_units"]},
            )
        with rule_tabs[1]:
            _rule_graph_tab(st, data["rule_graph"])

    with sections[2]:
        review_tabs = st.tabs(["Review", "Review Assistant", "Review Resolution", "Semantic Review"])
        with review_tabs[0]:
            _review_router_tab(st, data["router"])
        with review_tabs[1]:
            _review_assistant_tab(
                st,
                data["review_assistant_packets"],
                data["review"],
                output_dir,
                {str(unit.get("evidence_id")): unit for unit in data["evidence_units"]},
            )
        with review_tabs[2]:
            _review_resolution_tab(st, data["resolution"])
        with review_tabs[3]:
            _semantic_review_tab(st, data["semantic"])

    with sections[3]:
        evidence_tabs = st.tabs(
            ["Evidence Intelligence", "Evidence Repair", "Evidence Rerun", "Bundle Rerun", "Bylaw"]
        )
        with evidence_tabs[0]:
            _evidence_intelligence_tab(st, data["intelligence"])
        with evidence_tabs[1]:
            _repair_tab(st, data["repair"])
        with evidence_tabs[2]:
            _rerun_tab(st, data["rerun"], data["evidence_units"])
        with evidence_tabs[3]:
            _bundle_rerun_tab(st, data["bundle_rerun"])
        with evidence_tabs[4]:
            _bylaw_tab(st, data)

    with sections[4]:
        gis_tabs = st.tabs(["Map", "3D Envelope", "Felt Export"])
        with gis_tabs[0]:
            _map_tab(st, data, city_key)
        with gis_tabs[1]:
            _envelope_3d_tab(st, data, output_dir)
        with gis_tabs[2]:
            _felt_export_tab(st, data["felt_export"], output_dir)

    with sections[5]:
        system_tabs = st.tabs(["Safe Tuning", "Verification Structure", "Extraction Preflight"])
        with system_tabs[0]:
            _safe_tuning_tab(st, data["safe_tuning"], data["evidence_units"])
        with system_tabs[1]:
            _structure_tab(st)
        with system_tabs[2]:
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
    _bar_rows(st, data["router"].get("summary", {}).get("category_counts", []), "name", "count")

    st.subheader("Review Action Buckets")
    _bar_rows(st, data["router"].get("summary", {}).get("action_counts", []), "name", "count")

    st.subheader("Potential Mistakes")
    flags = Counter(
        flag
        for rule in data["review"]
        for flag in rule.get("potential_mistake_flags", [])
    )
    _bar_table(st, dict(flags.most_common(12)))


def pipeline_comparison_rows(output_dir: Path) -> list[dict[str, Any]]:
    """Return P5/P9 comparison rows for the selected city stem."""
    stem = city_stem_from_dir(output_dir)
    candidates = [
        ("Pipeline 5", OUTPUTS_ROOT / f"{stem}{OUTPUT_DIR_SUFFIX}"),
        ("Pipeline 9", OUTPUTS_ROOT / f"{stem}{P9_DIR_SUFFIX}"),
    ]
    rows: list[dict[str, Any]] = []
    for label, path in candidates:
        summary = _read_json(path / "slim_summary.json", {})
        benchmark = _read_json(path / "benchmark_report.json", {})
        metrics = benchmark.get("rule_metrics", {})
        gates = benchmark.get("quality_gates", {})
        rows.append(
            {
                "pipeline": label,
                "path": path.name,
                "candidates": summary.get("candidate_rule_count"),
                "evidence": summary.get("evidence_unit_count"),
                "verified": summary.get("verified_rule_count"),
                "review": summary.get("review_rule_count"),
                "rejected": summary.get("rejected_rule_count"),
                "not_used": summary.get("not_used_rule_count"),
                "precision": metrics.get("verified_precision"),
                "false_verified": metrics.get("false_verified_count"),
                "verified_or_review_recall": metrics.get("verified_or_review_recall"),
                "gate_status": pipeline_gate_status(summary, benchmark),
            }
        )
    return rows


def pipeline_gate_status(summary: dict[str, Any], benchmark: dict[str, Any]) -> str:
    """Human label for benchmark state; keeps P9 failures honest."""
    if not summary:
        return "missing"
    quality = benchmark.get("quality_gates", {})
    if quality.get("passed") is True:
        return "pass"
    metrics = benchmark.get("rule_metrics", {})
    false_verified = int(metrics.get("false_verified_count") or 0)
    false_approval = int(metrics.get("false_approval_count") or 0)
    candidates = int(summary.get("candidate_rule_count") or 0)
    verified = int(summary.get("verified_rule_count") or 0)
    review = int(summary.get("review_rule_count") or 0)
    rejected = int(summary.get("rejected_rule_count") or 0)
    not_used = int(summary.get("not_used_rule_count") or 0)
    if false_verified or false_approval:
        return "unsafe / needs fix"
    if verified == 0 and review:
        return "fail-closed"
    if candidates and not_used >= max(1, verified + review + rejected):
        return "scope mismatch"
    return "needs review"


def _pipeline_comparison_tab(st: Any, output_dir: Path) -> None:
    st.subheader("Pipeline Comparison")
    st.caption("Same verifier, different upstream extractors. Failed gates are shown honestly; review/rejected rules are not GIS-safe.")
    rows = pipeline_comparison_rows(output_dir)
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)


def _packet_by_rule_id(packet_report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("rule_id") or ""): item for item in packet_report.get("items", [])}


def _review_assistant_tab(
    st: Any,
    packet_report: dict[str, Any],
    review_rules: list[dict[str, Any]],
    output_dir: Path,
    evidence_by_id: dict[str, dict[str, Any]],
) -> None:
    st.subheader("Interactive Review Assistant")
    st.caption(
        "Advisory only. This panel explains review items and prepares bounded context for an optional LLM; "
        "it cannot approve rules or write GIS outputs."
    )
    packet_by_rule = _packet_by_rule_id(packet_report)
    if not review_rules:
        st.info("No review-needed rules in this output.")
        return
    options = [str(rule.get("rule_id")) for rule in review_rules if rule.get("rule_id")]
    selected_id = st.selectbox("Review item", options, key=f"assistant_rule_{output_dir.name}")
    rule = _by_rule_id(review_rules, selected_id)
    packet = packet_by_rule.get(selected_id, {})
    if not packet:
        st.warning("No prebuilt review assistant packet found. Rerun the slim verifier to generate review_assistant_packets.json.")
        packet = _fallback_packet(rule)

    left, right = st.columns([1, 1])
    with left:
        st.markdown("#### Candidate")
        st.table([compact_rule_row(rule)])
        st.markdown("#### Why It Is Held")
        st.write(_list_text(rule.get("support_gaps", [])))
        st.info(packet.get("suggested_next_action") or "Inspect the source evidence before any verifier rerun.")
    with right:
        source = packet.get("source", {})
        st.markdown("#### Evidence Packet")
        st.caption(f"Page {source.get('page') or 'unknown'} · evidence `{source.get('evidence_id') or ''}` · repair `{source.get('repair_status') or 'unknown'}`")
        st.markdown("*Original extractor evidence*")
        st.code(source.get("original_evidence") or _source_text(rule), language="text")
        st.markdown("*Repaired source context*")
        repaired = source.get("repaired_context")
        if repaired:
            st.code(repaired, language="text")
        else:
            st.caption("No repaired context available.")

    _legal_context_expander(st, output_dir, rule, evidence_by_id)

    st.markdown("#### Ask The Review Assistant")
    question = st.text_input(
        "Question for this item",
        key=f"assistant_q_{output_dir.name}_{selected_id}",
        placeholder="e.g. why is the operator missing, or what evidence would repair this?",
    )
    prompt = _assistant_prompt(packet, question)
    with st.expander("Bounded LLM context"):
        st.code(prompt, language="text")
    if question:
        answer = _optional_llm_review_answer(prompt)
        if answer:
            st.markdown("#### LLM Draft")
            st.write(answer)
            st.caption("Draft only. Any proposed repair must be rerun through the deterministic verifier.")
        else:
            st.info("No LLM key/client available. Use the bounded context above with a reviewer or keep using retrieval-only review.")


def _fallback_packet(rule: dict[str, Any]) -> dict[str, Any]:
    source = rule.get("source", {}) if isinstance(rule.get("source"), dict) else {}
    return {
        "rule_id": rule.get("rule_id"),
        "candidate_rule": compact_rule_row(rule),
        "support_gaps": list(rule.get("support_gaps", [])),
        "suggested_next_action": "Inspect the source evidence and rerun deterministic verification only after evidence is repaired.",
        "source": {
            "page": source.get("page"),
            "evidence_id": source.get("evidence_id"),
            "original_evidence": source.get("evidence_text"),
            "repaired_context": source.get("source_context"),
            "repair_status": "fallback",
        },
    }


def _assistant_prompt(packet: dict[str, Any], question: str) -> str:
    context = packet.get("llm_context") or {
        "instruction": "Advisory only. Do not approve or verify.",
        "rule": packet.get("candidate_rule", {}),
        "support_gaps": packet.get("support_gaps", []),
        "original_evidence": (packet.get("source") or {}).get("original_evidence"),
        "repaired_context": (packet.get("source") or {}).get("repaired_context"),
        "suggested_next_action": packet.get("suggested_next_action"),
    }
    return (
        f"{context.get('instruction')}\n\n"
        f"Rule: {json.dumps(context.get('rule', {}), ensure_ascii=False)}\n"
        f"Support gaps: {', '.join(str(gap) for gap in context.get('support_gaps', [])) or 'none'}\n"
        f"Original evidence: {context.get('original_evidence') or ''}\n"
        f"Repaired context: {context.get('repaired_context') or ''}\n"
        f"Suggested next action: {context.get('suggested_next_action') or ''}\n\n"
        f"Reviewer question: {question or 'Explain why this item is still in review.'}\n\n"
        "Answer briefly. Cite only the evidence above. Do not say this rule is approved or verified."
    )


def _optional_llm_review_answer(prompt: str) -> str | None:
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    if not api_key:
        return None
    try:  # pragma: no cover - optional interactive network path
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-opus-4-8"),
            max_tokens=700,
            system="You are an advisory zoning review assistant. Never approve or verify rules.",
            messages=[{"role": "user", "content": prompt}],
        )
        return "\n".join(block.text for block in response.content if getattr(block, "type", "") == "text").strip()
    except Exception as error:
        return f"LLM unavailable: {type(error).__name__}: {error}"


def _evidence_intelligence_tab(st: Any, report: dict[str, Any]) -> None:
    items = report.get("items", [])
    st.subheader("Evidence Intelligence")
    st.caption("Rule-centric evidence ranking and bundle suggestions. This page does not verify rules.")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Review Rules", report.get("review_rule_count", len(items)))
    metric_cols[1].metric("Evidence Indexed", report.get("evidence_index_count", 0))
    metric_cols[2].metric("Safe Bundle Retry", report.get("safe_retry_count", 0))
    metric_cols[3].metric("Blocked", report.get("blocked_count", 0))

    summary = report.get("summary", {})
    left, right = st.columns(2)
    with left:
        st.markdown("### Next Actions")
        _bar_rows(st, summary.get("next_action_counts", []), "name", "count")
    with right:
        st.markdown("### Missing Fields")
        _bar_rows(st, summary.get("missing_field_counts", []), "name", "count")

    if not items:
        st.info("No evidence intelligence output found. Rerun the slim verifier.")
        return
    only_safe = st.checkbox("Show safe bundle retry only")
    visible = [item for item in items if item.get("safe_retry")] if only_safe else items
    rows = [
        {
            "rule_id": item.get("rule_id"),
            "safe_retry": item.get("safe_retry"),
            "score": item.get("bundle_score"),
            "next_action": item.get("next_action"),
            "rule_object": item.get("rule_object"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "missing_fields": ", ".join(item.get("bundle_missing_fields", [])),
            "blocked_by": ", ".join(item.get("blocked_by", [])),
        }
        for item in visible[:250]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if visible:
        selected = st.selectbox("Evidence intelligence detail", [item["rule_id"] for item in visible])
        item = next(candidate for candidate in visible if candidate["rule_id"] == selected)
        _detail_sentence_panel(
            st,
            "Evidence intelligence in plain English",
            _intelligence_detail_sentences(item),
            _bundle_display_evidence(item),
            item,
        )
        st.markdown("#### Best Evidence Bundle")
        st.dataframe(_display_rows(_bundle_rows(item)), width="stretch", hide_index=True)
        with st.expander("Raw evidence intelligence JSON"):
            st.json(item)


def _review_router_tab(st: Any, report: dict[str, Any]) -> None:
    items = report.get("items", [])
    st.subheader("Review Decision Tree")
    st.caption("One explicit route per review item. It tells the human what to check next; it does not change verifier decisions.")
    summary = report.get("summary", {})
    left, middle, right = st.columns(3)
    with left:
        st.markdown("### Action Buckets")
        _bar_rows(st, summary.get("action_counts", []), "name", "count")
    with middle:
        st.markdown("### Review Categories")
        _bar_rows(st, summary.get("category_counts", []), "name", "count")
    with right:
        st.markdown("### Semantic Classes")
        _bar_rows(st, summary.get("semantic_review_counts", []), "name", "count")

    if not items:
        st.info("No review router output found. Rerun the slim verifier.")
        return
    actions = st.multiselect("Action bucket", _unique(items, "action_bucket"))
    categories = st.multiselect("Decision category", _unique(items, "review_category"))
    semantic_classes = st.multiselect("Semantic class", _unique(items, "semantic_review_class"))
    visible = items
    if actions:
        visible = [item for item in visible if item.get("action_bucket") in actions]
    if categories:
        visible = [item for item in visible if item.get("review_category") in categories]
    if semantic_classes:
        visible = [item for item in visible if item.get("semantic_review_class") in semantic_classes]
    rows = [
        {
            "rule_id": item.get("rule_id"),
            "category": item.get("review_category"),
            "action": item.get("action_bucket"),
            "priority": item.get("priority"),
            "rule_object": item.get("rule_object"),
            "semantic_class": item.get("semantic_review_class"),
            "semantic_score": item.get("semantic_score"),
            "semantic_match": item.get("semantic_verified_rule_id"),
            "semantic_blockers": ", ".join(item.get("semantic_guardrail_blockers", [])),
            "bundle_safe": item.get("bundle_safe_retry"),
            "bundle_ready": item.get("bundle_rerun_promotion_ready"),
            "decision_path": " > ".join(item.get("decision_path", [])),
            "next_step": item.get("next_step"),
        }
        for item in visible[:250]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if visible:
        selected = st.selectbox("Decision tree detail", [item["rule_id"] for item in visible])
        item = next(candidate for candidate in visible if candidate["rule_id"] == selected)
        _detail_sentence_panel(
            st,
            "Review route in plain English",
            _router_detail_sentences(item),
            {"evidence_quote": item.get("evidence_sentence")},
            item,
        )
        with st.expander("Raw route JSON"):
            st.json(item)


def _review_resolution_tab(st: Any, report: dict[str, Any]) -> None:
    """Show final reviewer-facing resolution labels for remaining review items."""
    items = report.get("items", [])
    st.subheader("Review Resolution")
    st.caption(
        "Final operating labels for the remaining review queue. This page tells a reviewer what kind of work is left; it does not promote rules."
    )
    summary = report.get("summary", {})
    metric_cols = st.columns(4)
    metric_cols[0].metric("Review Rules", report.get("review_rule_count", len(items)))
    metric_cols[1].metric("Evidence-Fix Candidates", summary.get("can_promote_after_evidence_fix_count", 0))
    metric_cols[2].metric("Semantic Duplicates", summary.get("duplicate_or_degraded_count", 0))
    metric_cols[3].metric("Promotable Now", summary.get("promotable_now_count", 0))

    left, right = st.columns(2)
    with left:
        st.markdown("### Resolution Buckets")
        _bar_rows(st, summary.get("resolution_counts", []), "name", "count")
    with right:
        st.markdown("### Next Step Types")
        _bar_rows(st, summary.get("next_step_type_counts", []), "name", "count")

    recommendations = summary.get("recommendations", [])
    if recommendations:
        st.markdown("### Recommended Workflow")
        for item in recommendations:
            st.markdown(f"- {item}")

    if not items:
        st.info("No review resolution output found. Rerun the slim verifier.")
        return
    buckets = st.multiselect("Resolution", _unique(items, "resolution"))
    next_steps = st.multiselect("Next step type", _unique(items, "next_step_type"))
    visible = items
    if buckets:
        visible = [item for item in visible if item.get("resolution") in buckets]
    if next_steps:
        visible = [item for item in visible if item.get("next_step_type") in next_steps]

    rows = [
        {
            "rule_id": item.get("rule_id"),
            "resolution": item.get("resolution"),
            "next_step": item.get("next_step_type"),
            "can_promote_after_fix": item.get("can_promote_after_evidence_fix"),
            "rule_object": item.get("rule_object"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "semantic_match": item.get("semantic_verified_rule_id"),
            "semantic_score": item.get("semantic_score"),
            "gaps": ", ".join(item.get("support_gaps", [])[:4]),
            "page": item.get("source_page"),
            "evidence_id": item.get("source_evidence_id"),
            "where": item.get("where_to_find_it"),
        }
        for item in visible[:250]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if visible:
        selected = st.selectbox("Resolution detail", [item["rule_id"] for item in visible])
        item = next(candidate for candidate in visible if candidate["rule_id"] == selected)
        _detail_sentence_panel(
            st,
            "Resolution in plain English",
            _resolution_detail_sentences(item),
            {"evidence_quote": item.get("evidence_sentence"), "page": item.get("source_page")},
            item,
        )
        with st.expander("Raw resolution JSON"):
            st.json(item)


def _bundle_rerun_tab(st: Any, report: dict[str, Any]) -> None:
    attempts = report.get("attempts", [])
    st.subheader("Evidence Bundle Rerun")
    st.caption("Shadow-mode rerun using the best evidence bundle. Bundle score cannot verify a rule by itself.")
    metric_cols = st.columns(6)
    metric_cols[0].metric("Attempts", report.get("attempt_count", len(attempts)))
    metric_cols[1].metric("Verified After Rerun", report.get("verified_after_rerun_count", 0))
    metric_cols[2].metric("Promotion Ready", report.get("promotion_ready_count", 0))
    metric_cols[3].metric("Still Review", report.get("review_after_rerun_count", 0))
    metric_cols[4].metric("Rejected", report.get("rejected_after_rerun_count", 0))
    metric_cols[5].metric("Skipped", report.get("skipped_count", 0))
    if not attempts:
        st.info("No bundle rerun attempts found.")
        return
    only_ready = st.checkbox("Promotion-ready bundle reruns only")
    visible = [item for item in attempts if item.get("promotion_ready")] if only_ready else attempts
    rows = [
        {
            "rule_id": item.get("original_rule_id"),
            "decision": item.get("retry_decision"),
            "ready": item.get("promotion_ready"),
            "score": item.get("bundle_score"),
            "rule_object": item.get("rule_object"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "bundle_ids": ", ".join(str(value) for value in item.get("bundle_evidence_ids", [])),
            "missing": ", ".join(item.get("bundle_missing_fields", [])),
            "risk_flags": ", ".join(item.get("promotion_risk_flags", [])),
            "gaps": ", ".join(item.get("retry_support_gaps", [])[:4]),
        }
        for item in visible[:250]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if visible:
        selected = st.selectbox("Bundle rerun detail", [item["original_rule_id"] for item in visible])
        item = next(candidate for candidate in visible if candidate["original_rule_id"] == selected)
        _detail_sentence_panel(
            st,
            "Bundle rerun in plain English",
            _bundle_rerun_detail_sentences(item),
            {"page": "", "evidence_quote": item.get("bundle_evidence_quote")},
            item,
        )
        with st.expander("Raw bundle rerun JSON"):
            st.json(item)


def _semantic_review_tab(st: Any, report: dict[str, Any]) -> None:
    items = report.get("items", [])
    st.subheader("Semantic Review")
    st.caption("Structured meaning comparison plus optional MiniLM embedding similarity. Advisory only; it cannot clear support gaps.")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Review Rules", report.get("review_rule_count", len(items)))
    metric_cols[1].metric("Verified Rules Compared", report.get("verified_rule_count", 0))
    metric_cols[2].metric("High Similarity", report.get("high_similarity_count", 0))
    embedding = report.get("embedding", {})
    metric_cols[3].metric("Embedding Mode", embedding.get("mode", "unknown"))
    if embedding:
        st.caption(
            f"Embedding backend: {embedding.get('model') or 'none'} "
            f"({ 'available' if embedding.get('available') else embedding.get('reason', 'unavailable') })."
        )
    actions = report.get("summary", {}).get("semantic_action_counts", [])
    if actions:
        st.markdown("### Semantic Next Actions")
        _bar_rows(st, actions, "name", "count")
    if not items:
        st.info("No semantic review report found. Rerun the slim verifier.")
        return
    threshold = st.slider("Minimum semantic score", 0.0, 1.0, 0.70, 0.05)
    visible = [item for item in items if float(item.get("best_semantic_score") or 0.0) >= threshold]
    rows = []
    for item in visible[:250]:
        top = item.get("best_verified_matches", [{}])[0] if item.get("best_verified_matches") else {}
        rows.append(
            {
                "rule_id": item.get("rule_id"),
                "combined_score": item.get("best_combined_semantic_score", item.get("best_semantic_score")),
                "structured_score": item.get("best_structured_score"),
                "embedding_score": item.get("best_embedding_score"),
                "match_type": item.get("semantic_match_type"),
                "action": item.get("semantic_next_action"),
                "matched_verified": top.get("verified_rule_id"),
                "guardrail_blockers": ", ".join(item.get("semantic_guardrail_blockers", [])),
                "reasons": ", ".join(top.get("match_reasons", [])),
                "support_gaps": ", ".join(item.get("support_gaps", [])[:4]),
            }
        )
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    if visible:
        selected = st.selectbox("Semantic detail", [item["rule_id"] for item in visible])
        item = next(candidate for candidate in visible if candidate["rule_id"] == selected)
        top = item.get("best_verified_matches", [{}])[0] if item.get("best_verified_matches") else {}
        _detail_sentence_panel(
            st,
            "Semantic review in plain English",
            [
                f"Review rule `{item.get('rule_id')}` has combined semantic score {_display_value(item.get('best_combined_semantic_score', item.get('best_semantic_score')))} against verified rule `{top.get('verified_rule_id')}`.",
                f"Structured score: {_display_value(top.get('structured_score'))}; embedding score: {_display_value(top.get('embedding_score'))}.",
                f"The match reasons are: {_list_text(top.get('match_reasons', []))}.",
                f"Guardrails passed: {_list_text(top.get('semantic_guardrails', []))}. Blockers: {_list_text(top.get('semantic_guardrail_blockers', []))}.",
                f"The verifier still blocks this candidate because of: {_list_text(item.get('support_gaps', []))}.",
                f"Suggested semantic action: `{item.get('semantic_next_action')}`.",
                "This comparison prioritizes review only. It cannot verify a rule.",
            ],
            {"evidence_quote": json.dumps(item.get("signature", {}), indent=2)},
            item,
        )
        with st.expander("Raw semantic JSON"):
            st.json(item)


def _rule_graph_tab(st: Any, graph: dict[str, Any]) -> None:
    st.subheader("Rule Graph")
    st.caption("Diagnostic graph showing candidates, evidence, canonical keys, verified rules, and review rules. It does not change verification.")
    metric_cols = st.columns(2)
    metric_cols[0].metric("Nodes", graph.get("node_count", len(graph.get("nodes", []))))
    metric_cols[1].metric("Edges", graph.get("edge_count", len(graph.get("edges", []))))
    summary = graph.get("summary", {})
    left, right = st.columns(2)
    with left:
        st.markdown("### Node Types")
        _bar_rows(st, summary.get("node_type_counts", []), "name", "count")
    with right:
        st.markdown("### Edge Types")
        _bar_rows(st, summary.get("edge_type_counts", []), "name", "count")
    edges = graph.get("edges", [])
    if edges:
        edge_types = st.multiselect("Edge type", _unique(edges, "type"))
        visible = [edge for edge in edges if not edge_types or edge.get("type") in edge_types]
        st.dataframe(_display_rows(visible[:500]), width="stretch", hide_index=True)
    else:
        st.info("No graph output found. Rerun the slim verifier.")


def p9_provenance_summary(rule: dict[str, Any], evidence_by_id: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    """Collect the Pipeline 9 lane for one review rule, or None for P5 rules.

    Pure data (no streamlit) so tests can pin it: provenance identifies where
    the RAG candidate came from (pack, lane, pseudo->original page, upstream
    filter action), and the evidence comparison shows the RAG block text next
    to the re-anchored authentic source window — or flags the mismatch that
    forced the rule to review.
    """
    candidate = rule.get("candidate") or {}
    provenance = candidate.get("p9_provenance") or rule.get("p9_provenance") or {}
    if not provenance:
        return None
    evidence = evidence_by_id.get(str(candidate.get("evidence_id") or rule.get("source_evidence_id") or "")) or {}
    return {
        "pack": provenance.get("rag_pack_id"),
        "lane": provenance.get("rag_lane"),
        "applicability": provenance.get("rag_applicability"),
        "pseudo_page": provenance.get("pseudo_page"),
        "original_page": provenance.get("original_page_number"),
        "filter_action": provenance.get("target_filter_action"),
        "block_id": provenance.get("block_id") or provenance.get("source_id"),
        "rag_text": str(evidence.get("evidence_text") or ""),
        "reanchored": bool(evidence.get("reanchored_to_source")),
        "mismatched": bool(evidence.get("rag_context_mismatch")),
        "source_window": str(evidence.get("source_context") or "") if evidence.get("reanchored_to_source") else "",
    }


def _legal_context_expander(
    st: Any,
    output_dir: Path,
    rule: dict[str, Any],
    evidence_by_id: dict[str, dict[str, Any]] | None = None,
) -> None:
    """Retrieved FULL bylaw sections for a review rule (advisory context).

    The reviewer's recurring question is 'is there a qualifier NEARBY that the
    extractor missed?' — this answers it in place: the rule's own sentence is
    the retrieval query against the city's bylaw-RAG index, and hits come back
    section-expanded (the whole numbered provision, not a fragment).
    """
    lane = p9_provenance_summary(rule, evidence_by_id or {})
    index_path = bylaw_index_path(output_dir)
    if index_path is None and lane is None:
        return
    with st.expander("Legal context (retrieved bylaw sections — advisory)"):
        if lane:
            st.markdown("**Pipeline 9 provenance**")
            st.caption(
                f"pack `{lane['pack']}` | lane {lane['lane']} ({lane['applicability']}) | "
                f"pseudo page {lane['pseudo_page']} → bylaw page {lane['original_page']} | "
                f"upstream filter: {lane['filter_action']} | block `{lane['block_id']}`"
            )
            if lane["mismatched"]:
                st.warning(
                    "RAG context mismatch: this block's text was NOT found on its claimed "
                    "source page — the candidate is forced to review."
                )
            if lane["reanchored"] and lane["source_window"]:
                rag_col, source_col = st.columns(2)
                with rag_col:
                    st.markdown("*RAG block text (Pipeline 9)*")
                    st.markdown(
                        f"<div class='bylaw-section'>{html.escape(_short_display_quote(lane['rag_text']))}</div>",
                        unsafe_allow_html=True,
                    )
                with source_col:
                    st.markdown("*Re-anchored source window (authentic page)*")
                    st.markdown(
                        f"<div class='bylaw-section'>{html.escape(_short_display_quote(lane['source_window']))}</div>",
                        unsafe_allow_html=True,
                    )
            st.caption("Provenance is display-only — upstream labels never promote a candidate.")
        if index_path is None:
            return
        try:
            from burnaby_prototype.bylaw_rag import load_index

            query = " ".join(
                str(rule.get(field) or "")
                for field in ("rule_object", "applies_to", "constraint_scope", "condition", "value", "unit")
            )
            hits = load_index(index_path).ask(query, top_k=3)
        except Exception as error:  # pragma: no cover - optional dep path
            st.caption(f"Retrieval unavailable: {error}")
            return
        if not hits:
            st.caption("No related sections retrieved.")
            return
        for hit in hits:
            label = hit.get("section") or hit.get("chunk_id")
            st.markdown(
                f"<div class='bylaw-section'><b>[{html.escape(str(label))}]</b><br>"
                f"{html.escape(_short_display_quote(hit.get('section_text') or hit.get('text') or ''))}</div>",
                unsafe_allow_html=True,
            )
        st.caption("Retrieved context only — it cannot change the rule's decision.")


def _candidate_compare_tab(
    st: Any,
    triage_items: list[dict[str, Any]],
    review_rules: list[dict[str, Any]],
    verified_rules: list[dict[str, Any]],
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    evidence_by_id: dict[str, dict[str, Any]] | None = None,
) -> None:
    st.subheader("Candidate vs Verified")
    st.caption("Use this view to compare the candidate claim against the closest already-verified rule before deciding whether to tune the verifier or repair evidence.")
    if not triage_items:
        st.info("No review items match the current filters.")
        return
    options = [item["rule_id"] for item in triage_items]
    selected_id = st.selectbox("Review rule", options)
    review_rule = _by_rule_id(review_rules, selected_id)
    _legal_context_expander(st, output_dir, review_rule, evidence_by_id)
    triage_item = next((item for item in triage_items if item["rule_id"] == selected_id), {})
    semantic_match_id = triage_item.get("semantic_verified_rule_id") or review_rule.get("semantic_verified_rule_id")
    lexical_match_id = triage_item.get("similar_verified_rule_id") or review_rule.get("similar_verified_rule_id")
    verified_rule = _by_rule_id(verified_rules, semantic_match_id or lexical_match_id)

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
                f"Semantic score: {triage_item.get('semantic_score') or review_rule.get('semantic_score') or 'n/a'}; lexical score: {triage_item.get('similar_verified_score')}",
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
            st.markdown(f"Semantic score: `{triage_item.get('semantic_score') or review_rule.get('semantic_score') or 'n/a'}`")
            st.markdown(f"Lexical score: `{triage_item.get('similar_verified_score')}`")
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


def _safe_tuning_tab(st: Any, report: dict[str, Any], evidence_units: list[dict[str, Any]]) -> None:
    items = report.get("items", [])
    st.subheader(f"Safe Verifier Tuning ({len(items)})")
    st.caption("Engineering backlog for general verifier improvements. These candidates are not automatically promoted.")
    metric_cols = st.columns(3)
    metric_cols[0].metric("Candidates", report.get("candidate_count", len(items)))
    metric_cols[1].metric("Promotion-Ready Reruns", sum(1 for item in items if item.get("rerun_promotion_ready")))
    metric_cols[2].metric("Tuning Types", len(report.get("tuning_type_counts", [])))

    type_rows = report.get("tuning_type_counts", [])
    if type_rows:
        st.markdown("### Tuning Type Mix")
        _bar_rows(st, type_rows, "name", "count")
    if not items:
        st.info("No safe verifier tuning candidates found.")
        return

    tuning_types = st.multiselect("Tuning type", _unique(items, "tuning_type"))
    visible = [item for item in items if not tuning_types or item.get("tuning_type") in tuning_types]
    rows = [
        {
            "rule_id": item.get("rule_id"),
            "tuning_type": item.get("tuning_type"),
            "rule_object": item.get("rule_object"),
            "value": item.get("value"),
            "unit": item.get("unit"),
            "likely": item.get("likely_status"),
            "score": item.get("likely_correct_score"),
            "rerun_ready": item.get("rerun_promotion_ready"),
            "gaps": ", ".join(item.get("support_gaps", [])[:4]),
        }
        for item in visible[:250]
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    selected = st.selectbox("Tuning detail", [item["rule_id"] for item in visible])
    item = next(candidate for candidate in visible if candidate["rule_id"] == selected)
    evidence = _evidence_by_id(evidence_units, item.get("evidence_id") or item.get("rerun_evidence_id"))
    _detail_sentence_panel(
        st,
        "Safe tuning candidate in plain English",
        _safe_tuning_detail_sentences(item),
        evidence,
        item,
    )
    with st.expander("Required tests"):
        for test in item.get("required_tests", []):
            st.write(f"- {test}")
    with st.expander("Guardrails"):
        for guardrail in item.get("guardrails", []):
            st.write(f"- {guardrail}")
    with st.expander("Raw safe-tuning JSON"):
        st.json(item)


def _felt_export_tab(st: Any, manifest: dict[str, Any], output_dir: Path) -> None:
    st.subheader("Felt Export")
    st.caption("These files are generated from verifier outputs for the Felt map. Only the verified-rule CSV is authoritative.")
    if not manifest:
        st.info("No Felt export manifest found. Rerun the slim verifier to generate Felt CSV outputs.")
        return

    rows = [
        {
            "file": manifest.get("verified_rules_csv"),
            "use": "Authoritative verified rule table for Felt popups / GIS handoff",
            "rows": manifest.get("verified_rule_count"),
            "safe_for_geometry": "yes",
        },
        {
            "file": manifest.get("review_rules_csv"),
            "use": "Review queue visualization only",
            "rows": manifest.get("review_rule_count"),
            "safe_for_geometry": "no",
        },
        {
            "file": manifest.get("evidence_rerun_csv"),
            "use": "Shadow rerun inspection only",
            "rows": manifest.get("rerun_attempt_count"),
            "safe_for_geometry": "no",
        },
    ]
    st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    st.markdown("### Upload Guidance")
    st.markdown(
        """
1. Upload `felt_verified_rules.csv` as the `Burnaby R1 Rules` table layer.
2. Use `rule_id`, `rule_sentence`, `source_page`, and `evidence_quote` in popups.
3. Keep `felt_review_rules.csv` and `felt_evidence_rerun.csv` visually separate from geometry-driving layers.
4. Build setbacks/buildable areas from `gis_rule_contract.json`, not from review or rerun rows.
"""
    )
    with st.expander("Manifest JSON"):
        st.json({**manifest, "output_dir": str(output_dir)})


def _structure_tab(st: Any) -> None:
    st.subheader("Verification Layer Structure")
    st.code(
        """Pipeline 5 final_rule_registry.json
  -> zihao_adapter.py
  -> slim_pipeline.py
  -> verification.py
       normalization.py
       support_checks.py
       proof_trace.py
       text_span_proof.py
       table_natural_logic.py
       decision_policy.py
  -> verified / review / rejected / not_used
  -> evidence_intelligence.py
  -> rule_graph.py
  -> evidence_bundle_rerun
  -> guarded bundle promotion
  -> semantic_review.py
  -> evidence_repair.py
  -> evidence_rerun.py
  -> safe_tuning.py
  -> review_router.py
  -> dashboard""",
        language="text",
    )
    rows = [
        {"layer": "Adapter", "file": "zihao_adapter.py", "purpose": "Normalize Pipeline 5 registry into candidates and evidence packets."},
        {"layer": "Verifier", "file": "verification.py", "purpose": "Main support-gap loop and final rule objects."},
        {"layer": "Normalization", "file": "normalization.py", "purpose": "Candidate cleanup before support checks; no rule promotion."},
        {"layer": "Support checks", "file": "support_checks.py", "purpose": "Reusable deterministic checks for value, unit, operator, scope, applies_to, and rule family."},
        {"layer": "Proof trace", "file": "proof_trace.py", "purpose": "Human-readable proof traces, review reasons, and proof/decision diagnostics."},
        {"layer": "Text span proof", "file": "text_span_proof.py", "purpose": "Prose evidence proof for value, unit, operator, scope, condition."},
        {"layer": "Table proof", "file": "table_natural_logic.py", "purpose": "Table title/row/column/cell proof."},
        {"layer": "Decision policy", "file": "decision_policy.py", "purpose": "Map support gaps to verified/review/rejected/not_used."},
        {"layer": "Evidence intelligence", "file": "evidence_intelligence.py", "purpose": "Build a rule-centric evidence index, score evidence bundles, and recommend safe shadow reruns."},
        {"layer": "Evidence repair", "file": "evidence_repair.py", "purpose": "Find stronger existing evidence for review rules."},
        {"layer": "Evidence rerun", "file": "evidence_rerun.py", "purpose": "Rerun repairable candidates or bundles against stronger evidence in shadow mode."},
        {"layer": "Bundle promotion", "file": "evidence_rerun.py", "purpose": "Move only deterministic, no-gap, no-risk bundle reruns into verified output."},
        {"layer": "Rule graph", "file": "rule_graph.py", "purpose": "Diagnostic graph linking candidates, evidence packets, canonical keys, verified rules, and review rules."},
        {"layer": "Verification cache", "file": "verification_cache.py", "purpose": "Stable cache keys and hit/miss diagnostics for future incremental multi-bylaw runs."},
        {"layer": "Semantic review", "file": "semantic_review.py", "purpose": "Structured meaning comparison between review and verified rules; advisory only."},
        {"layer": "Safe tuning", "file": "safe_tuning.py", "purpose": "List verifier-tuning candidates with experiments, tests, and guardrails."},
        {"layer": "Review router", "file": "review_router.py", "purpose": "Single review module: triage (rank + likely mistakes), action audit (next-action buckets), and the consolidated reviewer route. Advisory only."},
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
    # The preflight script (scripts/run_pipeline5_extraction.py) only emits
    # checks/blockers/can_execute, so the saved-registry status is derived from
    # its saved_final_registry_exists check rather than from keys it never writes.
    if checks.get("saved_final_registry_exists"):
        st.success("Saved Pipeline 5 registry found. The verifier can run from this saved extraction output.")
    else:
        failed_checks = [name for name, passed in checks.items() if not passed]
        st.error("Saved registry missing: " + (", ".join(failed_checks) or "saved_final_registry_exists"))

    execution_blockers = preflight.get("blockers") or []
    if execution_blockers:
        st.warning("Full notebook execution still needs: " + ", ".join(execution_blockers))
    else:
        st.success("Pipeline 5 notebook execution is ready.")
    st.json({
        key: preflight.get(key)
        for key in ("pipeline5_dir", "notebook", "final_registry", "can_execute")
    })


# ---------------------------------------------------------------------------
# v2: demo-lot geometry helpers (shared by the Map tab, the SVG fallback, and
# scripts/build_envelope_3d.py). All values come straight from verified-only
# exports; the lot itself is a representative demo rectangle, NOT a parcel.
# ---------------------------------------------------------------------------


def lot_line_constraints(gis_export: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Group gis_felt_export constraints by demo-lot side (front/rear/side/lane)."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for constraint in gis_export.get("constraints", []):
        side = LOT_LINE_TARGETS.get(str(constraint.get("geometry_target")))
        if side is not None and constraint.get("value_numeric") is not None:
            grouped.setdefault(side, []).append(constraint)
    return grouped


def governing_lot_line_setbacks(gis_export: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Most restrictive setback per side (max value, since setbacks are `>=`)."""
    return {
        side: max(entries, key=lambda entry: float(entry["value_numeric"]))
        for side, entries in lot_line_constraints(gis_export).items()
    }


def export_max_height(gis_export: dict[str, Any]) -> dict[str, Any] | None:
    """Tallest verified height constraint (m) from gis_felt_export constraints."""
    candidates = [
        constraint
        for constraint in gis_export.get("constraints", [])
        if "height" in str(constraint.get("parameter_key", ""))
        and str(constraint.get("unit", "")).strip() == "m"
        and constraint.get("value_numeric") is not None
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda entry: float(entry["value_numeric"]))


def envelope_governing_setbacks(envelope: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Most restrictive setback per lot line from buildable_envelope.json."""
    governing: dict[str, dict[str, Any]] = {}
    for lot_line, entries in (envelope.get("lot_line_setbacks_m") or {}).items():
        valid = [entry for entry in entries if entry.get("value_numeric") is not None]
        if valid:
            governing[lot_line] = max(valid, key=lambda entry: float(entry["value_numeric"]))
    return governing


def envelope_max_height(envelope: dict[str, Any]) -> dict[str, Any] | None:
    """Tallest verified height limit across roles, with its role attached."""
    best: dict[str, Any] | None = None
    for role, entries in (envelope.get("max_height_m_by_role") or {}).items():
        for entry in entries:
            if entry.get("value_numeric") is None:
                continue
            if best is None or float(entry["value_numeric"]) > float(best["value_numeric"]):
                best = {**entry, "role": role}
    return best


def envelope_max_storeys(envelope: dict[str, Any]) -> dict[str, Any] | None:
    """Highest verified storey limit across roles, with its role attached."""
    best: dict[str, Any] | None = None
    for role, entries in (envelope.get("max_storeys_by_role") or {}).items():
        for entry in entries:
            if entry.get("value_numeric") is None:
                continue
            if best is None or float(entry["value_numeric"]) > float(best["value_numeric"]):
                best = {**entry, "role": role}
    return best


def demo_footprint_insets(setbacks: dict[str, dict[str, Any]]) -> dict[str, float]:
    """Map governing buildable_envelope setbacks onto the 4-sided demo lot.

    The demo lot has no lane, so lane setbacks are reported in tables but do
    not inset the footprint.
    """
    return {
        "front": float(setbacks.get("front_lot_line", {}).get("value_numeric") or 0.0),
        "rear": float(setbacks.get("rear_lot_line", {}).get("value_numeric") or 0.0),
        "side": float(setbacks.get("side_lot_line", {}).get("value_numeric") or 0.0),
    }


def build_envelope_svg(envelope: dict[str, Any]) -> str:
    """Plan-view SVG fallback for the 3D envelope viewer.

    Always renders without any optional dependency: demo lot rectangle, the
    setback-inset buildable footprint, and annotated setback arrows carrying
    values and governing rule ids. Returns well-formed standalone SVG.
    """
    setbacks = envelope_governing_setbacks(envelope or {})
    insets = demo_footprint_insets(setbacks)
    height = envelope_max_height(envelope or {})
    storeys = envelope_max_storeys(envelope or {})

    scale = 8.0  # px per metre
    margin_x, margin_y = 200.0, 60.0
    lot_w, lot_d = DEMO_LOT_WIDTH_M * scale, DEMO_LOT_DEPTH_M * scale
    width, height_px = lot_w + 2 * margin_x, lot_d + 2 * margin_y + 40
    lot_x, lot_y = margin_x, margin_y  # rear (top) at lot_y, front (bottom) at lot_y + lot_d

    fp_x = lot_x + insets["side"] * scale
    fp_y = lot_y + insets["rear"] * scale
    fp_w = max(lot_w - 2 * insets["side"] * scale, 0.0)
    fp_h = max(lot_d - (insets["front"] + insets["rear"]) * scale, 0.0)

    def _label(entry: dict[str, Any], name: str) -> str:
        value = entry.get("value_numeric")
        return f"{name} {value} {entry.get('unit') or 'm'} ({entry.get('rule_id')})" if value is not None else name

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height_px:g}" '
        f'width="{width:g}" height="{height_px:g}" role="img" aria-label="Buildable envelope plan view">',
        "<defs><marker id='arrow' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto-start-reverse'>"
        "<path d='M 0 0 L 10 5 L 0 10 z' fill='#cf222e'/></marker></defs>",
        f"<rect x='0' y='0' width='{width:g}' height='{height_px:g}' fill='#ffffff'/>",
        f"<text x='{lot_x:g}' y='{margin_y - 32:g}' font-size='16' font-weight='700' fill='#172033'>"
        f"{html.escape(str(envelope.get('city') or ''))} {html.escape(str(envelope.get('zone') or ''))} buildable envelope — plan view</text>",
        f"<text x='{lot_x:g}' y='{margin_y - 14:g}' font-size='12' fill='#57606a'>"
        f"Demo lot {DEMO_LOT_WIDTH_M:g} m x {DEMO_LOT_DEPTH_M:g} m (representative, not a real parcel). Front lot line at bottom.</text>",
        # Lot rectangle.
        f"<rect x='{lot_x:g}' y='{lot_y:g}' width='{lot_w:g}' height='{lot_d:g}' fill='#f1f4f7' stroke='#57606a' stroke-width='2'/>",
        # Buildable footprint after governing setbacks.
        f"<rect x='{fp_x:g}' y='{fp_y:g}' width='{fp_w:g}' height='{fp_h:g}' fill='#1a7f37' fill-opacity='0.22' stroke='#1a7f37' stroke-width='2'/>",
    ]

    mid_x, mid_y = lot_x + lot_w / 2, lot_y + lot_d / 2
    arrows: list[tuple[str, str, float, float, float, float, float, float, str]] = []
    front = setbacks.get("front_lot_line")
    if front:
        arrows.append(("front", _label(front, "front"), mid_x, lot_y + lot_d, mid_x, fp_y + fp_h, mid_x + 8, lot_y + lot_d - insets["front"] * scale / 2, "start"))
    rear = setbacks.get("rear_lot_line")
    if rear:
        arrows.append(("rear", _label(rear, "rear"), mid_x, lot_y, mid_x, fp_y, mid_x + 8, lot_y + insets["rear"] * scale / 2 + 4, "start"))
    side = setbacks.get("side_lot_line")
    if side:
        arrows.append(("side-left", _label(side, "side"), lot_x, mid_y, fp_x, mid_y, lot_x - 8, mid_y - 8, "end"))
        arrows.append(("side-right", _label(side, "side"), lot_x + lot_w, mid_y, fp_x + fp_w, mid_y, lot_x + lot_w + 8, mid_y - 8, "start"))
    for _key, label, x1, y1, x2, y2, tx, ty, anchor in arrows:
        parts.append(
            f"<line x1='{x1:g}' y1='{y1:g}' x2='{x2:g}' y2='{y2:g}' stroke='#cf222e' stroke-width='2' marker-end='url(#arrow)'/>"
        )
        parts.append(
            f"<text x='{tx:g}' y='{ty:g}' font-size='12' fill='#172033' text-anchor='{anchor}'>{html.escape(label)}</text>"
        )

    notes_y = lot_y + lot_d + 24
    note_lines: list[str] = []
    if height:
        note_lines.append(_label(height, "max height") + f" — {height.get('role')}" + (f", {height.get('condition')}" if height.get("condition") else ""))
    if storeys:
        note_lines.append(_label(storeys, "max storeys") + f" — {storeys.get('role')}")
    lane = setbacks.get("lane_lot_line")
    if lane:
        note_lines.append(_label(lane, "lane setback") + " — demo lot has no lane; shown for reference only")
    for index, line in enumerate(note_lines):
        parts.append(
            f"<text x='{lot_x:g}' y='{notes_y + index * 16:g}' font-size='12' fill='#57606a'>{html.escape(line)}</text>"
        )
    parts.append("</svg>")
    return "".join(parts)


def _map_tab(st: Any, data: dict[str, Any], city_key: str) -> None:
    """City-centered pydeck map with a DEMO parcel showing verified constraints."""
    st.subheader("Constraint Map (Demo Parcel)")
    st.caption(
        f"Representative {DEMO_LOT_WIDTH_M:g} m x {DEMO_LOT_DEPTH_M:g} m demo lot placed at the {city_key} city "
        "centroid. It is NOT a real parcel; it only visualizes verified setback and height constraints."
    )
    gis_export = data.get("gis_export", {})
    if not gis_export:
        st.info("No gis_felt_export.json found for this city. Rerun the slim verifier.")
        return
    try:
        import pydeck as pdk
    except ModuleNotFoundError:
        st.info("pydeck not installed — pip install -e .[map]")
        return
    centroid = CITY_CENTROIDS.get(city_key)
    if centroid is None:
        st.info(f"No map centroid configured for city prefix `{city_key}`. Add one to CITY_CENTROIDS.")
        return

    import math

    lat0, lon0 = centroid
    m_per_deg_lat = 111_320.0
    m_per_deg_lon = m_per_deg_lat * math.cos(math.radians(lat0))

    def _corner(dx_m: float, dy_m: float) -> list[float]:
        return [lon0 + dx_m / m_per_deg_lon, lat0 + dy_m / m_per_deg_lat]

    half_w, half_d = DEMO_LOT_WIDTH_M / 2, DEMO_LOT_DEPTH_M / 2

    def _rect(x_min: float, x_max: float, y_min: float, y_max: float) -> list[list[float]]:
        return [_corner(x_min, y_min), _corner(x_max, y_min), _corner(x_max, y_max), _corner(x_min, y_max)]

    def _tooltip(constraint: dict[str, Any], note: str) -> str:
        quote = _short_display_quote(constraint.get("source_quote", ""), 180)
        return (
            f"<b>{html.escape(str(constraint.get('parameter_key')))}</b><br/>"
            f"{html.escape(str(constraint.get('operator')))} {html.escape(str(constraint.get('value')))} "
            f"{html.escape(str(constraint.get('unit') or ''))}<br/>"
            f"rule: {html.escape(str(constraint.get('source_rule_id')))}<br/>"
            f"{html.escape(note)}<br/><i>{html.escape(quote)}</i>"
        )

    setbacks = governing_lot_line_setbacks(gis_export)
    flat_polygons: list[dict[str, Any]] = [
        {
            "polygon": _rect(-half_w, half_w, -half_d, half_d),
            "fill": [87, 96, 106, 40],
            "tooltip": f"<b>Demo lot</b><br/>{DEMO_LOT_WIDTH_M:g} m x {DEMO_LOT_DEPTH_M:g} m representative lot (front at south edge). Not a real parcel.",
        }
    ]
    # Setback strips (no-build bands between the lot line and the inset footprint).
    front = float(setbacks.get("front", {}).get("value_numeric") or 0.0)
    rear = float(setbacks.get("rear", {}).get("value_numeric") or 0.0)
    side = float(setbacks.get("side", {}).get("value_numeric") or 0.0)
    strip_specs = [
        ("front", _rect(-half_w, half_w, -half_d, -half_d + front), front),
        ("rear", _rect(-half_w, half_w, half_d - rear, half_d), rear),
        ("side", _rect(-half_w, -half_w + side, -half_d, half_d), side),
        ("side", _rect(half_w - side, half_w, -half_d, half_d), side),
    ]
    for side_key, polygon, inset in strip_specs:
        constraint = setbacks.get(side_key)
        if constraint is None or inset <= 0:
            continue
        flat_polygons.append(
            {
                "polygon": polygon,
                "fill": [207, 34, 46, 70],
                "tooltip": _tooltip(constraint, f"{side_key} setback band (no-build)"),
            }
        )

    layers = [
        pdk.Layer(
            "PolygonLayer",
            data=flat_polygons,
            get_polygon="polygon",
            get_fill_color="fill",
            get_line_color=[87, 96, 106, 220],
            line_width_min_pixels=1,
            stroked=True,
            pickable=True,
        )
    ]

    height = export_max_height(gis_export)
    if height is not None:
        prism = [
            {
                "polygon": _rect(-half_w + side, half_w - side, -half_d + front, half_d - rear),
                "height": float(height["value_numeric"]),
                "tooltip": _tooltip(height, "buildable footprint extruded to the max verified height"),
            }
        ]
        layers.append(
            pdk.Layer(
                "PolygonLayer",
                data=prism,
                get_polygon="polygon",
                get_fill_color=[26, 127, 55, 130],
                get_line_color=[26, 127, 55, 255],
                get_elevation="height",
                extruded=True,
                stroked=True,
                pickable=True,
            )
        )
    else:
        st.caption("No verified height constraint found, so the footprint is drawn flat.")

    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=pdk.ViewState(latitude=lat0, longitude=lon0, zoom=17.4, pitch=45, bearing=0),
            tooltip={"html": "{tooltip}"},
            map_style="light",
        )
    )

    st.markdown("#### Constraints behind this demo lot")
    rows = []
    for side_key, entries in sorted(lot_line_constraints(gis_export).items()):
        for constraint in entries:
            rows.append(
                {
                    "side": side_key,
                    "parameter_key": constraint.get("parameter_key"),
                    "operator": constraint.get("operator"),
                    "value": constraint.get("value_numeric"),
                    "unit": constraint.get("unit"),
                    "condition": constraint.get("condition"),
                    "rule_id": constraint.get("source_rule_id"),
                    "evidence": _short_display_quote(constraint.get("source_quote", ""), 140),
                }
            )
    if height is not None:
        rows.append(
            {
                "side": "height",
                "parameter_key": height.get("parameter_key"),
                "operator": height.get("operator"),
                "value": height.get("value_numeric"),
                "unit": height.get("unit"),
                "condition": height.get("condition"),
                "rule_id": height.get("source_rule_id"),
                "evidence": _short_display_quote(height.get("source_quote", ""), 140),
            }
        )
    if rows:
        st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
    else:
        st.info("No lot-line or height constraints in gis_felt_export.json for this city.")
    st.caption("Bands use the most restrictive verified variant per lot line; conditional variants are listed in the table.")


def load_bylaw_sections(bylaw_dir: Path) -> list[dict[str, str]]:
    """Load extracted bylaw text from data/bylaws/<city>/, tolerating many shapes.

    A parallel extraction effort owns that folder, so this reader is
    deliberately defensive: it renders whatever sections it can find and
    returns [] when nothing usable exists.
    """
    if not bylaw_dir.is_dir():
        return []
    sections: list[dict[str, str]] = []
    # Metadata sidecars (e.g. provenance.json) are not bylaw text.
    skipped_stems = {"provenance", "manifest", "metadata", "config"}
    json_paths = sorted(path for path in bylaw_dir.glob("*.json") if path.stem.lower() not in skipped_stems)
    preferred = bylaw_dir / "extracted_text.json"
    if preferred in json_paths:
        json_paths = [preferred, *[path for path in json_paths if path != preferred]]
    for path in json_paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        sections.extend(extract_bylaw_sections(payload))
        if sections:
            return sections
    for path in sorted([*bylaw_dir.glob("*.txt"), *bylaw_dir.glob("*.md")]):
        try:
            text = path.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if text:
            sections.append({"title": path.stem, "text": text})
    return sections


def extract_bylaw_sections(payload: Any) -> list[dict[str, str]]:
    """Normalize an unknown extraction payload into [{title, text}, ...]."""
    title_keys = ("section", "section_id", "id", "anchor", "number", "title", "heading", "name")
    text_keys = ("text", "content", "body", "raw_text", "section_text")

    def _from_dict_item(item: dict[str, Any], fallback_title: str) -> dict[str, str] | None:
        text = next((str(item[key]) for key in text_keys if isinstance(item.get(key), str) and item[key].strip()), "")
        if not text:
            return None
        title = next((str(item[key]) for key in title_keys if item.get(key) not in (None, "")), fallback_title)
        heading = next((str(item[key]) for key in ("title", "heading") if item.get(key) not in (None, "")), "")
        if heading and heading != title:
            title = f"{title} — {heading}"
        return {"title": title, "text": text}

    sections: list[dict[str, str]] = []
    if isinstance(payload, str):
        if payload.strip():
            sections.append({"title": "Extracted text", "text": payload})
    elif isinstance(payload, list):
        for index, item in enumerate(payload, start=1):
            if isinstance(item, dict):
                section = _from_dict_item(item, f"Section {index}")
                if section:
                    sections.append(section)
            elif isinstance(item, str) and item.strip():
                sections.append({"title": f"Section {index}", "text": item})
    elif isinstance(payload, dict):
        nested = payload.get("sections")
        if isinstance(nested, (list, dict)):
            return extract_bylaw_sections(nested if isinstance(nested, list) else [
                {"title": key, **(value if isinstance(value, dict) else {"text": str(value)})}
                for key, value in nested.items()
            ])
        direct = _from_dict_item(payload, "Extracted text")
        if direct:
            sections.append(direct)
        else:
            # Loose {key: text} shape: only accept prose-like values so
            # metadata payloads (urls, hashes, timestamps) are not mistaken
            # for bylaw sections.
            for key, value in payload.items():
                if isinstance(value, str) and len(value.split()) >= 8:
                    sections.append({"title": str(key), "text": value})
                elif isinstance(value, dict):
                    section = _from_dict_item(value, str(key))
                    if section:
                        sections.append(section)
    return sections


def highlight_evidence(section_text: str, quote: str) -> tuple[str, bool]:
    """Mark the cited evidence inside section text via simple substring markup.

    Both sides are whitespace-normalized; progressively shorter quote prefixes
    are tried so truncated evidence quotes still anchor. Returns escaped HTML
    plus whether a match was found.
    """
    normalized = " ".join(str(section_text or "").split())
    words = " ".join(str(quote or "").split()).rstrip(". ").removesuffix("...").split()
    for length in (len(words), 24, 16, 10, 6):
        needle = " ".join(words[:length])
        if len(needle) < 12:
            break
        index = normalized.lower().find(needle.lower())
        if index >= 0:
            end = index + len(needle)
            return (
                html.escape(normalized[:index])
                + "<mark class='evidence-hit'>"
                + html.escape(normalized[index:end])
                + "</mark>"
                + html.escape(normalized[end:]),
                True,
            )
    return html.escape(normalized), False


def _rule_evidence_quote(rule: dict[str, Any]) -> str:
    """Best evidence text for a rule: source text, then any proof-trace quote."""
    quote = _source_text(rule)
    if quote:
        return quote
    proof_trace = rule.get("proof_trace")
    if isinstance(proof_trace, dict):
        for entry in proof_trace.values():
            if isinstance(entry, dict) and entry.get("evidence_quote"):
                return str(entry["evidence_quote"])
    return ""


def _ask_the_bylaw_panel(st: Any, output_dir: Path) -> None:
    """Local hybrid-RAG retrieval over the city's bylaw corpus. ADVISORY only:
    answers are retrieved clauses with section ids — never a verification."""
    index_path = bylaw_index_path(output_dir)
    city_stem = city_stem_from_dir(output_dir)
    st.markdown("#### Ask the bylaw")
    if index_path is None:
        st.info(
            "No retrieval index yet — build it with "
            f"`.venv/bin/python scripts/build_rag_index.py --city {city_stem}`."
        )
        return
    question = st.text_input(
        "Question (retrieval is local BM25+dense with section expansion; results are clauses, not advice)",
        key=f"rag_q_{city_stem}",
        placeholder="e.g. what is the maximum height for a backyard suite",
    )
    if not question:
        return
    try:
        from burnaby_prototype.bylaw_rag import load_index

        hits = load_index(index_path).ask(question, top_k=4)
    except Exception as error:  # pragma: no cover - depends on optional deps
        st.warning(f"Retrieval unavailable: {error}")
        return
    if not hits:
        st.info("No clause shares any term with that question — try the bylaw's own vocabulary.")
        return
    for hit in hits:
        label = hit.get("section") or hit.get("chunk_id")
        st.markdown(
            f"<div class='bylaw-section'><b>[{html.escape(str(label))}]</b> "
            f"score {hit['score']:.4f}<br>{html.escape(_short_display_quote(hit.get('section_text') or hit.get('text') or ''))}</div>",
            unsafe_allow_html=True,
        )
    st.caption("Advisory retrieval — the verified rule set remains the only executable output.")


def _bylaw_tab(st: Any, data: dict[str, Any]) -> None:
    """Section-anchored bylaw text with rule-picked evidence highlighting."""
    st.subheader("Bylaw Text")
    output_dir = Path(data.get("output_dir") or DEFAULT_OUTPUT_DIR)
    bylaw_dir = ROOT / "data" / "bylaws" / city_stem_from_dir(output_dir)
    sections = load_bylaw_sections(bylaw_dir)
    _ask_the_bylaw_panel(st, output_dir)

    rules = [(rule, "verified") for rule in data["verified"]] + [(rule, "review") for rule in data["review"]]
    rule_options = {
        f"{rule.get('rule_id')} [{status}] — {_humanize(rule.get('rule_object'))}": rule
        for rule, status in rules
        if rule.get("rule_id")
    }

    if not sections:
        st.info(
            f"No extracted bylaw text found under `{bylaw_dir}` yet — falling back to the "
            "evidence-units view. Once extraction lands there, this tab shows section-anchored bylaw text."
        )
        if rule_options:
            selected = st.selectbox("Rule", list(rule_options), key="bylaw_rule_fallback")
            rule = rule_options[selected]
            quote = _rule_evidence_quote(rule)
            if quote:
                st.markdown("#### Cited evidence")
                st.markdown(
                    f"<div class='bylaw-section'><mark class='evidence-hit'>{html.escape(_short_display_quote(quote))}</mark></div>",
                    unsafe_allow_html=True,
                )
        evidence_units = data.get("evidence_units", [])
        if evidence_units:
            st.markdown("#### Evidence units")
            rows = [
                {
                    "evidence_id": unit.get("evidence_id"),
                    "page": unit.get("page"),
                    "type": unit.get("evidence_type"),
                    "section": unit.get("section"),
                    "text": _short_display_quote(unit.get("evidence_text", ""), 200),
                }
                for unit in evidence_units[:250]
            ]
            st.dataframe(_display_rows(rows), width="stretch", hide_index=True)
        return

    st.caption(f"{len(sections)} extracted section(s) from `{bylaw_dir}`. Pick a rule to highlight its cited evidence.")
    selected_rule_label = st.selectbox("Rule", ["(none)", *rule_options], key="bylaw_rule_picker")
    quote = ""
    if selected_rule_label != "(none)":
        quote = _rule_evidence_quote(rule_options[selected_rule_label])
        if not quote:
            st.caption("This rule carries no evidence quote; sections are shown without highlighting.")

    matched_index = 0
    highlighted: dict[int, str] = {}
    if quote:
        for index, section in enumerate(sections):
            markup, hit = highlight_evidence(section["text"], quote)
            if hit:
                highlighted[index] = markup
                if len(highlighted) == 1:
                    matched_index = index
        if highlighted:
            st.success(f"Evidence found in {len(highlighted)} section(s).")
        else:
            st.warning("The cited evidence text was not found verbatim in any extracted section.")

    titles = [section["title"] for section in sections]
    picked = st.selectbox("Section", range(len(titles)), index=matched_index, format_func=lambda i: titles[i], key="bylaw_section_picker")
    body = highlighted.get(picked) or html.escape(" ".join(sections[picked]["text"].split()))
    st.markdown(
        f"<div class='bylaw-section'><h4>{html.escape(sections[picked]['title'])}</h4>{body}</div>",
        unsafe_allow_html=True,
    )


def _envelope_3d_tab(st: Any, data: dict[str, Any], output_dir: Path) -> None:
    """Three.js buildable-envelope viewer with an always-available SVG fallback."""
    st.subheader("3D Buildable Envelope")
    envelope = data.get("buildable_envelope", {})
    if not envelope:
        st.info(
            "No buildable_envelope.json for this city yet. The 3D viewer and plan view appear once the "
            "verified-only envelope export exists in the output directory."
        )
        return
    st.caption(
        f"Demo {DEMO_LOT_WIDTH_M:g} m x {DEMO_LOT_DEPTH_M:g} m lot (representative, not a real parcel), "
        "derived only from verified rules in buildable_envelope.json."
    )

    html_path = output_dir / "envelope_3d.html"
    if html_path.exists():
        try:
            # Prefer the modern embed API; components.v1.html is deprecated in
            # streamlit >= 1.58 but kept as a fallback for older installs.
            if hasattr(st, "iframe"):
                st.iframe(html_path, height=640)
            else:
                from streamlit.components.v1 import html as components_html

                components_html(html_path.read_text(encoding="utf-8"), height=640)
            st.caption("Three.js viewer (CDN). Drag to orbit; hover faces for the governing rule.")
        except Exception:  # embed support varies by streamlit version
            st.info("Inline embedding unavailable in this Streamlit version — showing the SVG plan view only.")
    else:
        st.info(
            "Three.js viewer not built yet. Run: "
            f"`.venv/bin/python scripts/build_envelope_3d.py --output-dir {output_dir}`"
        )

    st.markdown("#### Plan view (always available, printable)")
    st.markdown(build_envelope_svg(envelope), unsafe_allow_html=True)

    governing = envelope_governing_setbacks(envelope)
    rows = [
        {
            "constraint": lot_line,
            "value": entry.get("value_numeric"),
            "unit": entry.get("unit"),
            "operator": entry.get("operator"),
            "condition": entry.get("condition"),
            "applies_to": entry.get("applies_to"),
            "rule_id": entry.get("rule_id"),
        }
        for lot_line, entry in sorted(governing.items())
    ]
    for picker, name in ((envelope_max_height, "max_height"), (envelope_max_storeys, "max_storeys")):
        entry = picker(envelope)
        if entry:
            rows.append(
                {
                    "constraint": f"{name} ({entry.get('role')})",
                    "value": entry.get("value_numeric"),
                    "unit": entry.get("unit"),
                    "operator": entry.get("operator"),
                    "condition": entry.get("condition"),
                    "applies_to": entry.get("applies_to"),
                    "rule_id": entry.get("rule_id"),
                }
            )
    if rows:
        st.markdown("#### Governing constraints (most restrictive verified variant per family)")
        st.dataframe(_display_rows(rows), width="stretch", hide_index=True)


def _render_kpis(st: Any, data: dict[str, Any], filtered_items: list[dict[str, Any]]) -> None:
    validation = data["validation"]
    benchmark = data["benchmark"]
    metrics = benchmark.get("rule_metrics", {})
    proposal = benchmark.get("proposal_metrics", {})
    counts = validation.get("bucket_counts", {})
    review_counts = _named_counts(data.get("router", {}).get("summary", {}).get("action_counts", []))
    intelligence = data.get("intelligence", {})
    bundle_rerun = data.get("bundle_rerun", {})
    bundle_promotion = data.get("bundle_promotion", {})
    semantic = data.get("semantic", {})
    resolution = data.get("resolution", {}).get("summary", {})
    # These KPI cards put the two most actionable review-reduction paths in the
    # first screen: alternate evidence and safe verifier tuning.
    cards = [
        ("Verified", counts.get("verified", 0), "verified"),
        ("Review", counts.get("review_needed", 0), "review"),
        ("Filtered Review", len(filtered_items), "review"),
        ("Better Evidence", review_counts.get("retry_with_better_evidence", 0), ""),
        ("Bundle Safe Retry", intelligence.get("safe_retry_count", 0), ""),
        ("Promoted By Bundle", bundle_promotion.get("promotion_count", 0), "verified"),
        ("Bundle Ready", bundle_rerun.get("promotion_ready_count", 0), ""),
        ("Evidence-Fix Path", resolution.get("can_promote_after_evidence_fix_count", 0), ""),
        ("Semantic Near-Match", semantic.get("high_similarity_count", 0), ""),
        ("Precision", f"{metrics.get('verified_precision', 0):.2f}", "verified"),
        ("False Approvals", proposal.get("false_approval_count", 0), "rejected"),
    ]
    cards_html = "".join(
        f"<div class='metric{' metric-' + tone if tone else ''}'>"
        f"<div class='metric-label'>{html.escape(label)}</div>"
        f"<div class='metric-value'>{html.escape(str(value))}</div></div>"
        for label, value, tone in cards
    )
    st.markdown(f"<div class='metric-grid'>{cards_html}</div>", unsafe_allow_html=True)


def _render_header(st: Any, city_label: str = "Burnaby R1") -> None:
    """Render a compact product-style header for the review console."""
    st.markdown(
        f"""
<div class="app-header">
  <div>
    <div class="eyebrow">Verification Review Console</div>
    <h1>{html.escape(city_label)} Verification Dashboard</h1>
    <p>Inspect review rules, compare candidate claims against verified rules, and identify the safest path to reduce review volume.</p>
  </div>
  <div class="status-legend">
    <span class="status-pill status-verified">verified</span>
    <span class="status-pill status-review">review</span>
    <span class="status-pill status-rejected">rejected</span>
    <span class="status-pill status-not_used">not_used</span>
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
  <div class="guide-card"><b>3. Pick the next action</b><span>Use Evidence Repair, Evidence Rerun, and the Review tab to decide whether the issue is evidence, verifier tuning, or legal review.</span></div>
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
3. If the meaning matches, check whether `Evidence Rerun` or the `Review` tab says it is safe to tune.
4. If the issue involves exceptions, conflicts, or legal scope, keep it in human review.
"""
        )


def _action_summary(st: Any, data: dict[str, Any]) -> None:
    """Surface the highest-value review-volume reduction paths."""
    review_counts = _named_counts(data.get("router", {}).get("summary", {}).get("action_counts", []))
    promotion = data.get("bundle_promotion", {})
    semantic = data.get("semantic", {})
    resolution = data.get("resolution", {}).get("summary", {})
    cards = [
        (
            "Guarded bundle promotions",
            promotion.get("promotion_count", 0),
            "Review rules moved to verified only after deterministic bundle rerun passed.",
        ),
        (
            "Retry with better evidence",
            review_counts.get("retry_with_better_evidence", 0),
            "Repair evidence packets before changing verifier logic.",
        ),
        (
            "Safe verifier tuning",
            review_counts.get("safe_verifier_tuning_candidate", 0),
            "Candidates likely need general rule-pattern support.",
        ),
        (
            "Resolution evidence-fix path",
            resolution.get("can_promote_after_evidence_fix_count", 0),
            "Remaining review items that may be repairable by stronger deterministic evidence, not by semantic score.",
        ),
        (
            "Semantic near-matches",
            semantic.get("high_similarity_count", 0),
            "Meaning-similar review items to inspect, not automatic approvals.",
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

    scope_phrase = f" for {scope.strip()}" if scope else ""
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


def _intelligence_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one evidence intelligence item in plain English."""
    missing = _list_text(item.get("bundle_missing_fields", []))
    blocked = _list_text(item.get("blocked_by", []))
    safe = "safe to rerun through the deterministic verifier" if item.get("safe_retry") else "not safe to rerun automatically"
    return [
        f"Candidate claim: {_rule_sentence(item)}",
        f"The best evidence bundle has score {_display_value(item.get('bundle_score'))} and is {safe}.",
        f"The bundle currently supports: {_list_text(item.get('bundle_supported_fields', []))}. Missing fields: {missing}.",
        f"Blocked by: {blocked}.",
        f"Next action: `{item.get('next_action')}`. Bundle sentence: {item.get('bundle_sentence')}",
    ]


def _router_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one decision-tree route in plain English."""
    path = " -> ".join(item.get("decision_path", [])) or "no path recorded"
    semantic_match = item.get("semantic_verified_rule_id") or "none"
    semantic_score = _display_value(item.get("semantic_score"))
    semantic_blockers = _list_text(item.get("semantic_guardrail_blockers", [])) or "none"
    return [
        f"Candidate claim: {item.get('candidate_sentence') or _rule_sentence(item)}",
        f"Original evidence says: {item.get('evidence_sentence') or 'no evidence sentence available'}",
        f"The review tree routed this to `{item.get('review_category')}` with action `{item.get('action_bucket')}`.",
        f"Semantic review class: `{item.get('semantic_review_class')}`. Closest verified match: `{semantic_match}` with score {semantic_score}; blockers: {semantic_blockers}.",
        f"Decision path: {path}.",
        f"Human instruction: {item.get('human_instruction')}",
        f"Evidence bundle summary: {item.get('bundle_sentence')}",
    ]


def _resolution_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one review-resolution label in plain English."""
    can_fix = (
        "has a plausible deterministic evidence-fix path"
        if item.get("can_promote_after_evidence_fix")
        else "does not currently have a safe deterministic promotion path"
    )
    semantic = item.get("semantic_verified_rule_id") or "none"
    score = _display_value(item.get("semantic_score"))
    return [
        f"Candidate claim: {item.get('candidate_sentence') or _rule_sentence(item)}",
        f"Original evidence says: {item.get('evidence_sentence') or 'no evidence sentence available'}",
        f"The final resolution is `{item.get('resolution')}`, so the next step is `{item.get('next_step_type')}`.",
        f"This item {can_fix}. Support gaps: {_list_text(item.get('support_gaps', []))}.",
        f"Closest semantic verified match: `{semantic}` with score {score}. Guardrail blockers: {_list_text(item.get('semantic_guardrail_blockers', []))}.",
        f"Bundle rerun decision: `{item.get('bundle_rerun_decision')}` with gaps {_list_text(item.get('bundle_rerun_gaps', []))}.",
        f"Human next step: {item.get('human_next_step')}",
        f"Where to check in the bylaw: {item.get('where_to_find_it')}",
    ]


def _bundle_rerun_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one evidence-bundle rerun result in plain English."""
    decision = str(item.get("retry_decision") or "unknown")
    ready = "promotion-ready" if item.get("promotion_ready") else "not promotion-ready"
    return [
        f"Candidate claim: {_rule_sentence(item)}",
        f"The rerun used bundle `{item.get('bundle_evidence_id')}` built from: {_list_text(item.get('bundle_evidence_ids', []))}.",
        f"The deterministic verifier returned `{decision}` with gaps: {_list_text(item.get('retry_support_gaps', []))}.",
        f"The result is {ready}. Risk flags: {_list_text(item.get('promotion_risk_flags', []))}.",
        f"Recommendation: {item.get('promotion_recommendation') or 'keep in review until the verifier and benchmark support promotion'}.",
    ]


def _bundle_display_evidence(item: dict[str, Any]) -> dict[str, Any]:
    """Return one evidence-like object for the bylaw lookup panel."""
    bundle = item.get("best_evidence_bundle", [])
    first = bundle[0] if bundle else {}
    return {
        "page": first.get("page"),
        "evidence_quote": first.get("evidence_quote") or item.get("original_evidence_sentence"),
    }


def _bundle_rows(item: dict[str, Any]) -> list[dict[str, Any]]:
    """Return display rows for a best evidence bundle."""
    return [
        {
            "evidence_id": evidence.get("evidence_id"),
            "page": evidence.get("page"),
            "type": evidence.get("evidence_type"),
            "score": evidence.get("raw_score"),
            "confidence": evidence.get("bundle_confidence"),
            "supported_fields": ", ".join(evidence.get("supported_fields", [])),
            "reasons": ", ".join(evidence.get("match_reasons", [])),
            "quote": evidence.get("evidence_quote"),
        }
        for evidence in item.get("best_evidence_bundle", [])
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


def _safe_tuning_detail_sentences(item: dict[str, Any]) -> list[str]:
    """Explain one verifier-tuning backlog item in plain English."""
    gaps = _list_text(item.get("support_gaps", []))
    tests = _list_text(item.get("required_tests", []))
    guardrails = _list_text(item.get("guardrails", []))
    rerun = item.get("rerun_decision") or "not rerun"
    rerun_ready = "promotion-ready" if item.get("rerun_promotion_ready") else "not promotion-ready"
    return [
        f"Candidate claim: {_rule_sentence(item)}",
        f"This is a `{item.get('tuning_type')}` tuning candidate because the blocking gaps are: {gaps}.",
        f"Proposed experiment: {item.get('proposed_experiment')}",
        f"Evidence rerun status: `{rerun}`, {rerun_ready}.",
        f"Required validation: {tests}.",
        f"Guardrails that must remain true: {guardrails}.",
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
1. Open the [{_ACTIVE_SOURCE['label']}]({_ACTIVE_SOURCE['url']}).
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
    # Design system: typography scale, spacing, KPI cards, and STRICT status
    # color semantics (verified green, review amber, rejected red, not_used grey)
    # reused by every status-coded element below. Presentation only.
    st.markdown(
        """
<style>
:root {
  --status-verified: #1a7f37;
  --status-review: #9a6700;
  --status-rejected: #cf222e;
  --status-not-used: #57606a;
  --ink: #172033;
  --ink-soft: #5d6875;
  --line: #d9e0e8;
}
html, body, [class*="css"] {font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;}
.block-container {padding-top: 1.5rem; max-width: 1500px;}
h1 {font-size:30px;} h2 {font-size:24px;} h3 {font-size:19px;} h4 {font-size:16px;}
.app-header {display:flex; justify-content:space-between; align-items:flex-start; gap:16px; border:1px solid var(--line); border-radius:8px; padding:18px 20px; background:linear-gradient(180deg,#ffffff,#f7fafc); margin-bottom:14px;}
.app-header h1 {font-size:30px; line-height:1.15; margin:2px 0 6px; color:var(--ink); letter-spacing:0;}
.app-header p {margin:0; color:#526070; font-size:15px;}
.eyebrow {font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:#2563eb; font-weight:700;}
.status-legend {display:flex; gap:6px; flex-wrap:wrap; justify-content:flex-end;}
.status-pill {font-size:11px; font-weight:700; padding:3px 9px; border-radius:999px; color:#fff; letter-spacing:.02em;}
.status-pill.status-verified, .status-verified-bg {background:var(--status-verified);}
.status-pill.status-review, .status-review-bg {background:var(--status-review);}
.status-pill.status-rejected, .status-rejected-bg {background:var(--status-rejected);}
.status-pill.status-not_used, .status-not_used-bg {background:var(--status-not-used);}
.metric-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(118px,1fr)); gap:10px; margin:12px 0 18px;}
.metric {border:1px solid #d7dde5; border-radius:8px; padding:13px 14px; background:#fff; box-shadow:0 1px 2px rgba(15,23,42,.04); min-height:86px;}
.metric-verified {border-top:4px solid var(--status-verified);}
.metric-review {border-top:4px solid var(--status-review);}
.metric-rejected {border-top:4px solid var(--status-rejected);}
.metric-not_used {border-top:4px solid var(--status-not-used);}
.metric-label {font-size:10px; line-height:1.25; color:var(--ink-soft); text-transform:uppercase; font-weight:700; overflow-wrap:normal;}
.metric-value {font-size:25px; font-weight:750; color:#111827;}
.guidance-grid, .action-grid {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:12px 0 20px;}
.guide-card, .action-card {border:1px solid var(--line); border-radius:8px; background:#fff; padding:14px 15px;}
.guide-card b {display:block; color:var(--ink); margin-bottom:5px;}
.guide-card span, .action-card p {color:var(--ink-soft); font-size:14px; margin:0;}
.action-value {font-size:28px; font-weight:760; color:var(--status-verified);}
.action-title {font-weight:720; color:var(--ink); margin:1px 0 4px;}
.sentence-card {border:1px solid var(--line); border-radius:8px; padding:15px 16px; min-height:142px; background:#fff; box-shadow:0 1px 2px rgba(15,23,42,.04);}
.sentence-card p {font-size:17px; line-height:1.45; color:#111827; margin:8px 0 10px;}
.sentence-card span {font-size:12px; color:#667085;}
.sentence-title {font-size:12px; text-transform:uppercase; letter-spacing:.06em; font-weight:760;}
.sentence-review {border-top:4px solid var(--status-review);}
.sentence-verified {border-top:4px solid var(--status-verified);}
.sentence-neutral {border-top:4px solid var(--status-not-used);}
.bylaw-section {border:1px solid var(--line); border-radius:8px; background:#fff; padding:14px 16px; margin:8px 0; line-height:1.6; color:var(--ink); white-space:pre-wrap;}
.bylaw-section h4 {margin:0 0 8px; color:var(--ink);}
mark.evidence-hit {background:#fff3bf; border-bottom:2px solid var(--status-review); padding:1px 2px; border-radius:2px;}
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
