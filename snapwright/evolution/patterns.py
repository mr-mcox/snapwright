"""Batch pattern detection across multiple SnapshotDiffs.

A pattern is a (channel_name, channel_num, param_path) tuple that shows a
significant change across N or more snapshots.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from snapwright.evolution.diff import SnapshotDiff, ParamChange


@dataclass
class Occurrence:
    snapshot: str
    date: str | None
    old_val: str
    new_val: str
    delta: float | None


@dataclass
class Pattern:
    channel: str
    channel_num: int
    path: str
    section: str
    label: str
    occurrences: list[Occurrence] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.occurrences)

    @property
    def typical_delta(self) -> float | None:
        deltas = [o.delta for o in self.occurrences if o.delta is not None]
        return statistics.median(deltas) if deltas else None

    @property
    def consistent_direction(self) -> bool:
        deltas = [o.delta for o in self.occurrences if o.delta is not None]
        if len(deltas) < 2:
            return True
        return all(d > 0 for d in deltas) or all(d < 0 for d in deltas)

    @property
    def constant_offset(self) -> bool:
        """All numeric deltas identical — may indicate a stale baseline value."""
        deltas = [o.delta for o in self.occurrences if o.delta is not None]
        if len(deltas) < 2:
            return False
        return len(set(round(d, 3) for d in deltas)) == 1

    @property
    def recent_count(self) -> int:
        """Occurrences in the second half of the batch — recency signal."""
        n = len(self.occurrences)
        return len(self.occurrences[n // 2:])


def find_patterns(diffs: list[SnapshotDiff], min_occurrences: int = 3) -> list[Pattern]:
    """Return patterns that recur across at least min_occurrences snapshots.

    Sorted: consistent + recent first, then by total count.
    """
    raw: dict[tuple[str, int, str], list[tuple[SnapshotDiff, ParamChange]]] = {}

    for snap_diff in diffs:
        for ch_diff in snap_diff.significant_channel_diffs:
            for change in ch_diff.significant_changes:
                key = (ch_diff.name, ch_diff.number, change.path)
                raw.setdefault(key, []).append((snap_diff, change))

    patterns: list[Pattern] = []

    for (ch_name, ch_num, path), entries in raw.items():
        if len(entries) < min_occurrences:
            continue

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

        last_label = entries[-1][1].label
        patterns.append(Pattern(
            channel=ch_name,
            channel_num=ch_num,
            path=path,
            section=last_label.section,
            label=last_label.label,
            occurrences=occurrences,
        ))

    return sorted(patterns, key=lambda p: (
        -int(p.consistent_direction),
        -p.recent_count,
        -p.count,
    ))
