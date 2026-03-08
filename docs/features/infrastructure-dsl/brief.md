---
feature: infrastructure-dsl
date: 2026-03-08
commit: 9b4bb7b
branch: main
status: problem-space
read-when: "starting or resuming the infrastructure layer design"
---

## Problem

The rendering pipeline currently uses Base.snap (an opaque binary with accumulated debris) as its foundation. Every rendered snapshot silently inherits wrong bus names, phantom DCA faders, broken mute group memberships, stale channel labels, and mystery configuration from Base.snap. There's no way to audit what's intentional vs accidental, and no way to evolve infrastructure components (monitor config, headset EQ, personal mixer routing) without manually editing a binary file on the Wing.

The fix is a two-layer DSL: Init.snap (factory reset, the one opaque binary) + infrastructure.yaml (every change from factory documented with purpose). The renderer switches from `snap_template()` loading Base.snap to loading Init.snap and applying the infrastructure layer.

## Not Doing

- Full coverage of every Init→Base diff on day one. Start with sections we actively need; unmodeled sections pass through from Init (correct by definition)
- Strategy overlays or complexity levels (separate feature)
- Team-specific assembly changes (this is infrastructure only)
- ce_data.user layers (separate feature)
- Console preference tuning (ce_data.cfg) — include the known preferences from Investigation A but don't exhaustively model every option

## Constraints

- Init.snap (`data/reference/Init.snap`, Wing Edit 3.3.1) is the rendering foundation — never modified
- Infrastructure YAML lives at `data/dsl/infrastructure.yaml` (single file to start; can split later if it grows)
- Every value in infrastructure.yaml must have a comment or be self-documenting — no unexplained parameters
- Investigation A is the primary reference for what to include (intentional infrastructure + active configuration categories)
- The renderer's existing channel pipeline (`_render()` for ae_data.ch) must continue to work — infrastructure is additive
- Existing tests (73) must continue to pass after switching from Base.snap to Init.snap + infrastructure
- New infrastructure rendering code gets TDD from day one

## Escalation Triggers

- If switching from Base.snap to Init.snap breaks more than 5 existing tests, pause — the schema differences may need a migration strategy
- If the infrastructure YAML format gets beyond ~200 lines, pause — may need to split into sections or reconsider granularity
- If modeling a particular section (e.g., FX slots, bus dynamics) requires significant new Pydantic schema, pause — worth checking if that section should be a separate feature
- If Init.snap is missing fields that Base.snap has (firmware schema gaps), pause — need to decide whether to patch Init or skip those fields

## Decisions

(populated during implementation)
