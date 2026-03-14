# Snapwright Coverage — Gaps and Priorities

_Generated: 2026-03-14. Source: docs/coverage-report.json_

This document explains what the Snapwright renderer owns in the Wing snapshot, where gaps exist, and which gaps are worth closing. It is regenerated from `docs/coverage-report.json` after each significant renderer change. The ratio metric (changed fields ÷ total fields per section) surfaces three patterns: zero-ratio sections the renderer never touches, high-ratio sections the renderer substantially owns, and partial-coverage sections where the ratio is low within a higher-ratio parent or siblings diverge sharply — those are the most actionable signals. Overall: **3,110 of 28,585 fields changed from Init.snap (10.9%)**.

---

## Priority: Gaps Worth Closing

Ordered by operational impact. Correctness gaps (something is wrong on load) outrank convenience gaps (works but requires manual setup). The Sunday service context weights errors discovered mid-service as high-cost and nearly unrecoverable.

---

### 1. `ce_data.safes` — Protect monitor faders from mid-service snapshot recall

**What it is**: Snapshot recall safes are a per-parameter bitmask that prevents specific values from being overwritten when any snapshot is recalled. Without safes, a full recall resets every parameter to the stored value — including monitor bus fader positions.

**Why it ranks first**: Monitor faders are explicitly designed to drift from DSL defaults each service. That is the point — musicians and the engineer adjust in-ear and wedge levels during rehearsal. If a volunteer accidentally triggers a snapshot recall mid-service, every monitor mix reverts to the DSL starting point. Monitors feed in-ear packs and wedges; an unexpected level jump mid-song causes disorientation, feedback risk, and no quick path back to the per-service mix. No feature brief has addressed safes. The renderer writes nothing to `ce_data.safes`; Init.snap's "no safes" default passes through unchanged.

**What closing it requires**: Map the Wing `ce_data.safes` JSON format (field names and bitmask structure — likely one bitmask word per section), decide which parameters to protect (monitor bus faders at minimum; possibly monitor sends on individual channels), and render the safe mask as infrastructure — it is identical for every team. This is a self-contained infrastructure renderer addition with no DSL schema impact.

---

### 2. `ae_data.fx` slots 10, 11 — Deessers absent from Handheld and Headset channels

**What it is**: FX slot 10 is a DE-S2 deesser pre-inserted on ch37 (Handheld wireless mic). FX slot 11 is a DE-S2 deesser pre-inserted on ch38 (Headset mic). Without them, both vocal mic channels load with no sibilance control.

**Why it ranks second**: These are correctness gaps — both channels load with a pre-insert assignment that points to an empty FX slot. The deessers are not session-adjusted; they are permanent infrastructure-level processing for the mic type. The `infrastructure-dsl` brief deferred them explicitly ("Channel-insert FX (FX10, FX11 for infra channels) are also deferred — they'll leave those inserts unpopulated until a follow-on feature models them"). The deferral was intentional scope management, not a permanent decision.

**What closing it requires**: Add DE-S2 deesser model parameters to FX slots 10 and 11 in `infrastructure.yaml` (same pass-through schema as bus-wired FX slots). The channels already declare the pre-insert assignments — those write correctly. The slots just need populated parameters.

---

### 3. `ae_data.fx` slot 13 — GEQ absent from main house output

**What it is**: FX slot 13 is a graphic equalizer (GEQ) pre-inserted on `main.1` (HOUSE output). The house GEQ shapes the room's frequency response for the PA system. Without it, the house output loads without room correction.

**Why it ranks third**: Correctness gap. The GEQ is not a session-adjusted effect — it is the room's tuning curve, set during PA commissioning. Loading without it means the house sounds different until an engineer notices and manually loads the GEQ. The `infrastructure-dsl` brief deferred it in the same batch as FX10/11. Main.1 already declares the pre-insert assignment correctly; the FX slot is empty.

**What closing it requires**: Extract the GEQ model parameters from the James reference snapshot and add FX slot 13 to `infrastructure.yaml`. Same pattern as FX10/11.

---

### 4. `ae_data.io.in` — Computer channel unlabeled on console input patch

**What it is**: The Computer channel (ch39) uses local input LCL/4. The renderer writes channel name and processing to `ae_data.ch.39` correctly, but never writes `io.in.LCL.4.name`. The Wing displays the `io.in` label on the physical strip in input-patch view; without it, the slot shows blank.

