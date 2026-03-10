"""Render a DSL assembly to a Wing .snap dict.

Pipeline per channel:
  1. Start from channel_defaults() (Base.snap for that channel number)
  2. Apply firmware patches
  3. Apply identity (name, color, icon, mute, fader)
  4. Apply input routing
  5. Apply processing (filters, EQ, dynamics, gate)
  6. Apply sends (submix/FX buses POST, monitor buses PRE)

Key invariant: when a DSL specifies a model that differs from the Wing default
(STD / COMP / GATE), the corresponding dict is rebuilt from scratch so that
old-model params are not left behind — matching Wing's own behaviour.

Channels not listed in the assembly keep their Base.snap defaults + firmware patches.
"""

from __future__ import annotations

import copy
from pathlib import Path

from snapwright.dsl.infrastructure import get_p16_slots, patch_channel_firmware
from snapwright.dsl.loader import load_assembly, resolve_musician
from snapwright.dsl.schema import AssemblyDef
from snapwright.wing.defaults import channel_defaults, snap_template
from snapwright.wing.writer import save_snap

# ---------------------------------------------------------------------------
# Send key constants
# ---------------------------------------------------------------------------

_MIX_SEND_KEYS = [str(i) for i in range(1, 13)]  # buses 1-12  (POST default)
_MON_SEND_KEYS = [str(i) for i in range(13, 17)]  # buses 13-16 (PRE)
_MX_SEND_KEYS = [f"MX{i}" for i in range(1, 9)]  # personal monitors (PRE + plink)
_ALL_SEND_KEYS = _MIX_SEND_KEYS + _MON_SEND_KEYS + _MX_SEND_KEYS

_SEND_OFF_POST = {
    "on": False,
    "lvl": -144.0,
    "pon": False,
    "mode": "POST",
    "plink": False,
    "pan": 0,
}
_SEND_OFF_PRE = {
    "on": False,
    "lvl": -144.0,
    "pon": False,
    "mode": "PRE",
    "plink": False,
    "pan": 0,
}
_SEND_OFF_MX = {
    "on": False,
    "lvl": -144.0,
    "pon": False,
    "mode": "PRE",
    "plink": True,
    "pan": 0,
}

_FLT_SLOPE_DEFAULTS = {"lcs": "24", "hcs": "12"}
_IN_SET_DELAY_DEFAULT = 0.100000001

_SOURCE_GROUP_MAP = {
    "stage-box": "A",
    "local": "B",
    "usb": "C",
    "off": "OFF",
}

# Wing Base.snap default models — switching away from these triggers a dict rebuild
_DEFAULT_EQ_MODEL = "STD"
_DEFAULT_DYN_MODEL = "COMP"
_DEFAULT_GATE_MODEL = "GATE"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def render_assembly(
    assembly_path: str | Path,
    output_path: str | Path | None = None,
) -> dict:
    """Render a team assembly to a Wing snap dict.

    If output_path is given, also writes the .snap file.
    Returns the full snap dict.
    """
    assembly, dsl_root = load_assembly(assembly_path)
    snap = _render(assembly, dsl_root)

    if output_path is not None:
        save_snap(snap, output_path)


    return snap


# ---------------------------------------------------------------------------
# Internal rendering
# ---------------------------------------------------------------------------


def _render(assembly: AssemblyDef, dsl_root: Path) -> dict:
    snap = snap_template()

    # Build reverse map: logical bus name -> physical bus number (as string)
    bus_by_name: dict[str, str] = {
        name: str(num) for num, name in assembly.buses.items()
    }

    # Build musician-to-channel reverse map for the monitors offset pass
    musician_to_ch: dict[str, int] = {
        name: num for num, name in assembly.channels.items()
    }

    # Apply firmware patch to ALL channels (Base.snap predates these fields)
    for ch_dict in snap["ae_data"]["ch"].values():
        ch_dict["in"]["set"]["dly"] = _IN_SET_DELAY_DEFAULT
        for field, value in _FLT_SLOPE_DEFAULTS.items():
            if field not in ch_dict["flt"]:
                ch_dict["flt"][field] = value

    # Render each channel listed in the assembly
    for ch_num, musician_name in assembly.channels.items():
        entry = assembly.musicians[musician_name]
        resolved = resolve_musician(entry, dsl_root)

        ch = channel_defaults(ch_num)
        _patch_firmware(ch)
        _apply_identity(ch, resolved)
        _apply_input(ch, assembly, musician_name)
        _apply_processing(ch, resolved.get("processing", {}))
        _apply_sends(ch, bus_by_name, resolved.get("sends", {}))
        snap["ae_data"]["ch"][str(ch_num)] = ch

    # Apply assembly monitors as additive offsets on top of musician-file defaults.
    # If the musician has no default for a monitor (send is off), treat as absolute.
    for monitor_name, musician_offsets in assembly.monitors.items():
        bus_key = bus_by_name.get(monitor_name)
        if bus_key is None:
            known = list(assembly.buses.values())
            raise ValueError(
                f"Monitor {monitor_name!r} not found in buses: {known}"
            )
        for musician_name, offset in musician_offsets.items():
            ch_num = musician_to_ch.get(musician_name)
            if ch_num is None:
                continue
            send = snap["ae_data"]["ch"][str(ch_num)]["send"][bus_key]
            if send.get("on"):
                send["lvl"] = (
                    send["lvl"] + offset
                )  # additive: shift from musician default
            else:
                send["lvl"] = offset  # no default: treat as absolute
                send["on"] = True
                send["mode"] = "PRE"

    # Apply personal mixer assembly (MX sends + USR channel assignments)
    if assembly.personal_mixer is not None:
        import yaml as _yaml
        _infra_path = Path(__file__).parent.parent.parent / "data" / "dsl" / "infrastructure.yaml"
        _infra = _yaml.safe_load(_infra_path.read_text())
        _slots = get_p16_slots(_infra)
        _apply_personal_mixer_assembly(snap, assembly, musician_to_ch, _slots)

    return snap


