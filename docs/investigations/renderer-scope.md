# Investigation D: Renderer Scope Assessment

**Purpose**: Audit what the current renderer handles vs. what Phase 3 will require, and identify the gap.

**Date**: 2026-03-08
**Method**: Source audit of `snapwright/dsl/renderer.py` and `schema.py`, cross-referenced against Base.snap, James.snap, and Priscilla team snap. Ran rendered output comparisons in Python to verify what the renderer actually writes vs. what the reference snapshots contain.

---

## 1. Current ae_data Coverage

### ✅ `ae_data.ch` — Full coverage

The renderer processes all 40 channels. For channels listed in the assembly, it applies a complete pipeline:

| Sub-section | Fields managed | Notes |
|-------------|----------------|-------|
| Identity | `name`, `col`, `icon`, `mute`, `fdr`, trim (`in.set.trim`), `main.1.on` | All from musician resolution |
| Input routing | `in.conn.grp`, `in.conn.in`, `in.conn.altgrp`, `in.conn.altin` | Source group mapped from `stage-box/local/usb/off` |
| Firmware patches | `in.set.dly`, `flt.lcs`, `flt.hcs` | Applied to all 40 channels regardless of DSL entry |
| Filters | `flt.lc`, `flt.lcf`, `flt.lcs`, `flt.hc`, `flt.hcf`, `flt.tf`, `flt.tilt` | Full HPF/LPF/tilt coverage |
| EQ | `eq.on`, `eq.mdl`, all band/shelf fields | Patch mode for STD; rebuild-from-scratch for non-STD |
| Dynamics | `dyn.on`, `dyn.mdl`, all compressor fields | Patch mode for COMP; ECL33-specific sub-section; rebuild for others |
| Gate | `gate.on`, `gate.mdl`, threshold/range/attack/hold/release/ratio | Patch mode for GATE; rebuild for PSE/RIDE/9000G/etc |
| Sends | `send.1`–`send.12` (POST), `send.13`–`send.16` (PRE), `send.MX1`–`send.MX8` | All 24 sends declared as OFF then populated from DSL |

Channels **not** listed in the assembly keep their Base.snap defaults with only the firmware patches applied. This is intentional and correct.

**Tags field**: The renderer never writes to `ch.tags`. Tags on channels come from Base.snap defaults. This works by accident for channels 1–24 (which have `#M8` in Base.snap), but breaks for channels 5–8, 25–28, and any vocals/instruments that weren't in Base.snap when it was configured. See §4 for impact.

### ❌ `ae_data.bus` — Not touched

The renderer calls `snap_template()` (deep copy of Base.snap) and only updates `ae_data.ch` entries. All bus configuration is passed through unchanged from Base.snap.

**Impact**: Bus names in the rendered output are stale Base.snap names, not the DSL logical names:

| Bus | Base.snap name | James DSL logical name | James.snap actual name |
|-----|---------------|----------------------|----------------------|
| 1 | `DRUMS` | `drums` | `DRUMS` ✓ (coincidence) |
| 2 | `BASS` | `inst_house` | `Rhythm/House` |
| 3 | `Inst/House` | `inst_stream` | `Rhythm/Stream` |
| 4 | `Inst/Stream` | — (not in DSL) | `Melodic/House` |
| 5 | `Back Vox` | — (not in DSL) | `Melodic/Stream` |
| 6 | `Lead/House` | `vocals` | `Vocals` |
| 9 | `Delay/Slap` | `delay_slap` | `Delay/Slap` ✓ |
| 10 | `Delay/Repeat` | `reverb_medium` | `Reverb/Medium` |
| 11 | `Reverb/Medium` | `reverb_long` | `Reverb/Long` |
| 12 | `Reverb/Long` | `back_vox` | `Back Vox` |
| 13–16 | `Monitor/1`–`/4` | `monitor_1`–`_4` | `Monitor/1`–`/4` ✓ |

The rendered output has wrong bus names for buses 2–6 and 10–12. These are displayed on the Wing's faders — wrong names on faders is a real usability problem.

