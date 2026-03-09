#!/usr/bin/env python3
import json

b = json.load(open("data/reference/Base.snap"))
ce = b["ce_data"]
layer = ce.get("layer", {})

print("=== LAYER BANKS (Base.snap) ===")
for section in ["L", "C", "R"]:
    sec = layer[section]
    sel = sec.get("sel", 0)
    print(f"\nSection {section} (selected bank: {sel}):")
    for bk, bv in sec.items():
        if bk == "sel":
            continue
        if isinstance(bv, dict):
            name = bv.get("name", "")
            strips = [(k, v) for k, v in bv.items() if k not in ("ofs", "name")]
            strip_types = set(
                v.get("type", "") for k, v in strips if isinstance(v, dict)
            )
            strip_count = len([v for k, v in strips if isinstance(v, dict)])
            print(
                f"  Bank {bk}: {repr(name)} ({strip_count} strips) types={strip_types}"
            )

print()
print("=== USER LAYERS (Base.snap) ===")
user = ce.get("user", {})
print("User layer keys:", list(user.keys()))
for k, v in sorted(user.items()):
    if not isinstance(v, dict):
        continue
    strips = [(sk, sv) for sk, sv in v.items() if sk not in ("name", "sel")]
    active = []
    for sk, sv in strips:
        if isinstance(sv, dict):
            enc = sv.get("enc", "OFF")
            bu = sv.get("bu", "OFF")
            bd = sv.get("bd", "OFF")
            if enc != "OFF" or bu != "OFF" or bd != "OFF":
                active.append((sk, sv))
    if active:
        print(f"\n  user[{k}]: {len(active)} active strips")
        for sk, sv in sorted(active, key=lambda x: int(x[0]) if x[0].isdigit() else 99):
            enc = sv.get("enc", "OFF")
            bu = sv.get("bu", "OFF")
            bd = sv.get("bd", "OFF")
            col = sv.get("col", 0)
            print(f"    strip {sk}: enc={enc} bu={bu} bd={bd} col={col}")
    else:
        # Show all-OFF layers briefly
        pass

print()
print("=== LAYER BANKS DETAIL (Section L) ===")
L = layer["L"]
for bk, bv in sorted(L.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
    if bk == "sel":
        continue
    if not isinstance(bv, dict):
        continue
    name = bv.get("name", "")
    print(f"\nL.{bk} ({name!r}):")
    for sk, sv in sorted(bv.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
        if sk in ("ofs", "name"):
            continue
        if isinstance(sv, dict):
            t = sv.get("type", "")
            i = sv.get("i", "")
            dst = sv.get("dst", "")
            print(f"  strip {sk}: type={t} i={i} dst={dst}")

print()
print("=== LAYER BANKS DETAIL (Section C) ===")
C = layer["C"]
for bk, bv in sorted(C.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
    if bk == "sel":
        continue
    if not isinstance(bv, dict):
        continue
    name = bv.get("name", "")
    print(f"\nC.{bk} ({name!r}):")
    for sk, sv in sorted(bv.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
        if sk in ("ofs", "name"):
            continue
        if isinstance(sv, dict):
            t = sv.get("type", "")
            i = sv.get("i", "")
            dst = sv.get("dst", "")
            print(f"  strip {sk}: type={t} i={i} dst={dst}")

print()
print("=== LAYER BANKS DETAIL (Section R) ===")
R = layer["R"]
for bk, bv in sorted(R.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
    if bk == "sel":
        continue
    if not isinstance(bv, dict):
        continue
    name = bv.get("name", "")
    print(f"\nR.{bk} ({name!r}):")
    for sk, sv in sorted(bv.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
        if sk in ("ofs", "name"):
            continue
        if isinstance(sv, dict):
            t = sv.get("type", "")
            i = sv.get("i", "")
            dst = sv.get("dst", "")
            print(f"  strip {sk}: type={t} i={i} dst={dst}")
