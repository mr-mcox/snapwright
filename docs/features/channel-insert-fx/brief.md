---
feature: channel-insert-fx
date: 2026-03-12
commit: 7c801d5
branch: main
status: compacting
read-when: "starting implementation"
---

## Problem

FX slots 10, 11, and 13 are assigned as pre-inserts on Handheld, Headset, and house main
respectively, but the slots have no model parameters — they load empty. The deessers are
permanent infrastructure-level processing for those mic types; without them, both vocal
channels load with sibilance uncontrolled. FX13 is a placeholder for future room-tuning GEQ;
without it the house main has no insert in the slot that is already assigned. Additionally,
ch39 (Computer) and ch40 (Talkback) load with blank input-patch labels and default gain
because `io.in.LCL` slots are never written — the renderer has no concept of local input
labels or preamp gains for infrastructure channels.

## Not Doing

- GEQ room calibration — FX13 is a near-flat placeholder pending real room tuning; values
  from the James reference are used as-is (all bands near 0 dB)
- DE-S2 parameter tuning — James reference values are the accepted baseline; per-team
  deesser adjustment is out of scope
- FX3 — inconsistent across team references, remains deferred
- LCL slots 2-3 — populated in team references but unowned by infrastructure (drift, not intentional config)

## Constraints

- FX10 and FX11 params copied verbatim from James 2025-12-14 reference: `{mdl: DE-S2,
  fxmix: 100, lo: 29, hi: 35, los: 0, his: 0, gdr: f, mode: st}` and `{..., lo: 19,
  hi: 37, gdr: m}` — added to infrastructure.yaml under `fx: 10:` and `11:`; renderer
  already handles pass-through via `_apply_fx`
- FX13 added to infrastructure.yaml under `fx: 13:` with James reference values
  (near-flat STD GEQ); the `# placeholder — room tuning deferred` comment is required
- `_apply_local_input_labels` (new function in infrastructure.py) writes name, icon,
  and preamp_gain (`g`) to `io.in.LCL[n]` for ch39 (LCL.4) and ch40 (LCL.1) —
  both infrastructure channels with local inputs; same fields as `_apply_stage_box_labels`
- `preamp_gain` added to `channels.39` (15 dB) and `channels.40` (42.5 dB) in
  infrastructure.yaml; James reference is canonical; variation in other team snapshots
  is drift, not intentional
- `io.in.LCL.1.name` will render as 'TALKBACK' (infrastructure-authoritative); all
  existing snapshots carry 'Matthew' — accepted drift, rendered snapshots will converge
- Integration diff covers FX10, FX11, FX13 fully; LCL.4 fully (name+icon+g); LCL.1
  icon+g only (name diverges from James reference — 'TALKBACK' vs 'Matthew' — accepted);
  LCL slots 2-3 remain masked

## Escalation Triggers

- If any other team reference snapshot has materially different FX10/11 values, pause —
  these are infrastructure-level and should be consistent across teams
- If the GEQ placeholder framing needs to change (e.g., if you want explicitly-all-zeros
  rather than James values), pause before writing FX13

## Decisions

- FX10/11/13 added to infrastructure.yaml as pass-through YAML blocks; `_apply_fx`
  already handled them, no renderer changes needed
- `_apply_local_input_labels` added to infrastructure.py; writes name/icon/g to
  io.in.LCL[n] for any channels: entry with grp=LCL; ch40 name renders 'TALKBACK'
  (infrastructure-authoritative), divergence from all existing snapshots accepted
