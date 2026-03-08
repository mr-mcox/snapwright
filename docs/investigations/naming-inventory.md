# Investigation E: Labeling & Naming Inventory

**Status**: Complete  
**Input files**: `James.snap`, `Base.snap`, `Init.snap`, all Sunday Starters, DSL assembly + musician files  
**Output**: This document

---

## Summary

Every `name` field across `ae_data` sections has been catalogued, cross-referenced across six team snapshots, Base.snap, Init.snap, and the DSL. The core finding is a **two-layer naming problem**: Base.snap contains stale channel and bus names that don't match reality on the Wing, *and* the renderer doesn't set bus display names at all, so every rendered snapshot ships with wrong bus labels. Several infrastructure channels are completely invisible to the DSL yet appear consistently in all six team snapshots.

---

## Method

1. Extracted `name` fields from `ae_data.ch` (1-40), `bus` (1-16), `dca` (1-16), `mgrp` (1-8), `main` (1-4), `mtx` (1-8), `aux` (1-8), `fx` (1-16)
2. Compared across Init.snap, Base.snap, and six Sunday Starters: James, Levin, Jen, Priscilla, Morks, Kana
3. Cross-referenced with DSL musician files and assembly.yaml files for both James and Priscilla teams
4. Identified which names come from: Init (factory), Base.snap (infrastructure config), DSL rendering, or manual console edits
5. Checked what the current renderer actually outputs vs what the Sunday Starters show

---

## 1. Channels (ch 1-40)

### 1.1 Provenance classification

Each channel classified by naming consistency across all six Sunday Starters:

| Class | Meaning |
|-------|---------|
| **INFRA** | Same non-empty name in all 6 teams |
| **SEMI-INFRA** | Same name in teams that use it, empty elsewhere |
| **TEAM-SPECIFIC** | Different names across teams |
| **UNUSED** | Empty in all teams |

#### Infrastructure channels (consistent across all teams)

| Ch | Name | In Base.snap | In DSL | Notes |
|----|------|-------------|--------|-------|
| 1 | Kick | ✅ 'Kick' | ✅ DSL-rendered | Fully managed |
| 2 | Snare | ✅ 'Snare' | ✅ DSL-rendered | Fully managed |
| 3 | Tom | ✅ 'Tom' | ✅ DSL-rendered | Fully managed |
| 4 | Overhead | ✅ 'Overhead' | ✅ DSL-rendered | Fully managed |
| 5 | Bass | ❌ (empty) | ✅ DSL-rendered | Base gap |
| 15 | Piano | ❌ (empty) | ⚠️ Priscilla DSL only | James doesn't list it |
| 37 | Handheld | ❌ (empty) | ✅ DSL-rendered | Both teams list it |
| 38 | Headset | ⚠️ 'Lapel' (STALE) | ✅ DSL-rendered | Base name is wrong |
| 39 | Computer | ❌ (empty) | ❌ Not in any DSL | De facto infra, invisible to renderer |
| 40 | TALKBACK | ✅ 'TALKBACK' | ❌ Not in any DSL | Base correct, renderer doesn't touch it |

#### Semi-infrastructure channels (named consistently where used, empty elsewhere)

| Ch | Name | Teams with name | In Base | In DSL | Notes |
|----|------|----------------|---------|--------|-------|
| 36 | Oscillator | 5/6 teams (all except Jen) | ❌ | ❌ | Quasi-infrastructure; not rendered |
| 7 | Conga 2 | James only | ❌ | ✅ James DSL | Single-team instrument |
| 8 | Bongos | James only | ❌ | ✅ James DSL | Single-team instrument |
| 18 | Sanctuary | James only | ❌ | ❌ | Not in DSL; manual-only |
| 30 | Elizabeth | James only | ❌ | ❌ | Not in DSL; manual-only |

#### Team-specific channels (instrument and vocalist banks)

