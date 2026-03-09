"""Significance thresholds for Wing parameter changes.

A change is significant if it's large enough to be worth surfacing in an
evolution report. Thresholds are defined here as a first-class policy —
readable as documentation, testable in isolation, not scattered across
translation or diffing logic.
"""

from __future__ import annotations

from typing import Any

# Wing's sentinel value for "send is off"
_SEND_OFF = -144.0

# Thresholds by parameter category (exposed for tests)
THRESHOLDS = {
    "fader_db": 2.0,
    "send_level_db": 2.0,
    "eq_gain_db": 1.5,
    "freq_relative": 0.10,  # 10% relative shift
    "dynamics_threshold_db": 2.0,
    "dynamics_ratio": 0.5,
    "gate_threshold_db": 2.0,
    "gate_range_db": 3.0,
    "input_trim_db": 2.0,
}


def is_significant(path: str, old: Any, new: Any) -> bool:
    """Return True if the change at this Wing param path is worth surfacing.

    Handles booleans, strings (model names, modes), and numerics.
    Path is a dot-separated Wing JSON path within a channel, e.g. "eq.1g".
    """
    # No change at all — never significant
    if old == new:
        return False

    # Boolean changes (on/off, mute) — always significant when they differ
    if isinstance(old, bool) or isinstance(new, bool):
        return old != new

    # String changes (model names, modes, source groups) — always significant
    if isinstance(old, str) or isinstance(new, str):
        return old != new

    # Numeric: compute absolute delta
    try:
        old_f, new_f = float(old), float(new)
    except (TypeError, ValueError):
        return old != new

    delta = abs(new_f - old_f)

    # --- Fader ---
    if path == "fdr":
        return delta >= THRESHOLDS["fader_db"]

    # --- Send level ---
    # Transitions involving -144 (off sentinel) are significant if the level
    # change itself would be (≥2 dB). Since the delta is always huge when
    # crossing -144, check the other value is meaningfully non-silent.
    if _is_send_level(path):
        if abs(old_f - _SEND_OFF) < 0.1 or abs(new_f - _SEND_OFF) < 0.1:
            return True  # any transition from/to off is significant
        return delta >= THRESHOLDS["send_level_db"]

    # --- EQ gain ---
    if _is_eq_gain(path):
        return delta >= THRESHOLDS["eq_gain_db"]

    # --- Frequency (EQ bands, HPF, LPF) ---
    if _is_frequency(path):
        ref = abs(old_f) if old_f != 0 else 1.0
        return (delta / ref) >= THRESHOLDS["freq_relative"]

    # --- Dynamics threshold ---
    if _is_dynamics_threshold(path):
        return delta >= THRESHOLDS["dynamics_threshold_db"]

    # --- Dynamics ratio ---
    if path.endswith("ratio") and path.startswith("dyn."):
        return delta >= THRESHOLDS["dynamics_ratio"]

    # --- Gate threshold ---
    if path.startswith("gate.") and path.endswith("thr"):
        return delta >= THRESHOLDS["gate_threshold_db"]

    # --- Gate range ---
    if path.startswith("gate.") and path.endswith("range"):
        return delta >= THRESHOLDS["gate_range_db"]

    # --- Input trim ---
    if path == "in.set.trim":
        return delta >= THRESHOLDS["input_trim_db"]

    # Default: surface if delta >= 2 units
    return delta >= 2.0


# ---------------------------------------------------------------------------
# Path classifiers
# ---------------------------------------------------------------------------


def _is_send_level(path: str) -> bool:
    parts = path.split(".")
    return len(parts) == 3 and parts[0] == "send" and parts[2] == "lvl"


def _is_eq_gain(path: str) -> bool:
    if not path.startswith("eq."):
        return False
    key = path[3:]
    # STD: lg, 1g, 2g, 3g, 4g, hg
    # SOUL/E88: lmg, hmg (also lg, hg)
    return key.endswith("g") and key != "mdl"


def _is_frequency(path: str) -> bool:
    if path in ("flt.lcf", "flt.hcf"):
        return True
    if path.startswith("eq."):
        key = path[3:]
        # STD: lf, 1f, 2f, 3f, 4f, hf
        # SOUL/E88: lmf, hmf, lmf3, hmf3
        return key.endswith("f") or key.endswith("f3")
    return False


def _is_dynamics_threshold(path: str) -> bool:
    if not path.startswith("dyn."):
        return False
    key = path[4:]
    return key in ("thr", "cthr", "lthr")
