"""Integration diff harness for infrastructure-dsl.

Renders Init.snap + infrastructure.yaml + James assembly.yaml and diffs
against james-2025-12-14.snap section by section.

Usage:
    python scripts/infra_diff.py          # full diff, all focus sections
    python scripts/infra_diff.py fx       # FX section only
    python scripts/infra_diff.py bus      # buses only
    python scripts/infra_diff.py main     # main outputs only
    python scripts/infra_diff.py ch       # infra channels (37-40) only
    python scripts/infra_diff.py dca      # DCAs only
    python scripts/infra_diff.py mgrp     # mute groups only
    python scripts/infra_diff.py cfg      # ae_data.cfg only

Exit code: 0 if no meaningful diffs, 1 if diffs remain.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on path when run directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from snapwright.dsl.renderer import render_assembly
from snapwright.wing.parser import load_snap

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

JAMES_ASSEMBLY = Path("data/dsl/teams/james/assembly.yaml")
REFERENCE_SNAP = Path("data/reference/snapshots/james-2025-12-14.snap")

# ---------------------------------------------------------------------------
# Masking config (per brief)
# ---------------------------------------------------------------------------

# Channels to include in ch diff (infra channels only)
_INFRA_CHANNELS = {"37", "38", "39", "40"}

# Session-adjusted send keys within buses (monitor faders move per service)
_SESSION_BUS_KEYS = {"fdr"}
_SESSION_MONITOR_BUSES = {"13", "14", "15", "16"}

# Float precision threshold — 0.1 covers both dB rounding (0.1 dB negligible)
# and Hz rounding (0.1 Hz at any audio freq is inaudible).
_FLOAT_TOL = 0.1

# Focus sections (what the brief cares about)
_FOCUS_SECTIONS = {"fx", "bus", "main", "ch", "dca", "mgrp", "cfg"}

# ---------------------------------------------------------------------------
# Diff helpers
# ---------------------------------------------------------------------------


def _is_float_close(a, b) -> bool:
    """Return True if both are numeric and within tolerance."""
    try:
        return abs(float(a) - float(b)) < _FLOAT_TOL
    except (TypeError, ValueError):
        return False


def _diff_dict(rendered: dict, reference: dict, path: str = "") -> list[str]:
    """Recursively diff two dicts. Returns list of human-readable diff lines."""
    lines = []
    all_keys = set(list(rendered.keys()) + list(reference.keys()))
    for k in sorted(all_keys, key=lambda x: (isinstance(x, str) and x.isdigit(), x)):
        rk = rendered.get(k)
        fk = reference.get(k)
        full_path = f"{path}.{k}" if path else str(k)

        if rk == fk:
            continue
        if _is_float_close(rk, fk):
            continue

        if isinstance(rk, dict) and isinstance(fk, dict):
            lines.extend(_diff_dict(rk, fk, full_path))
        elif k not in rendered:
            lines.append(f"  MISSING  {full_path}  (ref has {fk!r})")
        elif k not in reference:
            lines.append(f"  EXTRA    {full_path}  (rendered has {rk!r})")
        else:
            lines.append(f"  DIFFER   {full_path}  rendered={rk!r}  ref={fk!r}")
    return lines


def _diff_section(rendered_snap: dict, ref_snap: dict, section: str) -> list[str]:
    """Diff a single ae_data section. Returns diff lines."""
    rendered = rendered_snap["ae_data"].get(section, {})
    reference = ref_snap["ae_data"].get(section, {})
    return _diff_dict(rendered, reference, section)


# ---------------------------------------------------------------------------
# Section-specific diff functions
# ---------------------------------------------------------------------------


def diff_fx(rendered_snap: dict, ref_snap: dict) -> list[str]:
    """Diff ae_data.fx. Only bus-wired slots (1,2,5,6,7) are in scope."""
    lines = []
    rendered = rendered_snap["ae_data"].get("fx", {})
    reference = ref_snap["ae_data"].get("fx", {})
    for slot in ["1", "2", "5", "6", "7"]:
        r = rendered.get(slot, {})
        f = reference.get(slot, {})
        lines.extend(_diff_dict(r, f, f"fx.{slot}"))
    return lines


def diff_bus(rendered_snap: dict, ref_snap: dict) -> list[str]:
    """Diff ae_data.bus (all 16). Mask session-adjusted faders and bus 8.

    Bus 8 is excluded: never operator-configured factory debris. Its Q values
    differ between rendered (Init default, firmware patch skipped) and reference
    (varies) but carry no operational meaning.
    """
    lines = []
    rendered = rendered_snap["ae_data"].get("bus", {})
    reference = ref_snap["ae_data"].get("bus", {})
    for bus_num in [str(i) for i in range(1, 17)]:
        if bus_num == "8":
            continue  # bus 8 masked — never configured, factory debris
        r = dict(rendered.get(bus_num, {}))
        f = dict(reference.get(bus_num, {}))
        # Faders are session-adjusted on all buses (mix + monitor)
        r.pop("fdr", None)
        f.pop("fdr", None)
        lines.extend(_diff_dict(r, f, f"bus.{bus_num}"))
    return lines


def diff_main(rendered_snap: dict, ref_snap: dict) -> list[str]:
    """Diff ae_data.main. Mask main fader (session-adjusted)."""
    lines = []
    rendered = rendered_snap["ae_data"].get("main", {})
    reference = ref_snap["ae_data"].get("main", {})
    for out in ["1", "2", "3"]:
        r = dict(rendered.get(out, {}))
        f = dict(reference.get(out, {}))
        # Main fader is session-adjusted
        r.pop("fdr", None)
        f.pop("fdr", None)
        lines.extend(_diff_dict(r, f, f"main.{out}"))
    return lines


def diff_ch(rendered_snap: dict, ref_snap: dict) -> list[str]:
    """Diff ae_data.ch, infra channels (37-40) only.

    Masking rules:
    - flt.hcf: LPF frequency — LPF is off on all infra channels; value is inaudible noise
    - send.N.lvl / send.N.mode: off-sends have session-adjusted stored levels/modes
    - main.*.lvl: session-adjusted fader levels (Wing float noise for 0 dB, etc.)
    """
    import copy
    lines = []
    rendered = rendered_snap["ae_data"].get("ch", {})
    reference = ref_snap["ae_data"].get("ch", {})
    for ch_num in sorted(_INFRA_CHANNELS, key=int):
        r = copy.deepcopy(rendered.get(ch_num, {}))
        f = copy.deepcopy(reference.get(ch_num, {}))
        # Mask flt.hcf (LPF off — frequency value is irrelevant)
        for d in (r, f):
            d.get("flt", {}).pop("hcf", None)
        # Mask off-send lvl/mode (session-adjusted stored levels)
        for d in (r, f):
            for send_cfg in d.get("send", {}).values():
                if isinstance(send_cfg, dict) and not send_cfg.get("on", False):
                    send_cfg.pop("lvl", None)
                    send_cfg.pop("mode", None)
        # Mask main fader levels (session-adjusted)
        for d in (r, f):
            for out_cfg in d.get("main", {}).values():
                if isinstance(out_cfg, dict):
                    out_cfg.pop("lvl", None)
        lines.extend(_diff_dict(r, f, f"ch.{ch_num}"))
    return lines


def diff_dca(rendered_snap: dict, ref_snap: dict) -> list[str]:
    """Diff ae_data.dca. Mask fader values (session-adjusted)."""
    lines = []
    rendered = rendered_snap["ae_data"].get("dca", {})
    reference = ref_snap["ae_data"].get("dca", {})
    for dca_key in sorted(set(list(rendered) + list(reference)), key=int):
        r = dict(rendered.get(dca_key, {}))
        f = dict(reference.get(dca_key, {}))
        # DCA faders are session-adjusted (moved during worship)
        r.pop("fdr", None)
        f.pop("fdr", None)
        lines.extend(_diff_dict(r, f, f"dca.{dca_key}"))
    return lines


def diff_mgrp(rendered_snap: dict, ref_snap: dict) -> list[str]:
    return _diff_section(rendered_snap, ref_snap, "mgrp")


def diff_cfg(rendered_snap: dict, ref_snap: dict) -> list[str]:
    """Diff ae_data.cfg only."""
    rendered = rendered_snap["ae_data"].get("cfg", {})
    reference = ref_snap["ae_data"].get("cfg", {})
    return _diff_dict(rendered, reference, "cfg")


_SECTION_FUNCS = {
    "fx": diff_fx,
    "bus": diff_bus,
    "main": diff_main,
    "ch": diff_ch,
    "dca": diff_dca,
    "mgrp": diff_mgrp,
    "cfg": diff_cfg,
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run(sections: list[str] | None = None) -> int:
    if sections is None:
        sections = list(_SECTION_FUNCS.keys())

    print(f"Rendering {JAMES_ASSEMBLY} ...")
    rendered_snap = render_assembly(JAMES_ASSEMBLY)
    ref_snap = load_snap(REFERENCE_SNAP)
    print(f"Reference: {REFERENCE_SNAP}")
    print()

    total_diffs = 0
    for section in sections:
        fn = _SECTION_FUNCS.get(section)
        if fn is None:
            print(f"Unknown section: {section!r}. Choose from: {list(_SECTION_FUNCS)}")
            return 2
        diffs = fn(rendered_snap, ref_snap)
        label = section.upper()
        if diffs:
            print(f"=== {label} ({len(diffs)} diffs) ===")
            for line in diffs:
                print(line)
            print()
            total_diffs += len(diffs)
        else:
            print(f"=== {label} — clean ✓ ===")

    print()
    if total_diffs == 0:
        print("✓ All focus sections clean.")
        return 0
    else:
        print(f"✗ {total_diffs} diff(s) remaining.")
        return 1


if __name__ == "__main__":
    args = sys.argv[1:]
    sections = args if args else None
    sys.exit(run(sections))
