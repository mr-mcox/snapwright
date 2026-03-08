#!/usr/bin/env python3
"""
Focused audit of Base.snap vs Init.snap for Investigation A.
Targets meaningful human-configured fields rather than doing a raw leaf diff.
"""

import json
from typing import Any


BASE = "/Users/mcox/dev/snapwright/data/reference/Base.snap"
INIT = "/Users/mcox/Documents/Wing Backup/Init.snap"

base = json.load(open(BASE))
init = json.load(open(INIT))

ae_b = base["ae_data"]
ae_i = init["ae_data"]
ce_b = base["ce_data"]
ce_i = init["ce_data"]


def fmt_fdr(v):
    if v == -144 or v == -144.0:
        return "-inf dB"
    return f"{v:.1f} dB"


def ch_num_label(n):
    return f"ch{int(n):02d}"


# ============================================================
# 1. CHANNELS - names, colors, icons, faders, mutes, processing on/off
# ============================================================
print("=" * 70)
print("CHANNELS (ae_data.ch)")
print("=" * 70)

INIT_NAME_DEFAULT = ""
INIT_FDR_DEFAULT = -144.0
INIT_MUTE_DEFAULT = False
INIT_COL_DEFAULT = 1
INIT_ICON_DEFAULT = 0
INIT_TAGS_DEFAULT = ""

ch_rows = []
for n in [str(i) for i in range(1, 41)]:
    b_ch = ae_b["ch"].get(n, {})
    i_ch = ae_i["ch"].get(n, {})
    label = ch_num_label(n)

    # Name
    b_name = b_ch.get("name", "")
    i_name = i_ch.get("name", "")
    if b_name != i_name:
        ch_rows.append(("name", label, i_name or "(blank)", b_name or "(blank)"))

    # Fader
    b_fdr = b_ch.get("fdr", -144.0)
    i_fdr = i_ch.get("fdr", -144.0)
    if abs(float(b_fdr) - float(i_fdr)) > 0.01:
        ch_rows.append(("fader", label, fmt_fdr(i_fdr), fmt_fdr(b_fdr)))

    # Color
    b_col = b_ch.get("col", 1)
    i_col = i_ch.get("col", 1)
    if b_col != i_col:
        ch_rows.append(("color", label, i_col, b_col))

    # Icon
    b_icon = b_ch.get("icon", 0)
    i_icon = i_ch.get("icon", 0)
    if b_icon != i_icon:
        ch_rows.append(("icon", label, i_icon, b_icon))

    # Mute
    b_mute = b_ch.get("mute", False)
    i_mute = i_ch.get("mute", False)
    if b_mute != i_mute:
        ch_rows.append(("mute", label, i_mute, b_mute))

    # Tags
    b_tags = b_ch.get("tags", "")
    i_tags = i_ch.get("tags", "")
    if b_tags != i_tags:
        ch_rows.append(("tags", label, i_tags or "(blank)", b_tags or "(blank)"))

    # Input routing
    b_in = b_ch.get("in", {})
    i_in = i_ch.get("in", {})
    # Check input source
    b_insrc = b_in.get("src", b_in.get("s", ""))
    i_insrc = i_in.get("src", i_in.get("s", ""))
    if b_insrc != i_insrc:
        ch_rows.append(("input.src", label, i_insrc or "(none)", b_insrc or "(none)"))

    # HPF
    b_flt = b_ch.get("flt", {})
    i_flt = i_ch.get("flt", {})
    b_hpf = b_flt.get("lc", b_flt.get("hp", 0))
    i_hpf = i_flt.get("lc", i_flt.get("hp", 0))
    b_hpf_on = b_flt.get("lcon", b_flt.get("hpon", False))
    i_hpf_on = i_flt.get("lcon", i_flt.get("hpon", False))
    if b_hpf_on != i_hpf_on or (b_hpf_on and abs(float(b_hpf) - float(i_hpf)) > 1.0):
        ch_rows.append(("HPF", label, f"{'ON' if i_hpf_on else 'OFF'} @ {i_hpf:.0f}Hz",
                         f"{'ON' if b_hpf_on else 'OFF'} @ {b_hpf:.0f}Hz"))

    # Gate on/off
    b_gate = b_ch.get("gate", {})
    i_gate = i_ch.get("gate", {})
    b_gate_on = b_gate.get("on", False)
    i_gate_on = i_gate.get("on", False)
    if b_gate_on != i_gate_on:
        ch_rows.append(("gate.on", label, i_gate_on, b_gate_on))

    # Dyn on/off
    b_dyn = b_ch.get("dyn", {})
    i_dyn = i_ch.get("dyn", {})
    b_dyn_on = b_dyn.get("on", False)
    i_dyn_on = i_dyn.get("on", False)
    if b_dyn_on != i_dyn_on:
        ch_rows.append(("dyn.on", label, i_dyn_on, b_dyn_on))


