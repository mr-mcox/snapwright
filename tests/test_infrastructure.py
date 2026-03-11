"""Tests for infrastructure DSL — schema, renderer, and firmware patch.

TDD contract: each test encodes a behavior that the infrastructure renderer
must provide. The integration diff against james-2025-12-14.snap is what
drives *what* to test; these unit tests are the *contract*.
"""



from snapwright.wing.defaults import snap_template

# ---------------------------------------------------------------------------
# Firmware patch — Q values
# ---------------------------------------------------------------------------

# Wing factory reset (Init.snap) uses Q=0.997970223 for all EQ bands.
# All real-world snapshots use Q=1.411322355 (≈ √2). This is a firmware
# version difference; snap_template() must patch it globally.

_INIT_Q = 0.997970223
_PATCHED_Q = 1.411322355  # ≈ √2, standard Wing default in current firmware
_INIT_DYNSC_Q = 1.995881796
_PATCHED_DYNSC_Q = 1.411322355


def _all_bus_eq_q(snap: dict) -> set[float]:
    """Collect all float EQ Q values across all buses."""
    result = set()
    for bus in snap["ae_data"]["bus"].values():
        for k, v in bus.get("eq", {}).items():
            if "q" in k and isinstance(v, float):
                result.add(v)
    return result


def _all_ch_eq_q(snap: dict) -> set[float]:
    """Collect all float EQ Q values across all channels."""
    result = set()
    for ch in snap["ae_data"]["ch"].values():
        for k, v in ch.get("eq", {}).items():
            if "q" in k and isinstance(v, float):
                result.add(round(v, 6))
    return result


class TestFirmwarePatch:
    """snap_template() must apply firmware-level corrections
    beyond Init.snap defaults."""

    def test_bus_eq_q_patched_to_sqrt2(self):
        """Bus EQ Q values (lq, 1q-6q) should be patched to sqrt2 on configured buses.

        Exception: bus 8 was never configured by the operator; the firmware patch
        skips it entirely, so Init.snap Q values (0.997970223) stand naturally.
        hq (high-shelf Q) is never patched on any bus.
        """
        snap = snap_template()
        # Buses 1-7 and 9-16 should have patched parametric Q
        for bus_num in ["1", "2", "6", "9", "13", "16"]:
            bus_eq = snap["ae_data"]["bus"][bus_num]["eq"]
            for k, v in bus_eq.items():
                _parametric = ("lq", "1q", "2q", "3q", "4q", "5q", "6q")
                if k in _parametric and isinstance(v, float):
                    assert abs(v - _PATCHED_Q) < 0.01, (
                        f"bus.{bus_num}.eq.{k}={v}, expected ~{_PATCHED_Q}"
                    )
        # Bus 8 EQ Q stays at Init default (firmware patch skips bus 8)
        bus8_eq = snap["ae_data"]["bus"]["8"]["eq"]
        for k in ("lq", "1q"):
            v = bus8_eq.get(k)
            if v is not None:
                assert abs(v - _INIT_Q) < 0.01, (
                    f"bus.8.eq.{k}={v}, expected Init default ~{_INIT_Q}"
                )

    def test_main_eq_q_patched(self):
        """main.3 parametric EQ Q (no infrastructure EQ config) should be
        patched to sqrt2.

        hq (high-shelf Q) is never patched. main.1 has a fully configured EQ via
        infrastructure.yaml with deliberate per-band Q values; not tested here.
        """
        snap = snap_template()
        main3_eq = snap["ae_data"]["main"]["3"]["eq"]
        for k, v in main3_eq.items():
            if k in ("lq", "1q", "2q", "3q", "4q", "5q", "6q") and isinstance(v, float):
                assert abs(v - _PATCHED_Q) < 0.01, (
                    f"main.3.eq.{k}={v} not patched; expected ~{_PATCHED_Q}"
                )

    def test_bus_dynsc_q_patched(self):
        """Bus dynsc.q should be ~sqrt2 for configured buses.

        Exception: bus 8 was never configured; the firmware patch skips it,
        so dynsc.q stays at Init default naturally.
        """
        snap = snap_template()
        for bus_num, bus in snap["ae_data"]["bus"].items():
            if bus_num == "8":
                continue  # bus 8 deliberately keeps Init dynsc.q
            dynsc_q = bus.get("dynsc", {}).get("q")
            if dynsc_q is not None:
                assert abs(dynsc_q - _PATCHED_DYNSC_Q) < 0.01, (
                    f"bus.{bus_num}.dynsc.q = {dynsc_q}, expected ≈ {_PATCHED_DYNSC_Q}"
                )

    def test_cfg_mon_eq_q_patched(self):
        """cfg.mon EQ Q values (init: 1.995881796) should be patched to sqrt2."""
        _CFG_MON_Q_INIT = 1.995881796
        snap = snap_template()
        for mon_num, mon in snap["ae_data"]["cfg"].get("mon", {}).items():
            for k, v in mon.get("eq", {}).items():
                if "q" in k and isinstance(v, float):
                    assert abs(v - _PATCHED_Q) < 0.01, (
                        f"cfg.mon.{mon_num}.eq.{k} = {v}, expected ≈ {_PATCHED_Q}"
                    )


