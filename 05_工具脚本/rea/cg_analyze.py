#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cg_analyze.py — 分析全量调用图（429,850 函数 / 4,373,442 条边）

产出：
  1. 方法名覆盖率（多少函数能映射回 il2cpp 方法）
  2. 入度 Top（被调用最多的核心 hub）+ 不同调用者数
  3. 出度 Top（巨型调度/分发函数）
  4. 模块级热度（哪个模块被外部调用最多）
  5. 孤立函数（入度 0）/ 叶子函数（出度 0）统计 —— 找可疑死代码与入口

输出 bh3_cg_hubs.tsv / bh3_cg_modules.tsv
"""
import collections

BASE = 0x180000000
MADDR = r"D:\Carol-start\_rea\bh3_method_addr.tsv"
FUNCS = r"D:\Carol-start\_rea\bh3_cg_funcs.tsv"
EDGES = r"D:\Carol-start\_rea\bh3_cg_edges.tsv"
OUT_HUB = r"D:\Carol-start\_rea\bh3_cg_hubs.tsv"
OUT_MOD = r"D:\Carol-start\_rea\bh3_cg_modules.tsv"

# ---- 方法名映射 ----
va2method = {}
mod_of = {}
with open(MADDR, encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) < 7 or not p[3]:
            continue
        try:
            va = BASE + int(p[3], 16)
        except ValueError:
            continue
        va2method[va] = "%s::%s" % (p[4], p[5])
        mod_of[va] = p[2]
print("方法地址映射 %d 条" % len(va2method))

# ---- 函数表 ----
fn_body = {}
fn_name = {}
with open(FUNCS, encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) < 4:
            continue
        va = int(p[0], 16)
        fn_body[va] = int(p[1])
        fn_name[va] = p[3]
print("Ghidra 函数 %d 个" % len(fn_body))

hit = sum(1 for va in fn_body if va in va2method)
print("其中能映射到 il2cpp 方法 %d 个 = %.2f%%" % (hit, 100.0 * hit / len(fn_body)))

# ---- 边 ----
indeg = collections.Counter()
outdeg = collections.Counter()
callers = collections.defaultdict(set)
mod_edges = collections.Counter()
n = 0
with open(EDGES, encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) < 3:
            continue
        c, t = int(p[0], 16), int(p[1], 16)
        indeg[t] += 1
        outdeg[c] += 1
        callers[t].add(c)
        mod_edges[mod_of.get(t, "?")] += 1
        n += 1
print("调用边 %d 条" % n)

# ---- 入度 Top ----
print("\n=== 入度 Top 30（被调用最多的核心函数） ===")
print("  %-12s %8s %8s  %-14s %s" % ("VA", "调用次数", "不同调用者", "body", "方法"))
top_in = indeg.most_common(30)
for va, cnt in top_in:
    print("  %-12x %8d %8d  %-14d %s" % (
        va, cnt, len(callers[va]), fn_body.get(va, -1),
        va2method.get(va, fn_name.get(va, "?"))))

print("\n=== 出度 Top 20（最大的分发/调度函数） ===")
print("  %-12s %8s %-14s %s" % ("VA", "调出次数", "body", "方法"))
for va, cnt in outdeg.most_common(20):
    print("  %-12x %8d %-14d %s" % (
        va, cnt, fn_body.get(va, -1),
        va2method.get(va, fn_name.get(va, "?"))))

# ---- 孤立 / 叶子 ----
iso = [va for va in fn_body if indeg.get(va, 0) == 0]
leaf = [va for va in fn_body if outdeg.get(va, 0) == 0]
print("\n入度为 0（没人调用）: %d = %.1f%%" % (len(iso), 100.0 * len(iso) / len(fn_body)))
print("出度为 0（不调别人）: %d = %.1f%%" % (len(leaf), 100.0 * len(leaf) / len(fn_body)))
iso_named = sum(1 for va in iso if va in va2method)
print("  ↑ 其中能映射到方法名的 %d 个" % iso_named)

# ---- 模块热度 ----
print("\n=== 模块热度 Top 20（被调用边数） ===")
for m, c in mod_edges.most_common(20):
    print("  %-42s %9d" % (m, c))

with open(OUT_HUB, "w", encoding="utf-8") as f:
    f.write("va\tindeg\tdistinct_callers\toutdeg\tbody\tmethod\tmodule\n")
    for va in sorted(fn_body, key=lambda v: -indeg.get(v, 0)):
        f.write("%x\t%d\t%d\t%d\t%d\t%s\t%s\n" % (
            va, indeg.get(va, 0), len(callers[va]), outdeg.get(va, 0),
            fn_body[va], va2method.get(va, fn_name.get(va, "")),
            mod_of.get(va, "")))
print("\n写出 %s" % OUT_HUB)

with open(OUT_MOD, "w", encoding="utf-8") as f:
    f.write("module\tcallee_edges\n")
    for m, c in mod_edges.most_common():
        f.write("%s\t%d\n" % (m, c))
print("写出 %s" % OUT_MOD)
