---
feature: personal-mixer-dsl
date: 2026-03-09
commit: bdc991a
branch: personal-mixer-dsl
status: compacting
read-when: starting implementation of P16 personal mixer abstraction
---

## Problem

The Behringer P16 personal mixer uses the last 16 stage-box outputs (A.33-A.48),
currently configured manually on the console — not expressed in the DSL at all.
Each slot carries either a group submix (multiple musicians blended → Wing matrix),
a single musician tap (→ Wing user source), or a monitor bus feed. The DSL should
let infrastructure declare the slot topology once and let each team assembly
populate who feeds what, hiding the matrix/USR/io.out mechanics entirely.

## Not Doing

- Per-slot level mixing within the P16 itself (that's the hardware unit's job)
- Changing the physical slot→output assignment at assembly time (fixed in infra)
- MX1-MX8 Wing send keys for anything other than P16 group routing (confirmed
  these are the mechanism for channel→matrix sends; no other purpose in reference)
- A.7: vestigial MTX.1 output outside the P16 range — confirmed, excluded

## Constraints

### Slot topology (infrastructure.yaml)

Infrastructure declares slots as a dict keyed by slot number (1–16). Absent
slot numbers are implicit OFF — no need to declare unused slots:

```yaml
personal_mixer:
  slots:
    1:  { label: Bass,       type: individual, tap: PRE  }
    2:  { label: Drum Set,   type: group }
    3:  { label: Congas,     type: group }
    5:  { label: Lead 1,     type: individual, tap: POST }
    6:  { label: Lead 2,     type: individual, tap: POST }
    7:  { label: Back Vox,   type: group }
    9:  { label: Piano,      type: individual, tap: PRE  }
    10: { label: Keys,       type: individual, tap: PRE  }
    11: { label: Guitars,    type: group }
    12: { label: Other Inst, type: group }
    15: { label: Wireless,   type: group }
    16: { label: Drums Mon,  type: monitor,    bus: monitor_4 }
    # slots 4, 8, 13, 14 absent → implicit OFF
```

### Slot numbering rules

- Group slots get consecutive MX numbers in ascending slot-number order
  (first group by slot number → MX1, second → MX2, etc.)
- Individual slots get consecutive USR numbers in ascending slot-number order
- OFF and monitor slots consume a physical A.xx output but allocate no Wing resource
- io.out A.33 = slot 1, A.34 = slot 2, ..., A.48 = slot 16
- MX numbers are fully internal — operators never see them

### Assembly population (assembly.yaml)

A single flat dict: slot-label → list of musicians. Tap points come from the
infrastructure slot definition, not the assembly. Omit a slot to leave it OFF:

```yaml
personal_mixer:
  Bass:       [bass]
  Drum Set:   [kick, snare, tom, overhead]
  Lead 1:     [priscilla-vox]
  Lead 2:     [james-vox]
  Back Vox:   [anna-vox, yolaine-vox]
  Piano:      [piano]
  Guitars:    [james-guitar, violin]
  Other Inst: [flute]
  Wireless:   [handheld, headset]
  # Congas omitted → MX2 silent, matrix still named
  # Keys omitted → USR.5 stays OFF, label still written by infrastructure
```

- Individual slots: list must have 0 or 1 musician. More than 1 raises `ValueError`.
- Monitor slots: nothing to declare in assembly (bus is fixed in infrastructure).
- All MX send levels are 0 dB — per-musician P16 mixing is the hardware's job.

### Wing field mechanics

**Group slots** (MX send rendering):
- Each musician in the group gets `ch.send.MX{n}`: `on: true, lvl: 0.0, mode: PRE, plink: true, pan: 0`
- Matrix bus: `ae_data.mtx.{n}` → name from infra label, fdr: 0 dB, icon/color from Init defaults
- io.out routing: `{grp: MTX, in: (n*2)-1}` (L-channel convention, same as BUS)

**Individual slots** (USR source rendering):
- Infrastructure writes label to `ae_data.io.in.USR.{n}.name`; user.grp stays OFF
- Assembly writes: `user.grp: CH, user.in: {ch_number}, user.tap: {from infra}, user.lr: L+R`
- Omitted from assembly: user.grp stays OFF, label preserved
- io.out routing: `{grp: USR, in: n}`

**Monitor slots** (bus passthrough):
- io.out routing: `{grp: BUS, in: (bus_num*2)-1}` — same formula as existing bus outputs
- Bus resolved via hardcoded `_MONITOR_BUS_NUMBERS` map in infrastructure.py

