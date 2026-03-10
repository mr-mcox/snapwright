---
feature: infra-dsl-vocabulary
date: 2026-03-09
commit: bd53dc5
branch: infrastructure-dsl
status: implementing
read-when: starting implementation of infra vocabulary cleanup
---

## Problem

`infrastructure.yaml` uses raw Wing snap field names (`thr`, `att`, `rel`, `mdl`, `in`, `out`,
`2g`, `2f`, `2q`) even though the DSL renderer already has human-readable translations for these
concepts. The file serves two purposes — IaaC record of intentional house config, and source of
truth for feedback-driven tuning ("drums are always hitting the house limiter, adjust the
threshold") — neither of which works well without knowing Wing internals. Wing field names also
hide implementation artifacts that shouldn't appear in config at all (`rel: "0.4"` as a quoted
string, `ratio: "20"`, the bus 8 Q-reset block).

Scope decisions are driven by **effort/impact**: translate anything a trained operator would
want to evolve based on service feedback; leave alone anything that's set-once preset data.

## Not Doing

- FX internal parameters that are preset blobs (`erpdly`, `ertype`, `lxo`, `mxo`, `hxo`,
  `mtype`, `mrate`, etc.) — high effort to name, zero feedback-loop value
- Wing metadata (`icon`, `col`, `led`) — deferred; useful long-term for visual setup but
  not part of the feedback loop this feature targets
- Bus 8 entirely — never operator-configured, factory debris; mask in diff harness

## Constraints

- infrastructure.yaml must remain valid (diff harness stays green, 178 tests pass)
- DSL vocabulary must match what the channel renderer already uses — no new names invented
- Wing string-encoding artifacts (`rel: "0.4"`, `ratio: "20"`) hidden in the renderer, not YAML
- Bus 8 Q-reset block removed from `infrastructure.yaml`; bus 8 masked in diff harness
- Translation layer lives in `infrastructure.py`; `infrastructure.yaml` stays a pure data file
- EQ bands are in scope: `2g`/`2f`/`2q` → readable equivalents (same reasoning as dynamics)

## Escalation Triggers

- If bus dynamics DSL names conflict with how the channel renderer uses those same names, pause —
  consistency across both files matters more than either individually
- If a FX parameter inside a blob has obvious high-character-impact (`lc`, `hc`, `dcy`, `time`,
  `rep`) and a clear human name, surface it rather than leaving it as a Wing name — don't
  pre-decide all of them now, evaluate as encountered

## Decisions

_(populated during Phase 3)_