def _patch_firmware(ch: dict) -> None:
    ch["in"]["set"]["dly"] = _IN_SET_DELAY_DEFAULT
    for field, value in _FLT_SLOPE_DEFAULTS.items():
        if field not in ch["flt"]:
            ch["flt"][field] = value
    # Firmware Q correction: Init.snap uses ~1.0, current firmware uses √2
    patch_channel_firmware(ch)


def _apply_identity_main(ch: dict, resolved: dict) -> None:
    if "main_on" in resolved:
        ch["main"]["1"]["on"] = resolved["main_on"]
    if "main_2_on" in resolved:
        ch["main"]["2"]["on"] = resolved["main_2_on"]
    if "main_2_lvl" in resolved:
        ch["main"]["2"]["lvl"] = resolved["main_2_lvl"]


def _apply_identity(ch: dict, resolved: dict) -> None:
    if "name" in resolved:
        ch["name"] = resolved["name"]
    if "color" in resolved:
        ch["col"] = resolved["color"]
    if "icon" in resolved:
        ch["icon"] = resolved["icon"]
    if "mute" in resolved:
        ch["mute"] = resolved["mute"]
    if "fader" in resolved:
        ch["fdr"] = resolved["fader"]
    if "trim" in resolved:
        ch["in"]["set"]["trim"] = resolved["trim"]
    _apply_identity_main(ch, resolved)
    if "preins" in resolved:
        ch["preins"]["ins"] = resolved["preins"]
        ch["preins"]["on"] = True
    if "ptap" in resolved:
        ch["ptap"] = str(resolved["ptap"])

def _apply_input(ch: dict, assembly: AssemblyDef, musician_name: str) -> None:
    assignment = assembly.inputs.get(musician_name)
    if assignment is None:
        return
    grp = _SOURCE_GROUP_MAP.get(assignment.source)
    if grp is None:
        raise ValueError(f"Unknown input source: {assignment.source!r}")
    ch["in"]["conn"]["grp"] = grp
    ch["in"]["conn"]["in"] = assignment.input
    ch["in"]["conn"]["altgrp"] = "OFF"
    ch["in"]["conn"]["altin"] = 1


def _apply_processing(ch: dict, processing: dict) -> None:
    if not processing:
        return
    if "filters" in processing:
        _apply_filters(ch, processing["filters"])
    if "eq" in processing:
        _apply_eq(ch, processing["eq"])
    if "dynamics" in processing:
        _apply_dynamics(ch, processing["dynamics"])
    if "gate" in processing:
        _apply_gate(ch, processing["gate"])


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

_FILTER_MAP = {
    "hpf_on": "lc",
    "hpf_freq": "lcf",
    "hpf_slope": "lcs",
    "lpf_on": "hc",
    "lpf_freq": "hcf",
    "tilt_on": "tf",
    "tilt": "tilt",
}


def _apply_filters(ch: dict, flt: dict) -> None:
    for dsl_key, wing_key in _FILTER_MAP.items():
        if flt.get(dsl_key) is not None:
            ch["flt"][wing_key] = flt[dsl_key]


# ---------------------------------------------------------------------------
# EQ
# ---------------------------------------------------------------------------

_DECLARED_EQ_KEYS = {"on", "model", "low_shelf", "bands", "high_shelf"}


