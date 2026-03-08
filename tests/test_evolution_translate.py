"""Tests for Wing parameter path → audio label translation.

Translation is pure: given a path, old value, new value, and model context,
produce a human-readable label and formatted values. No Wing snapshot loading.
"""

import pytest
from snapwright.evolution.translate import translate, ParamLabel


def ctx(eq="STD", dyn="COMP", gate="GATE"):
    return {"eq_model": eq, "dyn_model": dyn, "gate_model": gate}


class TestFader:
    def test_label(self):
        result = translate("fdr", -8.9, 0.0, ctx())
        assert result.section == "Fader"
        assert result.label == "level"

    def test_dB_formatting(self):
        result = translate("fdr", -8.9, 0.0, ctx())
        assert result.old_fmt == "-8.9 dB"
        assert result.new_fmt == "+0.0 dB"

    def test_delta(self):
        result = translate("fdr", -8.9, 0.0, ctx())
        assert abs(result.delta - 8.9) < 0.01


class TestMute:
    def test_label_and_format(self):
        result = translate("mute", False, True, ctx())
        assert result.section == "Mute"
        assert result.old_fmt == "off"
        assert result.new_fmt == "on"
        assert result.delta is None


class TestFilters:
    def test_hpf_on(self):
        result = translate("flt.lc", False, True, ctx())
        assert result.section == "Filter"
        assert result.label == "HPF on"

    def test_hpf_freq_formatted_as_hz(self):
        result = translate("flt.lcf", 199.0, 108.0, ctx())
        assert result.label == "HPF freq"
        assert result.old_fmt == "199 Hz"
        assert result.new_fmt == "108 Hz"

    def test_large_freq_formatted_with_comma(self):
        result = translate("flt.hcf", 1206.0, 224.0, ctx())
        assert result.old_fmt == "1,206 Hz"
        assert result.new_fmt == "224 Hz"

    def test_lpf_freq(self):
        result = translate("flt.hcf", 1206.0, 224.0, ctx())
        assert result.label == "LPF freq"


class TestEqSTD:
    def test_band_gain(self):
        result = translate("eq.1g", 3.2, 0.1, ctx(eq="STD"))
        assert "band 1" in result.label
        assert "gain" in result.label
        assert result.old_fmt == "+3.2 dB"

    def test_band_freq(self):
        result = translate("eq.2f", 500.0, 400.0, ctx(eq="STD"))
        assert "band 2" in result.label
        assert "freq" in result.label
        assert result.old_fmt == "500 Hz"

    def test_low_shelf_gain(self):
        result = translate("eq.lg", 0.0, -2.0, ctx(eq="STD"))
        assert "low shelf" in result.label
        assert "gain" in result.label

    def test_high_shelf_freq_no_section_doubling(self):
        # Regression: "eq" is a substring of "freq" — section must not be stripped
        result = translate("eq.hf", 7251.0, 10096.0, ctx(eq="STD"))
        assert "high shelf" in result.label
        assert result.section == "EQ (STD)"

    def test_model_change(self):
        result = translate("eq.mdl", "STD", "SOUL", ctx())
        assert result.section == "EQ"
        assert result.label == "model"
        assert result.old_fmt == "STD"
        assert result.new_fmt == "SOUL"


class TestEqSOUL:
    def test_lo_mid_band(self):
        result = translate("eq.lmg", 0.0, 3.0, ctx(eq="SOUL"))
        assert "lo-mid" in result.label
        assert "gain" in result.label

    def test_hi_mid_freq(self):
        result = translate("eq.hmf", 2000.0, 1500.0, ctx(eq="SOUL"))
        assert "hi-mid" in result.label
        assert "freq" in result.label


class TestDynamics:
    def test_comp_threshold(self):
        result = translate("dyn.thr", -20.0, -24.0, ctx(dyn="COMP"))
        assert "threshold" in result.label
        assert result.old_fmt == "-20.0 dB"

    def test_ecl33_comp_threshold(self):
        result = translate("dyn.cthr", -17.0, -24.0, ctx(dyn="ECL33"))
        assert "comp threshold" in result.label

    def test_ecl33_leveler_threshold(self):
        result = translate("dyn.lthr", -30.0, -20.0, ctx(dyn="ECL33"))
        assert "leveler threshold" in result.label

    def test_la_gain(self):
        result = translate("dyn.ingain", 40.0, 56.0, ctx(dyn="LA"))
        assert result.label == "gain"

    def test_la_peak_reduction(self):
        result = translate("dyn.peak", 20.0, 54.0, ctx(dyn="LA"))
        assert result.label == "peak reduction"

    def test_model_label(self):
        result = translate("dyn.mdl", "COMP", "ECL33", ctx())
        assert result.label == "model"
        assert result.section == "Dynamics"


class TestGate:
    def test_threshold(self):
        result = translate("gate.thr", -24.0, -32.5, ctx(gate="GATE"))
        assert "threshold" in result.label
        assert result.old_fmt == "-24.0 dB"

    def test_pse_depth(self):
        result = translate("gate.depth", 5.0, 10.0, ctx(gate="PSE"))
        assert result.label == "depth"
        assert result.section == "Gate (PSE)"

    def test_ride_target(self):
        result = translate("gate.tgt", -28.0, -17.0, ctx(gate="RIDE"))
        assert result.label == "target"

    def test_model_label(self):
        result = translate("gate.mdl", "GATE", "PSE", ctx())
        assert result.label == "model"
        assert result.section == "Gate"


class TestSends:
    def test_named_bus(self):
        result = translate("send.6.lvl", -144.0, -12.0, ctx())
        assert "Vocals sub" in result.section
        assert result.label == "level"

    def test_send_off_sentinel_suppresses_delta(self):
        # -144 → real value: delta suppressed (the swing is meaningless)
        result = translate("send.6.lvl", -144.0, -12.0, ctx())
        assert result.delta is None

    def test_send_to_sentinel_suppresses_delta(self):
        result = translate("send.6.lvl", -12.0, -144.0, ctx())
        assert result.delta is None

    def test_normal_send_level_has_delta(self):
        result = translate("send.6.lvl", -12.0, -8.0, ctx())
        assert result.delta is not None
        assert abs(result.delta - 4.0) < 0.01

    def test_send_on_off(self):
        result = translate("send.1.on", False, True, ctx())
        assert result.label == "on"
        assert result.delta is None
