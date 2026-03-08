# Prototype Mode

**Entry**: User opts in — "I need to explore" / "I don't know what this should feel like"
**Exit**: Patterns repeating, question shifts to "how should it work properly?" → Write first agent brief, enter Phase 2.
**Output**: `docs/prototype/[topic].md` — running learnings document.

---

## Purpose

Build fast to learn. The code is disposable; the learnings are the asset. No tests, no abstractions, no architecture. Maximum velocity toward understanding.

This can happen on any project at any stage — it's not just for new projects. A mature project like harvest-hound can enter prototype mode for a feature branch (e.g., recipe variations) and return to build mode with learnings in hand.

---

## Rules of Engagement

**Do:**
- Build the simplest thing that lets you feel the behavior
- Capture learnings as you go (the document is the real output)
- Try multiple approaches — reference each in the learnings doc
- Keep scope tiny: single behavior per experiment, max 3 files

**Don't:**
- Write tests (they anchor disposable code)
- Create abstractions "for later" (YAGNI, enforced)
- Review code quality (deliberately avoid this — it's not the point)
- Spend time on error handling, edge cases, or robustness
- Create helper functions that won't be called immediately

If you catch yourself doing any of these, stop and refocus on learning velocity.

---

## Process

### Step 1: State the Exploration Question

Before building anything, articulate what you're trying to learn:

```
Exploration question: [What are we trying to understand?]

This is NOT a feature spec — it's a question we'll answer by building something.
```

Examples:
- "What does recipe variation feel like when you start from an existing recipe?"
- "What level of granularity do we need for Logseq block interactions?"
- "Does importing recipes from URLs feel natural alongside manual entry?"

### Step 2: Build and Learn

Build the simplest thing that addresses the question. While building, maintain the learnings document.

Create or update `docs/prototype/[topic].md`:

```markdown
# Prototype: [Topic]

**Question**: [What are we exploring?]
**Started**: [Date]
**Status**: active

## Learnings

### [Date] - [What we tried]
**Experiment**: [What was built — reference files/lines]
**Observed**: [What happened when we used it]
**Insight**: [What this tells us]

### [Date] - [Next thing we tried]
**Experiment**: [What was built]
**Observed**: [What happened]
**Insight**: [What this tells us]
```

Each entry should reference the specific code that produced the learning — file paths, line numbers, the approach taken. When the code is eventually deleted, the learnings doc preserves *what was tried and what it revealed*.

### Step 3: Recognize the Transition Signal

You're ready to exit prototype mode when:
- The same patterns keep emerging across experiments
- You can articulate what the feature should do (not just what question you're exploring)
- You're adding known features rather than discovering new behaviors
- The question shifts from "does this work?" to "how should it work properly?"

When you notice this:

```
I think we've learned enough to transition to build mode.

**Key learnings from prototype**:
- [Learning 1]
- [Learning 2]
- [Learning 3]

**The feature is now**: [Clear statement of what to build]

Ready to write the agent brief and enter build mode?
```

### Step 4: Transition to Build Mode

On user confirmation:
1. Ensure `docs/prototype/[topic].md` is committed and up to date
2. The prototype code can stay or be deleted — it doesn't matter, the learnings are captured
3. Enter Phase 2 (solution space) — the learnings doc becomes primary input for the agent brief
4. The prototype learnings doc stays in `docs/prototype/` until compaction (Phase 4) absorbs the relevant parts into `docs/learnings/`

---

## Learnings Document Maintenance

The agent should actively maintain the learnings document throughout the prototype:

- **After each experiment**: Add an entry with what was tried and what it revealed
- **After user feedback**: Capture their reactions — "that felt right" or "that's not quite it" is valuable signal
- **On surprising discoveries**: Flag with emphasis — these are often the highest-value insights
- **On dead ends**: Document them! Knowing what *didn't* work is as valuable as what did

The user should never have to ask "did we capture that?" — the learnings doc should already have it.

---

## Principles

- **Learning velocity over code quality.** The fastest path to understanding, not the cleanest code.
- **The learnings doc is the artifact, not the code.** Code can be deleted; learnings persist.
- **Reference, don't describe.** Point to specific code (`app.py:45-80`) rather than abstractly describing what was built.
- **Small experiments, fast cycles.** One behavior at a time. Feel it, learn from it, move on.
- **The transition is deliberate, not gradual.** Don't let prototype code drift into load-bearing infrastructure. When you're ready to build, write the brief and start clean.

---

## Anti-patterns

- Spending time on code quality in prototype mode (this is the discipline to resist)
- Building without updating the learnings doc (the code alone won't preserve the insights)
- Prototyping for too long — if you've answered your question, transition
- Prototyping for too short — if you're still surprised by what you find, stay in prototype mode
- Letting prototype code become the real implementation without a deliberate transition
