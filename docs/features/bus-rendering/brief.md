---
feature: bus-rendering
date: 2026-03-08
commit: 6e48f10
branch: main
status: solution-space
read-when: "starting implementation — infrastructure-dsl is done, all dependencies satisfied"
---

## Problem

Every bus and main output fader renders at -144 dB (Init default = fully off). Loading
this snapshot on Sunday produces total silence. Bus display names, colors, and dynamics
are also unmanaged — operators see "BASS" instead of "Rhythm/House", etc. All of this
passes through from Init.snap unchanged.

## Not Doing

- Bus *send* rendering (channel sends to buses are already handled by the channel pipeline)
- Bus tags (handled by `tags-ownership` feature)
- Matrix bus rendering (handled by `personal-mixer-routing` feature)
- Bus EQ (not currently used on any submix bus in reference snapshots)
- Assembly-level bus overrides (e.g. bus 12 name per team) — deferred until post-beta

## Constraints

- Infrastructure layer defines all 16 buses (name, col, fdr, mute, dynamics) and mains 1-3 (fdr)
- Bus fader defaults: ~0 dB for active mix buses; Init -144 preserved only for explicitly unused buses
- Main fader defaults: reasonable operational starting point (not -144, not necessarily reference values)
- Display names are explicit in the DSL — no automatic derivation from logical names
- Renderer writes `name`, `col`, `fdr`, `mute`, and dynamics to `ae_data.bus[N]`; `fdr` to `ae_data.main[N]`
- TDD — bus and main fader rendering are new renderer sections with their own test coverage

## Escalation Triggers

- If bus dynamics config (SBUS model params) requires new Pydantic schema beyond what exists for channel dynamics, pause — reuse vs new models decision
- If main output fader defaults conflict with what the sound engineer expects on load, pause — operational defaults are a user decision

## Decisions

(populated during implementation)
