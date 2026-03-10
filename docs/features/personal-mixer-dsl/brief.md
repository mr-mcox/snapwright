---
feature: personal-mixer-dsl
date: 2026-03-09
commit: dfce014
branch: infrastructure-dsl
status: implementing
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

Infrastructure declares all 16 P16 slots under a `personal_mixer:` key. Each slot
has a label, a type, and type-specific fields:

```yaml
personal_mixer:
  slots:
    - label: Bass          # shown on P16 hardware strip
      type: individual     # → USR source
    - label: Drum Set
      type: group          # → Wing matrix bus
    - label: Congas
      type: group
    - type: off            # physical slot not used
    - label: Lead 1
      type: individual
    - label: Lead 2
      type: individual
    - label: Back Vox
      type: group
    - type: off
    - label: Piano
      type: individual
    - label: Keys
      type: individual
    - label: Guitars
      type: group
    - label: Other Inst
      type: group
    - type: off
    - type: off
    - label: Wireless
      type: group
    - label: Drums Mon
      type: monitor
      bus: monitor_4       # logical bus name, resolved to bus number by renderer
```

### Slot numbering rules

- Group slots get consecutive MX numbers in the order they appear in the list
  (first group slot → MX1, second → MX2, etc.)
- Individual slots get consecutive USR numbers in the order they appear
  (first individual slot → USR.1, second → USR.2, etc.)
- OFF and monitor slots consume a physical A.xx output but allocate no Wing resource
- io.out A.33 = slot 1, A.34 = slot 2, ..., A.48 = slot 16

**Numbering alignment note**: The reference snap's MX numbering (Back Vox=MX1,
Guitars=MX2, Other Inst=MX3, Drum Set=MX4, Congas=MX5, Wireless=MX6) doesn't
match the P16 slot order (Drum Set at slot 2, Congas at slot 3). Strictly applying
"ordering determines numbering" will assign different MX numbers than the reference.
This affects io.out MTX.in values in the diff test. **Implementation decision**: adopt
ordering-based numbering (Drum Set → MX1, Congas → MX2, Back Vox → MX3, Guitars → MX4,
Other Inst → MX5, Wireless → MX6) and update the diff harness to unmask A.33-A.48 with
the new expected values. The MX numbers are fully internal — operators never see them.

### Assembly population (assembly.yaml)

```yaml
personal_mixer:
  groups:
    Drum Set:
      kick:       0    # level offset from 0 dB (omit to use default 0)
      snare:      0
      tom:        0
      overhead:   0
    Congas:
      # empty for James team — slot exists in infra but no musicians assigned
    Back Vox:
      anna-vox:   0
      yolaine-vox: 0
    Guitars:
      james-guitar: 0
      violin:       0
    Other Inst:
      flute:        0
    Wireless:
      handheld:     0
      headset:      0

  individuals:
    Bass:
      musician: bass
      tap: PRE
    Lead 1:
      musician: priscilla-vox
      tap: POST
    Lead 2:
      musician: james-vox
      tap: POST
    Piano:
      musician: piano          # infrastructure channel; renderer resolves ch number
      tap: PRE
    Keys:
      musician: ~              # null → USR grp=OFF; slot present but unassigned
      tap: PRE
```

### Wing field mechanics

**Group slots** (MX send rendering):
- Each musician in the group gets `ch.send.MX{n}`: `on: true, lvl: {level}, mode: PRE, plink: 1, pan: 0`
- Absent musicians (not on this team) write `on: false, lvl: -144` (same as Init default)
- Matrix bus: `ae_data.mtx.{n}` → name from infra label, fdr: 0, icon/color from Init defaults
- io.out routing: `{grp: MTX, in: (n*2)-1}` (L-channel convention, same as BUS)

**Individual slots** (USR source rendering):
- `ae_data.io.in.USR.{n}`: `name: {label}, user.grp: CH, user.in: {ch_number}, user.tap: {PRE|POST}, user.lr: L+R`
- `mode: M, mute: false, pol: false, col: 1, icon: 0, tags: ""`
- Null musician: `user.grp: OFF, user.in: 1`
- io.out routing: `{grp: USR, in: n}`

