import json

def load_snap(path):
    with open(path) as f:
        return json.load(f)

james_rendered = load_snap("data/dsl/teams/james/james-team.snap")
james_sunday = load_snap("data/reference/sunday-starters/James.snap")
base = load_snap("data/reference/Base.snap")

print("=== Bus names: Rendered vs Sunday Starter (James) ===")
print("The rendered snap gets bus names from snap_template (which is Base.snap)")
print("The Sunday Starter was manually saved after operator made changes on console")
print()
for i in range(1, 17):
    key = str(i)
    rendered_name = james_rendered.get("ae_data", {}).get("bus", {}).get(key, {}).get("name", "")
    sunday_name = james_sunday.get("ae_data", {}).get("bus", {}).get(key, {}).get("name", "")
    base_name = base.get("ae_data", {}).get("bus", {}).get(key, {}).get("name", "")
    same = rendered_name == sunday_name
    mark = "[match]" if same else "[DIFF]"
    print(f"  bus {i:2d}: rendered='{rendered_name:<20}' sunday='{sunday_name:<20}' base='{base_name:<20}' {mark}")

print("\n=== Channel name differences: Rendered vs Sunday Starter ===")
mismatch_count = 0
for i in range(1, 41):
    key = str(i)
    r = james_rendered.get("ae_data", {}).get("ch", {}).get(key, {}).get("name", "")
    s = james_sunday.get("ae_data", {}).get("ch", {}).get(key, {}).get("name", "")
    if r == s:
        continue
    print(f"  ch {i:2d}: rendered='{r}' sunday='{s}'")
    mismatch_count += 1
if mismatch_count == 0:
    print("  All channel names match!")

print("\n=== Key finding: bus names in snap_template (Base.snap origin) ===")
print("The renderer DOES NOT set bus names - they come from Base.snap via snap_template")
print("But the Sunday Starters show DIFFERENT bus names (Rhythm/House etc.) from Base (BASS, etc.)")
print("This means the Sunday Starters were saved AFTER manually renaming buses on the Wing")
print("The rendered snap uses Base.snap's STALE bus names!")
