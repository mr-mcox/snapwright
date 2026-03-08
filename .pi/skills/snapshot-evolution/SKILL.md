---
name: snapshot-evolution
description: Analyse how Wing mixer snapshots have evolved over time relative to a baseline. Surfaces recurring adjustments worth promoting into DSL templates. Supports single-team temporal analysis and cross-team instrument analysis.
disable-model-invocation: true
---

# Snapshot Evolution Analysis

Batch-compare post-service Wing snapshots against a baseline to surface recurring
adjustments worth promoting into DSL templates.

---

## Workflow

### Step 1 — Establish intent and frame

Ask Matthew two things:

1. **What's the analysis frame?**
   - *Single team over time*: how has one team's sound drifted from the baseline across
     multiple services? Baseline = the team's rendered Sunday Starter.
   - *Cross-team instrument*: how do multiple teams handle the same instrument group
     (e.g. drums, handheld, bass)? Baseline = `data/reference/Base.snap` (factory state).

2. **What's the focus?** (team name, instrument group, time window, or open question)

Capture the intent — you'll write it to the session folder shortly.

### Step 2 — Gather inputs

**Baseline** — accept either:
- A DSL assembly file (`assembly.yaml`): render it first, use the output as baseline
  ```bash
  cd /Users/mcox/dev/snapwright
  .venv/bin/snapwright render <assembly-path> --output /tmp/baseline-rendered.snap
  ```
  Then use `/tmp/baseline-rendered.snap` as the baseline.
- A `.snap` file: use directly.

**Post-service snapshots** — ask for the directory or individual paths.
Wing backup snapshots are typically on Matthew's machine; ask where they are.

**Min occurrences threshold** — default 3. Ask only if Matthew wants to adjust.

Confirm inputs before proceeding.

### Step 3 — Create session folder

```
data/evolution/YYYY-MM-DD-<team>-<focus>/
  intent.md     ← write now
  report.md     ← written after analysis
  decisions.md  ← appended during step 5
```

Write `intent.md` with: date, frame, baseline, snapshots, and the question being asked.

### Step 4 — Run the analysis

```bash
cd /Users/mcox/dev/snapwright
.venv/bin/snapwright analyze-evolution \
  "<baseline>" \
  "<snapshot1>" "<snapshot2>" ... \
  --output "data/evolution/YYYY-MM-DD-<team>-<focus>/report.md" \
  --min-occurrences <n>
```

### Step 5 — Synthesize internally, then present themes

**Read the full report silently. Do not present it.**

Synthesize into 3–6 themes. A theme names a coherent problem, not a list of facts.
Good themes cut across channels. Examples: "reverb sends are consistently too hot across
all vocalists", "three channels have faders substantially below where James runs them".

For each theme:
- One sentence naming the pattern
- Confidence: occurrence count, consistency, any ⚠️ flags
- One or two concrete examples — not exhaustive lists

Present as a short numbered list (aim for under 15 lines). Then stop and ask:
*"Which of these feels most worth acting on, or do you want to talk through any first?"*

**Do not enumerate every channel. Do not read the suggestions section aloud.**

### Step 6 — Work through decisions one at a time

For each theme Matthew wants to act on:
- State the specific suggestion in one sentence
- Show a compact table if comparing before/after across multiple channels
- Ask: accept, modify, or skip?
- If accepted or modified, append to `data/evolution/YYYY-MM-DD-<team>-<focus>/decisions.md`:

```markdown
### YYYY-MM-DD — [title]
**Decision**: [what]
**Rationale**: [pattern count, direction, median shift if relevant]
**Category**: escalated | autonomous
```

Move to the next decision without preamble. One at a time.

**Do not write to `docs/decisions.md`** — that file is for architectural decisions about
the system, not mixing decisions.

### Step 7 — Wrap up

Summarise: decisions logged, themes skipped and why, anything surprising worth flagging
for the next session. Note the session folder path.

Remind Matthew: DSL file changes are Phase 4 scope. This skill surfaces signal;
acting on it is a separate step.

---

## Baseline Strategy (reference)

| Frame | Baseline | Rationale |
|---|---|---|
| Single team over time | Rendered DSL for that team, or a saved Sunday Starter `.snap` | Shows drift from intended state |
| Cross-team instrument | `data/reference/Base.snap` | Common ancestor; shows what each team built on top |

The rendered DSL is preferred for single-team analysis because it represents the *intended*
state. As evolution sessions promote patterns back into the DSL, the rendered output
converges with reality and diffs naturally shrink over time.

---

## Reading Patterns (internal — not for presentation)

**Strong template candidates**: consistent direction (✓), no ⚠️ constant offset, count ≥ 4,
with recent occurrences.

**⚠️ constant offset**: all deltas identical — likely a stale baseline value corrected once
and held. Worth surfacing as a theme ("baseline may have wrong model/value for X") but
distinct from genuine recurring service adjustments.

**~ mixed direction**: context-dependent (e.g. fader varies with who's singing). Not a
template candidate unless Matthew flags it.

**High-value pattern types**:
- FX send routing (reverb/delay on/off) — structural preferences, stable per team
- EQ/dynamics/gate model changes — if consistent, base likely had wrong preset loaded
- Fader levels — check direction; consistent push in one direction = baseline is off
- Monitor sends — personal preferences, tend to be stable per team

**Significance thresholds** (already applied):
Fader/send level ≥ 2 dB · EQ gain ≥ 1.5 dB · Frequency ≥ 10% shift · Dynamics threshold ≥ 2 dB

---

## Project Context

- DSL source: `data/dsl/teams/`
- Reference snapshots: `data/reference/sunday-starters/`
- Factory baseline: `data/reference/Base.snap`
- Evolution sessions: `data/evolution/`
- Phase spec: `docs/phase-2-spec.md`

Promoting patterns to DSL files is **Phase 4** scope.
