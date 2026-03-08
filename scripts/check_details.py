#!/usr/bin/env python3
import json
b = json.load(open('data/reference/Base.snap'))
ae = b['ae_data']

print("=== FX SLOTS ===")
for n in [str(i) for i in range(1, 17)]:
    fx = ae['fx'].get(n, {})
    mdl = fx.get('mdl', 'NONE')
    name = fx.get('name', '')
    if mdl != 'NONE':
        params = list({k: v for k, v in fx.items() if k not in ['mdl', 'name']}.keys())
        print(f"  fx{int(n):02d}: mdl={mdl} name={repr(name)} param_keys={params[:8]}")

print()
print("=== AUX INPUTS (full) ===")
for n in [str(i) for i in range(1, 9)]:
    aux = ae['aux'].get(n, {})
    name = aux.get('name', '')
    fdr = aux.get('fdr', 0)
    col = aux.get('col', 1)
    icon = aux.get('icon', 0)
    mute = aux.get('mute', False)
    # Main send
    main = aux.get('main', {})
    main1 = main.get('1', {})
    print(f"  aux{int(n):02d}: name={repr(name)} fdr={fdr:.1f} col={col} icon={icon} mute={mute} main1={main1}")

print()
print("=== MATRIX (full) ===")
for n in [str(i) for i in range(1, 9)]:
    mtx = ae['mtx'].get(n, {})
    name = mtx.get('name', '')
    fdr = mtx.get('fdr', -144)
    col = mtx.get('col', 1)
    mute = mtx.get('mute', False)
    print(f"  mtx{int(n):02d}: name={repr(name)} fdr={fdr:.1f} col={col} mute={mute}")
    # Source sends
    send = mtx.get('send', {})
    for sn, sv in sorted(send.items(), key=lambda x: int(x[0])):
        if isinstance(sv, dict) and sv.get('on', False):
            lvl = sv.get('lvl', sv.get('l', -144))
            print(f"    send[{sn}]: on=True lvl={lvl:.1f}")

print()
print("=== MAIN OUTPUTS (full) ===")
for n in [str(i) for i in range(1, 5)]:
    main = ae['main'].get(n, {})
    name = main.get('name', '')
    fdr = main.get('fdr', -144)
    mute = main.get('mute', False)
    icon = main.get('icon', 0)
    eq = main.get('eq', {})
    eq_on = eq.get('on', False)
    dyn = main.get('dyn', {})
    dyn_on = dyn.get('on', False)
    print(f"  main{int(n):02d}: name={repr(name)} fdr={fdr:.1f} mute={mute} icon={icon} eq_on={eq_on} dyn_on={dyn_on}")

print()
print("=== ae_data.cfg - Talkback assignment ===")
cfg = ae['cfg']
talk = cfg.get('talk', {})
print(f"  talk.assign: {talk.get('assign', 'OFF')}")
talkA = talk.get('A', {})
print(f"  talk.A buses: {[(k,v) for k,v in talkA.items() if v and k.startswith('B')]}")
print(f"  talk.A.busdim: {talkA.get('busdim', 0)}")

mon = cfg.get('mon', {})
for mk, mv in mon.items():
    if isinstance(mv, dict):
        print(f"  mon.{mk}.srclvl: {mv.get('srclvl', 'n/a')}")
        print(f"  mon.{mk}.pfldim: {mv.get('pfldim', 'n/a')}")

print()
print("=== ce_data.cfg - Console engine config ===")
ce_cfg = b['ce_data']['cfg']
for k, v in sorted(ce_cfg.items()):
    if not isinstance(v, dict):
        print(f"  {k}: {v}")

print()
print("=== Channel sends (ch01 as example) ===")
ch1 = ae['ch']['1']
sends = ch1.get('send', {})
for sn in sorted(sends.keys(), key=lambda x: int(x)):
    sv = sends[sn]
    if isinstance(sv, dict):
        on = sv.get('on', False)
        lvl = sv.get('lvl', sv.get('l', -144))
        mode = sv.get('mode', sv.get('m', ''))
        print(f"  send[{sn}]: on={on} lvl={lvl:.1f} mode={mode}")
