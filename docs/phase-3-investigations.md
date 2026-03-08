# Phase 3 Investigations

Pre-work to inform Phase 3 (Complexity Levels) sequencing and design.
Each investigation is scoped for an independent session.

---

## Investigation A: Base.snap Audit

**Purpose**: Catalog every non-default value in `Base.snap` by diffing against `Init.snap` (factory reset). Separate intentional design choices from accumulated debris.

**Inputs**:
- `data/reference/Base.snap` — current BCF base configuration
- `/Users/mcox/Documents/Wing Backup/Init.snap` — factory-initialized Wing snapshot

**Method**:
1. Leaf-level diff of Init vs Base across `ae_data` and `ce_data`
2. Categorize each difference:
   - **Intentional infrastructure** — bus naming, routing, talkback setup, monitor sources, I/O config
   - **Active configuration** — DCA names/levels, mute group names, EQ on monitor outputs, talkback assignments
   - **Suspected debris** — values that look like experiments or leftovers (e.g., non-default processing on unused channels, orphaned bus routing, stale names on unused DCA/mgrp slots)
   - **Unknown** — things that need Matthew's input to classify
3. For each category, produce a table with path, Init value, Base value, and a plain-English label

**Output**: `docs/investigations/base-audit.md` — a categorized inventory of Base.snap's customizations, with specific questions for Matthew about unknowns.

**Why this matters**: The Base.snap is the foundation every rendered snapshot inherits from. Debris in Base propagates to all teams. Understanding what's intentional vs stale also tells us what the renderer needs to manage vs what it can safely ignore. This also directly enables future workflows where we adjust Base.snap configuration via the DSL.

**Known leads from preliminary scan**:
- Bus names in James.snap still show old 4-bus structure ("Rhythm/House", "Melodic/House") despite DSL consolidation — likely Base.snap origin
- Channels 15 (Piano), 18 (Sanctuary), 29 (Kana), 30 (Elizabeth), 36 (Oscillator), 39 (Computer) are named in James.snap but not in the DSL — some may be Base.snap inhabitants
- DCAs 1-7 have names and non-zero faders; DCA 5 ("FX") at -16.4 dB could be affecting FX bus levels silently
- Mute groups 1-6 have custom names but unclear if any channels are actually assigned to them (membership is via `tags` field — `#M5`, `#M6` on some buses)
- `#M8` ("Worshp") tag is on every active channel — this is the one mute group in active use

---

## Investigation B: Control Surface Structure Mapping

**Purpose**: Document the Wing's `ce_data` JSON structure — layers, user layers, CC Edit — so we understand what we can render and how.

**Inputs**:
- `Init.snap` — factory defaults for all control surface config
- `James.snap` — a configured example
- `Base.snap` — current BCF state

**Method**:
1. Map `ce_data.layer` (L/C/R sections): what does each bank's strip assignment mean (`type`/`i`/`dst` fields), how many banks per section, how strips map to faders
2. Map `ce_data.user` — the custom user layers (1-16 plus named ones: U1-U4, D1-D4, MM, daw1-4, gpio). Each strip has `enc`/`bu`/`bd` modes and color. What modes are available and what do they control?
3. Map `ce_data.cfg` — console preferences (auto-select, spill modes, fader banking, etc.)
4. Identify which `ce_data` sections are snapshot-recalled vs global (some Wing settings are "show" level, not "snapshot" level)
5. Document how DCA/mgrp membership actually works: the `tags` field on channels/buses uses `#M<n>` for mute group and `#D<n>` for DCA assignment — verify this encoding

**Output**: `docs/investigations/control-surface-map.md` — a reference doc similar to `wing-param-map.md` but for the console engine side.

**Why this matters**: Complexity levels require rendering custom user layers (the beginner fader view), DCA assignments (grouping channels for simplified mixing), and potentially layer bank customization. We currently have zero renderer coverage of `ce_data`. This map tells us what's possible and what the DSL needs to express.

---

## Investigation C: DCA & Mute Group Membership Audit

**Purpose**: Determine what's actually wired up in the current DCA and mute group assignments, and what's stale.

**Inputs**:
- `James.snap`, `Base.snap`, other Sunday Starters in `data/reference/sunday-starters/`

