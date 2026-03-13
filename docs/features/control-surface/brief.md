---
feature: control-surface
date: 2026-03-12
commit: 6e48f10
branch: main
status: solution-space
read-when: "starting implementation"
---

## Problem

The rendered snapshot has no custom control surface configuration (`ce_data.layer`,
`ce_data.user`). Volunteers are trained to use a specific custom control layout —
particularly the "send on fader" flip for monitor adjustments. Without it, they
have no tool for their trained workflow and cannot manage monitors independently.
The right-surface User 1 layer is also absent.

## Not Doing

- Full programmatic generation of all standard pages (DCA, CH1-12, BUSES, etc.) —
  Init.snap defaults for those stand; only USER pages are modeled
- Strip content for left and center USER pages — selected page only for L/C
- Strategy-based layout switching (beginner/advanced views) — deferred to `strategy-overlays`

## Constraints

- `ce_data.layer` and `ce_data.user` are infrastructure-level: same for all teams,
  belong in infrastructure not assembly
- **DO NOT** carry a verbatim blob from James.snap into infrastructure.yaml — that
  approach was explored and rejected (86KB, unreadable, unmaintainable)
- **Only model USER pages** — standard pages (DCA, CH1-12, MAIN, BUSES, AUX) keep
  Init.snap defaults; the renderer only writes what the DSL specifies
- **Channel name resolution at infrastructure time** — names like `Handheld` resolve
  via the infrastructure `channels:` name table, not at assembly time. Extend ch37
  and ch38 entries in `channels:` with `name:` fields (even though their full config
  lives in the assembly) to make them resolvable here
- Bank sidecar files are opaque Wing JSON — one file per named bank in
  `data/dsl/user_banks/`, like musician files. Contents extracted from James.snap.
- The integration diff test must be widened to include `ce_data.layer` and
  `ce_data.user` — a passing diff against the James reference is the acceptance
  criterion for correctness

## DSL Sketch

Two new top-level sections in `infrastructure.yaml`:

```yaml
# ===========================================================================
# Control surface — user layer pages
# ===========================================================================

user_layers:
  right:
    selected: user1      # opens "send on fader" flip for monitors
    user1:
      - { channel: Handheld }
      - { channel: Headset }
      - { main: HOUSE }
      - { main: STREAM }

  # left and center: selected page only — strip content deferred
  left:
    selected: user1
  center:
    selected: main


# ===========================================================================
# Control surface — right-side user button banks
# ===========================================================================

user_banks:
  # Assign named banks to physical buttons 1–4 in order.
  # Reorder, remove, or null out to change what operators get.
  active:
    - monitors       # btn 1: monitor send levels per mix
    - vocals         # btn 2: lead/back vox faders + FX inserts
    - fx_sends       # btn 3: delay / reverb send controls
    - dca_fx         # btn 4: DCA FX mute
```

Bank sidecar files:
```
data/dsl/user_banks/
  monitors.json    ← extracted from James.snap ce_data.user.1
  vocals.json      ← extracted from James.snap ce_data.user.2
  fx_sends.json    ← extracted from James.snap ce_data.user.3
  dca_fx.json      ← extracted from James.snap ce_data.user.4
```

Wing encoding for strip types (resolved at render time):
- `channel: NAME` → look up name in infrastructure `channels:` → `{type: CH, i: N}`
- `main: NAME`    → look up name in infrastructure `mains:` → `{type: BUS, i: 16+N}`
  (Wing internal: HOUSE=17, STREAM=18)
- `bus: NAME`     → look up name in infrastructure `buses:` → `{type: BUS, i: N}`
- `dca: NAME`     → look up name in infrastructure `dca:` → `{type: DCA, i: N}`

Selected page name → Wing `sel` integer mapping:
  main=2, user1=6, user2=7  (right surface page order: MAIN/DCA/CH1-40/AUX/BUSES/USER1/USER2)

## Escalation Triggers

- If left/center USER page strip content is needed during this pass, pause — that
  expands scope
- If the Wing `sel` integer differs between surfaces (left vs right page ordering),
  pause — the mapping may need to be per-surface

## Decisions

(populated during implementation)