| Ch | Description | Sample names |
|----|-------------|-------------|
| 6 | Instrument slot A (James=Conga 1, Levin=Violin, others=empty) | Varies |
| 13 | Primary instrument (James=James/guitar, Levin=Guitar, Jen=Acoustic, Priscilla=Flute, Morks=Guitar) | Varies |
| 14 | Secondary instrument (James=Flute, Jen=Electric Guitar, Morks=Roudy, others=empty) | Varies |
| 16 | Tertiary instrument (James=Violin, Levin=Violin, Jen=Keys, Priscilla=Guitar) | Varies |
| 25 | Vocalist 1 (James=James, Levin=James, Jen=JEN, Morks=Roudy) | Varies |
| 26 | Vocalist 2 (James=Pricilla, Levin=James, Jen=BETH, Morks=Roudy) | Varies |
| 27 | Vocalist 3 (James=Anna, Levin=James, Jen=NEENAH, Morks=Roudy) | Varies |
| 28 | Vocalist 4 (James=Yolaine, Levin=James, Jen=Marin, Morks=Roudy) | Varies |
| 29 | Area mic/guest (James=Kana, Jen=Peace, Priscilla=area mic, Kana=area mic) | Varies |

#### Unused channels (empty in all teams)

Channels 9-12, 17, 19-24, 31-35 have no names in any snapshot.

### 1.2 Base.snap channel name staleness

Base.snap contains only 8 channel names. Three are stale:

| Ch | Base.snap value | Reality (Sunday Starters) | Status |
|----|-----------------|--------------------------|--------|
| 1 | Kick | Kick | ✅ Current |
| 2 | Snare | Snare | ✅ Current |
| 3 | Tom | Tom | ✅ Current |
| 4 | Overhead | Overhead | ✅ Current |
| 13 | **Computer** | Team-specific instruments (James/Guitar/Acoustic/Flute) | ❌ Stale — Computer moved to ch 39 |
| 14 | **Handheld** | Team-specific instruments (Flute/Electric Guitar/etc.) | ❌ Stale — Handheld moved to ch 37 |
| 38 | **Lapel** | Headset (all teams) | ❌ Stale — equipment renamed |
| 40 | TALKBACK | TALKBACK | ✅ Current |

**Impact**: When the renderer outputs a snapshot, channels 13 and 14 will show 'Computer' and 'Handheld' as their base defaults for any channel not overridden by the DSL. For James/Priscilla, those channels are in the assembly so they get the right names. But Kana team has no ch 13 in DSL — their ch 13 will inherit Base's 'Computer' label.

### 1.3 DSL name coverage (James team rendered vs Sunday Starter)

The renderer accurately matches all channel names for DSL-managed channels:

| Ch | DSL musician | DSL name | Snap name | Match? |
|----|-------------|----------|-----------|--------|
| 1-8 | kick/snare/tom/overhead/bass/conga-1/conga-2/bongos | Correct | Correct | ✅ |
| 13 | james-guitar | James | James | ✅ |
| 14 | flute | Flute | Flute | ✅ |
| 16 | violin | Violin | Violin | ✅ |
| 25 | james-vox | James | James | ✅ |
| 26 | priscilla-vox | Pricilla | Pricilla | ✅ (but see spelling note below) |
| 27 | anna-vox | Anna | Anna | ✅ |
| 28 | yolaine-vox | Yolaine | Yolaine | ✅ |
| 37 | handheld | Handheld | Handheld | ✅ |
| 38 | headset | Headset | Headset | ✅ |

**Channels not in DSL that appear in Sunday Starter (James)**:

| Ch | Snap name | Source |
|----|-----------|--------|
| 15 | Piano | Manual (set on Wing at some point) |
| 18 | Sanctuary | Manual (James only) |
| 29 | Kana | Manual (James only) |
| 30 | Elizabeth | Manual (James only) |
| 36 | Oscillator | Manual |
| 39 | Computer | Manual |