def _apply_eq(ch: dict, eq: dict) -> None:
    model = eq.get("model")
    on = eq.get("on")

    if model is None or model == _DEFAULT_EQ_MODEL:
        # Same model as Base.snap — patch individual fields, keep defaults
        if on is not None:
            ch["eq"]["on"] = on
        if model is not None:
            ch["eq"]["mdl"] = model
        _apply_std_eq_fields(ch["eq"], eq)
        _apply_eq_extras(ch["eq"], eq)
    else:
        # Different model — rebuild from scratch (Wing drops old-model params)
        new_eq: dict = {"on": on if on is not None else False, "mdl": model, "mix": 100}
        _apply_std_eq_fields(new_eq, eq)
        _apply_eq_extras(new_eq, eq)
        ch["eq"] = new_eq


def _apply_eq_shelf(target: dict, shelf: dict, prefix: str) -> None:
    if shelf.get("gain") is not None:
        target[f"{prefix}g"] = shelf["gain"]
    if shelf.get("freq") is not None:
        target[f"{prefix}f"] = shelf["freq"]


def _apply_std_eq_fields(target: dict, eq: dict) -> None:
    """Write typed STD-model fields (low_shelf, bands, high_shelf)."""
    if eq.get("low_shelf"):
        _apply_eq_shelf(target, eq["low_shelf"], "l")
    if eq.get("bands"):
        for i, band in enumerate(eq["bands"][:4]):
            k = str(i + 1)
            if band.get("gain") is not None:
                target[f"{k}g"] = band["gain"]
            if band.get("freq") is not None:
                target[f"{k}f"] = band["freq"]
            if band.get("q") is not None:
                target[f"{k}q"] = band["q"]
    if eq.get("high_shelf"):
        _apply_eq_shelf(target, eq["high_shelf"], "h")

def _apply_eq_extras(target: dict, eq: dict) -> None:
    """Pass through any non-declared EQ keys (SOUL, PULSAR, E88 params)."""
    for k, v in eq.items():
        if k not in _DECLARED_EQ_KEYS and v is not None:
            target[k] = v


# ---------------------------------------------------------------------------
# Dynamics
# ---------------------------------------------------------------------------

_DECLARED_DYN_KEYS = {"on", "model", "leveler", "compressor"}


def _apply_ecl33_leveler(new_dyn: dict, lv: dict) -> None:
    new_dyn["lon"] = lv.get("on", False)
    new_dyn["lthr"] = lv.get("threshold", -10.0)
    new_dyn["lrec"] = str(int(lv.get("recovery", 50)))
    new_dyn["lfast"] = lv.get("fast", False)


def _apply_ecl33_compressor(new_dyn: dict, co: dict) -> None:
    new_dyn["con"] = co.get("on", False)
    new_dyn["cthr"] = co.get("threshold", -10.0)
    new_dyn["ratio"] = co.get("ratio", 3.0)
    new_dyn["crec"] = str(int(co.get("recovery", 100)))
    new_dyn["cfast"] = co.get("fast", False)


def _apply_dyn_extras(target: dict, dyn: dict) -> None:
    """Copy undeclared dynamics keys straight through."""
    for k, v in dyn.items():
        if k not in _DECLARED_DYN_KEYS and v is not None:
            target[k] = v


def _apply_dynamics(ch: dict, dyn: dict) -> None:
    model = dyn.get("model")
    on = dyn.get("on")

    if model == "ECL33":
        # Rebuild from scratch — ECL33 has a completely different shape
        new_dyn: dict = {
            "on": on if on is not None else False,
            "mdl": "ECL33",
            "mix": 100,
            "gain": 0,
            "cgain": 0,
        }
        if dyn.get("leveler"):
            _apply_ecl33_leveler(new_dyn, dyn["leveler"])
        if dyn.get("compressor"):
            _apply_ecl33_compressor(new_dyn, dyn["compressor"])
        ch["dyn"] = new_dyn
    elif model is None or model == _DEFAULT_DYN_MODEL:
        # Same model as Base.snap — patch individual fields
        if on is not None:
            ch["dyn"]["on"] = on
        if model is not None:
            ch["dyn"]["mdl"] = model
        _apply_dyn_extras(ch["dyn"], dyn)

    else:
        # Different model (LA, NSTR, 9000C, …) — rebuild from scratch
        new_dyn = {
            "on": on if on is not None else False,
            "mdl": model,
            "mix": 100,
            "gain": 0,
        }
        _apply_dyn_extras(new_dyn, dyn)
        ch["dyn"] = new_dyn

# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------

_TYPED_GATE_MAP = {
    "threshold": "thr",
    "range": "range",
    "attack": "att",
    "hold": "hld",
    "release": "rel",
    "ratio": "ratio",
}
_DECLARED_GATE_KEYS = {"on", "model"} | set(_TYPED_GATE_MAP.keys())


def _apply_typed_gate_params(target: dict, gate: dict) -> None:
    for dsl_key, wing_key in _TYPED_GATE_MAP.items():
        if gate.get(dsl_key) is not None:
            target[wing_key] = gate[dsl_key]


