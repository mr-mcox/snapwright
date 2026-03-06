# Decisions

### 2025-03-05 — Reference snapshots: copy subset, not full backup
**Decision**: Copied Base.snap + 6 Sunday Starters (James, Priscilla, Levin, Morks, Jen, Kana) into `data/reference/`. Not the full 125-snapshot backup.
**Rationale**: These cover the active team snapshots and enough variety for structural analysis. Full backup is 40MB+ of historical snapshots we don't need in the repo.
**Category**: autonomous

### 2025-03-05 — Python 3.12+, standard tooling
**Decision**: Target Python 3.12+. Pydantic for schema, Click for CLI, PyYAML for DSL, deepdiff for comparisons.
**Rationale**: Matches existing project conventions (logseq-navigator). Pydantic is specified in the project brief for schema validation.
**Category**: autonomous

### 2026-03-06 — Steel thread uses throwaway channel-frame DSL
**Decision**: Phase 0 DSL works in channel-frame (explicit `channel: 1`) to prove round-trip. The instrument-frame DSL (musician configs, templates, inheritance) gets designed in Phase 1 once we understand what the renderer needs.
**Rationale**: Need to validate Wing JSON tooling and tolerances before designing the abstraction layer; channel-frame is honest scaffolding, not premature architecture.
**Category**: autonomous

### 2026-03-06 — DSL naming conventions: short standard audio terms
**Decision**: Use short standard names (`hpf`, `freq`, `gain`, `threshold`) rather than Wing's internal abbreviations (`lc`, `f`, `g`, `thr`) or fully spelled out (`high_pass_filter_frequency`).
**Rationale**: Readable to audio engineers without being verbose; Wing abbreviations are cryptic.
**Category**: autonomous

### 2026-03-06 — Send omission means off
**Decision**: DSL only lists active sends. Omitted sends render to `on=false, lvl=-144, mode=POST`.
**Rationale**: 24 sends per channel, typically 1-3 active — explicit listing of all sends would be noise.
**Category**: autonomous

### 2026-03-06 — Input source uses explicit group label
**Decision**: Input source expressed as `source: stage-box, input: 2` rather than compact `A2` or inferred group.
**Rationale**: Only one card installed but other source types exist (local, talkback). Explicit group avoids inference ambiguity.
**Category**: autonomous

### 2026-03-06 — Always-default params omitted from DSL, hardcoded in renderer
**Decision**: Params like `solosafe`, `mon`, `clink`, `proc`, `tapwid`, `phase_invert`, `delay`, `eq_mix` stay out of the DSL and get Wing defaults in the renderer.
**Rationale**: These are never tweaked across any reference snapshots; DSL should express intent, not echo defaults.
**Category**: autonomous

### 2026-03-06 — Physical layout explicit through Phase 2, resolver needed in Phase 3
**Decision**: Phase 1-2 use explicit physical assignments in assembly files. Phase 3 (complexity levels) is where a layout resolver gets built if needed.
**Rationale**: Different complexity levels may need different channel counts and routing topologies, which is the first case where the system needs to make assignment decisions.
**Category**: autonomous