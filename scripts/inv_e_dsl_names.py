"""
Cross-reference DSL-set names vs snapshot names.
Which channel names does the DSL set vs what comes from Base?
"""
import json
import yaml
from pathlib import Path

def load_snap(path):
    with open(path) as f:
        return json.load(f)

james = load_snap("data/reference/sunday-starters/James.snap")
base = load_snap("data/reference/Base.snap")
init = load_snap("data/reference/Init.snap")

# Load all musician yamls and get their names
musician_dir = Path("data/dsl/musicians")
musician_names = {}  # filename_stem -> name
for yf in musician_dir.glob("*.yaml"):
    with open(yf) as f:
        data = yaml.safe_load(f)
    if "name" in data:
        musician_names[yf.stem] = data["name"]

print("=== DSL musician names (from musician YAML files) ===")
for stem, name in sorted(musician_names.items()):
    print(f"  {stem}: '{name}'")

print("\n=== James assembly: channel->musician mapping ===")
with open("data/dsl/teams/james/assembly.yaml") as f:
    james_assembly = yaml.safe_load(f)

print("Channel assignments:")
for ch_num, musician in sorted(james_assembly["channels"].items()):
    snap_name = james.get("ae_data", {}).get("ch", {}).get(str(ch_num), {}).get("name", "")
    # Find DSL name for this musician
    # The musician in assembly is the key in musicians block
    # which may inherit from a musician file
    musicians_block = james_assembly.get("musicians", {})
    mdata = musicians_block.get(musician, {})
    inherits = mdata.get("inherits", [])
    dsl_name = None
    for inh in inherits:
        stem = Path(inh).stem
        if stem in musician_names:
            dsl_name = musician_names[stem]
            break
    print(f"  ch {ch_num:2d} = {musician:<20} DSL name='{dsl_name or '(no name)'}' snap='{snap_name}'")

print("\n=== Bus names: DSL assembly buses vs snap names ===")
buses = james_assembly.get("buses", {})
print("Assembly bus mapping:")
for bus_num, logical_name in sorted(buses.items()):
    snap_name = james.get("ae_data", {}).get("bus", {}).get(str(bus_num), {}).get("name", "")
    base_name = base.get("ae_data", {}).get("bus", {}).get(str(bus_num), {}).get("name", "")
    print(f"  bus {bus_num:2d} = '{logical_name:<20}' snap='{snap_name}' base='{base_name}'")

print("\n=== Channels named in James.snap but NOT in DSL ===")
dsl_channels = set(james_assembly["channels"].keys())
for i in range(1, 41):
    snap_name = james.get("ae_data", {}).get("ch", {}).get(str(i), {}).get("name", "")
    if snap_name and i not in dsl_channels:
        base_name = base.get("ae_data", {}).get("ch", {}).get(str(i), {}).get("name", "")
        print(f"  ch {i:2d}: snap='{snap_name}' base='{base_name}' (source: {'Base.snap' if base_name else 'manual/unknown'})")

print("\n=== Name mismatches: DSL name vs snap name ===")
for ch_num, musician in sorted(james_assembly["channels"].items()):
    snap_name = james.get("ae_data", {}).get("ch", {}).get(str(ch_num), {}).get("name", "")
    musicians_block = james_assembly.get("musicians", {})
    mdata = musicians_block.get(musician, {})
    inherits = mdata.get("inherits", [])
    dsl_name = None
    for inh in inherits:
        stem = Path(inh).stem
        if stem in musician_names:
            dsl_name = musician_names[stem]
            break
    if dsl_name and snap_name and dsl_name != snap_name:
        print(f"  ch {ch_num:2d} ({musician}): DSL='{dsl_name}' snap='{snap_name}' MISMATCH")
    elif not dsl_name:
        print(f"  ch {ch_num:2d} ({musician}): no DSL name (inherits={inherits})")
