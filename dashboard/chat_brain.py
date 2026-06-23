"""Advisory chat helpers for the "Ask the Bylaw" assistant — ADVISORY, read-only.

This module is the brain behind the dashboard chatbot. It does four things, all
*deterministically* and all *read-only* over the verifier's existing JSON
outputs:

1. ``reformulate_and_route`` — classify a user's question into an intent and (for
   follow-ups) rewrite it into a standalone search query, using a tiny optional
   LLM call with a deterministic keyword fallback.
2. ``detect_rule_reference`` — match a question to a specific verified/review rule.
3. ``explain_verification`` — turn a rule + its ``support_gaps`` into a plain,
   friendly explanation: is it verified or in review, why it did not pass yet,
   what is likely missing, and where to look in the original bylaw.
4. ``reconstruct_dimensional_tables`` / ``rule_list_table`` — rebuild the original
   dimensional bylaw tables and tabular rule lists for embedding in answers.

It never verifies, approves, rejects, promotes, or writes anything. The
deterministic verifier remains the sole authority (no verify-path module imports
this; pinned by ``tests/test_bylaw_chat.py``). The only "facts" it states about
verification come straight from the verifier's own JSON via
:func:`proof_trace.human_reason` — never invented by an LLM.
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable

# --- Self-contained verifier vocabulary --------------------------------------
# This module is mirrored VERBATIM to ``dashboard/chat_brain.py`` so the chatbot
# brain runs on the Streamlit Cloud deploy, where the ``burnaby_prototype``
# package is NOT installed. To keep that mirror a single portable file, the gap
# catalogs and the gap -> plain-English map are inlined here rather than imported
# from ``decision_policy`` / ``proof_trace``. ``tests/test_bylaw_chat.py`` asserts
# (a) the two files stay byte-identical and (b) this map stays in sync with the
# verifier's own ``proof_trace.human_reason``.
ADVISORY_GAPS = frozenset({"upstream_extraction_requested_review"})
CRITICAL_REJECTION_GAPS = frozenset({
    "source_evidence_id_not_found",
    "value_not_found_in_evidence",
    "unit_not_found_in_evidence",
    "rule_object_unit_not_compatible",
    "table_operator_refuted",
    "value_bound_to_foreign_unit",
    "column_value_mismatch",
})
NOT_USED_GAPS = frozenset({
    "cross_reference_only",
    "outside_current_rule_contract",
    "definition_not_rule",
    "non_numeric_value_for_numeric_rule",
    "outside_target_section",
})

_HUMAN_REASON_LABELS = {
    "source_evidence_id_not_found": "the candidate cites evidence that is missing",
    "value_not_found_in_evidence": "the proposed value is not visible in the cited evidence",
    "unit_not_found_in_evidence": "the proposed unit is not visible in the cited evidence",
    "operator_not_supported": "the proposed operator is not supported by the cited wording",
    "applies_to_not_supported": "the applies_to field is not clearly grounded",
    "constraint_scope_not_supported": "the scope or condition is not clearly grounded",
    "rule_object_not_canonical": "the rule object is outside the verifier's known contract",
    "rule_object_not_supported": "the cited evidence does not support the proposed rule object",
    "rule_object_unit_not_compatible": "the unit is not compatible with the proposed rule object",
    "table_operator_refuted": "the table wording supports the opposite operator direction",
    "table_rule_object_not_supported": "the table context does not support the rule object",
    "table_applies_to_not_supported": "the table row or column does not support applies_to",
    "table_condition_not_supported": "the table row or column does not support the condition",
    "table_column_not_target_scope": "the table column does not match the configured target scope",
    "upstream_extraction_requested_review": "the extraction layer marked this candidate for review",
    "non_numeric_value_for_numeric_rule": "the candidate has a text value for a numeric GIS rule family",
    "unresolved_exception_cue": "the evidence contains exception or override wording that needs review",
    "text_candidate_requires_review": "Text rules are held for review until they pass the GIS text-rule contract (value/unit/operator/scope/direction)",
    "text_condition_not_supported": "the cited text does not support a material condition needed for text-rule verification",
    "cross_reference_only": "the candidate is a bylaw section cross-reference, not a directly validated rule",
    "outside_current_rule_contract": "the rule family is outside the current validation contract",
    "outside_target_section": "the source section is outside the configured target sections for this verification run",
    "definition_not_rule": "the value sits inside a defined-term sentence, which defines vocabulary rather than a rule",
    "column_value_mismatch": "the claimed table column does not hold this value — it belongs to a different column",
    "applicability_not_grounded": "the claimed dwelling-type/unit-count column cannot be found in the table",
    "column_qualifier_not_claimed": "the table column carries a qualifier (e.g. Frequent Transit Network Area) the rule does not claim",
    "conditional_cell_condition_missing": "the table cell is conditional (e.g. by lot size) and the rule does not claim its branch condition",
    "anchored_row_family_mismatch": "the table row this cell belongs to regulates a different rule family",
    "enumerated_branch_condition_missing": "the clause lists several values by condition (e.g. side vs rear) and the rule does not prove which branch its value belongs to",
    "allowance_trigger_threshold": "the value is the trigger of a 'no maximum/minimum ... where' allowance, not a requirement",
    "value_bound_to_foreign_unit": "every visible occurrence of the value is glued to a unit from a different rule family",
    "coefficient_operand_not_value": "the value is a ratio coefficient (e.g. 0.25 multiplied by the site area), not an absolute cap",
    "range_bound_not_maximum": "the value is one range bound (e.g. 1 to 3) while a higher range is listed — not the overall maximum",
}


def human_reason(support_gaps: list[str]) -> str:
    """Convert machine gap codes into readable review reasons.

    A package-free mirror of :func:`burnaby_prototype.proof_trace.human_reason`;
    kept here so this module is portable to the dashboard-only cloud deploy.
    """
    if not support_gaps:
        return "all critical evidence checks passed"
    return "; ".join(_HUMAN_REASON_LABELS.get(gap, gap.replace("_", " ")) for gap in support_gaps)

# ---------------------------------------------------------------------------
# Intent vocabulary
# ---------------------------------------------------------------------------

INTENTS = ("why_verification", "specific_rule", "definition", "list_table", "out_of_scope")

ADVISORY_NOTE = (
    "I'm an advisory assistant — I explain the verifier's result and the bylaw text, "
    "but I never approve, verify, reject, or change a rule."
)

# Cue phrases (substring match on the lowercased question). Order of the checks in
# ``_keyword_route`` encodes priority.
_WHY_CUES = (
    "why", "in review", "needs review", "under review", "not verified", "unverified",
    "didn't pass", "did not pass", "didnt pass", "not pass", "fail", "failed",
    "held", "on hold", "rejected", "not confirmed", "not approved", "blocked",
    "what's wrong", "whats wrong", "what is wrong", "problem with", "missing",
    "gap", "what's missing", "whats missing", "is it verified", "was it verified",
    "is it confirmed", "did it pass", "status of",
)
_LIST_CUES = (
    "list all", "list the", "show all", "show me all", "show me the", "all the",
    "every ", "as a table", "in a table", "table of", "summary of", "what are the",
    "which rules", "give me the", "all rules", "all of the", "overview of",
)
_DEFINE_CUES = (
    "what is a ", "what is an ", "what's a ", "what's an ", "what does ", "define ",
    "definition of", "meaning of", "what counts as", "what do you mean by",
    "what is meant by", "explain the term",
)
# rule family -> phrases that point at it (lowercased substring match)
_RULE_FAMILY_CUES: dict[str, tuple[str, ...]] = {
    "setback": ("setback", "set back", "yard", "from the property line", "from the lot line"),
    "height": ("height", "how tall", "how high", "tall", "storey", "storeys", "stories", "floors"),
    "lot_area": ("lot area", "parcel area", "lot size", "parcel size", "site area", "minimum lot"),
    "lot_coverage": ("lot coverage", "site coverage", "coverage", "footprint"),
    "dwelling_units": ("dwelling unit", "dwelling units", "number of units", "how many units", "how many homes", "density", "secondary suite", "suites"),
    "building_separation": ("building separation", "separation", "between buildings", "space between"),
    "floor_area": ("floor area", "gross floor area", "floor space"),
    "floor_space_ratio": ("floor space ratio", "fsr", "far ratio"),
    "impervious_surface": ("impervious", "permeable", "hard surface", "soft landscaping"),
    "storeys": ("storey", "storeys", "stories", "how many floors", "number of storeys"),
    "automatic_sprinkler": ("sprinkler", "fire suppression"),
    "fire_access_corridor": ("fire access", "access corridor", "fire corridor"),
}
# generic zoning vocabulary used only to decide "is this even about the bylaw?"
# Stopwords are filtered out so a function word like "the" (which appears inside
# family cue phrases such as "from the property line") can never make an
# unrelated question ("what's the weather today?") read as in-scope.
_VOCAB_STOP = {
    "the", "of", "from", "a", "an", "to", "for", "how", "many", "much", "is", "are",
    "be", "in", "on", "at", "by", "or", "and", "no", "not", "do", "you", "mean",
    "number", "set", "me", "my", "this", "that", "with",
}
_BYLAW_VOCAB = {
    "bylaw", "zoning", "zone", "rule", "rules", "lot", "parcel", "building", "buildings",
    "rowhouse", "dwelling", "unit", "units", "suite", "permitted", "allowed", "minimum",
    "maximum", "verified", "review", "regulation", "regulations",
}
for _phrases in _RULE_FAMILY_CUES.values():
    for _p in _phrases:
        _BYLAW_VOCAB.update(w for w in _p.split() if w not in _VOCAB_STOP and len(w) > 2)

_FOLLOWUP_STARTERS = (
    "why", "what about", "and ", "ok ", "okay ", "but ", "how about", "what if",
    "that", "this", "those", "these", "it ", "its ", "it's", "same", "also",
)


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", str(text or "").lower()))


def _numbers(text: str) -> list[float]:
    out: list[float] = []
    for tok in re.findall(r"\d+(?:\.\d+)?", str(text or "").replace(",", "")):
        try:
            out.append(float(tok))
        except ValueError:
            continue
    return out


def _families_in(text: str) -> list[str]:
    low = str(text or "").lower()
    hits = []
    for family, phrases in _RULE_FAMILY_CUES.items():
        if any(phrase in low for phrase in phrases):
            hits.append(family)
    return hits


def _last_user_question(history: list[dict[str, Any]] | None) -> str:
    for turn in reversed(history or []):
        if turn.get("role") == "user" and turn.get("content"):
            return str(turn["content"])
    return ""


def _keyword_route(question: str, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Deterministic intent router + follow-up query carry-over.

    Always available (no key, no network). Returns the same shape as
    :func:`reformulate_and_route`.
    """
    raw = str(question or "").strip()
    low = raw.lower()
    standalone = raw

    # Follow-up carry-over: a short/bare question that leans on the previous turn.
    prev = _last_user_question(history)
    looks_followup = (
        len(_tokens(raw)) <= 4
        or low.startswith(_FOLLOWUP_STARTERS)
    ) and bool(prev)
    if looks_followup and prev.lower() != low:
        # Fold the prior topic in so retrieval has something concrete to match.
        prev_families = _families_in(prev)
        if prev_families and not _families_in(raw):
            standalone = f"{raw} ({prev})".strip()

    families = _families_in(standalone)
    has_question_word = any(w in low for w in ("what", "how", "which", "is ", "are ", "can ", "does ", "list", "show"))

    why_strong = any(cue in low for cue in _WHY_CUES)
    list_hit = any(cue in low for cue in _LIST_CUES)
    # A bare "...verified?" / "...confirmed?" is a status question, but an explicit
    # listing request ("show me all verified rules") is handled first.
    status_word = any(w in low for w in ("verified", "confirmed", "did it pass", "does it pass", "is it approved"))
    define_hit = any(cue in low for cue in _DEFINE_CUES)
    strong_define = define_hit and (
        "mean" in low
        or "definition" in low
        or "define " in low
        or "what counts as" in low
        or "what do you mean" in low
        or low.startswith(("what is a ", "what is an ", "what's a ", "what's an "))
    )
    # A CONCEPT/definition question ("what is a laneway home?", "what does setback
    # mean?", "what is FSR?") should be explained from general knowledge, NOT forced
    # through retrieval. We treat a "what is/does ..." question as a concept UNLESS
    # it asks for a specific number/limit ("what is the MINIMUM lot area") or names a
    # family with the definite article ("what is THE rear setback" -> wants the value).
    value_cue = any(t in low for t in (
        "minimum", "maximum", " max", " min ", "how tall", "how high", "how big",
        "how much", "how many", "how wide", "how long", "how far", "limit",
        "requirement", "required", "allowed", "permitted", "what's the", "whats the",
        "can i build", "value of", "number of",
    ))
    definite_family = bool(families) and (
        low.startswith(("what is the ", "what's the ", "what are the ")) or " the " in f" {low} "
    )
    concept = (
        strong_define
        or (low.startswith(("what is ", "what's ", "what are ", "what does ")) and not value_cue)
    ) and not definite_family

    if why_strong:
        intent = "why_verification"
    elif list_hit:
        intent = "list_table"
    elif status_word:
        intent = "why_verification"
    elif concept:
        intent = "definition"
    elif families:
        intent = "specific_rule"
    elif _tokens(low) & _BYLAW_VOCAB:
        intent = "specific_rule" if has_question_word else "definition"
    else:
        intent = "out_of_scope"

    return {
        "intent": intent,
        "standalone_query": standalone,
        "families": families,
        "confidence": 0.6,
        "method": "keyword",
    }