**Monitor slots** (bus passthrough):
- io.out routing: `{grp: BUS, in: (bus_num*2)-1}` — same formula as existing bus outputs
- No USR or MTX resource allocated

**OFF slots**:
- io.out routing: `{grp: OFF, in: 1}`

### Matrix fader defaults

Matrix faders default to 0 dB in the DSL. Reference faders (-0.34, +0.44, etc.) are
operator-adjusted session values. **Mask matrix faders in the diff harness** (same
treatment as monitor bus faders and main fader).

### Code placement

- Infrastructure slot topology parsing: `infrastructure.py`
- USR + MX send rendering: `renderer.py`, called during assembly render
- Diff harness updates: unmask A.33-A.48 io.out, mask `ae_data.mtx.{n}.fdr`

## Escalation Triggers

- If matrix slot allocation by ordering produces any conflict with matrices used for
  other purposes (currently none, but check during implementation), pause
- If the Wing's USR channel strip has fields beyond `mode/mute/pol/col/name/icon/tags/user`
  that need non-default values, surface before writing them as Init defaults
- If piano (ch15, infrastructure channel) isn't resolved correctly as a USR source
  target — ch15 is not in assembly.yaml musicians, renderer must handle infra channel
  references for individual slots

## Decisions

### 2026-03-09 — MX sends are the group mechanism (resolved)
**Context**: Reference snap james-2025-12-14 showed all MX sends OFF. James-2025-11-02
showed them live: kick/snare/tom/overhead → MX4, guitar/violin → MX2, flute → MX3,
anna/yolaine → MX1, handheld/headset → MX6. Congas group has no active sends for James
team (slot exists, empty assignment is valid).
**Choice**: Groups use `ch.send.MX{n}` from channels to matrix buses, PRE tap, plink=1.

### 2026-03-09 — USR tap points declared explicitly in assembly (resolved)
**Context**: Reference shows both PRE (Bass, Piano) and POST (Lead 1, Lead 2) taps in
use. No universal default applies.
**Choice**: Assembly declares tap per individual slot. No default — omitting tap is a
YAML validation error.

### 2026-03-09 — Keys slot always present, musician optional (resolved)
**Context**: "Keys" is a fixed P16 strip label. May or may not be assigned per team.
**Choice**: Infrastructure always declares the Keys slot as individual type. Assembly
sets `musician: ~` (null) when unassigned → USR grp=OFF. Label "Keys" always written
to USR source name regardless.

### 2026-03-09 — Matrix faders at 0 dB, masked in diff (resolved)
**Context**: Reference faders are operator-adjusted session values (-0.34 to +0.44 dB).
**Choice**: DSL default is 0 dB. Mask `ae_data.mtx.{n}.fdr` in diff harness.

### 2026-03-09 — A.48 is engineer's drum monitor (resolved)
**Context**: A.48 = BUS.in=31 = BUS.16 = Monitor/4. Confirmed as escape-hatch feed for
drummer who doesn't want to mix on the P16 themselves.
**Choice**: `type: monitor, bus: monitor_4` in infrastructure. Renderer writes BUS routing.

### 2026-03-09 — Piano is always in James's assembly (resolved)
**Context**: ch15 is a grand piano, permanently plugged into A.1. piano.yaml already exists.
The reference's mute=true and fdr=-51dB were session decisions (ambient pickup that night).
**Choice**: Add `piano` to James's assembly musicians (inherits musicians/piano.yaml, input A.1).
Personal mixer individuals: `Piano: { musician: piano, tap: PRE }`. DSL renders ch15 as
normal active channel; operator mutes on the night if needed.

### 2026-03-09 — A.7 excluded as vestigial (resolved)
**Context**: io.out.A.7 = MTX.in=1 in the james reference, outside P16 range. Not present
in other reference patterns. infra-output-routing explicitly deferred it.
**Choice**: Not expressed. Vestigial.
