---
feature: infrastructure-dsl
date: 2026-03-08
commit: 5d94430
branch: main
status: implementing
read-when: "starting or resuming implementation of Init.snap + infrastructure.yaml"
---

## Problem

The rendering pipeline uses Base.snap as its foundation — an opaque binary with accumulated debris (phantom faders, stale labels, mystery config). There's no way to audit what's intentional vs accidental, and no way to evolve infrastructure without manually editing a binary. The fix is Init.snap (factory reset) + infrastructure.yaml (every intentional change from factory, documented with purpose), replacing Base.snap entirely as the rendering foundation.

## Not Doing

- Full coverage of every Init→Base diff on day one; unmodeled sections pass through from Init (correct by definition)
- Strategy overlays or complexity levels (separate feature)
- Team-specific channel config — drums, bass, piano belong in musician/assembly files
- ce_data.user layers (separate feature)
- Custom USER bank layouts encoding operator skill level (future complexity-levels feature)
- Display/lighting console preferences (ce_data.cfg lighting, RTA colors) — personal, not operational

## Constraints

- Init.snap (`data/reference/Init.snap`, schema v11) is the rendering foundation — never modified
- Infrastructure YAML lives at `data/dsl/infrastructure.yaml`; single file, well-organized by section
- Every value in infrastructure.yaml must be self-documenting — no unexplained parameters
- Infrastructure scope = "how we run sound at BCF regardless of which team is playing": bus dynamics, main limiters, monitor start levels, fixed infrastructure channels (ch13 Computer, ch14 Handheld, ch40 Talkback), talkback routing, standard layer banks + R.USER1 default view, audio-consequential console preferences (solo mode, mute behavior)
- `#M8` tags are NOT set in infrastructure.yaml — renderer owns all tag assignment
- Confirmed debris explicitly omitted: `#M8` pre-tags on ch01–24, JEN label on io.in.A.7, +0.5 dB gain on io.in.A.8–A.30
- The existing channel pipeline (`_render()` for ae_data.ch) must continue to work — infrastructure is additive
- Existing 148 tests must continue to pass after switching from Base.snap to Init.snap
- New infrastructure rendering code gets TDD from day one

## Escalation Triggers

- If switching from Base.snap to Init.snap breaks more than 5 existing tests, pause — the value-level schema differences (send modes, main.1.on) may need a targeted patch strategy
- If infrastructure.yaml is becoming a dumping ground (values without clear operational justification), pause and reassess what belongs in team config instead
- If modeling a section requires significant new Pydantic schema beyond simple key→value, pause — worth checking if that section should be a separate feature
- If any Init.snap field needed by existing renderer code is absent or behaves differently than Base.snap, pause

## Decisions

(populated during implementation)
