---
description: "Run a Phase 3 pre-investigation. Usage: /investigate A (or B, C, D, E)"
---

# Phase 3 Investigation $1

You are running one of five pre-investigations for the snapwright project's Phase 3 (Complexity Levels). Read `docs/phase-3-investigations.md` to find the brief for **Investigation $1**, then execute it fully.

## Project Context

Snapwright generates Behringer Wing digital mixer snapshots from a YAML-based DSL. The system renders `.snap` files (JSON) that the Wing loads to configure all channels, buses, processing, routing, and control surface state.

### Architecture

```
data/dsl/musicians/*.yaml    → instrument/person configs (EQ, dynamics, gate, fader, sends)
data/dsl/teams/*/assembly.yaml → team assemblies (who plays what, channel layout, monitors)
snapwright/dsl/schema.py      → Pydantic models for the DSL
snapwright/dsl/loader.py      → YAML loading + inheritance merge
snapwright/dsl/renderer.py    → DSL → Wing JSON rendering
data/reference/Base.snap      → BCF base configuration (foundation every snapshot inherits from)
data/reference/Init.snap      → Factory-initialized Wing snapshot (true zero state)
data/reference/sunday-starters/ → Actual team snapshots pulled from the mixer
```

### Wing JSON Structure

A `.snap` file has two top-level data sections:

- **`ae_data`** (Audio Engine) — channels, buses, DCA, mute groups, FX, aux, main, matrix, I/O, config
  - `ch` (1-40): input channels. Each has ~267 params: `name`, `fdr`, `mute`, `col`, `icon`, `in` (input routing), `flt` (filters), `eq`, `dyn` (dynamics), `gate`, `send` (24 bus sends + 8 matrix sends), `tags`, and more
  - `bus` (1-16): mix buses. Similar structure to channels but with different routing
  - `dca` (1-16): DCA faders. Fields: `name`, `fdr`, `mute`, `col`, `icon`, `led`, `mon`
  - `mgrp` (1-8): mute groups. Fields: `name`, `mute`
  - `fx` (1-16): effects slots
  - `aux` (1-8): aux inputs
  - `main` (1-4): main outputs (1=HOUSE, 2=STREAM used; 3-4 unused)
  - `mtx` (1-8): matrix buses
  - `cfg`: console config — monitor outputs, solo settings, RTA, talkback, metering

- **`ce_data`** (Console Engine) — physical control surface state
  - `layer` (L/C/R): fader layer banks. Each section has numbered banks, each bank has 24 strip slots. Each strip: `{ type: "CH"|"BUS"|"DCA"|"OFF", i: <number>, dst: 1 }`
  - `user`: custom user layers (16 numbered + U1-U4, D1-D4, MM, daw1-4, gpio). Each layer has 4 strips with `enc` (encoder), `bu` (button up), `bd` (button down) mode assignments. Modes include: `OFF`, `FDR`, `SSND`, `SOF`, `INS1`, `INS2`, `DCA`, `DCAMUTE`, etc.
  - `cfg`: console preferences — auto-select, spill modes, fader banking, RTA display, solo behavior, lighting
  - `safes`: channel/bus safe assignments
  - `daw`, `midi`, `osc`, `gpio`: external control configuration

### Group Membership Encoding

DCA and mute group membership is encoded in the `tags` field on channels and buses:
- `#M8` = member of mute group 8 (e.g., the "Worship" group)
- `#D5` = member of DCA 5
- Multiple tags comma-separated: `#M5,#M6`
- Tags are strings, not numeric references

### Current State (after Phases 0-2)

**What the renderer handles today** (ae_data only):
- Channel identity: name, color, icon, mute, fader
- Input routing: source group + input number
- Processing: filters (HPF/LPF/tilt), EQ (STD + model pass-through), dynamics (ECL33 + model pass-through), gate (GATE + model pass-through)
- Sends: bus sends with on/off, level, mode (POST/PRE)
- Bus naming
- Monitor sends (as bus sends on monitor buses 13-16)

