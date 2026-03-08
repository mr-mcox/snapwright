# Phase 1: Problem Space

**Status value**: `problem-space`
**Entry**: No active brief exists, user has described what they want to build.
**Exit gate**: No open threads — all unknowns are either resolved or explicitly deferred.
**Output**: Understanding sufficient to write a tight agent brief in Phase 2.

---

## Purpose

Align on the problem before defining the solution. The agent does the heavy lifting (code exploration, learnings review, surfacing unknowns). The user's job is to close threads — confirm understanding, answer questions, make calls on ambiguities.

This is the highest-leverage phase. A misunderstanding here cascades into wasted implementation. Invest the time.

---

## Process

### Step 1: Load Existing Context

Before asking the user anything, gather what's already known:

1. **Read project learnings** (if they exist):
   ```bash
   find docs/learnings -name "*.md" 2>/dev/null
   ```
   Extract anything relevant to the stated feature/goal.

2. **Read previous briefs** (for patterns and prior decisions):
   ```bash
   find docs/features -name "brief.md" 2>/dev/null
   ```

3. **Explore relevant code** — targeted, not exhaustive:
   - What exists in the area we're changing?
   - What patterns does this codebase already use?
   - What would this feature touch?

4. **Check for prototype learnings** that might inform this:
   ```bash
   find docs/prototype -name "*.md" 2>/dev/null
   ```

### Step 2: Present What You Found

Concise synthesis — not a dump of everything you read. Apply the performance equation.

```
Here's what I found relevant to [feature]:

**Existing patterns**: [what the codebase already does in this area]
**From learnings**: [relevant prior discoveries]
**What this would touch**: [files/modules affected]

Things I'm unsure about:
- [Unknown 1]: [why it matters]
- [Unknown 2]: [why it matters]
```

### Step 3: Close the Threads

For each unknown, get resolution:
- **User answers directly** → thread closed
- **Needs more exploration** → agent investigates, comes back with findings
- **Explicitly deferred** → noted as out of scope (goes in brief's "not doing" section)
- **Genuinely uncertain, could go either way** → becomes an escalation trigger in the brief

The goal is not to resolve every possible question — it's to ensure there are no *surprise* unknowns lurking. Known unknowns that are flagged as escalation triggers are fine.

### Step 4: Confirm Readiness

When all threads are closed or deferred:

```
I think we're ready to write the brief. Here's what I'd capture:

**Problem**: [2-3 sentences]
**Not doing**: [explicit scope boundary]
**Key constraints emerging**: [what we've decided so far]
**Escalation triggers**: [the things that need your judgment during implementation]

Ready to move to Phase 2 (solution space)?
```

Wait for confirmation before transitioning.

---

## Principles

- **User's words, not your interpretation.** When capturing the problem statement, preserve how they described it. Restatement is for clarity, not reframing.
- **Explore first, ask second.** Don't ask the user questions the codebase can answer. That's what code exploration is for.
- **Surface unknowns, don't solve them.** Your job is to find the gaps, not fill them with assumptions.
- **Shorter is better.** A 5-line problem statement that's accurate beats a 50-line analysis that's comprehensive. The brief will be concise — this phase should trend toward concision too.

---

## Anti-patterns

- Presenting a comprehensive architecture analysis before the user has confirmed what they want
- Asking questions that could be answered by reading the code
- Treating every uncertainty as a blocker (some are fine as escalation triggers)
- Over-exploring — the goal is "enough to write the brief," not "understand everything"
