---
feature: stage-box-labels
date: 2026-03-09
commit: 6e48f10
branch: main
status: implementing
read-when: "starting implementation"
---

## Problem

The Wing displays the stage box input label (`io.in.A[N].name`) on the physical fader
strip — not `ae_data.ch.name`. Because the renderer never writes `io.in.A`, every
channel strip shows blank on the console. Preamp gains (`io.in.A[N].g`) also render
as 0 dB across all 32 slots, meaning all inputs arrive at the wrong level regardless
of what's dialed into channel processing.

## Not Doing

- Slots A.33–A.48 (personal mixer outputs — owned by `personal-mixer-routing`)
- Stage box B inputs (not used in current assembly)
- Local (`LCL`) or Aux (`AUX`) input labeling — deferred

## Constraints

- `preamp_gain: float | None` is added to `InstrumentLayer` and `MusicianEntry` — it is a property of the musician/instrument, not the slot assignment; `InputAssignment` stays as `source` + `input` only
- Name and icon for `io.in.A[N]` are derived from the musician's `name` and `icon` fields — no separate declaration
- Renderer writes `name`, `icon`, `g` to `io.in.A[slot]` for each musician in the assembly's `inputs:` map
- Slots not in the assembly keep Init.snap defaults (blank name, 0 gain) — no fabrication
- TDD — slot label and gain writing are pure functions of the assembled musician map
- The integration diff test must be widened to include `io.in.A` slots covered by the assembly — a passing diff against the James reference is the acceptance criterion for correctness

## Escalation Triggers

- If a musician has no icon set and the reference has a non-zero icon for that slot, pause — should icon default to 0 or be required?
- If the `preamp_gain` field name conflicts with existing DSL terminology, pause — naming matters here

## Decisions

(populated during implementation)
