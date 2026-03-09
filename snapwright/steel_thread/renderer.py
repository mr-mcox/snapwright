"""Minimal channel-frame renderer for Phase 0 steel thread.

Takes a ChannelConfig (from YAML), starts from the Wing defaults for that
channel, applies the DSL overrides, and returns the rendered channel dict.

Throwaway: this gets replaced by the instrument-frame renderer in Phase 1.
"""

import copy

from snapwright.steel_thread.dsl import (
    ChannelConfig,
    DynamicsConfig,
    EqConfig,
    FiltersConfig,
    GateConfig,
)
from snapwright.wing.defaults import channel_defaults

# --- Send defaults ---
# Buses 1-12: POST (mix/FX buses)
# Buses 13-16: PRE (monitor buses) — Base.snap has POST here but all team snapshots use PRE
# MX sends: PRE + plink=True — Base.snap has POST/False, firmware difference
_BUS_SEND_OFF = {
    "on": False,
    "lvl": -144.0,
    "pon": False,
    "mode": "POST",
    "plink": False,
    "pan": 0,
}
_MON_SEND_OFF = {
    "on": False,
    "lvl": -144.0,
    "pon": False,
    "mode": "PRE",
    "plink": False,
    "pan": 0,
}
_MX_SEND_OFF = {
    "on": False,
    "lvl": -144.0,
    "pon": False,
    "mode": "PRE",
    "plink": True,
    "pan": 0,
}

_MIX_SEND_KEYS = [str(i) for i in range(1, 13)]  # buses 1-12
_MON_SEND_KEYS = [str(i) for i in range(13, 17)]  # buses 13-16 (monitors)
_MX_SEND_KEYS = [f"MX{i}" for i in range(1, 9)]
_ALL_SEND_KEYS = _MIX_SEND_KEYS + _MON_SEND_KEYS + _MX_SEND_KEYS


def _off_template(key: str) -> dict:
    if key.startswith("MX"):
        return _MX_SEND_OFF
    if key in _MON_SEND_KEYS:
        return _MON_SEND_OFF
    return _BUS_SEND_OFF


# --- Firmware-default patches ---
# Fields absent from Base.snap (older firmware) but present in all team snapshots.
_FLT_SLOPE_DEFAULTS = {"lcs": "24", "hcs": "12"}
_IN_SET_DELAY_DEFAULT = (
    0.100000001  # 0.1ms — identical across all 40 channels in every snapshot
)


# --- EQ band Wing keys (in order) ---
_EQ_BAND_KEYS = ["1", "2", "3", "4"]
_EQ_BAND_FREQ_DEFAULTS = [200.0, 600.0, 1500.0, 4000.0]


def render_channel(config: ChannelConfig) -> dict:
    """Render a ChannelConfig to a Wing channel dict.

    Starts from Base.snap defaults for this channel number, then applies
    only the fields specified in the DSL. Everything else stays as Base.snap.
    """
    ch = channel_defaults(config.channel)

    # --- Identity ---
    ch["name"] = config.name
    ch["col"] = config.color
    ch["icon"] = config.icon
    ch["mute"] = config.mute

    # --- Fader ---
    ch["fdr"] = config.fader

    # --- Input routing ---
    conn = config.input.to_wing_conn()
    ch["in"]["conn"].update(conn)

    # --- Firmware patches (Base.snap predates these) ---
    ch["in"]["set"]["dly"] = _IN_SET_DELAY_DEFAULT
    for field, value in _FLT_SLOPE_DEFAULTS.items():
        if field not in ch["flt"]:
            ch["flt"][field] = value

    # --- Input filters ---
    _apply_filters(ch, config.filters)

    # --- EQ ---
    _apply_eq(ch, config.eq)

    # --- Dynamics ---
    _apply_dynamics(ch, config.dynamics)

    # --- Gate ---
    _apply_gate(ch, config.gate)

    # --- Sends ---
    sends = {}
    for key in _ALL_SEND_KEYS:
        off_template = _off_template(key)
        if key in config.sends:
            s = config.sends[key]
            sends[key] = {
                "on": s.on,
                "lvl": s.level,
                "pon": off_template["pon"],
                "mode": s.mode,
                "plink": off_template["plink"],
                "pan": off_template["pan"],
            }
        else:
            sends[key] = copy.deepcopy(off_template)
    ch["send"] = sends

    return ch


def _apply_filters(ch: dict, filters: FiltersConfig) -> None:
    ch["flt"]["lc"] = filters.hpf_on
    ch["flt"]["lcf"] = filters.hpf_freq
    ch["flt"]["hc"] = filters.lpf_on
    ch["flt"]["hcf"] = filters.lpf_freq
    ch["flt"]["tf"] = filters.tilt_on


def _apply_eq(ch: dict, eq: EqConfig) -> None:
    ch["eq"]["on"] = eq.on
    ch["eq"]["mdl"] = eq.model

    ch["eq"]["lg"] = eq.low_shelf.gain
    ch["eq"]["lf"] = eq.low_shelf.freq

    ch["eq"]["hg"] = eq.high_shelf.gain
    ch["eq"]["hf"] = eq.high_shelf.freq

    # Apply up to 4 bands; bands not in DSL list stay at Base.snap defaults
    for i, band_key in enumerate(_EQ_BAND_KEYS):
        if i < len(eq.bands):
            band = eq.bands[i]
            ch["eq"][f"{band_key}g"] = band.gain
            ch["eq"][f"{band_key}f"] = band.freq
            ch["eq"][f"{band_key}q"] = band.q


def _apply_dynamics(ch: dict, dyn: DynamicsConfig) -> None:
    if dyn.model == "ECL33":
        ch["dyn"] = {
            "on": dyn.on,
            "mdl": "ECL33",
            "mix": 100,
            "gain": 0,
            "lon": dyn.leveler.on,
            "lthr": dyn.leveler.threshold,
            "lrec": str(dyn.leveler.recovery),
            "lfast": dyn.leveler.fast,
            "con": dyn.compressor.on,
            "cthr": dyn.compressor.threshold,
            "ratio": dyn.compressor.ratio,
            "crec": str(dyn.compressor.recovery),
            "cfast": dyn.compressor.fast,
            "cgain": 0,
        }
    else:
        # Standard COMP model (Base.snap default shape)
        ch["dyn"]["on"] = dyn.on
        ch["dyn"]["mdl"] = dyn.model


def _apply_gate(ch: dict, gate: GateConfig) -> None:
    ch["gate"]["on"] = gate.on
    ch["gate"]["thr"] = gate.threshold
    ch["gate"]["range"] = gate.range
    ch["gate"]["att"] = gate.attack
    ch["gate"]["hld"] = gate.hold
    ch["gate"]["rel"] = gate.release
