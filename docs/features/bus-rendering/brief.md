---
feature: bus-rendering
date: 2026-03-08
commit: 9b4bb7b
branch: main
status: problem-space
read-when: "after infrastructure-dsl lands"
---

## Problem

The renderer has zero coverage of `ae_data.bus`. Bus display names, colors, faders, and dynamics all pass through from the base template unchanged. This means 8 of 12 active buses render with wrong names (operators see "BASS" instead of "Rhythm/House", "Lead/House" instead of "Vocals", etc.). Bus dynamics (SBUS compressors on submix buses) and colors are also unmanaged.

## Not Doing

- Bus *send* rendering (channel sends to buses are already handled by the channel pipeline)
- Bus tags (handled by `tags-ownership` feature)
- Matrix bus rendering (handled by `personal-mixer-routing` feature)
- Bus EQ (not currently used on any submix bus in reference snapshots)

## Constraints

- Bus config is split between infrastructure (shared bus names/colors/dynamics) and assembly (team-specific overrides like bus 12 name)
- The infrastructure layer defines all 16 buses; assembly `buses:` section can override `name` for team-specific buses
- Display names are explicit in the DSL — no automatic derivation from logical names
- Renderer writes `name`, `col`, `fdr`, `mute`, and dynamics config to `ae_data.bus[N]`
- Depends on `infrastructure-dsl` being complete (Init.snap as base template)
- TDD — bus rendering is a new renderer section with its own test coverage

## Escalation Triggers

- If bus dynamics config (SBUS model params) requires new Pydantic schema beyond what exists for channel dynamics, pause — reuse vs new models decision
- If the assembly bus override mechanism feels awkward for the "bus 12 varies by team" case, pause — DSL shape question

## Decisions

(populated during implementation)
