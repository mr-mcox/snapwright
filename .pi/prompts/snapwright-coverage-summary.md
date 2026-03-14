---
description: Refresh coverage-report.json and regenerate docs/coverage.md
---
First, run `snapwright coverage` to regenerate `docs/coverage-report.json` from the
current renderer state.

Then regenerate `docs/coverage.md` — a human-readable explanation of renderer coverage
gaps. Start with the priority summary so the most actionable content is at the top.

## Inputs to read before writing

1. `docs/coverage-report.json` — the diff tree. Each node has `total` (leaf field count)
   and `changed` (fields that differ from Init.snap). Ratio = changed/total.
2. `agent.md` — project context: what Snapwright is, who uses it, and what it's for
3. `docs/ROADMAP.md` — project phase goals, what "done" looks like, current priorities
4. `docs/features/*/brief.md` — every feature brief. Use these to explain why gaps exist.
5. The existing `docs/coverage.md` if it exists — update rather than rewrite from scratch.

## How to read the diff tree

The JSON `diff_tree` is a recursive structure. Every node: `{total, changed, children?}`.
Ratio = `changed / total`. This surfaces three distinct patterns:

- **Zero ratio (0%)** — section not touched at all. Init.snap passes through.
- **High ratio (>10%)** — section substantially rendered.
- **Low ratio within a high-ratio parent, or siblings with sharply different ratios** —
  partial coverage. The renderer touches *something* here but leaves most of it alone.
  This is the most interesting signal: neither cleanly rendered nor cleanly skipped.

Examples visible in the current report:
- `ce_data.layer`: R is 2.1%, L is 0.2%, C is 0.3% — R gets real content, L/C get
  only a selected-page indicator. Partial coverage, visible from ratios alone.
- `ae_data.fx`: slots 1,2,5,6,7 at ~97-100%, slots 3,4,8-16 at 0% — only bus-wired
  FX slots are rendered.
- `ae_data.bus`: bus 8 at 0%, all others at 10-21% — bus 8 is intentionally skipped.
- `ce_data.user`: banks 1-4 at 12-69%, banks 5-16 at 0% — only right surface USER
  pages have strip content rendered.

## Three kinds of sections to classify

- **Not rendered (0%)** — Init.snap passes through. Classify as pass-through (Init
  default is intentionally correct) or gap (wrong/incomplete, deferral was conscious).
  Use feature brief "Not Doing" sections to distinguish.
- **Substantially rendered (>10%)** — the renderer owns this section. Document briefly.
- **Partial coverage** — low ratio within a rendered parent, or siblings with sharply
  different ratios. Treat as gaps: the renderer touches the section but leaves a
  meaningful sub-section unset.

## What to write for each gap

- **What it is** — what Wing functionality this controls (1-2 sentences)
- **Why it's not (fully) rendered** — cite the feature brief; note if Init default is
  wrong/incomplete vs. correct
- **What would be gained** — honest, specific operational value. Flag correctness gaps
  (something wrong on load) separately from convenience gaps (works, requires manual setup)

## Format

```markdown
# Snapwright Coverage — Gaps and Priorities

_Generated: [date]. Source: docs/coverage-report.json_

One paragraph: what this doc is, how it's generated, what to do with it.

---

## Priority: Gaps Worth Closing

[Ordered list, most to least impactful — see reasoning instructions below]

---

## Partial coverage (rendered sections with low-ratio sub-sections)

### [path] — [short description]
[What / why / what would be gained]

---

## Not-rendered gaps (0% ratio, Init.snap defaults are wrong or incomplete)

### [path]
[What / why / what would be gained]

---

## Pass-through (0% ratio, Init.snap defaults are intentionally correct)

### [path]
[One short paragraph]
```

## Reasoning for the priority section

Order gaps from most to least worth closing, given:
- The project's aim: complete, correct snapshots so volunteers load and have a working
  console without manual setup
- The Sunday service context: mistakes discovered mid-service are high-cost
- Correctness gaps (something wrong on load) outrank convenience gaps (works but
  requires manual setup after load)
- Feature brief deferral language calibrates whether a gap is "next natural step" vs.
  genuinely low priority

For each item: what it is, why it ranks here, what closing it would require (brief).

Write the file when done. Do not ask for confirmation first.
