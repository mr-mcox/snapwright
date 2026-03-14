## Decisions

### 2026-03-12 - Strip order: STREAM before HOUSE in user1 bank

**Context**: Brief DSL sketch listed `{ main: HOUSE }` then `{ main: STREAM }`, but
James.snap has STREAM (BUS 18) at strip 3 and HOUSE (BUS 17) at strip 4.

**Choice**: Match James.snap order — STREAM first, HOUSE second. Updated infrastructure.yaml accordingly.

**Alternatives considered**: Follow the brief DSL sketch literally (HOUSE first). This would
fail the integration diff test.

**Rationale**: The acceptance criterion is a passing diff against the James reference. The
brief DSL was written from memory; the reference snap is authoritative.

---

### 2026-03-12 - Infra channels: moved handheld/headset to infrastructure level

**Context**: User raised that teams could forget to configure ch37/ch38, leaving the
pastor's mic unconfigured (no EQ, dynamics, routing).

**Choice**: Added `infra_channels:` section to infrastructure.yaml. ch37/ch38 are now
always rendered from `musicians/handheld.yaml` and `musicians/headset.yaml` regardless
of which team assembly is loaded. Teams keep thin override entries (fader, mute) but
no longer need `inherits:` or input assignments.

**Alternatives considered**:
1. Keep in assembly with inherits — status quo, fragile (easy to forget)
2. Inline the full config in infrastructure.yaml channels: section — works but loses
   the musician file inheritance pattern and duplicates the config

**Rationale**: Infrastructure is the right layer for config that is constant across all
teams. The musician files are already the source of truth for EQ/dynamics; using them
at infra time is consistent with existing patterns.

**Implementation note**: Assembly renderer now starts each channel from
`snap["ae_data"]["ch"][str(ch_num)]` (the snap_template state after infra is applied)
instead of `channel_defaults(ch_num)` (raw Init.snap). This lets infra-applied channel
config persist as the base for team overrides. `_patch_firmware` gains the tapwid
default since `channel_defaults` no longer provides it.

---

### 2026-03-12 - User bank sidecar files: opaque JSON extracted from James.snap

**Context**: The ce_data.user layer content (monitor sends, vocal processing shortcuts,
FX sends, DCA FX) is complex Wing JSON with many implicit relationships. The brief
called for opaque sidecar files.

**Choice**: Extracted ce_data.user.1-4 directly from James.snap as JSON files in
data/dsl/user_banks/. The infrastructure renderer loads and places them verbatim.

**Alternatives considered**: Model each layer in DSL YAML — would be thorough but
high-effort with no immediate benefit. The sidecar approach is readable and
maintainable since the files can be regenerated from any reference snap.

**Rationale**: The brief was explicit: "bank sidecar files are opaque Wing JSON."
The opaque approach keeps the scope bounded; if future layers need modeling they
can be added incrementally.
