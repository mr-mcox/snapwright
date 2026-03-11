## Decisions

### 2026-03-09 — Use James reference snapshot values as infrastructure fdr defaults

**Context**: Brief said "~0 dB for active mix buses" and "reasonable operational starting point"
for mains, but deferred exact values to user judgment (escalation trigger). The James reference
had main 1 (HOUSE) at -35.43 dB — clearly not a "0 dB default" situation. User directed:
use James snapshot values to get the integration diff test to pass.

**Choice**: Set fdr in infrastructure.yaml to the exact values from `James.snap`:
buses 1–7 and 9–12 (all active buses); mains 1–2. Monitor buses 13–16 excluded
(session-adjusted; Init default 0 dB stands).

**Alternatives considered**:
- 0 dB for all active buses + mains — clean default but diff test would show residual noise
- Split main 1 at -144, main 2 at 0 — safe but arbitrary

**Rationale**: Integration diff as acceptance criterion is the guiding star. Reference values
represent deliberate operator choices for this console's operational state. Main 1 at -35 dB
is where James leaves the house PA after a service — a known, stable position.