# ---------------------------------------------------------------------------
# Infrastructure sections — these tests are written before the renderer exists.
# They describe what snap_template() must produce after infrastructure is applied.
# ---------------------------------------------------------------------------

class TestInfrastructureDCA:
    """DCA names and faders must come from infrastructure.yaml."""

    def test_dca_names_set(self):
        snap = snap_template()
        dca = snap["ae_data"]["dca"]
        assert dca["1"]["name"] == "Rhythm"
        assert dca["2"]["name"] == "Inst B"
        assert dca["3"]["name"] == "Vox B"
        assert dca["4"]["name"] == "Leads"
        assert dca["5"]["name"] == "FX"
        assert dca["6"]["name"] == "All No L"
        assert dca["7"]["name"] == "Monitors"
        assert dca["8"]["name"] == "DCA|8"

    def test_dca_faders_at_unity(self):
        """DCAs 1-7 should start at unity (0 dB)."""
        snap = snap_template()
        dca = snap["ae_data"]["dca"]
        for i in range(1, 8):
            fdr = dca[str(i)]["fdr"]
            assert abs(fdr - 0.0) < 0.01, f"DCA{i} fdr={fdr}, expected ≈ 0"

    def test_dca8_fader_at_minus144(self):
        snap = snap_template()
        assert snap["ae_data"]["dca"]["8"]["fdr"] == -144


class TestInfrastructureMGRP:
    """Mute group names must come from infrastructure.yaml."""

    def test_mgrp_names(self):
        snap = snap_template()
        mgrp = snap["ae_data"]["mgrp"]
        assert mgrp["1"]["name"] == "Rhythm"
        assert mgrp["2"]["name"] == "Inst B"
        assert mgrp["3"]["name"] == "Vox B"
        assert mgrp["4"]["name"] == "Leads"
        assert mgrp["5"]["name"] == "Inst All"
        assert mgrp["6"]["name"] == "Vox All"
        assert mgrp["7"]["name"] == "Monitors"
        assert mgrp["8"]["name"] == "Worshp"

    def test_mgrp8_muted(self):
        """mgrp8 should be pre-muted (as found in reference snapshot)."""
        snap = snap_template()
        assert snap["ae_data"]["mgrp"]["8"]["mute"] is True


class TestInfrastructureFX:
    """FX slot models must come from infrastructure.yaml (pass-through schema)."""

    def test_fx1_vplate(self):
        snap = snap_template()
        fx1 = snap["ae_data"]["fx"]["1"]
        assert fx1["mdl"] == "V-PLATE"
        assert fx1["fxmix"] == 5

    def test_fx2_vss3_church(self):
        snap = snap_template()
        fx2 = snap["ae_data"]["fx"]["2"]
        assert fx2["mdl"] == "VSS3"
        assert fx2.get("preset") == "Church"

    def test_fx5_vss3_ballad(self):
        snap = snap_template()
        fx5 = snap["ae_data"]["fx"]["5"]
        assert fx5["mdl"] == "VSS3"
        assert fx5.get("preset") == "Ballad Vocal Hall"

    def test_fx6_tapdl(self):
        snap = snap_template()
        fx6 = snap["ae_data"]["fx"]["6"]
        assert fx6["mdl"] == "TAP-DL"

    def test_fx7_vss3_venue(self):
        snap = snap_template()
        fx7 = snap["ae_data"]["fx"]["7"]
        assert fx7["mdl"] == "VSS3"
        assert fx7.get("preset") == "Venue Warm 1"
        assert fx7["fxmix"] == 0  # level via bus send, not mix knob


