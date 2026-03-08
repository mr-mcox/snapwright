---
name: agent-brief
description: "Format spec for writing and reading agent briefs — the central artifact of the coding workflow. Briefs are dead drops between sessions, governing implementation and enabling async re-entry."
---

# Agent Brief

Agent briefs are the central artifact of the coding workflow. They serve as:
- **Contract** between user and implementation agent (what's in scope, what's not, when to escalate)
- **Dead drop** between sessions (pick up where you left off by reading the brief)
- **Phase tracker** (frontmatter status field determines which workflow phase is active)

---

## Writing a Brief

### Location

```
docs/features/[feature-name]/brief.md
```

### Template

```markdown
---
feature: [kebab-case-name]
date: [YYYY-MM-DD]
commit: [sha at time of writing]
branch: [branch name]
status: [problem-space | solution-space | implementing | compacting | done]
read-when: [human-readable guidance, e.g. "resuming implementation" or "starting diff review"]
---

## Problem

[2-3 sentences. What user need does this address? Why does it matter?
Preserve the user's own framing from problem-space discussions.]

## Not Doing

[Explicit scope boundary. What's out. Be specific.]
- [Thing explicitly deferred and why]
- [Another boundary]

## Constraints

[Pre-decisions that bound implementation. 3-7 items.]
- [Decision, not instruction. e.g. "Use existing Recipe model" not "First create a migration..."]
- [Another constraint]
- [Another constraint]

## Escalation Triggers

[Conditions under which the implementation agent should pause and surface the decision.]
- If [condition], pause. [Brief context on why this matters.]
- If [condition], pause.
- If [condition], pause.

## Decisions

[Populated during Phase 3. Empty at brief creation.]
[See decisions.md in the same directory for the full running log.]
```

### Sizing

The brief body should be **~20 lines of content** (plus frontmatter). If it's longer, you're over-specifying. The brief captures *what* and *why*, never *how*.

---

## Reading a Brief

### For Phase Detection (orchestrator)

Read only the YAML frontmatter. The `status` field determines the active phase:
- `problem-space` — still aligning on the problem
- `solution-space` — writing/refining the brief itself
- `implementing` — implementation in progress
- `compacting` — distilling learnings post-implementation
- `done` — compacted, ready for cleanup

The `date`, `commit`, and `branch` fields indicate freshness. If the commit is far behind HEAD, the brief may be stale.

### For Session Re-entry

Read the full brief. Check:
1. **Status** — which phase are we in?
2. **Commit** — has the code moved since the brief was last updated?
3. **Constraints** — still valid given current code state?
4. **Decisions section** — what's already been decided?
5. **read-when** — does the current situation match the guidance?

Then read `decisions.md` in the same directory (if it exists) for the full decision log.

### For Implementation

The brief is the governing document. During Phase 3:
- Constraints are binding unless explicitly renegotiated with the user
- Escalation triggers are active — check each one before making a relevant decision
- The "Not Doing" section is a hard boundary — don't drift into deferred scope

---

## Frontmatter Fields

| Field | Purpose | Updated when |
|-------|---------|-------------|
| `feature` | Machine-readable name, matches directory | Never (set at creation) |
| `date` | Brief creation date | Never |
| `commit` | Git SHA at time of writing | On significant brief updates |
| `branch` | Working branch | On branch changes |
| `status` | Current workflow phase | On phase transitions |
| `read-when` | Human guidance for when to read this | On phase transitions |

---

## Phase-Specific Variations

### Problem Space (`problem-space`)
Brief is a stub — only frontmatter and a rough problem statement. Constraints and escalation triggers are TBD. The brief exists mainly to track that work has started.

### Solution Space (`solution-space`)
Brief is being actively written. All sections being filled in. This is the phase where the brief gets its final shape before approval.

### Implementing (`implementing`)
Brief is frozen — constraints are binding. Only the Decisions section gets updated (via `decisions.md`). Status changes only on completion.

### Compacting (`compacting`)
Brief is being read for distillation. Learnings are extracted, then the brief is archived or deleted.

---

## Principles

- **Briefs are ephemeral.** They govern a feature's implementation, then get compacted into learnings and deleted. Don't let them accumulate.
- **30-second readability.** Anyone (human or agent) should understand the current state in 30 seconds from the frontmatter + a quick scan.
- **Constraints are decisions, not instructions.** They bound the solution space without prescribing the path.
- **Escalation triggers preserve user agency.** Better to have too many than too few — the user can always say "just decide."
- **The `read-when` field is for humans.** It's the one field that exists purely for the user scanning their feature directory.
