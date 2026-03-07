---
name: snapshot-evolution
description: Analyse how Wing mixer snapshots have evolved over time relative to a Sunday Starter baseline. Surfaces recurring adjustments worth promoting into DSL templates. Use when Matthew wants to review recent service trends and update team templates.
---

# Snapshot Evolution Analysis

Batch-compare post-service Wing snapshots against a Sunday Starter baseline.
Produces a report of recurring changes and concrete suggestions for DSL template updates.

Run every 1–3 months after a batch of services has accumulated.

---

## Workflow

### Step 1 — Confirm baseline and snapshots

Ask Matthew:
- Which team? (default: James)
- Which baseline snapshot? (the Sunday Starter loaded at the start of services)
- Which post-service snapshots to include? (files saved at end of services)

**Simulation defaults** (for testing without new data):
- Baseline: `data/reference/sunday-starters/james-starter-2025-06-01.snap`
- Snapshots: the July–November 2025 James snapshots in the Wing backup directory
  ```
  SNAP_DIR="/Users/mcox/Documents/Wing Backup/2025-12-14/snapshots"
  $SNAP_DIR/2025-07-27 James.snap
  $SNAP_DIR/2025-08-10 James.snap
  $SNAP_DIR/2025-08-24 James.snap
  $SNAP_DIR/James 2025-09-21.snap
  $SNAP_DIR/James 2025-10-05.snap
  $SNAP_DIR/2025-11-02James.snap
  ```

### Step 2 — Run the analysis

```bash
cd /Users/mcox/dev/snapwright
.venv/bin/snapwright analyze-evolution \
  "<baseline>" \
  "<snapshot1>" "<snapshot2>" ... \
  --output evolution-report.md \
  --min-occurrences 3
```

### Step 3 — Read and present the report

Read `evolution-report.md` in full, then present findings in this order:

1. **Summary line**: N patterns found across M channels. Briefly note anything surprising.

2. **High-signal patterns** — consistent direction, no ⚠️ constant offset flag, count ≥ 4:
   Present these channel by channel. For each, state what changed and by how much.

3. **Constant-offset patterns** (⚠️ flag): Note these separately.
   These suggest the baseline had a stale value that got corrected once and held.
   Ask Matthew: "Does this match your memory? Should we just update the base?"

4. **Mixed-direction patterns**: Flag these as "situational — not ready to promote."

5. **Suggestions section**: Read the high-confidence suggestions aloud (concisely).
   Ask Matthew which ones to act on.

### Step 4 — Decide and log

For each suggestion Matthew wants to act on:

- Note it in `docs/decisions.md` using the standard format:
  ```
  ### YYYY-MM-DD — [title]
  **Decision**: [what changed]
  **Rationale**: [why — reference the pattern count and direction]
  **Category**: escalated | autonomous
  ```

- Remind Matthew that DSL changes are Phase 4 scope (promotion + regeneration).
  This skill produces the *signal*; acting on it is a separate step.

---

## Interpreting the Report

**Pattern metadata key:**
- `(6×, 3 recent ✓ consistent)` — changed 6 times total, 3 in the second half of the batch (recent), all in the same direction
- `⚠️ constant offset` — all deltas are identical; likely a stale baseline value corrected once, not a genuine recurring adjustment
- `~ mixed direction` — changed both ways; situational, not a template candidate

**What to look for:**
- High count + consistent + recent + no constant-offset flag → strong template candidate
- Send level/on changes to FX buses → routing preferences worth baking in
- Fader movements → check if consistent direction; mixed means singer-dependent
- Model changes (EQ/dynamics/gate) → high-value if consistent; may mean base had wrong preset loaded
- Monitor sends → capture preferences; these are personal and tend to be stable per team

**Significance thresholds** (already applied by the tool):
- Fader / send level: ≥ 2 dB
- EQ gain: ≥ 1.5 dB
- Frequency: ≥ 10% relative shift
- Dynamics threshold: ≥ 2 dB

---

## Project Context

- DSL source: `data/dsl/teams/`
- Reference snapshots: `data/reference/sunday-starters/`
- Wing backup snapshots: `/Users/mcox/Documents/Wing Backup/2025-12-14/snapshots/`
- Decisions log: `docs/decisions.md`
- Phase spec: `docs/phase-2-spec.md`
- Roadmap: `docs/ROADMAP.md`

Promoting patterns to DSL templates is **Phase 4** scope. This skill is **Phase 2** — surface the signal, Matthew decides.
