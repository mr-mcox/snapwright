import json

import yaml


def load_snap(path):
    with open(path) as f:
        return json.load(f)


james = load_snap("data/reference/sunday-starters/James.snap")
base = load_snap("data/reference/Base.snap")
init = load_snap("data/reference/Init.snap")

print("=== RENDERER: does it set bus names? ===")
with open("snapwright/wing/defaults.py") as f:
    defaults = f.read()
print("\ndefaults.py relevant lines (bus/name):")
found = False
for i, line in enumerate(defaults.split("\n"), 1):
    if "bus" in line.lower() and "name" in line.lower():
        print(f"  {i}: {line.rstrip()}")
        found = True
if not found:
    print("  (none found)")

print("\n=== snap_template structure for buses ===")
# Check what snap_template includes
import sys

sys.path.insert(0, ".")
from snapwright.wing.defaults import snap_template

t = snap_template()
print("Bus 1 in snap_template:")
print(json.dumps(t["ae_data"]["bus"]["1"], indent=2)[:500])
print("\nDCA 1 in snap_template:")
print(json.dumps(t["ae_data"]["dca"]["1"], indent=2)[:200])
print("\nmgrp 1 in snap_template:")
print(json.dumps(t["ae_data"]["mgrp"]["1"], indent=2)[:200])
print("\nmtx 1 in snap_template:")
print(
    json.dumps(t["ae_data"]["mtx"]["1"], indent=2)[:200]
    if "1" in t["ae_data"].get("mtx", {})
    else "(not present)"
)
print("\nce_data in snap_template:")
print(list(t.get("ce_data", {}).keys()))

print("\n=== PRISCILLA team bus names (vs james) ===")
with open("data/dsl/teams/priscilla/assembly.yaml") as f:
    priscilla_assembly = yaml.safe_load(f)
priscilla_buses = priscilla_assembly.get("buses", {})
print(f"Priscilla buses in DSL: {priscilla_buses}")
priscilla_snap = load_snap("data/reference/sunday-starters/pricilla team.snap")
print("\nPriscilla snap bus names (showing differences from James):")
all_same = True
for i in range(1, 17):
    key = str(i)
    p_name = (
        priscilla_snap.get("ae_data", {}).get("bus", {}).get(key, {}).get("name", "")
    )
    j_name = james.get("ae_data", {}).get("bus", {}).get(key, {}).get("name", "")
    b_name = base.get("ae_data", {}).get("bus", {}).get(key, {}).get("name", "")
    diff = " <<< DIFFERS" if p_name != j_name else ""
    print(
        f"  bus {i:2d}: Priscilla='{p_name:<20}' James='{j_name:<20}' Base='{b_name}'{diff}"
    )
    if p_name != j_name:
        all_same = False
if all_same:
    print("  (all identical)")

print("\n=== Ch 13/14 in Base.snap ===")
# These were Computer and Handheld in Base but James/Flute in James
for i in [13, 14, 38, 40]:
    key = str(i)
    b = base.get("ae_data", {}).get("ch", {}).get(key, {})
    j = james.get("ae_data", {}).get("ch", {}).get(key, {})
    print(
        f"  ch {i}: base_name='{b.get('name', '')}' james_name='{j.get('name', '')}' base_col={b.get('col', '')} james_col={j.get('col', '')}"
    )

print("\n=== Names that differ across ALL teams (team-specific) ===")
snaps_all = {
    "James": james,
    "Levin": load_snap("data/reference/sunday-starters/Levin.snap"),
    "Jen": load_snap("data/reference/sunday-starters/Jen.snap"),
    "Priscilla": priscilla_snap,
    "Morks": load_snap("data/reference/sunday-starters/Morks~2025.snap"),
    "Kana": load_snap("data/reference/sunday-starters/Kana's Team from base.snap"),
}
print("\nChannels where names differ across teams:")
for i in range(1, 41):
    key = str(i)
    names = set()
    for snap in snaps_all.values():
        n = snap.get("ae_data", {}).get("ch", {}).get(key, {}).get("name", "")
        names.add(n)
    if len(names) > 1:
        print(
            f"  ch {i:2d}: {dict((t, snaps_all[t].get('ae_data', {}).get('ch', {}).get(key, {}).get('name', '')) for t in snaps_all)}"
        )
