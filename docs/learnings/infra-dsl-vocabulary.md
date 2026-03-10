# Infrastructure DSL Vocabulary

_Last updated: 2026-03-09 (infra-dsl-vocabulary feature)_

This document records the current state of human-readable vs Wing-native field
names in `infrastructure.yaml`, the reasoning behind the split, and the
evaluation framework for future translation work.

---

## Why the split exists

`infrastructure.yaml` serves two jobs:
1. **IaaC record** — what the house console intentionally looks like post-reset
2. **Feedback-loop anchor** — the thing you edit when service experience says
   "the house compressor is pumping, pull back the ratio" or "vocals are
   swamping the room, lower the threshold"

Wing-native field names (`thr`, `att`, `rel`, `mdl`, `in`, `out`, `2g`) make
job 2 harder: you have to know Wing internals to read or edit the file. DSL
vocabulary (`threshold`, `attack`, `release`, `model`, `input`, `output`,
`bands`) makes it legible to a trained operator without Wing expertise.

The translation layer lives entirely in `infrastructure.py`. `infrastructure.yaml`
is a pure data file; `infrastructure.py` maps DSL vocabulary → Wing field names
and handles Wing encoding artifacts (e.g. SBUS `rel` stored as a string, 76LA
`ratio` stored as `"20"` not `20`).

---

## Evaluation framework

When deciding whether to translate a parameter, ask:

> **Would a trained operator want to evolve this value based on service feedback?**

- **Yes** → translate. The operator needs to read and edit it; Wing-native names
  are friction.
- **No / set-once preset** → leave as Wing-native. Translation cost isn't worth
  it for values that are established once and never revisited.
- **Maybe / deferred** → note it here. Don't translate speculatively, but flag
  it so the decision is conscious when the use case materialises.

---

## Current vocabulary state

### Fully translated (human-readable in YAML)

| DSL name | Wing field | Where used |
|---|---|---|
| `model` | `mdl` | bus dyn, main dyn |
| `threshold` | `thr` | bus dyn (SBUS) |
| `attack` | `att` | bus dyn, main dyn |
| `release` | `rel` | bus dyn, main dyn — also encodes the Wing string artifact |
| `ratio` | `ratio` | bus/main dyn — numeric in YAML; 76LA string encoding is hidden |
| `input` | `in` | main dyn (76LA Input knob) |
| `output` | `out` | main dyn (76LA Output knob) |
| `bands: {N: {gain, freq, q}}` | `Ng`, `Nf`, `Nq` | bus EQ, main EQ |
| `high_shelf: {gain, freq, q}` | `hg`, `hf`, `hq` | main EQ |
| `low_shelf: {gain, freq, q}` | `lg`, `lf`, `lq` | (available; not yet used) |

Structural identity keys (`name`, `color`→`col`, `icon`, `led`, `tags`) were
already a mix — `name` is already human-readable, `color` was already mapped via
`_BUS_FIELD_MAP`. These predate the vocabulary feature.

### Wing-native (intentional — FX preset blobs)

FX internal parameters (`erpdly`, `ertype`, `ersize`, `lxo`, `mxo`, `hxo`,
`mtype`, `mrate`, `dcy`, `diff`, etc.) are preset-blob data: set once when the
FX type is chosen, never operator-tuned based on service feedback. Naming them
costs significant effort with zero feedback-loop value.

`mdl` inside FX slots is technically translatable to `model` but has been left
as Wing-native for now — FX models are also set-once, and translating `mdl`
alone while leaving the rest of the blob untouched would create inconsistency
within the FX section. The right time to translate FX `mdl` is if/when we build
structured FX DSL for the high-value parameters (see Candidates below).

### Wing-native (deferred — identity metadata)

| Wing field | DSL candidate | Deferred because |
|---|---|---|
| `icon: 210` (numeric) | `icon: drums-kit` or similar | Requires a full icon name map; no feedback-loop use case yet. Useful long-term for visual rig setup docs. |
| `col: 8` (numeric) | `color: orange` or similar | Same as icon — useful for visual docs, zero feedback-loop value. |

When icon/color become a pain point (e.g. writing setup docs, or building a
visual rig diagram), the pattern is the same as dynamics: add a map in
`infrastructure.py`, use readable names in the YAML.

### Masked entirely

**Bus 8** — never operator-configured; factory debris left over from the
initial console setup. Removed from `infrastructure.yaml` and skipped in the
firmware patch (`apply_firmware_patches` skips bus 8 by number). Masked in
`scripts/infra_diff.py` so diff harness tests are unaffected.

---

## Path forward for specific candidates

### Routing parameters (`main: {1: {on, lvl}}`, send modes)

Bus and main routing (`on`, `lvl`, `mode`) are **already readable** — `on`/`lvl`
are clear, and `POST`/`PRE` are Wing's own vocabulary. The values an operator
tunes (mix bus levels to house/stream, monitor routing flags) are legible as-is.

If routing becomes a pain point (e.g. expressing "this bus goes to house but not
stream" declaratively), the right move is a higher-level routing DSL key rather
than renaming individual `on`/`lvl` fields. No work needed now.

### FX high-value parameters

Some FX parameters inside blobs have clear human names and genuine feedback-loop
use (e.g. `dcy` → `decay`, `time` → `time`, `rep` → `repeats`, `lc` →
`low_cut`, `hc` → `high_cut`). These are candidates if we find ourselves
reaching into the blob to tune them after services.

The escalation trigger from the original brief is the right gate: "if a FX
parameter has obvious high-character-impact and a clear human name, surface it."
Don't pre-translate speculatively — wait for the moment you want to tune it.

### Other dynamics models

If we ever add buses with dynamics models other than SBUS or 76LA (e.g. NSTR,
9000C, LA), the same `_BUS_DYN_DSL_MAP` / `_translate_bus_dyn` pattern applies.
Add the model-specific string-encoding logic if Wing requires it, same as SBUS
`rel` and 76LA `ratio`.

### Gate / sidechain EQ on buses

Bus `dynsc` (sidechain EQ) parameters are currently set only by the firmware
patch, not by `infrastructure.yaml`. If we add explicit sidechain EQ config to
a bus, `dynsc.q` etc. are already in Wing-native form. Translate if we get to
the point of operator-tuning sidechain filters.
