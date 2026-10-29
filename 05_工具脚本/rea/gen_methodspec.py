#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_methodspec.py —— 导出表4（泛型方法实例化规格）213,854 条到 TSV。"""
import csv
import struct
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")
from rd import d, va2off  # noqa: E402

T4 = 0x187127630
N = 213854
STRIDE = 12

types = {}
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    types[int(p[0])] = (p[1], p[2])

methods = {}
with open("bh3_methods_v2.tsv", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        methods[int(r["idx"])] = r

o = va2off(T4)
out = open("bh3_methodspecs.tsv", "w", encoding="utf-8", newline="")
w = csv.writer(out, delimiter="\t")
w.writerow(["idx", "methodGenericArgIdx", "typeGenericArgIdx", "methodDefIdx",
            "declType", "method", "genericContainer"])
for i in range(N):
    mg, tg, md = struct.unpack_from("<iii", d, o + i * STRIDE)
    r = methods.get(md)
    if r:
        ns, nm = types.get(int(r["declTypeIdx"]), ("", r["declType"]))
        dt = (ns + "::" + nm) if ns else nm
        w.writerow([i, mg, tg, md, dt, r["name"], r["genericContainer"]])
    else:
        w.writerow([i, mg, tg, md, "?", "?", ""])
out.close()
print("写出 bh3_methodspecs.tsv：%d 行" % N)

# 边界检查
print("\n数组边界检查（末端 ±3 条）")
for i in range(N - 3, N + 3):
    t = struct.unpack_from("<iii", d, o + i * STRIDE)
    print("  [%6d] %8d %8d %8d" % (i, t[0], t[1], t[2]))
