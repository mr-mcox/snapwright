"""Tests for personal mixer (P16) DSL — infrastructure topology + assembly rendering.

Infrastructure responsibilities:
  - Parse slot topology from infrastructure.yaml
  - Write matrix names + faders for group slots
  - Write USR source label defaults for individual slots
  - Write io.out A.33-A.48 routing for all 16 slots

Assembly responsibilities:
  - Write MX channel sends for group slots (musician membership + level)
  - Write USR source channel assignments for individual slots (tap point)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from snapwright.dsl.infrastructure import get_p16_slots
from snapwright.dsl.renderer import render_assembly
from snapwright.wing.defaults import snap_template

ASSEMBLY = Path("data/dsl/teams/james/assembly.yaml")

# ---------------------------------------------------------------------------
# Slot topology helper — pure parsing
# ---------------------------------------------------------------------------


class TestGetP16Slots:
    """get_p16_slots() parses the infrastructure YAML into a numbered slot list."""

    def _slots(self):
        import yaml
        infra = yaml.safe_load(
            Path("data/dsl/infrastructure.yaml").read_text()
        )
        return get_p16_slots(infra)

    def test_returns_16_slots(self):
        slots = self._slots()
        assert len(slots) == 16

    def test_slot_numbers_are_1_indexed(self):
        slots = self._slots()
        assert slots[0]["slot_num"] == 1
        assert slots[15]["slot_num"] == 16

    def test_a_out_matches_slot_number(self):
        """A.33 = slot 1, A.48 = slot 16."""
        slots = self._slots()
        assert slots[0]["a_out"] == "33"
        assert slots[15]["a_out"] == "48"

    def test_group_slots_get_sequential_mx_numbers(self):
        """Group slots numbered consecutively in P16 order (1-indexed)."""
        slots = self._slots()
        groups = [s for s in slots if s["type"] == "group"]
        mx_nums = [s["mx_num"] for s in groups]
        assert mx_nums == list(range(1, len(groups) + 1))

    def test_individual_slots_get_sequential_usr_numbers(self):
        slots = self._slots()
        individuals = [s for s in slots if s["type"] == "individual"]
        usr_nums = [s["usr_num"] for s in individuals]
        assert usr_nums == list(range(1, len(individuals) + 1))

    def test_off_and_monitor_slots_have_no_mx_or_usr(self):
        slots = self._slots()
        for s in slots:
            if s["type"] in ("off", "monitor"):
                assert s.get("mx_num") is None
                assert s.get("usr_num") is None

    def test_bass_is_first_individual(self):
        slots = self._slots()
        individuals = [s for s in slots if s["type"] == "individual"]
        assert individuals[0]["label"] == "Bass"
        assert individuals[0]["usr_num"] == 1

    def test_drum_set_is_first_group(self):
        slots = self._slots()
        groups = [s for s in slots if s["type"] == "group"]
        assert groups[0]["label"] == "Drum Set"
        assert groups[0]["mx_num"] == 1

    def test_monitor_slot_has_bus(self):
        slots = self._slots()
        monitors = [s for s in slots if s["type"] == "monitor"]
        assert len(monitors) == 1
        assert monitors[0]["bus"] == "monitor_4"
        assert monitors[0]["slot_num"] == 16


# ---------------------------------------------------------------------------
# Infrastructure rendering — snap_template() output
# ---------------------------------------------------------------------------


class TestPersonalMixerInfrastructure:
    """snap_template() must configure matrices, USR labels, and io.out A.33-A.48."""

    @pytest.fixture(scope="class")
    def snap(self):
        return snap_template()

    def test_group_matrix_names_set(self, snap):
        """Each group slot label is written to ae_data.mtx.{n}.name."""
        import yaml
        infra = yaml.safe_load(Path("data/dsl/infrastructure.yaml").read_text())
        slots = get_p16_slots(infra)
        mtx = snap["ae_data"]["mtx"]
        for s in slots:
            if s["type"] == "group":
                assert mtx[str(s["mx_num"])]["name"] == s["label"], (
                    f"mtx.{s['mx_num']}.name should be {s['label']!r}"
                )

    def test_group_matrix_faders_at_zero(self, snap):
        """Group matrix faders default to 0 dB."""
        import yaml
        infra = yaml.safe_load(Path("data/dsl/infrastructure.yaml").read_text())
        slots = get_p16_slots(infra)
        mtx = snap["ae_data"]["mtx"]
        for s in slots:
            if s["type"] == "group":
                fdr = mtx[str(s["mx_num"])]["fdr"]
                assert abs(fdr) < 0.01, (
                    f"mtx.{s['mx_num']}.fdr={fdr}, expected 0"
                )

    def test_individual_usr_labels_set(self, snap):
        """USR source names are set to slot labels by infrastructure."""
        import yaml
        infra = yaml.safe_load(Path("data/dsl/infrastructure.yaml").read_text())
        slots = get_p16_slots(infra)
        usr = snap["ae_data"]["io"]["in"]["USR"]
        for s in slots:
            if s["type"] == "individual":
                assert usr[str(s["usr_num"])]["name"] == s["label"], (
                    f"USR.{s['usr_num']}.name should be {s['label']!r}"
                )

    def test_individual_usr_sources_off_by_default(self, snap):
        """USR sources default to OFF — assembly populates channel assignments."""
        import yaml
        infra = yaml.safe_load(Path("data/dsl/infrastructure.yaml").read_text())
        slots = get_p16_slots(infra)
        usr = snap["ae_data"]["io"]["in"]["USR"]
        for s in slots:
            if s["type"] == "individual":
                user = usr[str(s["usr_num"])]["user"]
                assert user["grp"] == "OFF", (
                    f"USR.{s['usr_num']}.user.grp should be OFF after infra (before assembly)"
                )

    def test_io_out_group_slots_route_to_mtx(self, snap):
        """Group slot A.xx routes to MTX with in=(mx_num*2)-1."""
        import yaml
        infra = yaml.safe_load(Path("data/dsl/infrastructure.yaml").read_text())
        slots = get_p16_slots(infra)
        io_out_a = snap["ae_data"]["io"]["out"]["A"]
        for s in slots:
            if s["type"] == "group":
                entry = io_out_a[s["a_out"]]
                assert entry["grp"] == "MTX"
                assert entry["in"] == (s["mx_num"] * 2) - 1, (
                    f"A.{s['a_out']}: expected MTX.in={(s['mx_num']*2)-1}, got {entry['in']}"
                )

    def test_io_out_individual_slots_route_to_usr(self, snap):
        """Individual slot A.xx routes to USR.n."""
        import yaml
        infra = yaml.safe_load(Path("data/dsl/infrastructure.yaml").read_text())
        slots = get_p16_slots(infra)
        io_out_a = snap["ae_data"]["io"]["out"]["A"]
        for s in slots:
            if s["type"] == "individual":
                entry = io_out_a[s["a_out"]]
                assert entry == {"grp": "USR", "in": s["usr_num"]}, (
                    f"A.{s['a_out']}: expected USR.{s['usr_num']}, got {entry}"
                )

    def test_io_out_monitor_slot_routes_to_bus16(self, snap):
        """Monitor slot (monitor_4 = bus 16) routes to BUS.in=31."""
        import yaml
        infra = yaml.safe_load(Path("data/dsl/infrastructure.yaml").read_text())
        slots = get_p16_slots(infra)
        io_out_a = snap["ae_data"]["io"]["out"]["A"]
        for s in slots:
            if s["type"] == "monitor":
                entry = io_out_a[s["a_out"]]
                # monitor_4 = bus 16, in = 16*2-1 = 31
                assert entry == {"grp": "BUS", "in": 31}, (
                    f"A.{s['a_out']}: expected BUS.in=31, got {entry}"
                )

    def test_io_out_off_slots_are_off(self, snap):
        """OFF slots route to {grp: OFF, in: 1}."""
        import yaml
        infra = yaml.safe_load(Path("data/dsl/infrastructure.yaml").read_text())
        slots = get_p16_slots(infra)
        io_out_a = snap["ae_data"]["io"]["out"]["A"]
        for s in slots:
            if s["type"] == "off":
                entry = io_out_a[s["a_out"]]
                assert entry == {"grp": "OFF", "in": 1}, (
                    f"A.{s['a_out']}: expected OFF, got {entry}"
                )


# ---------------------------------------------------------------------------
# Assembly rendering — render_assembly() output
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def rendered():
    return render_assembly(ASSEMBLY)


class TestPersonalMixerMXSends:
    """Channels in a group send to the right MX bus at the declared level."""

    def test_kick_sends_to_drum_set_matrix(self, rendered):
        """Kick (ch1) should send to MX1 (Drum Set) with on=True."""
        ch1 = rendered["ae_data"]["ch"]["1"]
        mx = ch1["send"]["MX1"]
        assert mx["on"] is True
        assert mx["mode"] == "PRE"
        assert mx["plink"] is True

    def test_snare_in_drum_set_group(self, rendered):
        ch2 = rendered["ae_data"]["ch"]["2"]
        assert rendered["ae_data"]["ch"]["2"]["send"]["MX1"]["on"] is True

    def test_tom_in_drum_set_group(self, rendered):
        assert rendered["ae_data"]["ch"]["3"]["send"]["MX1"]["on"] is True

    def test_overhead_in_drum_set_group(self, rendered):
        assert rendered["ae_data"]["ch"]["4"]["send"]["MX1"]["on"] is True

    def test_anna_vox_in_back_vox_group(self, rendered):
        """anna-vox (ch27) → MX3 Back Vox."""
        ch27 = rendered["ae_data"]["ch"]["27"]
        assert ch27["send"]["MX3"]["on"] is True
        assert ch27["send"]["MX3"]["mode"] == "PRE"

    def test_yolaine_vox_in_back_vox_group(self, rendered):
        ch28 = rendered["ae_data"]["ch"]["28"]
        assert ch28["send"]["MX3"]["on"] is True

    def test_james_guitar_in_guitars_group(self, rendered):
        """james-guitar (ch13) → MX4 Guitars."""
        ch13 = rendered["ae_data"]["ch"]["13"]
        assert ch13["send"]["MX4"]["on"] is True

    def test_violin_in_guitars_group(self, rendered):
        ch16 = rendered["ae_data"]["ch"]["16"]
        assert ch16["send"]["MX4"]["on"] is True

    def test_flute_in_other_inst_group(self, rendered):
        """flute (ch14) → MX5 Other Inst."""
        ch14 = rendered["ae_data"]["ch"]["14"]
        assert ch14["send"]["MX5"]["on"] is True

    def test_handheld_in_wireless_group(self, rendered):
        """handheld (ch37) → MX6 Wireless."""
        ch37 = rendered["ae_data"]["ch"]["37"]
        assert ch37["send"]["MX6"]["on"] is True

    def test_headset_in_wireless_group(self, rendered):
        ch38 = rendered["ae_data"]["ch"]["38"]
        assert ch38["send"]["MX6"]["on"] is True

    def test_congas_group_empty_for_james(self, rendered):
        """MX2 (Congas) has no members for James team — sends stay off."""
        # Conga channels 6, 7, 8 should not send to MX2
        for ch_num in ["6", "7", "8"]:
            ch = rendered["ae_data"]["ch"][ch_num]
            assert ch["send"]["MX2"]["on"] is False, (
                f"ch{ch_num} should not send to MX2 (Congas group is empty)"
            )

    def test_mx_send_level_at_zero_when_not_specified(self, rendered):
        """MX sends at 0 dB level when no override declared."""
        ch1 = rendered["ae_data"]["ch"]["1"]
        assert abs(ch1["send"]["MX1"]["lvl"]) < 0.01

    def test_channels_not_in_any_group_have_mx_sends_off(self, rendered):
        """Vocalist channels have no MX group assignments — all MX sends off."""
        # james-vox (ch25) is individual, not in any group
        ch25 = rendered["ae_data"]["ch"]["25"]
        for mx_key in ["MX1", "MX2", "MX3", "MX4", "MX5", "MX6"]:
            assert ch25["send"][mx_key]["on"] is False, (
                f"ch25 send.{mx_key} should be off (james-vox is individual, not group)"
            )


class TestPersonalMixerUSRSources:
    """USR sources correctly assigned from individual slot declarations."""

    def test_bass_usr1_points_to_ch5(self, rendered):
        """Bass (ch5) → USR.1, PRE tap."""
        usr1 = rendered["ae_data"]["io"]["in"]["USR"]["1"]
        assert usr1["user"]["grp"] == "CH"
        assert usr1["user"]["in"] == 5
        assert usr1["user"]["tap"] == "PRE"

    def test_lead1_usr2_points_to_priscilla(self, rendered):
        """Lead 1 (priscilla-vox, ch26) → USR.2, POST tap."""
        usr2 = rendered["ae_data"]["io"]["in"]["USR"]["2"]
        assert usr2["user"]["grp"] == "CH"
        assert usr2["user"]["in"] == 26
        assert usr2["user"]["tap"] == "POST"

    def test_lead2_usr3_points_to_james_vox(self, rendered):
        """Lead 2 (james-vox, ch25) → USR.3, POST tap."""
        usr3 = rendered["ae_data"]["io"]["in"]["USR"]["3"]
        assert usr3["user"]["grp"] == "CH"
        assert usr3["user"]["in"] == 25
        assert usr3["user"]["tap"] == "POST"

    def test_piano_usr4_points_to_ch15(self, rendered):
        """Piano (ch15) → USR.4, PRE tap."""
        usr4 = rendered["ae_data"]["io"]["in"]["USR"]["4"]
        assert usr4["user"]["grp"] == "CH"
        assert usr4["user"]["in"] == 15
        assert usr4["user"]["tap"] == "PRE"

    def test_keys_usr5_is_off(self, rendered):
        """Keys has no musician assigned for James — USR.5 grp=OFF."""
        usr5 = rendered["ae_data"]["io"]["in"]["USR"]["5"]
        assert usr5["user"]["grp"] == "OFF"

    def test_usr_labels_preserved_after_assembly(self, rendered):
        """USR source names set in infrastructure survive assembly rendering."""
        usr = rendered["ae_data"]["io"]["in"]["USR"]
        assert usr["1"]["name"] == "Bass"
        assert usr["2"]["name"] == "Lead 1"
        assert usr["3"]["name"] == "Lead 2"
        assert usr["4"]["name"] == "Piano"
        assert usr["5"]["name"] == "Keys"

    def test_usr_lr_field_set(self, rendered):
        """USR sources have lr=L+R."""
        usr = rendered["ae_data"]["io"]["in"]["USR"]
        for k in ["1", "2", "3", "4"]:
            assert usr[k]["user"]["lr"] == "L+R"
