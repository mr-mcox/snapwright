---
name: snapshot-evolution
description: Analyse how Wing mixer snapshots have evolved over time relative to a Sunday Starter baseline. Surfaces recurring adjustments worth promoting into DSL templates. Use when Matthew wants to review recent service trends and update team templates.
disable-model-invocation: true
---

# Snapshot Evolution Analysis

Batch-compare post-service Wing snapshots against a Sunday Starter baseline.
Produces a report of recurring changes and concrete suggestions for DSL template updates.

---

## Workflow

### Step 1 — Gather inputs

Ask Matthew for:

1. **Baseline snapshot** — the Wing `.snap` file that was loaded at the start of services
   during the period being analysed. This is a binary snapshot file (`.snap`), not a DSL
   assembly file. Sunday Starter snapshots for reference teams live in
   `data/reference/sunday-starters/`. Matthew may also point to a file elsewhere on disk.

2. **Post-service snapshots** — the `.snap` files saved at the end of services.
   Ask for the directory or individual file paths. These are typically in the Wing backup
   folder on Matthew's machine.

3. **Team name** (for labelling the report output, e.g. `james`, `priscilla`).

4. **Min occurrences threshold** — how many snapshots must show the same change before
   it's flagged as a pattern. Default: 3. Ask only if Matthew wants to adjust it.

Once you have the inputs, confirm them before running.

### Step 2 — Run the analysis

```bash
cd /Users/mcox/dev/snapwright
.venv/bin/snapwright analyze-evolution \
  "<baseline-path>" \
  "<snapshot1>" "<snapshot2>" ... \
  --output "evolution-<team>-report.md" \
  --min-occurrences <n>
```

### Step 3 — Read and present the report

Read the generated report in full, then present findings in this order:

1. **Summary**: N patterns across M channels. Flag anything immediately striking.

2. **High-signal patterns** — consistent direction, no ⚠️ constant offset flag, count ≥ 4:
   Present channel by channel. For each: what changed, by how much, how recently.

3. **Constant-offset patterns** (⚠️ flag): Present separately.
   These suggest the baseline had a stale value corrected once and held — not a recurring
   weekly adjustment. Ask Matthew: "Does this match your memory? Should we update the base?"

4. **Mixed-direction patterns**: Flag as situational — not ready to promote.

5. **Suggestions**: Read the high-confidence suggestions concisely.
   Ask Matthew which ones to act on.

### Step 4 — Log decisions

For each suggestion Matthew wants to act on, append to `docs/decisions.md`:

```
### YYYY-MM-DD — [title]
**Decision**: [what]
**Rationale**: [why — reference pattern count and direction]
**Category**: escalated | autonomous
```

Remind Matthew: DSL file changes are Phase 4 scope. This skill surfaces the signal;
acting on it is a separate step.

---

## Reading the Report

**Pattern metadata:**
- `(6×, 3 recent ✓ consistent)` — 6 occurrences total, 3 in the second half of the batch,
  all in the same direction
- `⚠️ constant offset` — all deltas identical; likely a stale baseline value, not a genuine
  recurring adjustment
- `~ mixed direction` — changed both ways; situational, not a template candidate

**What to look for:**
- High count + consistent + recent + no ⚠️ → strong template candidate
- FX send changes (reverb/delay on/off, level) → routing preferences worth baking in
- Fader movements → check direction consistency; mixed means context-dependent
- EQ/dynamics/gate model changes → high-value if consistent; base may have had wrong preset
- Monitor sends → personal preferences, tend to be stable per team

**Significance thresholds** (applied by the tool — changes below these are filtered out):
- Fader / send level: ≥ 2 dB
- EQ gain: ≥ 1.5 dB  
- Frequency: ≥ 10% relative shift
- Dynamics threshold: ≥ 2 dB

---

## Project Context

- DSL source: `data/dsl/teams/`
- Reference snapshots: `data/reference/sunday-starters/`
- Decisions log: `docs/decisions.md`
- Phase spec: `docs/phase-2-spec.md`

Promoting patterns to DSL templates is **Phase 4** scope. This skill is **Phase 2** —
surface the signal, Matthew decides.
