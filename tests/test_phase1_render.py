"""Phase 1 round-trip test: render James team from DSL, diff against James.snap.

Validates:
- Loader resolves inheritance stacks correctly
- Renderer produces valid Wing JSON for all DSL-specified channels
- Identity, processing, and sends match the reference within tolerance
"""

from pathlib import Path

import pytest
from deepdiff import DeepDiff

from snapwright.dsl.renderer import render_assembly
from snapwright.wing.parser import load_snap, get_channel

ASSEMBLY = Path("data/dsl/teams/james/assembly.yaml")
REFERENCE = Path("data/reference/sunday-starters/James.snap")

# Channels we fully specify in the DSL (others keep Base.snap defaults)
DSL_CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 16, 25, 26, 27, 28, 37, 38]

# Relative tolerance for numeric comparisons (3 significant figures)
REL_TOL = 0.001


def _render():
    return render_assembly(ASSEMBLY)


def _ref():
    return load_snap(REFERENCE)


@pytest.fixture(scope="module")
def rendered():
    return _render()


@pytest.fixture(scope="module")
def reference():
    return _ref()


# ---------------------------------------------------------------------------
# Smoke test — just check it renders without error
# ---------------------------------------------------------------------------

def test_render_completes(rendered):
    assert "ae_data" in rendered
    assert "ch" in rendered["ae_data"]
    assert len(rendered["ae_data"]["ch"]) == 40


# ---------------------------------------------------------------------------
# Identity checks
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ch_num,expected_name", [
    (1,  "Kick"),
    (2,  "Snare"),
    (3,  "Tom"),
    (5,  "Bass"),
    (13, "James"),
    (25, "James"),
    (26, "Pricilla"),
    (27, "Anna"),
    (28, "Yolaine"),
    (37, "Handheld"),
    (38, "Headset"),
])
def test_channel_name(rendered, ch_num, expected_name):
    ch = rendered["ae_data"]["ch"][str(ch_num)]
    assert ch["name"] == expected_name


@pytest.mark.parametrize("ch_num", DSL_CHANNELS)
def test_fader_within_tolerance(rendered, reference, ch_num):
    r = rendered["ae_data"]["ch"][str(ch_num)]["fdr"]
    t = reference["ae_data"]["ch"][str(ch_num)]["fdr"]
    assert abs(r - t) < 0.05, f"ch{ch_num} fader: rendered={r:.3f} target={t:.3f}"


# ---------------------------------------------------------------------------
# Input routing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ch_num,expected_grp,expected_in", [
    (1,  "A", 2),
    (2,  "A", 3),
    (13, "A", 14),
    (25, "A", 10),
    (26, "A", 11),
    (37, "A", 32),
])
def test_input_routing(rendered, reference, ch_num, expected_grp, expected_in):
    conn = rendered["ae_data"]["ch"][str(ch_num)]["in"]["conn"]
    assert conn["grp"] == expected_grp, f"ch{ch_num} grp"
    assert conn["in"]  == expected_in,  f"ch{ch_num} in"


# ---------------------------------------------------------------------------
# EQ model checks
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ch_num,expected_model", [
    (1,  "STD"),
    (2,  "STD"),
    (6,  "E88"),
    (13, "PULSAR"),
    (14, "SOUL"),
    (25, "SOUL"),
    (26, "SOUL"),
])
def test_eq_model(rendered, ch_num, expected_model):
    eq = rendered["ae_data"]["ch"][str(ch_num)]["eq"]
    assert eq["mdl"] == expected_model, f"ch{ch_num} EQ model"


# ---------------------------------------------------------------------------
# Dynamics model checks
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ch_num,expected_model", [
    (1,  "ECL33"),
    (2,  "ECL33"),
    (5,  "LA"),
    (6,  "9000C"),
    (13, "NSTR"),
    (25, "LA"),
])
def test_dynamics_model(rendered, ch_num, expected_model):
    dyn = rendered["ae_data"]["ch"][str(ch_num)]["dyn"]
    assert dyn["mdl"] == expected_model, f"ch{ch_num} dynamics model"


# ---------------------------------------------------------------------------
# Gate model checks
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ch_num,expected_model", [
    (1,  "GATE"),
    (2,  "GATE"),
    (6,  "9000G"),
    (14, "PSE"),
    (25, "PSE"),
    (37, "RIDE"),
    (38, "RIDE"),
])
def test_gate_model(rendered, ch_num, expected_model):
    gate = rendered["ae_data"]["ch"][str(ch_num)]["gate"]
    assert gate["mdl"] == expected_model, f"ch{ch_num} gate model"


# ---------------------------------------------------------------------------
# Active send checks
# ---------------------------------------------------------------------------

def _send_on(snap, ch_num, bus_key):
    return snap["ae_data"]["ch"][str(ch_num)]["send"][bus_key]


def test_kick_sends_drums(rendered, reference):
    r = _send_on(rendered, 1, "1")
    t = _send_on(reference, 1, "1")
    assert r["on"] is True
    assert abs(r["lvl"] - t["lvl"]) < 0.05


def test_james_guitar_rhythm_house(rendered, reference):
    r = _send_on(rendered, 13, "2")
    t = _send_on(reference, 13, "2")
    assert r["on"] is True
    assert abs(r["lvl"] - t["lvl"]) < 0.05


def test_james_vox_vocals_sub(rendered, reference):
    r = _send_on(rendered, 25, "6")
    t = _send_on(reference, 25, "6")
    assert r["on"] is True
    assert abs(r["lvl"] - t["lvl"]) < 0.05


def test_james_vox_monitor_1(rendered, reference):
    r = _send_on(rendered, 25, "13")
    t = _send_on(reference, 25, "13")
    assert r["on"] is True
    assert abs(r["lvl"] - t["lvl"]) < 0.05


# ---------------------------------------------------------------------------
# Full diff printout (not a pass/fail — review to assess overall quality)
# ---------------------------------------------------------------------------

def test_print_full_diff_active_channels(rendered, reference):
    """Print a summary diff for all DSL-specified channels.

    Run with: uv run pytest tests/test_phase1_render.py::test_print_full_diff_active_channels -s
    """
    print(f"\n{'='*70}")
    print("DIFF: rendered James team vs James.snap (DSL channels only)")
    print(f"{'='*70}")

    total_params = 0
    total_diffs = 0

    for ch_num in DSL_CHANNELS:
        r = rendered["ae_data"]["ch"][str(ch_num)]
        t = reference["ae_data"]["ch"][str(ch_num)]
        name = t.get("name", f"ch{ch_num}")
        diff = DeepDiff(r, t, ignore_numeric_type_changes=True, significant_digits=2)
        n_params = sum(len(v) if isinstance(v, dict) else 1 for v in diff.values()) if diff else 0
        total_params += 1
        total_diffs += n_params
        if diff:
            print(f"\n  ch{ch_num} ({name}): {n_params} difference(s)")
            for change_type, changes in diff.items():
                if isinstance(changes, dict):
                    for path, detail in list(changes.items())[:5]:
                        print(f"    {change_type}: {path} → {detail}")
                else:
                    for item in list(changes)[:5]:
                        print(f"    {change_type}: {item}")
        else:
            print(f"  ch{ch_num} ({name}): ✓ identical (2 sig fig)")

    print(f"\nTotal diff items across {len(DSL_CHANNELS)} channels: {total_diffs}")