**Why it ranks fourth**: Convenience gap. The channel processes audio correctly — it mutes on load, routes to stream, and has full processing. The only symptom is a blank label in the console's input patch view. No operational failure. The `stage-box-labels` brief deferred local and aux input labeling explicitly.

**What closing it requires**: Extend the stage-box-labels renderer to write `io.in.LCL.{n}.name` for infrastructure channels (ch39 = LCL/4). Low effort; the pattern already exists for stage-box A slots.

---

### 5. `ce_data.cfg` — Console preferences rest on an untested Init.snap assumption

**What it is**: Console display and behavior settings — solo exclusivity, fader-to-solo behavior, screen preferences. The `infrastructure-dsl` brief validated Init.snap's `ce_data.cfg` defaults against the Dec-14 James reference and found them correct. The renderer writes nothing here; Init defaults pass through.

**Why it ranks fifth**: The risk is not today's gap but future drift. If a firmware update changes Init.snap defaults for an audio-consequential preference (solo exclusivity, for example), the renderer silently inherits the new value. Explicit rendering would make that detectable. Low near-term priority — the assumption has held and the settings are not on the critical path for a working console.

**What closing it requires**: Extract audio-consequential `ce_data.cfg` values from the reference snapshot, add them to `infrastructure.yaml`, and write them in the infrastructure renderer. Scope is small (a handful of fields); the effort is mainly in deciding which preferences warrant explicit ownership.

---

### Everything else — Low priority

Remaining not-rendered sections are either hardware absent from the current rig (expansion cards, GPIO, MIDI, OSC, DAW), session-level operator preferences that correctly belong outside renderer scope (playback mode, recording paths), or deferred convenience features with no operational failure mode (left/center surface strip content, user banks 5–16). Init.snap defaults are correct for all of them; no Sunday service risk.

---

## Partial Coverage — Rendered sections with low-ratio sub-sections

These sections have a parent ratio above 10% but contain sub-sections that differ sharply or sit near zero. The renderer touches them but leaves meaningful sub-sections unset. Most are explained by intentional deferral; a few are correctness gaps (see Priority above).

---

### `ae_data.fx` — Bus-wired FX slots rendered; channel-insert and unused slots at 0%

**82.4% overall. Slots 1, 2, 5, 6, 7: 91–100%. Slots 3, 4, 8–16: 0%.**

FX slots 1, 2, 5, 6, and 7 are bus-wired effects (V-PLATE drums reverb, VSS3 room reverbs, TAP-DL delay, stream reverb). They are fully rendered with all model parameters from `infrastructure.yaml`.

- **FX3** (0%): Deferred per `infrastructure-dsl` brief — the corresponding FX content is inconsistent across team snapshots. Init.snap has this slot as NONE; it is a genuine deferred gap.
- **FX4** (0%): Not used in any reference snapshot. Init NONE default is correct.
- **FX8–9** (0%): Not used. Init NONE defaults are correct.
- **FX10, 11** (0%): DE-S2 deessers for Handheld and Headset channels. Channel pre-insert assignments are written correctly; the FX slots are empty. **Correctness gap — see Priority #2.**
- **FX12** (0%): Not used. Init NONE default is correct.
- **FX13** (0%): GEQ for main.1 house output. Main.1 pre-insert assignment is written correctly; FX slot is empty. **Correctness gap — see Priority #3.**
- **FX14–16** (0%): Not used. Init NONE defaults are correct.

---

### `ae_data.cfg` — Monitor config and RTA rendered; bus config settings pass through

**16.1% overall. cfg.mon: 22.4%. cfg.rta: 50%. cfg.talk: 9.1%. All others: 0%.**

The renderer owns monitor dim levels (`cfg.mon.1/2`), RTA display settings (decay rates, source, gain), and talkback routing (`cfg.talk` — assign=CH40, bus dim, monitor bus assignments). The zero-ratio sub-sections are not gaps:

- `cfg.amix` — Auto-mix disabled rig-wide; Init default correct.
- `cfg.dcamgrp` — No inter-group DCA/mgrp dependencies used; Init default correct.
- `cfg.mainlink` — HOUSE and STREAM run independently; Init "unlinked" default correct.
- `cfg.mtr` — Meter bridge display settings; visual only, no audio consequence.
- `cfg.solo` — PFL mode matches monitoring workflow; Init default correct.

---

### `ae_data.io` — Stage box A and output routing rendered; local/aux inputs not

