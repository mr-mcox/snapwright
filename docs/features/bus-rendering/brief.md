---
feature: bus-rendering
date: 2026-03-08
commit: 6e48f10
branch: main
status: compacting
read-when: "starting implementation — infrastructure-dsl is done, all dependencies satisfied"
---

## Problem

Every bus and main output fader renders at -144 dB (Init default = fully off). Loading
this snapshot on Sunday produces total silence. (Bus names, colors, and dynamics are
already handled by the infrastructure renderer from the infra-dsl feature.)

## Not Doing
- Bus *send* rendering (channel sends to buses are already handled by the channel pipeline)
- Bus tags (handled by `tags-ownership` feature)
- Matrix bus rendering (handled by `personal-mixer-routing` feature)
- Bus EQ (not currently used on any submix bus in reference snapshots)
- Assembly-level bus overrides (e.g. bus 12 name per team) — deferred until post-beta

## Constraints

- Renderer change is minimal: add `fdr` and `mute` to `_BUS_FIELD_MAP` in `infrastructure.py` — the existing pass-through loop already handles both buses and mains
- YAML: add `fdr` values for active buses 1–7 and FX return buses 9–12, and mains 1–2; monitor buses 13–16 keep Init default (-144, session-adjusted)
- Integration diff test (`test_phase1_render.py`) widened to cover `ae_data.bus` and `ae_data.main` — a passing diff against the James reference is the acceptance criterion
- TDD — unit tests in `test_infrastructure.py` (following existing `TestInfrastructureBuses` / `TestInfrastructureMain` pattern) cover bus faders and main faders before implementation

## Escalation Triggers

- If main output fader defaults conflict with what the sound engineer expects on load, pause — operational defaults are a user decision

## Decisions
(populated during implementation)
