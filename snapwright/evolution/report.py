"""Format snapshot evolution analysis as a human-readable markdown report."""

from __future__ import annotations

from pathlib import Path

from snapwright.evolution.diff import SnapshotDiff
from snapwright.evolution.patterns import Pattern


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _delta_str(delta: float | None) -> str:
    if delta is None:
        return ""
    sign = "+" if delta > 0 else ""
    return f" ({sign}{delta:.1f})"


def _base_section(section: str) -> str:
    """Strip model suffix: 'EQ (STD)' → 'EQ', 'Dynamics (ECL33)' → 'Dynamics'."""
    return section.split("(")[0].strip()


def _suggestion(p: Pattern) -> str:
    """Generate a 'Consider...' suggestion for a pattern."""
    d = p.typical_delta
    last = p.occurrences[-1]
    target_val = last.new_val
    section = _base_section(p.section)

    # Channel + section + label, e.g. "Kick EQ high shelf gain"
    # Section names (Fader, Filter, etc.) don't collide with labels so no deduplication needed
    full_label = f"{p.channel} {section} {p.label}".strip()

    # On/off changes: enable / disable phrasing
    if p.label in ("on", "mute") or p.path.endswith(".on") or p.path == "mute":
        action = "enabling" if target_val == "on" else "disabling"
        return (
            f"Consider **{action}** {full_label} in the Sunday Starter template "
            f"(changed {p.count}×)"
        )

    # -144 dB target means the send should be off
    if target_val == "-144.0 dB" or target_val == "-144":
        return (
            f"Consider **removing** {full_label} from the Sunday Starter template "
            f"(turned off {p.count}×)"
        )

    # Model changes
    if p.label == "model" or p.path.endswith(".mdl"):
        return (
            f"Consider updating **{full_label}** to {target_val} in the Sunday Starter template "
            f"(changed {p.count}×)"
        )

    # Numeric changes with direction
    if d is not None:
        is_freq = "freq" in p.label or "freq" in p.path
        direction = ("raising" if d > 0 else "lowering") if is_freq else ("increasing" if d > 0 else "reducing")
        return (
            f"Consider {direction} **{full_label}** to {target_val} "
            f"in the Sunday Starter template (changed {p.count}×, median shift "
            f"{'+' if d > 0 else ''}{d:.1f})"
        )

    return (
        f"Consider updating **{full_label}** to {target_val} "
        f"in the Sunday Starter template (changed {p.count}×)"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_report(
    base_name: str,
    diffs: list[SnapshotDiff],
    patterns: list[Pattern],
    min_occurrences: int = 3,
) -> str:
    """Render a full markdown analysis report."""
    lines: list[str] = []

    lines.append("# Snapshot Evolution Analysis")
    lines.append("")
    lines.append(f"**Baseline**: {base_name}")
    lines.append(f"**Snapshots analysed**: {len(diffs)}")
    lines.append(f"**Pattern threshold**: {min_occurrences}+ occurrences")
    lines.append("")

    # -----------------------------------------------------------------------
    # Patterns section
    # -----------------------------------------------------------------------
    lines.append("---")
    lines.append("")
    lines.append("## Patterns (Recurring Changes)")
    lines.append("")

    if not patterns:
        lines.append(f"_No patterns found meeting the {min_occurrences}+ threshold._")
    else:
        # Group by (channel_name, channel_num) to keep same-named channels separate
        by_channel: dict[tuple[str, int], list[Pattern]] = {}
        for p in patterns:
            by_channel.setdefault((p.channel, p.channel_num), []).append(p)

        for (ch_name, ch_num), ch_patterns in by_channel.items():
            # Show channel number only if another channel shares the name
            name_count = sum(1 for (n, _) in by_channel if n == ch_name)
            num_suffix = f" (ch{ch_num})" if name_count > 1 else ""
            lines.append(f"### {ch_name}{num_suffix}")
            lines.append("")
            for p in ch_patterns:
                direction = " ✓ consistent" if p.consistent_direction else " ~ mixed direction"
                recency = f", {p.recent_count} recent" if p.recent_count > 0 else ""
                offset_note = " ⚠️ constant offset" if p.constant_offset else ""
                lines.append(f"**{p.section} — {p.label}** ({p.count}×{recency}{direction}{offset_note})") 
                lines.append("")
                for o in p.occurrences:
                    date_str = f" [{o.date}]" if o.date else ""
                    d_str = _delta_str(o.delta)
                    lines.append(f"- {o.snapshot}{date_str}: {o.old_val} → {o.new_val}{d_str}")
                lines.append("")

    # -----------------------------------------------------------------------
    # Suggestions section
    # -----------------------------------------------------------------------
    lines.append("---")
    lines.append("")
    lines.append("## Suggestions for Sunday Starter Template")
    lines.append("")

    strong = [p for p in patterns if p.consistent_direction and p.count >= min_occurrences]
    weak = [p for p in patterns if not p.consistent_direction and p.count >= min_occurrences]

    if not strong and not weak:
        lines.append("_No patterns strong enough to suggest template updates._")
    else:
        if strong:
            lines.append("### High confidence (consistent direction)")
            lines.append("")
            for p in strong:
                lines.append(f"- {_suggestion(p)}")
            lines.append("")
        if weak:
            lines.append("### Worth watching (mixed direction)")
            lines.append("")
            for p in weak:
                lines.append(f"- {_suggestion(p)}")
            lines.append("")

    # -----------------------------------------------------------------------
    # Per-snapshot detail
    # -----------------------------------------------------------------------
    lines.append("---")
    lines.append("")
    lines.append("## Per-Snapshot Diffs")
    lines.append("")

    for snap_diff in diffs:
        date_str = f" ({snap_diff.date})" if snap_diff.date else ""
        sig_diffs = snap_diff.significant_channel_diffs
        lines.append(f"### {snap_diff.name}{date_str}")
        lines.append("")

        if not sig_diffs:
            lines.append("_No significant changes from baseline._")
            lines.append("")
            continue

        # Group by channel
        for ch_diff in sig_diffs:
            lines.append(f"**{ch_diff.name}** (ch{ch_diff.number})")
            lines.append("")

            # Group by section within channel
            by_section: dict[str, list] = {}
            for change in ch_diff.significant_changes:
                by_section.setdefault(change.label.section, []).append(change)

            for section, changes in by_section.items():
                lines.append(f"  *{section}*")
                for change in changes:
                    d_str = _delta_str(change.label.delta)
                    lines.append(
                        f"  - {change.label.label}: {change.label.old_fmt} → {change.label.new_fmt}{d_str}"
                    )
                lines.append("")

    return "\n".join(lines)
