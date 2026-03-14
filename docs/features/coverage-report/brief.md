---
feature: coverage-report
date: 2026-03-12
commit: 6e48f10
branch: main
status: compacting
read-when: "starting implementation"
---

## Problem

There is no way to quickly see which Wing snapshot sections the renderer owns vs.
which pass through from Init.snap unchanged. As the project grows, gaps get forgotten
or rediscovered accidentally. A deterministically generated coverage report would serve
as a living record of renderer scope — usable by LLM agents without reading the
renderer source, and as input to a summary pass that explains which gaps are worth closing.

## Not Doing

- Coverage tracking at the individual-parameter level — section-level granularity is enough
- Integration into CI — this is an on-demand tool, not a gate
- Human-maintained classification of pass-through vs gap — that distinction is an LLM
  synthesis task driven by the JSON report, not hand-edited data

## Constraints

### CLI: `snapwright coverage [assembly]`

- Accepts an optional assembly path; defaults to `data/dsl/teams/james/assembly.yaml`
- Renders Init.snap + infrastructure.yaml + the given assembly, diffs the result against
  Init.snap at section granularity, writes `docs/coverage-report.json`, and prints a
  summary table to stdout
- `rendered` status is derived purely from the diff — any section that differs between
  Init.snap and the rendered output is `rendered`; no hardcoding of section names
- Section granularity: top-level ae_data/ce_data keys, plus named sub-sections where
  behavior differs within a key (e.g. `ae_data.cfg.rta`, `ae_data.io.in.A` are separate
  rows; `ae_data.io.out.A` is split by slot range matching actual renderer behavior)
- JSON schema: `{ generated_at, rendered_from, sections: [{ path, rendered, changed_keys }] }`
  — `changed_keys` lists the top-level keys that diffed within each section, giving the
  downstream LLM context about what specifically changed
- Stdout summary: a plain table of every section with `rendered` / `not rendered` —
  human-readable spot check without opening the JSON

### Pi prompt: `snapwright-coverage-summary`

- Lives at `docs/prompts/snapwright-coverage-summary.md`
- Accepts `docs/coverage-report.json` as primary input
- Reads `docs/features/*/brief.md` to understand why each feature exists and what it owns
- Produces an updated `docs/coverage.md` covering the not-rendered set: what each section
  is, whether its exclusion is intentional, and what would be gained by rendering it
- `docs/coverage.md` is LLM-generated output — not maintained by hand, not read by the CLI

## Escalation Triggers

- If section granularity for a key is ambiguous (e.g. should a sub-section be split
  further or kept as one row), pause — needs a user decision before the schema is finalized
- If the diff reveals unexpected sections as `rendered` or `not rendered` relative to
  the coverage doc written during solution-space, surface them — they may indicate a
  renderer bug or a missing feature

## Decisions

(populated during implementation)