**Method**:
1. Parse `tags` field across all channels, buses, auxes, mains in James.snap to build a membership map: which sources belong to which DCA and mute group
2. Cross-reference with DCA fader levels — a DCA with members and a non-unity fader is actively affecting the mix
3. Repeat for Base.snap to distinguish team-specific from infrastructure-level assignments
4. Compare across Sunday Starters (Priscilla, Levin, etc.) to see if groups are consistent or per-team
5. Flag specific concerns: DCA 5 "FX" at -16.4 dB with potential members, mute groups 1-6 with custom names but potentially no members

**Output**: `docs/investigations/dca-mgrp-audit.md` — membership tables, impact assessment, and recommendations for cleanup.

**Why this matters**: DCAs are the primary mechanism for the beginner custom views — we need to understand what's already there before designing new assignments. Stale DCA assignments with non-unity faders are actively and silently scaling channel levels. Mute groups need to be rationalized (keep Worship, possibly Monitors, clean up the rest).

---

## Investigation D: Renderer Scope Assessment

**Purpose**: Audit what the current renderer handles vs. what Phase 3 will require, and identify the gap.

**Inputs**:
- `snapwright/dsl/renderer.py` — current rendering code
- `snapwright/dsl/schema.py` — current DSL schema
- The assembly files for James and Priscilla teams

**Method**:
1. Catalog every `ae_data` section and which ones the renderer currently touches:
   - ✅ `ch` (channels — EQ, dynamics, gate, filters, sends, faders, names, inputs)
   - ✅ `bus` (naming, some config)
   - ❓ `dca`, `mgrp`, `fx`, `aux`, `main`, `mtx`, `cfg` — check coverage
2. Catalog `ce_data` coverage (expected: zero)
3. For each Phase 3 capability, identify what renderer additions are needed:
   - **Gate disable** → renderer must support `gate.on: false` override (may already work)
   - **EQ model switch** → renderer already handles model switching (SOUL, LA, etc.)
   - **DCA assignments** → needs: `tags` field rendering on channels, DCA naming/config in `ae_data.dca`
   - **Custom user layers** → needs: `ce_data.user` rendering (strip assignments, modes, colors)
   - **Layer bank customization** → needs: `ce_data.layer` rendering
   - **Labels/naming** → renderer handles `ch.name`; check bus, DCA, mgrp, main naming
4. Assess Phase 1 renderer code quality — does it need a TDD rewrite (per the dev pattern) before adding Phase 3 complexity, or is it solid enough to extend?

**Output**: `docs/investigations/renderer-scope.md` — gap analysis with specific items to build, plus recommendation on whether Phase 1 renderer needs refactoring first.

**Why this matters**: This is the technical feasibility check. The modular complexity system ("turn collections of strategies on and off") needs a renderer that can compose features. If the current renderer is monolithic or brittle, we should know before designing the DSL extensions.

---

## Investigation E: Labeling & Naming Inventory

**Purpose**: Catalog all user-visible names/labels across the snapshot and compare intended vs actual state.

**Inputs**:
- `James.snap`, `Base.snap`, `Init.snap`
- Current DSL assembly and musician files

**Method**:
1. Extract all `name` fields from: channels (1-40), buses (1-16), auxes (1-8), DCAs (1-16), mute groups (1-8), mains (1-4), matrix (1-8), FX slots (1-16)
2. Compare James vs Base — which names are team-specific vs infrastructure
3. Compare Base vs Init — which names are BCF customization vs factory
4. Cross-reference with DSL — which names does the renderer currently set vs inherit from Base
5. Flag inconsistencies: e.g., bus names showing old 4-bus naming while DSL uses new names, channels named in snapshot but absent from DSL

**Output**: `docs/investigations/naming-inventory.md` — complete name map with provenance (Init/Base/team/DSL-rendered) and inconsistencies.

**Why this matters**: Labels are critical for usability, especially for beginners. The custom user layer strips show the channel/bus name — if those names are stale or inconsistent, the beginner view is confusing. This also surfaces channels/buses that exist in the snapshot but aren't managed by the DSL, which is input to the "clean base" effort.

---

## How These Feed Phase 3 Design

After all five investigations are complete, we'll have:

1. **A clean base** (A + E) — know what to keep, what to clean, what the DSL should manage
2. **Control surface vocabulary** (B) — know how to express custom views and DCA assignments in the DSL
3. **Current state reality** (C + E) — know what's actively affecting the mix vs stale
4. **Technical gap** (D) — know what to build and in what order
5. **Design inputs for the modular complexity system** — enough understanding to design the DSL extensions for composable "strategies" (gate on/off, EQ model choice, DCA groupings, custom views)

The investigations are independent and can run in parallel. Results should be reviewed together before committing to Phase 3 design.
