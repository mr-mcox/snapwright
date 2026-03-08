"""
Find infrastructure channels: channels named in ALL team snapshots with consistent names.
These are candidates for addition to Base.snap or dedicated DSL management.
"""
import json

def load_snap(path):
    with open(path) as f:
        return json.load(f)

snaps = {
    "James": load_snap("data/reference/sunday-starters/James.snap"),
    "Levin": load_snap("data/reference/sunday-starters/Levin.snap"),
    "Jen": load_snap("data/reference/sunday-starters/Jen.snap"),
    "Priscilla": load_snap("data/reference/sunday-starters/pricilla team.snap"),
    "Morks": load_snap("data/reference/sunday-starters/Morks~2025.snap"),
    "Kana": load_snap("data/reference/sunday-starters/Kana's Team from base.snap"),
}
base = load_snap("data/reference/Base.snap")
init = load_snap("data/reference/Init.snap")

teams = list(snaps.keys())

print("=== Channels: infrastructure vs team-specific classification ===")
print()
print("Legend:")
print("  [INFRA-NAMED]  = same non-empty name across ALL teams -> likely infrastructure")
print("  [INFRA-EMPTY]  = empty across all teams -> likely unused")
print("  [SEMI-INFRA]   = named in some teams with same name, empty in others -> partially managed")
print("  [TEAM-SPECIFIC]= different names across teams -> team-assigned")
print()

for i in range(1, 41):
    key = str(i)
    names_by_team = {t: snaps[t].get("ae_data", {}).get("ch", {}).get(key, {}).get("name", "") for t in teams}
    base_name = base.get("ae_data", {}).get("ch", {}).get(key, {}).get("name", "")
    
    unique_names = set(names_by_team.values())
    all_empty = unique_names == {""}
    all_same = len(unique_names) == 1
    non_empty = [n for n in names_by_team.values() if n]
    
    if all_empty:
        category = "[INFRA-EMPTY] "
    elif all_same:
        category = "[INFRA-NAMED] "
    elif len(set(n for n in non_empty)) == 1:
        # Some teams have name, others empty, but all non-empty are same
        category = "[SEMI-INFRA]  "
    else:
        category = "[TEAM-SPECIFIC]"
    
    sample_name = non_empty[0] if non_empty else ""
    teams_with_name = [t for t, n in names_by_team.items() if n]
    
    if not all_empty:
        base_note = f" base='{base_name}'" if base_name else " (not in Base)"
        print(f"  ch {i:2d} {category} '{sample_name}'{base_note}")
        if not all_same:
            for t in teams:
                n = names_by_team[t]
                if n and n != sample_name:
                    print(f"         {t}: '{n}'")
                elif not n:
                    print(f"         {t}: (empty)")

print()
print("=== Channels with non-DSL names that appear consistently ===")
print("These are channels not in the James DSL that show up consistently across teams:")
print()

dsl_channels = {1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 16, 25, 26, 27, 28, 37, 38}  # James DSL channels

for i in range(1, 41):
    if i in dsl_channels:
        continue
    key = str(i)
    names_by_team = {t: snaps[t].get("ae_data", {}).get("ch", {}).get(key, {}).get("name", "") for t in teams}
    non_empty = [n for n in names_by_team.values() if n]
    if not non_empty:
        continue
    
    unique_non_empty = set(non_empty)
    consistency = f"{len(non_empty)}/{len(teams)} teams named it"
    if len(unique_non_empty) == 1:
        print(f"  ch {i:2d}: '{non_empty[0]}' ({consistency}, same name)")
    else:
        print(f"  ch {i:2d}: multiple names {unique_non_empty} ({consistency})")