_ROUTER_PROMPT = (
    "You are a router for a zoning-bylaw assistant. Classify the user's question and, "
    "for follow-ups, rewrite it into a standalone search query that resolves pronouns "
    "using the recent conversation. Reply with ONLY a JSON object, no prose.\n"
    'Schema: {"intent": one of '
    '["why_verification","specific_rule","definition","list_table","out_of_scope"], '
    '"standalone_query": string}\n'
    "Intent meanings:\n"
    "- why_verification: asks why a rule is in review / not verified / rejected, what is "
    "missing, what is the problem, or whether a rule passed.\n"
    "- specific_rule: asks for a specific number/limit in the bylaw (e.g. the minimum lot "
    "area, the maximum height).\n"
    "- definition: asks what a zoning term means.\n"
    "- list_table: asks to list/show many rules or wants a table.\n"
    "- out_of_scope: not about this zoning bylaw.\n"
)


def _extract_json_object(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"\{.*\}", str(text), re.DOTALL)
    if not match:
        return None
    try:
        obj = json.loads(match.group(0))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def reformulate_and_route(
    question: str,
    history: list[dict[str, Any]] | None = None,
    *,
    llm_call: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    """Route a question to an intent and rewrite follow-ups into a standalone query.

    ``llm_call`` (when provided) is any function that takes a prompt string and
    returns the model's raw text. We parse a small JSON object out of it. On a
    missing key, malformed output, or any error we fall back to the deterministic
    :func:`_keyword_route`, so the router always returns a usable result.
    """
    base = _keyword_route(question, history)
    if llm_call is None:
        return base

    convo = "\n".join(
        f"{turn.get('role')}: {str(turn.get('content') or '')[:240]}"
        for turn in (history or [])[-4:]
        if turn.get("role") in {"user", "assistant"}
    )
    prompt = f"{_ROUTER_PROMPT}\nRecent conversation:\n{convo or '(none)'}\n\nUser question: {question}\nJSON:"
    try:
        obj = _extract_json_object(llm_call(prompt))
    except Exception:
        obj = None
    if not obj:
        return base

    intent = str(obj.get("intent") or "").strip()
    if intent not in INTENTS:
        return base
    standalone = str(obj.get("standalone_query") or "").strip() or base["standalone_query"]
    return {
        "intent": intent,
        "standalone_query": standalone,
        # keep the deterministic family detection — it powers rule matching
        "families": base["families"] or _families_in(standalone),
        "confidence": 0.85,
        "method": "llm",
    }


# ---------------------------------------------------------------------------
# Rule reference detection
# ---------------------------------------------------------------------------

def status_of(rule: dict[str, Any]) -> str:
    """Canonical bucket for a rule: verified | in_review | rejected | not_used."""
    decision = str(rule.get("verification_decision") or "").strip().lower()
    vstatus = str(rule.get("verification_status") or "").strip().lower()
    if decision == "verified" or vstatus == "verified":
        return "verified"
    if decision == "rejected" or vstatus == "rejected":
        return "rejected"
    if decision == "not_used" or vstatus == "not_used":
        return "not_used"
    if decision == "review_needed" or vstatus in {"review_needed", "missing_scope"}:
        return "in_review"
    # Fall back to the gap catalogs (mirrors decision_policy ordering).
    gaps = set(rule.get("support_gaps") or []) - ADVISORY_GAPS
    if not gaps:
        return "verified"
    if CRITICAL_REJECTION_GAPS & gaps:
        return "rejected"
    if NOT_USED_GAPS & gaps:
        return "not_used"
    return "in_review"


def index_rules_by_id(*rule_lists: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for rules in rule_lists:
        for rule in rules or []:
            rid = str(rule.get("rule_id") or "").strip()
            if rid and rid not in out:
                out[rid] = rule
    return out


def detect_rule_reference(
    question: str,
    verified: list[dict[str, Any]],
    review: list[dict[str, Any]],
    *,
    prefer: str | None = None,
) -> dict[str, Any] | None:
    """Best-effort match of a question to a single rule.

    Scores each rule on explicit rule-id match, numeric value match, rule-family
    match, and direction (min/max) match. ``prefer`` ('in_review' or 'verified')
    breaks ties toward that bucket. Returns the matched rule (a copy annotated
    with ``_status``) or ``None`` when nothing scores above threshold.
    """
    low = str(question or "").lower()
    q_numbers = set(_numbers(question))
    q_families = set(_families_in(question))
    wants_max = any(t in low for t in ("max", "maximum", "no more than", "up to", "at most"))
    wants_min = any(t in low for t in ("min", "minimum", "at least", "no less than"))

    candidates: list[tuple[float, int, dict[str, Any]]] = []
    pools = [("verified", verified or []), ("in_review", review or [])]
    for status, rules in pools:
        for rule in rules:
            score = 0.0
            rid = str(rule.get("rule_id") or "").lower()
            if rid and rid in low:
                score += 6.0
            else:
                m = re.search(r"\brule\s*#?\s*(\d+)\b", low)
                if m and rid.endswith(m.group(1).zfill(3)):
                    score += 5.0
            rule_nums = set(_numbers(rule.get("value")))
            if rule_nums and rule_nums & q_numbers:
                score += 3.0
            family = str(rule.get("rule_object") or "")
            if family in q_families:
                score += 2.0
            direction = f"{rule.get('operator') or ''} {rule.get('constraint_type') or ''}".lower()
            is_max = any(t in direction for t in ("<=", "max"))
            is_min = any(t in direction for t in (">=", "min"))
            if (wants_max and is_max) or (wants_min and is_min):
                score += 1.0
            elif (wants_max and is_min) or (wants_min and is_max):
                score -= 0.5
            if score <= 0:
                continue
            prefer_bonus = 1 if (prefer and status == prefer) else 0
            candidates.append((score, prefer_bonus, {**rule, "_status": status}))

    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0] + 0.25 * item[1]), reverse=True)
    best_score, _, best = candidates[0]
    if best_score < 2.0:
        return None
    return best