These are not rendered — they exist only because they were manually entered on the Wing and the Sunday Starter was saved afterward.

---

## 2. Buses (bus 1-16)

### 2.1 Critical finding: bus names are wrong in every rendered snapshot

The renderer **does not set bus display names**. It uses the DSL logical name (`inst_house`, `vocals`) only for routing — the `name` field in `ae_data.bus` is never written. Rendered snapshots inherit bus names from Base.snap via `snap_template()`.

Base.snap bus names are from an **older naming scheme** that was manually updated on the Wing but never updated in Base. Every DSL-rendered snapshot ships with wrong bus names:

| Bus | Base.snap / Rendered | Sunday Starters | DSL logical name | Notes |
|-----|---------------------|-----------------|-----------------|-------|
| 1 | DRUMS | DRUMS | drums | ✅ Matches |
| 2 | **BASS** | Rhythm/House | inst_house | ❌ Wrong |
| 3 | **Inst/House** | Rhythm/Stream | inst_stream | ❌ Wrong |
| 4 | **Inst/Stream** | Melodic/House | (not in James DSL) | ❌ Wrong |
| 5 | **Back Vox** | Melodic/Stream | (not in James DSL) | ❌ Wrong |
| 6 | **Lead/House** | Vocals | vocals | ❌ Wrong |
| 7 | **Lead/Stream** | (empty) | (not in DSL) | ❌ Wrong |
| 8 | **All channels** | (empty) | stage_feed | ❌ Wrong |
| 9 | Delay/Slap | Delay/Slap | delay_slap | ✅ Matches |
| 10 | **Delay/Repeat** | Reverb/Medium | reverb_medium | ❌ Wrong |
| 11 | **Reverb/Medium** | Reverb/Long | reverb_long | ❌ Wrong |
| 12 | **Reverb/Long** | Delay/Rhythm (5 teams) / Back Vox (James only) | back_vox / delay_rhythm | ❌ Wrong (team-specific) |
| 13 | Monitor/1 | Monitor/1 | monitor_1 | ✅ Matches |
| 14 | Monitor/2 | Monitor/2 | monitor_2 | ✅ Matches |
| 15 | Monitor/3 | Monitor/3 | monitor_3 | ✅ Matches |
| 16 | Monitor/4 | Monitor/4 | monitor_4 | ✅ Matches |

**8 of 12 active buses have wrong display names in rendered output.**

### 2.2 Bus name provenance

All six Sunday Starters share the same bus names for buses 1-11 and 13-16. This is consistent infrastructure — the names were manually updated at some point and saved into all team snapshots. Bus 12 is the only team-specific bus name: James uses it for 'Back Vox' (DSL: `back_vox`), while all five other teams use 'Delay/Rhythm' (DSL: `delay_rhythm`). James is the outlier here.

The "correct" display names aligned with the DSL logical names are:

| Bus | Correct display name | DSL logical name |
|-----|---------------------|-----------------|
| 1 | DRUMS | drums |
| 2 | Rhythm/House (or Inst/House) | inst_house |
| 3 | Rhythm/Stream (or Inst/Stream) | inst_stream |
| 4 | Melodic/House | (unnamed in current DSL) |
| 5 | Melodic/Stream | (unnamed in current DSL) |
| 6 | Vocals | vocals |
| 7 | (empty) | (unused in both teams) |
| 8 | (empty) | stage_feed (James only) |
| 9 | Delay/Slap | delay_slap |
| 10 | Reverb/Medium | reverb_medium |
| 11 | Reverb/Long | reverb_long |
| 12 | Back Vox / Delay/Rhythm | back_vox / delay_rhythm |
| 13-16 | Monitor/1-4 | monitor_1-4 |

Note: Buses 4-5 (Melodic/House, Melodic/Stream) appear in all Sunday Starters but are not in any DSL assembly. The DSL consolidated these into `inst_house` and `inst_stream` (buses 2-3). Whether buses 4-5 still carry signal needs to be confirmed.

