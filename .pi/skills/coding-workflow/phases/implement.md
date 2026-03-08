# Phase 3: Implement

**Status value**: `implementing`
**Entry**: Agent brief approved.
**Exit gate**: Clean commit after diff review.
**Output**: Working code + `docs/features/[feature-name]/decisions.md` (running log)

---

## Purpose

Execute against the agent brief's constraints. Log decisions along the way. Escalate when triggers fire. Pause for diff review before committing.

The user is treating you as a junior engineer — you have autonomy within the brief's constraints, but architectural judgment calls go up.

---

## Process

### Step 1: Re-read the Brief

Every implementation session starts by reading the brief:

```bash
cat docs/features/[feature-name]/brief.md
```

Check:
- Constraints still make sense given current code state
- Escalation triggers are fresh in context
- Any decisions already logged (if resuming)

### Step 2: Explore and Plan (internally)

Before writing code:
- Read the files you'll need to change
- Identify the implementation approach
- Check if any escalation triggers are already relevant

**Do NOT present a detailed implementation plan.** Just start implementing. If something comes up that needs a decision, log it or escalate it.

### Step 3: Implement

Write code. Follow the codebase's existing patterns. Respect the brief's constraints.

**TDD intensity** (from PROFILE.md):
- **Thorough**: Domain logic, business rules, invariants
- **Basic**: Integration, config, UI wiring
- **None**: Scaffolding, prototype-graduated code that hasn't earned tests yet

**While implementing, maintain the decision log**:

Create or append to `docs/features/[feature-name]/decisions.md`:

```markdown
## Decisions

### [Date] - [Short description]
**Context**: [What prompted this decision]
**Choice**: [What was decided]
**Alternatives considered**: [Brief — what else was on the table]
**Rationale**: [Why this choice]
```

Log decisions that:
- Chose between meaningful alternatives
- Interpreted ambiguity in the brief
- Affected the shape of the code in a non-obvious way

Don't log:
- Obvious choices (variable naming, standard patterns)
- Things dictated by the brief's constraints

### Step 4: Escalation

When an escalation trigger fires, **stop and present the decision**:

```
🔶 Escalation: [trigger condition that fired]

**What I found**: [context]
**Options**:
1. [Option A] — [tradeoff]
2. [Option B] — [tradeoff]
3. [Your suggestion if you have one]

Which direction?
```

Wait for the user's call. Log the decision.

Also escalate for anything not in the triggers but that feels architectural — err on the side of asking. The user can always say "just decide."

### Step 5: Diff Review

Before committing, present the diff for review:

```bash
git diff --stat
git diff
```

Frame the review:

```
Ready for diff review. Here's what changed:

**Files**: [count] modified, [count] new
**Key changes**:
- [Most important change and why]
- [Second most important]
- [Any non-obvious change worth flagging]

**Decisions made** (see decisions.md for full log):
- [Decision 1 summary]
- [Decision 2 summary]

Review the diff and let me know:
- Anything to change before committing?
- Ready to commit?
```

The user reviews the diff directly — this replaces PR review. They may:
- Approve → commit
- Request changes → implement and re-present diff
- Flag a decision to revisit → update or revert

### Step 6: Commit and Transition

After approval:

```bash
git add -A
git commit -m "[type]: [description]"
```

Update brief status to `compacting`:

```
Committed. Brief status updated to `compacting`.
Ready to compact learnings now, or letting this bake first?
```

"Letting it bake" is explicitly valid — the user may want to use the feature for a few days before reflecting.

---

## Resuming Mid-Implementation

If re-entering after a gap:
1. Read the brief (constraints, triggers)
2. Read the decision log (what's been decided)
3. Check git status / diff for in-progress work
4. Present: "Last session we [summary]. Picking up at [next step]."

---

## Principles

- **Implement, don't plan.** The brief is the plan. Start writing code.
- **Log decisions as you go**, not retroactively. They're harder to reconstruct later and less accurate.
- **Escalate early, not late.** A 2-minute pause for user input is cheaper than reverting a wrong decision.
- **The diff review is sacred.** This is the user's quality gate. Don't rush it. Surface the important changes clearly.

---

## Anti-patterns

- Writing a multi-phase implementation plan before starting (the brief is the plan)
- Making architectural decisions silently because they "seemed obvious"
- Logging every trivial choice (noise drowns signal)
- Presenting the diff without context (raw diff without framing is hard to review)
- Skipping the diff review to commit directly
