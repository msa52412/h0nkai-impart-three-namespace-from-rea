#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_probe2.py —— 生成「每类型最多 3 个实例方法」的布局探针表

输入：bh3_types_v5.txt / bh3_methods_v2.tsv / bh3_method_addr.tsv
输出：bh3_layout_probe2.tsv
  typeIdx \t rva1[,rva2,rva3] \t fieldCount

选法：
  1) 只要实例方法（flags & 0x10 == 0）；非静态方法的第 1 个参数就是 this
  2) 优先 .ctor（构造函数通常把实例字段全写一遍）
  3) 再补 1~2 个其它实例方法，用于覆盖「ctor 偷懒没写的字段」
  4) 同一类型内 RVA 去重（泛型共享别名会指向同一函数体）
"""
import csv
import re
from collections import defaultdict

types = {}
field_count = {}
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
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

print("类型 %d / 方法 %d / 有地址 %d" % (len(types), len(methods), len(addr)))

# declTypeIdx -> 实例方法列表
by_type = defaultdict(list)
for idx, m in methods.items():
    if idx not in addr:
        continue
    flags = int(m["flags"], 16) if m["flags"] else 0
    if flags & 0x10:          # static
        continue
    try:
        dt = int(m["declTypeIdx"])
    except Exception:
        continue
    nm = m["name"]
    by_type[dt].append((idx, addr[idx], nm))

print("有实例方法的类型 %d" % len(by_type))

out = []
stat = defaultdict(int)
for ti in sorted(by_type):
    if field_count.get(ti, 0) <= 0:
        stat["无字段类型"] += 1
        continue
    lst = by_type[ti]
    ctor = [x for x in lst if x[2] in (".ctor", "ctor")]
    other = [x for x in lst if x[2] not in (".ctor", "ctor")]
    # 稳定排序，保证可复现
    ctor.sort(key=lambda x: x[0])
    other.sort(key=lambda x: x[0])
    picked, seen = [], set()
    for idx, rva, nm in ctor + other:
        if rva in seen:
            continue
        seen.add(rva)
        picked.append(rva)
        if len(picked) >= 3:
            break
    if not picked:
        stat["无可用方法"] += 1
        continue
    out.append((ti, ",".join("%X" % r for r in picked), field_count[ti],
                len(picked), 1 if ctor else 0))

print("探针行 %d ；统计 %s" % (len(out), dict(stat)))
print("  1 个方法 %d / 2 个 %d / 3 个 %d"
      % (sum(1 for x in out if x[3] == 1),
         sum(1 for x in out if x[3] == 2),
         sum(1 for x in out if x[3] == 3)))

with open("bh3_layout_probe2.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["typeIdx", "rvas", "fieldCount"])
    for ti, rv, fc, n, hasctor in out:
        w.writerow([ti, rv, fc])

print("抽样：")
for x in out[:6]:
    print("   t%-6d fields=%-3d rvas=%s" % (x[0], x[2], x[1]))
