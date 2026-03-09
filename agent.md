# Snapwright — Agent Context

Snapwright generates Behringer Wing digital mixer snapshots from a YAML-based DSL.
It renders `.snap` files (JSON) that the Wing loads to configure channels, buses,
processing, routing, and control surface state for live sound at a church.

## Toolchain

- **Python 3.12+**, managed with **uv** (not pip, not conda)
- Run tests: `uv run pytest`
- Lint: `uv run ruff check .`
- Run CLI: `uv run snapwright <command>`

## Quality Gates

**All tests must pass before presenting a diff for review.** Run `uv run pytest -q`
and `uv run ruff check .` before calling anything done. If you find a pre-existing
failing test you didn't break, flag it — don't normalize it.

## TDD Policy

| Domain | Intensity | What that means |
|--------|-----------|-----------------|
| Rendering logic, schema validation, pure functions | Thorough | Test first, watch it fail, implement. |
| Integration (full pipeline, snapshot diff) | Basic | Diff against reference snapshots. |
| Scaffolding, CLI wiring, file I/O | None/Basic | Test if non-trivial; skip if plumbing. |

## Architecture (current state)

```
Base.snap (BCF base config — opaque binary, used as rendering foundation today)
    ↓
team/assembly.yaml (musicians, channels, monitors, bus names)
    ↓
rendered .snap file
```

Key modules:
- `snapwright/wing/` — parser, writer, defaults (Wing JSON tooling)
- `snapwright/dsl/` — schema (Pydantic), loader (YAML + inheritance), renderer (DSL → Wing JSON)
- `snapwright/evolution/` — snapshot diff analysis for promoting volunteer adjustments
- `data/reference/` — Base.snap, Init.snap (factory reset), reference snapshots
- `data/dsl/` — YAML source files (musicians, teams, overlays)

## Known Gotcha

PyYAML 1.1 parses `on:` as boolean `True`. Normalize with `type(k) is bool`, not `k == True`.

## Workflow

This project uses the `coding-workflow` skill with agent briefs per feature.
Feature briefs live at `docs/features/<name>/brief.md`. The brief is the plan —
read it, implement against its constraints, escalate at its triggers.

Active feature work and dependencies: `docs/features/README.md`
Project history and phase narrative: `docs/ROADMAP.md`
Architecture decisions with rationale: `docs/decisions.md`
