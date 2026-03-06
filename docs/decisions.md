# Decisions

### 2025-03-05 — Reference snapshots: copy subset, not full backup
**Decision**: Copied Base.snap + 6 Sunday Starters (James, Priscilla, Levin, Morks, Jen, Kana) into `data/reference/`. Not the full 125-snapshot backup.
**Rationale**: These cover the active team snapshots and enough variety for structural analysis. Full backup is 40MB+ of historical snapshots we don't need in the repo.
**Category**: autonomous

### 2025-03-05 — Python 3.12+, standard tooling
**Decision**: Target Python 3.12+. Pydantic for schema, Click for CLI, PyYAML for DSL, deepdiff for comparisons.
**Rationale**: Matches existing project conventions (logseq-navigator). Pydantic is specified in the project brief for schema validation.
**Category**: autonomous
