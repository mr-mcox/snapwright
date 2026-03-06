# Wing Channel Parameter Map

Reference for all 267 parameters in a Wing input channel (`ae_data.ch.N`).
Derived from James.snap ch1 (Kick). Used to inform the Phase 1 instrument-frame DSL design.

---

## Top-level keys

| Key | Description | In DSL? |
|---|---|---|
| `in` | Input routing and preamp settings | partial |
| `flt` | Input filters (HPF, LPF, Tilt) | yes |
| `clink` | Channel link | no (hardcoded) |
| `col` | Color index | yes |
| `name` | Channel name | yes |
| `icon` | Icon index | yes |
| `led` | LED on/off | no (hardcoded) |
| `mute` | Mute state | yes |
| `fdr` | Fader level (dB) | yes |
| `pan` | Pan (-100..100) | no (hardcoded 0) |
| `wid` | Width | no (hardcoded) |
| `solosafe` | Solo safe | no (hardcoded) |
| `mon` | Monitor assignment | no (hardcoded) |
| `proc` | Processing chain order (e.g. GEDI) | no (hardcoded) |
| `ptap` | Parallel tap point | no (hardcoded) |
| `peq` | Pre-EQ (3-band) | no (unused in all snapshots) |
| `gate` | Gate / expander | yes |
| `gatesc` | Gate sidechain | no (hardcoded) |
| `eq` | Main EQ | yes |
| `dyn` | Dynamics (compressor/leveler) | yes |
| `dynxo` | Dynamics crossover | no (hardcoded) |
| `dynsc` | Dynamics sidechain | no (hardcoded) |
| `preins` | Pre-fader insert | no (hardcoded off) |
| `main` | Main bus outputs (1-4) | no (all off in all snapshots) |
| `send` | Bus sends (1-16) + Matrix sends (MX1-8) | yes |
| `tapwid` | Tap width (firmware default 100) | no (hardcoded) |
| `postins` | Post-fader insert | no (hardcoded off) |
| `tags` | Channel tags (e.g. #M8) | no |

---

## `in` — Input (18 params)

### `in.set` (8 params)

| Wing key | Description | Notes |
|---|---|---|
| `srcauto` | Auto source select | always false |
| `altsrc` | Alternate source active | always false |
| `inv` | Phase invert | always false in all snapshots |
| `trim` | Input trim (dB) | always 0 |
| `bal` | Input balance | always 0 |
| `dlymode` | Delay mode (M = milliseconds) | always M |
| `dly` | Delay value | always 0.100000001 (firmware default, not audible) |
| `dlyon` | Delay enabled | always false |

### `in.conn` (4 params)

| Wing key | DSL field | Notes |
|---|---|---|
| `grp` | `input.source` | A=stage-box, B=local, C=usb |
| `in` | `input.input` | 1-based input number within group |
| `altgrp` | — | always OFF |
| `altin` | — | always 1 |

---

## `flt` — Input Filters (9 params)

| Wing key | DSL field | Notes |
|---|---|---|
| `lc` | `filters.hpf_on` | HPF (low-cut) on/off |
| `lcf` | `filters.hpf_freq` | HPF frequency (Hz) |
| `lcs` | — | HPF slope ("24" dB/oct); firmware default, absent from Base.snap |
| `hc` | `filters.lpf_on` | LPF (high-cut) on/off |
| `hcf` | `filters.lpf_freq` | LPF frequency (Hz) |
| `hcs` | — | LPF slope ("12" dB/oct); firmware default, absent from Base.snap |
| `tf` | `filters.tilt_on` | Tilt filter on/off |
| `mdl` | — | Tilt model (always TILT) |
| `tilt` | — | Tilt amount (always 0) |

---

## `eq` — Main EQ (20 params)

| Wing key | DSL field | Notes |
|---|---|---|
| `on` | `eq.on` | |
| `mdl` | `eq.model` | STD in all snapshots |
| `mix` | — | always 100 |
| `lg` | `eq.low_shelf.gain` | dB |
| `lf` | `eq.low_shelf.freq` | Hz |
| `lq` | — | always 0.997970223 (Wing's "Q=1.0") |
| `leq` | — | always SHV (shelf type) |
| `1g`–`4g` | `eq.bands[n].gain` | dB |
| `1f`–`4f` | `eq.bands[n].freq` | Hz |
| `1q`–`4q` | `eq.bands[n].q` | Wing quantizes 1.0 → 0.997970223 |
| `hg` | `eq.high_shelf.gain` | dB |
| `hf` | `eq.high_shelf.freq` | Hz |
| `hq` | — | always 0.997970223 |
| `heq` | — | always SHV |

---

## `dyn` — Dynamics (14 params, ECL33 model)

The ECL33 (leveler + compressor combo) replaces the standard COMP model.
Base.snap uses COMP; all team snapshots use ECL33. Full struct is replaced when model changes.

| Wing key | DSL field | Notes |
|---|---|---|
| `on` | `dynamics.on` | |
| `mdl` | `dynamics.model` | ECL33 or COMP |
| `mix` | — | always 100 |
| `gain` | — | always 0 |
| `lon` | `dynamics.leveler.on` | ECL33 only |
| `lthr` | `dynamics.leveler.threshold` | dB; ECL33 only |
| `lrec` | `dynamics.leveler.recovery` | ms, stored as string; ECL33 only |
| `lfast` | `dynamics.leveler.fast` | ECL33 only |
| `con` | `dynamics.compressor.on` | ECL33 only |
| `cthr` | `dynamics.compressor.threshold` | dB; ECL33 only |
| `ratio` | `dynamics.compressor.ratio` | ECL33 only |
| `crec` | `dynamics.compressor.recovery` | ms, stored as string; ECL33 only |
| `cfast` | `dynamics.compressor.fast` | ECL33 only |
| `cgain` | — | always 0 |

---

## `gate` — Gate / Expander (7 params)

| Wing key | DSL field | Notes |
|---|---|---|
| `on` | `gate.on` | |
| `mdl` | — | always GATE |
| `thr` | `gate.threshold` | dB |
| `range` | `gate.range` | dB |
| `att` | `gate.attack` | ms |
| `hld` | `gate.hold` | ms |
| `rel` | `gate.release` | ms |
| `acc` | — | always 0 |
| `ratio` | — | always 1:3 |

## `gatesc` — Gate Sidechain (4 params)

Always at defaults in all snapshots. Hardcoded.

---

## `send` — Bus and Matrix Sends (24 × 6 = 144 params)

Each send has 6 fields: `on`, `lvl`, `pon`, `mode`, `plink`, `pan`.

| Send keys | Purpose | Default mode | Default plink |
|---|---|---|---|
| `1`–`12` | Mix/FX buses | POST | False |
| `13`–`16` | Monitor buses | PRE | False |
| `MX1`–`MX8` | Matrix sends | PRE | True |

DSL: only active sends listed. Omitted sends render to off at -144 dB with the default mode for their group.

---

## Known firmware differences (Base.snap vs team snapshots)

| Field | Base.snap | Team snapshots | Handling |
|---|---|---|---|
| `flt.lcs` | absent | "24" | patched in renderer |
| `flt.hcs` | absent | "12" | patched in renderer |
| `in.set.dly` | 0 | 0.100000001 | patched in renderer |
| `send.MX*.mode` | POST | PRE | renderer default |
| `send.MX*.plink` | False | True | renderer default |
| `send.13-16.mode` | POST | PRE | renderer default |
| `dyn.mdl` | COMP | ECL33 | expressed in DSL |
