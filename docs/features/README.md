# Snapwright Feature Map

Post-Phase-2 work breakdown. Each feature gets its own `docs/features/<name>/brief.md`.
Use `coding-workflow` skill for session management.

## Architecture

```
Init.snap (factory reset — the only opaque binary, never modified)
    ↓
infrastructure.yaml (every diff from Init documented with purpose)
    ↓
team/assembly.yaml (musicians, channels, monitors, personal mixer)
    ↓
strategy.yaml (optional: beginner/advanced overlays)
    ↓
rendered .snap file
```

Init.snap replaces Base.snap as the rendering foundation. The infrastructure layer
is transparent YAML — auditable, version-controlled, and evolvable. Base.snap is
retained as a historical reference but is no longer used in rendering.

## Dependency Graph

```
                    ┌──────────────────┐
                    │ infrastructure-  │  Foundation: Init + infrastructure YAML
                    │ dsl              │  replaces opaque Base.snap
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
    ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
    │ bus-         │  │ tags-       │  │ infra-       │
    │ rendering    │  │ ownership   │  │ channels     │
    └──────┬──────┘  └──────┬──────┘  └──────┬───────┘
           │                │                │
           └────────────────┼────────────────┘
                            ▼
              ┌──────────────────────────┐
              │    dca-mgrp-rendering    │
              └──────────┬───────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
  ┌──────────────┐ ┌───────────┐ ┌──────────────────┐
  │ strategy-    │ │ user-     │ │ personal-mixer-  │
  │ overlays     │ │ layers    │ │ routing          │
  └──────────────┘ └───────────┘ └──────────────────┘
```

---

## Feature Inventory

### Tier 0: Foundation

#### `infrastructure-dsl`
**What**: Replace opaque Base.snap with a two-layer DSL: Init.snap (factory reset) + infrastructure.yaml (documented changes). The renderer uses Init.snap as the template instead of Base.snap.
**Why**: 
- Every parameter that differs from factory has a documented purpose
- Eliminates accumulated debris (phantom DCAs, stale names, mystery channels, accidental fader bumps)
- Enables slow evolution of any infrastructure component (oscillator channel, personal mixer layout, headset EQ, monitor config)
- Git history on readable YAML instead of opaque binary diffs
- Enables pi-assisted infrastructure modifications
**Scope**:
- Design infrastructure.yaml format covering: bus config (names, faders, dynamics, colors, tags), DCA config (names, faders), mgrp config (names), channel infrastructure (talkback, computer, handheld, headset, piano — name/color/icon/input/processing), main output config (names, EQ, limiters, faders), FX slot loading, talkback routing, monitor output config, IO input config (stage box gains/names), IO output routing (main feeds, monitor feeds, personal mixer feeds), console preferences (ce_data.cfg)
- Renderer change: `snap_template()` loads Init.snap instead of Base.snap, applies infrastructure layer, then applies team assembly
- Incremental coverage: start with the sections we actively need (buses, DCAs, mgrps, channels, IO routing), expand to others over time. Unmodeled sections pass through from Init (which is correct by definition)
- Investigation A output is the reference for what to include
**Decision inputs resolved**:
- ch37, mtx1 +10dB, A.8-30 +0.5dB gain, A.7 "JEN" — all accidental, omit from infrastructure
- Monitor bus faders ~-20dB — keep as infrastructure defaults
- Buses 4-5, 7-8 — unused, omit from infrastructure
- Init.snap from Wing Edit 3.3.1 — compatible with current console firmware

#### `priscilla-spelling`
**What**: Fix `Pricilla` → `Priscilla` in musician YAML.
**Why**: Typo confirmed.
**Scope**: One-line fix + regenerate.

### Tier 1: Renderer Extensions (depend on infrastructure-dsl)

#### `bus-rendering`
**What**: Renderer writes bus configuration from infrastructure + assembly DSL to `ae_data.bus[N]`.
**Why**: 8 of 12 active buses currently render with wrong names. Bus dynamics, colors, and faders are also unmanaged.
**Scope**: 
- Infrastructure layer defines bus names, colors, faders, dynamics for all 16 buses
- Assembly can override bus names for team-specific buses (e.g., bus 12 = "Back Vox" vs "Delay/Rhythm")
- Renderer writes `name`, `col`, `fdr`, and dynamics config to `ae_data.bus[N]`
- TDD from day one

#### `tags-ownership`
**What**: Renderer owns `ch.tags` and `bus.tags` completely — rebuilds from DSL declarations.
**Why**: Current tags are "correct by coincidence" for some channels, missing for others, and broken for all DCA/mgrp bus memberships.
**Scope**: 
- Infrastructure layer declares mute group and DCA membership for buses
- Assembly declares #M8 (Worship) membership for all active channels
- Renderer builds tag strings from declarations — no pass-through from Init/Base
- TDD — tag building is a pure function