# Print channel table
print(f"\n{'Field':<12} {'Channel':<8} {'Init':<25} {'Base':<35}")
print("-" * 82)
for field, label, iv, bv in ch_rows:
    print(f"{field:<12} {label:<8} {str(iv):<25} {str(bv):<35}")


# ============================================================
# 2. BUSES
# ============================================================
print("\n" + "=" * 70)
print("BUSES (ae_data.bus)")
print("=" * 70)

bus_rows = []
for n in [str(i) for i in range(1, 17)]:
    b_bus = ae_b["bus"].get(n, {})
    i_bus = ae_i["bus"].get(n, {})
    label = f"bus{int(n):02d}"

    b_name = b_bus.get("name", "")
    i_name = i_bus.get("name", "")
    if b_name != i_name:
        bus_rows.append(("name", label, i_name or "(blank)", b_name or "(blank)"))

    b_fdr = b_bus.get("fdr", -144.0)
    i_fdr = i_bus.get("fdr", -144.0)
    if abs(float(b_fdr) - float(i_fdr)) > 0.01:
        bus_rows.append(("fader", label, fmt_fdr(i_fdr), fmt_fdr(b_fdr)))

    b_col = b_bus.get("col", 1)
    i_col = i_bus.get("col", 1)
    if b_col != i_col:
        bus_rows.append(("color", label, i_col, b_col))

    b_mute = b_bus.get("mute", False)
    i_mute = i_bus.get("mute", False)
    if b_mute != i_mute:
        bus_rows.append(("mute", label, i_mute, b_mute))

    b_tags = b_bus.get("tags", "")
    i_tags = i_bus.get("tags", "")
    if b_tags != i_tags:
        bus_rows.append(("tags", label, i_tags or "(blank)", b_tags or "(blank)"))

print(f"\n{'Field':<12} {'Bus':<8} {'Init':<30} {'Base':<35}")
print("-" * 87)
for field, label, iv, bv in bus_rows:
    print(f"{field:<12} {label:<8} {str(iv):<30} {str(bv):<35}")


# ============================================================
# 3. DCAs
# ============================================================
print("\n" + "=" * 70)
print("DCAs (ae_data.dca)")
print("=" * 70)

dca_rows = []
for n in [str(i) for i in range(1, 17)]:
    b_dca = ae_b["dca"].get(n, {})
    i_dca = ae_i["dca"].get(n, {})
    label = f"dca{int(n):02d}"

    b_name = b_dca.get("name", "")
    i_name = i_dca.get("name", "")
    if b_name != i_name:
        dca_rows.append(("name", label, i_name or "(blank)", b_name or "(blank)"))

    b_fdr = b_dca.get("fdr", 0.0)
    i_fdr = i_dca.get("fdr", 0.0)
    if abs(float(b_fdr) - float(i_fdr)) > 0.01:
        dca_rows.append(("fader", label, fmt_fdr(i_fdr), fmt_fdr(b_fdr)))

    b_mute = b_dca.get("mute", False)
    i_mute = i_dca.get("mute", False)
    if b_mute != i_mute:
        dca_rows.append(("mute", label, i_mute, b_mute))

    b_col = b_dca.get("col", 1)
    i_col = i_dca.get("col", 1)
    if b_col != i_col:
        dca_rows.append(("color", label, i_col, b_col))

print(f"\n{'Field':<12} {'DCA':<8} {'Init':<20} {'Base':<35}")
print("-" * 77)
for field, label, iv, bv in dca_rows:
    print(f"{field:<12} {label:<8} {str(iv):<20} {str(bv):<35}")


# ============================================================
# 4. MUTE GROUPS
# ============================================================
print("\n" + "=" * 70)
print("MUTE GROUPS (ae_data.mgrp)")
print("=" * 70)

mgrp_rows = []
for n in [str(i) for i in range(1, 9)]:
    b_mg = ae_b["mgrp"].get(n, {})
    i_mg = ae_i["mgrp"].get(n, {})
    label = f"mgrp{int(n):02d}"

    b_name = b_mg.get("name", "")
    i_name = i_mg.get("name", "")
    if b_name != i_name:
        mgrp_rows.append(("name", label, i_name or "(blank)", b_name or "(blank)"))

    b_mute = b_mg.get("mute", False)
    i_mute = i_mg.get("mute", False)
    if b_mute != i_mute:
        mgrp_rows.append(("mute", label, i_mute, b_mute))