class TestInfrastructureBuses:
    """Bus names, dynamics model, and routing must come from infrastructure.yaml."""

    def test_bus_led_false(self):
        """Configured buses should have led=False.
        Bus 8 is unconfigured, keeps led=True."""
        snap = snap_template()
        for i in range(1, 13):
            if i == 8:
                continue  # bus 8 was never set up; reference has led=True
            bus = snap["ae_data"]["bus"][str(i)]
            assert bus["led"] is False, f"bus.{i}.led should be False"

    def test_mix_buses_sbus_dynamics(self):
        """Buses 1-7 must use SBUS dynamics model (enabled)."""
        snap = snap_template()
        for i in range(1, 8):
            dyn = snap["ae_data"]["bus"][str(i)]["dyn"]
            assert dyn["mdl"] == "SBUS", f"bus.{i}.dyn.mdl={dyn['mdl']}, expected SBUS"
            assert dyn["on"] is True, f"bus.{i}.dyn.on should be True"

    def test_bus1_name_and_color(self):
        snap = snap_template()
        bus1 = snap["ae_data"]["bus"]["1"]
        assert bus1["name"] == "DRUMS"
        assert bus1["col"] == 8

    def test_monitor_buses_not_to_house(self):
        """Monitor buses 13-16 should have main.1.on=False."""
        snap = snap_template()
        for i in range(13, 17):
            bus = snap["ae_data"]["bus"][str(i)]
            assert bus["main"]["1"]["on"] is False, f"bus.{i}.main.1.on should be False"

    def test_monitor_buses_to_stream(self):
        """Monitor buses 13-16 should have main.2.on=True."""
        snap = snap_template()
        for i in range(13, 17):
            bus = snap["ae_data"]["bus"][str(i)]
            assert bus["main"]["2"]["on"] is True, f"bus.{i}.main.2.on should be True"

    def test_bus1_post_insert_fx1(self):
        """Bus 1 should have FX1 as post-insert (drums reverb)."""
        snap = snap_template()
        postins = snap["ae_data"]["bus"]["1"]["postins"]
        assert postins["ins"] == "FX1"
        assert postins["on"] is True


class TestInfrastructureMain:
    """Main outputs must be configured from infrastructure.yaml."""

    def test_main1_name_and_icon(self):
        snap = snap_template()
        m1 = snap["ae_data"]["main"]["1"]
        assert m1["name"] == "HOUSE"
        assert m1["icon"] == 509
        assert m1["led"] is False

    def test_main2_name_and_icon(self):
        snap = snap_template()
        m2 = snap["ae_data"]["main"]["2"]
        assert m2["name"] == "STREAM"
        assert m2["icon"] == 606
        assert m2["led"] is False

    def test_main1_dynamics_76la(self):
        snap = snap_template()
        dyn = snap["ae_data"]["main"]["1"]["dyn"]
        assert dyn["mdl"] == "76LA"
        assert dyn["on"] is True
        assert dyn["ratio"] == "20"

    def test_main2_dynamics_76la(self):
        snap = snap_template()
        dyn = snap["ae_data"]["main"]["2"]["dyn"]
        assert dyn["mdl"] == "76LA"
        assert dyn["on"] is True

    def test_main3_led_false(self):
        snap = snap_template()
        assert snap["ae_data"]["main"]["3"]["led"] is False


class TestInfrastructureCfg:
    """ae_data.cfg settings from infrastructure.yaml."""

    def test_talkback_assigned_to_ch40(self):
        snap = snap_template()
        assert snap["ae_data"]["cfg"]["talk"]["assign"] == "CH40"

    def test_talkback_monitors_active(self):
        snap = snap_template()
        talk_a = snap["ae_data"]["cfg"]["talk"]["A"]
        assert talk_a["B13"] is True
        assert talk_a["B14"] is True
        assert talk_a["B15"] is True
        assert talk_a["B16"] is True
        assert talk_a["busdim"] == 20

    def test_mon_dim_zero(self):
        """cfg.mon.1 and mon.2 dim and pfldim must be 0 (not Init.snap's 20/12)."""
        snap = snap_template()
        for mon_key in ("1", "2"):
            mon = snap["ae_data"]["cfg"]["mon"][mon_key]
            assert mon["dim"] == 0, f"cfg.mon.{mon_key}.dim={mon['dim']}, expected 0"
            assert mon["pfldim"] == 0, (
                f"cfg.mon.{mon_key}.pfldim={mon['pfldim']}, expected 0"
            )

    def test_mon1_src_main2(self):
        """cfg.mon.1 source should be MAIN.2 (headphones monitor stream)."""
        snap = snap_template()
        assert snap["ae_data"]["cfg"]["mon"]["1"]["src"] == "MAIN.2"

    def test_rta_settings(self):
        snap = snap_template()
        rta = snap["ae_data"]["cfg"]["rta"]
        assert rta["eqdecay"] == "SLOW"
        assert rta["rtadecay"] == "SLOW"
        assert rta["rtasrc"] == 65
        assert rta["rtaauto"] is False
        assert rta["eqgain"] == -5