#### `infra-channels`
**What**: Infrastructure channels (Piano, Computer, Headset, Talkback, optionally Oscillator) defined in infrastructure layer.
**Why**: These appear in all/most team snapshots but are invisible to the renderer. Custom views need named channels.
**Scope**: 
- Infrastructure layer defines these channels with name, color, icon, input routing, and processing
- Renderer applies infrastructure channel config before team assembly
- Oscillator included initially but can be removed later if not needed

### Tier 2: Group Configuration (depends on Tier 1)

#### `dca-mgrp-rendering`
**What**: Renderer writes DCA and mute group configuration from infrastructure DSL.
**Why**: DCAs 1-7 are phantom faders with zero members in team snaps. Monitor mute group is broken. DCA 5 silently crushed FX returns.
**Scope**: 
- Infrastructure layer defines DCA names, faders (default 0dB), member buses
- Infrastructure layer defines mgrp names and member buses/channels
- Renderer writes `ae_data.dca[N]` and `ae_data.mgrp[N]`
- Membership flows through tags system (depends on `tags-ownership`)
- Simplified grouping: Rhythm (bus1+drums), Instruments (bus2-3), Vocals (bus6), FX (bus9-12), Monitors (bus13-16)

### Tier 3: Routing & Complexity (depends on Tier 2)

#### `personal-mixer-routing`
**What**: Renderer manages User Signal channels and Matrix bus config for personal mixer stems.
**Why**: USR assignments (Lead 1 = which vocalist) change per team and are easily forgotten. Matrix buses provide grouped stems to personal mixers.
**Scope**:
- Infrastructure layer defines: matrix bus names/faders, AES50 A.33-48 output routing map (which slots carry USR, which carry MTX — this is infrastructure, same across teams)
- Assembly layer defines: USR source assignments (which musician → which USR slot, with tap point PRE/POST)
- Renderer writes `io.in.USR[N]` and `io.out.A[33-48]` and `ae_data.mtx[N]`
**Current state**: James/Levin/Priscilla have identical A.33-48 routing; only USR sources differ per team. Jen/Kana/Morks have it all OFF.
**Depends on**: `infrastructure-dsl`, `infra-channels` (Piano ch15 referenced by USR 4)

#### `strategy-overlays`
**What**: Composable strategy system — named profiles that bundle processing and view decisions.
**Why**: Core complexity-level goal. "Filbert is on his second week — keep it simple."
**Scope**:
- Strategy file format (e.g., `strategies/beginner.yaml`)
- Strategy flags: `gates: off`, `eq_model: SOUL`, `eq_preset: simple-3band`, DCA grouping choice, user layer choice
- Render CLI: `snapwright render james --strategy beginner`
- Named profiles as bundles of flags
- Individual flags composable: `snapwright render james --no-gates --simple-eq`
**Design**: Strategy overlays apply after musician resolution, before rendering. They're a transform pass over the resolved channel configs.
**Depends on**: `dca-mgrp-rendering` (for DCA grouping strategies), `tags-ownership` (for membership)

#### `user-layers`
**What**: Renderer writes `ce_data.user[N]` custom user layers from DSL/strategy config.
**Why**: Beginner mixing view — 4-5 DCA faders on the center section instead of 40 channels.
**Scope**:
- DSL schema for user layer strip configuration
- Logical-to-physical name resolution (DSL says `monitor_1`, renderer writes `ch: 61`)
- Strategy profiles include user layer definitions
- Beginner profile: DCA strips for Rhythm, Instruments, Vocals, FX, Monitors
**Depends on**: `dca-mgrp-rendering` (DCA names must exist for user layer references), `strategy-overlays` (delivery mechanism)

---

## Suggested Starting Order

1. **`priscilla-spelling`** — 5 minutes, ship it
2. **`infrastructure-dsl`** — the foundation. Design the YAML format, switch renderer from Base.snap to Init.snap + infrastructure layer
3. **`bus-rendering`**, **`tags-ownership`**, **`infra-channels`** — can run in parallel after infrastructure-dsl
4. **`dca-mgrp-rendering`** — after Tier 1 lands
5. **`personal-mixer-routing`** — after infrastructure-dsl + infra-channels
6. **`strategy-overlays`** — after dca-mgrp-rendering
7. **`user-layers`** — after dca-mgrp-rendering + strategy-overlays

Items 3 are good candidates for parallel sessions.
Items 5-7 are the meaty design work and benefit from the foundation being solid first.

---

## Reference

- Investigation outputs: `docs/investigations/` (A through E)
- Decisions to date: `docs/decisions.md`
- Wing param reference: `docs/wing-param-map.md`
- Init.snap: `data/reference/Init.snap`
- Base.snap: `data/reference/Base.snap` (historical reference only)
