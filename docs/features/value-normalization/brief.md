---
feature: value-normalization
date: 2026-03-09
commit: 6e48f10
branch: main
status: solution-space
read-when: "starting implementation"
---

## Problem

DSL source files contain floating-point noise captured from real service snapshots:
faders at -0.1 dB when the intent was 0, sends at -3.08 when the intent was -3.
This makes diffs between snapshot cycles full of sub-threshold chatter, obscuring
meaningful changes (Anna's gain is consistently up, Jen's threshold is consistently
lower). Before beta, the sources need a single quantization pass to establish a clean
starting point for evolution tracking.

## Not Doing

- Modifying source files in place — originals stay immutable
- A configurable coarse/fine system — one well-chosen set of tolerances per type
- Quantizing boolean, enum, or string fields
- EQ frequency quantization beyond the fixed 5 Hz tolerance (intentional HPF values like 101.7 Hz matter)

## Constraints

- CLI: `snapwright normalize <input-dir> --output <output-dir>` writes quantized copies of all YAML DSL files
- Tolerances are named constants (not config): faders/levels to nearest 0.5 dB, EQ gain to nearest 0.5 dB, EQ frequency to nearest 5 Hz, preamp gain to nearest 0.5 dB
- Values outside any threshold are passed through unchanged
- Source files are never overwritten — the command always writes to a separate output location
- Output files are valid DSL (parseable by existing loader/schema) — normalization does not restructure YAML

## Escalation Triggers

- If any rounded value would fail schema validation (e.g. a frequency rounded out of a valid range), pause
- If the 0.5 dB fader tolerance would collapse intentionally different sends to the same value, pause — tolerance may need adjustment for sends vs bus faders

## Decisions

(populated during implementation)