class TestFirmwarePatchAuxMtx:
    """aux and mtx EQ Q and dynsc.q must be patched to sqrt2."""

    def test_aux_eq_q_patched(self):
        """aux parametric EQ Q values must be patched (hq IS patched for aux)."""
        snap = snap_template()
        for aux_num, aux in snap["ae_data"].get("aux", {}).items():
            for k, v in aux.get("eq", {}).items():
                if k in ("1q", "2q", "lq") and isinstance(v, float):
                    assert abs(v - _PATCHED_Q) < 0.01, (
                        f"aux.{aux_num}.eq.{k}={v}, expected ~{_PATCHED_Q}"
                    )

    def test_aux_hq_patched(self):
        """aux hq (high-shelf Q) IS patched — unlike buses where it's left alone."""
        snap = snap_template()
        for aux_num, aux in snap["ae_data"].get("aux", {}).items():
            hq = aux.get("eq", {}).get("hq")
            if isinstance(hq, float):
                assert abs(hq - _PATCHED_Q) < 0.01, (
                    f"aux.{aux_num}.eq.hq={hq}, expected ~{_PATCHED_Q}"
                )

    def test_mtx_eq_q_patched(self):
        """mtx parametric EQ Q values must be patched (hq NOT patched for mtx)."""
        snap = snap_template()
        for mtx_num, mtx in snap["ae_data"].get("mtx", {}).items():
            for k, v in mtx.get("eq", {}).items():
                if k in ("1q", "2q", "lq") and isinstance(v, float):
                    assert abs(v - _PATCHED_Q) < 0.01, (
                        f"mtx.{mtx_num}.eq.{k}={v}, expected ~{_PATCHED_Q}"
                    )

    def test_mtx_hq_not_patched(self):
        """mtx hq stays at Init default — same pattern as buses."""
        snap = snap_template()
        for mtx_num, mtx in snap["ae_data"].get("mtx", {}).items():
            hq = mtx.get("eq", {}).get("hq")
            if isinstance(hq, float):
                assert abs(hq - _INIT_Q) < 0.01, (
                    f"mtx.{mtx_num}.eq.hq={hq}, expected Init default ~{_INIT_Q}"
                )

    def test_aux_dynsc_q_patched(self):
        snap = snap_template()
        for aux_num, aux in snap["ae_data"].get("aux", {}).items():
            q = aux.get("dynsc", {}).get("q")
            if q is not None and isinstance(q, float):
                assert abs(q - _PATCHED_DYNSC_Q) < 0.01, (
                    f"aux.{aux_num}.dynsc.q={q}, expected ~{_PATCHED_DYNSC_Q}"
                )

    def test_mtx_dynsc_q_patched(self):
        snap = snap_template()
        for mtx_num, mtx in snap["ae_data"].get("mtx", {}).items():
            q = mtx.get("dynsc", {}).get("q")
            if q is not None and isinstance(q, float):
                assert abs(q - _PATCHED_DYNSC_Q) < 0.01, (
                    f"mtx.{mtx_num}.dynsc.q={q}, expected ~{_PATCHED_DYNSC_Q}"
                )


class TestOutputRouting:
    """Physical output routing (io.out) derived from infrastructure.yaml outputs: keys.

    Renderer derives Wing-native {grp, in} from context:
    - mains: grp=MAIN, in=main_num (one slot per main; mains 3+ masked in diff)
    - monitor buses: grp=BUS, in=bus_num*2-1 (Wing's L-channel virtual index)
    """
    def _io_out(self, snap: dict) -> dict:
        return snap["ae_data"]["io"]["out"]
        """mains.1 outputs: A: 1 → {grp: MAIN, in: 1}"""
        io_out = self._io_out(snap_template())
        assert io_out["A"]["1"] == {"grp": "MAIN", "in": 1}
    def test_main2_to_stage_box_a2(self):
        """mains.2 outputs: A: 2 → {grp: MAIN, in: 2}"""
        io_out = self._io_out(snap_template())
        assert io_out["A"]["2"] == {"grp": "MAIN", "in": 2}
        """Monitor buses 13-16 route to A.3-A.6; in derived as bus_num*2-1."""
        io_out = self._io_out(snap_template())
        assert io_out["A"]["3"] == {"grp": "BUS", "in": 25}  # bus 13: 13*2-1=25
        assert io_out["A"]["4"] == {"grp": "BUS", "in": 27}  # bus 14: 14*2-1=27
        assert io_out["A"]["5"] == {"grp": "BUS", "in": 29}  # bus 15: 15*2-1=29
        assert io_out["A"]["6"] == {"grp": "BUS", "in": 31}  # bus 16: 16*2-1=31


