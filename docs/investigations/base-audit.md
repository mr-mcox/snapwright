# Base.snap Audit — Investigation A

**Date**: 2026-03-08  
**Input files**: `data/reference/Base.snap` (firmware 2.0), `/Users/mcox/Documents/Wing Backup/Init.snap` (Wing Edit 3.3.1)  
**Method**: Targeted leaf-level diff focusing on human-configured fields (names, faders, colors, icons, processing on/off, routing, tags). Schema-level differences due to firmware version mismatch are identified and excluded.

---

## ⚠️ Firmware Version Mismatch

Init.snap was created by **Wing Edit 3.3.1** (snapshot type 11), while Base.snap was created on **firmware 2.0** (snapshot type 8). Sunday starters are on **firmware 3.0.5** (snapshot type 10). This means a raw leaf diff produces thousands of false-positive differences from schema changes — parameter names for dynamics, filters, and some routing were restructured between versions.

This audit focuses on semantically stable fields: `name`, `fdr`, `mute`, `col`, `icon`, `on` (processing toggles), `tags`, and input routing (`in.conn`). Schema-version diffs are called out explicitly where they occur.

**Implication for Phase 3**: If we ever want to "reset to factory" any parameter group, we need a Base.snap-relative baseline, not an Init.snap-relative one.

---

## Section 1: Channels (`ae_data.ch`)

### 1a. Named and Configured Channels in Base

Eight channels have meaningful configuration in Base (names, faders, or both):

| Ch | Name | Fader | Mute | Input | Tags | Notes |
|----|------|-------|------|-------|------|-------|
| 01 | Kick | -0.6 dB | off | A.2 | `#M8` | Drum kit — permanent infrastructure |
| 02 | Snare | +0.2 dB | off | A.3 | `#M8` | Gate ON, Dyn ON (COMP) |
| 03 | Tom | -0.4 dB | off | A.5 | `#M8` | EQ on |
| 04 | Overhead | +0.1 dB | off | A.4 | `#M8` | EQ on |
| 13 | Computer | +5.8 dB | off | LCL.4 | `#M8` | Dyn ON (RIDE model) — playback source |
| 14 | Handheld | +0.2 dB | off | A.32 | `#M8` | Dyn ON (RIDE model) — handheld mic |
| 38 | Lapel | +0.8 dB | **on** | A.31 | _(none)_ | Dyn ON (COMP); **muted at Base level** |
| 40 | TALKBACK | -inf dB | **on** | LCL.1 | _(none)_ | Red (col=9), headset icon; **muted at Base** |

**Category: Intentional Infrastructure** (channels 1, 3, 4, 13, 14, 40)  
**Category: Active Configuration** (channels 2, 38)

