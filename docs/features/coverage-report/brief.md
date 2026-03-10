---
feature: coverage-report
date: 2026-03-09
commit: 6e48f10
branch: main
status: solution-space
read-when: "starting implementation"
---

## Problem

There is no way to quickly see which Wing snapshot sections the renderer owns, which
pass through from Init.snap, and which are known gaps with a documented reason.
As the project grows, intentional gaps (user layers, center/left surface) get forgotten
or rediscovered accidentally. A generated coverage view paired with a rationale doc
would serve as a living record of scope decisions and a discovery tool for future work.

## Not Doing

- Coverage tracking at the individual-parameter level — section-level granularity is enough
- Auto-generating the "why" rationale — that stays human-maintained
- Integration into CI — this is an on-demand tool, not a gate

## Constraints

- CLI: `snapwright coverage` emits a markdown or text table to stdout
- Three statuses per section: `rendered` (renderer writes it), `pass-through` (Init.snap values, intentional), `gap` (not rendered, reason in companion doc)
- Companion doc lives at `docs/coverage.md` — maintained by hand, updated as scope evolves
- The CLI derives its section list from the known Wing snapshot structure (ae_data.*, ce_data.*), not from the companion doc
- The companion doc explains *why* for each non-rendered section — the CLI provides the *what*

## Escalation Triggers

- If the boundary between "pass-through" and "gap" is ambiguous for a section, pause — needs a user decision on intent
- If the section list in the CLI diverges significantly from the actual snapshot structure, pause — the Wing structure reference may need updating

## Decisions

(populated during implementation)
