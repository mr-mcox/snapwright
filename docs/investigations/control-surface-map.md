# Investigation B: Control Surface Structure Map

**Date**: 2026-03-08  
**Source files examined**: `Init.snap`, `Base.snap`, `James.snap`, `Levin.snap`, `Jen.snap`, `pricilla team.snap`, `Morks~2025.snap`  
**Output location**: `docs/investigations/control-surface-map.md`

---

## Overview

`ce_data` (Console Engine data) is the second top-level section of every Wing snapshot. It captures the physical control surface state: which channels appear on which faders, what the custom user layer encoders do, and console-wide preferences. Everything in ce_data is snapshot-recalled — there is no "global only" distinction in the .snap format. Safe assignments (`ce_data.safes`) allow specific items to be immune from recall.

```
ce_data/
├── layer      # Fader bank assignments for each hardware surface section
├── user       # Custom user layer (CC) strip assignments
├── cfg        # Console preferences
├── safes      # Snapshot recall protection
├── daw        # DAW controller config
├── midi       # MIDI control config
├── osc        # OSC config
├── gpio       # GPIO config
└── lib        # (empty in observed files)
```

---

## Section 1: `ce_data.layer` — Fader Bank Assignments

### 1.1 Hardware Sections

The Wing has eight recognized surface sections, each with their own set of banks:

| Section key | Hardware | Faders/bank | Banks (Init) | Notes |
|---|---|---|---|---|
| `L` | Left bay | 24 | 7 | Main input channels section |
| `C` | Center bay | 16 | 6 | DCAs, mains, buses |
| `R` | Right bay | 16 | 7 | Monitor/bus overview |
| `CMPCT` | Wing Compact | 24 | 9 | Compact model (absent in Base.snap) |
| `RCK` | Wing Rack | 40 | 5 | Rack model (absent in Base.snap) |
| `EXT` | External bay | 16 | 8 | External hardware bay (absent in Base.snap) |
| `VRT` | Virtual | 16 | 8 | Software virtual surface |
| `WEDIT` | Wing Edit (PC) | 96 | 11 | PC software surface |

**Note**: `Base.snap` is missing `CMPCT`, `EXT`, `RCK`, and `VRT` sections entirely. These are Init defaults and aren't carried into the BCF configuration. Only `L`, `C`, `R`, and `WEDIT` sections are present in Base.

### 1.2 Section Structure

Each section contains:
```json
{
  "sel": 2,          // currently selected bank number
  "spidx": 0,        // spill index (used when a spill mode is active)
  "1": { ... },      // bank 1
  "2": { ... },      // bank 2
  ...
}
```

### 1.3 Bank Structure

Each bank contains:
```json
{
  "ofs": 0,          // scroll/display offset (which strip is shown at fader 1)
  "name": "CH1-12",  // display name for this bank
  "1": { "type": "CH", "i": 1, "dst": 1 },
  "2": { "type": "CH", "i": 2, "dst": 1 },
  ...
}
```

**`ofs` field**: Most banks use `ofs=0`. Non-zero offsets appear in BCF custom banks (e.g., Base.snap C bank 5 has `ofs=4`, Base.snap C bank 4 has `ofs=8`). This likely controls which strip is displayed at the leftmost physical fader position. Exact semantics require hardware verification.

**Strip count**: L banks have 24 strips (matching 12 physical faders × 2 pages), C and R banks have 16 strips, WEDIT has 96.

### 1.4 Strip Types

Each strip is `{ "type": "<TYPE>", "i": <index>, "dst": <dst> }`.

| Type | `i` field | `dst` field | Meaning |
|---|---|---|---|
| `CH` | Channel 1–40 or AUX 1–8 (as 41–48) | User layer ref (1–16) | Input channel or aux input on fader |
| `BUS` | See bus numbering below | User layer ref (1–16) | Mix bus, main, or matrix on fader |
| `DCA` | DCA 1–16 | User layer ref (1–16) | DCA group fader |
| `FX` | FX slot (0 = first slot?) | User layer ref | FX return on fader |
| `SENDS` | Source channel (1–40) | Destination bus number (1–16) | One channel's send level to a specific bus (L section) |
| `SEND` | Source channel (1–40) | Destination bus number (1–16) | One channel's send level to a specific bus (C section); functionally identical to SENDS |
| `OFF` | 0 | 1 | Empty/unused strip |