**What the renderer does NOT handle**:
- `ce_data` (layers, user layers, console config) — zero coverage
- DCA configuration (names, faders, group membership via tags)
- Mute group configuration (names, membership via tags)
- FX slot configuration
- Matrix bus configuration
- Main output configuration beyond naming
- Channel tags field

### Key Reference Files

- `docs/wing-param-map.md` — annotated parameter grouping for channel params
- `docs/decisions.md` — all architecture decisions with rationale
- `docs/ROADMAP.md` — phase plan and context

### DSL Conventions

- **Inheritance**: ordered list via `inherits`, Kustomize-style deep merge, last writer wins
- **Offsets vs overrides**: offsets are additive (levels only), overrides are absolute replacement
- **Send omission = off**: only active sends listed, omitted renders to off/-144dB
- **Naming**: short audio terms (`hpf`, `freq`, `gain`) not Wing abbreviations (`lc`, `f`, `g`)
- **EQ model switch**: renderer rebuilds entire dict from scratch (matches Wing behavior)
- **Float tolerance**: 3 significant figures (covers Wing's internal quantization)

### Current BCF Setup (from James.snap audit)

**Buses**: 1=DRUMS, 2=Rhythm/House, 3=Rhythm/Stream, 4=Melodic/House, 5=Melodic/Stream, 6=Vocals, 7=(unnamed), 8=(stage_feed in DSL), 9=Delay/Slap, 10=Reverb/Medium, 11=Reverb/Long, 12=Back Vox, 13-16=Monitors
Note: DSL consolidated buses 2-5 into inst_house + inst_stream, but snapshot bus names still show old 4-bus naming.

**DCAs** (1-7 named, 8-16 default):
1=Rhythm (fdr≈0), 2=Inst B (fdr≈0.3), 3=Vox B (fdr≈-0.3), 4=Leads (fdr≈-0.7), 5=FX (fdr≈-16.4!), 6=All No L (fdr≈-0.7), 7=Monitors (fdr≈0.1)

**Mute Groups**: 1=Rhythm, 2=Inst B, 3=Vox B, 4=Leads, 5=Inst All, 6=Vox All, 7=Monitors, 8=Worshp (mute=True, active — all worship channels tagged #M8)

**Named but not in DSL**: ch15 Piano, ch18 Sanctuary, ch29 Kana, ch30 Elizabeth, ch36 Oscillator, ch39 Computer, ch40 TALKBACK

**Custom user layers** (James.snap): layers 1-3 have active strip assignments (SSND, SOF, FDR, INS modes). Layer 4 has DCA control. Layers 5-16 may have configuration too.

### Why Phase 3 Matters

The goal is modular complexity control: same DSL source renders different snapshots depending on operator skill level. Examples:
- Disable all gates for a beginner
- Switch parametric EQ to a simpler model (SOUL 3-band) with pre-set frequencies
- Create custom user layers that put just 4-5 DCAs/buses on faders for simplified mixing
- Bundle these into composable "strategies" rather than rigid tiers

This requires the renderer to handle ce_data (custom views), DCA/mgrp configuration, and the tags system — none of which exist today.

## Instructions

1. Read `docs/phase-3-investigations.md` for the specific brief for Investigation $1
2. Execute the investigation as described
3. Write your output to the specified location (under `docs/investigations/`)
4. Flag anything that needs Matthew's input as explicit questions at the end
5. Be thorough — this output will be read by a separate session that synthesizes all five investigations into a Phase 3 design
6. You have `web_search` and `web_extract` tools available — use them for Wing documentation, parameter meanings, control surface modes, etc.
7. If you need to verify how a JSON change manifests on the console, you can generate a minimal test snapshot (copy Base.snap, make one targeted change to `ce_data`) and ask Matthew to load it in the Wing Edit application to confirm the effect. Write test snapshots to `data/investigations/` with descriptive names.