---
feature: infra-output-routing
date: 2026-03-09
commit: dfce014
branch: infrastructure-dsl
status: solution-space
read-when: starting implementation of physical output routing in infrastructure
---

## Problem

`infrastructure.yaml` has no `io.out` section, so the physical output patch
(which stage-box/local/USB/AUX outputs carry house, stream, and monitor
signals) exists only in manually-saved snapshots. A render from Init.snap
produces wrong output routing — nothing reaches the PA or stream. This is
the most operationally consequential gap in the infrastructure DSL.

## Not Doing

- Stage-box outputs A.33-A.48 (P16 personal mixer block) — handled by the
  personal-mixer-dsl feature; left absent here intentionally
- `io.in` (stage-box input labels, preamp gains) — team-specific, belongs
  in assembly DSL
- `aux` channel EQ tuning (aux.1 has operator-set EQ freqs) — team-specific
- `mtx` names, icons, faders — team-specific; covered by personal-mixer-dsl

## Constraints

- `io.out` entries in infrastructure.yaml use Wing-native field names
  (grp, in) — no DSL translation layer needed; routing values aren't
  operator-tuned, they're set-once wiring decisions
- Firmware Q patches extended to cover `mtx` and `aux` in
  `apply_firmware_patches` — same pattern as buses/mains
- `aux` structural defaults (all `main.1.on: false`, send modes POST for
  buses 1-12, PRE for 13-16) belong in infrastructure, not team assembly
- `aux.1.name: "USB 1/2"` is a hardware label — infrastructure
- Diff harness gains an `io` section; `io.in` entirely masked (team content),
  A.33-A.48 masked (personal mixer, not yet expressed)

## Escalation Triggers

- If any `io.out` entry differs between james and priscilla team snaps,
  pause — it may be team-specific rather than house infrastructure
- If `aux` send mode defaults conflict with how the channel renderer sets
  send modes for regular channels, pause — consistency matters

## Decisions

_(populated during Phase 3)_
