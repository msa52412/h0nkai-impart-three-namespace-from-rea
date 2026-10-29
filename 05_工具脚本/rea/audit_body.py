#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit_body.py — 比对 Ghidra 函数体长度 与 `.pdata` 的 (End - Begin)

`.pdata` 里的 EndAddress 是编译器给出的权威函数边界，
Ghidra 自己推断的 body 可能与之一致、偏小（截断）或偏大（把未定义区并进来）。

输出：
  - 一致率
  - 按差异分桶
  - 差异最大的前 20 个（这些就是需要 clearListing 重划边界的）
"""
import collections

TRUTH = r"D:\Carol-start\_rea\bh3_pdata_truth.tsv"
GHIDRA = r"D:\Carol-start\_rea\bh3_ghidra_funcs.txt"
OUT = r"D:\Carol-start\_rea\bh3_body_mismatch.tsv"

truth = {}
for ln in open(TRUTH, encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 2:
        continue
    b, e = int(p[0], 16), int(p[1], 16)
    truth[b] = e

gh = {}
for ln in open(GHIDRA, encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4:
        continue
    gh[int(p[0], 16)] = int(p[1])

both = sorted(set(truth) & set(gh))
print("参与比对 %d 个函数" % len(both))

eq = 0
buck = collections.Counter()
mismatch = []
for a in both:
    pdata_len = truth[a] - a
    g_len = gh[a]
    if g_len == pdata_len:
        eq += 1
        buck["完全一致"] += 1
        continue
    d = g_len - pdata_len
    mismatch.append((a, pdata_len, g_len, d))
    if d < 0:
        buck["Ghidra 偏小"] += 1
    else:
        if d <= 16:
            buck["偏大 <=16"] += 1
        elif d <= 256:
            buck["偏大 17-256"] += 1
        elif d <= 4096:
            buck["偏大 257-4K"] += 1
        else:
            buck["偏大 >4K"] += 1

print()
print("完全一致 %d / %d = %.2f%%" % (eq, len(both), 100.0 * eq / len(both)))
for k in ["完全一致", "Ghidra 偏小", "偏大 <=16", "偏大 17-256", "偏大 257-4K", "偏大 >4K"]:
    if buck[k]:
        print("  %-14s %d" % (k, buck[k]))

mismatch.sort(key=lambda r: -abs(r[3]))
print("\n=== 差异最大的 20 个（需重划边界） ===")
print("  %-12s %10s %10s %10s" % ("VA", ".pdata长度", "Ghidra body", "差"))
for a, pl, gl, dd in mismatch[:20]:
    print("  %-12x %10d %10d %+10d" % (a, pl, gl, dd))

big = [r for r in mismatch if r[2] > 16384]
print("\nGhidra body >16K 的共 %d 个：" % len(big))
for a, pl, gl, dd in sorted(big, key=lambda r: -r[2])[:12]:
    print("  %x  body=%d  .pdata 长度=%d  差 %+d" % (a, gl, pl, dd))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("va\tpdata_len\tghidra_body\tdiff\n")
    for a, pl, gl, dd in mismatch:
        f.write("%x\t%d\t%d\t%d\n" % (a, pl, gl, dd))
print("\n写出 %s（%d 行不一致）" % (OUT, len(mismatch)))