The DSL's `buses` dict (e.g. `{2: inst_house}`) is purely internal routing logic — used to translate logical send names to bus numbers. It is never written to the output snap.

### ❌ `ae_data.dca` — Not touched

All 16 DCAs pass through from Base.snap unmodified. The renderer has no DCA concept.

Base.snap DCA state:

| DCA | Name | Fader | Status |
|-----|------|-------|--------|
| 1 | `Rhythm` | +0.2 dB | Named infrastructure |
| 2 | `Inst B` | +0.3 dB | Named infrastructure |
| 3 | `Vox B` | -0.3 dB | Named infrastructure |
| 4 | `Leads` | -0.7 dB | Named infrastructure |
| 5 | `FX` | -0.2 dB | Named (James.snap has this at -16.4 dB — team-specific divergence) |
| 6 | `All No L` | -0.7 dB | Named infrastructure |
| 7 | `Monitors` | +0.1 dB | Named infrastructure |
| 8 | `DCA\|8` | -144 dB | Default/unused |
| 9–16 | `DCA.N` | -144 dB | Default/unused |

**Active risk**: DCA faders 1–7 are all non-zero (ranging from -0.7 to +0.3 dB). These silently scale all channels assigned to them. Since the renderer never sets DCA membership (tags), the actual membership for these DCAs is unknown from the DSL perspective — it's whatever was manually set in each team's snap.

### ❌ `ae_data.mgrp` — Not touched

All 8 mute groups pass through from Base.snap unmodified.

| Mgrp | Name | Active in Base? |
|------|------|----------------|
| 1 | `Rhythm` | `mute: false` |
| 2 | `Inst B` | `mute: false` |
| 3 | `Vox B` | `mute: false` |
| 4 | `Leads` | `mute: false` |
| 5 | `Inst All` | `mute: false` |
| 6 | `Vox All` | `mute: false` |
| 7 | `Monitors` | `mute: false` |
| 8 | `Worshp` | `mute: false` |

Mute group 8 ("Worshp") is the only one with verified membership via `#M8` tags in the channel data. Groups 1–7 have names but their channel/bus membership is unclear without a DCA/mgrp audit (Investigation C territory).

### ❌ `ae_data.fx` — Not touched

All 16 FX slots pass through from Base.snap. The renderer has no FX concept.

In James.snap, slots 1–4 are configured (Delay, Reverb Medium, Reverb Long, and a guitar amp plugin). These are team-specific configurations accumulated manually in the snap — the renderer doesn't know they exist.

### ❌ `ae_data.main` — Not touched

All 4 main outputs pass through from Base.snap. Names (`HOUSE`, `STREAM`) and faders come from whatever was in Base.snap at configuration time.

### ❌ `ae_data.mtx` — Not touched

All 8 matrix buses pass through from Base.snap. James.snap has mtx[1] named `Back Vox` with a non-default fader — manually configured, not in DSL.

### ❌ `ae_data.cfg` — Not touched

Console-level config (talkback routing, solo settings, monitor sources, RTA config, metering, etc.) passes through from Base.snap. This is mostly infrastructure that doesn't change per team.

### ❌ `ae_data.aux`, `ae_data.io`, `ae_data.cards` — Not touched

All pass through from Base.snap. These are physical I/O routing and input configurations — infrastructure that is currently maintained manually.

---

## 2. ce_data Coverage

**Zero coverage.** The entire `ce_data` section passes through from Base.snap unmodified.

| ce_data section | What it is | Renderer coverage |
|-----------------|------------|-------------------|
| `layer` (L/C/R) | Physical fader bank assignments | ❌ |
| `user` (1–16 + named) | Custom user layers | ❌ |
| `cfg` | Console preferences | ❌ |
| `safes` | Channel/bus safe assignments | ❌ |
| `daw`, `midi`, `osc`, `gpio` | External control | ❌ |

The Base.snap `ce_data.user` entries are all blank (mode: OFF for all strips). The James.snap user layers 1–4 are actively configured with monitor send faders, DCA controls, FX send controls, and vocal fader strips — all manually set, not rendered.

