"""Format snapshot evolution analysis as a markdown report."""

from __future__ import annotations

from snapwright.evolution.diff import SnapshotDiff
from snapwright.evolution.patterns import Pattern


def _delta_str(delta: float | None) -> str:
    if delta is None:
        return ""
    sign = "+" if delta > 0 else ""
    return f" ({sign}{delta:.1f})"


def _base_section(section: str) -> str:
    """'EQ (STD)' → 'EQ', 'Dynamics (ECL33)' → 'Dynamics'."""
    return section.split("(")[0].strip()


def _suggestion(p: Pattern) -> str:
    d = p.typical_delta
    last = p.occurrences[-1]
    target_val = last.new_val
    section = _base_section(p.section)
    full_label = f"{p.channel} {section} {p.label}".strip()

    if p.label in ("on", "mute") or p.path.endswith(".on") or p.path == "mute":
        action = "enabling" if target_val == "on" else "disabling"
        return f"Consider **{action}** {full_label} in the Sunday Starter ({p.count}×)"

    if target_val in ("-144.0 dB", "-144"):
        return (
            f"Consider **removing** {full_label}"
            f" from the Sunday Starter ({p.count}×, turned off)"
        )

    if p.label == "model" or p.path.endswith(".mdl"):
        return f"Consider updating **{full_label}** to {target_val} ({p.count}×)"

    if d is not None:
        is_freq = "freq" in p.label
        direction = (
            ("raising" if d > 0 else "lowering")
            if is_freq
            else ("increasing" if d > 0 else "reducing")
        )
        sign = "+" if d > 0 else ""
        return (
            f"Consider {direction} **{full_label}** to {target_val}"
            f" ({p.count}×, median {sign}{d:.1f})"
        )

    return f"Consider updating **{full_label}** to {target_val} ({p.count}×)"


def _render_patterns_section(
    patterns: list[Pattern], min_occurrences: int
) -> list[str]:
    lines: list[str] = ["## Patterns (Recurring Changes)", ""]

    if not patterns:
        lines.append(f"_No patterns found at threshold {min_occurrences}+._")
        return lines

    by_channel: dict[tuple[str, int], list[Pattern]] = {}
    for p in patterns:
        by_channel.setdefault((p.channel, p.channel_num), []).append(p)

    for (ch_name, ch_num), ch_patterns in by_channel.items():
        name_count = sum(1 for (n, _) in by_channel if n == ch_name)
        num_suffix = f" (ch{ch_num})" if name_count > 1 else ""
        lines += [f"### {ch_name}{num_suffix}", ""]

        for p in ch_patterns:
            direction = (
                "✓ consistent" if p.consistent_direction else "~ mixed direction"
            )
            recency = f", {p.recent_count} recent" if p.recent_count > 0 else ""
            offset = " ⚠️ constant offset" if p.constant_offset else ""
            header = (
                f"**{p.section} — {p.label}**"
                f" ({p.count}×{recency} {direction}{offset})"
            )
            lines.append(header)
            lines.append("")
            for o in p.occurrences:
                date_str = f" [{o.date}]" if o.date else ""
                d = _delta_str(o.delta)
                lines.append(f"- {o.snapshot}{date_str}: {o.old_val} → {o.new_val}{d}")
            lines.append("")

    return lines


def _render_suggestions_section(patterns: list[Pattern]) -> list[str]:
    lines: list[str] = ["---", "", "## Suggestions for Sunday Starter Template", ""]

    strong = [p for p in patterns if p.consistent_direction]
    mixed = [p for p in patterns if not p.consistent_direction]

    if not patterns:
        lines.append("_No patterns strong enough to suggest template updates._")
        return lines

    if strong:
        lines += ["### High confidence (consistent direction)", ""]
        for p in strong:
            lines.append(f"- {_suggestion(p)}")
        lines.append("")
    if mixed:
        lines += ["### Worth watching (mixed direction)", ""]
        for p in mixed:
            lines.append(f"- {_suggestion(p)}")
        lines.append("")

    return lines


def _render_per_snapshot_section(diffs: list[SnapshotDiff]) -> list[str]:
    lines: list[str] = ["---", "", "## Per-Snapshot Diffs", ""]

    for snap_diff in diffs:
        date_str = f" ({snap_diff.date})" if snap_diff.date else ""
        lines += [f"### {snap_diff.name}{date_str}", ""]

        sig = snap_diff.significant_channel_diffs
        if not sig:
            lines += ["_No significant changes from baseline._", ""]
            continue

        for ch_diff in sig:
            lines.append(f"**{ch_diff.name}** (ch{ch_diff.number})")
            lines.append("")
            by_section: dict[str, list] = {}
            for change in ch_diff.significant_changes:
                by_section.setdefault(change.label.section, []).append(change)
            for section, changes in by_section.items():
                lines.append(f"  *{section}*")
                for change in changes:
                    lbl = change.label
                    d = _delta_str(lbl.delta)
                    lines.append(f"  - {lbl.label}: {lbl.old_fmt} → {lbl.new_fmt}{d}")
                lines.append("")

    return lines


def render_report(
    base_name: str,
    diffs: list[SnapshotDiff],
    patterns: list[Pattern],
    min_occurrences: int = 3,
) -> str:
    lines: list[str] = [
        "# Snapshot Evolution Analysis",
        "",
        f"**Baseline**: {base_name}",
        f"**Snapshots analysed**: {len(diffs)}",
        f"**Pattern threshold**: {min_occurrences}+",
        "",
        "---",
        "",
    ]

    lines += _render_patterns_section(patterns, min_occurrences)
    lines += _render_suggestions_section(patterns)
    lines += _render_per_snapshot_section(diffs)

    return "\n".join(lines)
