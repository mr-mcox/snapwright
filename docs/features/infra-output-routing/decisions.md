## Decisions

### 2026-03-09 — LCL outputs masked, not cleared
**Context**: Init.snap has LCL.1-8 with factory default routing (buses 1-6, mains 1-2).
James reference snap has vestigial LCL.1 and LCL.6 entries (MAIN.3) not present in priscilla.
**Choice**: Mask LCL port group entirely in the diff harness. Don't clear Init defaults in renderer. Don't express james's vestigial LCL entries in infrastructure.yaml.
**Alternatives considered**: Explicitly clear LCL.1-8 to OFF in the renderer (adds code, no operational benefit if nothing is plugged into local outs).
**Rationale**: If local outs aren't connected, the Init defaults are harmless. Masking in the diff harness is sufficient. James's LCL entries are vestigial — confirmed by absence in priscilla.

### 2026-03-09 — AUX.6 priscilla-only, not in infrastructure
**Context**: AUX.6: {grp: MAIN, in: 1} appears in priscilla-team.snap but NOT in james-2025-12-14.snap.
**Choice**: Not expressed in infrastructure.yaml. Priscilla-specific wiring or vestigial.
**Rationale**: James is the diff-harness reference; AUX.6 absent there means it's not infrastructure.

### 2026-03-09 — A.7 (MTX.1) deferred to personal-mixer-dsl
**Context**: James reference snap has io.out.A.7: {grp: MTX, in: 1}, absent in priscilla.
**Choice**: Not expressed in infrastructure.yaml. Deferred to personal-mixer-dsl feature.
**Rationale**: MTX routing is personal-mixer territory. Consistent with brief's Not Doing scope.

### 2026-03-09 — aux structural defaults as a fixed rendering patch
**Context**: Init.snap aux send modes are PRE for buses 1-8, GRP for 9-10, POST for 11-16.
Both james and priscilla have POST for buses 1-12, PRE for 13-16.
**Choice**: Apply as a fixed patch in apply_infrastructure (same class as firmware Q patches),
not expressed per-aux-channel in infrastructure.yaml. aux.1 name "USB 1/2" expressed in YAML.
**Alternatives considered**: Expressing full send dicts per aux channel in infrastructure.yaml
(very verbose — 16 send entries × 8 aux channels with no operator-relevant variation).
**Rationale**: The pattern is universal and invariant. No team will differ. Hardcoding it
keeps infrastructure.yaml readable and focused on operator-meaningful values.
