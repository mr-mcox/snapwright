"""Translate Wing JSON parameter paths into audio-meaningful labels and values.

Covers the parameters actually present in James team snapshots. Unknown params
fall back to the raw key name so nothing is silently dropped.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# Bus send name map (from James.snap ae_data.bus names)
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
# EQ band labels per model
# ---------------------------------------------------------------------------

# STD: lo-shelf, 4 parametric bands, hi-shelf
_STD_BAND_LABELS: dict[str, str] = {
    "l": "low shelf", "1": "band 1", "2": "band 2",
    "3": "band 3", "4": "band 4", "h": "high shelf",
}

# SOUL / E88: lo, lo-mid, hi-mid, hi
_4BAND_LABELS: dict[str, str] = {
    "l": "low shelf", "lm": "lo-mid", "hm": "hi-mid", "h": "high shelf",
}

# PULSAR: different structure — translate keys directly
_PULSAR_LABELS: dict[str, str] = {
    "eq1": "section 1 on", "1lb": "lo boost", "1latt": "lo atten",
    "1lf": "lo freq", "1hw": "hi width", "1hb": "hi boost",
    "1hf": "hi freq", "1hatt": "hi atten", "1hattf": "hi atten freq",
    "eq5": "section 5 on", "5lb": "lo boost", "5lf": "lo freq",
    "5md": "mid depth", "5mf": "mid freq", "5hb": "hi boost", "5hf": "hi freq",
}


def _eq_label(key: str, model: str) -> str:
    """Translate an EQ parameter key to a human label given the model."""
    suffix_map = {"g": "gain", "f": "freq", "q": "Q", "t": "type", "eq": "shelf type"}

    if model == "PULSAR":
        return _PULSAR_LABELS.get(key, key)

    if model in ("SOUL", "E88"):
        for band_key, band_label in _4BAND_LABELS.items():
            for sfx, sfx_label in suffix_map.items():
                if key == f"{band_key}{sfx}":
                    return f"{band_label} {sfx_label}"
            # E88 extra: lt, ht (type)
            if key in (f"{band_key}t",):
                return f"{band_label} type"
        return key

    # STD (default)
    for band_key, band_label in _STD_BAND_LABELS.items():
        for sfx, sfx_label in suffix_map.items():
            if key == f"{band_key}{sfx}":
                return f"{band_label} {sfx_label}"
    return key


# ---------------------------------------------------------------------------
# Dynamics param labels per model
# ---------------------------------------------------------------------------

_DYN_COMMON: dict[str, str] = {
    "on": "on", "mix": "mix", "gain": "output gain",
    "thr": "threshold", "ratio": "ratio", "att": "attack",
    "rel": "release", "hld": "hold", "knee": "knee",
    "det": "detection", "env": "envelope", "auto": "auto release",
    "fast": "fast mode", "peak": "peak mode", "mode": "mode",
}

_DYN_MODEL_EXTRAS: dict[str, dict[str, str]] = {
    "ECL33": {
        "lon": "leveler on", "lthr": "leveler threshold",
        "lrec": "leveler recovery", "lfast": "leveler fast",
        "con": "comp on", "cthr": "comp threshold",
        "crec": "comp recovery", "cfast": "comp fast", "cgain": "comp gain",
    },
    "LA": {"ingain": "input gain"},
    "NSTR": {"in": "input gain", "out": "output gain"},
    "CMB": {},
    "9000C": {},
    "COMP": {},
}


def _dyn_label(key: str, model: str) -> str:
    extras = _DYN_MODEL_EXTRAS.get(model, {})
    if key in extras:
        return extras[key]
    return _DYN_COMMON.get(key, key)


# ---------------------------------------------------------------------------
# Gate param labels per model
# ---------------------------------------------------------------------------

_GATE_COMMON: dict[str, str] = {
    "on": "on", "thr": "threshold", "range": "range",
    "att": "attack", "hld": "hold", "rel": "release",
    "acc": "accuracy", "ratio": "ratio", "fast": "fast mode",
    "mode": "mode", "peak": "peak mode",
}

_GATE_MODEL_EXTRAS: dict[str, dict[str, str]] = {
    "PSE":   {"depth": "depth"},
    "RIDE":  {"tgt": "target", "spd": "speed"},
    "WARM":  {},
    "WAVE":  {},
    "9000G": {},
    "GATE":  {},
}


def _gate_label(key: str, model: str) -> str:
    extras = _GATE_MODEL_EXTRAS.get(model, {})
    if key in extras:
        return extras[key]
    return _GATE_COMMON.get(key, key)


# ---------------------------------------------------------------------------
# Value formatting
# ---------------------------------------------------------------------------

_FREQ_PATH_MARKERS = ("lcf", "hcf", "eq.lf", "eq.hf", "eq.1f", "eq.2f", "eq.3f", "eq.4f",
                       "eq.lmf", "eq.hmf", "eq.lmf3", "eq.hmf3",
                       "1lf", "1hf", "5lf", "5mf", "5hf",)
_DB_PATH_MARKERS = ("fdr", "lvl", ".thr", "lthr", "cthr", "cgain",
                    "eq.lg", "eq.hg", "eq.1g", "eq.2g", "eq.3g", "eq.4g",
                    "eq.lmg", "eq.hmg",
                    "dyn.gain", "gate.range", "in.set.trim")


def _fmt(value: Any, path: str) -> str:
    """Format a Wing value for display."""
    if isinstance(value, bool):
        return "on" if value else "off"
    if isinstance(value, float):
        # dB values
        if any(path.endswith(m) or m in path for m in _DB_PATH_MARKERS):
            return f"{value:+.1f} dB"
        # frequencies — use comma-formatted integer Hz
        if any(m in path for m in _FREQ_PATH_MARKERS):
            if abs(value) >= 1000:
                return f"{value:,.0f} Hz"
            return f"{value:.0f} Hz"
        return f"{value:.3g}"
    return str(value)


# ---------------------------------------------------------------------------
# Significance thresholds
# ---------------------------------------------------------------------------

def _is_significant(path: str, old: Any, new: Any) -> bool:
    """Return True if the change is worth surfacing in a report."""
    # Boolean changes (on/off, mute) always significant
    if isinstance(old, bool) or isinstance(new, bool):
        return old != new

    # Model changes always significant
    if path.endswith(".mdl"):
        return old != new

    # String changes (names, modes) always significant if they differ
    if isinstance(old, str) or isinstance(new, str):
        return old != new

    # Numeric: compute absolute delta
    try:
        delta = abs(float(new) - float(old))
    except (TypeError, ValueError):
        return old != new

    # Fader / send level: >= 2 dB
    if "fdr" in path or ("send" in path and "lvl" in path):
        return delta >= 2.0

    # EQ gain: >= 1.5 dB
    if any(p in path for p in ("eq.",)) and path.endswith(("g", "gain")):
        return delta >= 1.5

    # EQ / filter frequency: >= 10% relative change
    if path.endswith(("f", "lcf", "hcf")) or "freq" in path:
        ref = abs(float(old)) if float(old) != 0 else 1.0
        return (delta / ref) >= 0.10

    # Dynamics threshold: >= 2 dB
    if "thr" in path or "threshold" in path:
        return delta >= 2.0

    # Dynamics ratio: >= 0.5
    if path.endswith("ratio"):
        return delta >= 0.5

    # Dynamics / gate gain: >= 2 dB
    if path.endswith("gain") or path.endswith("cgain"):
        return delta >= 2.0

    # Gate range: >= 3 dB
    if path.endswith("range"):
        return delta >= 3.0

    # Input trim: >= 2 dB
    if "trim" in path:
        return delta >= 2.0

    # Default: surface if delta >= 2 units
    return delta >= 2.0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass
class ParamLabel:
    """Human-readable label and formatted values for a Wing parameter change."""
    section: str    # e.g. "EQ", "Dynamics", "Gate", "Fader", "Send", "Filter"
    label: str      # e.g. "band 2 gain"
    old_fmt: str
    new_fmt: str
    delta: float | None  # signed numeric delta; None for non-numeric
    significant: bool


def translate(path: str, old: Any, new: Any, context: dict) -> ParamLabel:
    """Translate a Wing param path + values into a ParamLabel.

    context: dict with optional keys:
        'eq_model'   — current channel's EQ model string
        'dyn_model'  — current channel's dynamics model string
        'gate_model' — current channel's gate model string
    """
    eq_model = context.get("eq_model", "STD")
    dyn_model = context.get("dyn_model", "COMP")
    gate_model = context.get("gate_model", "GATE")

    sig = _is_significant(path, old, new)

    try:
        delta = float(new) - float(old)
    except (TypeError, ValueError):
        delta = None

    # --- Fader ---
    if path == "fdr":
        return ParamLabel("Fader", "level", _fmt(old, path), _fmt(new, path), delta, sig)

    # --- Mute ---
    if path == "mute":
        return ParamLabel("Mute", "mute", _fmt(old, path), _fmt(new, path), None, sig)

    # --- Filters ---
    if path.startswith("flt."):
        key = path[4:]
        label_map = {
            "lc": "HPF on", "lcf": "HPF freq", "lcs": "HPF slope",
            "hc": "LPF on", "hcf": "LPF freq", "hcs": "LPF slope",
            "tf": "tilt on", "tilt": "tilt gain", "mdl": "tilt model",
        }
        label = label_map.get(key, key)
        return ParamLabel("Filter", label, _fmt(old, path), _fmt(new, path), delta, sig)

    # --- EQ ---
    if path.startswith("eq."):
        key = path[3:]
        if key == "on":
            label = "on"
        elif key == "mdl":
            label = "model"
        elif key == "mix":
            label = "mix"
        else:
            label = _eq_label(key, eq_model)
        section = f"EQ ({eq_model})" if key not in ("on", "mdl", "mix") else "EQ"
        return ParamLabel(section, label, _fmt(old, path), _fmt(new, path), delta, sig)

    # --- Dynamics ---
    if path.startswith("dyn."):
        key = path[4:]
        label = _dyn_label(key, dyn_model) if key != "mdl" else "model"
        section = f"Dynamics ({dyn_model})" if key not in ("on", "mdl", "mix") else "Dynamics"
        return ParamLabel(section, label, _fmt(old, path), _fmt(new, path), delta, sig)

    # --- Gate ---
    if path.startswith("gate."):
        key = path[5:]
        label = _gate_label(key, gate_model) if key != "mdl" else "model"
        section = f"Gate ({gate_model})" if key not in ("on", "mdl") else "Gate"
        return ParamLabel(section, label, _fmt(old, path), _fmt(new, path), delta, sig)

    # --- Sends ---
    if path.startswith("send."):
        parts = path.split(".")
        bus_num = parts[1] if len(parts) > 1 else "?"
        param = parts[2] if len(parts) > 2 else "?"
        bus_name = BUS_NAMES.get(bus_num, f"bus {bus_num}")
        param_labels = {"on": "on", "lvl": "level", "mode": "mode", "pan": "pan"}
        label = param_labels.get(param, param)
        # When a send level crosses -144 (the off sentinel), suppress the numeric delta —
        # the meaningful change is the on/off state, tracked separately.
        send_delta = delta
        if param == "lvl" and (abs(float(old) + 144) < 0.1 or abs(float(new) + 144) < 0.1):
            send_delta = None
        return ParamLabel(f"Send → {bus_name}", label, _fmt(old, path), _fmt(new, path), send_delta, sig)

    # --- Input ---
    if path.startswith("in."):
        key = path.split(".")[-1]
        label_map = {
            "grp": "source group", "in": "input number",
            "trim": "trim", "inv": "phase invert", "dly": "delay",
            "dlyon": "delay on", "bal": "balance",
        }
        label = label_map.get(key, key)
        return ParamLabel("Input", label, _fmt(old, path), _fmt(new, path), delta, sig)

    # --- Fallback ---
    return ParamLabel("Other", path, _fmt(old, path), _fmt(new, path), delta, sig)
