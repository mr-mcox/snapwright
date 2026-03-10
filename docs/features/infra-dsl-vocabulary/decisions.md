## Decisions

### 2026-03-09 — Bus 8: skip firmware patch instead of YAML reset

**Context**: Bus 8's EQ Q reset block in infrastructure.yaml existed solely to
counteract the global firmware patch — not because bus 8 has any operator-tuned
EQ. Removing the YAML block (per brief) means the firmware patch would change
bus 8's Q to sqrt2, breaking tests that verify bus 8 stays at Init default.

**Choice**: Skip bus 8 in `apply_firmware_patches` rather than keeping a YAML
reset block. The result (bus 8 Q stays at Init default) is identical; the
mechanism is more honest — bus 8 was never configured, so the firmware patch
has nothing to correct.

**Alternatives considered**:
1. Keep a minimal bus 8 block in YAML with just the Q overrides — keeps bus 8
   fully driven from YAML but is still implementation-artifact noise.
2. Skip in firmware patch (chosen) — removes the artifact entirely.

**Rationale**: The YAML should express operator intent. A firmware-correction
block for a channel that was never configured is pure implementation noise.
Skipping in the patch is cleaner and the test assertions remain valid.

---

### 2026-03-09 — `input`/`output` vocabulary for 76LA

**Context**: The 76LA limiter uses Wing field names `in` and `out` for its
Input and Output level knobs. These are key tuning parameters — "house is
always hitting the limiter, adjust the threshold" means adjusting `in`. The
brief says "DSL vocabulary must match what the channel renderer already uses —
no new names invented", but the channel renderer has no equivalent for these
76LA-specific knobs.

**Choice**: Use `input` and `output` as DSL names, translating to `in`/`out`
in `infrastructure.py`. These exactly match the hardware faceplate labels on
the 1176-style limiter.

**Alternatives considered**:
1. Keep `in`/`out` in YAML — preserves the "no new names" constraint but `in`
   is collision-prone (also used for input routing) and both are opaque.
2. Use `input`/`output` (chosen) — unambiguous, match hardware labels, extend
   the spirit of the renderer's vocabulary consistently.

**Rationale**: The constraint is about consistency, not literalism. `input` and
`output` are the obvious human names for these controls and introduce no
ambiguity or conflict with existing renderer vocabulary.

---

### 2026-03-09 — EQ band format: dict keyed by band number

**Context**: The channel renderer addresses EQ bands as a positional array
(`bands: [{gain, freq, q}, ...]`). Infrastructure needs to patch specific bands
(e.g. bus 13 patches only bands 4 and 5; Main HOUSE patches all 6 bands plus
high shelf). A positional array would require padding with null entries for
unaddressed bands.

**Choice**: Use a dict keyed by band number (`bands: {4: {freq: ...}, 5: {freq:
...}}`). The leaf vocabulary (`gain`, `freq`, `q`) is identical to the renderer.

**Alternatives considered**:
1. Positional array matching the renderer exactly — would require null/empty
   entries for all bands not being patched; clutters Monitor/1 entry.
2. Dict by band number (chosen) — sparse, only specifies what changes,
   leaf names are consistent with renderer vocabulary.

**Rationale**: Structural difference between channel renderer (always writes all
bands for a complete channel) and infrastructure (patches specific bands of
pre-existing bus/main EQ) justifies the dict format. Leaf vocabulary (`gain`,
`freq`, `q`) is unchanged from the renderer, maintaining consistency.
