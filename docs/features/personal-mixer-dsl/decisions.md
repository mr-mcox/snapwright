## Decisions

### 2026-03-09 — MX numbering follows P16 slot order, not historical console numbering

**Context**: The reference snap uses Back Vox=MX1, Guitars=MX2, etc. (historical ordering).
Slot-order assignment gives Drum Set=MX1 (slot 2, first group). These differ, meaning
MTX.in values in io.out won't match the reference.

**Choice**: Ordering-based numbering. MX1=Drum Set, MX2=Congas, MX3=Back Vox, MX4=Guitars,
MX5=Other Inst, MX6=Wireless. Diff harness stays masked for A.33-A.48 (the personal mixer
block is validated by unit tests, not by diff against the james reference snap).

**Rationale**: MX numbers are fully internal — operators never see them. Preserving
historical numbers would require either explicit numbering in YAML or an unintuitive
declaration order. Ordering-based numbering is simpler and self-documenting.

---

### 2026-03-09 — Renderer re-reads infrastructure.yaml for slot topology

**Context**: The assembly renderer needs the P16 slot topology (derived MX/USR numbers)
to write sends and USR sources. Two options: (a) pass topology through snap_template(),
(b) renderer re-reads infrastructure.yaml independently.

**Choice**: Renderer re-reads infrastructure.yaml via `get_p16_slots()`. Adds one YAML
read per render call (~1ms). Keeps `snap_template()` signature unchanged and avoids
threading topology state through the call chain.

**Rationale**: Simplicity wins at current scale. If performance becomes a concern,
the infrastructure YAML can be cached at module load time.

---

### 2026-03-09 — Empty group is valid; omitting a label leaves the slot silent

**Context**: James has no conga players on the P16. With the flat assembly structure,
Congas is simply absent from the dict rather than declared with an empty body.

**Choice**: Omitting a group label from the assembly dict is valid — the matrix still
gets its name and 0 dB fader from infrastructure, but no channels send to it. A team
with no congas simply has a silent MX2 slot on the P16.

---

### 2026-03-09 — Omitting an individual label leaves USR OFF; no null syntax needed

**Context**: James has no keys player. Initial design used `musician: null` (YAML null)
to express an unassigned slot. With the flat list syntax the null case doesn't arise
— you simply omit the label.

**Choice**: Omit Keys from the assembly dict. Infrastructure still writes "Keys" to
USR.5.name; renderer leaves user.grp=OFF. The P16 hardware strip still shows "Keys".

---

### 2026-03-09 — Piano added to James assembly at ch15, input A.1

**Context**: Reference snap had ch15 (Piano) wired to USR.4 but not in James's
assembly. Confirmed: grand piano permanently on stage, always on A.1. The mute
and low fader in the december reference snap were session decisions, not DSL defaults.

**Choice**: Piano added to James musicians (inherits musicians/piano.yaml), ch15,
input A.1. Personal mixer: `Piano: [piano]`. DSL renders ch15 as a normal active
channel; operator mutes on the night if needed.
