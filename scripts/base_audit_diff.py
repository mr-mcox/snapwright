#!/usr/bin/env python3
"""
Leaf-level diff of Init.snap vs Base.snap for Investigation A.
Outputs all differences between factory state and BCF base configuration.
"""

import json
from typing import Any


def flatten(obj: Any, prefix: str = "") -> dict:
    """Flatten a nested dict/list into a flat dict with dot-path keys."""
    result = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}.{k}" if prefix else k
            result.update(flatten(v, new_key))
    elif isinstance(obj, list):
        for idx, v in enumerate(obj):
            new_key = f"{prefix}[{idx}]"
            result.update(flatten(v, new_key))
    else:
        result[prefix] = obj
    return result


def diff_flat(init_flat: dict, base_flat: dict) -> list[dict]:
    """Compare two flat dicts, return list of differences."""
    diffs = []
    all_keys = set(init_flat.keys()) | set(base_flat.keys())
    for key in sorted(all_keys):
        init_val = init_flat.get(key, "__MISSING__")
        base_val = base_flat.get(key, "__MISSING__")
        if init_val != base_val:
            diffs.append(
                {
                    "path": key,
                    "init": init_val,
                    "base": base_val,
                }
            )
    return diffs


def load_snap(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


BASE = "/Users/mcox/dev/snapwright/data/reference/Base.snap"
INIT = "/Users/mcox/Documents/Wing Backup/Init.snap"

base = load_snap(BASE)
init = load_snap(INIT)

# Diff ae_data
ae_base = flatten(base["ae_data"], "ae_data")
ae_init = flatten(init["ae_data"], "ae_data")
ae_diffs = diff_flat(ae_init, ae_base)

# Diff ce_data
ce_base = flatten(base["ce_data"], "ce_data")
ce_init = flatten(init["ce_data"], "ce_data")
ce_diffs = diff_flat(ce_init, ce_base)

print(f"ae_data differences: {len(ae_diffs)}")
print(f"ce_data differences: {len(ce_diffs)}")
print()

# Print ae_data grouped by section
sections = {}
for d in ae_diffs:
    # e.g. ae_data.ch[0].name -> section = "ch"
    path = d["path"]
    parts = path.split(".")
    if len(parts) >= 2:
        section = parts[1].split("[")[0]
    else:
        section = "top"
    sections.setdefault(section, []).append(d)

print("=== ae_data DIFFS BY SECTION ===")
for section, diffs in sorted(sections.items()):
    print(f"\n--- {section} ({len(diffs)} diffs) ---")
    for d in diffs:
        print(f"  {d['path']}")
        print(f"    INIT: {d['init']!r}")
        print(f"    BASE: {d['base']!r}")

print()
print("=== ce_data DIFFS BY SECTION ===")
ce_sections = {}
for d in ce_diffs:
    path = d["path"]
    parts = path.split(".")
    if len(parts) >= 2:
        section = parts[1].split("[")[0]
    else:
        section = "top"
    ce_sections.setdefault(section, []).append(d)

for section, diffs in sorted(ce_sections.items()):
    print(f"\n--- {section} ({len(diffs)} diffs) ---")
    for d in diffs:
        print(f"  {d['path']}")
        print(f"    INIT: {d['init']!r}")
        print(f"    BASE: {d['base']!r}")

# Summary counts
print("\n=== SUMMARY ===")
for section, diffs in sorted(sections.items()):
    print(f"  ae_data.{section}: {len(diffs)} diffs")
for section, diffs in sorted(ce_sections.items()):
    print(f"  ce_data.{section}: {len(diffs)} diffs")
