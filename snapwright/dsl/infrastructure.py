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
    By default skips hq (high-shelf Q): real-world bus/main snapshots keep hq=0.997970223.
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

    Covers all buses, mains, cfg.mon, and all channels.
    """
    ae = snap["ae_data"]

    # Buses 1-16 — patch parametric EQ Q and dynsc.q globally.
    # Bus 8 is the exception (never configured); infrastructure.yaml resets it.
    for bus in ae.get("bus", {}).values():
        _patch_eq_q(bus.get("eq", {}))
        _patch_dynsc_q(bus.get("dynsc", {}))

    # Main outputs 1-3 — patch parametric EQ Q and dynsc.q
    for main in ae.get("main", {}).values():
        _patch_eq_q(main.get("eq", {}))
        _patch_dynsc_q(main.get("dynsc", {}))

    # cfg.mon monitoring EQ — uses 1.995881796 as init Q (same as dynsc), not 0.997970223
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
            result[str(k) if isinstance(k, (int, float)) and not isinstance(k, bool) else k] = (
                _normalize_yaml_keys(v)
            )
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
    _apply_dca(ae, infra.get("dca", {}))
    _apply_mgrp(ae, infra.get("mgrp", {}))
    _apply_cfg(ae, infra.get("cfg", {}))
    _apply_channels(ae, infra.get("channels", {}))


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


def _apply_bus_dynamics(bus: dict, dyn_config: dict) -> None:
    """Apply dynamics config to a bus dict.
    field contamination. COMP patches in-place.
    When switching to SBUS, also patches dynsc.q to sqrt2 — Wing applies this
    when configuring a bus with SBUS dynamics.
    """
    model = dyn_config.get("mdl")
    if model is None:
        return
    if model != bus.get("dyn", {}).get("mdl"):
        # Model change — rebuild from scratch to avoid old-model field contamination
        bus["dyn"] = {"mdl": model, "mix": 100}
        if model == "SBUS":
            # SBUS configuration also updates dynsc.q to sqrt2 — Wing does this
            # when you configure a bus with SBUS dynamics
            bus.setdefault("dynsc", {})["q"] = _DYNSC_Q_PATCHED
    bus["dyn"].update(dyn_config)


def _apply_bus_inserts(bus: dict, preins: dict | None, postins: dict | None) -> None:
    if preins:
        bus["preins"].update(preins)
    if postins:
        bus["postins"].update(postins)


def _apply_buses(ae: dict, buses_config: dict) -> None:
    for bus_str, bus_cfg in buses_config.items():
        bus_key = str(bus_str)
        bus = ae["bus"][bus_key]

        for yaml_key, snap_key in _BUS_FIELD_MAP.items():
            if yaml_key in bus_cfg:
                bus[snap_key] = bus_cfg[yaml_key]

        if "dyn" in bus_cfg:
            _apply_bus_dynamics(bus, bus_cfg["dyn"])
        if "eq" in bus_cfg:
            bus["eq"].update(bus_cfg["eq"])
        if "dynsc" in bus_cfg:
            bus.setdefault("dynsc", {}).update(bus_cfg["dynsc"])
        if "preins" in bus_cfg:
            bus["preins"].update(bus_cfg["preins"])
        if "postins" in bus_cfg:
            bus["postins"].update(bus_cfg["postins"])
        if "main" in bus_cfg:
            for out_key, out_cfg in bus_cfg["main"].items():
                bus["main"][str(out_key)].update(out_cfg)


# ---------------------------------------------------------------------------
# Main outputs
# ---------------------------------------------------------------------------

def _apply_main_dynamics(main: dict, dyn_config: dict) -> None:
    model = dyn_config.get("mdl")
    if model is None:
        return
    if model != main.get("dyn", {}).get("mdl"):
        main["dyn"] = {"mdl": model, "mix": 100}
    main["dyn"].update(dyn_config)


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
            main["eq"].update(out_cfg["eq"])

        if "in" in out_cfg:
            _deep_update(main["in"], out_cfg["in"])

        if "preins" in out_cfg:
            main["preins"].update(out_cfg["preins"])
        if "postins" in out_cfg:
            main["postins"].update(out_cfg["postins"])


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

_SEND_OFF_POST = {"on": False, "lvl": -144.0, "pon": False, "mode": "POST", "plink": False, "pan": 0}
_SEND_OFF_PRE = {"on": False, "lvl": -144.0, "pon": False, "mode": "PRE", "plink": False, "pan": 0}
_SEND_OFF_MX = {"on": False, "lvl": -144.0, "pon": False, "mode": "PRE", "plink": True, "pan": 0}


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


def _apply_channels(ae: dict, channels_config: dict) -> None:
    """Apply infrastructure channel configs (ch37-40)."""
    for ch_str, ch_cfg in channels_config.items():
        ch_key = str(ch_str)
        ch = ae["ch"][ch_key]

        # Identity
        if "name" in ch_cfg:
            ch["name"] = ch_cfg["name"]
        if "col" in ch_cfg:
            ch["col"] = ch_cfg["col"]
        if "icon" in ch_cfg:
            ch["icon"] = ch_cfg["icon"]
        if "mute" in ch_cfg:
            ch["mute"] = ch_cfg["mute"]
        if "fdr" in ch_cfg:
            ch["fdr"] = ch_cfg["fdr"]
        if "led" in ch_cfg:
            ch["led"] = ch_cfg["led"]
        if "clink" in ch_cfg:
            ch["clink"] = ch_cfg["clink"]
        if "ptap" in ch_cfg:
            ch["ptap"] = str(ch_cfg["ptap"])

        # Input routing
        if "in" in ch_cfg:
            _deep_update(ch["in"], ch_cfg["in"])

        # Processing
        if "eq" in ch_cfg:
            ch["eq"].update(ch_cfg["eq"])
        if "dyn" in ch_cfg:
            ch["dyn"].update(ch_cfg["dyn"])
        if "gate" in ch_cfg:
            ch["gate"].update(ch_cfg["gate"])
        if "flt" in ch_cfg:
            ch["flt"].update(ch_cfg["flt"])

        # Inserts
        if "preins" in ch_cfg:
            ch["preins"].update(ch_cfg["preins"])
        if "postins" in ch_cfg:
            ch["postins"].update(ch_cfg["postins"])

        # Main routing
        if "main" in ch_cfg:
            for out_key, out_cfg in ch_cfg["main"].items():
                ch["main"][str(out_key)].update(out_cfg)

        # Sends — build complete send dict
        if "send" in ch_cfg:
            ch["send"] = _build_infra_channel_sends(ch_cfg["send"])


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
