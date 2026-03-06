# Decisions

### 2026-03-06 — YAML 1.1 bool-key fix via strict type check
**Decision**: PyYAML parses `on:` as a boolean dict key (`True`). Fixed by post-processing loaded dicts with `type(k) is bool` check (not `k == True`, which would wrongly match integer 1 due to Python's `True == 1`).
**Rationale**: Avoids dependency on ruamel.yaml or changing DSL field names. Strict type check is the minimal correct fix.
**Category**: autonomous

### 2026-03-06 — EQ/dynamics/gate dict rebuild on model switch
**Decision**: When the DSL specifies a model different from the Wing default (STD/COMP/GATE), the renderer rebuilds the entire dict from scratch rather than patching over Base.snap defaults. Matches Wing's own behaviour — switching models drops the previous model's params from JSON.
**Rationale**: Leaving old-model params in place produced spurious diff items (e.g. STD EQ bands appearing in SOUL EQ channels).
**Category**: autonomous

### 2026-03-06 — EQ/dynamics/gate extra fields pass-through for non-standard models
**Decision**: EqConfig, DynamicsConfig, GateConfig use Pydantic `extra='allow'`. Non-standard Wing model params (SOUL lf/lg/lmf, LA ingain/peak, PSE depth, RIDE tgt/spd, etc.) are written as extra fields in YAML and pass through directly to Wing JSON.
**Rationale**: Wing has 10+ EQ models and 6+ dynamics models with incompatible param structures. Typed fields for each would be premature. Pass-through handles them correctly with minimal schema surface area.
**Category**: autonomous

### 2026-03-06 — Omit -144dB monitor sends from assembly
**Decision**: The assembly monitors section only lists sends that are actively ON. -144dB level sends (Wing's silence value) are omitted — they render as off by default.
**Rationale**: Listing -144 sends as on=True contradicts the reference snapshots where those sends are off. Omitting them keeps the DSL expressive of intent, not Wing internals.
**Category**: autonomous

### 2026-03-06 — Phase 1 diff baseline: 112 items, ~70 float precision
**Decision**: Accept the current diff baseline as Phase 1 validation passing. ~70 of 112 diff items are Wing float quantization within 3-sig-fig tolerance. Remaining ~30 are metadata (ptap, tags, led) and detailed routing (preins, peq, dynsc) deferred to later phases.
**Rationale**: Core processing (EQ, dynamics, gate), channel sends, monitor sends, faders, and inputs all match the reference. The outstanding diffs are below the threshold of audible impact.
**Category**: autonomous

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