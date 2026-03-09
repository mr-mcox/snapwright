"""Diff two Wing snapshots at the channel level.

Pipeline: flatten channel → near-equality filter → significance filter → translate.
Snapshot-level diff aggregates channel diffs and filters unnamed channels.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from snapwright.evolution.significance import is_significant
from snapwright.evolution.translate import BUS_NAMES, ParamLabel, translate
from snapwright.wing.parser import load_snap

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ParamChange:
    path: str  # Wing JSON path within channel, e.g. "eq.1g"
    label: ParamLabel


@dataclass
class ChannelDiff:
    number: int
    name: str
    changes: list[ParamChange] = field(default_factory=list)

    @property
    def significant_changes(self) -> list[ParamChange]:
        return [c for c in self.changes if c.label is not None]


@dataclass
class SnapshotDiff:
    name: str
    date: str | None
    channel_diffs: list[ChannelDiff] = field(default_factory=list)

    @property
    def significant_channel_diffs(self) -> list[ChannelDiff]:
        return [cd for cd in self.channel_diffs if cd.significant_changes]


# ---------------------------------------------------------------------------
# Channel flattening
# ---------------------------------------------------------------------------

_SEND_TRACKED = {"on", "lvl", "mode"}


def _flatten_channel(ch: dict) -> dict[str, Any]:
    """Flatten a channel dict into path→value for tracked params only."""
    out: dict[str, Any] = {}

    for key in ("fdr", "mute"):
        if key in ch:
            out[key] = ch[key]

    for section in ("flt", "eq", "dyn", "gate"):
        for k, v in ch.get(section, {}).items():
            out[f"{section}.{k}"] = v

    for bus_num, send in ch.get("send", {}).items():
        if not bus_num.isdigit() or bus_num not in BUS_NAMES:
            continue
        for sub in _SEND_TRACKED:
            if sub in send:
                out[f"send.{bus_num}.{sub}"] = send[sub]

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
# Near-equality (3 significant figures — Wing float quantization tolerance)
# ---------------------------------------------------------------------------


def _nearly_equal(a: Any, b: Any) -> bool:
    if type(a) is bool or type(b) is bool:
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        fa, fb = float(a), float(b)
        if fa == fb:
            return True
        mag = max(abs(fa), abs(fb))
        return mag > 0 and abs(fa - fb) / mag < 1e-3
    return a == b


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def diff_channels(
    number: int,
    base_ch: dict,
    target_ch: dict,
) -> ChannelDiff:
    """Compare two channel dicts. Returns significant changes only."""
    name = target_ch.get("name", "").strip()
    ctx = _context_for(target_ch)

    base_flat = _flatten_channel(base_ch)
    target_flat = _flatten_channel(target_ch)

    result = ChannelDiff(number=number, name=name)

    for path in sorted(set(base_flat) | set(target_flat)):
        old_val = base_flat.get(path)
        new_val = target_flat.get(path)

        if old_val is None or new_val is None:
            continue
        if _nearly_equal(old_val, new_val):
            continue
        if not is_significant(path, old_val, new_val):
            continue

        label = translate(path, old_val, new_val, ctx)
        result.changes.append(ParamChange(path=path, label=label))

    return result


def diff_snapshots(
    base: dict,
    target: dict,
    name: str,
    date: str | None,
) -> SnapshotDiff:
    """Diff all named channels between two loaded snap dicts."""
    base_channels = base["ae_data"]["ch"]
    target_channels = target["ae_data"]["ch"]

    snap_diff = SnapshotDiff(name=name, date=date)

    for ch_num_str in sorted(target_channels, key=lambda x: int(x)):
        target_ch = target_channels[ch_num_str]
        if not target_ch.get("name", "").strip():
            continue  # skip unnamed channels

        base_ch = base_channels.get(ch_num_str, {})
        ch_diff = diff_channels(int(ch_num_str), base_ch, target_ch)

        if ch_diff.changes:
            snap_diff.channel_diffs.append(ch_diff)

    return snap_diff


_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def diff_snap_files(base_path: Path | str, target_path: Path | str) -> SnapshotDiff:
    """Load two .snap files and diff them."""
    base_path = Path(base_path)
    target_path = Path(target_path)
    name = target_path.stem
    date_match = _DATE_RE.search(target_path.name)
    date = date_match.group(1) if date_match else None
    return diff_snapshots(
        load_snap(base_path), load_snap(target_path), name=name, date=date
    )
