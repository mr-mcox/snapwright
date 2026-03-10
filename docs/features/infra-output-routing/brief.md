---
feature: infra-output-routing
date: 2026-03-09
commit: dfce014
branch: infrastructure-dsl
status: compacting
read-when: starting implementation of physical output routing in infrastructure
---

## Problem

`infrastructure.yaml` has no `io.out` section, so the physical output patch
(which stage-box/local/USB/AUX outputs carry house, stream, and monitor
signals) exists only in manually-saved snapshots. A render from Init.snap
produces wrong output routing — nothing reaches the PA or stream. This is
the most operationally consequential gap in the infrastructure DSL. Keeping
output routing expressed at the `mains:` and `buses:` level (not a separate
patch-bay section) is also the right abstraction layer — it stays consistent
with how the DSL will evolve and mirrors how `inputs:` lives alongside
other concerns in assembly.yaml.

## Not Doing

- Stage-box outputs A.33-A.48 (P16 personal mixer block) — handled by the
  personal-mixer-dsl feature; left absent here intentionally
- `io.in` (stage-box input labels, preamp gains) — team-specific, belongs
  in assembly DSL
- `aux` channel EQ tuning (aux.1 has operator-set EQ freqs) — team-specific
- `mtx` names, icons, faders — team-specific; covered by personal-mixer-dsl

## Constraints

- Output connection fields (`out.conn: grp/in`) live inline within `mains:`
  and `buses:` entries, parallel to how `in.conn` already works on input
  channels — no separate `io.out` section; Wing-native field names (grp, in)
  used directly since routing values are set-once wiring decisions, not
  operator-tuned parameters
- Firmware Q patches extended to cover `mtx` and `aux` in
  `apply_firmware_patches` — same pattern as buses/mains
- `aux` structural defaults (all `main.1.on: false`, send modes POST for
  buses 1-12, PRE for 13-16) belong in infrastructure, not team assembly
- `aux.1.name: "USB 1/2"` is a hardware label — infrastructure
- Diff harness masks output conn fields within mains/buses for A.33-A.48
  (personal mixer outputs, not yet expressed)

## Escalation Triggers

- If any `io.out` entry differs between james and priscilla team snaps,
  pause — it may be team-specific rather than house infrastructure
- If `aux` send mode defaults conflict with how the channel renderer sets
  send modes for regular channels, pause — consistency matters

## Decisions

_(populated during Phase 3)_
