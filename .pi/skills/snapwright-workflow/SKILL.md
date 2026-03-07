---
name: snapwright-workflow
description: "Session management for the snapwright project. Handles re-entry, escalation triggers, and decision logging. Lightweight — not a full phase-gated workflow."
---

# Snapwright Workflow

Lightweight session and decision management for a well-defined build project.

## Session Re-entry

On any new session:

1. `git log --oneline -10`
2. Read `docs/ROADMAP.md`
3. Check `docs/decisions.md` for recent entries
4. Present in 5-8 lines: where things stand, what's next
5. Wait for confirmation before working

---

## Git Workflow

- One branch per phase: `phase-N-<short-description>` off main
- Work freely on the branch; commits as granular as useful
- Squash merge to main when the phase is validated: `git merge --squash phase-N-...`
- One commit on main per phase summarising what it delivered
- Phase 0 is already on main with working commits — history is as-is
---

## Escalation Triggers (pause and show Matthew)

These encode **domain architecture** — decisions that require audio engineering knowledge or that set the contract between Matthew and the system.

### DSL Shape & Schema
- YAML structure: how templates, musicians, assemblies, overrides nest and reference each other
- Field naming conventions (audio terminology choices)
- Inheritance model (single inherits vs mixins vs layered overrides)
- How physical assignments work in DSL (explicit channel numbers vs logical names vs hybrid)

### Renderer Structural Joints
- Abstraction boundaries: where interfaces live for future flexibility
- How to handle Wing defaults (full merge vs partial)
- How to handle parameters the DSL doesn't cover (pass-through vs defaults vs error)

### Domain Boundaries
- Channel bank definitions (drums, instruments, vocals — are they correct and stable?)
- Bus purpose mapping (submixes vs FX vs monitors)
- What's shared infrastructure vs team-specific
- How to model stripped-down snapshots (Priscilla pattern)

### Tolerances
- What "close enough" means for round-trip validation
- What counts as noise vs signal in diffs

### Workflow & Scope
- CLI interface design (command names, flags, output format)
- When to stop steel thread and call it validated
- When/whether to tackle semantic diffing or LLM integration

---

## Iterate Freely (decide and log)

These are **software architecture** — engineering craft where the goal is "gracefully evolvable" and the profile standards (evolutionary architecture, YAGNI, supple design) provide sufficient guidance.

- Pipeline stage implementation
- Module decomposition and file organization
- Test strategy and structure
- Dependency choices
- Schema versioning mechanics
- Units representation in DSL
- Floating point handling strategy
- Rendering internals
- Which parameters to model first (within a phase)

Log non-trivial decisions in `docs/decisions.md` with a one-liner rationale.

---

## Decision Log Format

Append to `docs/decisions.md`:

```
### YYYY-MM-DD — [title]
**Decision**: [what]
**Rationale**: [why, one sentence]
**Category**: [escalated | autonomous]
```

---

## Project Principles

From the project brief and operator profile:

- **Cattle not pets**: Snapshots are generated artifacts, safely regenerated from source truth
- **Declarative as goal, imperative as path**: Allow explicit physical layout initially, migrate to logical over time
- **Learn from reality**: Volunteer adjustments are data
- **YAGNI**: Don't build flexibility that isn't needed yet, but put interfaces at known volatility boundaries
- **Evolutionary architecture**: The test suite makes safe refactoring possible; don't over-design upfront
