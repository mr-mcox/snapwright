"""Minimal channel-frame renderer for Phase 0 steel thread.

Takes a ChannelConfig (from YAML), starts from the Wing defaults for that
channel, applies the DSL overrides, and returns the rendered channel dict.

Throwaway: this gets replaced by the instrument-frame renderer in Phase 1.
"""

import copy
from snapwright.steel_thread.dsl import ChannelConfig
from snapwright.wing.defaults import channel_defaults

# Default send state for bus sends not listed in the DSL.
# Buses 1-12: POST (mix/FX buses)
# Buses 13-16: PRE (monitor buses) — Base.snap has POST here but all team snapshots use PRE
# MX sends: PRE + plink=True — Base.snap has POST/False, firmware difference
_BUS_SEND_OFF = {"on": False, "lvl": -144.0, "pon": False, "mode": "POST", "plink": False, "pan": 0}
_MON_SEND_OFF = {"on": False, "lvl": -144.0, "pon": False, "mode": "PRE",  "plink": False, "pan": 0}
_MX_SEND_OFF  = {"on": False, "lvl": -144.0, "pon": False, "mode": "PRE",  "plink": True,  "pan": 0}

_MIX_SEND_KEYS = [str(i) for i in range(1, 13)]   # buses 1-12
_MON_SEND_KEYS = [str(i) for i in range(13, 17)]   # buses 13-16 (monitors)
_MX_SEND_KEYS  = [f"MX{i}" for i in range(1, 9)]
_ALL_SEND_KEYS = _MIX_SEND_KEYS + _MON_SEND_KEYS + _MX_SEND_KEYS


def _off_template(key: str) -> dict:
    if key.startswith("MX"):
        return _MX_SEND_OFF
    if key in _MON_SEND_KEYS:
        return _MON_SEND_OFF
    return _BUS_SEND_OFF

# Filter slope fields absent from Base.snap (older firmware); present in all team snaps.
# Values are strings in the Wing JSON (e.g. "24", "12").
_FLT_SLOPE_DEFAULTS = {"lcs": "24", "hcs": "12"}


def render_channel(config: ChannelConfig) -> dict:
    """Render a ChannelConfig to a Wing channel dict.

    Starts from Base.snap defaults for this channel number, then applies
    only the fields specified in the DSL. Everything else stays as Base.snap.
    """
    ch = channel_defaults(config.channel)

    # Identity
    ch["name"] = config.name
    ch["col"] = config.color
    ch["icon"] = config.icon
    ch["mute"] = config.mute

    # Fader
    ch["fdr"] = config.fader

    # Input routing
    conn = config.input.to_wing_conn()
    ch["in"]["conn"].update(conn)

    # Sends — build full send dict from DSL; omitted sends are off at -144.
    # Bus sends default POST/plink=False; MX sends default PRE/plink=True.
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

    # Patch filter slope fields absent from Base.snap
    for field, value in _FLT_SLOPE_DEFAULTS.items():
        if field not in ch["flt"]:
            ch["flt"][field] = value

    return ch