# ---------------------------------------------------------------------------
# Verification explanation (the core "why didn't it pass" answer)
# ---------------------------------------------------------------------------

# What a human/better-evidence would need to supply to clear each blocking gap.
_GAP_NEEDS: dict[str, str] = {
    "value_not_found_in_evidence": "a cited source line that actually shows this number",
    "unit_not_found_in_evidence": "the unit (m, m², %, units) shown next to the number in the source",
    "rule_object_unit_not_compatible": "a unit that fits this rule family",
    "operator_not_supported": "wording that proves the direction — 'minimum', 'maximum', 'not less than', 'not more than'",
    "table_operator_refuted": "a source whose wording matches the claimed direction (the table reads the other way)",
    "rule_family_direction_mismatch": "confirmation of the direction — the value reads as the opposite of what this rule family usually sets",
    "applies_to_not_supported": "text that names what this applies to (which lot type or building)",
    "constraint_scope_not_supported": "text that names the scope (front, rear, or side yard, etc.)",
    "text_candidate_requires_review": "a second, clearer source — single weak text blocks are held by policy until they pass the full text-rule contract",
    "text_condition_not_supported": "the condition wording grounded in the cited text",
    "unresolved_exception_cue": "the 'except…' / override wording resolved",
    "enumerated_branch_condition_missing": "proof of which listed branch (e.g. side vs rear) this value belongs to",
    "range_bound_not_maximum": "the real maximum — this value is only one end of a range",
    "coefficient_operand_not_value": "the absolute cap — this number is a ratio multiplier, not a fixed limit",
    "applicability_not_grounded": "the dwelling-type / unit-count column this value sits under",
    "column_qualifier_not_claimed": "the column's qualifier (e.g. a transit-area condition) stated in the rule",
    "conditional_cell_condition_missing": "the cell's branch condition (e.g. by lot size) stated in the rule",
    "anchored_row_family_mismatch": "a source row that regulates this rule family",
    "column_value_mismatch": "the correct column — the claimed one holds a different value",
    "source_evidence_id_not_found": "a valid source citation (the current one is missing)",
}

