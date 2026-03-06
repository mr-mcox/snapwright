"""Tests for Wing .snap parser and writer."""

import json
import tempfile
from pathlib import Path

import pytest

from snapwright.wing.parser import load_snap, get_channel
from snapwright.wing.writer import save_snap, set_channel

JAMES = Path("data/reference/sunday-starters/James.snap")
BASE = Path("data/reference/Base.snap")


def test_load_james():
    snap = load_snap(JAMES)
    assert snap["creator_model"] == "wing"
    assert "ae_data" in snap


def test_load_base():
    snap = load_snap(BASE)
    # Base.snap is a BCF file, reports ngc-full not wing
    assert snap["creator_model"] == "ngc-full"


def test_get_channel():
    snap = load_snap(JAMES)
    ch1 = get_channel(snap, 1)
    assert ch1["name"] == "Kick"
    assert "eq" in ch1
    assert "send" in ch1


def test_channel_count():
    snap = load_snap(JAMES)
    assert len(snap["ae_data"]["ch"]) == 40


def test_round_trip_file():
    """Load, save, reload — data must be identical."""
    snap = load_snap(JAMES)
    with tempfile.NamedTemporaryFile(suffix=".snap", delete=False) as f:
        tmp = Path(f.name)
    try:
        save_snap(snap, tmp)
        reloaded = load_snap(tmp)
        assert reloaded == snap
    finally:
        tmp.unlink()


def test_set_channel_mutates_in_place():
    snap = load_snap(JAMES)
    ch = get_channel(snap, 1)
    ch["name"] = "TestKick"
    set_channel(snap, 1, ch)
    assert get_channel(snap, 1)["name"] == "TestKick"
