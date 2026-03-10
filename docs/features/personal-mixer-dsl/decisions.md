## Decisions

### 2026-03-09 — MX numbering follows P16 slot order, not historical console numbering

**Context**: The reference snap uses Back Vox=MX1, Guitars=MX2, etc. (historical ordering).
Strict "ordering determines numbering" (slot 2=Drum Set becomes MX1) produces different
MTX.in values in io.out. The diff harness currently masks A.33-A.48 entirely.

**Choice**: Ordering-based numbering. MX1=Drum Set, MX2=Congas, MX3=Back Vox, MX4=Guitars,
MX5=Other Inst, MX6=Wireless. Diff harness stays masked for A.33-A.48 (the personal mixer
block is validated by unit tests, not by diff against the james reference snap).

**Rationale**: MX numbers are fully internal — operators never see them. Preserving
historical numbers would require either explicit numbering in YAML or an unintuitive
declaration order. Ordering-based numbering is simpler and self-documenting.

---

### 2026-03-09 — infrastructure.py reads infrastructure.yaml; renderer re-reads for slot topology

**Context**: The assembly renderer needs the P16 slot topology (derived MX/USR numbers)
to write sends and USR sources. Two options: (a) pass topology through snap_template(),
(b) renderer re-reads infrastructure.yaml independently.

**Choice**: Renderer re-reads infrastructure.yaml via `get_p16_slots()`. Adds one YAML
read per render call (~1ms). Keeps `snap_template()` signature unchanged and avoids
threading topology state through the call chain.

**Rationale**: Simplicity wins at current scale. If performance becomes a concern,
the infrastructure YAML can be cached at module load time.

---

### 2026-03-09 — Congas group empty for James team; empty group is valid

**Context**: James's assembly declares `Congas:` with no musicians. No channels
send to MX2. The matrix (MX2) still gets its name and 0 dB fader from infrastructure.

**Choice**: Empty group is valid. Infrastructure always creates the matrix; assembly
assigns members. A team with no congas simply has a silent MX2 slot on the P16.

---

### 2026-03-09 — Keys slot rendered as USR grp=OFF when musician is null

**Context**: James has no keys player. Assembly declares `musician: null`. The "Keys"
label is still written to USR.5 by infrastructure; assembly leaves user.grp=OFF.

**Choice**: Null musician → OFF source. Label is preserved infrastructure-side so
the P16 hardware strip still shows "Keys" even when unassigned.

---

### 2026-03-09 — Piano added to James assembly at ch15, input A.1

**Context**: Reference snap had ch15 (Piano) wired to USR.4 but not in James's
assembly. Confirmed: grand piano permanently on stage, always on A.1. The mute
and low fader in the december reference snap were session decisions, not DSL defaults.

**Choice**: Piano added to James musicians (inherits musicians/piano.yaml), ch15,
input A.1. Personal mixer individual slot wired: `musician: piano, tap: PRE`.
DSL default fader is musicians/piano.yaml default (0 dB); operator adjusts live.
