## Decisions

### 2026-03-14 — Pi prompt location: .pi/prompts/ not docs/prompts/

**Context**: Brief specified `docs/prompts/snapwright-coverage-summary.md`. Pi loads
project-level prompt templates from `.pi/prompts/*.md`.

**Choice**: `.pi/prompts/snapwright-coverage-summary.md`

**Alternatives considered**: `docs/prompts/` with a settings.json entry pointing there.

**Rationale**: `.pi/prompts/` is the pi standard discovery path and already works with
the existing `.pi/settings.json`. Adding a non-standard path adds config noise for no
benefit. Brief updated mentally; the intent (a reachable pi prompt) is satisfied.

### 2026-03-14 — changed_keys for large sections lists all differing sub-keys

**Context**: `ae_data.ch` has 40 channels; the firmware Q patch touches all of them,
so `changed_keys` is a 40-element list of channel numbers. This is verbose in the JSON.

**Choice**: Keep it literal — list all differing top-level keys, no capping or summarizing.

**Alternatives considered**: Cap at N keys + `"...and N more"` string; emit a count instead.

**Rationale**: The JSON is for LLM consumption. 40 channel numbers is accurate signal —
the LLM understands this means the renderer touches all channels, not just active ones.
Summarizing would lose that signal. If JSON size becomes a problem, revisit.

### 2026-03-14 — Full recursive diff tree replaces hand-curated section list

**Context**: Initial implementation used a `_SIMPLE_SECTIONS` list with custom extractors
for slot ranges and grouped sources. This missed partial coverage within rendered sections
(e.g., L/C user layers) without additional prompt tricks.

**Choice**: Replace entirely with `_build_diff_tree` — a recursive diff that counts changed
and total leaf fields at every node, aggregated bottom-up. Section list is auto-discovered
from Init.snap structure. Partial coverage surfaces as ratio asymmetry between siblings.

**Alternatives considered**: Keep section list, add `changed_counts` to each entry (what
was briefly implemented). Richer than before but still required manual curation and prompt
tricks to catch within-section gaps.

**Rationale**: The ratio approach is strictly more informative and requires no manual
curation. Bus 8 at 0%, L/C at 0.2-0.3% vs R at 2.1%, FX slots 3/4/8-16 at 0% — all
visible from the data without reading a single feature brief.

### 2026-03-14 — ae_data.io.out.A slot ranges: 1–6, 7–32, 33–48

**Context**: Brief said split `ae_data.io.out.A` by slot range "matching actual renderer
behavior." Renderer writes: A.1–2 (main PA/stream), A.3–6 (monitors), A.33–48 (P16).
Slots 7–32 are unused.

**Choice**: Split at 1–6 (house/monitor outputs), 7–32 (unused gap), 33–48 (P16).

**Alternatives considered**: 1–2 / 3–6 / 7–32 / 33–48 (four ranges, separating PA from monitors).

**Rationale**: PA outputs (1–2) and monitor outputs (3–6) are both rendered by the same
feature (infra-output-routing) and represent the same concept (infrastructure physical
outputs). Splitting them further adds rows without adding coverage signal.
