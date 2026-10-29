#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_align.py —— 诊断剩余 P! 的错位来源

思路：对每个 P! 类型的每个「落空观测偏移」，找到打包结果里**紧邻它之前**的那个字段。
落空偏移恰好落在某个字段的 [off, off+size) 之外但紧接其后，说明该字段的尺寸偏小。
把「紧前驱字段的类型名」做聚合，出现频次最高的就是尺寸算错的结构体。

同时统计：
  · 前驱字段是值类型 struct 的占比  → 指向「结构体尺寸错」
  · 前驱字段是 class/string/数组的   → 指向「漏了字段」
  · 落空偏移落在 end 之后            → 尾部漏字段
"""
import sys
import io
from collections import Counter, defaultdict

# 让 layout5 的 import 副作用（重写 tsv + 打印）静默
_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout5 as L                                   # noqa: E402
sys.stdout = _bak

types, fields = L.types, L.fields
kind_of, pack = L.kind_of, L.pack
obs_all, obs_3, clean_obs = L.obs_all, L.obs_3, L.clean_obs


def primary(ti):
    o = obs_all.get(ti) or obs_3.get(ti) or set()
    return clean_obs(ti, o)


# ---------------- 扫描 ----------------
pred_type = Counter()          # 紧前驱字段的类型
pred_name = Counter()
by_parent = Counter()
miss_delta = Counter()         # 落空偏移 - 前驱字段末尾
n_internal = n_tail = n_head = 0
n_pred_struct = n_pred_ref = 0
cases = []

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
        continue
    by_parent[types[ti]["parent"] or "<none>"] += 1
    fl_sorted = sorted(fl, key=lambda x: x[4])
    for m in miss:
        # 紧前驱：offset 最大且 <= m 的字段
        pred = None
        for f in fl_sorted:
            if f[4] <= m:
                pred = f
            else:
                break
        if pred is None:
            n_head += 1
            continue
        p_off, p_sz = pred[4], pred[5]
        if m >= end:
            n_tail += 1
            continue
        n_internal += 1
        pred_type[pred[3]] += 1
        pred_name[pred[2]] += 1
        miss_delta[m - (p_off + p_sz)] += 1
        if kind_of(L.by_name.get(pred[3], -1)) == "struct" if pred[3] in L.by_name else False:
            n_pred_struct += 1
        else:
            n_pred_ref += 1
        if len(cases) < 4000:
            cases.append((types[ti]["full"], m, pred[2], pred[3], p_off, p_sz, end))

print("=" * 78)
print("P! 落空偏移归类")
print("=" * 78)
print("  内部错位  %6d" % n_internal)
print("  尾部漏字段 %6d" % n_tail)
print("  头部（前驱不存在）%4d" % n_head)
print()
print("  紧前驱字段是值类型的: %6d (%.1f%%)" % (
    n_pred_struct, 100.0 * n_pred_struct / max(1, n_internal)))
print("  紧前驱字段是引用类型的: %6d (%.1f%%)" % (
    n_pred_ref, 100.0 * n_pred_ref / max(1, n_internal)))

print()
print("=" * 78)
print("紧前驱字段类型 TOP 30（这些类型尺寸可能偏小）")
print("=" * 78)
for nm, c in pred_type.most_common(30):
    ti = L.by_name.get(nm)
    k = kind_of(ti) if ti is not None else "?"
    sz = L.packed_size(ti) if ti is not None and k == "struct" else None
    print("  %-58s %6d  [%s%s]" % (
        nm or "<null>", c, k, " size=%d" % sz if sz is not None else ""))

print()
print("=" * 78)
print("落空偏移相对前驱字段末尾的差值分布")
print("=" * 78)
for d, c in miss_delta.most_common(12):
    print("  +%-4d %6d" % (d, c))

print()
print("=" * 78)
print("按父类 TOP 25")
print("=" * 78)
for nm, c in by_parent.most_common(25):
    print("  %-58s %6d" % (nm or "<none>", c))

print()
print("=" * 78)
print("样例 40 条  (类型 / 落空偏移 / 前驱字段 / 前驱类型 / 前驱区间 / 类型尺寸)")
print("=" * 78)
seen = defaultdict(int)
n = 0
for full, m, pn, pt, po, ps, end in cases:
    key = pt
    if seen[key] > 2:
        continue
    seen[key] += 1
    print("  %-40s miss=0x%-3x  <%s>  pred=%s@0x%x+%d  end=0x%x" % (
        full[:40], m, pt, pn, po, ps, end))
    n += 1
    if n >= 40:
        break
