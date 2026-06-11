# Verification Dashboard

The dashboard is a reader for verifier outputs. It does not call an LLM, change
decisions, or promote rules.

Run from the project root:

```bash
.venv/bin/python -m streamlit run dashboard/streamlit_app.py --server.port 8502
```

Default output folder:

```text
outputs/burnaby_r1_slim_pipeline5_registry/
```

## v2

- **City selector** — the sidebar lists every `outputs/*_slim_pipeline5_registry/`
  dir that contains `verified_rules.json` (default `burnaby_r1`). New cities
  (e.g. Calgary) appear automatically once their outputs exist; nothing is
  hardcoded. All loads are city-aware.
- **Sections** — the former flat tab strip is grouped into six top-level
  sections (every original tab is preserved inside one of them):
  `Overview` / `Rules` (Candidate vs Verified, Rule Graph) / `Review` (Review,
  Review Resolution, Semantic Review) / `Evidence & Proof` (Evidence
  Intelligence, Evidence Repair, Evidence Rerun, Bundle Rerun, Bylaw) /
  `GIS & Map` (Map, 3D Envelope, Felt Export) / `System` (Safe Tuning,
  Verification Structure, Extraction Preflight).
- **Map tab** — a pydeck deck centered on the selected city showing a
  representative 30 m x 40 m **demo lot** (not a real parcel) with verified
  setback bands, the buildable footprint extruded to the max verified height,
  and tooltips carrying parameter, value, operator, rule id, and evidence
  quote. Requires the optional extra: `pip install -e .[map]`; without pydeck
  the tab shows an install hint instead.
- **Bylaw tab** — renders extracted bylaw sections from
  `data/bylaws/<city>/` when present, with a rule picker that `<mark>`s the
  picked rule's cited evidence inside the section. Falls back to the
  evidence-units view when no extraction exists yet.
- **3D envelope** — `scripts/build_envelope_3d.py` writes
  `outputs/<city>.../envelope_3d.html` (self-contained Three.js + OrbitControls
  from CDN) from `buildable_envelope.json`; the dashboard embeds it when the
  file exists and always shows a printable SVG plan-view fallback with setback
  arrows, values, and rule ids.
- **Color semantics (strict, everywhere)** — verified `#1a7f37` (green),
  review `#9a6700` (amber), rejected `#cf222e` (red), not_used `#57606a`
  (grey).

The dashboard still runs with only the base dependency (`streamlit`); pydeck
and the Three.js artifact degrade gracefully with informative messages.

## How To Read It

```text
verified
```

Safe, source-supported rules. These are the only rules that should drive GIS.

```text
review_needed
```

Possibly useful rules that need clearer evidence, scope, condition, or legal
review.

```text
rejected
```

Unsafe or contradicted candidates.

```text
not_used
```

Traceability-only or out-of-contract candidates, such as cross-references and
administrative rules.

## Main Pages

```text
Overview
```

Counts, quality gates, review categories, and benchmark results.

```text
Review
```

Single reviewer-facing queue from `review_router.json`. It combines priority,
likely status, action bucket, decision path, plain-English rule/evidence
sentences, and human next step.

```text
Candidate vs Verified
```

Side-by-side sentence view: what a review candidate claims versus the nearest
verified rule.

```text
Evidence Repair
```

Possible stronger evidence snippets. These suggestions are advisory only.

```text
GIS/Felt Export
```

Verified-only GIS contract and map-friendly export preview.

```text
Verification Structure
```

File and layer map explaining how the verifier is organized.

## Guardrail

The dashboard explains decisions. It does not make decisions.
