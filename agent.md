# Snapwright — Agent Context

Snapwright generates Behringer Wing digital mixer snapshots from a YAML-based DSL.
The system renders `.snap` files (JSON) that the Wing loads to configure channels, buses,
processing, routing, and control surface state for live sound at a church.

## Toolchain

- **Python 3.12+**, managed with **uv** (not pip, not conda)
- Run tests: `uv run pytest`
- Run CLI: `uv run snapwright <command>`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format --check .`
- Install dev deps: `uv sync --group dev`

## Quality Gates

**All tests must pass before presenting a diff for review.** Run `uv run pytest -q` and
`uv run ruff check .` before calling anything done. If you find a pre-existing failing
test you didn't break, flag it immediately — don't normalize it.

## TDD Policy

Derived from the operator profile's phase-aware model:

| Domain | Intensity | What that means |
|--------|-----------|-----------------|
| Rendering logic (sends, models, paths) | Thorough | Tests first. Clear inputs → expected outputs. |
| Schema validation, key normalization | Thorough | Pure functions with known edge cases — test them. |
| Integration (full pipeline, snapshot diff) | Basic | Diff against reference snapshots. Not unit-level. |
| Scaffolding, CLI wiring, file I/O | None/Basic | Test if non-trivial; skip if it's just plumbing. |

"Thorough" means: write the test, watch it fail, write the implementation. Not retroactive.

## Architecture

```
Init.snap (factory reset — opaque binary, never modified)
    ↓
infrastructure.yaml (every diff from factory documented with purpose)
    ↓
team/assembly.yaml (musicians, channels, monitors)
    ↓
rendered .snap file
```

Key modules:
- `snapwright/wing/` — parser, writer, defaults (Wing JSON tooling)
- `snapwright/dsl/` — schema (Pydantic), loader (YAML + inheritance), renderer (DSL → Wing JSON)
- `snapwright/evolution/` — snapshot diff analysis for promoting adjustments
- `data/reference/` — Init.snap, Base.snap (historical), reference snapshots
- `data/dsl/` — YAML source files (musicians, teams, infrastructure)

## Key Invariants

- **Init.snap is never modified** — it's the factory-reset foundation
- **Infrastructure YAML is the single source of truth** for shared mixer config
- The renderer **owns all tag assignment** (#M8, #D5) — no pass-through from Init/Base
- **Send modes**: POST for buses 1-12, PRE for buses 13-16 on infrastructure channels
- **YAML 1.1 `on:` key** — PyYAML parses `on:` as boolean True; normalize with `type(k) is bool`
- Float tolerance: 3 significant figures (Wing's internal quantization)

## Workflow

This project uses the `coding-workflow` skill with agent briefs per feature.
Feature briefs live at `docs/features/<name>/brief.md`. The brief is the plan —
read it, implement against its constraints, escalate at its triggers.

See `docs/features/README.md` for the feature map and dependency graph.
See `docs/ROADMAP.md` for historical phase context.

## Reference Files

- `docs/wing-param-map.md` — annotated parameter grouping
- `docs/decisions.md` — architecture decisions with rationale
- `docs/investigations/` — domain analysis outputs (Phase 3 prep)
- `docs/features/README.md` — feature map with dependencies
