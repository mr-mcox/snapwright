"""Translate Wing JSON parameter paths into audio-meaningful labels and values.

Pure functions: no Wing snapshot loading, no significance logic.
Context (EQ/dynamics/gate model) is passed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from snapwright.evolution.significance import is_significant, _SEND_OFF

# ---------------------------------------------------------------------------
# Bus name map — only named buses are tracked; unnamed are vestigial
# ---------------------------------------------------------------------------

BUS_NAMES: dict[str, str] = {
    "1": "Drums sub",
    "2": "Rhythm/House sub",
    "3": "Rhythm/Stream sub",
    "4": "Melodic/House sub",
    "5": "Melodic/Stream sub",
    "6": "Vocals sub",
    "9": "Delay/Slap FX",
    "10": "Reverb/Medium FX",
    "11": "Reverb/Long FX",
    "12": "Back Vox bus",
    "13": "Monitor 1",
    "14": "Monitor 2",
    "15": "Monitor 3",
    "16": "Monitor 4",
}

# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class ParamLabel:
    section: str        # e.g. "EQ (STD)", "Dynamics (ECL33)", "Filter", "Send → Vocals sub"
    label: str          # e.g. "band 1 gain", "comp threshold", "HPF freq"
    old_fmt: str        # formatted old value, e.g. "+3.2 dB", "199 Hz", "STD"
    new_fmt: str        # formatted new value
    delta: float | None # signed numeric delta; None for non-numeric or sentinel transitions


# ---------------------------------------------------------------------------
# Value formatting
# ---------------------------------------------------------------------------

_DB_PATHS = {
    "fdr",
    "eq.lg", "eq.hg",
    "eq.1g", "eq.2g", "eq.3g", "eq.4g",
    "eq.lmg", "eq.hmg",
    "dyn.gain", "dyn.thr", "dyn.cthr", "dyn.lthr", "dyn.cgain",
    "gate.thr", "gate.range",
    "in.set.trim",
}

_FREQ_PATHS = {
    "flt.lcf", "flt.hcf",
    "eq.lf", "eq.hf",
    "eq.1f", "eq.2f", "eq.3f", "eq.4f",
    "eq.lmf", "eq.hmf", "eq.lmf3", "eq.hmf3",
}


def _is_db_path(path: str) -> bool:
    if path in _DB_PATHS:
        return True
    # Send levels
    parts = path.split(".")
    return len(parts) == 3 and parts[0] == "send" and parts[2] == "lvl"


def _is_freq_path(path: str) -> bool:
    return path in _FREQ_PATHS


def _fmt(value: Any, path: str) -> str:
    if isinstance(value, bool):
        return "on" if value else "off"
    if isinstance(value, float):
        if _is_db_path(path):
            return f"{value:+.1f} dB"
        if _is_freq_path(path):
            return f"{value:,.0f} Hz" if abs(value) >= 1000 else f"{value:.0f} Hz"
        return f"{value:.3g}"
    return str(value)


# ---------------------------------------------------------------------------
# EQ label helpers
# ---------------------------------------------------------------------------

_STD_BAND_LABELS = {
    "l": "low shelf", "1": "band 1", "2": "band 2",
    "3": "band 3", "4": "band 4", "h": "high shelf",
}

_4BAND_LABELS = {
    "l": "low shelf", "lm": "lo-mid", "hm": "hi-mid", "h": "high shelf",
}

_EQ_SUFFIX_LABELS = {
    "g": "gain", "f": "freq", "q": "Q",
    "t": "type", "eq": "shelf type", "f3": "freq (octave)",
}


def _eq_label(key: str, model: str) -> str:
    bands = _4BAND_LABELS if model in ("SOUL", "E88") else _STD_BAND_LABELS
    for band_key, band_label in bands.items():
        for sfx, sfx_label in _EQ_SUFFIX_LABELS.items():
            if key == f"{band_key}{sfx}":
                return f"{band_label} {sfx_label}"
    return key


# ---------------------------------------------------------------------------
# Dynamics and gate label helpers
# ---------------------------------------------------------------------------

_DYN_COMMON = {
    "on": "on", "mix": "mix", "gain": "output gain",
    "thr": "threshold", "ratio": "ratio",
    "att": "attack", "rel": "release", "hld": "hold",
    "knee": "knee", "det": "detection", "env": "envelope",
    "auto": "auto release", "fast": "fast mode",
    "peak": "peak mode", "mode": "mode",
}

_DYN_MODEL_LABELS: dict[str, dict[str, str]] = {
    "ECL33": {
        "lon": "leveler on", "lthr": "leveler threshold",
        "lrec": "leveler recovery", "lfast": "leveler fast",
        "con": "comp on", "cthr": "comp threshold",
        "crec": "comp recovery", "cfast": "comp fast", "cgain": "comp gain",
    },
    "LA": {"ingain": "gain", "peak": "peak reduction"},
    "NSTR": {"in": "input gain", "out": "output gain"},
}

_GATE_COMMON = {
    "on": "on", "thr": "threshold", "range": "range",
    "att": "attack", "hld": "hold", "rel": "release",
    "acc": "accuracy", "ratio": "ratio",
    "fast": "fast mode", "mode": "mode", "peak": "peak mode",
}

_GATE_MODEL_LABELS: dict[str, dict[str, str]] = {
    "PSE":  {"depth": "depth"},
    "RIDE": {"tgt": "target", "spd": "speed"},
}


def _dyn_label(key: str, model: str) -> str:
    model_extras = _DYN_MODEL_LABELS.get(model, {})
    return model_extras.get(key) or _DYN_COMMON.get(key, key)


def _gate_label(key: str, model: str) -> str:
    model_extras = _GATE_MODEL_LABELS.get(model, {})
    return model_extras.get(key) or _GATE_COMMON.get(key, key)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def translate(path: str, old: Any, new: Any, context: dict) -> ParamLabel:
    """Translate a Wing param path and values into a ParamLabel.

    context keys:
        eq_model   — e.g. "STD", "SOUL"
        dyn_model  — e.g. "COMP", "ECL33", "LA"
        gate_model — e.g. "GATE", "PSE", "RIDE"
    """
    eq_model   = context.get("eq_model", "STD")
    dyn_model  = context.get("dyn_model", "COMP")
    gate_model = context.get("gate_model", "GATE")

    old_fmt = _fmt(old, path)
    new_fmt = _fmt(new, path)

    if isinstance(old, bool) or isinstance(new, bool):
        delta: float | None = None
    else:
        try:
            delta = float(new) - float(old)
        except (TypeError, ValueError):
            delta = None

    # --- Fader ---
    if path == "fdr":
        return ParamLabel("Fader", "level", old_fmt, new_fmt, delta)

    # --- Mute ---
    if path == "mute":
        return ParamLabel("Mute", "mute", old_fmt, new_fmt, None)

    # --- Filters ---
    if path.startswith("flt."):
        key = path[4:]
        label_map = {
            "lc": "HPF on", "lcf": "HPF freq", "lcs": "HPF slope",
            "hc": "LPF on", "hcf": "LPF freq", "hcs": "LPF slope",
            "tf": "tilt on", "tilt": "tilt gain", "mdl": "tilt model",
        }
        return ParamLabel("Filter", label_map.get(key, key), old_fmt, new_fmt, delta)

    # --- EQ ---
    if path.startswith("eq."):
        key = path[3:]
        if key == "mdl":
            return ParamLabel("EQ", "model", old_fmt, new_fmt, None)
        if key in ("on", "mix"):
            label = key
            section = "EQ"
        else:
            label = _eq_label(key, eq_model)
            section = f"EQ ({eq_model})"
        return ParamLabel(section, label, old_fmt, new_fmt, delta)

    # --- Dynamics ---
    if path.startswith("dyn."):
        key = path[4:]
        if key == "mdl":
            return ParamLabel("Dynamics", "model", old_fmt, new_fmt, None)
        label = _dyn_label(key, dyn_model)
        section = "Dynamics" if key in ("on", "mix") else f"Dynamics ({dyn_model})"
        return ParamLabel(section, label, old_fmt, new_fmt, delta)

    # --- Gate ---
    if path.startswith("gate."):
        key = path[5:]
        if key == "mdl":
            return ParamLabel("Gate", "model", old_fmt, new_fmt, None)
        label = _gate_label(key, gate_model)
        section = "Gate" if key == "on" else f"Gate ({gate_model})"
        return ParamLabel(section, label, old_fmt, new_fmt, delta)

    # --- Sends ---
    if path.startswith("send."):
        parts = path.split(".")
        bus_num = parts[1] if len(parts) > 1 else "?"
        param   = parts[2] if len(parts) > 2 else "?"
        bus_name = BUS_NAMES.get(bus_num, f"bus {bus_num}")
        param_labels = {"on": "on", "lvl": "level", "mode": "mode", "pan": "pan"}
        label = param_labels.get(param, param)

        # Suppress delta when crossing the -144 off sentinel — the swing is noise
        send_delta = delta
        if param == "lvl" and delta is not None:
            try:
                if abs(float(old) - _SEND_OFF) < 0.1 or abs(float(new) - _SEND_OFF) < 0.1:
                    send_delta = None
            except (TypeError, ValueError):
                pass

        return ParamLabel(f"Send → {bus_name}", label, old_fmt, new_fmt, send_delta)

    # --- Input ---
    if path.startswith("in."):
        key = path.split(".")[-1]
        label_map = {
            "grp": "source group", "in": "input number",
            "trim": "trim", "inv": "phase invert",
        }
        return ParamLabel("Input", label_map.get(key, key), old_fmt, new_fmt, delta)

    # --- Fallback ---
    return ParamLabel("Other", path, old_fmt, new_fmt, delta)