### 1.5 BUS Extended Numbering (layer context)

In `ce_data.layer` strip assignments, the `BUS` type uses a flat extended index that spans all output buses:

| Range | Maps to |
|---|---|
| BUS 1–16 | Mix buses 1–16 |
| BUS 17–20 | Main outputs 1–4 |
| BUS 21–28 | Matrix buses 1–8 |

Example: R section bank 1 "MAIN" has BUS(17)–BUS(28) = mains + matrix.

### 1.6 `dst` Field in Strip Assignments

The `dst` field serves two distinct purposes depending on strip type:

- **For CH, BUS, DCA strips**: `dst` is the **user layer number** (1–16) that becomes the active CC layer when you touch that fader. This links a physical fader to a custom user layer.
- **For SENDS/SEND strips**: `dst` is the **destination bus number** (1–16) — which mix bus these fader-sends are targeting.

Default value is `1` (user layer 1). BCF customization in `Base.snap` uses `dst=9` for the custom DCA bank (C section bank 5), linking those faders to user layer 9.

### 1.7 Default Layer Layouts (Init.snap)

**L section** (24-fader left bay, 7 banks):
1. `CH1-12` — input channels 1–12 on strips 1–12, 13–24 = OFF
2. `CH13-24` — channels 13–24
3. `CH25-36` — channels 25–36
4. `CH37-AUX` — channels 37–40 + aux inputs 41–48
5. `BUSES` — mix buses 1–16 (strips 1–16), 17–24 = OFF
6. `USER1` — all OFF (customizable)
7. `USER2` — all OFF (customizable)

**C section** (16-fader center bay, 6 banks):
1. `DCA` — DCAs 1–16 on strips 1–16
2. `MAIN` — BUS 17–28 (mains + matrix) on strips 1–12, 13–16 = OFF
3. `AUX` — aux inputs 41–48 on strips 1–8, rest = OFF
4. `BUSES` — mix buses 1–16
5. `USER1` — all OFF
6. `USER2` — all OFF

**R section** (16-fader right bay, 7 banks):
1. `MAIN` — BUS 17–28 (mains + matrix), same as C bank 2
2. `DCA` — DCAs 1–16
3. `CH1-40` — all 40 input channels (strips 1–40 fit a 40-strip bank)
4. `AUX` — aux inputs
5. `BUSES` — mix buses 1–16
6. `USER1` — all OFF
7. `USER2` — all OFF

### 1.8 BCF Customizations (Base.snap vs Init)

Base.snap makes targeted changes to the C section:
- **C bank 1 (DCA)**: Only DCAs 1–8 active (strips 9–16 turned OFF). Init shows DCAs 1–16.
- **C bank 4 (BUSES)**: `ofs=8` — shifts to show from strip 9 onward (buses 9–16 first? needs verification)
- **C bank 5 (USER1)**: Custom mix — DCAs 1–5 on strips 1–5, then BUS(9)=Delay, BUS(11)=Reverb/Long, BUS(12)=Back Vox, BUS(10)=Reverb/Medium on strips 6–9. All using `dst=9` (links to user layer 9). Named "USER1".
- **C section `sel=12`**: Selected bank is 12 — unclear since only 6 banks exist. May be an artifact or refer to cross-section state.
- **L bank 6 (USER1)**: `ofs=4` in Base (vs `ofs=0` in James/Init)

**James.snap adds monitor mix banks** (team-specific customization on top of Base):
- **C bank 5 (USER1)**: 16 SEND strips — channels 13–16 and 25–28 × monitor buses 13–14. Provides a full monitor mix matrix for monitors 1 and 2 directly on the C section faders.
- **C bank 6 (USER2)**: Same 8 channels × monitor buses 15–16 (monitors 3 and 4).

This pattern — a dedicated monitor-send bank in the C section — is a practical workflow feature and a good candidate for being rendered by the DSL from team assembly data (which knows the vocal channels and monitor bus assignments).

