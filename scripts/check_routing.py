#!/usr/bin/env python3
import json
base = json.load(open('data/reference/Base.snap'))
ae = base['ae_data']

print("=== MAIN OUTPUT DETAILS ===")
main = ae['main']
for n in ['1', '2', '3', '4']:
    m = main.get(n, {})
    name = m.get('name', '')
    print(f"main{n} ({repr(name)}):")
    eq = m.get('eq', {})
    print(f"  EQ on={eq.get('on',False)} mdl={eq.get('mdl','')}")
    dyn = m.get('dyn', {})
    print(f"  DYN on={dyn.get('on',False)} mdl={dyn.get('mdl','')}")
    fdr = m.get('fdr', -144)
    print(f"  fdr={fdr:.1f} mute={m.get('mute',False)}")

print()
print("=== CHANNEL SENDS to FX buses (9-12) ===")
for bnum in ['9', '10', '11', '12']:
    bus_name = ae['bus'][bnum].get('name', '')
    print(f"\nBus {bnum} ({bus_name}):")
    for chn in [str(i) for i in range(1, 41)]:
        ch = ae['ch'].get(chn, {})
        ch_name = ch.get('name', '')
        sends = ch.get('send', {})
        send = sends.get(bnum, {})
        if isinstance(send, dict) and send.get('on', False):
            lvl = send.get('lvl', send.get('l', -144))
            print(f"  ch{int(chn):02d} ({ch_name}): lvl={lvl:.1f}")

print()
print("=== FX SLOT ROUTING ===")
for n in [str(i) for i in range(1, 17)]:
    fx = ae['fx'].get(n, {})
    mdl = fx.get('mdl', 'NONE')
    if mdl != 'NONE':
        print(f"  fx{int(n):02d} ({mdl}): keys={[k for k in fx.keys() if k not in ['mdl','name']][:10]}")

print()
print("=== CHANNEL 37 AND 22 INVESTIGATION ===")
for n in ['22', '37']:
    ch = ae['ch'][n]
    print(f"ch{n}:")
    print(f"  name={repr(ch.get('name',''))}")
    print(f"  fdr={ch.get('fdr',-144):.1f}")
    print(f"  mute={ch.get('mute',False)}")
    conn = ch.get('in',{}).get('conn',{})
    print(f"  src={conn.get('grp','OFF')}.{conn.get('in',1)}")
    dyn = ch.get('dyn',{})
    print(f"  dyn on={dyn.get('on',False)} mdl={dyn.get('mdl','')} thr={dyn.get('thr',0):.1f}")

print()
print("=== BUS 8 (All channels) SENDS - what flows into it ===")
# Bus 8 seems to be an 'all channels' bus
ch_sends_to_8 = []
for chn in [str(i) for i in range(1, 41)]:
    ch = ae['ch'].get(chn, {})
    ch_name = ch.get('name', '')
    sends = ch.get('send', {})
    send = sends.get('8', {})
    if isinstance(send, dict) and send.get('on', False):
        lvl = send.get('lvl', send.get('l', -144))
        ch_sends_to_8.append(f"ch{int(chn):02d}({ch_name})")
print(f"  Channels: {ch_sends_to_8}")

print()
print("=== IO OUTPUTS (AES, card outputs) ===")
io_out = ae['io']['out']
for group in sorted(io_out.keys()):
    grp = io_out[group]
    for out in sorted(grp.keys(), key=lambda x: int(x) if x.isdigit() else 99):
        outp = grp[out]
        src = outp.get('src', outp.get('s', ''))
        name = outp.get('name', '')
        if src:
            print(f"  io.out.{group}.{out}: src={repr(src)} name={repr(name)}")