print(f"\n{'Field':<12} {'MGrp':<8} {'Init':<20} {'Base':<35}")
print("-" * 77)
for field, label, iv, bv in mgrp_rows:
    print(f"{field:<12} {label:<8} {str(iv):<20} {str(bv):<35}")


# ============================================================
# 5. MAINS
# ============================================================
print("\n" + "=" * 70)
print("MAINS (ae_data.main)")
print("=" * 70)

main_rows = []
for n in [str(i) for i in range(1, 5)]:
    b_main = ae_b["main"].get(n, {})
    i_main = ae_i["main"].get(n, {})
    label = f"main{int(n):02d}"

    b_name = b_main.get("name", "")
    i_name = i_main.get("name", "")
    if b_name != i_name:
        main_rows.append(("name", label, i_name or "(blank)", b_name or "(blank)"))

    b_fdr = b_main.get("fdr", -144.0)
    i_fdr = i_main.get("fdr", -144.0)
    if abs(float(b_fdr) - float(i_fdr)) > 0.01:
        main_rows.append(("fader", label, fmt_fdr(i_fdr), fmt_fdr(b_fdr)))

    b_mute = b_main.get("mute", False)
    i_mute = i_main.get("mute", False)
    if b_mute != i_mute:
        main_rows.append(("mute", label, i_mute, b_mute))

    b_col = b_main.get("col", 1)
    i_col = i_main.get("col", 1)
    if b_col != i_col:
        main_rows.append(("color", label, i_col, b_col))

    b_icon = b_main.get("icon", 0)
    i_icon = i_main.get("icon", 0)
    if b_icon != i_icon:
        main_rows.append(("icon", label, i_icon, b_icon))

print(f"\n{'Field':<12} {'Main':<8} {'Init':<20} {'Base':<35}")
print("-" * 77)
for field, label, iv, bv in main_rows:
    print(f"{field:<12} {label:<8} {str(iv):<20} {str(bv):<35}")


# ============================================================
# 6. AUX INPUTS
# ============================================================
print("\n" + "=" * 70)
print("AUX INPUTS (ae_data.aux)")
print("=" * 70)

aux_rows = []
for n in [str(i) for i in range(1, 9)]:
    b_aux = ae_b["aux"].get(n, {})
    i_aux = ae_i["aux"].get(n, {})
    label = f"aux{int(n):02d}"

    b_name = b_aux.get("name", "")
    i_name = i_aux.get("name", "")
    if b_name != i_name:
        aux_rows.append(("name", label, i_name or "(blank)", b_name or "(blank)"))

    b_col = b_aux.get("col", 1)
    i_col = i_aux.get("col", 1)
    if b_col != i_col:
        aux_rows.append(("color", label, i_col, b_col))

    b_icon = b_aux.get("icon", 0)
    i_icon = i_aux.get("icon", 0)
    if b_icon != i_icon:
        aux_rows.append(("icon", label, i_icon, b_icon))

    b_fdr = b_aux.get("fdr", 0.0)
    i_fdr = i_aux.get("fdr", 0.0)
    if abs(float(b_fdr) - float(i_fdr)) > 0.01:
        aux_rows.append(("fader", label, fmt_fdr(i_fdr), fmt_fdr(b_fdr)))

    b_mute = b_aux.get("mute", False)
    i_mute = i_aux.get("mute", False)
    if b_mute != i_mute:
        aux_rows.append(("mute", label, i_mute, b_mute))

    b_tags = b_aux.get("tags", "")
    i_tags = i_aux.get("tags", "")
    if b_tags != i_tags:
        aux_rows.append(("tags", label, i_tags or "(blank)", b_tags or "(blank)"))

print(f"\n{'Field':<12} {'Aux':<8} {'Init':<20} {'Base':<35}")
print("-" * 77)
for field, label, iv, bv in aux_rows:
    print(f"{field:<12} {label:<8} {str(iv):<20} {str(bv):<35}")


# ============================================================
# 7. MATRIX
# ============================================================
print("\n" + "=" * 70)
print("MATRIX (ae_data.mtx)")
print("=" * 70)