---

## Section 2: `ce_data.user` — Custom User Layers (CC Edit)

### 2.1 Structure Overview

```
ce_data.user/
├── sel           // currently active user layer number (1–16)
├── mode          // global encoder mode (always "MGRP" in observed files)
├── cmode         // compact mode ("HA" in all observed files)
├── gpio          // 4 GPIO button assignments
├── user          // 4 aux button assignments
├── daw1–4        // DAW transport button assignments
├── 1–16          // numbered user layers (main CC layers)
├── U1–U4         // user button rows (hardware shortcut buttons)
├── D1–D4         // deep button rows
├── MM            // master module buttons
└── cuser         // custom user layer mapping {"1":1, "2":1, "3":1}
```

In all observed snap files: `sel=1`, `mode=MGRP`, `cmode=HA`.

### 2.2 User Layers 1–16 (Primary CC Layers)

These are the main custom control layers. Each has exactly 4 strips:

```json
"1": {
  "led": false,        // LED state
  "col": 1,            // strip color (1 = no color)
  "enc": { "mode": "SSND", "name": "Lead Monitor", "send": "BUS13" },
  "bu": { "mode": "SOF", "name": "Lead Send", "ch": 61 },
  "bd": { "mode": "OFF", "name": "" }
}
```

Each strip has three controls:
- **`enc`**: rotary encoder
- **`bu`**: button up (upper button)
- **`bd`**: button down (lower button)

### 2.3 User Layer Strip Control Modes

These are all modes observed across all snap files:

| Mode | Controls | Extra fields | Behavior |
|---|---|---|---|
| `OFF` | enc/bu/bd | none | No assignment |
| `FDR` | enc | `ch` | Fader control for channel/bus/DCA |
| `MUTE` | bu/bd | `ch` | Mute on/off |
| `SOF` | bu/bd | `ch` | Send on/off (gate for a send) |
| `SSND` | enc | `send` | Send level encoder (amount) |
| `INS1` | bu/bd | `ch` | Open Insert 1 (FX page) |
| `INS2` | bu/bd | `ch` | Open Insert 2 (FX page) |
| `DCA` | enc | `dca` | DCA group fader |
| `DCAMUTE` | bu/bd | `dca` | DCA group mute |
| `DAWBTN` | bu/bd | `btn` | DAW transport button (daw layers only) |
| `OTHER` | bu/bd | `other` | Unimplemented/future (seen once, value "TBA") |

### 2.4 Universal Channel Index (`ch` field)

The `ch` field in user layer mode objects uses a universal flat index:

| Range | Maps to |
|---|---|
| 1–40 | Input channels 1–40 |
| 41–48 | Aux inputs 1–8 |
| 49–64 | Mix buses 1–16 (49=Bus1, 50=Bus2, …, 64=Bus16) |
| 65–68 | Main outputs 1–4 |
| 69–76 | Matrix buses 1–8 |

Examples from James.snap:
- `ch: 25` → Input channel 25 (James vocal)
- `ch: 53` → Bus 5 (Melodic/Stream), since 53−48=5
- `ch: 57` → Bus 9 (Delay/Slap), since 57−48=9
- `ch: 61` → Bus 13 (Monitor/1), since 61−48=13

### 2.5 SSND `send` Field

The `send` field uses a human-readable bus name string: `"BUS1"` through `"BUS16"`. In observed data only BUS 9–11 (FX buses) and BUS 13–16 (monitors) appear. This string is a literal Wing identifier, not a number.

### 2.6 DCA Reference (`dca` field)

The `dca` field in `DCA` and `DCAMUTE` modes is the **DCA's name string**, not its number. Example: `"dca": "FX"` refers to the DCA named "FX" (which is DCA 5 in the current BCF setup).

**Critical implication**: DCA user layer references and `ae_data.dca[N].name` must stay synchronized. If the renderer sets DCA names, user layer strip references must use matching strings.

### 2.7 Peripheral Layer Types

