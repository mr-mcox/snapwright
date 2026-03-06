# Snapwright Roadmap

## Current Phase: Steel Thread (Phase 0)

**Goal**: Prove end-to-end round-trip without loss on a single channel.

### What the structural analysis revealed

From comparing James, Priscilla, and Levin Sunday Starters:

- **Snapshots are ~95% identical** (~20,200 of 21,100 params match between any pair)
- **Shared channels** (kick, snare, tom, overhead) differ only in fader levels and 1-2 sends — processing is inherited from a common base
- **Team-specific content is thin**: different instruments on ch5-8 and ch13-16, different vocalists on ch25-30, fader/send tweaks
- **Bus layout is stable across teams**: Drums/Rhythm/Melodic submixes (1-5), Vocals (6), FX (9-11), Monitors (13-16). Only Bus12 varies (Back Vox vs Delay/Rhythm)
- **James ≈ Levin processing lineage**: kick drum has 264/267 identical params. Priscilla diverged earlier or from a different base
- **Priscilla's vocal channels are ghosts**: unnamed, muted, but retain send routing from a base snapshot — this is the partial-load problem in action
- **~267 params per channel**, ~21K params per full snapshot

### Steel thread plan

1. **Pick one shared channel** (Kick, ch1) from James snapshot
2. **Map the Wing JSON structure** for that channel to understand all 267 params
3. **⚠️ ESCALATE: Propose DSL schema** for representing that channel
4. **Build minimal renderer**: DSL YAML → Wing JSON for one channel
5. **Round-trip test**: render → diff against original → measure gap
6. **⚠️ ESCALATE: Review tolerances** — what's noise vs meaningful diff
7. **Expand**: add processing (EQ, dynamics, gate), then sends, then second channel

### Success criteria
- Rendered single-channel JSON matches original within agreed tolerances
- Test suite validates the round-trip
- DSL is readable and maps to audio concepts Matthew recognizes

---

## Phase 1: Basics + Team Generation
Render full team snapshots from DSL. Replace manual partial-load workflow.

## Phase 2: Semantic Diffing
Compare expected vs actual snapshots. LLM-interpreted reports.

## Phase 3: Complexity Levels
Same DSL source renders simple/standard/complex snapshots.

## Phase 4: Promotion & Refinement
Close the loop: diff → DSL updates → regenerate.

---

## Key reference files
- `data/reference/Base.snap` — BCF base configuration
- `data/reference/sunday-starters/James.snap` — primary reference for steel thread
- Project brief: `/Users/mcox/Downloads/wing-snapshot-dsl-project-brief.md`
