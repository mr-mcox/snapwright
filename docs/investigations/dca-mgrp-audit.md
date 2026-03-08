# Investigation C: DCA & Mute Group Membership Audit

**Date**: 2026-03-08  
**Inputs**: James.snap, Base.snap, Levin.snap, Priscilla.snap, Jen.snap, Kana.snap, Morks.snap, James-old.snap, Init.snap

---

## Executive Summary

The DCA and mute group systems are in a split state: **Base.snap has full, correct membership assignments**, but **all team snapshots have largely lost those assignments** — through a bus renaming migration that was never finished. The practical consequences are:

1. **DCAs 1–4, 6, 7 are phantom faders in every team snap**: Named, with non-zero fader levels, but zero members. They are doing nothing.
2. **DCA 5 "FX" is doing something significant in James and Levin**: At −16.44 dB with FX bus members assigned — actively pulling FX returns down ~16 dB.
3. **Mute groups 1–4 are similarly orphaned**: Present in every snap, custom names, but no members in any team snap.
4. **Mute group 8 "Worship" works correctly**: Channel membership maintained everywhere. It's the only fully functional group system in team snaps.
5. **Monitor mute group (MGRP 7) is broken in most team snaps**: Has no members, so the "kill monitors" button does nothing in James, Levin, Priscilla, Jen, Morks.

Phase 3 requires the renderer to own this system. The membership tables below establish what currently exists, what was intended, and what needs to change.

---

## Tags Encoding — Confirmed

DCA and mute group membership is encoded in the `tags` string field on `ae_data.ch[n]`, `ae_data.bus[n]`, `ae_data.aux[n]`, and `ae_data.main[n]`:

