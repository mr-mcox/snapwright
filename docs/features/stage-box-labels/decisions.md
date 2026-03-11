## Decisions

### 2026-03-09 — preamp_gain on musician, not InputAssignment

**Context**: Brief originally specified `preamp_gain` on `InputAssignment` (alongside `source`
and `input`). Before implementation, the user revised this: gain is a property of the
instrument/person, not of the cable plug.

**Choice**: `preamp_gain: float | None = None` added to `InstrumentLayer` and `MusicianEntry`.
`InputAssignment` stays as `source + input` only.

**Alternatives considered**: Keeping it on `InputAssignment` (original brief constraint).

**Rationale**: How loud a kick drum hits a preamp depends on the drum, the mic, and how
it's positioned — not which stage box slot it's plugged into. Musician files already carry
all the other per-instrument characteristics (fader, EQ, dynamics). Gain belongs there too.
It also means gain can be set once in the musician file and flow to any team that uses that
musician, with per-team overrides available through `MusicianEntry`.

---

### 2026-03-09 — Flute preamp_gain sourced from Priscilla reference

**Context**: In the James assembly, flute is at slot 15, but the James.snap reference shows
"Violin" at slot 15 — the assembly has been updated since that reference was saved. No direct
reference value exists for flute's gain in a James context.

**Choice**: Used `33` (from Priscilla team reference, where flute appears at slot 7 with g=33).

**Alternatives considered**: Leaving gain unset (would render as 0); guessing a value.

**Rationale**: 33 dB is consistent with what was set for flute on the Priscilla team. It's
the best available calibrated value. Can be refined when a fresh James reference is captured.

---

### 2026-03-09 — Violin preamp_gain sourced from old James slot 15

**Context**: Violin is now at slot 18 in the James assembly, but the reference shows "Keys"
at slot 18. The reference does show "Violin" at slot 15 (g=45.5), confirming the assembly
reorganized these slots after the reference was saved.

**Choice**: Used `45.5` (from James.snap A[15], where violin was before the slot rearrangement).

**Alternatives considered**: Leaving unset; using Priscilla reference.

**Rationale**: The value at A[15] is the actual measured gain for violin on this team. The slot
number changed but the instrument gain didn't.