The structure of a configured user layer strip (from James.snap layer 1):
```json
{
  "led": false,
  "col": 1,
  "enc": { "mode": "SSND", "name": "Lead Monitor", "send": "BUS13" },
  "bu":  { "mode": "SOF",  "name": "Lead Send",    "ch": 61 },
  "bd":  { "mode": "OFF",  "name": "" }
}
```

Each strip has an encoder (`enc`) and two buttons (`bu` up, `bd` down). Modes observed in James.snap:
- `SSND` — send level for a specific bus (encoder controls send amount)
- `FDR` — fader control for a specific channel
- `DCA` — DCA level control (encoder controls DCA fader)
- `DCAMUTE` — DCA mute button
- `SOF` — spill-on-fader button (expands a bus/DCA's members across faders)
- `INS1` / `INS2` — insert FX control
- `OFF` — strip disabled

---

## 3. Phase 3 Capability Gap Analysis

### 3.1 Gate Disable Strategy

**Status: ✅ Already works — no renderer changes needed.**

`_apply_gate()` handles `on: False` cleanly for all gate models:
- GATE model: patches `gate.on = False` directly
- PSE/RIDE/9000G/etc: the `on` field is the first thing written in the rebuild path

A strategy overlay that sets `gate.on: false` on all channels will work correctly today. Tested:
```python
# PSE gate, only specifying on: false
gate_override = {'on': False}
_apply_gate(ch, gate_override)
# Result: ch['gate']['on'] = False, all other PSE params unchanged ✓
```

What's missing is the **strategy delivery mechanism** — a way to declare "for this complexity level, disable all gates" in the DSL and have the renderer apply it as an overlay across all channels. The renderer function itself is ready; the DSL schema for expressing strategies is not.

### 3.2 EQ Model Switch Strategy

**Status: ✅ Already works — no renderer changes needed.**

The model switching was a core Phase 1 feature. `_apply_eq()` already handles switching to SOUL (or any other model) with a full dict rebuild. SOUL is already in active use across both teams' reference snaps.

A strategy that specifies `model: SOUL` with pre-configured frequencies works today. The DSL can express this already via `overrides` in musician entries.

Same caveat as gate disable: what's missing is the strategy delivery mechanism, not the rendering capability.

### 3.3 DCA Configuration

**Status: ❌ Not implemented. Moderate complexity to add.**

Phase 3 requires:
1. **DCA naming and faders** — write `ae_data.dca[N].name`, `.fdr`, `.col`, `.mute` from DSL configuration
2. **Channel DCA membership** — write `#D<n>` tags to `ae_data.ch[N].tags`
3. **Bus DCA membership** — write `#D<n>` tags to `ae_data.bus[N].tags`

The renderer currently never touches `ae_data.dca` or the `tags` field on any entity.

**DSL schema gap**: `AssemblyDef` has no DCA configuration section. Needs something like:
```yaml
dcas:
  5:
    name: FX Returns
    fader: 0
    members: [delay_slap, reverb_medium, reverb_long, back_vox]  # logical bus names
```

The `members` list would resolve to bus keys and write `#D5` tags on those buses. Channel membership could work the same way or be declared per-channel in the musician files.

**Tags field complexity**: Tags are comma-separated strings like `#M8,#D5`. The renderer needs to either:
(a) Read the existing tags from Base.snap defaults and append/replace, or
(b) Own the complete tags value (rebuild from scratch based on DSL declarations)

Option (b) is cleaner architecturally (no hidden state from Base.snap), but requires complete DCA and mgrp membership to be declared in the DSL before using it.

### 3.4 Custom User Layers

**Status: ❌ Not implemented. High complexity.**

This is the core of the "beginner view" concept. The renderer currently has zero ce_data handling. Adding user layers requires:

1. **New renderer section** for `ce_data.user[N]` — completely separate from the current `ae_data.ch` pipeline
2. **New DSL schema** for user layer configuration — the most significant schema design work
3. **Physical reference resolution** — user layer strips reference physical bus/channel numbers (e.g. `BUS13`, `ch: 25`), so the DSL needs to resolve logical names to physical slots for ce_data

The James.snap user layers show the intended semantics:
- Layer 1: Monitor fader view (4 monitor sends, one per strip, all SSND mode)
- Layer 2: Lead vocal control (FDR + INS mode strips)
- Layer 3: FX return levels (SSND to FX buses)
- Layer 4: DCA control (single FX DCA with encoder + mute button)

A beginner-oriented user layer would look like: 4 strips showing the main DCAs (Drums, Instruments, Vocals, Monitors) with FDR mode for the encoders and DCAMUTE for the buttons.

**Key complication**: User layer strips reference Wing physical object numbers directly (bus `BUS13` not logical `monitor_1`, channel `25` not logical `james-vox`). The renderer needs a resolution step from logical assembly names to physical numbers before writing ce_data.

### 3.5 Layer Bank Customization

**Status: ❌ Not implemented. Lower priority.**

The L/C/R fader bank layout (which channels appear on which physical fader banks) is currently the Base.snap default. It could in principle be generated from the assembly's `channels` dict — but the Base.snap default (banks of 12 channels in order) is usually fine. The real need is the custom user layers (§3.4), not the main bank layout.

However, for a "stripped down" complexity view, bank customization could put just the active assembly channels on the faders and hide the unused slots. This is medium priority, not blocking.

### 3.6 Bus Naming

**Status: ❌ Not implemented. High priority — needed for correctness today, not just Phase 3.**

The rendered output has wrong bus names (Base.snap legacy names). This is a Phase 1 gap that affects usability right now — the console shows `BASS` and `Inst/House` where the current DSL expects `inst_house` and `inst_stream`.

The DSL already has the physical bus number → logical name mapping in `assembly.buses`. What's missing is:
1. A human-readable display name for each bus (the DSL logical name `inst_house` isn't the Wing display name `Inst/House`)
2. Renderer code to write these to `ae_data.bus[N].name`

This could be expressed in the assembly as:
```yaml
buses:
  2:
    logical: inst_house
    name: Inst/House
```
Or the renderer could derive a display name from the logical name (underscore → slash, title case).

### 3.7 Mute Group Naming

**Status: ❌ Not implemented. Medium priority.**

Currently mgrp names pass through from Base.snap. The DSL could declare mgrp names alongside DCA config. This is lower urgency since mute group 8 ("Worshp") is the only one actively used.

---

## 4. Tags Field: Current State vs. Required

The `tags` field encodes DCA and mute group membership and is the most pervasive gap.

**Current state** (rendered James output vs James.snap reference):

| Channel | DSL entry | Base.snap tags | Rendered tags | James.snap tags | Match? |
|---------|-----------|----------------|---------------|-----------------|--------|
| ch[1–4] | kick/snare/tom/overhead | `#M8` | `#M8` | `#M8` | ✅ (accident) |
| ch[5] | bass | `` (empty) | `` | `#M8` | ❌ |
| ch[6–8] | conga1/2/bongos | `` | `` | `#M8` | ❌ |
| ch[13] | james-guitar | `#M8` | `#M8` | `#M8` | ✅ (accident) |
| ch[14–16] | flute/violin | `#M8` | `#M8` | `#M8` | ✅ |
| ch[25–28] | vocals | `` | `` | `#M8` | ❌ |
| ch[37–38] | handheld/headset | `` | `` | `` | ✅ |

**Current state for buses** (rendered output always has Base.snap values):

| Bus | Rendered tags | James.snap tags | Gap |
|-----|---------------|-----------------|-----|
| 1–4 | `` | `#M5` | ❌ |
| 5 | `` | `#M6` | ❌ |
| 6 | `` | `#M5,#M6` | ❌ |
| 9–12 | `` | `#D5` | ❌ |

The `#M8` on ch[1–4] and ch[13–24] is "correct by coincidence" because those channels happen to have `#M8` in Base.snap. The renderer does nothing to maintain this.

**Consequence**: If the assembly changes channel assignments (moves bass from ch5 to ch11, for example), the `#M8` membership will be wrong because it depends on where Base.snap has tags, not on what the DSL declares.

---

## 5. DSL Schema Gaps

Current `AssemblyDef` is missing:

| Missing field | Purpose | Phase 3 need |
|---------------|---------|-------------|
| `dcas` section | DCA names, faders, membership | High — core of beginner view |
| `mgrps` section | Mgrp names (membership can derive from channels) | Medium |
| Bus display names | Human-readable name written to wing snap | High — fixes existing gap |
| `user_layers` section | ce_data custom view configuration | High — beginner view strips |
| Strategy flags | `gate: off`, `eq_model: SOUL` | High — the complexity mechanism itself |

The `InstrumentLayer` schema (musician/overlay/template files) is missing:
- No `dca_groups` field — there's no way for a musician to declare its DCA membership
- No `mgrp_members` field — same for mute groups
- Tags would need to flow from these declarations into the rendered `ch.tags`

Current musician YAML files have no concept of group membership; that's only in the James.snap manually.

---

## 6. Code Quality Assessment

**Verdict: Do not rewrite the Phase 1 renderer before Phase 3. It is solid enough to extend.**

### What's good

1. **Clear pipeline structure**: `_render()` → firmware patch → identity → input → processing → sends. The stages are separated into named functions with single responsibilities.

2. **Model-switching handled correctly**: The rebuild-vs-patch decision for EQ/dynamics/gate is well-designed and battle-tested.

3. **Send system is declarative**: All sends initialized OFF, then populated from DSL. No hidden state.

4. **Well-tested**: 73 tests covering all major channel rendering paths. All passing.

5. **Prototype-vs-TDD**: Phase 1 renderer was developed with sufficient test coverage; it's load-bearing and trusted for real decisions. The domain model is stable.

### Where it will strain under Phase 3

1. **Channel-centric architecture**: The current renderer loops over channels. DCA config, mgrp config, and bus naming need top-level sections in `_render()` that loop over different data. This is not a problem — just extension needed, not surgery.

2. **snap_template() as pass-through**: Sections the renderer doesn't manage are inherited silently from Base.snap. This is the right design for Phase 1 (don't invent defaults) but Phase 3 needs the renderer to actively manage more sections. The architecture supports this; it's additive work.

3. **Tags are cross-cutting**: DCA/mgrp membership affects both channel tags and bus tags. These aren't handled by any existing renderer function. Adding them requires touching both the channel pipeline (add tags to `_apply_identity`) and a new bus pipeline.

4. **ce_data is entirely new territory**: The entire console engine side needs new functions. There's nothing to reuse from the current ae_data rendering code — it's a parallel structure.

5. **No tests for non-channel sections**: The test suite only covers `ae_data.ch`. Phase 3 additions need test coverage from the start.

### Recommendation

**Extend, don't rewrite.** The Phase 1 renderer passes 73 tests on real data. Its architecture is clean enough to extend with:
- New top-level blocks in `_render()` for buses, DCAs, mgrps, and ce_data
- A `_apply_tags()` function called from the channel pipeline
- Parallel new functions `_render_buses()`, `_render_dcas()`, `_render_mgrps()`, `_render_user_layers()`
- New DSL schema sections validated by new Pydantic models

**Use TDD from day one for Phase 3 additions** — unlike Phase 1 where the domain was unknown, the Phase 3 rendering targets (tags format, DCA structure, user layer strip structure) are now documented. Tests should be written before the renderer code.

---

## 7. Ordered Build List for Phase 3

Sequenced by dependency and impact:

### Tier 1: Schema design (gate everything else)
1. **Strategy DSL shape** — how to express "disable all gates", "switch EQ to SOUL". This is the core Phase 3 design question. Needs Matthew's input on the composability model (does a strategy file overlay on top of musician files? Is it per-assembly or a separate file?).
2. **DCA DSL schema** — `dcas` section in `AssemblyDef` with names, faders, member lists. Blocks DCA rendering, tags rendering, and user layer DCA strips.
3. **User layer DSL schema** — strip mode/target configuration. Blocks ce_data rendering.

### Tier 2: ae_data extensions (build on stable foundation)
4. **Bus naming renderer** — write bus display names from DSL to `ae_data.bus[N].name`. Fixes existing gap.
5. **DCA config renderer** — write DCA names, faders to `ae_data.dca[N]`. Depends on DCA DSL schema.
6. **Tags rendering** — write `ch.tags` and `bus.tags` from declared DCA/mgrp membership. Depends on DCA DSL schema.
7. **Strategy overlay application** — apply gate/EQ strategies as a pass over all channels before channel-specific processing. Depends on strategy DSL shape.

### Tier 3: ce_data (new territory, higher complexity)
8. **User layer renderer** — write `ce_data.user[N]` from DSL declarations. Depends on user layer DSL schema and physical number resolution.
9. **Layer bank renderer** — optionally customize L/C/R banks from assembly. Lower priority.

### Tier 4: Test coverage
10. **Phase 3 renderer tests** — TDD the above additions. Should be concurrent with Tier 2–3, not sequential.

---

## 8. Questions for Matthew

**Q1 — Strategy delivery mechanism**: How should complexity strategies be expressed in the DSL? Options:
- (a) A `strategies` section in the assembly file that names strategy profiles to apply
- (b) Separate strategy files (`strategies/beginner.yaml`) that are applied at render time via a flag
- (c) Strategy as a render-time argument to the CLI (`snapwright render --strategy beginner`)

The investigation reveals the renderer already supports gate disable and EQ model switching per-channel. The missing piece is how to apply these transformations across all channels from a single declaration. What's the intended ergonomics?

**Q2 — DCA membership authority**: Currently DCA membership (`#D5` on buses) is manually configured in team snaps. For Phase 3, should membership be:
- (a) Declared in the assembly DSL (DSL owns it completely, renderer writes tags from scratch)
- (b) Inherited from Base.snap and supplemented by DSL (keep existing manual assignments, DSL adds team-specific ones)

Option (a) is cleaner but requires all existing DCA assignments to be captured in DSL. Option (b) maintains the status quo with DSL additions on top.

**Q3 — Bus display names**: The rendered output currently shows wrong bus names (Base.snap legacy names instead of current team names). Should the assembly file include a display name field per bus (`name: Inst/House`), or should the renderer derive display names from logical names? The current `{2: inst_house}` mapping doesn't have a display name.

**Q4 — User layer ownership**: Are user layers team-specific (per assembly), or could there be shared user layer templates? The James.snap user layers (monitor faders, FX sends, vocal controls) appear team-specific. But a "beginner view" layer might be shared across all teams with team-specific targets. How should this be structured?

**Q5 — Tags field rebuild strategy**: When the renderer starts managing DCA/mgrp membership, should it:
- (a) Rebuild `ch.tags` and `bus.tags` entirely from DSL declarations (clean, but requires complete declaration)
- (b) Read Base.snap tags and merge DSL additions (preserves manual assignments, but hidden state)

The current mute group 8 membership (`#M8` on worship channels) would need to be explicit in the DSL under option (a). Is that the right direction?

---

## Summary

The Phase 1 renderer is solid for `ae_data.ch` (73 tests, all passing). It has zero coverage of `ae_data.bus`, `dca`, `mgrp`, `main`, `mtx`, `fx`, tags fields, or any part of `ce_data`.

For Phase 3, two capabilities are already working (gate disable, EQ model switch) — they just need a strategy delivery mechanism. The three major gaps requiring new renderer code are: **bus naming**, **DCA config + tags**, and **custom user layers (ce_data)**. The renderer architecture is clean enough to extend without a rewrite; TDD should be used from day one for Phase 3 additions.

The most important design question is the **strategy composability model** — how a complexity level overlays on top of musician configs. That design drives everything else.
