# -*- coding: utf-8 -*-
"""挑几个字段很少的 proto 类，作为布局地面真值样本。"""
import collections

tinfo = {}
for line in open("bh3_structs.tsv", encoding="utf-8", errors="replace"):
    p = line.rstrip("\n").split("\t")
    if len(p) < 7 or p[0] == "typeIdx" or not p[1].startswith("/bh3/proto"):
        continue
    tinfo[int(p[0])] = (p[2], int(p[3]), int(p[5]))

fields = collections.defaultdict(list)
for line in open("bh3_fields.tsv", encoding="utf-8", errors="replace"):
    p = line.rstrip("\n").split("\t")
    if len(p) < 5 or p[0] == "typeIdx":
        continue
    ti = int(p[0])
    if ti in tinfo:
        fields[ti].append((int(p[2]), p[3], p[4]))

probe = {}
for line in open("bh3_layout_probe_all.tsv", encoding="utf-8", errors="replace"):
    p = line.rstrip("\n").split("\t")
    if len(p) < 3 or p[0] == "typeIdx":
        continue
    ti = int(p[0])
    if ti in tinfo:
        probe[ti] = p[1]

cand = []
for ti, (nm, sz, ni) in tinfo.items():
    fl = fields.get(ti, [])
    if 2 <= len(fl) <= 4 and sz <= 48 and ti in probe:
        cand.append((len(fl), sz, nm, ti, ni, probe[ti], fl))
cand.sort()
for c in cand[:8]:
    print("t%-6d %-30s size=%-3d nInst=%-2d" % (c[3], c[2], c[1], c[4]))
    print("   fields:", ", ".join("%s:%s" % (f[1], f[2]) for f in sorted(c[6])))
    print("   probe :", c[5])