| Layer keys | Strip controls | Notes |
|---|---|---|
| `U1`–`U4` | `bu` only | Hardware shortcut button rows |
| `D1`–`D4` | `bu` only | Deep button rows |
| `MM` | `bu` only | Master module buttons |
| `daw1`–`daw4` | `bu`/`bd` only | DAW transport buttons; use `DAWBTN` mode |
| `gpio` | `bu` only | GPIO button assignments |
| `user` (sub) | `bu`/`bd` | Aux user buttons |

These peripheral layers only have button controls, no encoder. Their strip structure omits `enc`.

### 2.8 James.snap User Layer Configuration

James has 4 active layers (1–3 content-rich, 4 with a single DCA assignment):

**Layer 1 — Monitor sends**:
- Strips 1–4: enc=SSND (BUS13–16 = monitor sends), bu=SOF (ch 61–64 = monitor bus on/off)
- *Purpose*: Quick access to four monitor levels + send gate

**Layer 2 — Lead/backing vocal processing**:
- Strip 1: enc=FDR (ch 25 = James vocal), bu=INS1 (James FX), bd=INS1 (Delay FX ch 57)
- Strip 2: enc=FDR (ch 53 = Bus 5 backing), bu=INS1 (reverb), bd=INS2 (chorus)
- *Purpose*: Vocal processing quick access

**Layer 3 — FX send levels**:
- Strips 1–3: enc=SSND (BUS9–11 = Delay/Reverbs), bu=SOF (FX bus on/off)
- Strip 4: enc=FDR (ch 60 = Bus 12 Back Vox), bu=SOF
- *Purpose*: FX return level management

**Layer 4 — FX DCA**:
- Strip 1: enc=DCA (dca="FX"), bu=DCAMUTE (dca="FX")
- *Purpose*: Master FX level + mute

Layers 5–16 and U1–U4, D1–D4, MM are all default (OFF) in James.snap.

---

## Section 3: `ce_data.cfg` — Console Preferences

```json
{
  "lights": { "btns": 10, "leds": 90, "meters": 40, "rgbleds": 50, ... },
  "rta": { "homedisp": "OFF", "eqdisp": "OVL", "homecol": "RD25", ... },
  "muteovr": false,
  "soloexcl": true,
  "selfsolo": true,
  "layerlinkl": false,
  "layerlinkr": false,
  "autoview": false,
  "csctouch": false,
  "autosel_L": false, "autosel_C": false, "autosel_R": false, ...
  "fdrbanking": false,
  "soffdr": "L/C",
  "sofbutton": "AUTO",
  "sofframe": false,
  "sofmode": false,
  "seldblclick": "OFF",
  "usrmode": "BUS",
  "mfdr": "OFF",
  "cscmode": "BUS",
  "rackmode": "CH",
  "busspill": false, "mainspill": false, "mtxspill": false,
  "dcaspill": false, "dcacc": false, "showfdr": false
}
```

Key field glossary:

| Field | Type | Description |
|---|---|---|
| `lights.*` | int | Brightness for buttons, LEDs, meters, RGB LEDs, LCDs (0–100 scale) |
| `rta.homedisp` | str | RTA display on home screen: `"OFF"`, `"1/3"`, `"1/4"` (octave bands) |
| `rta.eqdisp` | str | RTA in EQ screen: `"OVL"` (overlay), `"1/4"`, etc. |
| `rta.*col` | str | RTA color code: `"RD25"`, `"BL50"`, etc. |
| `rta.*tap` | str | RTA tap point: `"PRE"`, `"POST"`, `"IN"` |
| `muteovr` | bool | Mute override: global mute button overrides group mutes |
| `soloexcl` | bool | Exclusive solo (only one channel soloed at a time) |
| `selfsolo` | bool | Allow soloing the currently selected channel |
| `layerlinkl`/`layerlinkr` | bool | Link L/R fader layer scrolling across L/R physical sections |
| `autoview` | bool | Screen follows selected channel automatically |
| `csctouch` | bool | Channel select on fader touch |
| `autosel_*` | bool | Auto-select on fader touch per surface section |
| `fdrbanking` | bool | Fader banking mode (scroll banks by page vs. continuous) |
| `soffdr` | str | Which section's faders are used for sends-on-faders: `"L/C"` |
| `sofbutton` | str | SOF button behavior: `"AUTO"` |
| `sofframe` | bool | Show SOF frame indicator on channel strip |
| `seldblclick` | str | Double-click action: `"BUSFX"` (open FX), `"OFF"` |
| `usrmode` | str | Default user encoder mode: `"BUS"` (bus sends) |
| `mfdr` | str | Master fader source: `"MAIN.1"`, `"OFF"` |
| `cscmode` | str | Channel select mode: `"BUS"` |
| `rackmode` | str | Rack surface mode: `"CH"` (channels) |
| `busspill` | bool | Bus spill: touching a bus expands its member channels to faders |
| `dcaspill` | bool | DCA spill: touching a DCA expands member channels |
| `dcacc` | bool | DCA channel contribution mode (CC shows DCA assignment on channels) |
| `showfdr` | bool | Show fader level in channel detail view |