- `#D<n>` = member of DCA n
- `#M<n>` = member of mute group n
- Multiple memberships: comma-separated, e.g., `#D6,#M5,#D1,#M1`
- Factory default (Init.snap): all `tags` fields are empty strings
- Tags are applied to **buses only** for DCA groupings; channels are only tagged for mute groups (specifically #M8)

---

## Section 1: Base.snap — The Designed Group Hierarchy

Base.snap has a fully specified, coherent DCA + mute group system. This is the designed baseline.

### Base.snap Bus Tag Assignments

| Bus | Name | Tags | DCA membership | Mute group membership |
|-----|------|------|----------------|----------------------|
| 1 | DRUMS | `#D6,#M5,#D1,#M1` | DCA1(Rhythm), DCA6(All No L) | MGRP1(Rhythm), MGRP5(Inst All) |
| 2 | BASS | `#D6,#M5,#D1,#M1` | DCA1(Rhythm), DCA6(All No L) | MGRP1(Rhythm), MGRP5(Inst All) |
| 3 | Inst/House | `#D6,#M5,#D2,#M2` | DCA2(Inst B), DCA6(All No L) | MGRP2(Inst B), MGRP5(Inst All) |
| 4 | Inst/Stream | `#D6,#M5,#D2,#M2` | DCA2(Inst B), DCA6(All No L) | MGRP2(Inst B), MGRP5(Inst All) |
| 5 | Back Vox | `#D6,#M6,#D3,#M3` | DCA3(Vox B), DCA6(All No L) | MGRP3(Vox B), MGRP6(Vox All) |
| 6 | Lead/House | `#M5,#D4,#M4,#M6` | DCA4(Leads) | MGRP4(Leads), MGRP5(Inst All), MGRP6(Vox All) |
| 7 | Lead/Stream | `#M5,#D4,#M4,#M6` | DCA4(Leads) | MGRP4(Leads), MGRP5(Inst All), MGRP6(Vox All) |
| 8 | All channels | (none) | — | — |
| 9 | Delay/Slap | `#D5` | DCA5(FX) | — |
| 10 | Delay/Repeat | `#D5` | DCA5(FX) | — |
| 11 | Reverb/Medium | `#D5` | DCA5(FX) | — |
| 12 | Reverb/Long | `#D5` | DCA5(FX) | — |
| 13 | Monitor/1 | `#D7,#M7` | DCA7(Monitors) | MGRP7(Monitors) |
| 14 | Monitor/2 | `#D7,#M7` | DCA7(Monitors) | MGRP7(Monitors) |
| 15 | Monitor/3 | `#D7,#M7` | DCA7(Monitors) | MGRP7(Monitors) |
| 16 | Monitor/4 | `#D7,#M7` | DCA7(Monitors) | MGRP7(Monitors) |

No channels in Base.snap have DCA tags. Channels 1–4, 13–24 have `#M8` (Worship kill-switch).

### Base.snap DCA Faders (design intent)

| DCA | Name | Fader | Members | Scope |
|-----|------|-------|---------|-------|
| 1 | Rhythm | +0.20 dB | bus1, bus2 | Rhythm submixes (DRUMS + BASS) |
| 2 | Inst B | +0.30 dB | bus3, bus4 | Instrument submixes |
| 3 | Vox B | −0.30 dB | bus5 | Back vocals submix |
| 4 | Leads | −0.70 dB | bus6, bus7 | Lead vocal submixes |
| 5 | FX | −0.20 dB | bus9–12 | All FX returns |
| 6 | All No L | −0.70 dB | bus1–5 | Everything except leads |
| 7 | Monitors | +0.10 dB | bus13–16 | All monitor outputs |
| 8–16 | (default) | −144 dB | — | Unused (fully off) |

### Base.snap Mute Group Design

| MGRP | Name | Mute | Members |
|------|------|------|---------|
| 1 | Rhythm | off | bus1, bus2 |
| 2 | Inst B | off | bus3, bus4 |
| 3 | Vox B | off | bus5 |
| 4 | Leads | off | bus6, bus7 |
| 5 | Inst All | off | bus1–4, bus6, bus7 |
| 6 | Vox All | off | bus5, bus6, bus7 |
| 7 | Monitors | off | bus13–16 |
| 8 | Worshp | off | ch1–4, ch13–24 |

---

## Section 2: Team Snapshot State — What Actually Exists

### Team Snap Bus Structure

All team snaps have a **consistent 6-bus mix structure** that differs from Base.snap's 7-bus layout:

| Bus | Team snap name | Base equivalent | Notes |
|-----|---------------|-----------------|-------|
| 1 | DRUMS | bus1 DRUMS | Same |
| 2 | Rhythm/House | bus1 DRUMS + bus3 Inst/House (merged) | House submix for rhythm instruments |
| 3 | Rhythm/Stream | bus3 Inst/Stream equivalent | Stream submix for rhythm |
| 4 | Melodic/House | bus3 Inst/House equivalent | House submix for melodic instruments |
| 5 | Melodic/Stream | bus4 Inst/Stream equivalent | Stream submix for melodic |
| 6 | Vocals | bus6 Lead/House equivalent | Main vocal submix |
| 7 | (unnamed) | bus7 Lead/Stream? | Unknown purpose — see Q3 below |
| 8 | (unnamed) | bus8 All channels | Unknown purpose |
| 9 | Delay/Slap | bus9 | Same |
| 10 | Reverb/Medium | bus10 (or bus11 renamed) | |
| 11 | Reverb/Long | bus11 | |
| 12 | Back Vox / Delay/Rhythm | bus5 Back Vox or bus12 | Varies: James=Back Vox, others=Delay/Rhythm |
| 13–16 | Monitor/1–4 | bus13–16 | Same purpose |

**Key observation**: Base.snap had separate BASS and DRUMS buses; team snaps merged these into bus1 DRUMS. Base had 2 lead vocal buses (House/Stream); team snaps merged these into bus6 Vocals. The migration was a consolidation from 7 to 6 mix buses, but DCA tag assignments weren't updated.

### Team Snap Bus Tag Assignments (James, representative)

| Bus | Name | Tags | DCA membership | Mute group membership |
|-----|------|------|----------------|----------------------|
| 1 | DRUMS | `#M5` | — | MGRP5(Inst All) |
| 2 | Rhythm/House | `#M5` | — | MGRP5(Inst All) |
| 3 | Rhythm/Stream | `#M5` | — | MGRP5(Inst All) |
| 4 | Melodic/House | `#M5` | — | MGRP5(Inst All) |
| 5 | Melodic/Stream | `#M6` | — | MGRP6(Vox All) |
| 6 | Vocals | `#M5,#M6` | — | MGRP5(Inst All), MGRP6(Vox All) |
| 7 | (unnamed) | `#M5,#M6` | — | MGRP5(Inst All), MGRP6(Vox All) |
| 9 | Delay/Slap | `#D5` | DCA5(FX) | — |
| 10 | Reverb/Medium | `#D5` | DCA5(FX) | — |
| 11 | Reverb/Long | `#D5` | DCA5(FX) | — |
| 12 | Back Vox | `#D5` | DCA5(FX) | — |
| 13–16 | Monitor/1–4 | (none) | — | — |

Notable differences from Base.snap:
- Buses 1–7 lost all DCA tags (`#D1` through `#D6`)
- Buses 1–7 lost individual mute group tags (`#M1` through `#M4`)
- Monitor buses lost both `#D7` and `#M7`
- FX buses 9–12 retained `#D5` (partially — James only; other team snaps lost even this)

### Team Snap DCA Faders (across all snaps)

All DCA names are identical across all team snaps. Faders are also identical except DCA 5:

| DCA | Name | James | Levin | Priscilla | Jen | Kana | Morks |
|-----|------|-------|-------|-----------|-----|------|-------|
| 1 | Rhythm | +0.20 | +0.20 | +0.20 | +0.20 | +0.20 | +0.20 |
| 2 | Inst B | +0.30 | +0.30 | +0.30 | +0.30 | +0.30 | +0.30 |
| 3 | Vox B | −0.30 | −0.30 | −0.30 | −0.30 | −0.30 | −0.30 |
| 4 | Leads | −0.70 | −0.70 | −0.70 | −0.70 | −0.70 | −0.70 |
| **5** | **FX** | **−16.44** | **−16.44** | −0.20 | −0.20 | −0.20 | −0.20 |
| 6 | All No L | −0.70 | −0.70 | −0.70 | −0.70 | −0.70 | −0.70 |
| 7 | Monitors | +0.10 | +0.10 | +0.10 | +0.10 | +0.10 | +0.10 |
| 8–16 | (default) | −144 | −144 | −144 | −144 | −144 | −144 |

**DCA 5 in James/Levin**: At −16.44 dB with FX buses assigned — pulling all FX returns down ~16 dB. `james-starter-2025-06-01.snap` (older James) shows DCA5 at −4.75 dB, suggesting this value drifted over time rather than being a stable setting.

### Team Snap Mute Group States

| MGRP | Name | James | Levin | Priscilla | Jen | Kana | Morks |
|------|------|-------|-------|-----------|-----|------|-------|
| 1 | Rhythm | off, 0 members | off, 0 | off, 0 | off, 0 | off, 0 | off, 0 |
| 2 | Inst B | off, 0 members | off, 0 | off, 0 | off, 0 | off, 0 | off, 0 |
| 3 | Vox B | off, 0 members | off, 0 | off, 0 | off, 0 | off, 0 | off, 0 |
| 4 | Leads | off, 0 members | off, 0 | **MUTED**, 0 | off, 0 | off, 0 | off, 0 |
| 5 | Inst All | off, 6 buses | off, 6 | off, 6 | off, 6 | off, 6 | off, 6 |
| 6 | Vox All | off, 3 buses | off, 3 | off, 3 | off, 3 | off, 2 | off, 3 |
| 7 | Monitors | off, **0 members** | off, 0 | off, 0 | off, 0 | off, 4 | off, 0 |
| 8 | Worshp | **MUTED** | **MUTED** | **MUTED** | **MUTED** | off | off |

Mute group 5 (Inst All) and 6 (Vox All) **do** have members in team snaps and are functional, though their semantics have shifted with the new bus naming.

---

## Section 3: Impact Assessment

### Critical: DCA 5 "FX" at −16.44 dB (James, Levin)

**What it does**: In James.snap, buses 9–12 (Delay/Slap, Reverb/Medium, Reverb/Long, Back Vox) all carry `#D5`. DCA 5 is at −16.44 dB. Result: all FX returns are scaled down ~16 dB relative to their bus faders.

**Context**: The FX bus faders in James are near unity (0, −0.10, −0.55, −144). The DCA is what's actually pulling them down. Any operator adjusting the bus faders without knowing about the DCA offset would be confused by the effective level.

**Evidence of drift**: Older James snapshot (2025-06-01) shows DCA5 at −4.75 dB, not −16.44 dB. This is a session-state capture, not an intentional design value. **Matthew should confirm whether −16.44 dB is intentional or an artifact**.

**Levin has the same DCA5 fader level (−16.44) but the FX buses lost their `#D5` tags**, so in Levin the DCA has no effect. Levin appears to have been derived from James at a time when the tags were different.

### Active But Stale: DCAs 1–4, 6, 7 with Non-Unity Faders and Zero Members

These DCAs have non-zero fader offsets (+0.20 to −0.70 dB) but no members in any team snap. They are completely inert — doing nothing but creating confusion. The fader offsets are carried in the snapshot and will affect any buses assigned to them in future, which is a latent risk if someone adds tags manually on the console.

The consistent fader values across all snaps (all inherited from wherever they were set) suggests these were intentional calibration values at the time of the original Base.snap, but the member assignments were lost when the bus structure changed.

### Monitor Mute Group Broken (James, Levin, Priscilla, Jen, Morks)

MGRP 7 "Monitors" has no members in these snaps. The "kill monitors" button on the console does nothing. Only Kana's snap has monitor membership (via #M7 only — no DCA7 tag). This is a safety/usability issue: an operator expecting to mute all monitors at once cannot.

### Priscilla: MGRP 4 (Leads) Saved as MUTED

MGRP 4 has no members in any team snap, so this mute is inert. But it's a snapshot state artifact — likely saved mid-session when a button was activated. Worth noting because Phase 3 logic around mute states needs to handle this correctly.

### Mute Groups 5 and 6 — Functional but Semantically Shifted

In Base.snap, MGRP 5 (Inst All) covered buses 1–4, 6, 7 (instruments and leads). In team snaps it covers buses 1–4, 6, 7 but those buses now represent different things (e.g., bus6 is now unified "Vocals", not "Lead/House"). The mute group still works — pressing it will silence those buses — but the label "Inst All" is slightly misleading since bus6 (Vocals) is a member but is a vocal bus, not an instrument bus.

### MGRP 8 "Worshp" — The Kill-Switch — Works Correctly

Every active channel in team snaps has `#M8`. This is the one group that was fully maintained through the migration. Current mute status:
- James, Levin, Priscilla, Jen: MUTED (these snapshots were saved with the worship group silenced — normal for non-worship periods)
- Kana, Morks: not muted (saved ready to play)
- Base: not muted

---

## Section 4: Cross-Snap Comparison Summary

### DCA Member Presence by Snap

| DCA | Base | James | Levin | Priscilla | Jen | Kana | Morks |
|-----|------|-------|-------|-----------|-----|------|-------|
| 1 Rhythm | ✅ bus1+2 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 |
| 2 Inst B | ✅ bus3+4 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 |
| 3 Vox B | ✅ bus5 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 |
| 4 Leads | ✅ bus6+7 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 |
| 5 FX | ✅ bus9–12 | ✅ bus9–12 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 |
| 6 All No L | ✅ bus1–5 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 |
| 7 Monitors | ✅ bus13–16 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 |

### Mute Group Member Presence by Snap

| MGRP | Base | James | Levin | Priscilla | Jen | Kana | Morks |
|------|------|-------|-------|-----------|-----|------|-------|
| 1 Rhythm | ✅ bus1+2 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 |
| 2 Inst B | ✅ bus3+4 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 |
| 3 Vox B | ✅ bus5 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 |
| 4 Leads | ✅ bus6+7 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 |
| 5 Inst All | ✅ 6 buses | ⚠️ 6 buses (shifted) | ⚠️ 6 | ⚠️ 6 | ⚠️ 6 | ⚠️ 6 | ⚠️ 6 |
| 6 Vox All | ✅ 3 buses | ⚠️ 3 buses (shifted) | ⚠️ 3 | ⚠️ 3 | ⚠️ 3 | ⚠️ 2 | ⚠️ 3 |
| 7 Monitors | ✅ bus13–16 | ❌ 0 | ❌ 0 | ❌ 0 | ❌ 0 | ⚠️ 4 buses (no DCA) | ❌ 0 |
| 8 Worshp | ✅ ch1–24 | ✅ ch1–8,13–16,25–30 | ✅ | ✅ | ✅ | ✅ | ✅ |

Legend: ✅ complete, ⚠️ partial/shifted, ❌ missing

---

## Section 5: Proposed Group Structure for Phase 3

Based on the current team snap bus layout, here's a proposed DCA/mgrp restructure that the renderer should own:

### Current Bus Layout (team snaps)

```
Bus 1:  DRUMS          (rhythm percussion)
Bus 2:  Rhythm/House   (rhythm instruments, house)
Bus 3:  Rhythm/Stream  (rhythm instruments, stream)
Bus 4:  Melodic/House  (melodic instruments, house)
Bus 5:  Melodic/Stream (melodic instruments, stream)
Bus 6:  Vocals         (all vocals)
Bus 7:  (unknown)
Bus 8:  (unknown)
Bus 9:  Delay/Slap     (FX return)
Bus 10: Reverb/Medium  (FX return)
Bus 11: Reverb/Long    (FX return)
Bus 12: Back Vox / Delay/Rhythm (varies by team)
Bus 13-16: Monitors
```

### Proposed DCA Redesign (keep existing slot numbers for console surface continuity)

| DCA | Name | Proposed members | Fader | Notes |
|-----|------|-----------------|-------|-------|
| 1 | Rhythm | bus1 (DRUMS) + bus2/3 (Rhythm H/S) | 0 dB | Rhythm submix master |
| 2 | Melodic | bus4 (Mel/House) + bus5 (Mel/Stream) | 0 dB | Melodic instrument submix master |
| 3 | Vocals | bus6 (Vocals) | 0 dB | Vocal submix master |
| 4 | (open) | — | — | Available for team-specific use |
| 5 | FX | bus9–12 | 0 dB | FX returns master |
| 6 | All | bus1–6 | 0 dB | Everything except monitors |
| 7 | Monitors | bus13–16 | 0 dB | Monitor master |
| 8–16 | — | — | −144 | Unused |

This maps cleanly to a "beginner view" custom user layer with 5 faders: Rhythm, Melodic, Vocals, FX, Monitors.

### Proposed Mute Group Redesign

| MGRP | Name | Proposed members | Notes |
|------|------|-----------------|-------|
| 1 | Rhythm | bus1–3 | Mirrors DCA 1 |
| 2 | Melodic | bus4–5 | Mirrors DCA 2 |
| 3 | Vocals | bus6 | Mirrors DCA 3 |
| 4 | (open) | — | Available per-team |
| 5 | Inst All | bus1–6 | Kill all instruments inc vocals |
| 6 | Vox All | bus6 | May simplify to just vocals if inst/vox distinction not needed |
| 7 | Monitors | bus13–16 | Kill all monitors |
| 8 | Worshp | all active channels | Kill-switch (keep as-is) |

**Note**: Whether MGRP 5 and 6 should map to current member assignments or be rationalized is a question for Matthew (see Q5).

---

## Section 6: Implications for Phase 3 Renderer

### What the renderer needs to add

1. **`tags` field rendering on buses**: The renderer must be able to write DCA and mute group membership tags onto buses. Format: comma-separated `#D<n>` and `#M<n>` tokens.

2. **`tags` field rendering on channels**: Already partially handled — channels get `#M8` from the Worship group. The renderer needs to generalize this to support arbitrary mute group membership per channel.

3. **DCA config rendering in `ae_data.dca`**: Name, fader, and mute state for DCAs 1–n.

4. **Mute group config rendering in `ae_data.mgrp`**: Name and default mute state.

5. **DSL vocabulary for group membership**: The DSL needs a way to declare which buses/channels belong to which groups. This can live in the assembly (bus-level groups) or in a shared infrastructure config.

### Key design question: where does group membership live in the DSL?

Option A: In the assembly — each assembly declares its DCA/mgrp topology  
Option B: In infrastructure config — groups are a shared structure independent of teams (since bus1–7 are the same across all teams)  
Option C: Hybrid — infrastructure declares the group structure, assembly can override per-team needs

The fact that buses 1–7 are consistent across all team snaps strongly suggests Option B or C. The group structure is infrastructure, not team-specific.

### Tags are cumulative and order matters

In Base.snap, `bus1` has `#D6,#M5,#D1,#M1` — multiple DCA and mgrp memberships. The renderer needs to accumulate all memberships into a single comma-separated string. The order in Base.snap appears to follow: DCA6 first (the "parent" group), then MGRP5, then the individual DCA, then the individual MGRP. Whether Wing cares about ordering is unknown; safer to be consistent.

---

## Questions for Matthew

**Q1: Is DCA 5 "FX" at −16.44 dB in James intentional?**

The older James backup (2025-06-01) shows DCA5 at −4.75 dB. The current James.snap has it at −16.44 dB. This looks like a live-session artifact that got saved. If so, the "correct" value is whatever you use in practice — should this be 0 dB (with individual bus faders doing the scaling), or do you actively use the DCA to pull FX down globally?

**Q2: What are buses 7 and 8 actually used for?**

Bus 7 is unnamed in all team snaps but carries `#M5,#M6` tags (member of Inst All and Vox All). Bus 8 is unnamed and has no tags. What signals route to these buses, if anything? In Base.snap, bus7 was "Lead/Stream" and bus8 was "All channels". Are either of these active in current team setups?

**Q3: James has bus12 = "Back Vox" with `#D5`; all other team snaps have bus12 = "Delay/Rhythm" with no tags. Which is correct for James? Is bus12 a FX return or a vocal submix?**

Based on channel sends in James.snap, `priscilla-vox`, `anna-vox`, and `yolaine-vox` all send to bus12. The bus fader is at −144 dB. Is "Back Vox" on bus12 an intentional setup that's currently bypassed (fader off) or a naming artifact?

**Q4: Should DCAs 1–4 and 6–7 be redesigned to match the current bus structure?**

The original Base.snap design (DRUMS+BASS → DCA1, etc.) doesn't map to the current team snap bus layout. A redesign is needed before Phase 3 can deliver meaningful "simplified mixing view" DCAs. The proposal in Section 5 above is a starting point — does that match your intent for the beginner operator experience?

**Q5: What should mute groups 1–4 do in the new design?**

They have custom names (Rhythm, Inst B, Vox B, Leads) but zero members in all team snaps. Options:
- (a) Keep names, assign members based on proposed redesign
- (b) Rename + reassign to match new bus structure (e.g., MGRP1=Rhythm, MGRP2=Melodic, MGRP3=Vocals)
- (c) Repurpose some as team-specific groups

**Q6: Priscilla snap has MGRP 4 (Leads) saved as muted with no members. Was that intentional?**

It's currently inert since no buses are assigned to MGRP 4. But when members are added, loading that snapshot would activate the mute group. This should be reset to "off" when the snap is regenerated.

**Q7: Monitor buses should have DCA 7 and MGRP 7 membership. Kana has the mute group but not the DCA; most others have neither. Should the renderer restore this consistently?**

Monitor DCA 7 at +0.10 dB with members would mean loading any generated snapshot would apply a +0.10 dB nudge to monitor buses. Is that intentional? If the DCA fader is going to 0 dB, that's fine. If you want the traditional +0.10 carry-over, that's fine too — just needs to be a deliberate choice.

---

## Appendix: Full Tag Inventory

### James.snap — All Sources with Tags

| Source | Name | Tags |
|--------|------|------|
| ch1 | Kick | `#M8` |
| ch2 | Snare | `#M8` |
| ch3 | Tom | `#M8` |
| ch4 | Overhead | `#M8` |
| ch5 | Bass | `#M8` |
| ch6 | Conga 1 | `#M8` |
| ch7 | Conga 2 | `#M8` |
| ch8 | Bongos | `#M8` |
| ch13 | James | `#M8` |
| ch14 | Flute | `#M8` |
| ch15 | Piano | `#M8` |
| ch16 | Violin | `#M8` |
| ch25 | James | `#M8` |
| ch26 | Pricilla | `#M8` |
| ch27 | Anna | `#M8` |
| ch28 | Yolaine | `#M8` |
| ch29 | Kana | `#M8` |
| ch30 | Elizabeth | `#M8` |
| bus1 | DRUMS | `#M5` |
| bus2 | Rhythm/House | `#M5` |
| bus3 | Rhythm/Stream | `#M5` |
| bus4 | Melodic/House | `#M5` |
| bus5 | Melodic/Stream | `#M6` |
| bus6 | Vocals | `#M5,#M6` |
| bus7 | (unnamed) | `#M5,#M6` |
| bus9 | Delay/Slap | `#D5` |
| bus10 | Reverb/Medium | `#D5` |
| bus11 | Reverb/Long | `#D5` |
| bus12 | Back Vox | `#D5` |

### Base.snap — All Sources with Tags

| Source | Name | Tags |
|--------|------|------|
| ch1 | Kick | `#M8` |
| ch2 | Snare | `#M8` |
| ch3 | Tom | `#M8` |
| ch4 | Overhead | `#M8` |
| ch13 | Computer | `#M8` |
| ch14 | Handheld | `#M8` |
| ch15–24 | (unnamed) | `#M8` |
| bus1 | DRUMS | `#D6,#M5,#D1,#M1` |
| bus2 | BASS | `#D6,#M5,#D1,#M1` |
| bus3 | Inst/House | `#D6,#M5,#D2,#M2` |
| bus4 | Inst/Stream | `#D6,#M5,#D2,#M2` |
| bus5 | Back Vox | `#D6,#M6,#D3,#M3` |
| bus6 | Lead/House | `#M5,#D4,#M4,#M6` |
| bus7 | Lead/Stream | `#M5,#D4,#M4,#M6` |
| bus9 | Delay/Slap | `#D5` |
| bus10 | Delay/Repeat | `#D5` |
| bus11 | Reverb/Medium | `#D5` |
| bus12 | Reverb/Long | `#D5` |
| bus13 | Monitor/1 | `#D7,#M7` |
| bus14 | Monitor/2 | `#D7,#M7` |
| bus15 | Monitor/3 | `#D7,#M7` |
| bus16 | Monitor/4 | `#D7,#M7` |
