---
feature: infrastructure-dsl
date: 2026-03-08
commit: b8e5feb
branch: main
status: solution-space
read-when: "starting implementation of Init.snap + infrastructure.yaml rendering foundation"
---

## Problem

The rendering pipeline uses Base.snap as its foundation — an opaque binary with accumulated debris (phantom faders, stale labels, mystery config). There's no way to audit what's intentional vs accidental, and no way to evolve infrastructure without manually editing a binary. The fix is Init.snap (factory reset) + infrastructure.yaml (every intentional change from factory, documented with purpose), replacing Base.snap entirely as the rendering foundation.

## Not Doing

- Full coverage of every Init→Base diff on day one; unmodeled sections pass through from Init (correct by definition)
- Strategy overlays or complexity levels (separate feature)
- Team-specific assembly changes (infrastructure only)
- ce_data.user layers (separate feature)

## Constraints

- Init.snap (`data/reference/Init.snap`, schema v11) is the rendering foundation — never modified
- Infrastructure YAML lives at `data/dsl/infrastructure.yaml`; single file to start
- Every value in infrastructure.yaml must be self-documenting — no unexplained parameters
- `#M8` tags are NOT set in infrastructure.yaml — renderer owns all tag assignment
- Infrastructure.yaml explicitly omits: `#M8` pre-tags on ch1–24 (debris), JEN label on io.in.A.7 (debris), +0.5 dB gain on io.in.A.8–A.30 (debris)
- The existing channel pipeline (`_render()` for ae_data.ch) must continue to work — infrastructure is additive
- Existing 148 tests must continue to pass after switching from Base.snap to Init.snap
- New infrastructure rendering code gets TDD from day one

## Escalation Triggers

- If switching from Base.snap to Init.snap breaks more than 5 existing tests, pause — the remaining value-level schema differences (send modes, main.1.on, ptap) may need a targeted patch strategy
- If the infrastructure YAML exceeds ~200 lines, pause — may need to split into sections or reconsider granularity
- If modeling a section requires significant new Pydantic schema beyond simple key→value, pause — worth checking if that section should be a separate feature
- If any Init.snap field needed by existing renderer code is absent or behaves differently than Base.snap, pause

## Decisions

(populated during implementation)
