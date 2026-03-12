---
feature: tags-ownership
date: 2026-03-08
commit: 9b4bb7b
branch: main
status: compacting
read-when: "if revisiting tag behaviour"
---

## Problem

DCA and mute group membership is encoded in the `tags` field on channels and buses (`#D5`, `#M8`, etc.). The renderer currently never writes tags — they pass through from the base template. This means:
- Channels 5-8, 25-28 are missing `#M8` (Worship mute group) — the kill-switch doesn't cover them
- All DCA membership tags on buses were lost during the bus consolidation — DCAs 1-4, 6-7 have zero members
- Monitor buses lost `#D7` and `#M7` — the monitor DCA and mute group are broken
- Tags correctness depends on which channels happen to have `#M8` in the base template — fragile

## Not Doing

- DCA/mgrp *config* rendering (names, faders, mute states) — that's `dca-mgrp-rendering`
- Tag ordering optimization (Wing doesn't appear to care about tag order)
- Tags on aux, main, or matrix buses (not used in any reference snapshot)

## Constraints

- Renderer owns tags completely — rebuilds `ch.tags` and `bus.tags` from DSL declarations, no merge with base template
- Infrastructure layer declares DCA and mgrp membership for buses (e.g., bus 1 is in DCA 1 "Rhythm" and MGRP 1 "Rhythm")
- Assembly declares mute group membership for channels — specifically `#M8` (Worship) on all active worship channels
- Tag format: comma-separated `#D<n>` and `#M<n>` tokens (e.g., `#D6,#M5,#D1,#M1`)
- Tag building is a pure function: inputs = list of DCA numbers + list of MGRP numbers → output = tag string
- Channels not in the assembly get empty tags (Init default)
- Depends on `infrastructure-dsl` for the base template switch
- TDD from day one

## Escalation Triggers

- If tag ordering matters to the Wing (test by loading snapshots with different tag orders), pause
- If tags need to support values beyond `#D<n>` and `#M<n>` (e.g., custom tags), pause — scope expansion

## Decisions

- **2026-03-09** Assembly-level `channel_mute_groups`/`channel_dcas` on `AssemblyDef`; per-musician
  override via `mute_groups`/`dcas` on `MusicianEntry`. Renderer owns `ch.tags` completely
  (clears all first, then writes from DSL). Bus tags left as raw strings in infrastructure.yaml
  (already correct; no structural change needed).
- **2026-03-09** Integration diff: `ch_tags` section added covering all 18 assembly channels.
