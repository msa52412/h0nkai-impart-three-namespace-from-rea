#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_probe_all.py —— 每类型「全部实例方法」的探针表（给本地汇编扫描器用）

比 gen_probe2 更全：不再只取 3 个方法，而是把该类型所有有地址的实例方法都列上，
让观测偏移集合尽量完整（少一个观测 → 布局歧义/失败概率大幅上升）。

输出：bh3_layout_probe_all.tsv
  typeIdx \t rva1,rva2,... \t fieldCount
"""
import csv
from collections import defaultdict

import sizes

types = {}
field_count = {}
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    if len(p) < 10:
        continue
    types[int(p[0])] = (p[1], p[2])
    try:
        field_count[int(p[0])] = int(p[9])
    except Exception:
        field_count[int(p[0])] = 0

methods = {}
with open("bh3_methods_v2.tsv", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        methods[int(r["idx"])] = r

addr = {}
with open("bh3_method_addr.tsv", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        v = r["rva"].strip()
        if v:
            addr[int(r["idx"])] = int(v, 16)

by_type = defaultdict(list)
for idx, m in methods.items():
    if idx not in addr:
        continue
    flags = int(m["flags"], 16) if m["flags"] else 0
    if flags & 0x10:
        continue
    try:
        dt = int(m["declTypeIdx"])
    except Exception:
        continue
    by_type[dt].append((m["name"], addr[idx], idx, 1 if sizes.is_sret(m["returnType"]) else 0))

CAP = 60
out = []
tot = 0
for ti in sorted(by_type):
    if field_count.get(ti, 0) <= 0:
        continue
    lst = by_type[ti]
    ctor = sorted([x for x in lst if x[0] in (".ctor", "ctor")], key=lambda x: x[2])
    other = sorted([x for x in lst if x[0] not in (".ctor", "ctor")], key=lambda x: x[2])
    picked, seen = [], set()
    for _n, rva, _i, sr in ctor + other:
        if rva in seen:
            continue
        seen.add(rva)
        picked.append((rva, sr))
        if len(picked) >= CAP:
            break
    if not picked:
        continue
    out.append((ti, ",".join("%X:%d" % (r, sr) for r, sr in picked), field_count[ti]))
    tot += len(picked)

print("类型 %d / 方法总数 %d（平均 %.1f）" % (len(out), tot, tot / max(len(out), 1)))
with open("bh3_layout_probe_all.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["typeIdx", "rvas", "fieldCount"])
    for ti, rv, fc in out:
        w.writerow([ti, rv, fc])
print("→ bh3_layout_probe_all.tsv")
