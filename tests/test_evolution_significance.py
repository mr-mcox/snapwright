"""Tests for evolution significance thresholds.

Significance is a first-class policy: given a Wing param path and a numeric delta,
is this change worth surfacing? Tests encode the policy explicitly so it can be
read as documentation and changed with confidence.
"""

import pytest
from snapwright.evolution.significance import is_significant, THRESHOLDS


class TestFaderSignificance:
    def test_exactly_at_threshold_is_significant(self):
        assert is_significant("fdr", -8.9, -6.9) is True  # delta = 2.0

    def test_below_threshold_is_not(self):
        assert is_significant("fdr", -8.9, -7.5) is False  # delta = 1.4

    def test_direction_does_not_matter(self):
        assert is_significant("fdr", 0.0, -2.5) is True
        assert is_significant("fdr", 0.0, +2.5) is True


class TestSendLevelSignificance:
    def test_meaningful_level_change_is_significant(self):
        assert is_significant("send.1.lvl", -10.0, -5.0) is True  # delta = 5.0

    def test_small_level_change_is_not(self):
        assert is_significant("send.1.lvl", -10.0, -9.0) is False  # delta = 1.0

    def test_transition_from_off_sentinel_is_significant(self):
        # -144 is Wing's "off" state — turning a send on is always significant
        assert is_significant("send.6.lvl", -144.0, -12.0) is True

    def test_transition_to_off_sentinel_is_significant(self):
        assert is_significant("send.6.lvl", -12.0, -144.0) is True


class TestEqGainSignificance:
    def test_at_threshold(self):
        assert is_significant("eq.1g", 3.2, 1.7) is True   # delta = 1.5

    def test_below_threshold(self):
        assert is_significant("eq.1g", 3.2, 2.0) is False  # delta = 1.2

    def test_shelf_gain(self):
        assert is_significant("eq.lg", 0.0, -2.0) is True
        assert is_significant("eq.hg", 0.0, 1.0) is False  # delta = 1.0 < 1.5


class TestFrequencySignificance:
    def test_large_relative_shift_is_significant(self):
        # 199 Hz → 108 Hz: ~46% shift, well above 10%
        assert is_significant("flt.lcf", 199.0, 108.0) is True

    def test_small_relative_shift_is_not(self):
        # 1000 Hz → 1050 Hz: 5% shift
        assert is_significant("flt.lcf", 1000.0, 1050.0) is False

    def test_exactly_at_10_percent(self):
        assert is_significant("flt.lcf", 100.0, 110.0) is True

    def test_eq_frequency(self):
        assert is_significant("eq.1f", 500.0, 400.0) is True   # 20% shift
        assert is_significant("eq.1f", 500.0, 495.0) is False  # 1% shift


class TestBooleanSignificance:
    def test_on_off_always_significant(self):
        assert is_significant("gate.on", True, False) is True
        assert is_significant("eq.on", False, True) is True
        assert is_significant("mute", False, True) is True

    def test_no_change_not_significant(self):
        assert is_significant("gate.on", True, True) is False


class TestModelChangeSignificance:
    def test_model_change_always_significant(self):
        assert is_significant("eq.mdl", "STD", "SOUL") is True
        assert is_significant("dyn.mdl", "COMP", "ECL33") is True
        assert is_significant("gate.mdl", "GATE", "PSE") is True

    def test_same_model_not_significant(self):
        assert is_significant("eq.mdl", "STD", "STD") is False


class TestDynamicsSignificance:
    def test_threshold_at_2db(self):
        assert is_significant("dyn.thr", -20.0, -22.5) is True
        assert is_significant("dyn.thr", -20.0, -21.5) is False

    def test_ecl33_comp_threshold(self):
        assert is_significant("dyn.cthr", -17.0, -24.0) is True

    def test_ratio_at_0_5(self):
        assert is_significant("dyn.ratio", 3.0, 4.0) is True   # delta = 1.0
        assert is_significant("dyn.ratio", 3.0, 3.3) is False  # delta = 0.3


class TestGateSignificance:
    def test_threshold(self):
        assert is_significant("gate.thr", -24.0, -32.5) is True
        assert is_significant("gate.thr", -24.0, -25.5) is False

    def test_range_at_3db(self):
        assert is_significant("gate.range", 40.0, 43.5) is True
        assert is_significant("gate.range", 40.0, 42.0) is False
