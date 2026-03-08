# Snapwright Roadmap

## ~~Phase 0: Steel Thread~~ ✓ COMPLETE — [phase-0-steel-thread commits on main]

**Goal**: Prove end-to-end round-trip without loss on a single channel. Build reusable Wing JSON tooling. ✓ Done.

## ~~Phase 1: Instrument-Frame DSL + Team Generation~~ ✓ COMPLETE

**Goal**: Design real DSL from instrument/musician frame. Render full team snapshots (James + Priscilla). Replace manual partial-load workflow.

### What the structural analysis revealed

From comparing James, Priscilla, and Levin Sunday Starters:

- **Snapshots are ~95% identical** (~20,200 of 21,100 params match between any pair)
- **Shared channels** (kick, snare, tom, overhead) differ only in fader levels and 1-2 sends — processing is inherited from a common base
- **Team-specific content is thin**: different instruments on ch5-8 and ch13-16, different vocalists on ch25-30, fader/send tweaks
- **Bus layout is stable across teams**: Drums/Rhythm/Melodic submixes (1-5), Vocals (6), FX (9-11), Monitors (13-16). Only Bus12 varies (Back Vox vs Delay/Rhythm)
- **James ≈ Levin processing lineage**: kick drum has 264/267 identical params. Priscilla diverged earlier or from a different base
- **Priscilla's vocal channels are ghosts**: unnamed, muted, but retain send routing from a base snapshot — this is the partial-load problem in action
- **~267 params per channel**, ~21K params per full snapshot

### What Phase 0 is de-risking

1. **Wing JSON fidelity** — can we parse and write .snap files without corruption?
2. **Defaults baseline** — Base.snap as the "zero state"; how does merging unset params work in practice?
3. **Floating point tolerances** — Wing stores `0.100000001` and `198.56604`. What precision matters?
4. **Param structure assumptions** — do the 267 params per channel decompose cleanly, or are there hidden dependencies?
5. **Surprise params** — values that don't mean what we think, or that change together unexpectedly

### What carries forward from Phase 0

- `snapwright/wing/` — parser, writer, defaults, Pydantic models for Wing's JSON structure
- `snapwright/diff/` — comparison tooling, tolerance rules
- `docs/wing-param-map.md` — annotated parameter grouping reference
- `tests/` — round-trip test infrastructure and reference fixtures

### What gets thrown away

- The channel-frame YAML format (replaced by instrument-frame DSL in Phase 1)
- The minimal renderer in `snapwright/steel_thread/` (replaced by real rendering pipeline)
- Any hardcoded channel-number assumptions

### Steel thread plan

1. ~~**Pick one shared channel** (Kick, ch1) from James snapshot~~ ✓
2. ~~**Map the Wing JSON structure** for that channel — all 267 params~~ ✓
3. ~~**Pick conventions for throwaway DSL** — naming, defaults, send omission~~ ✓ (autonomous)
4. ~~**Build Wing JSON tooling**: parser, writer, defaults extraction from Base.snap~~ ✓
5. ~~**Build minimal channel-frame renderer**: throwaway YAML → Wing JSON for ch1~~ ✓
6. ~~**Round-trip test**: render → diff against James.snap ch1 → measure gap~~ ✓
7. ~~**⚠️ ESCALATE: Review tolerances** — 3 sig figs, Q quantization as noise~~ ✓
8. ~~**Expand to full channel**: add EQ, dynamics, gate, filters~~ ✓
9. **Document Wing param map** — grouped reference for future DSL design

### Success criteria
- Rendered single-channel JSON matches James.snap ch1 within agreed tolerances
- Test suite validates the round-trip
- Wing tooling (parser/writer/defaults) is solid enough to build on
- We understand what the real DSL needs to express

---

## Phase 1: Instrument-Frame DSL + Team Generation

**Goal**: Design the real DSL from the instrument/musician frame. Render full team snapshots. Replace manual partial-load workflow.

**Physical layout**: Explicit in assembly files. You write `kick: { channel: 1 }` in the team assembly. No resolver needed — the human decides channel assignments.

**Key work**:
- Design instrument-frame DSL (inherits from templates, musician base configs)
- Assembly format: maps instruments → physical channels/buses for a team
- Template system: `templates/kick-drum.yaml` defines shared processing
- Override system: team-specific tweaks layer on top
- Renderer: DSL + assembly → complete Wing snapshot
- Generate all team snapshots from DSL source

**Escalation points**: DSL shape, inheritance model, assembly format, template boundaries

---

## ~~Phase 2: Snapshot Evolution Analysis~~ ✓ COMPLETE

**Goal**: Batch-compare post-service snapshots against a baseline to surface recurring adjustments worth promoting into DSL templates.

**What got built**:
- `snapwright/evolution/` module: `significance` (threshold policy), `translate` (Wing paths → audio labels), `diff` (channel and snapshot diffing), `patterns` (batch pattern detection), `report` (markdown output)
- `snapwright analyze-evolution` CLI command
- Pi skill at `.pi/skills/snapshot-evolution/` for periodic analysis sessions
- Session folder pattern at `data/evolution/` (intent + report + decisions per session)
- Baseline strategy: rendered DSL for single-team, `Base.snap` for cross-team
- Prototype written first, learnings captured, then TDD rewrite — 63 tests covering significance thresholds, translation correctness, and diff behaviour
- First real session: `data/evolution/2026-03-07-james-over-time/`

---

## Phase 3: Complexity Levels

Same DSL source renders simple/standard/complex snapshots.

**Physical layout**: This is where a layout resolver may be needed. Different complexity levels might use different channel counts, subgroup structures, or routing topologies. If simple mode skips subgroups, the channel-to-bus mapping changes. This is the first phase where the system needs to make physical assignment decisions.

---

## Phase 4: Promotion & Refinement

Close the loop: diff → DSL updates → regenerate.

---

## Future: Architecture Review

Before or alongside Phase 3, step back and review how the whole system has evolved.
Potential outputs: a system diagram, assessment of whether Phase 1 DSL/renderer code
needs a TDD rewrite similar to the Phase 2 evolution module, and a decision on whether
any cross-phase refactoring is warranted before adding more complexity.

---

## Key reference files
- `data/reference/Base.snap` — BCF base configuration
- `data/reference/sunday-starters/James.snap` — primary reference for steel thread
- Project brief: `/Users/mcox/Downloads/wing-snapshot-dsl-project-brief.md`
