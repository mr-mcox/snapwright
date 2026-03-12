"""Stage box label rendering tests.

Validates that the renderer writes name, icon, and preamp gain to
io.in.A[slot] for each musician in the assembly's inputs map.

Acceptance criteria:
- Slots assigned in the assembly carry musician name, icon, and preamp_gain.
- Slots NOT in the assembly keep Init.snap defaults (blank name, 0 gain).
- Non-stage-box sources (local, usb) do not write to io.in.A.
- preamp_gain is a musician property — resolved from the inheritance stack,
  not from the input assignment.
"""

from pathlib import Path

import pytest

from snapwright.dsl.renderer import render_assembly

JAMES_ASSEMBLY = Path("data/dsl/teams/james/assembly.yaml")

# ---------------------------------------------------------------------------
# Reference-aligned slots: name, icon, gain all match James.snap
# ---------------------------------------------------------------------------

# musician_name -> (slot, expected_name, expected_icon, expected_gain)
_JAMES_SLOT_CHECKS = [
    ("piano",         1,  "Piano",    400,  38.0),
    ("kick",          2,  "Kick",     200,  28.0),
    ("snare",         3,  "Snare",    202,  15.5),
    ("overhead",      4,  "Overhead", 210,  33.0),
    ("tom",           5,  "Tom",      208,  18.0),
    ("bass",          6,  "Bass",     302,  15.5),
    ("conga-1",       7,  "Conga 1",  215,  28.0),
    ("conga-2",       8,  "Conga 2",  215,  30.5),
    ("bongos",        9,  "Bongos",   216,  23.0),
    ("james-vox",     10, "James",    0,    38.0),
    ("priscilla-vox", 11, "Pricilla", 0,    33.0),
    ("anna-vox",      12, "Anna",     0,    45.5),
    ("yolaine-vox",   13, "Yolaine",  0,    45.5),
    ("james-guitar",  14, "James",    306,  23.0),
    ("headset",       31, "Headset",  105,  35.5),
    ("handheld",      32, "Handheld", 102,  30.5),
]


@pytest.fixture(scope="module")
def james_rendered():
    return render_assembly(JAMES_ASSEMBLY)


@pytest.fixture(scope="module")
def io_a(james_rendered):
    return james_rendered["ae_data"]["io"]["in"]["A"]


@pytest.mark.parametrize(
    "musician,slot,expected_name,expected_icon,expected_gain",
    _JAMES_SLOT_CHECKS,
    ids=[c[0] for c in _JAMES_SLOT_CHECKS],
)
def test_slot_name(io_a, musician, slot, expected_name, expected_icon, expected_gain):
    assert io_a[str(slot)]["name"] == expected_name, (
        f"A[{slot}] ({musician}): expected name {expected_name!r}"
    )


@pytest.mark.parametrize(
    "musician,slot,expected_name,expected_icon,expected_gain",
    _JAMES_SLOT_CHECKS,
    ids=[c[0] for c in _JAMES_SLOT_CHECKS],
)
def test_slot_icon(io_a, musician, slot, expected_name, expected_icon, expected_gain):
    assert io_a[str(slot)]["icon"] == expected_icon, (
        f"A[{slot}] ({musician}): expected icon {expected_icon}"
    )


@pytest.mark.parametrize(
    "musician,slot,expected_name,expected_icon,expected_gain",
    _JAMES_SLOT_CHECKS,
    ids=[c[0] for c in _JAMES_SLOT_CHECKS],
)
def test_slot_gain(io_a, musician, slot, expected_name, expected_icon, expected_gain):
    assert io_a[str(slot)]["g"] == expected_gain, (
        f"A[{slot}] ({musician}): expected gain {expected_gain}"
    )


# ---------------------------------------------------------------------------
# Unassigned slots keep Init.snap defaults
# ---------------------------------------------------------------------------

# Slots 19-30 are not in the James assembly
_UNASSIGNED_SLOTS = list(range(19, 31))


@pytest.mark.parametrize("slot", _UNASSIGNED_SLOTS)
def test_unassigned_slot_name_blank(io_a, slot):
    """Slots not in the assembly keep blank name (Init.snap default)."""
    assert io_a[str(slot)]["name"] == "", f"A[{slot}] should have blank name"


@pytest.mark.parametrize("slot", _UNASSIGNED_SLOTS)
def test_unassigned_slot_gain_zero(io_a, slot):
    """Slots not in the assembly keep 0 gain (Init.snap default)."""
    assert io_a[str(slot)]["g"] == 0, f"A[{slot}] should have 0 gain"


# ---------------------------------------------------------------------------
# preamp_gain is inherited through the musician stack
# (conga-2 inherits from conga-1, overrides gain independently)
# ---------------------------------------------------------------------------

def test_conga_2_gain_differs_from_conga_1(io_a):
    """conga-2 (30.5 dB) has a different gain than conga-1 (28 dB) —
    confirming per-musician override works through inheritance."""
    assert io_a["7"]["g"] == 28.0   # conga-1
    assert io_a["8"]["g"] == 30.5   # conga-2


# ---------------------------------------------------------------------------
# io.in.A diff vs James reference (informational — not a hard pass/fail)
# ---------------------------------------------------------------------------

def test_stage_box_diff_vs_reference(james_rendered):
    """Print io.in.A diff for assembly-covered slots against James reference.

    This test always passes. Run with -s to see the diff output.
    Slots where the assembly has diverged from the reference are expected.
    """
    import json

    from deepdiff import DeepDiff

    ref = json.load(open("data/reference/sunday-starters/James.snap"))
    ref_a = ref["ae_data"]["io"]["in"]["A"]
    rend_a = james_rendered["ae_data"]["io"]["in"]["A"]

    # Slots currently assigned in the James assembly
    assembly_slots = {str(s) for _, s, *_ in _JAMES_SLOT_CHECKS}

    print(f"\n{'=' * 60}")
    print("DIFF: io.in.A rendered vs James.snap (assembly slots only)")
    print(f"{'=' * 60}")
    total_diffs = 0
    for slot in sorted(assembly_slots, key=int):
        r = rend_a[slot]
        t = ref_a[slot]
        diff = DeepDiff(r, t, ignore_numeric_type_changes=True, significant_digits=2)
        n = (
            sum(len(v) if isinstance(v, dict) else 1 for v in diff.values())
            if diff
            else 0
        )
        total_diffs += n
        if diff:
            ref_name = t.get("name", "")
            rend_name = r.get("name", "")
            print(
                f"\n  A[{slot:2s}] rendered={rend_name!r}"
                f" ref={ref_name!r}: {n} difference(s)"
            )
            for change_type, changes in diff.items():
                if isinstance(changes, dict):
                    for path, detail in list(changes.items())[:3]:
                        print(f"    {change_type}: {path} → {detail}")
        else:
            print(f"  A[{slot:2s}] ({r.get('name','')!r}): ✓ identical")

    print(f"\nTotal diff items across {len(assembly_slots)} slots: {total_diffs}")
