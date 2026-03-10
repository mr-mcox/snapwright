---
feature: stream-output-routing
date: 2026-03-09
commit: 6e48f10
branch: main
status: solution-space
read-when: "starting implementation"
---

## Problem

The rendered snapshot has no routing configured for `io.out.AUX` or `io.out.USB`.
Streaming and recording outputs are dead on load. The reference James.snap has
these routed to specific buses; the Init.snap defaults leave them unassigned.

## Not Doing

- `io.out.LCL` — local outputs intentionally left to Init defaults (no Sunday impact)
- `io.out.B`, `io.out.CRD` — not used in current rig

## Constraints

- Stream output routing (which bus feeds AUX out, which bus feeds USB) is infrastructure-level — same for all teams, defined in `infrastructure.yaml`
- The reference James.snap is the source of truth for what the correct routing should be
- Renderer writes `io.out.AUX` and `io.out.USB` routing from infrastructure
- Related `ae_data.aux` config (aux channel names, colors, send modes) is in scope if needed to make stream outputs functional on load
- TDD

## Escalation Triggers

- If the correct stream bus assignments differ between teams, pause — this would move from infrastructure to assembly scope
- If `ae_data.aux` requires significant new schema work beyond the diff, pause — scope question

## Decisions

(populated during implementation)
