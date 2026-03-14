"""Coverage report: deterministic renderer scope analysis.

Diffs Init.snap vs a rendered assembly by building a full recursive diff tree.
Every node in the tree carries total leaf-field count and changed leaf-field count,
aggregated bottom-up. This surfaces partial coverage automatically — a section
with 5% ratio inside a parent with 60% ratio stands out without manual curation.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from snapwright.dsl.renderer import render_assembly
from snapwright.wing.parser import load_snap

INIT_SNAP = Path("data/reference/Init.snap")
DEFAULT_ASSEMBLY = Path("data/dsl/teams/james/assembly.yaml")
REPORT_PATH = Path("docs/coverage-report.json")

# Depth (from root) at which children are omitted in JSON output.
# Depth 0 = root, 1 = ae_data/ce_data, 2 = ae_data.ch, 3 = ae_data.ch.1
# Capped at 3: captures section → sub-section → item granularity without
# exploding to individual parameter level (~21k leaf nodes).
_JSON_MAX_DEPTH = 3


# ---------------------------------------------------------------------------
# Diff tree
# ---------------------------------------------------------------------------


def _sort_key(k: str) -> tuple:
    """Sort dict keys: numeric strings numerically, others alphabetically."""
    return (k.isdigit(), int(k) if k.isdigit() else k)


def _build_diff_tree(a: Any, b: Any) -> dict:
    """Recursively diff two values. Returns {total, changed, children?}.

    total   — count of leaf fields reachable from this node in either snapshot
    changed — count of leaf fields that differ between a and b
    children — present only when both a and b are dicts
    """
    if not isinstance(a, dict) or not isinstance(b, dict):
        changed = 0 if a == b else 1
        return {"total": 1, "changed": changed}

    all_keys = set(a) | set(b)
    children: dict[str, dict] = {}
    total = changed = 0

    for k in sorted(all_keys, key=_sort_key):
        child = _build_diff_tree(a.get(k), b.get(k))
        children[k] = child
        total += child["total"]
        changed += child["changed"]

    return {"total": total, "changed": changed, "children": children}


def _prune_tree(node: dict, max_depth: int, depth: int = 0) -> dict:
    """Return node with children omitted beyond max_depth.

    total and changed are preserved accurately at all depths — they were
    computed bottom-up over the full tree before pruning.
    """
    result: dict = {"total": node["total"], "changed": node["changed"]}
    if depth < max_depth and "children" in node:
        result["children"] = {
            k: _prune_tree(child, max_depth, depth + 1)
            for k, child in node["children"].items()
        }
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_coverage_report(assembly: Path = DEFAULT_ASSEMBLY) -> dict:
    """Render assembly, diff against Init.snap, return structured report dict."""
    init = load_snap(INIT_SNAP)
    rendered = render_assembly(assembly)

    full_tree = _build_diff_tree(init, rendered)
    pruned = _prune_tree(full_tree, max_depth=_JSON_MAX_DEPTH)

    # Only include the audio/control engine sections — top-level snapshot
    # metadata (type, creator, creator_fw, etc.) is noise for coverage purposes.
    _REPORT_ROOTS = {"ae_data", "ce_data"}
    diff_tree = {
        k: v for k, v in pruned.get("children", {}).items() if k in _REPORT_ROOTS
    }

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "rendered_from": str(assembly),
        "diff_tree": diff_tree,
    }


def write_report(report: dict, path: Path = REPORT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------


def _pct(changed: int, total: int) -> str:
    if total == 0:
        return "  —"
    return f"{changed / total:5.1%}"


def _flag_partial(node: dict) -> bool:
    """True if children show significant ratio asymmetry (partial coverage signal)."""
    children = node.get("children", {})
    if len(children) < 2:
        return False
    ratios = [
        c["changed"] / c["total"] for c in children.values() if c["total"] > 0
    ]
    if not ratios or max(ratios) == 0:
        return False
    return max(ratios) / (min(ratios) + 1e-9) > 10


def format_summary_table(report: dict) -> str:
    """Human-readable tree showing changed/total and ratio at each node.

    Shows depth-1 and depth-2 nodes always. Expands depth-3 children only
    when they show significant ratio asymmetry (partial coverage signal).
    """
    lines = [
        f"Coverage diff — rendered from: {report['rendered_from']}",
        f"Generated: {report['generated_at']}",
        "",
        f"{'Section':<48} {'Changed':>8}  {'Total':>7}  {'%':>6}",
        f"{'-' * 48} {'-' * 8}  {'-' * 7}  {'-' * 6}",
    ]

    tree = report["diff_tree"]

    def _row(label: str, node: dict, suffix: str = "") -> str:
        c, t = node["changed"], node["total"]
        return f"{label:<48} {c:>8}  {t:>7}  {_pct(c, t):>6}{suffix}"

    for top_key in sorted(tree):                         # ae_data, ce_data
        top = tree[top_key]
        lines.append(_row(top_key, top))

        for sec_key in sorted(top.get("children", {}), key=_sort_key):
            sec = top["children"][sec_key]
            path = f"  {top_key}.{sec_key}"
            flag = "  \u2190 partial?" if _flag_partial(sec) else ""
            lines.append(_row(path, sec, flag))

            # Expand children when asymmetry suggests partial coverage
            if _flag_partial(sec):
                for item_key in sorted(
                    sec.get("children", {}), key=_sort_key
                ):
                    item = sec["children"][item_key]
                    ipath = f"    {top_key}.{sec_key}.{item_key}"
                    lines.append(_row(ipath, item))

        lines.append("")

    total_changed = sum(tree[k]["changed"] for k in tree)
    total_fields = sum(tree[k]["total"] for k in tree)
    lines.append(
        f"Overall: {total_changed} / {total_fields} fields changed"
        f"  ({_pct(total_changed, total_fields)})"
    )
    return "\n".join(lines)