**BCF changes from Init defaults**:
- `csctouch`: True → False (no auto-channel-select on touch)
- `muteovr`: True → False
- `seldblclick`: `"BUSFX"` → `"OFF"` (James) / `"OFF"` (Base)
- `mfdr`: `"MAIN.1"` → `"OFF"` (Base and James)
- `sofframe`: True → False
- Lighting: `btns` 25→10, `rgbleds` 25→50, `main` 80→100
- RTA: `homedisp` `"1/3"` → `"OFF"`, colors changed to red theme (`"RD25"`)

---

## Section 4: `ce_data.safes` — Snapshot Recall Protection

Safes define which items are immune from snapshot recall. The encoding is a **string of ASCII characters** where each character position represents one item. Empty string (`""`) = no safes. The Init.snap default uses space-padded strings (same as "no safes"). James.snap uses empty strings (equivalent effect).

```json
{
  "ch": "",           // 40 chars: one per input channel
  "aux": "",          // 8 chars: one per aux input
  "bus": "",          // 16 chars: one per mix bus
  "main": "",         // 4 chars: one per main output
  "mtx": "",          // 8 chars: one per matrix bus
  "dca": "",          // 16 chars: one per DCA
  "mute": "",         // 8 chars: one per mute group
  "fx": "",           // 16 chars: one per FX slot
  "source": { ... },  // I/O source safes by card/connection type
  "output": { ... },  // I/O output safes by card/connection type
  "area": { ... },    // Surface area safes (LEFT, CENTER, RIGHT, etc.)
  "custom": "",       // Custom safes
  "setup": ""         // Setup safes
}
```

The `area` sub-section allows protecting entire surface sections from recall: `LEFT`, `CENTER`, `RIGHT`, `COMPACT`, `RACK`, `EXTERN`, `VIRTUAL`, `WINGEDIT`, `WEDIT`.

---

## Section 5: DCA and Mute Group Membership (`ae_data.*.tags`)

**This is in ae_data, not ce_data**, but is documented here because it's the primary mechanism for group assignments that affect custom views.

### 5.1 Encoding

The `tags` field on channels (`ae_data.ch[n].tags`) and buses (`ae_data.bus[n].tags`) is a comma-separated string of tag tokens:

```
"#M8"              → member of mute group 8
"#D5"              → member of DCA 5
"#D6,#M5,#D1,#M1"  → member of DCA 6, mgrp 5, DCA 1, mgrp 1 (multi-membership)
```

### 5.2 Base.snap Tag Assignments

Base.snap contains the infrastructure-level tag assignments on buses (channels default to empty):

