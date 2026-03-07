"""Batch pattern detection across multiple SnapshotDiffs.

A pattern is a (channel, param path) pair that shows a significant change
in the same direction across N or more snapshots.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Any

from snapwright.evolution.diff import SnapshotDiff, ParamChange


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Occurrence:
    snapshot: str       # snapshot display name
    date: str | None
    old_val: str        # formatted old value
    new_val: str        # formatted new value
    delta: float | None # signed numeric delta


@dataclass
class Pattern:
    channel: str        # e.g. "Kick"
    channel_num: int    # e.g. 1 (to disambiguate same-named channels)
    path: str           # Wing param path e.g. "eq.1g"
    section: str        # e.g. "EQ (STD)"
    label: str          # e.g. "band 1 gain"
    occurrences: list[Occurrence] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.occurrences)

    @property
    def typical_delta(self) -> float | None:
        deltas = [o.delta for o in self.occurrences if o.delta is not None]
        if not deltas:
            return None
        return statistics.median(deltas)

    @property
    def consistent_direction(self) -> bool:
        """True if all numeric deltas have the same sign."""
        deltas = [o.delta for o in self.occurrences if o.delta is not None]
        if len(deltas) < 2:
            return True
        return all(d > 0 for d in deltas) or all(d < 0 for d in deltas)

    @property
    def constant_offset(self) -> bool:
        """True if all numeric deltas are identical — may indicate a stale baseline
        rather than a genuine recurring adjustment."""
        deltas = [o.delta for o in self.occurrences if o.delta is not None]
        if len(deltas) < 2:
            return False
        return len(set(round(d, 3) for d in deltas)) == 1

    @property
    def recent_count(self) -> int:
        """Occurrences in the second half of the batch (most recent snapshots)."""
        n = len(self.occurrences)
        return sum(1 for o in self.occurrences[n // 2:] if o.delta is not None or o.old_val != o.new_val)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def find_patterns(diffs: list[SnapshotDiff], min_occurrences: int = 3) -> list[Pattern]:
    """Find params that change significantly in the same direction across >= min_occurrences snapshots.

    Returns patterns sorted by: recency weight (more recent = higher weight), then count.
    """
    # Accumulate occurrences per (channel_name, param_path)
    raw: dict[tuple[str, str, int], list[tuple[SnapshotDiff, ParamChange]]] = {}

    for snap_diff in diffs:
        for ch_diff in snap_diff.significant_channel_diffs:
            for change in ch_diff.significant_changes:
                # Include channel number to disambiguate same-named channels (e.g. ch13 vs ch25 both named "James")
                key = (ch_diff.name, change.path, ch_diff.number)
                raw.setdefault(key, []).append((snap_diff, change))

    patterns: list[Pattern] = []

    for (ch_name, path, ch_num), entries in raw.items():
        if len(entries) < min_occurrences:
            continue

        # Build occurrences list
        occurrences = [
            Occurrence(
                snapshot=snap.name,
                date=snap.date,
                old_val=change.label.old_fmt,
                new_val=change.label.new_fmt,
                delta=change.label.delta,
            )
            for snap, change in entries
        ]

        # Use the last entry's label metadata for display
        last_label = entries[-1][1].label

        p = Pattern(
            channel=ch_name,
            channel_num=ch_num,
            path=path,
            section=last_label.section,
            label=last_label.label,
            occurrences=occurrences,
        )
        patterns.append(p)

    # Sort: consistent + recent first, then by count
    def sort_key(p: Pattern) -> tuple:
        return (
            -int(p.consistent_direction),   # consistent direction first
            -p.recent_count,                # more recent occurrences first
            -p.count,                       # then by total count
        )

    return sorted(patterns, key=sort_key)
