#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_probe3.py —— 生成「属性 getter/setter」探针表，用于把 名字 → 偏移 绑定起来

动机：主探针只给出「偏移集合」，当同尺寸字段相邻时无法判定谁是谁（conf=M）。
属性访问器 get_X / set_X 直接给出 X 的偏移，可消歧。

输出：
  bh3_prop_probe.tsv   syntheticIdx \t rva      （给 Ghidra 脚本用，格式与主探针一致）
  bh3_prop_map.tsv     syntheticIdx \t realTypeIdx \t propName \t kind

syntheticIdx 从 9000000 起，避开真实类型索引（0..57486）。
"""
import csv
import re
from collections import defaultdict

import sizes

types = {}
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    types[int(p[0])] = (p[1], p[2])

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

print("类型 %d / 方法 %d / 有地址 %d" % (len(types), len(methods), len(addr)))

# 每类型里形如 get_X / set_X 的方法
prop = defaultdict(dict)     # typeIdx -> {(kind, prop): [rva,...]}
PAT = re.compile(r"^(get|set|get_|set_)(.+)$")
for idx, m in methods.items():
    if idx not in addr:
        continue
    nm = m["name"]
    if not (nm.startswith("get_") or nm.startswith("set_")):
        continue
    kind = "get" if nm.startswith("get_") else "set"
    pn = nm[4:]
    if not pn:
        continue
    try:
        dt = int(m["declTypeIdx"])
    except Exception:
        continue
    prop[dt].setdefault((kind, pn), []).append((addr[idx], 1 if sizes.is_sret(m["returnType"]) else 0))

print("有属性的类型 %d / 属性条目 %d"
      % (len(prop), sum(len(v) for v in prop.values())))

rows = []
smap = []
sid = 9000000
for ti in sorted(prop):
    for (kind, pn), rvas in sorted(prop[ti].items()):
        rvas = sorted(set(rvas))[:2]
        if not rvas:
            continue
        rows.append((sid, ",".join("%X:%d" % (r, sr) for r, sr in rvas)))
        smap.append((sid, ti, pn, kind))
        sid += 1

print("探针行 %d（上限 synthetic=%d）" % (len(rows), sid))

with open("bh3_prop_probe.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["typeIdx", "rvas", "fieldCount"])
    for s, rv in rows:
        w.writerow([s, rv, 0])

with open("bh3_prop_map.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["syntheticIdx", "typeIdx", "propName", "kind"])
    for r in smap:
        w.writerow(list(r))

print("抽样：")
for i in range(min(5, len(rows))):
    s, rv = rows[i]
    st, ti, pn, kd = smap[i]
    print("   s=%-9d t%-6d %s_%s  rva=%s" % (s, ti, kd, pn, rv))
