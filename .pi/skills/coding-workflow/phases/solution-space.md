# Phase 2: Solution Space

**Status value**: `solution-space`
**Entry**: Problem space threads are closed. Ready to define constraints.
**Exit gate**: User approves the agent brief.
**Output**: `docs/features/[feature-name]/brief.md`

---

## Purpose

Translate problem space understanding into a tight agent brief — the document that governs Phase 3 implementation. This is where pre-decisions get locked in and escalation rules get defined.

The brief is the contract between you (the user making decisions) and the implementation agent (the junior engineer doing the work).

---

## Process

### Step 1: Create the Feature Directory

```bash
mkdir -p docs/features/[feature-name]
```

### Step 2: Draft the Agent Brief

Write `docs/features/[feature-name]/brief.md` using the agent-brief skill's format spec.

The brief should be ~20 lines of content (plus frontmatter). If it's longer, you're over-specifying. The key sections:

1. **Problem** — carried forward from Phase 1 (2-3 sentences)
2. **Not doing** — explicit scope boundary (what's out)
3. **Constraints** — 3-7 pre-decisions that bound implementation
4. **Escalation triggers** — when to pause and ask the user
5. **Decisions** — empty at this point, populated during Phase 3

Constraints should be *decisions*, not instructions. Good: "Use the existing Recipe model, don't create a new one." Bad: "First create a migration, then add a field, then update the service..."

### Step 3: Define Escalation Triggers

This is the most important part of the brief. Get it right.

Escalation triggers are the conditions under which the implementation agent should **stop and surface the decision** to the user. They should capture:

- **Architectural forks** — choices that would be expensive to reverse
- **Scope questions** — "this feature touches X, should I include that?"
- **Trade-off moments** — performance vs simplicity, flexibility vs directness
- **Surprise discoveries** — "the code doesn't work how we assumed"

Frame triggers as conditions, not questions:
- Good: "If recipe import requires a new data model beyond the existing Recipe, pause."
- Bad: "Ask me about the data model."

### Step 4: Present for Approval

```
Here's the draft brief at docs/features/[feature-name]/brief.md:

**Problem**: [1-sentence summary]
**Scope boundary**: [what's explicitly out]
**Constraints**: [count] pre-decisions
**Escalation triggers**: [count] conditions

Please review. Key things to check:
- Are the constraints accurate pre-decisions, or are any still open?
- Are the escalation triggers catching the things you'd want to weigh in on?
- Is the scope boundary in the right place?
```

Wait for approval. The user may:
- Approve as-is → transition to Phase 3
- Adjust constraints → update and re-present
- Add/remove escalation triggers → update and re-present
- Realize a problem-space thread is still open → drop back to Phase 1

### Step 5: Transition

Once approved, update the brief's status to `implementing` and confirm:

```
Brief approved. Status updated to `implementing`.
Ready to start implementation, or picking this up later?
```

---

## Principles

- **Constraints are pre-decisions, not instructions.** They bound the solution space without prescribing the implementation path.
- **Escalation triggers are about preserving user agency on things that matter.** Err on the side of more triggers — the user can always say "just decide" in the moment, but a missed trigger means a decision made without their input.
- **The brief should be readable in 30 seconds.** If it takes longer, it's too long.
- **No implementation details.** The brief says what and why, never how. Phase 3 determines how.

---

## Anti-patterns

- Writing a TIP-style multi-phase implementation plan (that's over-specifying)
- Constraints that are really step-by-step instructions
- Missing escalation triggers for architectural decisions
- Scope boundary that's vague ("keep it simple") instead of specific ("no UI changes")