| Bus | Name | Tags | DCA members | Mgrp members |
|---|---|---|---|---|
| 1 | DRUMS | `#D6,#M5,#D1,#M1` | DCA 6 (All No L), DCA 1 (Rhythm) | Mgrp 5 (Inst All), Mgrp 1 (Rhythm) |
| 2 | BASS | `#D6,#M5,#D1,#M1` | DCA 6, DCA 1 | Mgrp 5, Mgrp 1 |
| 3 | Inst/House | `#D6,#M5,#D2,#M2` | DCA 6, DCA 2 (Inst B) | Mgrp 5, Mgrp 2 (Inst B) |
| 4 | Inst/Stream | `#D6,#M5,#D2,#M2` | DCA 6, DCA 2 | Mgrp 5, Mgrp 2 |
| 5 | Back Vox | `#D6,#M6,#D3,#M3` | DCA 6, DCA 3 (Vox B) | Mgrp 6 (Vox All), Mgrp 3 (Vox B) |
| 6 | Lead/House | `#M5,#D4,#M4,#M6` | DCA 4 (Leads) | Mgrp 5, Mgrp 4 (Leads), Mgrp 6 |
| 7 | Lead/Stream | `#M5,#D4,#M4,#M6` | DCA 4 | Mgrp 5, Mgrp 4, Mgrp 6 |
| 9 | Delay/Slap | `#D5` | DCA 5 (FX) | none |
| 10 | Delay/Repeat | `#D5` | DCA 5 | none |
| 11 | Reverb/Medium | `#D5` | DCA 5 | none |
| 12 | Reverb/Long | `#D5` | DCA 5 | none |
| 13–16 | Monitor/1–4 | `#D7,#M7` | DCA 7 (Monitors) | Mgrp 7 (Monitors) |

Buses 8, 17+ (mains, matrix) have no tags in Base.snap.

### 5.3 Channel-Level Tags

Base.snap channels: channels 1–4 (drums) and 13–24 (some named, many blank) have `#M8`. All other channels have empty tags.

James.snap channels: all 18 active channels (1–8 drums, 13–16 instruments, 25–30 vocals) have `#M8`. No DCA membership on channels themselves — DCA membership for channels flows through the buses they feed.

### 5.4 Multi-Membership

Tags support multiple DCA and mute group memberships simultaneously. The order within the comma-separated string appears to be first-added order (no canonical ordering observed). The renderer must produce the full comma-separated list.

---

## Section 6: Other `ce_data` Sections (Non-critical for Phase 3)

### `ce_data.daw`
DAW controller config. Fields: `on`, `conn`, `emul`, `config`, `ccup`, `disjog`, `preset`. Used for HUI/MCU DAW integration. Not relevant for Phase 3 complexity levels.

### `ce_data.midi`
MIDI control enable flags: `enchctl`, `enfxctl`, `encustctl`, `ensysex`, `enmidicc`, `enscenes`, `enshowctl`, `enscenetx`. All boolean. Not relevant for Phase 3.

### `ce_data.osc`
Minimal: `{ "ronly": <bool> }`. Read-only OSC flag.

### `ce_data.gpio`
GPIO button configuration. 4 buttons with `bu.mode` assignments. Part of `ce_data.user.gpio` sub-field.

---

## Section 7: Rendering Implications for Phase 3

### 7.1 What Phase 3 Needs to Render

| Feature | ce_data section | DSL needs |
|---|---|---|
| Custom fader views for beginners | `ce_data.layer` (USER1/USER2 banks) | `layer_banks:` list in assembly |
| Encoder/button assignments | `ce_data.user` (layers 1–16) | `user_layers:` list with strip modes |
| DCA group fader assignments | `ae_data.dca[n].name/fdr/mute` + `tags` | `dca:` section in assembly |
| Mute group assignments | `ae_data.mgrp[n].name` + `tags` | `mute_groups:` section in assembly |
| Console behavior prefs | `ce_data.cfg` | Optional `console_prefs:` block |
| Simplified DCA view | `ce_data.layer` C section bank | Part of complexity strategy |

### 7.2 User Layer DSL Shape (Proposed)

A user layer needs to express:
```yaml
user_layers:
  - id: 1  # layer number 1-16
    strips:
      - enc: { mode: SSND, send: BUS13, name: "Mon 1" }
        bu:  { mode: SOF, ch: BUS13, name: "Send On" }
        bd:  { mode: OFF }
      ...
```

The `ch` field in DSL should ideally use logical names (e.g., `BUS13`, `CH25`) that the renderer converts to universal indices. The `send` field in SSND mode already uses the `BUSn` string format that maps directly to JSON.

### 7.3 DCA Name Coupling

User layer strips reference DCAs by name string (`"dca": "FX"`). If the DSL controls DCA naming, the user layer strips in that same assembly must use matching names. This is a **strong coupling** — name changes require updating both `ae_data.dca[n].name` and every `user.*` strip referencing that DCA.

