#!/usr/bin/env python3
import json
base = json.load(open('data/reference/Base.snap'))
io_out = base['ae_data']['io']['out']
found = False
for group in sorted(io_out.keys()):
    grp = io_out[group]
    for out in sorted(grp.keys(), key=lambda x: int(x) if x.isdigit() else 99):
        outp = grp.get(out, {})
        src = outp.get('src', outp.get('s', ''))
        name = outp.get('name', '')
        g = outp.get('g', 0)
        if src or name or g != 0:
            print(f"io.out.{group}.{out}: src={repr(src)} name={repr(name)} g={g}")
            found = True
if not found:
    print("All IO outputs are default (no routing configured)")
