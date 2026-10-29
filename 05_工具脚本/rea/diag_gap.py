#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_gap.py —— 只剩「落在字段之间空隙」的观测，逐条列清

这是唯一还没被解释掉的落空类型，也是真正的漏字段 / 尺寸偏小候选。
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


gaps = Counter()
gap_pred_size = Counter()
gap_pred_type = Counter()
types_with_gap = 0
rows = []

for ti in sorted(types):
    if kind_of(ti) != "class":
        continue
    fl, end = pack(ti)
    if not fl:
        continue
    o = primary(ti)
    if not o:
        continue
    cov = L.covered_set(fl)
    fl_sorted = sorted(fl, key=lambda x: x[4])
    hit = []
    for m in o:
        if m in cov or m >= end:
            continue
        inside = False
        for f in fl:
            if f[4] < m < f[4] + f[5]:
                inside = True
                break
        if inside:
            continue
        pred = None
        for f in fl_sorted:
            if f[4] <= m:
                pred = f
            else:
                break
        if pred is None:
            continue
        g = m - (pred[4] + pred[5])
        hit.append((m, g, pred))
    if not hit:
        continue
    types_with_gap += 1
    for m, g, pred in hit:
        gaps[g] += 1
        gap_pred_size[(pred[5], g)] += 1
        gap_pred_type[pred[3]] += 1
        if len(rows) < 60:
            rows.append((types[ti]["full"], m, g, pred[2], pred[3], pred[4], pred[5], end))

print("=" * 84)
print("空隙类落空：类型数 %d" % types_with_gap)
print()
print("空隙大小分布")
for g, c in sorted(gaps.items()):
    print("   +%-4d %6d" % (g, c))
print()
print("(前驱字段尺寸, 空隙) 组合 TOP 20")
for (s, g), c in gap_pred_size.most_common(20):
    print("   pred_size=%-4d gap=%-4d %6d" % (s, g, c))
print()
print("前驱字段类型 TOP 15")
for nm, c in gap_pred_type.most_common(15):
    print("   %-52s %6d" % (nm or "<null>", c))
print()
print("=" * 84)
print("样例（类型 / 落空偏移 / 空隙 / 前驱字段 / 前驱类型 / 区间 / 类型末尾）")
print("=" * 84)
for r in rows:
    print("   %-42s m=0x%-4x gap=%d  pred=%s:%s@0x%x+%d  end=0x%x" % (
        r[0][:42], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
