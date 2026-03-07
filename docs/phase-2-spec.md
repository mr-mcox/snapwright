# Phase 2: Snapshot Evolution Analysis

## Goal

Batch-compare post-service snapshots against a Sunday Starter baseline to surface recurring volunteer adjustments worth promoting into DSL templates. Run every 1–3 months against accumulated snapshots.

## Inputs

- **Baseline**: Sunday Starter snapshot (e.g., James.snap, saved Nov 26 2025)
- **Post-service snapshots**: N snapshots saved after services over the analysis window

## Outputs

1. **Per-snapshot diff summary** — organized by channel name in audio-meaningful terms (e.g., "Kick: HPF 80→100Hz, compressor threshold −2dB"), not raw Wing JSON paths
2. **Cross-snapshot pattern report** — recurring changes flagged across multiple snapshots (e.g., "In 4 of 6 snapshots, James vocal fader lowered 3–5dB")
3. **Suggestions** — human-readable recommendations for Sunday Starter template updates, with supporting evidence

## Approach

- **Channel mapping via names**: Wing JSON channel names (Kick, Snare, James, Flute, etc.) are stable and descriptive across all snapshots — no assembly inverse mapping needed
- **Audio-semantic translation**: Wing param paths (`ch/1/eq/b2/f`) → human terms ("Kick EQ band 2 frequency"). Built as a translation layer on top of Phase 0 diff tooling
- **Batch pattern detection**: Load all diffs, group by channel + parameter, flag changes that recur across multiple snapshots vs one-off adjustments
- **Pi skill**: Wraps the workflow for periodic re-runs with new snapshot batches

## Simulation

Validate the pipeline using 2025 James team snapshots from `/Users/mcox/Documents/Wing Backup/2025-12-14/snapshots/`:
- James 2025-04-06
- 2025-05-18 James
- 2025-06-01 James
- 2025-07-27 James
- 2025-08-10 James
- 2025-08-24 James
- James 2025-09-21
- James 2025-10-05
- 2025-11-02 James

**Simulation baseline**: `James 2025-04-06.snap` (earliest in set — simulates a pre-refinement Sunday Starter)
**Simulation targets**: the 8 subsequent snapshots (May–November 2025)
**Validation artifact**: `data/reference/sunday-starters/James.snap` (saved Nov 26 2025) — patterns surfaced from the batch should roughly predict what was eventually baked into this refined snapshot

## Not in scope

- Auto-generating DSL YAML changes (that's Phase 4 promotion)
- Real-time / per-service workflow (batch only)
- Cross-team analysis (one team at a time)

---

## Escalation Triggers (pause and show Matthew)

### Report Content & Framing
- **Pattern threshold**: 3+ occurrences = signal, especially if recent. Independent convergence on the same adjustment is strong evidence of a real problem/solution pair.
- **Intentional vs situational**: Let emerge during simulation — no rule upfront.
- **Report organization**: By channel/instrument. We're looking at adjustments to individual musicians or buses, not aggregate parameter-type views.
### Audio-Semantic Translation Choices
- **Parameter naming**: Stay close to DSL vocabulary — terms engineers already use in the YAML files.
- **Reporting threshold**: Moderate to large changes only. ~1dB level shifts are below audible threshold for the congregation; broad-stroke changes are the target. Exact cutoffs TBD in simulation (hypothesis: ≥2–3dB for levels, meaningful frequency/threshold shifts for EQ/dynamics).
- **Level changes**: Deltas from baseline (e.g., "−4dB") plus resulting absolute value.
### Suggestion Boundaries
- **Format**: "Consider [action]" framing but with a clear concrete action — e.g., "Consider lowering James vocal fader from −3dB to −7dB in the Sunday Starter" rather than just "vocals seem loud."
- **Threshold for suggestion**: Emerges from simulation.
### Workflow Shape
- Batch, independent per run. No cross-run accumulation.
- Pi skill invocation details: emerge during simulation.

---

## Iterate Freely (decide and log)

- Diff algorithm internals and data structures
- Wing param path → human term mapping implementation
- File organization and module decomposition
- Test strategy for the translation and pattern detection layers
- Output format details (markdown, YAML, etc.) within the constraints above
- How to handle unnamed/empty channels in diffs
- Float tolerance reuse from Phase 0