class TestAuxDefaults:
    """AUX structural defaults and infrastructure settings."""

    def test_aux1_name(self):
        snap = snap_template()
        assert snap["ae_data"]["aux"]["1"]["name"] == "USB 1/2"

    def test_aux_send_modes_post_for_buses_1_to_12(self):
        """All aux channels must have POST send mode for buses 1-12."""
        snap = snap_template()
        for aux_num, aux in snap["ae_data"].get("aux", {}).items():
            send = aux.get("send", {})
            for bus in [str(i) for i in range(1, 13)]:
                if bus in send:
                    mode = send[bus].get("mode")
                    assert mode == "POST", (
                        f"aux.{aux_num}.send.{bus}.mode={mode!r}, expected POST"
                    )

    def test_aux_send_modes_pre_for_buses_13_to_16(self):
        """All aux channels must have PRE send mode for buses 13-16."""
        snap = snap_template()
        for aux_num, aux in snap["ae_data"].get("aux", {}).items():
            send = aux.get("send", {})
            for bus in [str(i) for i in range(13, 17)]:
                if bus in send:
                    mode = send[bus].get("mode")
                    assert mode == "PRE", (
                        f"aux.{aux_num}.send.{bus}.mode={mode!r}, expected PRE"
                    )

    def test_aux_main_outputs_off(self):
        """All aux channels must have all main outputs off."""
        snap = snap_template()
        for aux_num, aux in snap["ae_data"].get("aux", {}).items():
            for out_key, out_cfg in aux.get("main", {}).items():
                assert out_cfg.get("on") is False, (
                    f"aux.{aux_num}.main.{out_key}.on should be False"
                )


# ---------------------------------------------------------------------------
# Bus and main faders
# ---------------------------------------------------------------------------


class TestInfrastructureBusFaders:
    """Bus faders must be set from infrastructure.yaml, not left at Init -144."""

    def test_mix_buses_not_at_init_floor(self):
        """Buses 1-7 must not be at Init default (-144 dB) after infrastructure."""
        snap = snap_template()
        for i in range(1, 8):
            fdr = snap["ae_data"]["bus"][str(i)]["fdr"]
            assert fdr > -10, f"bus.{i}.fdr={fdr}, expected near 0 dB (not Init -144)"

    def test_bus1_fader(self):
        snap = snap_template()
        assert abs(snap["ae_data"]["bus"]["1"]["fdr"] - (-0.42969)) < 0.01

    def test_bus6_vocals_fader(self):
        snap = snap_template()
        assert abs(snap["ae_data"]["bus"]["6"]["fdr"] - 2.23633) < 0.01

    def test_bus8_keeps_init_floor(self):
        """Bus 8 is unconfigured — fdr stays at Init -144."""
        snap = snap_template()
        assert snap["ae_data"]["bus"]["8"]["fdr"] == -144.0

    def test_bus12_back_vox_fader(self):
        """Bus 12 (Back Vox) starts at -144 dB per reference."""
        snap = snap_template()
        assert snap["ae_data"]["bus"]["12"]["fdr"] == -144.0

    def test_monitor_buses_keep_init_default(self):
        """Monitor buses 13-16 keep Init default (0 dB) — session-adjusted, not set here."""
        snap = snap_template()
        for i in range(13, 17):
            fdr = snap["ae_data"]["bus"][str(i)]["fdr"]
            assert fdr == 0.0, f"bus.{i}.fdr={fdr}, expected Init default 0.0"


class TestInfrastructureMainFaders:
    """Main output faders must be set from infrastructure.yaml."""

    def test_main1_fader_not_at_init_floor(self):
        snap = snap_template()
        assert snap["ae_data"]["main"]["1"]["fdr"] > -144

    def test_main2_fader_not_at_init_floor(self):
        snap = snap_template()
        assert snap["ae_data"]["main"]["2"]["fdr"] > -144

    def test_main1_fader(self):
        snap = snap_template()
        assert abs(snap["ae_data"]["main"]["1"]["fdr"] - (-35.42969)) < 0.01

    def test_main2_fader(self):
        snap = snap_template()
        assert abs(snap["ae_data"]["main"]["2"]["fdr"] - 0.54688) < 0.01

    def test_main3_keeps_init_floor(self):
        """Main 3 is not infrastructure-managed — keeps Init -144."""
        snap = snap_template()
        assert snap["ae_data"]["main"]["3"]["fdr"] == -144.0