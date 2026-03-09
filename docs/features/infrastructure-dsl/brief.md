---
feature: infrastructure-dsl
date: 2026-03-08
commit: 6578c39
branch: infrastructure-dsl
status: implementing
read-when: "starting or resuming implementation of Init.snap + infrastructure.yaml"
---

## Problem

The rendering pipeline uses Base.snap as its foundation — an opaque binary with accumulated debris. There's no way to audit what's intentional vs accidental, and no way to evolve infrastructure without manually editing a binary. The fix is Init.snap (factory reset) + infrastructure.yaml (every intentional change from factory, documented with purpose), replacing Base.snap entirely as the rendering foundation.

## Validation Target

**Init.snap + infrastructure.yaml + James assembly.yaml should produce a snapshot that diffs cleanly against `data/reference/snapshots/james-2025-12-14.snap`.**

"Diffs cleanly" means zero differences in infrastructure sections. Acceptable noise:
- Float precision (Wing stores -2.799999714, we write -2.8 — within 0.01 is fine)
- Session-adjusted values: monitor faders, bus faders, main fader — these move per service
- Sections explicitly excluded (see below)

To validate: render `Init.snap + infrastructure.yaml + data/dsl/teams/james/assembly.yaml` using
the existing `render_assembly()` pipeline, then parse both the rendered bytes and the reference
file using the Wing parser (`WingSnapshot.from_bytes()`), and diff the resulting dicts section
by section. Mask out: unused input channels (ch1-36 except ch37-40), `ce_data.layer` (user-layers
feature), and float-precision-only differences (abs delta < 0.01 for numeric values). Focus
diff output on ae_data.bus, ae_data.fx, ae_data.main, ae_data.ch (infra channels), ae_data.dca,
ae_data.mgrp, ae_data.cfg.

## Not Doing

- `ce_data.layer` — layer bank layout. That's the `user-layers` feature.
- `ce_data.cfg` display/lighting prefs — personal operator settings (brightness, RTA colors, etc.)
- Unused channels (ch9-12, 15, 17-36 in James) — Init.snap defaults pass through, which is correct for unused slots
- DCA membership / bus tags — that's `tags-ownership`
- `io` section (stage box gains, labels) — separate feature
- Personal mixer routing (MX, matrix) — `personal-mixer-routing` feature

## Scope: What infrastructure.yaml Must Cover

Derived from diffing Init.snap + current infrastructure against Dec-14 James.snap.
All values sourced from the Dec-14 reference unless noted.

### FX slots (bus-wired only)
Full params for bus-wired FX slots only. Pass-through schema (extra="allow" on FxSlotDef),
no typed per-model fields needed.

- FX1: V-PLATE (drums reverb) — bus1 post-insert
- FX2: VSS3 Church long reverb — bus11 pre-insert
- FX5: VSS3 Ballad Vocal Hall medium reverb — bus10 pre-insert
- FX6: TAP-DL slap delay — bus9 pre-insert
- FX7: VSS3 Venue Warm 1 stream reverb — bus5 post-insert
- FX3: deferred (inconsistent across team snapshots)

Note FX7 has fxmix=0 — level controlled via bus send, not the mix knob.

Deferred (Init has these as NONE, need modeling eventually but not this feature):
- FX10: DE-S2 deesser — ch37 Handheld pre-insert
- FX11: DE-S2 deesser — ch38 Headset pre-insert
- FX13: GEQ — main.1 pre-insert

### Buses 1-12 (mix and FX return buses)
Per bus: name, color, icon, led=False, fader, dynamics (SBUS model with per-bus params),
main.1 and main.2 routing (on + lvl), pre/post insert assignments, tags.

Key findings:
- Buses 1-8 all use SBUS dynamics (enabled) with different thresholds per bus
- Bus 7: stream-only (main.2.on=True, main.1.lvl=-144), unnamed — probably a stream utility bus
- Bus 8: goes to house (main.1.on=True), unnamed  
- Bus 12: name='Back Vox' in James (not 'Delay/Rhythm' as other teams have)
- FX insert map: bus1→FX1(post), bus5→FX7(post), bus9→FX6(pre)+FX3(post), bus10→FX5(pre), bus11→FX2(pre)