**Notes on processing:**
- Only Snare (ch02) has **gate and dynamics both active** — the most fully processed drum channel
- Computer and Handheld use the **RIDE** dynamics model, not COMP — this is a "ride-through" dynamic rather than a compressor; probably intentional for clarity
- Lapel is muted in Base — it only gets unmuted when needed, keeping it out of the house mix by default
- TALKBACK: muted, -inf fader, but input is wired (LCL.1 = Matthew's local input 1). Talkback is via the `ae_data.cfg.talk` system, not through the fader

### 1b. Tagged-Only Channels (no name, #M8 tag present)

Channels 15–24 are unnamed and at -inf fader, but all carry `#M8` (Worship mute group) tags. These are **pre-tagged empty slots** — ready for team content to be placed here, and already assigned to the Worship mute group without the team needing to set the tag.

| Ch range | Tags | Routing | Fader |
|----------|------|---------|-------|
| ch15 | `#M8` | LCL.5 (unnamed!) | -inf |
| ch16–21, ch23–24 | `#M8` | OFF | -inf |
| ch22 | `#M8` | OFF | **-88.2 dB** ← suspicious |

**Category: Intentional Infrastructure** — the #M8 pre-tagging of ch15-24  
**Category: Unknown** — ch22 at -88.2 dB (not -inf); see Questions  
**Category: Suspected Debris** — ch15 routing to LCL.5 (which has no io.in.LCL.5 config)

### 1c. Channels 25–40 — No Base Tags

Channels 25–36 have **no tags in Base** and are completely empty. This contrasts with ch15–24. In James.snap, ch25–30 (vocals) have `#M8` added by the renderer. So the split is:

- **ch01–24**: Pre-tagged `#M8` in Base (drum slots + general instrument slots)
- **ch25–40**: No pre-tagging in Base; renderer adds `#M8` for active channels

This is a design decision embedded in Base — the implication is channels 25+ are treated differently. This boundary may not be intentional; see Questions.

### 1d. Anomaly: ch37

ch37 has:
- No name
- Fader at +0.9 dB (above unity!)
- Input routed to A.48 (an unlabeled stage box input)
- Dynamics on (COMP, -15.5 dB threshold)

This is suspicious — an unnamed channel with above-unity fader and active compression, routed to an unidentified physical input. **Category: Unknown.** See Questions.

---

## Section 2: Buses (`ae_data.bus`)

### 2a. Bus Naming and Tags

All 16 buses are named in Base:

| Bus | Name | Fader | Color | Tags | DCA | MGrp | Notes |
|-----|------|-------|-------|------|-----|------|-------|
| 01 | DRUMS | -inf | 8 (orange) | `#D6,#M5,#D1,#M1` | 1+6 | 1+5 | Drums submix → DCA1, DCA6 |
| 02 | BASS | -inf | 9 (yellow) | `#D6,#M5,#D1,#M1` | 1+6 | 1+5 | Bass/rhythm with drums |
| 03 | Inst/House | -87.3 dB | 10 (green) | `#D6,#M5,#D2,#M2` | 2+6 | 2+5 | House instruments submix |
| 04 | Inst/Stream | -inf | 10 (green) | `#D6,#M5,#D2,#M2` | 2+6 | 2+5 | Stream instruments submix |
| 05 | Back Vox | -inf | 1 (white) | `#D6,#M6,#D3,#M3` | 3+6 | 3+6 | Background vocals |
| 06 | Lead/House | -inf | 3 (purple) | `#M5,#D4,#M4,#M6` | 4 | 4+5+6 | Lead vox house |
| 07 | Lead/Stream | -inf | 3 (purple) | `#M5,#D4,#M4,#M6` | 4 | 4+5+6 | Lead vox stream |
| 08 | All channels | -inf | 1 (white) | _(none)_ | — | — | No DCA/mgrp membership |
| 09 | Delay/Slap | **-inf** | 11 (cyan) | `#D5` | 5 (FX) | — | FX return bus |
| 10 | Delay/Repeat | **-inf** | 11 (cyan) | `#D5` | 5 (FX) | — | FX return bus |
| 11 | Reverb/Medium | **-inf** | 11 (cyan) | `#D5` | 5 (FX) | — | FX return bus |
| 12 | Reverb/Long | **-inf** | 11 (cyan) | `#D5` | 5 (FX) | — | FX return bus |
| 13 | Monitor/1 | -19.3 dB | 1 (white) | `#D7,#M7` | 7 | 7 | EQ on |
| 14 | Monitor/2 | -19.9 dB | 1 (white) | `#D7,#M7` | 7 | 7 | EQ on |
| 15 | Monitor/3 | -19.8 dB | 1 (white) | `#D7,#M7` | 7 | 7 | EQ off |
| 16 | Monitor/4 | -20.3 dB | 1 (white) | `#D7,#M7` | 7 | 7 | EQ off |

**Category: Intentional Infrastructure** — all bus naming, color coding, DCA/mgrp tags  
**Category: Active Configuration** — monitor bus faders (~-20 dB); these are the default starting levels for IEM/wedge mixes

### 2b. Bus Dynamics

All submix buses (01–07) have dynamics processors active:

| Bus | Model | Threshold | Notes |
|-----|-------|-----------|-------|
| 01 (DRUMS) | SBUS | -15.0 dB | "SBUS" = sidechain bus compressor |
| 02 (BASS) | COMP | -17.5 dB | |
| 03 (Inst/House) | SBUS | -9.0 dB | |
| 04 (Inst/Stream) | SBUS | -8.0 dB | |
| 05 (Back Vox) | SBUS | -10.0 dB | |
| 06 (Lead/House) | SBUS | -9.0 dB | |
| 07 (Lead/Stream) | SBUS | -12.0 dB | |

FX buses (09–12) and monitor buses (13–16) have dynamics **off** in Base.

**Category: Active Configuration** — these are deliberate mix dynamics

### 2c. CRITICAL: Bus Names in James.snap Are Stale

Base.snap now has updated bus names (Inst/House, Lead/House, etc.), but James.snap still shows old names (Rhythm/House, Rhythm/Stream, Melodic/House, Melodic/Stream, Vocals) for buses 2–7. This confirms the renderer is **not currently setting bus names** in team snapshots — or James.snap was generated before the bus naming was updated and hasn't been regenerated.

This is a data integrity issue: the console shows wrong bus names for the James team.

### 2d. Bus 03 Fader Anomaly

Bus 03 (Inst/House) has fader at **-87.3 dB** (not -inf). This is suspicious — it's "almost muted" but not fully. If this propagates to team snapshots, the house instrument mix starts nearly silent.

**Category: Suspected Debris** — accidental drag to near-zero, or an intentional suppression that was never cleaned up. See Questions.

### 2e. Bus 08 ("All channels") Has No Tags

Bus 08 is named "All channels" with no DCA or mgrp membership. It's at -inf fader. No channels send to it in Base (confirmed by checking all ch sends). Its purpose is unclear.

**Category: Unknown** — see Questions.

---

## Section 3: DCAs (`ae_data.dca`)

### 3a. Named DCAs 1–7

| DCA | Name | Base Fader | James Fader | Notes |
|-----|------|-----------|------------|-------|
| 01 | Rhythm | +0.2 dB | +0.2 dB | Controls DRUMS + BASS buses (via their tags) |
| 02 | Inst B | +0.3 dB | +0.3 dB | Controls Inst/House + Inst/Stream buses |
| 03 | Vox B | -0.3 dB | -0.3 dB | Controls Back Vox bus |
| 04 | Leads | -0.7 dB | -0.7 dB | Controls Lead/House + Lead/Stream buses |
| 05 | FX | **-0.2 dB** | **-16.4 dB** | Controls FX return buses 9–12 ← IMPORTANT |
| 06 | All No L | -0.7 dB | -0.7 dB | Controls DRUMS+BASS+Inst+BackVox buses (1–5); **NOT leads** |
| 07 | Monitors | +0.1 dB | +0.1 dB | Controls all monitor buses |

**Category: Active Configuration** — DCAs 1–4, 6, 7 are near unity, functioning as intended  
**Category: Active Configuration (concern)** — DCA 5 "FX": at -0.2 dB in Base (near unity, correct), but James.snap has it at -16.4 dB. This 16 dB suppression of all FX returns is operator-set (James's team preference), not a Base issue. But it means the FX are essentially silent in James's mix — all that reverb/delay processing does nothing audibly.

### 3b. DCAs 8–16 — Inconsistent Placeholder Names

DCAs 8–16 all remain at -inf fader (Init default) but have non-default names:

| DCA | Base Name | Notes |
|-----|-----------|-------|
| 08 | `DCA\|8` | Pipe separator — different style |
| 09–16 | `DCA.9` through `DCA.16` | Dot separator |

The `DCA|8` style (pipe separator) differs from `DCA.9`–`DCA.16` (dot separator). This inconsistency suggests dca08 was named at a different time or in a different context.

**Category: Suspected Debris** — these names serve no purpose; unnamed DCAs would be cleaner. The formatting inconsistency on dca08 is an additional marker of accidental/leftover state.

---

## Section 4: Mute Groups (`ae_data.mgrp`)

All 8 mute groups are named (vs Init where they were `MGRP.1`–`MGRP.8`):

| MGrp | Name | Base mute | James mute | Notes |
|------|------|-----------|-----------|-------|
| 01 | Rhythm | off | off | Matches buses 01–02 DCA1 |
| 02 | Inst B | off | off | Matches buses 03–04 DCA2 |
| 03 | Vox B | off | off | Matches bus 05 DCA3 |
| 04 | Leads | off | off | Matches buses 06–07 DCA4 |
| 05 | Inst All | off | off | Instruments all = buses 01–07 |
| 06 | Vox All | off | off | Vocals all = buses 05–07 |
| 07 | Monitors | off | off | Matches buses 13–16 |
| 08 | Worshp | off | **on** | `#M8` on all active channels; **ACTIVE in James.snap** |

**Category: Intentional Infrastructure** — mgrp naming mirrors DCA structure (intentional parallel design)  
**Category: Active Configuration** — mgrp08 "Worshp" is the live-use mute group; being muted in James.snap means a button press can mute all worship channels simultaneously

**Observation**: The mgrp names match the DCA names exactly for groups 1–4, 7. The relationship is:
- DCAs control bus fader levels
- Mute groups (same grouping) control hard mutes
- Both are tagged on the same buses

**Category: Active Configuration** — all 8 mute groups have intentional names and a coherent system

---

## Section 5: Main Outputs (`ae_data.main`)

| Main | Name | Fader | Mute | EQ | Dyn | Notes |
|------|------|-------|------|-----|-----|-------|
| 01 | HOUSE | -31.5 dB | off | on (STD) | on (76LA) | Primary house mix |
| 02 | STREAM | -inf dB | off | off | on (76LA) | Stream output (fader down in Base) |
| 03 | _(blank)_ | -70.1 dB | off | off | off | Unnamed, suspicious fader |
| 04 | _(blank)_ | -inf dB | off | off | off | Unused |

**Category: Intentional Infrastructure** — HOUSE and STREAM naming; 76LA limiter on both mains  
**Category: Active Configuration** — HOUSE main EQ active; HOUSE fader at -31.5 dB (operator's preferred starting level)  
**Category: Unknown** — main03 at -70.1 dB (not -inf) on unnamed/unused output; see Questions  
**Category: Suspected Debris** — main03 fader looks like an accidental bump; it should be at -inf if unused

---

## Section 6: FX Slots (`ae_data.fx`)

12 of 16 FX slots are loaded (Init has all empty):

| FX | Model | Purpose |
|----|-------|---------|
| 01 | V-PLATE | Plate reverb (short) |
| 02 | VSS3 | Room/hall reverb (medium) |
| 03 | TAP-DL | Tap delay |
| 04 | CHORUS | Chorus effect |
| 05 | VSS3 | Room/hall reverb (long?) |
| 06 | DEL/REV | Delay+reverb combo |
| 07 | PCORR | Pitch corrector |
| 08 | _(empty)_ | — |
| 09 | BODY | Body resonance |
| 10 | DE-S2 | De-esser |
| 11 | DE-S2 | De-esser |
| 12 | _(empty)_ | — |
| 13 | P-BASS | Bass pitch/processing |
| 14–16 | _(empty)_ | — |

**Category: Active Configuration** — all loaded FX are intentional processing tools. The two DE-S2 slots (10+11) suggest two different de-esser needs.

**Observation**: In Base.snap, **no channels send to FX buses 9–12** (verified by checking all channel sends). The FX return buses exist and are named, but the sends from channels to FX buses must be set by the renderer for each team. This is correct — FX send amounts are musician-specific, not base-level infrastructure.

---

## Section 7: AUX Inputs (`ae_data.aux`)

| Aux | Name | Fader | Color | Icon | Notes |
|-----|------|-------|-------|------|-------|
| 01 | USB 1/2 | -inf | 8 (orange) | 605 (USB) | Named and colored — active input source |
| 02–03 | _(blank)_ | -inf | default | 0 | Unused |
| 04 | _(blank)_ | **-76.1 dB** | default | 0 | Suspicious non-default fader; unnamed |
| 05–08 | _(blank)_ | -inf | default | 0 | Unused |

**Category: Intentional Infrastructure** — aux01 "USB 1/2" (playback source)  
**Category: Suspected Debris** — aux04 at -76.1 dB is suspicious; unnamed aux with non-default fader. See Questions.

---

## Section 8: Matrix (`ae_data.mtx`)

| MTX | Name | Fader | Notes |
|-----|------|-------|-------|
| 01 | _(blank)_ | **+10.0 dB** | Above unity — unusual! |
| 02–08 | _(blank)_ | -inf | Unused |

**Category: Unknown** — mtx01 at +10 dB with no name. This is the only non-default matrix bus. Positive gain in a matrix is unusual. See Questions.

---

## Section 9: Physical I/O (`ae_data.io`)

### 9a. Named and Configured Inputs

| Input | Name | Gain (dB) | +48V | Notes |
|-------|------|----------|------|-------|
| LCL.1 | Matthew | 42.5 | off | Matthew's local input 1 (also TALKBACK ch40 source) |
| LCL.2 | Lapel | 37.5 | off | Lapel mic |
| LCL.3 | HANDHELD | 32.5 | off | Handheld |
| LCL.4 | Computer | 17.5 | off | Computer playback |
| A.1 | Piano | 38.0 | off | Stage box input |
| A.2 | Kick | 28.0 | off | |
| A.3 | Snare | 28.0 | off | |
| A.4 | Overhead | 33.0 | off | |
| A.5 | Tom | 18.0 | off | |
| A.6 | Bass | 15.5 | off | |
| A.7 | JEN | 45.5 | off | Person name — see Questions |
| A.31 | Lapel | 30.5 | off | |
| A.32 | Handheld | 35.5 | off | |

**Category: Intentional Infrastructure** — all named/gained inputs are real physical sources with deliberate gain settings

### 9b. Systematic +0.5 dB Gain on A.8–A.30

All 23 inputs from A.8 through A.30 have a gain of **+0.5 dB** (vs 0 in Init). They are all unnamed and have no other configuration. This looks like a systematic base gain applied to all "available but unassigned" stage box inputs.

**Category: Unknown** — is this intentional as a "pre-gain" baseline, or is it an artifact? See Questions.

### 9c. Init Had "2TR" Names on PLAY.1–2

Init.snap had `io.in.PLAY.1` and `io.in.PLAY.2` named "2TR" (2-track return from recording). Base.snap has these blank. Minor difference.

**Category: Active Configuration** — cleared in Base intentionally, or oversight. Low priority.

---

## Section 10: Audio Engine Config (`ae_data.cfg`)

### 10a. Talkback (Intentional Infrastructure)

| Parameter | Value | Notes |
|-----------|-------|-------|
| `talk.assign` | CH40 | Talkback source = channel 40 (TALKBACK) |
| `talk.A.B13–B16` | True | Talkback A feeds all 4 monitor buses |
| `talk.A.busdim` | 20 dB | Monitor buses dim by 20 dB when talkback active |

**Category: Intentional Infrastructure** — complete talkback configuration

### 10b. Monitor Outputs

| Parameter | Value | Notes |
|-----------|-------|-------|
| `mon.1.srclvl` | 1.7 dB | Monitor 1 source level slightly elevated |
| `mon.1.pfldim` | 0 dB | Pre-fader dim: off (Base) |
| `mon.2.pfldim` | 20 dB | Pre-fader dim: 20 dB on monitor 2 |

**Category: Active Configuration**

### 10c. RTA Settings

| Parameter | Init | Base | Notes |
|-----------|------|------|-------|
| `rta.eqdecay` | MED | SLOW | EQ RTA decay slower in Base |
| `rta.eqgain` | 0 | -5 | EQ RTA gain offset |
| `rta.rtaauto` | True | False | RTA auto-select disabled |
| `rta.rtadecay` | MED | SLOW | RTA decay slower |
| `rta.rtasrc` | 0 | 65 | RTA source = channel 65 (presumably main?) |
| `solo.mon` | PH | A | Solo monitor mode changed |

**Category: Active Configuration** — operator preferences for how the console displays information

---

## Section 11: Console Engine Config (`ce_data.cfg`)

Notable differences from Init (firmware version issues aside):

| Parameter | Base Value | Notes |
|-----------|-----------|-------|
| `csctouch` | False | Touch-select on channel screen: disabled |
| `muteovr` | False | Mute override: disabled |
| `sofframe` | False | SOF frame display: off |
| `seldblclick` | OFF | Double-click select action: off |
| `lights.main` | 100 | Display brightness: full |
| `lights.btns` | 10 | Button backlight: dim |
| `lights.rgbleds` | 50 | RGB LEDs: medium |
| `rta.eqcol` | RD25 | EQ RTA color: red |
| `rta.homecol` | RD25 | Home RTA color: red |
| `rta.homedisp` | OFF | Home RTA display: off |

Several Init fields are absent from Base due to firmware schema differences (not meaningful differences).

**Category: Active Configuration** — deliberate operator preferences

---

## Section 12: Layer Banks (`ce_data.layer`)

### 12a. Left Fader Section (L) — 7 banks

| Bank | Name | Content | Selected |
|------|------|---------|---------|
| 1 | CH1-12 | CH 1–12, strips 13–24 OFF | |
| 2 | CH13-24 | CH 13–24, strips 13–24 OFF | ✓ (default selected) |
| 3 | CH25-36 | CH 25–36, strips 13–24 OFF | |
| 4 | CH37-AUX | CH 37–40 + CH 41–48 (aux inputs), strips 13–24 OFF | |
| 5 | BUSES | BUS 1–16, strips 17–24 OFF | |
| 6 | USER1 | All OFF | |
| 7 | USER2 | All OFF | |

### 12b. Center Section (C) — 6 banks

| Bank | Name | Content |
|------|------|---------|
| 1 | DCA | DCA 1–8, strips 9–16 OFF |
| 2 | MAIN | BUS 17–28 (main+matrix index range) |
| 3 | AUX | CH 41–48 (aux inputs), strips 9–16 OFF |
| 4 | BUSES | BUS 1–16 (all 16 buses) |
| 5 | USER1 | **Custom**: DCA 1–5, BUS 9/11/12/10 (FX buses), strips 10–16 OFF |
| 6 | USER2 | All OFF |

### 12c. Right Section (R) — 7 banks

| Bank | Name | Content | Selected |
|------|------|---------|---------|
| 1 | MAIN | BUS 17–28 | |
| 2 | DCA | DCA 1–8, strips 9–16 OFF | |
| 3 | CH1-40 | All 40 channels | |
| 4 | AUX | CH 41–48, strips 9–16 OFF | |
| 5 | BUSES | BUS 1–16 | |
| 6 | USER1 | **Custom**: CH14, CH13, BUS18, BUS17, strips 5–16 OFF | ✓ (default selected) |
| 7 | USER2 | All OFF | |

**R.USER1 is the default-selected view** (bank 6 is selected). It shows: CH14 (Handheld), CH13 (Computer), BUS18 (?), BUS17 (?). The BUS 17/18 indices in layer context correspond to main outputs (main 1 = index 17, main 2 = index 18 in the Wing's internal indexing).

So R.USER1 shows: **Handheld, Computer, STREAM, HOUSE** — Matthew's personal monitoring and control strip. This is the operator's primary working view.

**C.USER1** shows: DCA 1–5, then FX return buses (Delay/Slap, Reverb/Medium, Reverb/Long, Delay/Repeat). This is a custom "overview" bank.

**Category: Active Configuration** (C.USER1, R.USER1 custom banks)  
**Category: Intentional Infrastructure** (all standard banks)

### 12d. User Layers (`ce_data.user`)

All 16 numbered user layers (1–16) and named layers (user, daw1–4, gpio) are present but have **all-OFF strip assignments with `{mode: 'OFF', name: ''}` objects** rather than truly absent entries. This is the "default populated but empty" state — not genuine user configuration.

**Category: Intentional Infrastructure** (empty user layer scaffold)  
No user layers are actively configured in Base.

---

## Section 13: Safes (`ce_data.safes`)

The Init.snap has different safe field names (some firmware schema difference: `area.COMPACT`, `area.EXTERN`, etc. in Init vs absent in Base). All safe values are empty strings/blank. No meaningful differences.

**Category: Intentional Infrastructure** (blank = nothing safe-protected, which is standard)

---

## Summary by Category

### Intentional Infrastructure

| Area | Items |
|------|-------|
| Channel routing | ch01–04 drums routing (A.2,3,5,4); ch13→LCL.4; ch14→A.32; ch38→A.31; ch40→LCL.1 |
| Channel identity | ch01–04, ch13, ch14, ch38, ch40 names + icons |
| Channel #M8 pre-tag | ch01–24 all carry `#M8` (pre-assigned to Worship mute group) |
| Bus naming | All 16 buses named with coherent structure |
| Bus color coding | Rhythmic=orange, melodic=green, lead=purple, monitor=white, FX=cyan |
| Bus DCA/mgrp tags | Complete tag structure across buses 1–7, 9–12, 13–16 |
| DCA naming | DCAs 1–7 named, mirroring bus groupings |
| Mgrp naming | All 8 mgrps named, paralleling DCA structure |
| Main outputs | HOUSE + STREAM named with 76LA limiters |
| Talkback | CH40 → monitors 13–16 with 20 dB dim |
| IO inputs | Named + gained: Matthew, Lapel, Handheld, Computer (LCL); Kick, Snare, Tom, Overhead, Bass, Lapel, Handheld (A) |
| FX slots | 12 slots loaded (reverbs, delays, pitch, de-essers, body/bass tools) |
| AUX01 | "USB 1/2" named |
| Layer banks | Standard banks (CH1-12, CH13-24, etc.) for all 3 sections |
| CE cfg | Console preferences (lighting, solo, mute behavior) |

### Active Configuration

| Area | Items |
|------|-------|
| Channel processing | ch02 gate+dyn on; ch13+14 RIDE dynamics; ch38 COMP dyn |
| Channel faders | ch01–04 near-unity; ch13 +5.8 dB; ch14+38 ~+0.8 dB |
| ch38 muted | Lapel starts muted in Base |
| ch40 muted | Talkback starts muted |
| Bus dynamics | SBUS/COMP on all 7 submix buses; active mix dynamics |
| Monitor faders | All 4 monitors at ~-20 dB (starting level, not unity) |
| Monitor EQ | bus13+14 have EQ active |
| HOUSE main | EQ + 76LA active; fader -31.5 dB |
| STREAM main | 76LA active |
| RTA settings | SLOW decay, RD25 color, source=65 |
| CE preferences | csctouch=off, muteovr=off, seldblclick=off |
| C.USER1 custom bank | DCA 1–5 + FX buses |
| R.USER1 custom bank (default) | CH14, CH13, MAIN2, MAIN1 |

### Suspected Debris

| Area | Path | Init value | Base value | Reason |
|------|------|-----------|-----------|--------|
| ch15 routing | `ch.15.in.conn` | OFF.1 | LCL.5 | LCL.5 has no config; ch has no name |
| DCA 8 name | `dca.8.name` | (blank) | `DCA\|8` | Pipe separator inconsistent with DCA.9–.16 |
| DCAs 8–16 faders | `dca.8-16.fdr` | (absent) | -inf | Named but at -inf; could just be cleared |
| io.in.A.7 named "JEN" | `io.in.A.7.name` | (blank) | `JEN` | Person name left in physical I/O |
| io.in.PLAY names cleared | `io.in.PLAY.1-2.name` | "2TR" | (blank) | Possibly intentional; may be Init artifact |

### Unknown (Questions for Matthew)

See Questions section below.

---

## Questions for Matthew

### Q1: ch22 at -88.2 dB
**Path**: `ae_data.ch.22.fdr`  
**Observation**: Channel 22 has fader at -88.2 dB (not -inf), tag `#M8`, and routing OFF.1 (disconnected). No name.  
**Question**: Is this intentional? It looks like an accidental fader drag. Should it be at -inf?

### Q2: ch37 — Unnamed channel with A.48 routing and active compression
**Path**: `ae_data.ch.37.*`  
**Observation**: ch37 has fader at +0.9 dB (above unity!), active compressor (COMP, -15.5 dB), input routed to A.48 (unlabeled stage box input), no name, no tags.  
**Questions**: What is A.48? What is this channel for? Should it be named? The above-unity fader is unusual — intentional?

### Q3: mtx01 at +10.0 dB
**Path**: `ae_data.mtx.1.fdr`  
**Observation**: Matrix bus 1 has fader at +10 dB (well above unity). All other matrix buses are at -inf. mtx01 has no name.  
**Question**: What is mtx01 used for? +10 dB is quite high for an output bus.

### Q4: Bus 03 (Inst/House) at -87.3 dB
**Path**: `ae_data.bus.3.fdr`  
**Observation**: The Inst/House submix bus is at -87.3 dB (nearly muted, but not -inf). All other submix buses are at -inf in Base. This means the house instrument mix starts essentially off.  
**Question**: Is this intentional? Or an accidental drag that needs to be set to -inf?

### Q5: Bus 08 "All channels" purpose
**Path**: `ae_data.bus.8.*`  
**Observation**: Bus 8 is named "All channels" with no DCA/mgrp tags, fader -inf, no dynamics. No channels send to it in Base.  
**Question**: What is this bus for? Is it a utility routing bus that team configs populate, or was it a previous idea that's no longer in use?

### Q6: A.8–A.30 systematic +0.5 dB gain
**Path**: `ae_data.io.in.A.8-30.g`  
**Observation**: All 23 unnamed stage box inputs from A.8 to A.30 have +0.5 dB gain (vs 0 in Init). They have no names and no other configuration.  
**Question**: Is this intentional as a base preamp trim, or is this an artifact?

### Q7: io.in.A.7 named "JEN"
**Path**: `ae_data.io.in.A.7.name`  
**Observation**: Stage box input A.7 is named "JEN" with 45.5 dB gain. This is a person name, not an instrument.  
**Question**: Is this a previous team member's channel that should be renamed or cleared? (Note: io.in naming is independent of channel naming — this labels the physical preamp, not the mixer channel.)

### Q8: aux04 at -76.1 dB
**Path**: `ae_data.aux.4.fdr`  
**Observation**: Aux input 4 has fader at -76.1 dB (not -inf). No name.  
**Question**: Is this intentional, or an accidental drag?

### Q9: main03 at -70.1 dB
**Path**: `ae_data.main.3.fdr`  
**Observation**: Main output 3 has fader at -70.1 dB. No name. Main 4 is at -inf. HOUSE (main1) and STREAM (main2) are the two in use.  
**Question**: What is main3 used for? Is the -70.1 dB fader intentional or accidental?

### Q10: ch15 routing to LCL.5
**Path**: `ae_data.ch.15.in.conn`  
**Observation**: ch15 has no name, fader at -inf, but is routed to LCL.5 (local input 5). LCL.5 has no name, gain, or configuration. 
**Question**: Is ch15 intentionally wired to LCL.5 for some purpose, or is this a leftover from a previous config?

### Q11: #M8 pre-tagging boundary
**Observation**: In Base, channels 1–24 all carry `#M8` pre-tags. Channels 25–40 do not. In James.snap, the renderer adds `#M8` to the vocal channels (ch25–30) explicitly.  
**Question**: Is the ch1–24 boundary for `#M8` pre-tagging intentional design (all "standard" slots are pre-tagged), or should it cover all 40 channels? The current split means ch25–40 depend on the renderer for their Worship group membership.

### Q12: Bus naming divergence — Base vs James.snap
**Observation**: Base.snap has updated bus names (Inst/House, Lead/House, etc.) but James.snap still shows old names (Rhythm/House, Melodic/House, etc.). This means the renderer is either not setting bus names, or James.snap was last generated before the bus naming update.  
**Question**: Can you confirm James.snap should be regenerated? (This is more a renderer/workflow issue than a Base.snap issue, but it's discovered here.)

### Q13: DCA 5 "FX" at -16.4 dB in James
**Observation**: DCA 5 "FX" is at -0.2 dB in Base (near unity, correct), but at -16.4 dB in James.snap. This silences all FX return buses for the James team. Is this intentional (James prefers no reverb/delay), or did someone accidentally pull down the FX DCA and not notice because the FX were never prominent in the mix?

---

## Implications for Phase 3

1. **Base is more organized than expected**. The bus/DCA/mgrp structure is coherent and parallels well — buses group by function, DCAs mirror that grouping, mgrps provide hard mute equivalents. This is a solid foundation.

2. **Debris is localized**. The suspicious values (ch22, ch37, aux04, main03, mtx01, bus03) are isolated anomalies, not systemic problems. Cleaning them is low-risk.

3. **The #M8 pre-tagging system is valuable but partial**. Base pre-tags ch01–24, but ch25–40 need renderer-added tags. For Phase 3 complexity levels, any channel that can receive a mute-all needs `#M8`. The current boundary should probably be explicit in the DSL.

4. **DCA 5 ("FX") at -16.4 dB in James is a hidden mix problem**. If the FX return buses are effectively silenced, the FX slots are wasted processing. This should be cleaned up in the James team config.

5. **Custom layer banks are sparse but useful**. C.USER1 (DCA 1–5 + FX buses) and R.USER1 (CH14, CH13, MAIN2, MAIN1) are the only active custom views in Base. These could serve as the model for Phase 3 "beginner view" design.

6. **Bus naming in James.snap is wrong** and should be corrected by regeneration. This confirms the renderer needs bus-name propagation working correctly before Phase 3 work begins.

7. **FX routing pattern**: FX send amounts are all zero in Base — they're a renderer concern, not a Base concern. The FX infrastructure (slots loaded, return buses named) is in place.

8. **Monitor infrastructure is complete in Base**: four monitor buses named, tagged, faders pre-set at ~-20 dB, talkback wired. Individual monitor mixes are a renderer concern, not a Base concern.