# Friendlier wording for a few gap codes that proof_trace.human_reason renders as
# raw underscores (they live in decision_policy's sets but not in its LABELS map).
# We prefer these, then fall back to human_reason for everything else.
_GAP_WHY: dict[str, str] = {
    "rule_family_direction_mismatch": (
        "the direction looks off — this reads as a maximum where this rule family normally sets a "
        "minimum (or vice versa), so it's held until the direction is confirmed"
    ),
    "text_candidate_requires_review": (
        "it was read from a single line of text, and the checker only auto-confirms a rule when the "
        "wording clearly proves the number, its unit, and whether it's a minimum or a maximum — so a "
        "person should confirm it"
    ),
    "text_condition_not_supported": (
        "the cited text doesn't clearly prove an extra condition this rule depends on (for example an "
        "'except…' clause or a lot-size branch)"
    ),
    "table_fallback_candidate_requires_review": "it came from a table fallback that a person should confirm before it is trusted",
    "table_cell_candidate_requires_review": "it came straight from a table cell that a person should confirm (which column and condition it belongs to)",
    "table_evidence_candidate_requires_review": "the table evidence needs a person to confirm before it is trusted",
    "extraction_source_fidelity_hold": "the extraction step flagged that the quoted text may not match the real source page, so it is held until the citation is confirmed",
    "non_metric_unit_requires_review": "the rule is stated in non-metric units (e.g. feet); it is held for a person to review or convert rather than being silently compared to a metric limit",
}


