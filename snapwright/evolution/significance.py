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


def _is_dynamics_ratio(path: str) -> bool:
    return path.startswith("dyn.") and path.endswith("ratio")


def _is_gate_threshold(path: str) -> bool:
    return path.startswith("gate.") and path.endswith("thr")


def _is_gate_range(path: str) -> bool:
    return path.startswith("gate.") and path.endswith("range")


def _is_fader(path: str) -> bool:
    return path == "fdr"


def _is_input_trim(path: str) -> bool:
    return path == "in.set.trim"


def _is_send_off_transition(old_f: float, new_f: float) -> bool:
    """True if either value is the -144 dB off sentinel."""
    return abs(old_f - _SEND_OFF) < 0.1 or abs(new_f - _SEND_OFF) < 0.1


# Flat threshold checks: (classifier, threshold_key).
# Frequency is handled separately (relative, not absolute delta).
# Send level is handled separately (off-sentinel short-circuit).
_THRESHOLD_CHECKS: list[tuple] = [
    (_is_fader, "fader_db"),
    (_is_eq_gain, "eq_gain_db"),
    (_is_dynamics_threshold, "dynamics_threshold_db"),
    (_is_dynamics_ratio, "dynamics_ratio"),
    (_is_gate_threshold, "gate_threshold_db"),
    (_is_gate_range, "gate_range_db"),
    (_is_input_trim, "input_trim_db"),
]


def _numeric_significant(path: str, old_f: float, new_f: float, delta: float) -> bool:
    """Threshold check for a known-numeric change."""
    if _is_send_level(path):
        if _is_send_off_transition(old_f, new_f):
            return True
        return delta >= THRESHOLDS["send_level_db"]

    if _is_frequency(path):
        ref = abs(old_f) if old_f != 0 else 1.0
        return (delta / ref) >= THRESHOLDS["freq_relative"]

    for is_match, key in _THRESHOLD_CHECKS:
        if is_match(path):
            return delta >= THRESHOLDS[key]

    return delta >= 2.0


def is_significant(path: str, old: Any, new: Any) -> bool:
    """Return True if the change at this Wing param path is worth surfacing.

    Handles booleans, strings (model names, modes), and numerics.
    Path is a dot-separated Wing JSON path within a channel, e.g. "eq.1g".
    """
    if old == new:
        return False

    # Boolean changes (on/off, mute) — always significant when they differ
    if isinstance(old, bool) or isinstance(new, bool):
        return old != new

    # String changes (model names, modes, source groups) — always significant
    if isinstance(old, str) or isinstance(new, str):
        return old != new

    # Numeric: delegate to threshold logic
    try:
        old_f, new_f = float(old), float(new)
    except (TypeError, ValueError):
        return old != new

    return _numeric_significant(path, old_f, new_f, abs(new_f - old_f))
