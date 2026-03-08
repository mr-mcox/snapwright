#!/usr/bin/env python3
import json

james = json.load(open('data/reference/sunday-starters/James.snap'))
base = json.load(open('data/reference/Base.snap'))

print("=== BUS NAMES: Base vs James ===")
print(f"{'Bus':<6} {'Base.snap':<25} {'James.snap':<25}")
print("-" * 58)
for n in [str(i) for i in range(1, 17)]:
    b_name = base['ae_data']['bus'].get(n, {}).get('name', '')
    j_name = james['ae_data']['bus'].get(n, {}).get('name', '')
    if b_name or j_name:
        marker = "  <-- DIFF" if b_name != j_name else ""
        print(f"bus{int(n):02d}: {b_name:<25} {j_name:<25}{marker}")

print()
print("=== DCA NAMES/FADERS: Base vs James ===")
print(f"{'DCA':<6} {'Base name':<15} {'Base fdr':>10} {'James name':<15} {'James fdr':>10}")
print("-" * 60)
for n in [str(i) for i in range(1, 17)]:
    b_dca = base['ae_data']['dca'].get(n, {})
    j_dca = james['ae_data']['dca'].get(n, {})
    b_name = b_dca.get('name', '')
    j_name = j_dca.get('name', '')
    b_fdr = b_dca.get('fdr', -144)
    j_fdr = j_dca.get('fdr', -144)
    if b_name or j_name:
        print(f"dca{int(n):02d}: {b_name:<15} {b_fdr:>10.1f}   {j_name:<15} {j_fdr:>10.1f}")

print()
print("=== MGRP NAMES: Base vs James ===")
for n in [str(i) for i in range(1, 9)]:
    b_mg = base['ae_data']['mgrp'].get(n, {})
    j_mg = james['ae_data']['mgrp'].get(n, {})
    b_name = b_mg.get('name', '')
    j_name = j_mg.get('name', '')
    b_mute = b_mg.get('mute', False)
    j_mute = j_mg.get('mute', False)
    print(f"mgrp{int(n):02d}: base={b_name!r} mute={b_mute}  james={j_name!r} mute={j_mute}")

print()
print("=== CHANNEL NAMES: Base vs James ===")
print(f"{'Ch':<5} {'Base name':<20} {'Base src':<12} {'James name':<20} {'James src':<12}")
print("-" * 72)
for n in [str(i) for i in range(1, 41)]:
    b_ch = base['ae_data']['ch'].get(n, {})
    j_ch = james['ae_data']['ch'].get(n, {})
    b_name = b_ch.get('name', '')
    j_name = j_ch.get('name', '')
    b_conn = b_ch.get('in', {}).get('conn', {})
    j_conn = j_ch.get('in', {}).get('conn', {})
    b_src = f"{b_conn.get('grp','OFF')}.{b_conn.get('in',1)}"
    j_src = f"{j_conn.get('grp','OFF')}.{j_conn.get('in',1)}"
    if b_name or j_name:
        print(f"ch{int(n):02d}: {b_name:<20} {b_src:<12} {j_name:<20} {j_src:<12}")
