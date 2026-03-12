"""Tests for personal mixer (P16) DSL — infrastructure topology + assembly rendering.

Infrastructure responsibilities:
  - Parse slot topology from infrastructure.yaml (dict keyed by slot number)
  - Write matrix names + faders for group slots
  - Write USR source label defaults for individual slots
  - Write io.out A.33-A.48 routing for all 16 slots

Assembly responsibilities:
  - Flat dict: slot-label -> [musician, ...]
  - Write MX channel sends for group slots (all at 0 dB)
  - Write USR source channel assignments for individual slots
  - Tap points come from infrastructure slot definition, not assembly
  - Individual slots with > 1 musician raise ValueError
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from snapwright.dsl.infrastructure import get_p16_slots
from snapwright.dsl.renderer import render_assembly
from snapwright.wing.defaults import snap_template

ASSEMBLY = Path("data/dsl/teams/james/assembly.yaml")
_INFRA = yaml.safe_load(Path("data/dsl/infrastructure.yaml").read_text())


# ---------------------------------------------------------------------------
# Slot topology helper — pure parsing
# ---------------------------------------------------------------------------


class TestGetP16Slots:
    """get_p16_slots() parses the infrastructure dict into a 16-slot list."""

    def test_returns_16_slots(self):
        assert len(get_p16_slots(_INFRA)) == 16

    def test_slot_numbers_are_1_indexed(self):
        slots = get_p16_slots(_INFRA)
        assert slots[0]["slot_num"] == 1
        assert slots[15]["slot_num"] == 16

    def test_a_out_matches_slot_number(self):
        slots = get_p16_slots(_INFRA)
        assert slots[0]["a_out"] == "33"
        assert slots[15]["a_out"] == "48"

    def test_absent_slots_are_off(self):
        """Slot numbers not declared in infrastructure become OFF."""
        slots = get_p16_slots(_INFRA)
        off_slot_nums = {4, 8, 13, 14}  # gaps in the declaration
        for s in slots:
            if s["slot_num"] in off_slot_nums:
                assert s["type"] == "off", (
                    f"slot {s['slot_num']} should be off (not declared)"
                )
                assert s["mx_num"] is None
                assert s["usr_num"] is None

    def test_group_slots_get_sequential_mx_numbers(self):
        """MX numbers assigned in ascending slot order."""
        slots = get_p16_slots(_INFRA)
        groups = [s for s in slots if s["type"] == "group"]
        assert [s["mx_num"] for s in groups] == list(range(1, len(groups) + 1))

    def test_individual_slots_get_sequential_usr_numbers(self):
        slots = get_p16_slots(_INFRA)
        individuals = [s for s in slots if s["type"] == "individual"]
        expected = list(range(1, len(individuals) + 1))
        assert [s["usr_num"] for s in individuals] == expected

    def test_drum_set_is_first_group_mx1(self):
        slots = get_p16_slots(_INFRA)
        groups = [s for s in slots if s["type"] == "group"]
        assert groups[0]["label"] == "Drum Set"
        assert groups[0]["mx_num"] == 1

    def test_bass_is_first_individual_usr1(self):
        slots = get_p16_slots(_INFRA)
        individuals = [s for s in slots if s["type"] == "individual"]
        assert individuals[0]["label"] == "Bass"
        assert individuals[0]["usr_num"] == 1

    def test_tap_points_from_infrastructure(self):
        """Tap points are defined on the infrastructure slot, not in assembly."""
        slots = get_p16_slots(_INFRA)
        by_label = {s["label"]: s for s in slots if s["label"]}
        assert by_label["Bass"]["tap"] == "PRE"
        assert by_label["Lead 1"]["tap"] == "POST"
        assert by_label["Lead 2"]["tap"] == "POST"
        assert by_label["Piano"]["tap"] == "PRE"
        assert by_label["Keys"]["tap"] == "PRE"

    def test_monitor_slot_has_bus(self):
        slots = get_p16_slots(_INFRA)
        monitors = [s for s in slots if s["type"] == "monitor"]
        assert len(monitors) == 1
        assert monitors[0]["bus"] == "monitor_4"
        assert monitors[0]["slot_num"] == 16

    def test_off_and_monitor_slots_have_no_mx_or_usr(self):
        slots = get_p16_slots(_INFRA)
        for s in slots:
            if s["type"] in ("off", "monitor"):
                assert s["mx_num"] is None
                assert s["usr_num"] is None


# ---------------------------------------------------------------------------
# Infrastructure rendering — snap_template() output
# ---------------------------------------------------------------------------


class TestPersonalMixerInfrastructure:
    """snap_template() must configure matrices, USR labels, and io.out A.33-A.48."""

    @pytest.fixture(scope="class")
    def snap(self):
        return snap_template()

    def test_group_matrix_names_set(self, snap):
        """Each group slot label written to ae_data.mtx.{n}.name."""
        slots = get_p16_slots(_INFRA)
        mtx = snap["ae_data"]["mtx"]
        for s in slots:
            if s["type"] == "group":
                assert mtx[str(s["mx_num"])]["name"] == s["label"]

    def test_group_matrix_faders_at_zero(self, snap):
        slots = get_p16_slots(_INFRA)
        mtx = snap["ae_data"]["mtx"]
        for s in slots:
            if s["type"] == "group":
                assert abs(mtx[str(s["mx_num"])]["fdr"]) < 0.01

    def test_individual_usr_labels_set(self, snap):
        slots = get_p16_slots(_INFRA)
        usr = snap["ae_data"]["io"]["in"]["USR"]
        for s in slots:
            if s["type"] == "individual":
                assert usr[str(s["usr_num"])]["name"] == s["label"]

    def test_individual_usr_sources_off_by_default(self, snap):
        slots = get_p16_slots(_INFRA)
        usr = snap["ae_data"]["io"]["in"]["USR"]
        for s in slots:
            if s["type"] == "individual":
                assert usr[str(s["usr_num"])]["user"]["grp"] == "OFF"

    def test_io_out_group_slots_route_to_mtx(self, snap):
        """Group A.xx routes to MTX with in=(mx_num*2)-1."""
        slots = get_p16_slots(_INFRA)
        io_out_a = snap["ae_data"]["io"]["out"]["A"]
        for s in slots:
            if s["type"] == "group":
                entry = io_out_a[s["a_out"]]
                assert entry == {"grp": "MTX", "in": (s["mx_num"] * 2) - 1}

    def test_io_out_individual_slots_route_to_usr(self, snap):
        slots = get_p16_slots(_INFRA)
        io_out_a = snap["ae_data"]["io"]["out"]["A"]
        for s in slots:
            if s["type"] == "individual":
                assert io_out_a[s["a_out"]] == {"grp": "USR", "in": s["usr_num"]}

    def test_io_out_monitor_slot_routes_to_bus16(self, snap):
        """monitor_4 = bus 16, in = 16*2-1 = 31."""
        slots = get_p16_slots(_INFRA)
        io_out_a = snap["ae_data"]["io"]["out"]["A"]
        for s in slots:
            if s["type"] == "monitor":
                assert io_out_a[s["a_out"]] == {"grp": "BUS", "in": 31}

    def test_io_out_off_slots_are_off(self, snap):
        slots = get_p16_slots(_INFRA)
        io_out_a = snap["ae_data"]["io"]["out"]["A"]
        for s in slots:
            if s["type"] == "off":
                assert io_out_a[s["a_out"]] == {"grp": "OFF", "in": 1}


# ---------------------------------------------------------------------------
# Assembly rendering — render_assembly() output
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def rendered():
    return render_assembly(ASSEMBLY)


class TestPersonalMixerMXSends:
    """Channels in a group send to the right MX bus at 0 dB."""

    def test_kick_in_drum_set_mx1(self, rendered):
        send = rendered["ae_data"]["ch"]["1"]["send"]["MX1"]
        assert send["on"] is True
        assert send["mode"] == "PRE"
        assert send["plink"] is True
        assert abs(send["lvl"]) < 0.01

    def test_snare_in_drum_set_mx1(self, rendered):
        assert rendered["ae_data"]["ch"]["2"]["send"]["MX1"]["on"] is True

    def test_tom_in_drum_set_mx1(self, rendered):
        assert rendered["ae_data"]["ch"]["3"]["send"]["MX1"]["on"] is True

    def test_overhead_in_drum_set_mx1(self, rendered):
        assert rendered["ae_data"]["ch"]["4"]["send"]["MX1"]["on"] is True

    def test_back_vox_is_mx3(self, rendered):
        """Back Vox is the 3rd group slot (slot 7) → MX3."""
        ch27 = rendered["ae_data"]["ch"]["27"]  # anna-vox
        assert ch27["send"]["MX3"]["on"] is True
        assert ch27["send"]["MX3"]["mode"] == "PRE"

    def test_yolaine_in_back_vox_mx3(self, rendered):
        assert rendered["ae_data"]["ch"]["28"]["send"]["MX3"]["on"] is True

    def test_guitars_is_mx4(self, rendered):
        """Guitars is the 4th group slot (slot 11) → MX4."""
        ch = rendered["ae_data"]["ch"]
        assert ch["13"]["send"]["MX4"]["on"] is True  # james-guitar
        assert ch["16"]["send"]["MX4"]["on"] is True  # violin

    def test_other_inst_is_mx5(self, rendered):
        """Other Inst is the 5th group slot (slot 12) → MX5."""
        assert rendered["ae_data"]["ch"]["14"]["send"]["MX5"]["on"] is True  # flute

    def test_wireless_is_mx6(self, rendered):
        """Wireless is the 6th group slot (slot 15) → MX6."""
        assert rendered["ae_data"]["ch"]["37"]["send"]["MX6"]["on"] is True  # handheld
        assert rendered["ae_data"]["ch"]["38"]["send"]["MX6"]["on"] is True  # headset

    def test_congas_mx2_empty(self, rendered):
        """MX2 (Congas, slot 3) — omitted from assembly, all sends off."""
        for ch_num in ["6", "7", "8"]:
            assert rendered["ae_data"]["ch"][ch_num]["send"]["MX2"]["on"] is False

    def test_james_vox_has_no_group_sends(self, rendered):
        """james-vox is individual (Lead 2), not in any group."""
        ch25 = rendered["ae_data"]["ch"]["25"]
        for mx_key in ["MX1", "MX2", "MX3", "MX4", "MX5", "MX6"]:
            assert ch25["send"][mx_key]["on"] is False


class TestPersonalMixerUSRSources:
    """USR sources correctly assigned; tap points from infrastructure."""

    def test_bass_usr1_ch5_pre(self, rendered):
        usr = rendered["ae_data"]["io"]["in"]["USR"]["1"]
        assert usr["user"] == {"grp": "CH", "in": 5, "tap": "PRE", "lr": "L+R"}

    def test_lead1_usr2_priscilla_post(self, rendered):
        """Lead 1 → priscilla-vox (ch26), tap POST from infrastructure."""
        usr = rendered["ae_data"]["io"]["in"]["USR"]["2"]
        assert usr["user"]["in"] == 26
        assert usr["user"]["tap"] == "POST"

    def test_lead2_usr3_james_vox_post(self, rendered):
        """Lead 2 → james-vox (ch25), tap POST from infrastructure."""
        usr = rendered["ae_data"]["io"]["in"]["USR"]["3"]
        assert usr["user"]["in"] == 25
        assert usr["user"]["tap"] == "POST"

    def test_piano_usr4_ch15_pre(self, rendered):
        usr = rendered["ae_data"]["io"]["in"]["USR"]["4"]
        assert usr["user"]["in"] == 15
        assert usr["user"]["tap"] == "PRE"

    def test_keys_usr5_off(self, rendered):
        """Keys omitted from assembly → USR.5 stays OFF."""
        assert rendered["ae_data"]["io"]["in"]["USR"]["5"]["user"]["grp"] == "OFF"

    def test_usr_labels_preserved(self, rendered):
        """Infrastructure-written labels survive assembly rendering."""
        usr = rendered["ae_data"]["io"]["in"]["USR"]
        assert usr["1"]["name"] == "Bass"
        assert usr["2"]["name"] == "Lead 1"
        assert usr["3"]["name"] == "Lead 2"
        assert usr["4"]["name"] == "Piano"
        assert usr["5"]["name"] == "Keys"

    def test_usr_lr_field(self, rendered):
        usr = rendered["ae_data"]["io"]["in"]["USR"]
        for k in ["1", "2", "3", "4"]:
            assert usr[k]["user"]["lr"] == "L+R"


class TestPersonalMixerValidation:
    """Renderer enforces individual slot constraints."""

    def test_individual_slot_with_two_musicians_raises(self):
        """Passing two musicians to an individual slot is an error."""
        from snapwright.dsl.loader import load_assembly
        from snapwright.dsl.renderer import _render

        assembly, dsl_root = load_assembly(ASSEMBLY)
        # Inject an invalid assignment for an individual slot
        assembly = assembly.model_copy(
            update={"personal_mixer": {"Bass": ["bass", "violin"]}}
        )
        with pytest.raises(ValueError, match="individual slots take exactly 0 or 1"):
            _render(assembly, dsl_root)
