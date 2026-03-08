"""Tests for channel and snapshot diffing.

Diff = flatten + near-equality filter + significance filter + translate.
Tests use synthetic channel dicts rather than loading real .snap files,
keeping them fast and self-contained.
"""

import pytest
from snapwright.evolution.diff import diff_channels, diff_snapshots, ChannelDiff


def make_channel(name="Kick", **overrides):
    """Minimal valid Wing channel dict."""
    ch = {
        "name": name,
        "mute": False,
        "fdr": -8.9,
        "flt": {"lc": False, "lcf": 80.0, "lcs": "24", "hc": False, "hcf": 20000.0, "hcs": "12", "tf": False, "tilt": 0.0, "mdl": "TILT"},
        "eq": {"on": True, "mdl": "STD", "mix": 100.0,
               "lg": 0.0, "lf": 80.0, "lq": 0.7, "leq": "PEAK",
               "1g": 0.0, "1f": 200.0, "1q": 1.0,
               "2g": 0.0, "2f": 1000.0, "2q": 1.0,
               "3g": 0.0, "3f": 3000.0, "3q": 1.0,
               "4g": 0.0, "4f": 8000.0, "4q": 1.0,
               "hg": 0.0, "hf": 12000.0, "hq": 0.7, "heq": "PEAK"},
        "dyn": {"on": False, "mdl": "COMP", "mix": 100.0,
                "gain": 0.0, "thr": -20.0, "ratio": 4.0,
                "knee": 0.0, "det": "RMS", "att": 10.0, "hld": 0.0, "rel": 100.0,
                "env": "LIN", "auto": False},
        "gate": {"on": False, "mdl": "GATE", "thr": -40.0, "range": 40.0,
                 "att": 1.0, "hld": 50.0, "rel": 100.0, "acc": 0.5, "ratio": 10.0},
        "send": {
            str(i): {"on": False, "lvl": -144.0, "pon": False, "mode": "POST", "plink": False, "pan": 0}
            for i in range(1, 17)
        },
        "in": {
            "conn": {"grp": "A", "in": 1, "altgrp": "OFF", "altin": 1},
            "set": {"srcauto": False, "altsrc": False, "inv": False, "trim": 0.0,
                    "bal": 0, "dlymode": "M", "dly": 0.1, "dlyon": False},
        },
    }
    # Apply overrides via dot-notation keys like "eq.1g" or flat keys like "fdr"
    for k, v in overrides.items():
        if "." in k:
            parts = k.split(".")
            target = ch
            for part in parts[:-1]:
                target = target[part]
            target[parts[-1]] = v
        else:
            ch[k] = v
    return ch


class TestChannelDiffBasics:
    def test_identical_channels_produce_no_changes(self):
        ch = make_channel()
        result = diff_channels(1, ch, ch)
        assert result.significant_changes == []

    def test_fader_change_above_threshold_detected(self):
        base = make_channel(fdr=-8.9)
        target = make_channel(fdr=0.0)
        result = diff_channels(1, base, target)
        paths = [c.path for c in result.significant_changes]
        assert "fdr" in paths

    def test_fader_change_below_threshold_ignored(self):
        base = make_channel(fdr=-8.9)
        target = make_channel(fdr=-8.0)  # delta = 0.9 dB
        result = diff_channels(1, base, target)
        paths = [c.path for c in result.significant_changes]
        assert "fdr" not in paths

    def test_wing_float_quantization_not_flagged(self):
        # Wing stores -3.33 as -3.330078125
        base = make_channel(fdr=-3.33)
        target = make_channel(fdr=-3.330078125)
        result = diff_channels(1, base, target)
        assert result.significant_changes == []

    def test_eq_model_change_detected(self):
        base = make_channel(**{"eq.mdl": "STD"})
        target = make_channel(**{"eq.mdl": "SOUL"})
        result = diff_channels(1, base, target)
        paths = [c.path for c in result.significant_changes]
        assert "eq.mdl" in paths

    def test_mute_change_detected(self):
        base = make_channel(mute=False)
        target = make_channel(mute=True)
        result = diff_channels(1, base, target)
        paths = [c.path for c in result.significant_changes]
        assert "mute" in paths


class TestChannelDiffSends:
    def test_named_bus_send_change_detected(self):
        base = make_channel()
        base["send"]["6"]["on"] = False
        base["send"]["6"]["lvl"] = -144.0
        target = make_channel()
        target["send"]["6"]["on"] = True
        target["send"]["6"]["lvl"] = -12.0
        result = diff_channels(1, base, target)
        paths = [c.path for c in result.significant_changes]
        assert "send.6.on" in paths

    def test_unnamed_bus_send_excluded(self):
        # Bus 7 is unnamed — changes to it should not appear
        base = make_channel()
        target = make_channel()
        target["send"]["7"]["on"] = True
        target["send"]["7"]["lvl"] = -10.0
        result = diff_channels(1, base, target)
        paths = [c.path for c in result.significant_changes]
        assert not any("send.7" in p for p in paths)


class TestSnapshotDiffChannelFiltering:
    def _make_snap(self, channels: dict) -> dict:
        """Minimal snap structure."""
        return {"ae_data": {"ch": channels}}

    def test_unnamed_channels_excluded(self):
        base_snap = self._make_snap({"1": make_channel(name="Kick"), "2": make_channel(name="")})
        target_snap = self._make_snap({"1": make_channel(name="Kick", fdr=0.0), "2": make_channel(name="", fdr=0.0)})
        result = diff_snapshots(base_snap, target_snap, name="test", date=None)
        channel_nums = [cd.number for cd in result.significant_channel_diffs]
        assert 2 not in channel_nums

    def test_same_named_channels_kept_separate(self):
        # ch13 and ch25 both named "James" — must not collide in pattern detection
        base_snap = self._make_snap({
            "13": make_channel(name="James", fdr=-5.3),
            "25": make_channel(name="James", fdr=-10.0),
        })
        target_snap = self._make_snap({
            "13": make_channel(name="James", fdr=1.3),   # +6.6 dB
            "25": make_channel(name="James", fdr=-10.0), # unchanged
        })
        result = diff_snapshots(base_snap, target_snap, name="test", date=None)
        changed_nums = [cd.number for cd in result.significant_channel_diffs]
        assert 13 in changed_nums
        assert 25 not in changed_nums
