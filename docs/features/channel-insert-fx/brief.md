---
feature: channel-insert-fx
date: 2026-03-12
commit: 7c801d5
branch: main
status: solution-space
read-when: "starting implementation"
---

## Problem

FX slots 10, 11, and 13 are assigned as pre-inserts on Handheld, Headset, and house main
respectively, but the slots have no model parameters — they load empty. The deessers are
permanent infrastructure-level processing for those mic types; without them, both vocal
channels load with sibilance uncontrolled. FX13 is a placeholder for future room-tuning GEQ;
without it the house main has no insert in the slot that is already assigned. Additionally,
ch39 (Computer) loads with a blank input-patch label because `io.in.LCL.4.name` is never
written — cosmetic, but the only labeled-but-blank slot on the console.

## Not Doing

- GEQ room calibration — FX13 is a near-flat placeholder pending real room tuning; values
  from the James reference are used as-is (all bands near 0 dB)
- DE-S2 parameter tuning — James reference values are the accepted baseline; per-team
  deesser adjustment is out of scope
- FX3 — inconsistent across team references, remains deferred
- icon or preamp gain for LCL/4 — name label only; other io.in.LCL fields stay at Init default

## Constraints

- FX10 and FX11 params copied verbatim from James 2025-12-14 reference: `{mdl: DE-S2,
  fxmix: 100, lo: 29, hi: 35, los: 0, his: 0, gdr: f, mode: st}` and `{..., lo: 19,
  hi: 37, gdr: m}` — added to infrastructure.yaml under `fx: 10:` and `11:`; renderer
  already handles pass-through via `_apply_fx`
- FX13 added to infrastructure.yaml under `fx: 13:` with James reference values
  (near-flat STD GEQ); the `# placeholder — room tuning deferred` comment is required
- `io.in.LCL.4.name = "Computer"` is written by a new `_apply_local_input_labels`
  function in infrastructure.py — reads `channels:` entries with LCL inputs and writes
  name to the corresponding `io.in.LCL[n]` slot; name is sourced from the existing
  `channels.39.name` declaration, no new DSL fields needed
- Integration diff test must pass for FX10, FX11, FX13, and io.in.LCL.4 against the
  James reference

## Escalation Triggers

- If any other team reference snapshot has materially different FX10/11 values, pause —
  these are infrastructure-level and should be consistent across teams
- If the GEQ placeholder framing needs to change (e.g., if you want explicitly-all-zeros
  rather than James values), pause before writing FX13

## Decisions

(populated during implementation)