def _apply_gate_extras(target: dict, gate: dict) -> None:
    for k, v in gate.items():
        if k not in _DECLARED_GATE_KEYS and v is not None:
            target[k] = v


def _apply_gate(ch: dict, gate: dict) -> None:
    model = gate.get("model")
    on = gate.get("on")
    if model is None or model == _DEFAULT_GATE_MODEL:
        # Same model as Base.snap — patch individual fields
        if on is not None:
            ch["gate"]["on"] = on
        if model is not None:
            ch["gate"]["mdl"] = model
        _apply_typed_gate_params(ch["gate"], gate)
        _apply_gate_extras(ch["gate"], gate)
    else:
        # Different model (PSE, RIDE, 9000G, …) — rebuild from scratch
        new_gate: dict = {
            "on": on if on is not None else False,
            "mdl": model, "mix": 100, "gain": 0,
        }
        _apply_typed_gate_params(new_gate, gate)
        _apply_gate_extras(new_gate, gate)
        ch["gate"] = new_gate

# ---------------------------------------------------------------------------
# Sends
# ---------------------------------------------------------------------------


def _apply_sends(
    ch: dict,
    bus_by_name: dict[str, str],
    all_sends: dict[str, float],
) -> None:
    """Build the complete send dict for this channel from resolved sends.

    PRE mode is used for monitor buses (physical bus number >= 13).
    POST mode is used for submix/FX buses (physical bus number < 13).
    Logical names not found in bus_by_name are silently ignored (allows
    musician files to reference buses that only exist on some teams).
    """
    sends: dict[str, dict] = {}

    for key in _ALL_SEND_KEYS:
        if key.startswith("MX"):
            sends[key] = copy.deepcopy(_SEND_OFF_MX)
        elif key in _MON_SEND_KEYS:
            sends[key] = copy.deepcopy(_SEND_OFF_PRE)
        else:
            sends[key] = copy.deepcopy(_SEND_OFF_POST)
    for logical_name, level in all_sends.items():
        bus_key = bus_by_name.get(logical_name)
        if bus_key is None:
            continue  # silently skip — this bus isn't in this team's assembly
        is_monitor = int(bus_key) >= 13
        sends[bus_key]["on"] = True
        sends[bus_key]["lvl"] = level
        sends[bus_key]["mode"] = "PRE" if is_monitor else "POST"
    ch["send"] = sends


# ---------------------------------------------------------------------------
# Personal mixer assembly rendering
# ---------------------------------------------------------------------------


def _apply_personal_mixer_assembly(
    snap: dict,
    assembly: AssemblyDef,
    musician_to_ch: dict[str, int],
    slots: list[dict],
) -> None:
    """Write MX channel sends (groups) and USR source assignments (individuals).

    Called after channel rendering so send dicts already exist.
    Infrastructure has already written matrix names and io.out A.33-A.48.
    """
    ae = snap["ae_data"]
    pm = assembly.personal_mixer
    if pm is None:
        return

    for s in slots:
        if s["type"] == "group":
            _apply_group_slot(ae, pm, musician_to_ch, s)
        elif s["type"] == "individual":
            _apply_individual_slot(ae, pm, musician_to_ch, s)
        # monitor and off slots: io.out written by infrastructure, nothing more needed


def _apply_group_slot(
    ae: dict,
    pm,
    musician_to_ch: dict[str, int],
    slot: dict,
) -> None:
    """Write send.MX{n} on each musician channel assigned to this group slot."""
    label = slot["label"]
    mx_key = f"MX{slot['mx_num']}"
    assignments = (pm.groups or {}).get(label) or {}
    for musician_name, level in assignments.items():
        ch_num = musician_to_ch.get(musician_name)
        if ch_num is None:
            continue  # musician not on this team
        send = ae["ch"][str(ch_num)]["send"][mx_key]
        send["on"] = True
        send["lvl"] = float(level)
        # mode/plink already set to PRE/True by _apply_sends default


def _apply_individual_slot(
    ae: dict,
    pm,
    musician_to_ch: dict[str, int],
    slot: dict,
) -> None:
    """Write USR source channel assignment for this individual slot."""
    label = slot["label"]
    usr_key = str(slot["usr_num"])
    ind = (pm.individuals or {}).get(label)
    if ind is None:
        return  # not declared in assembly — stays OFF (infrastructure default)

    usr = ae["io"]["in"]["USR"][usr_key]
    if ind.musician is None:
        # Explicitly unassigned — leave grp=OFF, keep label
        usr["user"]["grp"] = "OFF"
        usr["user"]["in"] = 1
        return

    ch_num = musician_to_ch.get(ind.musician)
    if ch_num is None:
        return  # musician not on this team

    usr["user"] = {
        "grp": "CH",
        "in": ch_num,
        "tap": ind.tap,
        "lr": "L+R",
    }
