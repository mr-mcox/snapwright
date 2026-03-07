"""Compare two Wing snapshots and produce structured, audio-meaningful channel diffs."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from snapwright.wing.parser import load_snap
from snapwright.evolution.translate import ParamLabel, translate


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ParamChange:
    path: str           # Wing JSON path within the channel, e.g. "eq.1g"
    label: ParamLabel


@dataclass
class ChannelDiff:
    number: int
    name: str
    changes: list[ParamChange] = field(default_factory=list)

    @property
    def significant_changes(self) -> list[ParamChange]:
        return [c for c in self.changes if c.label.significant]


@dataclass
class SnapshotDiff:
    name: str               # display name (filename stem)
    date: str | None        # parsed from filename, e.g. "2025-08-24"
    channel_diffs: list[ChannelDiff] = field(default_factory=list)

    @property
    def significant_channel_diffs(self) -> list[ChannelDiff]:
        return [cd for cd in self.channel_diffs if cd.significant_changes]


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def _parse_date(filename: str) -> str | None:
    m = _DATE_RE.search(filename)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Channel-level flattening
# ---------------------------------------------------------------------------

_TRACKED_SECTIONS = ("fdr", "mute", "flt", "eq", "dyn", "gate", "send", "in")

# Send sub-keys worth tracking (skip plink, pon, pan — rarely adjusted)
_SEND_TRACKED = {"on", "lvl", "mode"}


def _flatten_channel(ch: dict) -> dict[str, Any]:
    """Flatten a channel dict into a path→value mapping for tracked params."""
    out: dict[str, Any] = {}

    # Fader and mute — top-level scalars
    for key in ("fdr", "mute"):
        if key in ch:
            out[key] = ch[key]

    # Filters
    for k, v in ch.get("flt", {}).items():
        out[f"flt.{k}"] = v

    # EQ
    for k, v in ch.get("eq", {}).items():
        out[f"eq.{k}"] = v

    # Dynamics
    for k, v in ch.get("dyn", {}).items():
        out[f"dyn.{k}"] = v

    # Gate
    for k, v in ch.get("gate", {}).items():
        out[f"gate.{k}"] = v

    # Sends — only tracked sub-keys, only named buses (skip vestigial unlabeled buses)
    from snapwright.evolution.translate import BUS_NAMES
    for bus_num, send in ch.get("send", {}).items():
        if not bus_num.isdigit():
            continue
        if bus_num not in BUS_NAMES:
            continue  # skip unnamed/vestigial buses (e.g. bus 7, 8)
        for sub in _SEND_TRACKED:
            if sub in send:
                out[f"send.{bus_num}.{sub}"] = send[sub]

    # Input — just the parts that get adjusted in practice
    for k, v in ch.get("in", {}).get("conn", {}).items():
        out[f"in.conn.{k}"] = v
    for k, v in ch.get("in", {}).get("set", {}).items():
        if k in ("trim", "inv"):
            out[f"in.set.{k}"] = v

    return out


def _context_for(ch: dict) -> dict:
    return {
        "eq_model": ch.get("eq", {}).get("mdl", "STD"),
        "dyn_model": ch.get("dyn", {}).get("mdl", "COMP"),
        "gate_model": ch.get("gate", {}).get("mdl", "GATE"),
    }


# ---------------------------------------------------------------------------
# Numeric near-equality (reuse Phase 0 tolerance: 3 sig figs)
# ---------------------------------------------------------------------------

def _nearly_equal(a: Any, b: Any) -> bool:
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        return a == b
    if isinstance(a, bool):
        return a == b
    if isinstance(a, (int, float)):
        fa, fb = float(a), float(b)
        if fa == fb:
            return True
        mag = max(abs(fa), abs(fb))
        if mag == 0:
            return True
        return abs(fa - fb) / mag < 1e-3   # 3 sig figs
    return a == b


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def diff_snapshots(base_path: Path | str, target_path: Path | str) -> SnapshotDiff:
    """Compare target snapshot against base. Returns all changes (significant and minor)."""
    base_path = Path(base_path)
    target_path = Path(target_path)

    base = load_snap(base_path)
    target = load_snap(target_path)

    name = target_path.stem
    date = _parse_date(target_path.name)

    base_channels = base["ae_data"]["ch"]
    target_channels = target["ae_data"]["ch"]

    snap_diff = SnapshotDiff(name=name, date=date)

    for ch_num_str in sorted(target_channels.keys(), key=lambda x: int(x)):
        base_ch = base_channels.get(ch_num_str, {})
        target_ch = target_channels[ch_num_str]

        # Use target channel name; skip unnamed channels entirely
        ch_name = target_ch.get("name", "").strip()
        if not ch_name:
            continue

        ctx = _context_for(target_ch)

        base_flat = _flatten_channel(base_ch)
        target_flat = _flatten_channel(target_ch)

        all_paths = sorted(set(base_flat) | set(target_flat))
        ch_diff = ChannelDiff(number=int(ch_num_str), name=ch_name)

        for path in all_paths:
            old_val = base_flat.get(path)
            new_val = target_flat.get(path)

            if old_val is None or new_val is None:
                continue  # param appeared/disappeared — skip (model change handles this)

            if _nearly_equal(old_val, new_val):
                continue

            label = translate(path, old_val, new_val, ctx)
            ch_diff.changes.append(ParamChange(path=path, label=label))

        if ch_diff.changes:
            snap_diff.channel_diffs.append(ch_diff)

    return snap_diff
