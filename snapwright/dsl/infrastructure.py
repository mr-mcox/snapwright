"""Infrastructure renderer — applies infrastructure.yaml to a Wing snap dict.

infrastructure.yaml expresses every intentional change from the Wing factory
reset (Init.snap): FX slots, buses 1-16, main outputs, infrastructure channels
(ch37-40), DCA names, mute group names, and console config.

This module also applies firmware-level patches that Init.snap predates — EQ
Q defaults and dynsc Q defaults — since these affect every channel, bus, and
main output globally.

Called by snap_template() in defaults.py so the invariant holds for all callers.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

_INFRA_YAML_PATH = (
    Path(__file__).parent.parent.parent / "data" / "dsl" / "infrastructure.yaml"
)

# ---------------------------------------------------------------------------
# Firmware-level Q corrections
# ---------------------------------------------------------------------------
# Init.snap was saved with an older firmware that initialised EQ Q to ~1 and
# dynsc Q to ~2.  All current real-world Wing snapshots use Q = √2 ≈ 1.411322355
# for EQ bands and dynsc. We patch these universally so Init.snap + infra
# produces Q values that match real-world snapshots.

_EQ_Q_PATCHED = 1.411322355
_DYNSC_Q_PATCHED = 1.411322355
_EQ_Q_INIT = 0.997970223
_DYNSC_Q_INIT = 1.995881796


def _patch_eq_q(eq: dict, patch_hq: bool = False) -> None:
    """Replace Init.snap default EQ Q values with current-firmware defaults.
    By default skips hq (high-shelf Q): real-world bus/main snapshots keep
    hq=0.997970223. Pass patch_hq=True for channels, where Wing DOES update
    hq on configure.
    Pass patch_hq=True for channels, where Wing DOES update hq on configure.
    """
    for k, v in eq.items():
        if k == "hq" and not patch_hq:
            continue  # high-shelf Q is NOT patched for buses/mains
        if "q" in k and isinstance(v, float) and abs(v - _EQ_Q_INIT) < 0.01:
            eq[k] = _EQ_Q_PATCHED


def _patch_dynsc_q(dynsc: dict) -> None:
    q = dynsc.get("q")
    if q is not None and isinstance(q, float) and abs(q - _DYNSC_Q_INIT) < 0.01:
        dynsc["q"] = _DYNSC_Q_PATCHED


def apply_firmware_patches(snap: dict) -> None:
    """Apply firmware-version corrections to the full snap dict in-place.
    Covers all buses, mains, aux, mtx, cfg.mon, and all channels.
    """
    ae = snap["ae_data"]

    # Buses 1-16 — patch parametric EQ Q and dynsc.q globally.
    # Bus 8 is excluded: never operator-configured; firmware patch skipped so
    # Init.snap Q values stand (bus 8 is masked in the diff harness).
    for bus_num, bus in ae.get("bus", {}).items():
        if bus_num == "8":
            continue
        _patch_eq_q(bus.get("eq", {}))
        _patch_dynsc_q(bus.get("dynsc", {}))

    # Main outputs 1-3 — patch parametric EQ Q and dynsc.q
    for main in ae.get("main", {}).values():
        _patch_eq_q(main.get("eq", {}))
        _patch_dynsc_q(main.get("dynsc", {}))

    # cfg.mon monitoring EQ — uses 1.995881796 as init Q (same as dynsc),
    # not 0.997970223
    _CFG_MON_Q_INIT = 1.995881796
    for mon in ae.get("cfg", {}).get("mon", {}).values():
        mon_eq = mon.get("eq", {})
        for k, v in list(mon_eq.items()):
            if "q" in k and isinstance(v, float) and abs(v - _CFG_MON_Q_INIT) < 0.01:
                mon_eq[k] = _EQ_Q_PATCHED

    # All channels
    for ch in ae.get("ch", {}).values():
        _patch_eq_q(ch.get("eq", {}), patch_hq=True)
        _patch_dynsc_q(ch.get("dynsc", {}))
        _patch_dynsc_q(ch.get("gatesc", {}))   # gate sidechain uses dynsc Q default
        _patch_eq_q(ch.get("peq", {}), patch_hq=True)  # parallel EQ section

    # AUX channels — patch parametric EQ Q (hq IS patched; same as channels)
    # and dynsc.q. Both james and priscilla reference snaps confirm this.
    for aux in ae.get("aux", {}).values():
        _patch_eq_q(aux.get("eq", {}), patch_hq=True)
        _patch_dynsc_q(aux.get("dynsc", {}))

    # MTX channels — patch parametric EQ Q (hq NOT patched; same as buses)
    # and dynsc.q.
    for mtx in ae.get("mtx", {}).values():
        _patch_eq_q(mtx.get("eq", {}))
        _patch_dynsc_q(mtx.get("dynsc", {}))


def patch_channel_firmware(ch: dict) -> None:
    """Apply firmware Q patches to a single freshly-loaded channel dict.
    Covers eq, dynsc, gatesc, and peq Q values.
    """
    _patch_eq_q(ch.get("eq", {}), patch_hq=True)
    _patch_dynsc_q(ch.get("dynsc", {}))
    _patch_dynsc_q(ch.get("gatesc", {}))   # gate sidechain EQ uses dynsc Q default
    _patch_eq_q(ch.get("peq", {}), patch_hq=True)  # parametric EQ section


# ---------------------------------------------------------------------------
# YAML normalisation
# ---------------------------------------------------------------------------

def _normalize_yaml_keys(obj: Any) -> Any:
    """Recursively convert boolean True/False keys to 'on'/'off' strings.

    Wing JSON uses the string key 'on' but Python/YAML can produce True
    when a YAML boolean key is used accidentally.
    """
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            if k is True:
                k = "on"
            elif k is False:
                k = "off"
            is_int_key = isinstance(k, (int, float)) and not isinstance(k, bool)
            result[str(k) if is_int_key else k] = _normalize_yaml_keys(v)
        return result
    elif isinstance(obj, list):
        return [_normalize_yaml_keys(i) for i in obj]
    return obj


# ---------------------------------------------------------------------------
# Infrastructure application
# ---------------------------------------------------------------------------

def apply_infrastructure(snap: dict, infra_path: Path | None = None) -> None:
    """Apply infrastructure.yaml changes to a snap dict in-place.

    Safe to call even if infrastructure.yaml doesn't exist yet — a missing
    file is treated as an empty config (useful during early development).
    """
    if infra_path is None:
        infra_path = _INFRA_YAML_PATH

    if not infra_path.exists():
        return  # No infrastructure yet — Init.snap values stand

    with infra_path.open() as f:
        raw = yaml.safe_load(f) or {}

    infra = _normalize_yaml_keys(raw)
    ae = snap["ae_data"]

    _apply_fx(ae, infra.get("fx", {}))
    _apply_buses(ae, infra.get("buses", {}))
    _apply_mains(ae, infra.get("mains", {}))
    _apply_aux_structural_defaults(ae)
    _apply_aux(ae, infra.get("aux", {}))
    _apply_dca(ae, infra.get("dca", {}))
    _apply_mgrp(ae, infra.get("mgrp", {}))
    _apply_cfg(ae, infra.get("cfg", {}))
    _apply_channels(ae, infra.get("channels", {}))
    _apply_personal_mixer(ae, infra)


# ---------------------------------------------------------------------------
# FX slots
# ---------------------------------------------------------------------------

def _apply_fx(ae: dict, fx_config: dict) -> None:
    """Apply FX slot configs. Pass-through: any key in YAML goes to snap."""
    for slot_str, params in fx_config.items():
        slot_key = str(slot_str)
        if slot_key not in ae["fx"]:
            ae["fx"][slot_key] = {}
        ae["fx"][slot_key].update(params)


# ---------------------------------------------------------------------------
# Buses
# ---------------------------------------------------------------------------

_BUS_FIELD_MAP = {
    "name": "name",
    "color": "col",
    "icon": "icon",
    "led": "led",
    "tags": "tags",
}

# ---------------------------------------------------------------------------
# DSL vocabulary translation — bus / main dynamics and EQ
# ---------------------------------------------------------------------------

_BUS_DYN_DSL_MAP = {
    "model": "mdl",
    "threshold": "thr",
    "attack": "att",
    "release": "rel",
}

_MAIN_DYN_DSL_MAP = {
    "model": "mdl",
    "input": "in",
    "output": "out",
    "attack": "att",
    "release": "rel",
}


def _translate_bus_dyn(dyn_config: dict) -> dict:
    """Translate DSL dynamics vocabulary to Wing field names for buses.

    Also handles Wing string-encoding artifacts:
    - SBUS stores rel as a string (e.g. "0.4", not 0.4)
    """
    model = dyn_config.get("model") or dyn_config.get("mdl")
    result = {_BUS_DYN_DSL_MAP.get(k, k): v for k, v in dyn_config.items()}
    if model == "SBUS" and "rel" in result:
        result["rel"] = str(result["rel"])
    return result


def _translate_main_dyn(dyn_config: dict) -> dict:
    """Translate DSL dynamics vocabulary to Wing field names for main outputs.

    Also handles Wing string-encoding artifacts:
    - 76LA stores ratio as a string (e.g. "20", not 20)
    """
    model = dyn_config.get("model") or dyn_config.get("mdl")
    result = {_MAIN_DYN_DSL_MAP.get(k, k): v for k, v in dyn_config.items()}
    if model == "76LA" and "ratio" in result:
        result["ratio"] = str(int(result["ratio"]))
    return result

def _apply_infra_eq_shelf(result: dict, shelf: dict, prefix: str) -> None:
    """Write a DSL shelf dict {gain, freq, q} into result with Wing prefix."""
    if shelf.get("gain") is not None:
        result[f"{prefix}g"] = shelf["gain"]
    if shelf.get("freq") is not None:
        result[f"{prefix}f"] = shelf["freq"]
    if shelf.get("q") is not None:
        result[f"{prefix}q"] = shelf["q"]


def _translate_infra_eq(eq_config: dict) -> dict:
    """Translate DSL EQ vocabulary to Wing field names.
    - bands: {N: {gain, freq, q}} -> {Ng, Nf, Nq}
    - high_shelf: {gain, freq, q} -> {hg, hf, hq}
    - low_shelf:  {gain, freq, q} -> {lg, lf, lq}
    - on, mix, model: passed through unchanged
    """
    result: dict = {}
    for k, v in eq_config.items():
        if k == "bands" and isinstance(v, dict):
            for band_num, band in v.items():
                n = str(band_num)
                if band.get("gain") is not None:
                    result[f"{n}g"] = band["gain"]
                if band.get("freq") is not None:
                    result[f"{n}f"] = band["freq"]
                if band.get("q") is not None:
                    result[f"{n}q"] = band["q"]
        elif k == "high_shelf" and isinstance(v, dict):
            _apply_infra_eq_shelf(result, v, "h")
        elif k == "low_shelf" and isinstance(v, dict):
            _apply_infra_eq_shelf(result, v, "l")
        else:
            result[k] = v
    return result

def _apply_bus_dynamics(bus: dict, dyn_config: dict) -> None:
    """Apply dynamics config to a bus dict.
    field contamination. COMP patches in-place.
    When switching to SBUS, also patches dynsc.q to sqrt2 — Wing applies this
    when configuring a bus with SBUS dynamics.
    """
    translated = _translate_bus_dyn(dyn_config)
    model = translated.get("mdl")
    if model is None:
        return
    if model != bus.get("dyn", {}).get("mdl"):
        # Model change — rebuild from scratch to avoid old-model field contamination
        bus["dyn"] = {"mdl": model, "mix": 100}
        if model == "SBUS":
            # SBUS configuration also updates dynsc.q to sqrt2 — Wing does this
            # when you configure a bus with SBUS dynamics
            bus.setdefault("dynsc", {})["q"] = _DYNSC_Q_PATCHED
    bus["dyn"].update(translated)


def _apply_bus_inserts(bus: dict, preins: dict | None, postins: dict | None) -> None:
    if preins:
        bus["preins"].update(preins)
    if postins:
        bus["postins"].update(postins)


def _apply_single_bus(bus: dict, bus_cfg: dict) -> None:
    for yaml_key, snap_key in _BUS_FIELD_MAP.items():
        if yaml_key in bus_cfg:
            bus[snap_key] = bus_cfg[yaml_key]
    if "dyn" in bus_cfg:
        _apply_bus_dynamics(bus, bus_cfg["dyn"])
    if "eq" in bus_cfg:
        bus["eq"].update(_translate_infra_eq(bus_cfg["eq"]))
    if "dynsc" in bus_cfg:
        bus.setdefault("dynsc", {}).update(bus_cfg["dynsc"])
    if "preins" in bus_cfg:
        bus["preins"].update(bus_cfg["preins"])
    if "postins" in bus_cfg:
        bus["postins"].update(bus_cfg["postins"])
    if "main" in bus_cfg:
        for out_key, out_cfg in bus_cfg["main"].items():
            bus["main"][str(out_key)].update(out_cfg)


def _apply_buses(ae: dict, buses_config: dict) -> None:
    for bus_str, bus_cfg in buses_config.items():
        _apply_single_bus(ae["bus"][str(bus_str)], bus_cfg)
        if "outputs" in bus_cfg:
            _apply_bus_outputs(ae, int(bus_str), bus_cfg["outputs"])

# ---------------------------------------------------------------------------
# Main outputs
# ---------------------------------------------------------------------------

def _apply_main_dynamics(main: dict, dyn_config: dict) -> None:
    translated = _translate_main_dyn(dyn_config)
    model = translated.get("mdl")
    if model is None:
        return
    if model != main.get("dyn", {}).get("mdl"):
        main["dyn"] = {"mdl": model, "mix": 100}
    main["dyn"].update(translated)


def _apply_mains(ae: dict, mains_config: dict) -> None:
    for out_str, out_cfg in mains_config.items():
        out_key = str(out_str)
        main = ae["main"][out_key]

        for yaml_key, snap_key in _BUS_FIELD_MAP.items():
            if yaml_key in out_cfg:
                main[snap_key] = out_cfg[yaml_key]

        if "dyn" in out_cfg:
            _apply_main_dynamics(main, out_cfg["dyn"])

        if "eq" in out_cfg:
            main["eq"].update(_translate_infra_eq(out_cfg["eq"]))

        if "in" in out_cfg:
            _deep_update(main["in"], out_cfg["in"])

        if "preins" in out_cfg:
            main["preins"].update(out_cfg["preins"])
        if "postins" in out_cfg:
            main["postins"].update(out_cfg["postins"])
        if "outputs" in out_cfg:
            _apply_main_outputs(ae, int(out_key), out_cfg["outputs"])


# ---------------------------------------------------------------------------
# DCA
# ---------------------------------------------------------------------------

def _apply_dca(ae: dict, dca_config: dict) -> None:
    for dca_str, dca_cfg in dca_config.items():
        dca_key = str(dca_str)
        dca = ae["dca"][dca_key]
        if "name" in dca_cfg:
            dca["name"] = dca_cfg["name"]
        if "fdr" in dca_cfg:
            dca["fdr"] = dca_cfg["fdr"]


# ---------------------------------------------------------------------------
# Mute groups
# ---------------------------------------------------------------------------

def _apply_mgrp(ae: dict, mgrp_config: dict) -> None:
    for mgrp_str, mgrp_cfg in mgrp_config.items():
        mgrp_key = str(mgrp_str)
        mgrp = ae["mgrp"][mgrp_key]
        if "name" in mgrp_cfg:
            mgrp["name"] = mgrp_cfg["name"]
        if "mute" in mgrp_cfg:
            mgrp["mute"] = mgrp_cfg["mute"]


# ---------------------------------------------------------------------------
# Console config
# ---------------------------------------------------------------------------

def _apply_cfg(ae: dict, cfg_config: dict) -> None:
    if not cfg_config:
        return
    cfg = ae["cfg"]

    if "talk" in cfg_config:
        _deep_update(cfg["talk"], cfg_config["talk"])

    if "mon" in cfg_config:
        for mon_key, mon_cfg in cfg_config["mon"].items():
            _deep_update(cfg["mon"][str(mon_key)], mon_cfg)

    if "rta" in cfg_config:
        cfg["rta"].update(cfg_config["rta"])


# ---------------------------------------------------------------------------
# Infrastructure channels (ch37-40)
# ---------------------------------------------------------------------------

_INFRA_CH_SEND_MIX_KEYS = [str(i) for i in range(1, 13)]   # buses 1-12: POST
_INFRA_CH_SEND_MON_KEYS = [str(i) for i in range(13, 17)]  # buses 13-16: PRE
_INFRA_CH_SEND_MX_KEYS = [f"MX{i}" for i in range(1, 9)]  # personal: PRE + plink

_SEND_OFF_POST = {
    "on": False, "lvl": -144.0, "pon": False, "mode": "POST", "plink": False, "pan": 0
}
_SEND_OFF_PRE = {
    "on": False, "lvl": -144.0, "pon": False, "mode": "PRE", "plink": False, "pan": 0
}
_SEND_OFF_MX = {
    "on": False, "lvl": -144.0, "pon": False, "mode": "PRE", "plink": True, "pan": 0
}


def _build_infra_channel_sends(sends_cfg: dict) -> dict:
    """Build a complete send dict for an infrastructure channel.

    POST for buses 1-8, PRE for buses 9-12 (wait — ref shows POST for all 1-12)
    Actually per the brief: "POST for buses 1-8, PRE for 13-16".
    Buses 9-12 are also POST (they're submix/FX return buses, not monitors).
    """
    sends: dict = {}
    for k in _INFRA_CH_SEND_MIX_KEYS:
        sends[k] = copy.deepcopy(_SEND_OFF_POST)
    for k in _INFRA_CH_SEND_MON_KEYS:
        sends[k] = copy.deepcopy(_SEND_OFF_PRE)
    for k in _INFRA_CH_SEND_MX_KEYS:
        sends[k] = copy.deepcopy(_SEND_OFF_MX)

    # Apply specified sends
    for bus_key, send_cfg in sends_cfg.items():
        bus_key = str(bus_key)
        if bus_key in sends and isinstance(send_cfg, dict):
            sends[bus_key].update(send_cfg)
        elif bus_key in sends and isinstance(send_cfg, (int, float)):
            # Shorthand: just a level → turn on
            bus_num = int(bus_key) if bus_key.isdigit() else None
            sends[bus_key]["lvl"] = float(send_cfg)
            sends[bus_key]["on"] = True
            if bus_num is not None:
                sends[bus_key]["mode"] = "PRE" if bus_num >= 13 else "POST"

    return sends


_CH_SCALAR_KEYS = ("name", "col", "icon", "mute", "fdr", "led", "clink")


def _apply_channel_identity(ch: dict, ch_cfg: dict) -> None:
    for key in _CH_SCALAR_KEYS:
        if key in ch_cfg:
            ch[key] = ch_cfg[key]
    if "ptap" in ch_cfg:
        ch["ptap"] = str(ch_cfg["ptap"])
    if "in" in ch_cfg:
        _deep_update(ch["in"], ch_cfg["in"])


def _apply_channel_processing(ch: dict, ch_cfg: dict) -> None:
    if "eq" in ch_cfg:
        ch["eq"].update(ch_cfg["eq"])
    if "dyn" in ch_cfg:
        ch["dyn"].update(ch_cfg["dyn"])
    if "gate" in ch_cfg:
        ch["gate"].update(ch_cfg["gate"])
    if "flt" in ch_cfg:
        ch["flt"].update(ch_cfg["flt"])
    if "preins" in ch_cfg:
        ch["preins"].update(ch_cfg["preins"])
    if "postins" in ch_cfg:
        ch["postins"].update(ch_cfg["postins"])


def _apply_channels(ae: dict, channels_config: dict) -> None:
    """Apply infrastructure channel configs (ch37-40)."""
    for ch_str, ch_cfg in channels_config.items():
        ch = ae["ch"][str(ch_str)]
        _apply_channel_identity(ch, ch_cfg)
        _apply_channel_processing(ch, ch_cfg)
        if "main" in ch_cfg:
            for out_key, out_cfg in ch_cfg["main"].items():
                ch["main"][str(out_key)].update(out_cfg)
        if "send" in ch_cfg:
            ch["send"] = _build_infra_channel_sends(ch_cfg["send"])

# ---------------------------------------------------------------------------
# Physical output routing (io.out)
# ---------------------------------------------------------------------------

def _apply_main_outputs(ae: dict, main_num: int, outputs: dict) -> None:
    """Write main output routing into ae_data.io.out.

    outputs: {port_group: slot_number}  e.g. {"A": 1}
    Derives Wing fields: grp="MAIN", in=main_num.
    No stereo complexity — mains 1 and 2 are the only outputs expressed;
    mains 3+ are masked in the diff harness.
    """
    io_out = ae["io"]["out"]
    for port_grp, slot in outputs.items():
        io_out.setdefault(port_grp, {})[str(slot)] = {"grp": "MAIN", "in": main_num}


def _apply_bus_outputs(ae: dict, bus_num: int, outputs: dict) -> None:
    """Write monitor bus output routing into ae_data.io.out.

    outputs: {port_group: slot_number}  e.g. {"A": 3}
    Derives Wing fields: grp="BUS", in=bus_num*2-1 (Wing virtual L-channel index).
    """
    bus_in = bus_num * 2 - 1
    io_out = ae["io"]["out"]
    for port_grp, slot in outputs.items():
        io_out.setdefault(port_grp, {})[str(slot)] = {"grp": "BUS", "in": bus_in}


# ---------------------------------------------------------------------------
# AUX structural defaults
# ---------------------------------------------------------------------------

_AUX_POST_BUSES = [str(i) for i in range(1, 13)]   # buses 1-12: POST
_AUX_PRE_BUSES  = [str(i) for i in range(13, 17)]  # buses 13-16: PRE


def _apply_aux_structural_defaults(ae: dict) -> None:
    """Fix Init.snap aux send modes and ensure aux doesn't route to mains.

    Init.snap has buses 1-8 as PRE, 9-10 as GRP, 11-16 as POST.
    Both james and priscilla reference snaps have POST for 1-12, PRE for 13-16.
    This is a fixed infrastructure patch (same class as firmware Q patches).
    LCL outputs are masked in the diff harness so Init.snap LCL defaults
    are not cleared here.
    """
    for aux in ae.get("aux", {}).values():
        send = aux.get("send", {})
        for k in _AUX_POST_BUSES:
            if k in send:
                send[k]["mode"] = "POST"
        for k in _AUX_PRE_BUSES:
            if k in send:
                send[k]["mode"] = "PRE"
        # Aux outputs never route to mains
        for out_cfg in aux.get("main", {}).values():
            if isinstance(out_cfg, dict):
                out_cfg["on"] = False


def _apply_aux(ae: dict, aux_config: dict) -> None:
    """Apply aux section from infrastructure.yaml (name and other scalar fields)."""
    for aux_str, aux_cfg in aux_config.items():
        aux_key = str(aux_str)
        if aux_key not in ae.get("aux", {}):
            continue
        aux = ae["aux"][aux_key]
        if "name" in aux_cfg:
            aux["name"] = aux_cfg["name"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _deep_update(target: dict, source: dict) -> None:
    """Recursively update target with source — dicts merge, other values replace."""
    for k, v in source.items():
        if isinstance(v, dict) and isinstance(target.get(k), dict):
            _deep_update(target[k], v)
        else:
            target[k] = v


# ---------------------------------------------------------------------------
# Personal mixer (P16) — slot topology + infrastructure rendering
# ---------------------------------------------------------------------------

# Monitor logical-name → bus number. These are invariant across all teams.
_MONITOR_BUS_NUMBERS: dict[str, int] = {
    "monitor_1": 13,
    "monitor_2": 14,
    "monitor_3": 15,
    "monitor_4": 16,
}


def get_p16_slots(infra_yaml: dict) -> list[dict]:
    """Parse personal_mixer.slots from infrastructure.yaml into 16 slot dicts.

    The YAML uses a dict keyed by slot number (1-16); absent slots become OFF.
    MX numbers assigned in ascending slot-number order across group slots.
    USR numbers assigned in ascending slot-number order across individual slots.

    Returns a list of exactly 16 dicts (index 0 = slot 1), each with:
      slot_num  : int  1-16 (physical P16 channel position)
      a_out     : str  Wing stage-box output slot ("33"-"48")
      type      : str  "group" | "individual" | "monitor" | "off"
      label     : str | None  (display label; None for off slots)
      tap       : str | None  ("PRE" or "POST"; individual slots only)
      bus       : str | None  (logical bus name; monitor slots only)
      mx_num    : int | None  (sequential MX number; group slots only)
      usr_num   : int | None  (sequential USR number; individual slots only)
    """
    raw = infra_yaml.get("personal_mixer", {}).get("slots", {})

    # Assign MX and USR numbers in ascending slot order
    mx_counter = 1
    usr_counter = 1
    numbered: dict[int, dict] = {}
    for slot_num in sorted(int(k) for k in raw):
        cfg = raw[slot_num] if slot_num in raw else raw[str(slot_num)]
        slot_type = cfg.get("type", "off")
        mx_num = usr_num = None
        if slot_type == "group":
            mx_num = mx_counter
            mx_counter += 1
        elif slot_type == "individual":
            usr_num = usr_counter
            usr_counter += 1
        numbered[slot_num] = {
            "slot_num": slot_num,
            "a_out": str(32 + slot_num),
            "type": slot_type,
            "label": cfg.get("label"),
            "tap": cfg.get("tap"),
            "bus": cfg.get("bus"),
            "mx_num": mx_num,
            "usr_num": usr_num,
        }

    # Fill all 16 slots; absent ones are OFF
    result = []
    for i in range(1, 17):
        if i in numbered:
            result.append(numbered[i])
        else:
            result.append({
                "slot_num": i,
                "a_out": str(32 + i),
                "type": "off",
                "label": None,
                "tap": None,
                "bus": None,
                "mx_num": None,
                "usr_num": None,
            })
    return result


def _apply_personal_mixer(ae: dict, infra_yaml: dict) -> None:
    """Apply personal mixer infrastructure to snap:
    - Write matrix names + faders for group slots
    - Write USR source label defaults for individual slots (channel assignment
      deferred to assembly rendering)
    - Write io.out A.33-A.48 routing for all 16 slots
    """
    slots = get_p16_slots(infra_yaml)
    if not slots:
        return
    io_out_a = ae["io"]["out"].setdefault("A", {})
    usr_in = ae["io"]["in"]["USR"]
    for s in slots:
        a_key = s["a_out"]
        if s["type"] == "group":
            n = s["mx_num"]
            mtx = ae["mtx"][str(n)]
            mtx["name"] = s["label"] or ""
            mtx["fdr"] = 0.0
            io_out_a[a_key] = {"grp": "MTX", "in": (n * 2) - 1}
        elif s["type"] == "individual":
            n = s["usr_num"]
            usr = usr_in[str(n)]
            usr["name"] = s["label"] or ""
            # Leave user.grp=OFF — assembly renderer populates the channel
            io_out_a[a_key] = {"grp": "USR", "in": n}
        elif s["type"] == "monitor":
            bus_name = s["bus"] or ""
            bus_num = _MONITOR_BUS_NUMBERS.get(bus_name)
            if bus_num is None:
                raise ValueError(
                    f"P16 monitor slot references unknown bus {bus_name!r}. "
                    f"Known: {list(_MONITOR_BUS_NUMBERS)}"
                )
            io_out_a[a_key] = {"grp": "BUS", "in": (bus_num * 2) - 1}
        else:  # off
            io_out_a[a_key] = {"grp": "OFF", "in": 1}
