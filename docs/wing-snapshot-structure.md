# Wing Snapshot JSON Structure

Reference documentation derived from analyzing BCF's actual snapshots (2025-12-14 backup).

## Top-level keys

```
type                 "snapshot.8"
creator_fw/sn/model  Firmware and device metadata
created              Timestamp
active_show/scene    Current show/scene paths
ae_data              Audio engine data (the meat)
ce_data              Control engine data
ae_globals           Audio engine globals
ce_globals           Control engine globals
```

## ae_data structure

| Key | What | Count |
|-----|------|-------|
| `cfg` | Global config (solo, monitoring, talkback, RTA) | — |
| `io` | Physical I/O routing and patching | — |
| `ch` | Input channels | 40 (keyed "1"-"40") |
| `aux` | Auxiliary inputs | — |
| `bus` | Mix buses | 16 (keyed "1"-"16") |
| `main` | Main outputs | 4 (keyed "1"-"4") |
| `mtx` | Matrix outputs | 8 (keyed "MX1"-"MX8") |
| `dca` | DCA groups | — |
| `mgrp` | Mute groups | — |
| `fx` | Effects processors | — |
| `cards` | Expansion card config | — |
| `play` | Playback | — |
| `rec` | Recording | — |

## Channel structure (~267 params each)

```
ch.{n}.in          Input routing and gain
ch.{n}.flt         Filter config
ch.{n}.clink       Channel link settings
ch.{n}.col         Color
ch.{n}.name        Display name (string)
ch.{n}.icon        Icon ID
ch.{n}.led         LED settings
ch.{n}.mute        Mute state (bool)
ch.{n}.fdr         Fader level (float, dB; -144 = -inf)
ch.{n}.pan         Pan position
ch.{n}.wid         Width
ch.{n}.solosafe    Solo safe
ch.{n}.mon         Monitor settings
ch.{n}.proc        Processing order
ch.{n}.ptap        Pre/post tap
ch.{n}.peq         Pre-EQ (before dynamics)
ch.{n}.gate        Gate settings
ch.{n}.gatesc      Gate sidechain
ch.{n}.eq          Main EQ (6-band parametric + LC/HC)
ch.{n}.dyn         Dynamics/compressor
ch.{n}.dynxo       Dynamics crossover
ch.{n}.dynsc       Dynamics sidechain
ch.{n}.preins      Pre-insert
ch.{n}.main        Main bus assignments
ch.{n}.send        Bus sends (keyed "1"-"16" + "MX1"-"MX8")
ch.{n}.postins     Post-insert
ch.{n}.tags        Tags
```

## EQ structure

```
eq.on              Enable (bool)
eq.lc.on           Low-cut enable
eq.lc.f            Low-cut frequency (Hz, float)
eq.lc.slope        Low-cut slope
eq.{1-6}.g         Band gain (dB)
eq.{1-6}.f         Band frequency (Hz)
eq.{1-6}.q         Band Q factor
eq.{1-6}.type      Band type
eq.hc.on           High-cut enable
eq.hc.f            High-cut frequency
eq.hc.slope        High-cut slope
```

## Dynamics structure

```
dyn.on             Enable (bool)
dyn.mode           Compressor mode
dyn.thr            Threshold (dB)
dyn.ratio          Ratio
dyn.knee           Knee width
dyn.mgain          Makeup gain
dyn.attack         Attack time
dyn.hold           Hold time
dyn.release        Release time
dyn.mix            Wet/dry mix
```

## Send structure

```
send.{bus_num}.on    Send enable (bool)
send.{bus_num}.lvl   Send level (dB, float)
send.{bus_num}.pan   Send pan
send.{bus_num}.pre   Pre/post fader
```

## BCF Channel Layout (from Sunday Starters analysis)

| Range | Role | Stable across teams? |
|-------|------|---------------------|
| Ch 1-4 | Core drums (Kick, Snare, Tom, Overhead) | ✅ Names and processing stable |
| Ch 5-8 | Rhythm section / extras | ❌ Team-specific (Bass, Congas, Bongos, Violin) |
| Ch 9-12 | Unused in current snapshots | ✅ Empty |
| Ch 13-16 | Melodic instruments | ❌ Team-specific (Guitar, Flute, Piano, Violin) |
| Ch 17-24 | Mostly unused | ✅ Sparse |
| Ch 25-30 | Vocals | ❌ Team-specific singers |
| Ch 36 | Oscillator | ✅ Always muted |
| Ch 37-38 | Speech mics (Handheld, Headset) | ✅ Shared processing |
| Ch 39 | Computer | ✅ Always muted |
| Ch 40 | Talkback | ✅ Always muted |

## BCF Bus Layout

| Bus | Name | Role | Stable? |
|-----|------|------|---------|
| 1 | DRUMS | Drum submix | ✅ |
| 2 | Rhythm/House | Rhythm section → house | ✅ |
| 3 | Rhythm/Stream | Rhythm section → stream | ✅ |
| 4 | Melodic/House | Melodic → house | ✅ |
| 5 | Melodic/Stream | Melodic → stream | ✅ |
| 6 | Vocals | Vocal submix | ✅ |
| 7-8 | (unused) | — | ✅ |
| 9 | Delay/Slap | FX send | ✅ |
| 10 | Reverb/Medium | FX send | ✅ |
| 11 | Reverb/Long | FX send | ✅ |
| 12 | Back Vox / Delay/Rhythm | Varies by team | ❌ |
| 13-16 | Monitor/1-4 | Monitor sends | ✅ |

## Main outputs

| Main | Name | Notes |
|------|------|-------|
| 1 | HOUSE | PA system; fader varies widely by team (-35 to -9 dB) |
| 2 | STREAM | Livestream; more consistent levels |
| 3-4 | (unused) | At -70 / -144 dB |