def _gap_sentence(gap: str) -> str:
    """Plain-English reason for one gap: our override, else the verifier's own label."""
    if gap in _GAP_WHY:
        return _GAP_WHY[gap]
    return human_reason([gap])


_VERDICT_SENTENCE = {
    "verified": "This rule is verified — its value, unit, direction, and scope are all supported by the cited bylaw text.",
    "in_review": "This rule is held for review — it looks plausible, but the verifier could not yet prove every part of it from the cited text. It is not wrong, just unconfirmed.",
    "rejected": "This candidate was rejected — the cited evidence contradicts it or does not contain the stated value or unit.",
    "not_used": "This isn't treated as an enforceable rule for this product — for example it's a cross-reference or a definition, not a numeric limit.",
}


def _short(text: Any, limit: int = 220) -> str:
    s = re.sub(r"\s+", " ", str(text or "")).strip()
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def _source_block(rule: dict[str, Any], router_item: dict[str, Any] | None) -> dict[str, Any]:
    source = rule.get("source") or {}
    section = source.get("section") or source.get("source_section") or ""
    where = ""
    if router_item:
        where = str(router_item.get("where_to_find_it") or "")
    return {
        "page": source.get("page"),
        "section": str(section or "").strip(),
        "quote": _short(source.get("evidence_text") or source.get("evidence_quote") or "", 200),
        "document": source.get("document") or "",
        "url": source.get("url") or "",
        "where_hint": where,
    }


