#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_miss.py —— 把 P! 的落空偏移按几何位置细分

三类：
  A 落空偏移严格落在某个已打包字段的 [off, off+size) 之内  → 子字段访问（Ghidra 折叠）
  B 落空偏移落在两个字段之间的空隙                        → 真漏字段 / 结构体偏小
  C 落空偏移 >= 类型总尺寸                                → 尾部漏字段

同时统计：
  · A 类里 (miss - fieldOff) 的差值分布（子字段步长应是小整数）
  · B 类里空隙大小的分布（应是对齐单位 4/8 的倍数）
  · 若只剔除 A 类噪声，有多少 P! 能升为 P
"""
import sys
import io
from collections import Counter

_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout5 as L                                   # noqa: E402
sys.stdout = _bak

types = L.types
kind_of, pack = L.kind_of, L.pack
obs_all, obs_3, clean_obs = L.obs_all, L.obs_3, L.clean_obs


def primary(ti):
    return clean_obs(ti, (obs_all.get(ti) or obs_3.get(ti) or set()))


nA = nB = nC = 0
sub_step = Counter()
gap_size = Counter()
gap_pred = Counter()
tail_pred = Counter()
A_pred = Counter()
type_all_A = 0
type_has_B = 0
P_after_A = 0
P_before = 0
iA = iB = iC = 0

for ti in sorted(types):
    if kind_of(ti) != "class":
        continue
    fl, end = pack(ti)
    if not fl:
        continue
    o = primary(ti)
    if not o:
        continue
    offs = {x[4] for x in fl}
    miss = o - offs
    if not miss:
        P_before += 1
        continue
    fl_sorted = sorted(fl, key=lambda x: x[4])
    a = b = c = 0
    for m in miss:
        # 找出 m 落在哪个区间
        hit = None
        pred = None
        for f in fl_sorted:
            if f[4] <= m:
                pred = f
            if f[4] <= m < f[4] + f[5]:
                hit = f
                break
        if hit is not None:
            a += 1
            nA += 1
            sub_step[m - hit[4]] += 1
            A_pred[hit[3]] += 1
        elif m >= end:
            c += 1
            nC += 1
            if pred:
                tail_pred[pred[3]] += 1
        else:
            b += 1
            nB += 1
            if pred:
                g = m - (pred[4] + pred[5])
                gap_size[g] += 1
                gap_pred[(pred[3], g)] += 1
    if a and not b and not c:
        type_all_A += 1
        P_after_A += 1
    if b:
        type_has_B += 1

print("=" * 78)
print("落空偏移几何分类（class）")
print("=" * 78)
print("  A 落在字段内部（子字段访问噪声）  %6d  (%.1f%%)" % (nA, 100.0 * nA / max(1, nA + nB + nC)))
print("  B 落在字段之间空隙                %6d  (%.1f%%)" % (nB, 100.0 * nB / max(1, nA + nB + nC)))
print("  C 超出类型总尺寸                  %6d  (%.1f%%)" % (nC, 100.0 * nC / max(1, nA + nB + nC)))
print()
print("  只含 A 类落空的 P! 类型: %d  → 剔除后 P 从 %d 升到 %d" % (
    type_all_A, P_before, P_before + P_after_A))
print("  含 B 类落空的 P! 类型:   %d" % type_has_B)

print()
print("=" * 78)
print("A 类：落空偏移相对所属字段起点的差值 TOP 20")
print("=" * 78)
for d, c in sub_step.most_common(20):
    print("  +%-4d %6d" % (d, c))

print()
print("=" * 78)
print("A 类：被「穿越」的字段类型 TOP 15")
print("=" * 78)
for nm, c in A_pred.most_common(15):
    ti = L.by_name.get(nm)
    k = kind_of(ti) if ti is not None else "?"
    sz = L.packed_size(ti) if ti is not None and k == "struct" else None
    print("  %-52s %6d [%s%s]" % (nm or "<null>", c, k,
                                  " size=%d" % sz if sz is not None else ""))

print()
print("=" * 78)
print("B 类：空隙大小分布 TOP 15")
print("=" * 78)
for g, c in gap_size.most_common(15):
    print("  %-5d %6d" % (g, c))

print()
print("=" * 78)
print("B 类：前驱字段类型 + 空隙 组合 TOP 20")
print("=" * 78)
for (nm, g), c in gap_pred.most_common(20):
    print("  %-46s gap=%-4d %6d" % (nm or "<null>", g, c))

print()
print("=" * 78)
print("C 类：最后一个字段类型 TOP 15（尾部漏字段）")
print("=" * 78)
for nm, c in tail_pred.most_common(15):
    print("  %-52s %6d" % (nm or "<null>", c))
