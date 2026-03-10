---
feature: personal-mixer-dsl
date: 2026-03-09
commit: dfce014
branch: infrastructure-dsl
status: solution-space
read-when: starting implementation of P16 personal mixer abstraction
---

## Problem

The Behringer P16 personal mixer uses the last 16 stage-box outputs (A.33-A.48),
currently configured manually on the console — not expressed in the DSL at all.
Each slot carries either a group submix (multiple musicians blended → Wing matrix),
a single musician tap (→ Wing user source), or a monitor bus feed. The DSL should
let infrastructure declare the slot topology once and let each team assembly
populate who feeds what, hiding the matrix/USR/io.out mechanics entirely.

## Not Doing

- Per-slot level mixing within the P16 itself (that's the hardware unit's job)
- Changing the physical slot→output assignment at assembly time (fixed in infra)
- MX1-MX8 Wing send keys — these are a parallel personal monitor path; evaluate
  relationship to P16 slots before touching them (may be the same signal or not)

## Constraints

- Infrastructure declares slot topology: label, type (group/individual/monitor),
  and for monitor type: which logical bus (e.g. monitor_1)
- Infrastructure ordering determines matrix/USR slot allocation — slot 1 gets
  matrix 1, slot 2 gets matrix 2, etc. No explicit numbering in the YAML
- Assembly populates groups (same shape as existing `monitors` section: musician
  → level dict) and individuals (musician name only)
- Renderer creates matrices and USR sources dynamically; patches io.out A.33-A.48
- USR sources default to PRE-fader tap; tap point is a slot-level override if
  Wing supports post-mute/pre-fader (see escalation trigger)
- Translation layer for personal mixer lives in infrastructure.py and renderer.py
  respectively — infrastructure.yaml and assembly.yaml stay pure data files

## Escalation Triggers

- Before implementing USR tap points: verify on the Wing whether a post-mute /
  pre-fader tap point exists. If not, surface the tradeoff (stable P16 level vs.
  mutes follow FOH) and let the user decide the default
- If the MX1-MX8 send keys turn out to be the same physical signal path as
  P16 slots (not a parallel path), pause — the send model may need rethinking
- If matrix slot allocation by order produces a number conflict with matrices
  already used for other purposes, pause — may need explicit numbering after all

## Decisions

_(populated during Phase 3)_