mtx_rows = []
for n in [str(i) for i in range(1, 9)]:
    b_mtx = ae_b["mtx"].get(n, {})
    i_mtx = ae_i["mtx"].get(n, {})
    label = f"mtx{int(n):02d}"

    b_name = b_mtx.get("name", "")
    i_name = i_mtx.get("name", "")
    if b_name != i_name:
        mtx_rows.append(("name", label, i_name or "(blank)", b_name or "(blank)"))

    b_col = b_mtx.get("col", 1)
    i_col = i_mtx.get("col", 1)
    if b_col != i_col:
        mtx_rows.append(("color", label, i_col, b_col))

    b_fdr = b_mtx.get("fdr", -144.0)
    i_fdr = i_mtx.get("fdr", -144.0)
    if abs(float(b_fdr) - float(i_fdr)) > 0.01:
        mtx_rows.append(("fader", label, fmt_fdr(i_fdr), fmt_fdr(b_fdr)))

    b_mute = b_mtx.get("mute", False)
    i_mute = i_mtx.get("mute", False)
    if b_mute != i_mute:
        mtx_rows.append(("mute", label, i_mute, b_mute))

print(f"\n{'Field':<12} {'Mtx':<8} {'Init':<20} {'Base':<35}")
print("-" * 77)
for field, label, iv, bv in mtx_rows:
    print(f"{field:<12} {label:<8} {str(iv):<20} {str(bv):<35}")


# ============================================================
# 8. FX SLOTS
# ============================================================
print("\n" + "=" * 70)
print("FX SLOTS (ae_data.fx)")
print("=" * 70)

fx_rows = []
for n in [str(i) for i in range(1, 17)]:
    b_fx = ae_b["fx"].get(n, {})
    i_fx = ae_i["fx"].get(n, {})
    label = f"fx{int(n):02d}"

    b_name = b_fx.get("name", "")
    i_name = i_fx.get("name", "")
    if b_name != i_name:
        fx_rows.append(("name", label, i_name or "(blank)", b_name or "(blank)"))

    b_mdl = b_fx.get("mdl", "")
    i_mdl = i_fx.get("mdl", "")
    if b_mdl != i_mdl:
        fx_rows.append(("model", label, i_mdl or "(blank)", b_mdl or "(blank)"))

print(f"\n{'Field':<12} {'FX':<8} {'Init':<30} {'Base':<35}")
print("-" * 87)
for field, label, iv, bv in fx_rows:
    print(f"{field:<12} {label:<8} {str(iv):<30} {str(bv):<35}")


# ============================================================
# 9. IO - Physical input routing
# ============================================================
print("\n" + "=" * 70)
print("IO INPUTS (ae_data.io.in)")
print("=" * 70)

io_rows = []
io_b = ae_b["io"]
io_i = ae_i["io"]

for group in sorted(io_b["in"].keys()):
    b_grp = io_b["in"].get(group, {})
    i_grp = io_i["in"].get(group, {})

    all_inputs = sorted(set(list(b_grp.keys()) + list(i_grp.keys())), key=lambda x: int(x) if x.isdigit() else 99)
    for inp in all_inputs:
        b_in = b_grp.get(inp, {})
        i_in = i_grp.get(inp, {})
        label = f"io.in.{group}.{inp}"

        b_name = b_in.get("name", "")
        i_name = i_in.get("name", "")
        if b_name != i_name:
            io_rows.append(("name", label, i_name or "(blank)", b_name or "(blank)"))

        b_g = b_in.get("g", 0)
        i_g = i_in.get("g", 0)
        if abs(float(b_g) - float(i_g)) > 0.1:
            io_rows.append(("gain(dB)", label, f"{i_g}", f"{b_g}"))

        b_ph = b_in.get("vph", False)
        i_ph = i_in.get("vph", False)
        if b_ph != i_ph:
            io_rows.append(("+48V", label, i_ph, b_ph))

        b_tags = b_in.get("tags", "")
        i_tags = i_in.get("tags", "")
        if b_tags != i_tags:
            io_rows.append(("tags", label, i_tags or "(blank)", b_tags or "(blank)"))

        b_col = b_in.get("col", 1)
        i_col = i_in.get("col", 1)
        if b_col != i_col:
            io_rows.append(("color", label, i_col, b_col))

        b_icon = b_in.get("icon", 1)
        i_icon = i_in.get("icon", 1)
        if b_icon != i_icon:
            io_rows.append(("icon", label, i_icon, b_icon))

