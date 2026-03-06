# Decisions

### 2026-03-06 — DSL three-section assembly structure
**Decision**: Assembly files have three clear sections: *who they are* (musicians + inheritance + offsets/overrides), *where they sit* (channels + inputs + buses), *what they hear* (monitors). Musicians are named, configured, then assigned to channels separately.
**Rationale**: Separating identity from physical placement means the same musician config works across teams at different channel positions. Mirrors how Matthew thinks about it — people first, desk layout second.
**Category**: escalated

### 2026-03-06 — Kustomize-style ordered overlays for inheritance
**Decision**: `inherits` is an ordered list. Each entry deep-merges over the previous, last writer wins. Inline `overrides` mask everything. `offsets` are additive on top of the fully resolved result. Linear stack, no diamond inheritance.
**Rationale**: Solves positional reuse (e.g., `near-drums.yaml` applied to multiple musicians) without complex merge logic. Kustomize has proven the mental model.
**Category**: escalated

### 2026-03-06 — Offsets are level-only, overrides are absolute
**Decision**: `offsets` section is for level-type parameters only (fader, gain, send levels) — always relative, always dB. `overrides` section is always absolute value replacement. Two separate sections, no ambiguity.
**Rationale**: You nudge levels but you set thresholds/frequencies/ratios. Mixing relative and absolute in the same block creates type ambiguity. Separate sections make intent obvious.
**Category**: escalated

### 2026-03-06 — Assembly variants for team variations
**Decision**: When a team has different configurations (e.g., Jen on piano vs guitar), create multiple assembly files that render to multiple snapshots. Volunteer loads the appropriate one.
**Rationale**: Simpler than runtime switching. Regenerating weekly isn't practical; having 3-4 pre-built variants per team is.
**Category**: escalated

### 2026-03-06 — Channel presets as future output format
**Decision**: Note channel presets (Wing `.chn` format) as a future render target alongside full snapshots. Not Phase 1 scope.
**Rationale**: Enables ad-hoc reuse — import Jen's vocal preset onto any snapshot without regenerating. Useful for unplanned team changes.
**Category**: escalated

### 2026-03-06 — Monitors explicit in assembly, intelligence deferred
**Decision**: Monitor send levels are explicit per-team in the assembly. No position-awareness logic or musician-driven monitor preferences in Phase 1.
**Rationale**: Monitor balance depends on person + stage position + room acoustics. Too complex to model now. Capture data, use LLM intelligence later.
**Category**: escalated

### 2026-03-06 — Complexity levels shape-compatible but deferred to Phase 3
**Decision**: DSL structure should not fight complexity levels (intro/easy/standard/full rendering from same source), but implementation is Phase 3. Phase 1 renders one complexity level per assembly.
**Rationale**: Real use case (volunteer skill progression), but routing topology changes are significant work. Keep the interface clean now, build later.
**Category**: escalated

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

### 2026-03-06 — Round-trip tolerance: 3 significant figures
**Decision**: Rendered values match target if they agree to 3 significant figures. Wing stores DSL values with its own float quantization (e.g. `177.0` → `176.972168`, `1.0` Q → `0.997970223`); these are within tolerance.
**Rationale**: 3 sig figs is finer than any audible distinction on this desk; covers all Wing float quantization observed in practice.
**Category**: escalated

### 2026-03-06 — Wing Q quantization treated as noise
**Decision**: DSL authors write round Q values (e.g. `q: 1.0`); renderer stores them as-is; Wing's internal Q encoding (0.997970223 for "1.0") is accepted as noise under the 3 sig fig rule. No Q scale encoding in renderer.
**Rationale**: 0.2% error on Q is inaudible; encoding Wing's internal scale is premature complexity for Phase 0.
**Category**: escalated

### 2026-03-06 — Physical layout explicit through Phase 2, resolver needed in Phase 3
**Decision**: Phase 1-2 use explicit physical assignments in assembly files. Phase 3 (complexity levels) is where a layout resolver gets built if needed.
**Rationale**: Different complexity levels may need different channel counts and routing topologies, which is the first case where the system needs to make assignment decisions.
**Category**: autonomous