---

## 3. DCAs (dca 1-16)

### 3.1 Name inventory

All DCA names are set in Base.snap and consistent across all six Sunday Starters. Init.snap has empty DCA names:

| DCA | Name | Provenance | Notes |
|-----|------|-----------|-------|
| 1 | Rhythm | Base.snap | Used |
| 2 | Inst B | Base.snap | Used |
| 3 | Vox B | Base.snap | Used |
| 4 | Leads | Base.snap | Used |
| 5 | FX | Base.snap | Used (fdr at -16.4 dB — see Investigation C) |
| 6 | All No L | Base.snap | Used |
| 7 | Monitors | Base.snap | Used |
| 8 | **DCA\|8** | Base.snap | Generic — unused/undefined |
| 9 | DCA.9 | Base.snap | Generic — unused/undefined |
| 10 | DCA.10 | Base.snap | Generic — unused/undefined |
| 11 | DCA.11 | Base.snap | Generic — unused/undefined |
| 12 | DCA.12 | Base.snap | Generic — unused/undefined |
| 13 | DCA.13 | Base.snap | Generic — unused/undefined |
| 14 | DCA.14 | Base.snap | Generic — unused/undefined |
| 15 | DCA.15 | Base.snap | Generic — unused/undefined |
| 16 | DCA.16 | Base.snap | Generic — unused/undefined |

The renderer does not touch any DCA names. They all come from Base.snap via `snap_template()`. No team overrides them.

Note the **inconsistent formatting** in DCA 8: `DCA|8` (pipe) vs `DCA.9` through `DCA.16` (period). This is likely an artefact from how Base.snap was constructed and should be cleaned up to `DCA.8`.

---

## 4. Mute Groups (mgrp 1-8)

### 4.1 Name inventory

All mgrp names come from Base.snap. Init.snap has generic names (`MGRP.1` through `MGRP.8`):

| MGRP | Init name | Base/Snap name | Notes |
|------|-----------|---------------|-------|
| 1 | MGRP.1 | Rhythm | Consistent all teams |
| 2 | MGRP.2 | Inst B | Consistent all teams |
| 3 | MGRP.3 | Vox B | Consistent all teams |
| 4 | MGRP.4 | Leads | Consistent all teams |
| 5 | MGRP.5 | Inst All | Consistent all teams |
| 6 | MGRP.6 | Vox All | Consistent all teams |
| 7 | MGRP.7 | Monitors | Consistent all teams |
| 8 | MGRP.8 | **Worshp** | Consistent all teams — truncated |

`Worshp` is a truncated form of "Worship" — likely hitting the Wing's name character limit. This is in active use (`#M8` tags on all active channels). The truncation appears intentional or unavoidable.

The renderer does not touch mgrp names. No team overrides them.

---

## 5. Main Outputs (main 1-4)

| Main | Base.snap name | All Sunday Starters | Notes |
|------|---------------|-------------------|-------|
| 1 | HOUSE | HOUSE | ✅ Consistent, correct |
| 2 | STREAM | STREAM | ✅ Consistent, correct |
| 3 | (empty) | (empty) | Unused |
| 4 | (empty) | (empty) | Unused |