### Buses 13-16 (monitors)
Per bus: name, color (1=red), icon (520/521), led=False, fader (start level),
main.1.on=False (monitors don't go to house), main.2.on=True, main.2.lvl=-144.

Note: monitor faders in Dec-14 snapshot differ from Base.snap defaults (-17 to -20 range).
These are session-adjusted — set reasonable starting values and accept drift.

### Main outputs (main.1=HOUSE, main.2=STREAM)
main.1: name='HOUSE', icon=509, led=False, EQ (enabled, 6-band with specific settings),
dynamics (76LA, ratio='20', att=1.7, rel=1.8), pre-insert=FX13 (GEQ), fader (session value),
in.set.bal=-4.5, in.set.trim=-4.5

main.2: name='STREAM', icon=606, led=False, dynamics (76LA, ratio='20', enabled),
fader (session value)

main.3: fdr=-70.1, led=False (fixed, not session-adjusted)

### Infrastructure channels (ch37=Handheld, ch38=Headset, ch39=Computer, ch40=Talkback)

**Critical**: These channels need full rendering — name, icon, color, input routing,
fader, mute, EQ, dynamics, gate, filters, sends, insert assignments, ptap, main routing.
Init.snap's send mode defaults (PRE for buses 1-8) are wrong for these channels;
the infrastructure renderer must set correct send modes (POST for buses 1-8, PRE for 13-16).

ch37 (Handheld): full EQ tuned for wireless handheld, gate configured,
  pre-insert=FX10 (DE-S2 deesser), sends to monitor buses + bus 6, main.2.on=True

ch38 (Headset): full EQ tuned for headset mic, gate configured,
  pre-insert=FX11 (DE-S2 deesser), sends to monitor buses, main.2.on=True

ch39 (Computer): source=local/4, muted, main.2.on=True, standard send modes

ch40 (Talkback): source=local/1, muted, main.1.on=False, col=9, clink=False,
  standard send modes (POST for buses 1-8, PRE for 13-16), MX plink=True

### DCA names and faders
DCAs 1-7 are named and at unity (0 dB): Rhythm, Inst B, Vox B, Leads, FX, All No L, Monitors.
DCA 8: name='DCA|8' (apparent typo in reference, keep as-is). DCAs 9-16: Wing defaults.

### Mute groups (mgrp)
mgrp 1-7 named: Rhythm, Inst B, Vox B, Leads, Inst All, Vox All, Monitors.
mgrp 8: name='Worshp', mute=True (note: apparent typo in reference, keep as-is).

### ae_data.cfg (console config)
- cfg.talk: assign=CH40, A.B13-B16=True, A.busdim=20 (talkback routing — already clean in current code)
- cfg.mon.1/2: dim and pfldim need to be 0 (Init has 12/20, ref has 0)
- cfg.rta: eqdecay=SLOW, rtadecay=SLOW, rtasrc=65, rtaauto=False, eqgain=-5

### ce_data.cfg (audio-consequential prefs only)
Based on diff, Init.snap values match reference better than what we had before.
Items where Init differs from reference and we should match reference:
- muteovr=False (not True — leave at Init default)
- mfdr='OFF' (not 'MAIN.1' — leave at Init default)
- mtxspill=False, csctouch=False, seldblclick='OFF', sofframe=False (all Init defaults are correct)

Conclusion: ce_data.cfg may need NO infrastructure modeling — Init defaults match reference
for all audio-consequential settings. Verify this in implementation.

## Constraints

- Init.snap (`data/reference/Init.snap`) is the rendering foundation — never modified
- Infrastructure YAML lives at `data/dsl/infrastructure.yaml`; single file
- Validation target: `data/reference/snapshots/james-2025-12-14.snap` (committed to repo)
- Every value in infrastructure.yaml must be self-documenting — no unexplained parameters
- `#M8` tags are NOT set in infrastructure.yaml — renderer owns all tag assignment
- The existing channel pipeline (`_render()` for ae_data.ch DSL channels) must continue to work
- Existing tests must continue to pass
- **Tests are unit-level and behavior-focused**: test that a section can be modeled and renders
  to the correct snap path — not that specific values from the YAML appear in the snap.
  The diff against Dec-14 James.snap is the integration test.
- Infrastructure channels (ch37-40) need explicit send mode rendering, same pattern as
  DSL channel renderer — Init.snap's PRE defaults for buses 1-8 are wrong

## Escalation Triggers

- If SBUS dynamics params vary significantly across buses and require per-bus Pydantic schema,
  pause — pass-through extra fields may be the right approach
- If infrastructure channel sends need full rebuild logic (same as DSL renderer), consider
  extracting shared send-building utility rather than duplicating
- If any Dec-14 reference value looks like session debris rather than infrastructure
  (e.g., main fader position), document the decision rather than modeling it

## Decisions

### 2026-03-08 — Base.snap is not a valid validation target

Base.snap predates the channel reorganization that moved infrastructure channels from
ch13/14 to ch37/38/39/40. It has ch37-39 empty and ch13/14 configured as Computer/Handheld.
The Dec-14 James.snap is the correct reference for what infrastructure.yaml should produce.

### 2026-03-08 — infrastructure applied in defaults.py, not renderer.py

`snap_template()` returns Init.snap + infrastructure already applied. This enforces the
invariant for all callers without requiring opt-in.

### 2026-03-08 — FX scope: bus-wired slots only

Only FX slots that are wired to submix buses are in scope: FX1, FX2, FX5, FX6, FX7.
FX3 is deferred (inconsistent across team snapshots). Channel-insert FX (FX10, FX11
for infra channels; FX13 for main) are also deferred — they'll leave those inserts
unpopulated until a follow-on feature models them.
Pass-through schema (extra="allow") keeps Pydantic simple despite per-model variation.

### 2026-03-08 — ce_data.cfg: Init defaults match reference

After diffing against Dec-14 James.snap, Init.snap's ce_data.cfg defaults are correct
for all audio-consequential settings. No infrastructure modeling needed for this section.

### 2026-03-08 — Monitor faders are session-adjusted, not fixed infrastructure

Dec-14 James.snap has monitor faders at -15 to -17 dBFS, not the ~-20 we assumed.
These are set per-service. Infrastructure sets a reasonable start value; teams adjust.

### 2026-03-08 — Test philosophy

Unit tests verify that each schema section renders to the correct snap path and that
type coercions are correct. They do NOT verify specific YAML values appear in the snap
(circular/useless). A session-built diff harness against Dec-14 James.snap is the integration
test that drives what to implement next (see Validation Target section for what to build).
