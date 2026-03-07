---
name: snapshot-evolution
description: Analyse how Wing mixer snapshots have evolved over time relative to a Sunday Starter baseline. Surfaces recurring adjustments worth promoting into DSL templates. Use when Matthew wants to review recent service trends and update team templates.
disable-model-invocation: true
---

# Snapshot Evolution Analysis

Batch-compare post-service Wing snapshots against a Sunday Starter baseline to surface
recurring adjustments worth promoting into DSL templates.

---

## Workflow

### Step 1 — Gather inputs

Ask Matthew:
1. **Baseline**: the Wing `.snap` file that was loaded at the start of services during the
   analysis window. This is a `.snap` file (binary Wing format), not a DSL assembly file.
   Sunday Starter reference snaps live in `data/reference/sunday-starters/`.
2. **Post-service snapshots**: the `.snap` files saved at the end of services. Ask for the
   directory or individual paths.
3. **Team name** for labelling output (e.g. `james`).

Confirm inputs, then run.

### Step 2 — Run the analysis

```bash
cd /Users/mcox/dev/snapwright
.venv/bin/snapwright analyze-evolution \
  "<baseline>" \
  "<snapshot1>" "<snapshot2>" ... \
  --output "evolution-<team>-report.md" \
  --min-occurrences 3
```

### Step 3 — Synthesize internally, then present themes

**Read the full report silently first. Do not present it.**

Synthesize what you find into 3–6 themes. A theme is a cluster of related patterns that
tell a coherent story — e.g. "vocal FX routing is consistently different from the baseline"
or "several channel faders are substantially off". Good themes cut across channels; they
name a problem, not just a list of facts.

For each theme:
- One sentence naming the pattern
- Rough confidence: how many channels/occurrences support it, any ⚠️ flags
- One or two concrete examples (not exhaustive lists)

Present the themes as a short numbered list — aim for under 15 lines total. Then stop and
ask: *"Which of these feels most worth acting on, or do you want to talk through any of
them first?"*

**Do not present the full report. Do not read suggestions aloud. Do not enumerate every
channel.**

### Step 4 — Work through decisions one at a time

For each theme Matthew wants to act on:
- Offer the specific suggestion in one sentence ("Consider raising Kick fader from -8.9 to
  approximately 0 dB in the Sunday Starter")
- Ask: accept, modify, or skip?
- If accepted or modified, log immediately to `docs/decisions.md`:

```
### YYYY-MM-DD — [title]
**Decision**: [what]
**Rationale**: [pattern count, direction, median shift if relevant]
**Category**: escalated | autonomous
```

Move to the next decision. Keep the loop tight — one decision at a time, no preamble.

### Step 5 — Wrap up

Once Matthew is done, summarise: how many decisions logged, which themes were skipped and
why. Remind him that DSL file changes are Phase 4 scope — this skill surfaces signal,
acting on it is a separate step.

---

## Reading Patterns (internal reference — not for presentation)

**What makes a strong template candidate:**
- Consistent direction (✓ consistent), no ⚠️ constant offset flag, count ≥ 4
- Recent occurrences weighted higher than older ones
- FX send routing, model changes, and threshold corrections are high-value if consistent
- Monitor send levels are personal preferences — stable per team, worth baking in
- Mixed direction (~ mixed direction) means context-dependent; skip unless Matthew flags it

**⚠️ constant offset** means all deltas are identical — likely the baseline had a stale
value corrected once and held, not a genuine recurring weekly adjustment. Worth naming as
a theme ("baseline may have wrong values for X") but distinct from genuine service patterns.

**Significance thresholds** (already applied — changes below these are filtered):
- Fader / send level: ≥ 2 dB | EQ gain: ≥ 1.5 dB | Frequency: ≥ 10% shift | Dynamics threshold: ≥ 2 dB

---

## Project Context

- DSL source: `data/dsl/teams/`
- Reference snapshots: `data/reference/sunday-starters/`
- Decisions log: `docs/decisions.md`
- Phase spec: `docs/phase-2-spec.md`

Promoting patterns to DSL files is **Phase 4** scope.