def _clean_next_step(text: str) -> str:
    """Strip reviewer-jargon tails (raw gap codes, evidence ids, semantic-match
    notes) so the citizen-facing next step stays plain English."""
    text = re.split(r"\s+Check\s+[a-z0-9_]", text, maxsplit=1)[0]
    text = re.split(r"\s*Semantic match", text, maxsplit=1)[0]
    text = re.sub(r"\s*evidence_id\s+\S+", "", text)
    return text.strip()


def verification_narrative_prompt(card: dict[str, Any], rule_sentence: str) -> str:
    """Prompt asking an LLM to explain a verification card in warm, plain language
    using ONLY the deterministic facts (so it never invents anything)."""
    wtl = card.get("where_to_look") or {}
    loc = []
    if wtl.get("section"):
        loc.append(f"section {wtl['section']}")
    if wtl.get("page") not in (None, ""):
        loc.append(f"page {wtl['page']}")
    where = ", ".join(loc) or "the source bylaw"
    facts = [f"Rule: {rule_sentence}", f"Status: {card.get('status')}"]
    if card.get("why"):
        facts.append("Why it is not auto-confirmed: " + "; ".join(card["why"]))
    if card.get("likely_missing"):
        facts.append("What would confirm it: " + card["likely_missing"])
    facts.append(f"Where to check in the bylaw: {where}")
    if wtl.get("quote"):
        facts.append('Cited text: "' + wtl["quote"] + '"')
    if (card.get("similar_verified") or {}).get("rule"):
        facts.append("A closely related rule IS already verified.")
    facts_block = "\n".join(f"- {f}" for f in facts)
    return (
        "Explain this zoning rule's status to a non-expert homeowner in 2-4 warm, plain sentences. "
        "Use ONLY the facts below — never invent numbers, reasons, or citations, and never output codes "
        "or field names. If it is verified, reassure them it is confirmed and say where it comes from. If "
        "it is in review, explain in everyday words why it is not auto-confirmed yet and what a person "
        "would check — make clear that being in review is normal and not an error.\n\n"
        f"FACTS:\n{facts_block}"
    )


