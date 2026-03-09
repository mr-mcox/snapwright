import json


def load_snap(path):
    with open(path) as f:
        return json.load(f)


base = load_snap("data/reference/Base.snap")
init = load_snap("data/reference/Init.snap")
james = load_snap("data/reference/sunday-starters/James.snap")

print("=== Bus names: Base vs James (differences only) ===")
for i in range(1, 17):
    key = str(i)
    base_name = base.get("ae_data", {}).get("bus", {}).get(key, {}).get("name", "")
    james_name = james.get("ae_data", {}).get("bus", {}).get(key, {}).get("name", "")
    if base_name == james_name:
        continue
    print(f"  bus {i}: Base='{base_name}' James='{james_name}'")

print("\n=== Does renderer.py touch bus names? ===")
with open("snapwright/dsl/renderer.py") as f:
    content = f.read()
found = False
for i, line in enumerate(content.split("\n"), 1):
    if "bus" in line.lower() and "name" in line.lower():
        print(f"  line {i}: {line.rstrip()}")
        found = True
if not found:
    print("  No bus name setting found in renderer")

print("\n=== Does renderer touch DCA, mgrp, main, mtx? ===")
for section in ["dca", "mgrp", "main", "mtx", "ce_data"]:
    found_lines = []
    for i, line in enumerate(content.split("\n"), 1):
        if section in line.lower():
            found_lines.append(f"  line {i}: {line.rstrip()}")
    if found_lines:
        print(f"\n  -- {section} --")
        for l in found_lines:
            print(l)
    else:
        print(f"\n  {section}: NOT referenced in renderer")

print("\n=== James.snap channel names not in DSL assembly.yaml ===")
# channels in James assembly: 1-8, 13, 14, 16, 25-28, 37, 38
dsl_channels = {1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 16, 25, 26, 27, 28, 37, 38}
for i in range(1, 41):
    key = str(i)
    james_name = james.get("ae_data", {}).get("ch", {}).get(key, {}).get("name", "")
    if james_name and i not in dsl_channels:
        base_name = base.get("ae_data", {}).get("ch", {}).get(key, {}).get("name", "")
        init_name = init.get("ae_data", {}).get("ch", {}).get(key, {}).get("name", "")
        print(f"  ch {i}: name='{james_name}' (base='{base_name}', init='{init_name}')")

print("\n=== Matrix bus names - who sets them? ===")
for i in range(1, 9):
    key = str(i)
    base_name = base.get("ae_data", {}).get("mtx", {}).get(key, {}).get("name", "")
    james_name = james.get("ae_data", {}).get("mtx", {}).get(key, {}).get("name", "")
    print(f"  mtx {i}: base='{base_name}'  james='{james_name}'")
