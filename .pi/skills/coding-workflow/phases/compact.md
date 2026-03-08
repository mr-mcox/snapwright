# Phase 4: Compact

**Status value**: `compacting`
**Entry**: Implementation committed. Optionally after a baking period.
**Exit gate**: Learnings distilled, brief archived or deleted.
**Output**: Updated `docs/learnings/[topic].md`

---

## Purpose

Extract durable insights from the feature work. The code is committed; the brief and decision log have served their purpose. Distill what's worth keeping into learnings, then clean up.

This phase can happen immediately after commit or after days/weeks of using the feature. Baking time is valuable — some insights only emerge through use.

---

## Process

### Step 1: Gather the Feature's Artifacts

Read:
- `docs/features/[feature-name]/brief.md` — the original constraints and problem
- `docs/features/[feature-name]/decisions.md` — what was decided during implementation
- The committed code (if reviewing after bake time, re-read key files)

If baking time has passed, ask:
```
This feature has been in place since [date]. 

How has it felt in practice?
- Anything surprising?
- Anything you'd do differently?
- Any of the original constraints or escalation triggers that turned out to be wrong?
```

Wait for user input.

### Step 2: Identify Durable Learnings

Not everything is worth keeping. Filter for:

- **Domain insights** — "we discovered that X works this way" (understanding that transfers)
- **Pattern discoveries** — "this approach worked well for Y" (reusable in future features)
- **Mistakes worth remembering** — "we assumed Z but it was actually W" (prevents repeat errors)
- **Constraint validations** — "the pre-decision about X proved [correct/wrong] because..."

Don't keep:
- Implementation details that are obvious from reading the code
- Decisions that were straightforward and wouldn't inform future work
- Anything specific to this feature that doesn't generalize

### Step 3: Write to Learnings

Append to or create `docs/learnings/[topic].md`:

```markdown
### [Feature Name] ([Date])

- [x] **[Learning title]**: [Concise description of what was learned and why it matters]. (discovered: [feature-name], [date])
```

Follow the format established in existing learnings files (consistent with logseq-navigator and harvest-hound patterns).

If `docs/learnings/` doesn't exist yet, create it. Group by topic, not by feature — learnings should be findable by domain area.

### Step 4: Clean Up

After learnings are captured:

```
Learnings written to docs/learnings/[topic].md:
- [Learning 1 title]
- [Learning 2 title]

Ready to archive the feature folder?
Options:
1. Delete docs/features/[feature-name]/ (learnings are captured, brief served its purpose)
2. Keep for reference (if you want to revisit the decision log later)
```

Wait for user's call. Default recommendation is delete — the learnings doc is the permanent record.

If deleting:
```bash
rm -rf docs/features/[feature-name]
git add -A
git commit -m "chore: compact [feature-name] learnings, archive brief"
```

---

## Principles

- **Learnings are the permanent record; briefs are ephemeral.** The brief was a tool for implementation. The learning is what transfers.
- **Less is more.** 3 sharp learnings beat 10 vague ones.
- **Group by topic, not by feature.** Future-you will search by domain area, not by which feature generated the insight.
- **Baking time is real value.** Don't rush compaction. Let the feature breathe.

---

## Anti-patterns

- Keeping the brief "just in case" forever (it goes stale, clutters the feature directory)
- Writing learnings that are just a summary of what was built (that's what the commit is for)
- Compacting immediately when the feature would benefit from bake time
- Skipping compaction entirely (the brief rots, insights are lost)