**Overall 2.2%. io.in: 1.6% (65/3,972). io.out: 5.5% (41/748).**

The very low ratio reflects the large field count relative to what is rendered. Stage-box A input slots covered by the assembly get name, icon, and preamp gain from the `stage-box-labels` renderer. Physical output routing is rendered for PA monitor sends (A.1–A.6), P16 personal mixer outputs (A.33–A.48), AUX outputs (stream feeds), and USB outputs.

Sub-sections not rendered:
- `io.in.LCL` (local inputs): Only LCL/4 (Computer) matters; its channel processes correctly but the input-patch label is blank. **Convenience gap — see Priority #4.**
- `io.in.AUX`, stage box B, card inputs: Not used in current rig. Init defaults (blank) correct.
- `io.out.A.7–A.32`: Unused in current rig. A.7 confirmed as vestigial MTX.1 output, excluded in `infra-output-routing`. Init defaults correct.
- `io.out.LCL`, `io.out.B`, `io.out.CRD`: Not used. Init defaults correct.

---

### `ae_data.bus` — Mix buses rendered; bus 8 intentionally skipped

**13.4% overall. Buses 1–7: 10–21%. Bus 9–16: 10–21%. Bus 8: 0%.**

Buses 1–7 (submix and FX return buses) and buses 9–16 (FX return and monitor buses) are substantially rendered: name, color, icon, fader, dynamics, main.1/main.2 routing, and FX insert assignments. Monitor buses 13–16 keep their faders at Init default (-144 dB session-adjusted).

Bus 8 is intentionally skipped. The `infra-dsl-vocabulary` brief classifies it as "factory debris — never operator-configured" and masks it in the diff harness. Init.snap defaults pass through for bus 8; the decision is that this is acceptable debris, not an active bus.

---

### `ce_data.layer` — Right surface rendered; left and center get selected page only; others pass through

**0.2% overall. R: 2.1%. L: 0.2%. C: 0.3%. CMPCT, EXT, RCK, VRT, WEDIT: 0%.**

The control-surface renderer writes USER1 page strip content (channel and main strip assignments) to the right surface (`ce_data.layer.R`), plus the selected-page indicator. Left (`L`) and center (`C`) surfaces receive only the selected-page indicator — no strip content. The remaining layer types (CMPCT, EXT, RCK, VRT, WEDIT) pass through from Init.

The `control-surface` brief deferred left and center USER page strip content explicitly: "Strip content for left and center USER pages — selected page only for L/C." This is a convenience gap — the right surface works correctly for the "send on fader" monitor flip workflow, which is the trained volunteer interaction. Left and center surface USER pages default to Init layout.

**What would be gained**: Full strip labeling on L and C USER pages for volunteers who work from those surfaces. Not a correctness gap; the right surface and the four user banks cover the trained workflow.

---

### `ce_data.user` — Right surface user banks 1–4 rendered; banks 5–16 and all other layouts at 0%

**10.0% overall. Banks 1–4: 12–69%. Banks 5–16: 0%. D1–D4, MM, U1–U4, daw1–4, gpio, mode, sel, user: 0%.**

The control-surface renderer writes strip content for the four right-surface user banks declared in `infrastructure.yaml`: monitors (bank 1, 69%), vocals (bank 2, 47%), fx_sends (bank 3, 60%), and dca_fx (bank 4, 12%). These correspond to physical buttons 1–4 on the right surface.

Banks 5–16 are at 0% because no additional banks are declared in the DSL. Init defaults (empty bank content) pass through — buttons 5–16 on the right surface are blank, which is correct given the current four-bank design.

The remaining zero-ratio sub-sections (`D1–D4` — drum surface banks, `MM` — monitor module, `U1–U4` — undefined, `daw1–4` — DAW control, `gpio`, `mode`, `sel`, `user`) are left-surface and center-surface user page content, DAW integration, and mode configuration. All deferred per the control-surface brief; Init defaults pass through.

---

## Not-Rendered Gaps — 0% ratio; Init.snap defaults are wrong or incomplete

---

### `ce_data.safes` — No recall protection; all parameters unprotected

Snapshot recall safes prevent specific parameter values from being overwritten on recall. Without them, any snapshot recall (accidental or deliberate) resets all monitored parameters to the stored DSL starting point. Monitor faders are explicitly designed to drift from DSL defaults each service. A mid-service reset is an operational failure with no quick recovery path.

