---
name: coding-workflow
disable-model-invocation: true
description: "Orchestrates the build workflow for personal coding projects. Detects current phase from agent briefs, routes to the appropriate phase, and manages transitions. Default mode is build (delegate to junior engineer). Prototype mode is an opt-in branch for discovery."
---

# Coding Workflow

Orchestrator for Matthew Cox's personal project coding workflow. Determines current phase, loads the right phase instructions, and manages transitions.

## Phase Detection

On invocation, determine the current phase:

1. **Check for active agent briefs**:
   ```bash
   find docs/features -name "brief.md" 2>/dev/null | head -10
   ```

2. **If brief(s) found**: Read the most recent brief's YAML frontmatter. The `status` field determines the phase:
   - `problem-space` → Load `phases/problem-space.md`
   - `solution-space` → Load `phases/solution-space.md`
   - `implementing` → Load `phases/implement.md`
   - `compacting` → Load `phases/compact.md`

3. **If no briefs found**: Ask what we're working on. Two paths:
   - **Build mode** (default): "I know roughly what I want" → Start Phase 1 (problem space)
   - **Prototype mode**: "I need to explore / I don't know what this should feel like" → Load `phases/prototype.md`

4. **Present your read of the situation**:
   ```
   I see [brief name] at status: [phase]. 
   Last updated [date], at commit [sha].
   
   Ready to continue [phase description]?
   ```
   Wait for confirmation or correction before loading the phase file.

---

## Phase Overview

Read the appropriate phase file from this skill's `phases/` directory for detailed instructions.

### Build Mode (default — "delegate to junior engineer")

| Phase | Status | What happens | Gate to next |
|-------|--------|-------------|--------------|
| 1. Problem Space | `problem-space` | Agent explores code + learnings. Surfaces unknowns. User closes them. | No open threads |
| 2. Solution Space | `solution-space` | Write the agent brief: problem, scope, constraints, escalation triggers. | User approves brief |
| 3. Implement | `implementing` | Agent implements against constraints. Logs decisions. Escalates at triggers. Diff review before commit. | Clean commit |
| 4. Compact | `compacting` | Distill decisions → LEARNINGS.md. Archive or delete brief. | Compaction complete |

### Prototype Mode (opt-in — "I need to explore")

Separate workflow. No briefs, no constraints, no tests. Produces a learnings document. See `phases/prototype.md`.

**Transition to build mode**: When patterns repeat and the question shifts from "does this work?" to "how should it work properly?" — extract learnings, write the first agent brief, enter Phase 2.

---

## File Conventions

```
docs/features/[feature-name]/
  brief.md           ← Agent brief (see agent-brief skill for format)
  decisions.md        ← Running decision log during Phase 3
  
docs/learnings/       ← Compacted insights (permanent)
  [topic].md

docs/prototype/       ← Prototype learnings (checked in, deleted on compact)  
  [topic].md
```

---

## Re-entry After a Gap

This is the orchestrator's primary job. On any invocation:

1. Scan for active briefs
2. Read frontmatter (status, date, commit, branch)
3. Present current state in 3-5 lines
4. Wait for confirmation

If the gap is long (weeks+), also:
- Check if the branch still exists / has diverged from main
- Note that perspective may have shifted since last session
- Surface the brief's problem statement to re-anchor

---

## Interruption Tolerance

Sessions may be 20 minutes. The workflow is designed for messy exits:

- Agent briefs persist state between sessions (that's the whole point)
- Phase 3 decision log captures in-progress thinking
- Prototype learnings docs accumulate incrementally
- No phase requires a clean exit to be resumable

---

## When to Escalate to User

Always escalate:
- Phase transitions (user confirms before moving to next phase)
- Anything listed in the brief's escalation triggers
- Architectural decisions (new abstractions, interface changes, dependency additions)
- When the agent would need to deviate from the brief's constraints
- When implementation reveals the problem statement was wrong

Don't escalate:
- Trivial implementation choices (variable names, file organization within a module)
- Test structure decisions
- Standard patterns already established in the codebase
