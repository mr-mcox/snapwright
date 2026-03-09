import json


def load_snap(path):
    with open(path) as f:
        return json.load(f)


snaps = {}
snaps["James"] = load_snap("data/reference/sunday-starters/James.snap")
snaps["Levin"] = load_snap("data/reference/sunday-starters/Levin.snap")
snaps["Jen"] = load_snap("data/reference/sunday-starters/Jen.snap")
snaps["Priscilla"] = load_snap("data/reference/sunday-starters/pricilla team.snap")
snaps["Morks"] = load_snap("data/reference/sunday-starters/Morks~2025.snap")
snaps["Kana"] = load_snap("data/reference/sunday-starters/Kana's Team from base.snap")

base = load_snap("data/reference/Base.snap")
init = load_snap("data/reference/Init.snap")

ae_sections = [
    ("ch", range(1, 41)),
    ("bus", range(1, 17)),
    ("dca", range(1, 17)),
    ("mgrp", range(1, 9)),
    ("main", range(1, 5)),
    ("mtx", range(1, 9)),
    ("aux", range(1, 9)),
]

for section, indices in ae_sections:
    print(f"\n{'=' * 100}")
    print(f"Section: ae_data.{section}")
    print(f"{'=' * 100}")
    teams = list(snaps.keys())
    header = f"{'idx':<5} {'Init':<18} {'Base':<20} " + " ".join(
        f"{t:<18}" for t in teams
    )
    print(header)
    print("-" * 160)
    for i in indices:
        key = str(i)
        init_name = (
            init.get("ae_data", {}).get(section, {}).get(key, {}).get("name", "")
        )
        base_name = (
            base.get("ae_data", {}).get(section, {}).get(key, {}).get("name", "")
        )
        names = []
        all_same_across_teams = True
        first_team = None
        for t in teams:
            n = (
                snaps[t]
                .get("ae_data", {})
                .get(section, {})
                .get(key, {})
                .get("name", "")
            )
            names.append(n)
            if first_team is None:
                first_team = n
            elif n != first_team:
                all_same_across_teams = False
        row = f"{i:<5} {str(init_name):<18} {str(base_name):<20} " + " ".join(
            f"{str(n):<18}" for n in names
        )
        marker = "  [INFRA]" if all_same_across_teams else ""
        print(row + marker)