def explain_verification(
    rule: dict[str, Any],
    *,
    router_item: dict[str, Any] | None = None,
    repair_suggestion: dict[str, Any] | None = None,
    similar_verified: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a plain-language verification card for one rule. Pure & deterministic.

    Every fact comes from the rule's own JSON: ``support_gaps`` →
    :func:`proof_trace.human_reason`, ``source`` → where-to-look, the repair
    suggestion → "look here instead", and the router's ``similar_verified_rule_id``
    → a verified companion. Nothing is invented.
    """
    status = rule.get("_status") or status_of(rule)
    gaps = list(rule.get("support_gaps") or [])
    blocking = [g for g in gaps if g not in ADVISORY_GAPS]
    advisory = [g for g in gaps if g in ADVISORY_GAPS]

    why = [_gap_sentence(gap) for gap in blocking]
    if advisory and not why:
        why = [_gap_sentence(gap) for gap in advisory]

    needs = []
    seen: set[str] = set()
    for gap in blocking:
        need = _GAP_NEEDS.get(gap)
        if need and need not in seen:
            seen.add(need)
            needs.append(need)
    likely_missing = "; ".join(needs)

    card: dict[str, Any] = {
        "rule_id": rule.get("rule_id"),
        "status": status,
        "verdict_sentence": _VERDICT_SENTENCE.get(status, _VERDICT_SENTENCE["in_review"]),
        "why": why,
        "likely_missing": likely_missing,
        "where_to_look": _source_block(rule, router_item),
        "support_gaps": gaps,
        "advisory_note": ADVISORY_NOTE,
        "repair_hint": None,
        "similar_verified": None,
        "next_step": "",
        "rule": rule,
    }

    if router_item:
        raw_next = (
            router_item.get("human_instruction")
            or router_item.get("next_step")
            or router_item.get("suggested_next_action")
            or ""
        )
        card["next_step"] = _short(_clean_next_step(raw_next), 220)

    if repair_suggestion:
        top = (repair_suggestion.get("top_evidence") or [])
        if top:
            best = top[0]
            card["repair_hint"] = {
                "quote": _short(best.get("evidence_quote") or "", 200),
                "page": best.get("page"),
                "confidence": best.get("repair_confidence"),
            }

    if similar_verified:
        card["similar_verified"] = {
            "rule_id": similar_verified.get("rule_id"),
            "rule": similar_verified,
        }

    return card


# ---------------------------------------------------------------------------
# Retrievable rule corpus (so "why is X in review" can find the right rule)
# ---------------------------------------------------------------------------

def rule_corpus_text(rule: dict[str, Any]) -> str:
    """Searchable text for one rule chunk: family, scope, value, and the quote."""
    source = rule.get("source") or {}
    parts = [
        str(rule.get("rule_object") or "").replace("_", " "),
        str(rule.get("constraint_type") or ""),
        str(rule.get("constraint_scope") or "").replace("_", " "),
        str(rule.get("applies_to") or ""),
        str(rule.get("condition") or ""),
        f"{rule.get('value') or ''} {rule.get('unit') or ''}".strip(),
        str(rule.get("verification_status") or ""),
        str(source.get("evidence_text") or ""),
    ]
    return " ".join(p for p in parts if p).strip()


def build_rule_corpus(
    verified: list[dict[str, Any]],
    review: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """One retrievable chunk per rule (verified + review).

    Each chunk mirrors the bylaw-section chunk shape (chunk_id/section/page/text)
    so it can be indexed by the same ``BylawIndex``, and carries ``rule_ref`` so
    answer builders never have to re-look-up the rule by id.
    """
    corpus: list[dict[str, Any]] = []
    for status, rules in (("verified", verified or []), ("in_review", review or [])):
        for rule in rules:
            source = rule.get("source") or {}
            corpus.append(
                {
                    "chunk_id": str(rule.get("rule_id") or ""),
                    "section": str(source.get("section") or source.get("source_section") or ""),
                    "page": source.get("page"),
                    "text": rule_corpus_text(rule),
                    "source_kind": "rule",
                    "status": status,
                    "rule_ref": {**rule, "_status": status},
                }
            )
    return corpus


def build_rule_index(corpus: list[dict[str, Any]], embedding_backend: Any | None = None):
    """Wrap the rule corpus in a ``BylawIndex`` (BM25 + optional dense + RRF).

    Absolute, lazily-imported so this file stays a single portable module: when
    the package is absent (cloud deploy) the import raises and callers fall back
    to ``detect_rule_reference`` (which needs no index)."""
    from burnaby_prototype.bylaw_rag import BylawIndex

    return BylawIndex(corpus, embedding_backend=embedding_backend)


# ---------------------------------------------------------------------------
# Tables for embedding in answers
# ---------------------------------------------------------------------------

_HEADER_NOISE = {"dwelling", "type", "minimum", "maximum", "the", "of", "and", "or"}


def _column_label(header_text: str) -> str:
    """Turn a pipe-delimited band header path into a compact column label."""
    raw = str(header_text or "").replace("\n", " ")
    segments = [seg.strip() for seg in raw.split("|") if seg.strip()]
    if not segments:
        return raw.strip()
    # Drop a leading generic segment like "Dwelling Type" when more specific ones exist.
    if len(segments) > 1 and segments[0].lower() in {"dwelling type"}:
        segments = segments[1:]
    label = " ".join(segments)
    return re.sub(r"\s+", " ", label).strip()


def reconstruct_dimensional_tables(
    evidence_units: list[dict[str, Any]],
    *,
    row_filter: Callable[[str], bool] | None = None,
    max_tables: int = 4,
) -> list[dict[str, Any]]:
    """Rebuild original dimensional bylaw tables from ``matrix_anchor`` geometry.

    Each anchored evidence unit is ONE table row (its ``row_label``) whose bands
    are the columns. Units that share the same column signature (and page) belong
    to the same table. Returns table payloads ready for ``st.dataframe``.
    """
    groups: dict[tuple, dict[str, Any]] = {}
    order: list[tuple] = []
    for unit in evidence_units or []:
        anchor = unit.get("matrix_anchor")
        if not isinstance(anchor, dict):
            continue
        row_label = str(anchor.get("row_label") or "").strip()
        if not row_label:
            continue
        if row_filter and not row_filter(row_label):
            continue
        bands = anchor.get("bands") or []
        columns = [_column_label(band.get("header_text") or f"Column {i + 1}") for i, band in enumerate(bands)]
        if not columns:
            continue
        key = (anchor.get("page"), tuple(columns))
        if key not in groups:
            groups[key] = {"page": anchor.get("page"), "columns": columns, "rows": [], "_seen_rows": set()}
            order.append(key)
        group = groups[key]
        if row_label in group["_seen_rows"]:
            continue
        group["_seen_rows"].add(row_label)
        cells = {col: "" for col in columns}
        for col, band in zip(columns, bands):
            cells[col] = _short(band.get("text") or band.get("cell_text") or "", 60)
        group["rows"].append({"row_label": row_label, "cells": cells})

    tables: list[dict[str, Any]] = []
    for key in order[:max_tables]:
        group = groups[key]
        if not group["rows"]:
            continue
        tables.append(
            {
                "kind": "dimensional",
                "page": group["page"],
                "title": f"Dimensional table (p.{group['page']})" if group["page"] else "Dimensional table",
                "columns": ["Regulation", *group["columns"]],
                "rows": [
                    {"Regulation": row["row_label"], **row["cells"]}
                    for row in group["rows"]
                ],
            }
        )
    return tables


def rule_list_table(rules: list[dict[str, Any]], *, limit: int = 60) -> dict[str, Any]:
    """A flat tabular view of a set of rules — for 'list/show all' answers."""
    rows: list[dict[str, str]] = []
    for rule in (rules or [])[:limit]:
        source = rule.get("source") or {}
        direction = f"{rule.get('operator') or ''} {rule.get('constraint_type') or ''}".lower()
        if any(t in direction for t in ("<=", "max")):
            arrow = "≤ (max)"
        elif any(t in direction for t in (">=", "min")):
            arrow = "≥ (min)"
        else:
            arrow = str(rule.get("operator") or "").strip()
        value = f"{rule.get('value') or ''} {rule.get('unit') or ''}".strip()
        section = source.get("section") or source.get("source_section") or ""
        where = f"§{section}" if section else ""
        if source.get("page") not in (None, ""):
            where = (where + f" p.{source.get('page')}").strip()
        rows.append(
            {
                "Rule": str(rule.get("rule_object") or "").replace("_", " "),
                "Limit": f"{arrow} {value}".strip(),
                "Applies to": str(rule.get("applies_to") or "").strip(),
                "Status": (rule.get("_status") or status_of(rule)).replace("_", " "),
                "Source": where,
            }
        )
    return {
        "kind": "rule_list",
        "title": f"{len(rows)} rule{'s' if len(rows) != 1 else ''}",
        "columns": ["Rule", "Limit", "Applies to", "Status", "Source"],
        "rows": rows,
    }