Design options:
1. **Reference by number** in DSL, resolve to name at render time (renderer looks up DCA name)
2. **Reference by logical name** in DSL, validate that the DCA with that name exists in the rendered ae_data

Option 1 is more robust and matches the "reference by logical ID, render to concrete JSON" pattern.

### 7.4 Layer Bank Customization DSL Shape (Proposed)

A simplified beginner layer bank could be expressed as:
```yaml
layer_banks:
  section: C
  bank: 5
  name: "Quick Mix"
  ofs: 0
  strips:
    - { type: DCA, i: 1, dst: 1 }   # Rhythm
    - { type: DCA, i: 4, dst: 1 }   # Leads
    - { type: DCA, i: 7, dst: 1 }   # Monitors
    - { type: OFF }
    ...
```

### 7.5 Tags Rendering

DCA and mgrp membership is expressed in the `tags` field of channels and buses. The renderer needs to:
1. Collect all DCA and mgrp memberships declared for a channel/bus
2. Render them as `#Dn` and `#Mn` tokens
3. Comma-join them in the `tags` field
4. Preserve any existing tags from Base.snap that aren't overridden (if using pass-through approach)

Tags can appear on both input channels (`ae_data.ch[n].tags`) and buses (`ae_data.bus[n].tags`). In the current BCF, DCA grouping is primarily on buses (the submix buses are in DCAs), not on individual input channels.

### 7.6 Snapshot vs. Global Scope

**Everything in ce_data is snapshot-recalled.** There is no ce_data content that is global-only and therefore unrenderable. The `safes` field can protect items from being overridden on recall, but the renderer generates complete snapshots — safes are only relevant for partial recall on the hardware.

---

## Questions for Matthew

1. **`ofs` field in layer banks**: Base.snap has C bank 4 with `ofs=8` and C bank 5 with `ofs=4`. I believe this controls which strip is shown first at the leftmost physical fader. Could you confirm: does C bank 5 with `ofs=4` display starting from fader position 5 (skipping positions 1–4)? Or does it scroll within the strip list so that strip 5 appears at physical fader 1? This affects how we generate the beginner DCA view.

2. **`dst` field for CH/BUS/DCA strips**: I understand `dst` links a fader strip to a user layer for the encoder/button section. Base.snap C bank 5 uses `dst=9` for its custom DCA strips. Is `dst=9` intentional (linking to a specific user layer 9), or is this a leftover value from editing? What behavior does an operator see when they touch one of those DCA faders?

3. **`sel=12` in Base.snap C section**: The C section only has banks 1–6, but `sel=12`. Is this valid (selecting a bank by some other scheme), or is it a stale/corrupt value? Does the console just clamp to the last bank?

4. **DCA reference by name vs. number**: User layer strips reference DCAs by their name string (`"dca": "FX"`). For Phase 3, should the DSL specify DCA assignments by number (`dca: 5`) and the renderer resolve to name at render time? Or is there value in name-based references in the DSL?

5. **User layers and complexity tiers**: The existing James/Levin setup uses user layers 1–4. For Phase 3 simplified views, should we:
   - Overwrite layers 1–4 with simplified content in the "beginner" complexity tier?
   - Use different user layer slots (e.g., 5–8) so the regular layers remain available?
   - Have two separate layer banks (USER1/USER2 in the L/C/R sections) where one is for standard use and one for simplified use?

6. **Tags ownership**: Currently, bus DCA/mgrp tags are in Base.snap (infrastructure level), and channel tags (`#M8`) are in James.snap (team level). For Phase 3, when the renderer manages DCA assignments, should it write tags to channels (assigning input channels directly to DCAs) in addition to buses? Or should DCA membership remain bus-level only?

7. **`ce_data.cfg` rendering**: Are there any console preferences that should differ between complexity tiers? For example, should the beginner snapshot have `dcaspill=true` (so touching a DCA expands its channels to faders) while the advanced snapshot does not? Or should cfg be treated as a stable infrastructure setting that doesn't vary by complexity?
