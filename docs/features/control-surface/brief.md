---
feature: control-surface
date: 2026-03-09
commit: 6e48f10
branch: main
status: solution-space
read-when: "starting implementation"
---

## Problem

The rendered snapshot has no custom control surface configuration (`ce_data.layer`,
`ce_data.user`). Volunteers are trained to use a specific custom control layout —
particularly the "send on fader" flip for monitor adjustments. Without it, they
have no tool for their trained workflow and cannot manage monitors independently.
The right-surface User 1 layer is also absent.

## Not Doing

- Center and left surface user layers — not yet modeled, post-beta
- Full programmatic generation of the layout — the control surface config is static
  infrastructure, not derived from the assembly
- Strategy-based layout switching (beginner/advanced views) — deferred to `strategy-overlays`

## Constraints

- The control surface layout (`ce_data.layer`, `ce_data.user`) is infrastructure-level:
  it is the same for all teams and belongs in infrastructure rather than the assembly
- Implementation approach: carry the reference layout (from James.snap or a designated
  reference) into infrastructure.yaml as a verbatim block — do not attempt to model
  or regenerate the layout from first principles
- The existing reference snapshot is the source of truth; no layout redesign in this feature
- Renderer writes `ce_data.layer` and `ce_data.user` from infrastructure

## Escalation Triggers

- If the reference control surface layout contains team-specific assignments that should
  vary per assembly, pause — this changes the scope from pure infrastructure to a hybrid
- If the infrastructure.yaml verbatim block approach causes schema or loader friction, pause

## Decisions

(populated during implementation)