No feature brief has addressed this section. The renderer writes nothing; Init.snap's "no safes" state passes through unchanged. **See Priority #1.**

---

## Pass-Through — 0% ratio; Init.snap defaults are intentionally correct

These sections are never touched by the renderer. Init.snap factory defaults are the correct value for all of them given the current rig configuration.

---

### `ae_data.cards`
Wing expansion card slots (`wlive`, `wmadi`). No expansion cards installed in the current rig. Init no-op defaults correct.

### `ae_data.play`
Playback engine settings (repeat mode, source). Session-level operator preference, not a static infrastructure setting. Operators set this on the fly.

### `ae_data.rec`
Onboard recording configuration (file path, sample rate, channel selection). Filesystem paths are device-specific and change between sessions; not a renderer concern.

### `ae_data.cfg.amix`
Auto-mix configuration. Auto-mix not enabled on any channel in the current rig.

### `ae_data.cfg.dcamgrp`
Inter-group DCA and mute group dependency configuration. No inter-group dependencies used in the Sunday service workflow.

### `ae_data.cfg.mainlink`
Main output linking (gangs HOUSE and STREAM faders). Current rig uses HOUSE and STREAM as independent outputs; unlinked Init default is correct.

### `ae_data.cfg.mtr`
Meter bridge display settings (peak hold, RMS/peak mode, source). Visual only; no audio consequence.

### `ae_data.cfg.solo`
PFL/AFL solo bus configuration. Init PFL mode matches the monitoring workflow in use.

### `ce_data.cfg`
Console display and behavior preferences (brightness, RTA colors, fader touch behavior). The `infrastructure-dsl` feature diffed Init.snap against the Dec-14 James reference and found Init defaults correct for all audio-consequential settings. An implicit assumption: if a firmware update changes Init defaults here, the renderer would not catch the divergence. See Priority #5 for the long-term case for explicit rendering.

### `ce_data.gpio`
GPIO port assignments for footswitches and external control triggers. No GPIO hardware connected in the current rig.

### `ce_data.daw`
DAW control surface integration (HUI/MCU). No DAW integration in the Sunday service workflow.

### `ce_data.midi`
MIDI controller configuration. No MIDI controllers in use.

### `ce_data.osc`
OSC remote control configuration. No OSC-based control in use; Init read-only mode correct.

### `ce_data.lib`
Wing channel strip library (stored channel presets). Empty in Init.snap; presets live in the DSL, not the Wing library.

### `ce_data.layer.CMPCT`, `.EXT`, `.RCK`, `.VRT`, `.WEDIT`
Compact, external, rack, vertical, and W-Edit control surface layer layouts. Not used in the Sunday service workflow. Init defaults pass through.

---

## Substantially Rendered — For reference

Sections the renderer substantially owns (>10% ratio), documented briefly.

| Section | Ratio | What the renderer owns |
|---|---|---|
| `ae_data.ch` | 18.8% | All 18 assembly channels: name, icon, color, input routing, fader, mute, EQ, dynamics, gate, filters, sends, inserts, tags |
| `ae_data.bus` | 13.4% | Buses 1–7, 9–16: name, color, icon, fader, dynamics, main routing, FX insert assignments (bus 8 skipped) |
| `ae_data.main` | 21.4% | HOUSE and STREAM: name, icon, EQ, dynamics, fader; main.3 fixed level |
| `ae_data.dca` | 20.5% | DCAs 1–8: name, fader |
| `ae_data.mgrp` | 56.2% | Mute groups 1–8: name, mute state |
| `ae_data.fx` | 82.4% | FX slots 1, 2, 5, 6, 7: full model parameters for bus-wired effects |
| `ae_data.aux` | 10.0% | Aux channels 1–8: infrastructure routing configuration |
| `ae_data.mtx` | 12.3% | Matrix buses 1–6: P16 personal mixer group names, faders |
| `ae_data.cfg` | 16.1% | Monitor dim levels, RTA display settings, talkback routing |
| `ae_data.io` | 2.2% | Stage-box A input labels and gains (assembly channels); PA/monitor/P16/stream output routing |
| `ce_data.layer.R` | 2.1% | Right surface: USER1 strip content + selected page |
| `ce_data.layer.L` | 0.2% | Left surface: selected page indicator only |
| `ce_data.layer.C` | 0.3% | Center surface: selected page indicator only |
| `ce_data.user` | 10.0% | Right surface user banks 1–4: monitors, vocals, fx_sends, dca_fx |