print(f"\n{'Field':<12} {'Path':<30} {'Init':<20} {'Base':<35}")
print("-" * 99)
for field, label, iv, bv in io_rows:
    print(f"{field:<12} {label:<30} {str(iv):<20} {str(bv):<35}")


# ============================================================
# 10. IO OUTPUTS
# ============================================================
print("\n" + "=" * 70)
print("IO OUTPUTS (ae_data.io.out)")
print("=" * 70)

io_out_rows = []
for group in sorted(io_b["out"].keys()):
    b_grp = io_b["out"].get(group, {})
    i_grp = io_i["out"].get(group, {})

    all_outputs = sorted(set(list(b_grp.keys()) + list(i_grp.keys())), key=lambda x: int(x) if x.isdigit() else 99)
    for out in all_outputs:
        b_out = b_grp.get(out, {})
        i_out = i_grp.get(out, {})
        label = f"io.out.{group}.{out}"

        b_src = b_out.get("src", b_out.get("s", ""))
        i_src = i_out.get("src", i_out.get("s", ""))
        if b_src != i_src:
            io_out_rows.append(("src", label, i_src or "(none)", b_src or "(none)"))

        b_name = b_out.get("name", "")
        i_name = i_out.get("name", "")
        if b_name != i_name:
            io_out_rows.append(("name", label, i_name or "(blank)", b_name or "(blank)"))

        b_g = b_out.get("g", 0)
        i_g = i_out.get("g", 0)
        if abs(float(b_g) - float(i_g)) > 0.1:
            io_out_rows.append(("gain(dB)", label, f"{i_g}", f"{b_g}"))

print(f"\n{'Field':<12} {'Path':<30} {'Init':<20} {'Base':<35}")
print("-" * 99)
for field, label, iv, bv in io_out_rows:
    print(f"{field:<12} {label:<30} {str(iv):<20} {str(bv):<35}")


# ============================================================
# 11. CONSOLE CFG
# ============================================================
print("\n" + "=" * 70)
print("CONSOLE CFG (ae_data.cfg)")
print("=" * 70)

def flatten_cfg(obj, prefix=""):
    result = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}.{k}" if prefix else k
            result.update(flatten_cfg(v, new_key))
    elif isinstance(obj, list):
        for idx, v in enumerate(obj):
            result.update(flatten_cfg(v, f"{prefix}[{idx}]"))
    else:
        result[prefix] = obj
    return result

cfg_b = flatten_cfg(ae_b["cfg"])
cfg_i = flatten_cfg(ae_i["cfg"])

cfg_rows = []
for k in sorted(set(cfg_b.keys()) | set(cfg_i.keys())):
    bv = cfg_b.get(k, "__MISSING__")
    iv = cfg_i.get(k, "__MISSING__")
    if bv != iv:
        cfg_rows.append((k, iv, bv))

print(f"\n{'Path':<40} {'Init':<20} {'Base':<30}")
print("-" * 92)
for path, iv, bv in cfg_rows:
    print(f"{path:<40} {str(iv):<20} {str(bv):<30}")


# ============================================================
# 12. ce_data.cfg
# ============================================================
print("\n" + "=" * 70)
print("CONSOLE ENGINE CFG (ce_data.cfg)")
print("=" * 70)

cecfg_b = flatten_cfg(ce_b["cfg"])
cecfg_i = flatten_cfg(ce_i["cfg"])

cecfg_rows = []
for k in sorted(set(cecfg_b.keys()) | set(cecfg_i.keys())):
    bv = cecfg_b.get(k, "__MISSING__")
    iv = cecfg_i.get(k, "__MISSING__")
    if bv != iv:
        cecfg_rows.append((k, iv, bv))

print(f"\n{'Path':<50} {'Init':<20} {'Base':<30}")
print("-" * 102)
for path, iv, bv in cecfg_rows:
    print(f"{path:<50} {str(iv):<20} {str(bv):<30}")


# ============================================================
# 13. Channel processing details - show EQ/gate/dyn settings for named channels
# ============================================================
print("\n" + "=" * 70)
print("CHANNEL PROCESSING DETAIL (channels with non-default names in Base)")
print("=" * 70)