Set in Base.snap, inherited by all teams. The renderer references `main` only via `ch["main"]["1"]["on"]` (the channel's send to main 1). The main outputs themselves are not configured by the renderer. These names are correct and stable.

---

## 6. Matrix Buses (mtx 1-8)

### 6.1 Name inventory

Matrix buses have **no names in Base.snap or Init.snap**. They appear only in manually-saved Sunday Starters:

| MTX | Base | James | Levin | Jen | Priscilla | Morks | Kana |
|-----|------|-------|-------|-----|-----------|-------|------|
| 1 | (empty) | Back Vox | Back Vox | — | Back Vox | — | — |
| 2 | (empty) | Guitars | Guitars | — | Guitars | — | — |
| 3 | (empty) | Other Inst | Other Inst | — | Other Inst | — | — |
| 4 | (empty) | Drum Set | Drum Set | — | Drum Set | — | — |
| 5 | (empty) | Congas | Congas | — | Congas | — | — |
| 6 | (empty) | Wireless | Wireless | — | Wireless | — | — |
| 7 | (empty) | — | — | — | — | — | — |
| 8 | (empty) | — | — | — | — | — | — |

James, Levin, and Priscilla show the same six matrix bus names. Jen, Morks, and Kana have no matrix bus names. The renderer does not touch matrix bus names. A DSL-rendered snapshot would have unnamed matrix buses.

---

## 7. Aux Inputs (aux 1-8)

| Aux | Base.snap | All Sunday Starters |
|-----|----------|-------------------|
| 1 | USB 1/2 | USB 1/2 |
| 2-8 | (empty) | (empty) |

Consistent everywhere. Renderer doesn't touch aux names.

---

## 8. FX Slots (fx 1-16)

FX slots have no `name` field in any snapshot (Init, Base, or Sunday Starters). The `fx` section is present in `ae_data` but contains effect configuration, not a user-visible name. Not applicable to this investigation.

---

## 9. Cross-Reference: Renderer Coverage

Summary of which names the renderer currently sets vs inherits from Base.snap:

| Section | Renderer sets names? | Source if not rendered | Gap |
|---------|---------------------|----------------------|-----|
| ch (DSL-managed) | ✅ Yes (via musician DSL) | — | None |
| ch (non-DSL channels) | ❌ No | Base.snap or empty | Infrastructure channels unmanaged |
| bus | ❌ No | Base.snap (stale) | **All bus names wrong in rendered output** |
| dca | ❌ No | Base.snap | Phase 3 needs this for DCA grouping |
| mgrp | ❌ No | Base.snap | Phase 3 needs this if mgrp rationalized |
| main | ❌ No | Base.snap (correct) | No gap — names are stable |
| mtx | ❌ No | Empty | Named only in manually-saved snaps |
| aux | ❌ No | Base.snap (correct) | No gap |

---

## 10. Inconsistencies Found

### Critical
1. **Bus names in rendered output are wrong** — 8 of 12 active buses render with Base.snap's stale naming scheme ('BASS', 'Inst/House', 'Lead/House', 'Delay/Repeat', 'Reverb/Medium', 'Reverb/Long', 'Lead/Stream', 'All channels'). The Sunday Starters show the current naming (Rhythm/House, Vocals, etc.) but rendered snapshots don't. An operator loading a rendered snapshot sees a completely different bus layout on the Wing compared to what they're used to.

### Stale Base.snap
2. **ch 13: 'Computer' in Base** — Computer was moved to ch 39 across all teams. Base.snap ch 13 still says 'Computer'. The renderer overwrites this for DSL-managed teams, but teams that don't include ch 13 in their assembly will see stale label.
3. **ch 14: 'Handheld' in Base** — Handheld moved to ch 37. Same issue as ch 13.
4. **ch 38: 'Lapel' in Base** — Equipment renamed to 'Headset'. DSL overrides this, but any team not including ch 38 in their assembly would see 'Lapel'.

### Infrastructure channels missing from DSL and Base
5. **ch 15 Piano** — Present in ALL 6 team snapshots (consistent name), present in Priscilla DSL but NOT in Base.snap and NOT in James DSL. If a new team renders a James-style snapshot and ch 15 is not in their assembly, it will be unnamed.
6. **ch 36 Oscillator** — Present in 5/6 team snapshots (consistent name), NOT in Base.snap, NOT in any DSL. Completely invisible to the renderer. The Wing's Oscillator channel will be unnamed in any rendered snapshot.
7. **ch 39 Computer** — Present in ALL 6 team snapshots (consistent name), NOT in Base.snap, NOT in any DSL. Computer channel unnamed in every rendered snapshot.
8. **ch 40 TALKBACK** — Present in Base.snap and all 6 teams (consistent). Not in any DSL, but Base.snap covers it. This one is fine.

### Spelling
9. **'Pricilla' typo in musician file** — `data/dsl/musicians/priscilla-vox.yaml` has `name: Pricilla` (missing 'l'). This propagates to all rendered output and Sunday Starters. Should be `Priscilla` (matching the team leader's name) or confirmed as intentional.

### Formatting
10. **DCA 8 name: 'DCA|8'** — Uses pipe character instead of period, unlike DCA 9-16 which use 'DCA.N'. Minor cosmetic inconsistency in Base.snap.

### Missing infrastructure
11. **Matrix bus names not rendered** — Six matrix buses (Back Vox, Guitars, Other Inst, Drum Set, Congas, Wireless) appear consistently in James/Levin/Priscilla snapshots but are not rendered. They exist only in manually-saved snapshots.

---

## 11. Implications for Phase 3

### Bus name rendering (high priority)
The renderer must set bus display names. The DSL assembly already has logical names (`inst_house`, `vocals`, etc.) but they're only used for routing lookups. Phase 3 should add a bus display name field to the assembly DSL and have the renderer write it to `ae_data.bus[n]["name"]`. The assembly could look like:

```yaml
buses:
  1: { logical: drums, display: DRUMS }
  2: { logical: inst_house, display: Rhythm/House }
  6: { logical: vocals, display: Vocals }
```

Or simpler: define a display name map separate from the routing map, since some buses need names even when not in the assembly's routing config (e.g., buses 4-5 which appear named in Sunday Starters but have no routing in current DSL).

**Decision needed**: Should bus display names be managed in the assembly or in Base.snap? Given they're consistent across all teams (except bus 12), the right place is likely a cleaned Base.snap with the correct current names, and team-specific overrides only when a team uses a bus with a different purpose (as Priscilla does with bus 12 = Delay/Rhythm).

### Infrastructure channels (medium priority)
Channels 15 (Piano), 36 (Oscillator), 39 (Computer) should be added to Base.snap with their correct names. This is the cleanest fix — it gives them names everywhere without requiring DSL management. They're infrastructure channels that aren't team-specific.

### Beginner custom views (Phase 3 core)
If the custom user layers (Phase 3) show channel strip names on the Wing's screen, any unnamed channel will appear blank. This makes the beginner view confusing. The infrastructure channel gaps above must be closed before Phase 3's custom views ship.

### DCA name rendering
Phase 3 will likely add DCA group assignments per team. If DCAs get team-specific groupings (e.g., "Percussion" vs "Rhythm"), their names need to be rendered too. Currently they come from Base.snap unchanged. The renderer will need to write `ae_data.dca[n]["name"]` when Phase 3 adds DCA configuration.

### Matrix bus naming
If Phase 3 custom views route to matrix buses, naming becomes important. Consider adding matrix bus names to Base.snap (since James/Levin/Priscilla all use the same six names) and letting teams override if needed.

---

## Questions for Matthew

1. **Bus names on the Wing**: When you load a DSL-rendered snapshot today, the Wing's bus strip labels show the old Base.snap names (BASS, Inst/House, Lead/House, etc.) rather than the names you're used to (Rhythm/House, Vocals, etc.). Have you noticed this? Is it causing confusion, or have you been working around it?

2. **DSL bus name solution**: Should bus display names be:
   - (a) Part of the assembly YAML so each team can control its own bus labels
   - (b) Fixed in a cleaned Base.snap (since they're the same across all teams except bus 12)
   - (c) A hybrid: cleaned Base.snap for shared infrastructure + assembly override for team-specific buses

3. **Buses 4-5 (Melodic/House, Melodic/Stream)**: These appear in all Sunday Starters with names but are NOT in any DSL assembly. What are they currently used for? Are channels actually routed to them, or are they named relics from the old 4-bus routing scheme?

4. **Infrastructure channels to add to Base.snap**: I'd recommend adding these to Base.snap so they're named in every snapshot:
   - ch 15: Piano
   - ch 36: Oscillator  
   - ch 39: Computer
   
   And updating stale names:
   - ch 13: Computer → (empty or remove)
   - ch 14: Handheld → (empty or remove)
   - ch 38: Lapel → Headset
   
   Does this match your intent? Are there other properties (color, icon, mute state) for these channels that should also be standardized in Base?

5. **'Pricilla' spelling**: The musician file spells it `Pricilla`. Is this intentional (short form) or a typo that should be corrected to `Priscilla`?

6. **Matrix bus naming**: Buses MTX 1-6 (Back Vox, Guitars, Other Inst, Drum Set, Congas, Wireless) appear consistently in your snapshots. Should these be added to Base.snap so rendered snapshots include them? Are they used for anything specific or just labeled for reference?

7. **DCA 8 formatting**: `DCA|8` uses a pipe character while `DCA.9` through `DCA.16` use periods. Minor, but should this be cleaned up to `DCA.8` in Base.snap?

---

## Appendix: Complete Name Tables

### Channels — all teams at a glance

| Ch | Init | Base | James | Levin | Jen | Priscilla | Morks | Kana |
|----|------|------|-------|-------|-----|-----------|-------|------|
| 1 | — | Kick | Kick | Kick | Kick | Kick | Kick | Kick |
| 2 | — | Snare | Snare | Snare | Snare | Snare | Snare | Snare |
| 3 | — | Tom | Tom | Tom | Tom | Tom | Tom | Tom |
| 4 | — | Overhead | Overhead | Overhead | Overhead | Overhead | Overhead | Overhead |
| 5 | — | — | Bass | Bass | Bass | Bass | Bass | Bass |
| 6 | — | — | Conga 1 | Violin | — | — | — | — |
| 7 | — | — | Conga 2 | — | — | — | — | — |
| 8 | — | — | Bongos | — | — | — | — | — |
| 9-12 | — | — | — | — | — | — | — | — |
| 13 | — | **Computer** | James | Guitar | Acoustic | Flute | Guitar | — |
| 14 | — | **Handheld** | Flute | — | Electric Guitar | — | Roudy | — |
| 15 | — | — | Piano | Piano | Piano | Piano | Piano | Piano |
| 16 | — | — | Violin | Violin | Keys | Guitar | — | — |
| 17 | — | — | — | — | — | — | — | — |
| 18 | — | — | Sanctuary | — | — | — | — | — |
| 19-24 | — | — | — | — | — | — | — | — |
| 25 | — | — | James | James | JEN | — | Roudy | — |
| 26 | — | — | Pricilla | James | BETH | — | Roudy | — |
| 27 | — | — | Anna | James | NEENAH | — | Roudy | — |
| 28 | — | — | Yolaine | James | Marin | — | Roudy | — |
| 29 | — | — | Kana | — | Peace | area mic | — | area mic |
| 30 | — | — | Elizabeth | — | — | — | — | — |
| 31-35 | — | — | — | — | — | — | — | — |
| 36 | — | — | Oscillator | Oscillator | — | Oscillator | Oscillator | Oscillator |
| 37 | — | — | Handheld | Handheld | Handheld | Handheld | Handheld | Handheld |
| 38 | — | **Lapel** | Headset | Headset | Headset | Headset | Headset | Headset |
| 39 | — | — | Computer | Computer | Computer | Computer | Computer | Computer |
| 40 | — | TALKBACK | TALKBACK | TALKBACK | TALKBACK | TALKBACK | TALKBACK | TALKBACK |

Bold = stale Base.snap names. Dashes = empty.

### Buses — all teams

| Bus | Base | James | Levin | Jen | Priscilla | Morks | Kana |
|-----|------|-------|-------|-----|-----------|-------|------|
| 1 | DRUMS | DRUMS | DRUMS | DRUMS | DRUMS | DRUMS | DRUMS |
| 2 | **BASS** | Rhythm/House | Rhythm/House | Rhythm/House | Rhythm/House | Rhythm/House | Rhythm/House |
| 3 | **Inst/House** | Rhythm/Stream | Rhythm/Stream | Rhythm/Stream | Rhythm/Stream | Rhythm/Stream | Rhythm/Stream |
| 4 | **Inst/Stream** | Melodic/House | Melodic/House | Melodic/House | Melodic/House | Melodic/House | Melodic/House |
| 5 | **Back Vox** | Melodic/Stream | Melodic/Stream | Melodic/Stream | Melodic/Stream | Melodic/Stream | Melodic/Stream |
| 6 | **Lead/House** | Vocals | Vocals | Vocals | Vocals | Vocals | Vocals |
| 7 | Lead/Stream | — | — | — | — | — | — |
| 8 | All channels | — | — | — | — | — | — |
| 9 | Delay/Slap | Delay/Slap | Delay/Slap | Delay/Slap | Delay/Slap | Delay/Slap | Delay/Slap |
| 10 | **Delay/Repeat** | Reverb/Medium | Reverb/Medium | Reverb/Medium | Reverb/Medium | Reverb/Medium | Reverb/Medium |
| 11 | **Reverb/Medium** | Reverb/Long | Reverb/Long | Reverb/Long | Reverb/Long | Reverb/Long | Reverb/Long |
| 12 | **Reverb/Long** | **Back Vox** | Delay/Rhythm | Delay/Rhythm | Delay/Rhythm | Delay/Rhythm | Delay/Rhythm |
| 13 | Monitor/1 | Monitor/1 | Monitor/1 | Mon/Lead | Monitor/1 | Monitor/1 | Monitor/1 |
| 14 | Monitor/2 | Monitor/2 | Monitor/2 | Mon/Sing | Monitor/2 | Monitor/2 | Monitor/2 |
| 15 | Monitor/3 | Monitor/3 | Monitor/3 | Mon/Bass | Monitor/3 | Monitor/3 | Monitor/3 |
| 16 | Monitor/4 | Monitor/4 | Monitor/4 | Mon/Drums | Monitor/4 | Monitor/4 | Monitor/4 |

Bold = stale Base.snap names that don't match Sunday Starters.

Note: Jen team uses personalized monitor names (Mon/Lead, Mon/Sing, Mon/Bass, Mon/Drums) — the only team doing this.

### DCAs — all teams (consistent everywhere, provenance = Base.snap)

| DCA | Name | Status |
|-----|------|--------|
| 1 | Rhythm | Used |
| 2 | Inst B | Used |
| 3 | Vox B | Used |
| 4 | Leads | Used |
| 5 | FX | Used (problematic fader level) |
| 6 | All No L | Used |
| 7 | Monitors | Used |
| 8 | DCA\|8 | Generic |
| 9-16 | DCA.9 – DCA.16 | Generic |

### Mute groups — all teams (consistent everywhere, provenance = Base.snap)

| MGRP | Init name | Custom name |
|------|-----------|-------------|
| 1 | MGRP.1 | Rhythm |
| 2 | MGRP.2 | Inst B |
| 3 | MGRP.3 | Vox B |
| 4 | MGRP.4 | Leads |
| 5 | MGRP.5 | Inst All |
| 6 | MGRP.6 | Vox All |
| 7 | MGRP.7 | Monitors |
| 8 | MGRP.8 | Worshp |

### Matrix buses — James/Levin/Priscilla only (Base.snap = all empty)

| MTX | Name |
|-----|------|
| 1 | Back Vox |
| 2 | Guitars |
| 3 | Other Inst |
| 4 | Drum Set |
| 5 | Congas |
| 6 | Wireless |
| 7-8 | (empty) |
