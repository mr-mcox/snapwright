"""Phase 0 round-trip test: render ch1 from minimal DSL, diff against James.snap.

At this stage the DSL only covers identity, fader, and sends — so we expect
a large diff on EQ/dynamics/gate/input-filters. That's intentional: the diff
output is the work list for step 8 (expand to full channel).

The test asserts that the params we DO express in the DSL match exactly.
The full diff is printed to stdout so we can review it and agree tolerances.
"""

from pathlib import Path
from deepdiff import DeepDiff

from snapwright.wing.parser import load_snap, get_channel
from snapwright.steel_thread.dsl import load_channel_config
from snapwright.steel_thread.renderer import render_channel

JAMES = Path("data/reference/sunday-starters/James.snap")
KICK_DSL = Path("data/dsl/channels/kick.yaml")


def _james_ch1() -> dict:
    return get_channel(load_snap(JAMES), 1)


def _rendered_ch1() -> dict:
    config = load_channel_config(KICK_DSL)
    return render_channel(config)


def test_identity_matches():
    rendered = _rendered_ch1()
    target = _james_ch1()
    assert rendered["name"] == target["name"]
    assert rendered["col"] == target["col"]
    assert rendered["icon"] == target["icon"]
    assert rendered["mute"] == target["mute"]


def test_fader_matches():
    rendered = _rendered_ch1()
    target = _james_ch1()
    # Fader: DSL value is -3.33, Wing stores -3.330078125 — allow small float delta
    assert abs(rendered["fdr"] - target["fdr"]) < 0.01


def test_input_routing_matches():
    rendered = _rendered_ch1()
    target = _james_ch1()
    assert rendered["in"]["conn"]["grp"] == target["in"]["conn"]["grp"]
    assert rendered["in"]["conn"]["in"] == target["in"]["conn"]["in"]


def test_active_sends_match():
    rendered = _rendered_ch1()
    target = _james_ch1()
    # bus1 is active in DSL
    assert rendered["send"]["1"]["on"] == target["send"]["1"]["on"]
    assert abs(rendered["send"]["1"]["lvl"] - target["send"]["1"]["lvl"]) < 0.01
    assert rendered["send"]["1"]["mode"] == target["send"]["1"]["mode"]


def test_inactive_sends_are_off():
    rendered = _rendered_ch1()
    for key in ["2", "3", "4", "5", "6", "7", "9", "10", "11", "12"]:
        assert rendered["send"][key]["on"] is False, f"send {key} should be off"


def test_print_full_diff():
    """Not a pass/fail assertion — prints the diff so we can review the gap.

    Run with: pytest tests/test_round_trip.py::test_print_full_diff -s
    """
    rendered = _rendered_ch1()
    target = _james_ch1()
    diff = DeepDiff(rendered, target, ignore_numeric_type_changes=True)
    if diff:
        print(f"\n{'='*60}")
        print("DIFF: rendered ch1 vs James.snap ch1")
        print(f"{'='*60}")
        for change_type, changes in diff.items():
            print(f"\n--- {change_type} ({len(changes)} items) ---")
            if isinstance(changes, dict):
                for path, detail in changes.items():
                    print(f"  {path}: {detail}")
            else:
                for item in changes:
                    print(f"  {item}")
    else:
        print("\nNo diff — perfect round-trip!")