for n in [str(i) for i in range(1, 41)]:
    b_ch = ae_b["ch"].get(n, {})
    name = b_ch.get("name", "")
    if not name:
        continue

    label = f"ch{int(n):02d} ({name})"
    fdr = b_ch.get("fdr", -144.0)
    col = b_ch.get("col", 1)
    mute = b_ch.get("mute", False)
    tags = b_ch.get("tags", "")

    # Input
    b_in = b_ch.get("in", {})
    insrc = b_in.get("src", b_in.get("s", "(none)"))

    # HPF
    b_flt = b_ch.get("flt", {})
    hpf_freq = b_flt.get("lc", b_flt.get("hp", 0))
    hpf_on = b_flt.get("lcon", b_flt.get("hpon", False))

    # Gate
    b_gate = b_ch.get("gate", {})
    gate_on = b_gate.get("on", False)
    gate_mdl = b_gate.get("mdl", "")
    gate_thr = b_gate.get("thr", 0)

    # Dyn
    b_dyn = b_ch.get("dyn", {})
    dyn_on = b_dyn.get("on", False)
    dyn_mdl = b_dyn.get("mdl", "")
    dyn_thr = b_dyn.get("thr", 0)

    # EQ
    b_eq = b_ch.get("eq", {})
    eq_on = b_eq.get("on", False)
    eq_mdl = b_eq.get("mdl", "")

    print(f"\n  {label}")
    print(f"    fdr={fmt_fdr(fdr)} mute={mute} col={col} tags={tags!r}")
    print(f"    input.src={insrc}")
    print(f"    HPF: on={hpf_on} freq={hpf_freq:.0f}Hz")
    print(f"    gate: on={gate_on} mdl={gate_mdl} thr={gate_thr:.1f}dB")
    print(f"    dyn:  on={dyn_on} mdl={dyn_mdl} thr={dyn_thr:.1f}dB")
    print(f"    eq:   on={eq_on} mdl={eq_mdl}")

    # Sends summary
    sends = b_ch.get("send", {})
    active_sends = []
    for sn, sv in sorted(sends.items(), key=lambda x: int(x[0])):
        if isinstance(sv, dict) and sv.get("on", False):
            lvl = sv.get("lvl", sv.get("l", -144.0))
            active_sends.append(f"bus{int(sn):02d}={fmt_fdr(lvl)}")
    if active_sends:
        print(f"    sends: {', '.join(active_sends)}")


# ============================================================
# 14. Safes summary
# ============================================================
print("\n" + "=" * 70)
print("SAFES (ce_data.safes)")
print("=" * 70)

safes_b = flatten_cfg(ce_b["safes"])
safes_i = flatten_cfg(ce_i["safes"])

safe_rows = []
for k in sorted(set(safes_b.keys()) | set(safes_i.keys())):
    bv = safes_b.get(k, "__MISSING__")
    iv = safes_i.get(k, "__MISSING__")
    if bv != iv:
        safe_rows.append((k, iv, bv))

if safe_rows:
    print(f"\n{'Path':<40} {'Init':<15} {'Base':<15}")
    print("-" * 72)
    for path, iv, bv in safe_rows:
        print(f"{path:<40} {str(iv):<15} {str(bv):<15}")
else:
    print("  No differences in safes")


# ============================================================
# 15. Bus send routing on Monitor buses
# ============================================================
print("\n" + "=" * 70)
print("BUS PROCESSING (named buses - full detail)")
print("=" * 70)

for n in [str(i) for i in range(1, 17)]:
    b_bus = ae_b["bus"].get(n, {})
    name = b_bus.get("name", "")
    if not name:
        continue

    label = f"bus{int(n):02d} ({name})"
    fdr = b_bus.get("fdr", -144.0)
    col = b_bus.get("col", 1)
    mute = b_bus.get("mute", False)
    tags = b_bus.get("tags", "")

    # HPF
    b_flt = b_bus.get("flt", {})
    hpf_freq = b_flt.get("lc", b_flt.get("hp", 0))
    hpf_on = b_flt.get("lcon", b_flt.get("hpon", False))

    # Dyn
    b_dyn = b_bus.get("dyn", {})
    dyn_on = b_dyn.get("on", False)
    dyn_mdl = b_dyn.get("mdl", "")
    dyn_thr = b_dyn.get("thr", 0)

    # EQ
    b_eq = b_bus.get("eq", {})
    eq_on = b_eq.get("on", False)
    eq_mdl = b_eq.get("mdl", "")

    print(f"\n  {label}")
    print(f"    fdr={fmt_fdr(fdr)} mute={mute} col={col} tags={tags!r}")
    print(f"    HPF: on={hpf_on} freq={hpf_freq:.0f}Hz")
    print(f"    dyn:  on={dyn_on} mdl={dyn_mdl} thr={dyn_thr:.1f}dB")
    print(f"    eq:   on={eq_on} mdl={eq_mdl}")