**OFF slots**:
- io.out routing: `{grp: OFF, in: 1}`

### Matrix fader defaults

Matrix faders default to 0 dB in the DSL. Reference faders (−0.34, +0.44, etc.) are
operator-adjusted session values. **Mask matrix faders in the diff harness**.

### Code placement

- `infrastructure.py`: `get_p16_slots()` parses topology; `_apply_personal_mixer()`
  writes matrix names/faders, USR labels, io.out A.33-A.48 — called from `apply_infrastructure()`
- `renderer.py`: `_apply_personal_mixer_assembly()` writes MX sends and USR channel
  assignments — called from `_render()` after channel rendering
- `schema.py`: `AssemblyDef.personal_mixer: dict[str, list[str]] | None`

## Decisions

### 2026-03-09 — Dict-keyed slots, implicit OFF, flat assembly structure

**Context**: v1 design used an ordered list with explicit `type: off` entries and
a split `groups:`/`individuals:` assembly section with per-musician level values and
tap points in the assembly.

**Choice**: Infrastructure uses a dict keyed by slot number; absent slots are implicit
OFF. Assembly is a flat `label → [musicians]` dict. Tap points live in infrastructure
(they're the same every week for a given slot). All MX send levels are 0 dB.

**Rationale**: Cleaner to read — you see exactly which physical slots are occupied.
No `type: off` clutter. Assembly is homogeneous (no groups/individuals distinction
the operator needs to know about). Level control belongs to the P16 hardware.

---

### 2026-03-09 — MX sends are the group mechanism

**Context**: Reference snap james-2025-12-14 showed all MX sends OFF. James-2025-11-02
showed them live: kick/snare/tom/overhead → MX4, guitar/violin → MX2, flute → MX3,
anna/yolaine → MX1, handheld/headset → MX6. Congas group has no active sends for James
team (slot exists, empty assignment is valid).

**Choice**: Groups use `ch.send.MX{n}` from channels to matrix buses, PRE tap, plink=true.

---

### 2026-03-09 — Tap points in infrastructure, not assembly

**Context**: Reference shows both PRE (Bass, Piano) and POST (Lead 1, Lead 2) taps.
Initial design put tap in assembly per-individual. Discussion moved it to infrastructure
since the tap point reflects the nature of the slot (vocalists need POST, instrument
taps need PRE) not team-specific config.

**Choice**: `tap: PRE|POST` declared on the infrastructure slot. Renderer reads it from
the slot definition when writing USR sources. Not present in assembly YAML.

---

### 2026-03-09 — Omitting a slot label = OFF; no explicit null needed

**Context**: Initial design used `musician: ~` (YAML null) for unassigned individual
slots. With flat list syntax, omitting the slot entirely is cleaner.

**Choice**: Assembly simply omits slot labels that have no assignment. Infrastructure
still writes the USR name; renderer leaves user.grp=OFF. Congas and Keys both absent
from James assembly.

---

### 2026-03-09 — MX numbering by slot position, historical numbers not preserved

**Context**: Reference snap used Back Vox=MX1 (historical). Slot-order assignment
gives Drum Set=MX1 (slot 2, first group). These differ, meaning MTX.in values in
io.out won't match the reference.

**Choice**: Ordering-based numbering. Diff harness continues to mask A.33-A.48
(validated by unit tests, not diff against reference snap). Historical MX numbers
are fully internal — operators never see them.

---

### 2026-03-09 — Matrix faders at 0 dB, masked in diff

**Context**: Reference faders are operator-adjusted session values (−0.34 to +0.44 dB).

**Choice**: DSL default is 0 dB. Mask `ae_data.mtx.{n}.fdr` in diff harness.

---

### 2026-03-09 — A.48 is engineer's drum monitor

**Context**: A.48 = BUS.in=31 = BUS.16 = Monitor/4. Escape-hatch feed for the drummer
who doesn't want to mix on the P16 themselves — engineer sets the mix at the board.

**Choice**: `type: monitor, bus: monitor_4` in infrastructure. Renderer writes BUS routing.

---

### 2026-03-09 — Piano added to James assembly; always at ch15, A.1

**Context**: Grand piano permanently on stage, always on stage-box A.1. piano.yaml
already existed. The reference's mute=true and fdr=−51dB were session decisions.

**Choice**: Piano added to James musicians (inherits musicians/piano.yaml, input A.1).
Personal mixer: `Piano: [piano]`. DSL renders ch15 as a normal active channel.
