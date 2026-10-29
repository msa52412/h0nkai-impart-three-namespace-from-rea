#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compare56.py —— 逐类型对比 v5（命名启发式）与 v6（attrs 真值）的观测落空数

v5 用「不变体」（不做 class 常量剔除），因为那才是 v5 的实际默认行为。
只比较两个版本都有实例字段、且都有观测的类型。
"""
import sys
import io

_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout5 as V5
sys.stdout = io.StringIO()
import bh3_layout6 as V6
sys.stdout = _bak

both = better6 = better5 = tie = 0
miss6_tot = miss5_tot = 0
worse6 = []
worse5 = []

for ti in sorted(V6.types):
    k6 = V6.kind_of(ti)
    if k6 == "enum":
        continue
    k5 = V5.kind_of(ti)
    if k5 == "enum":
        continue
    o = V6.clean_obs(ti, V6.obs_of(ti))
    if not o:
        continue
    f6, e6 = V6.pack(ti)
    if not f6:
        continue
    f5, e5 = V5.pack(ti, 0, 0)          # 变体 0 = v5 原始行为
    if not f5:
        continue
    both += 1
    m6 = len(V6.real_miss(f6, e6, o))
    m5 = len(V5.real_miss(f5, e5, o))
    miss6_tot += m6
    miss5_tot += m5
    if m6 < m5:
        better6 += 1
        if len(worse5) < 10:
            worse5.append((V6.types[ti]["full"], m5, m6))
    elif m6 > m5:
        better5 += 1
        if len(worse6) < 12:
            worse6.append((V6.types[ti]["full"], m5, m6))
    else:
        tie += 1

print("=" * 80)
print("共同可比类型: %d" % both)
print("  v6 更好  %6d" % better6)
print("  v5 更好  %6d" % better5)
print("  持平      %6d" % tie)
print("  落空总数  v5=%d   v6=%d   (%+.1f%%)" % (
    miss5_tot, miss6_tot,
    100.0 * (miss6_tot - miss5_tot) / max(1, miss5_tot)))
print()
print("v6 反而变差的样例（类型 / v5 落空 / v6 落空）:")
for r in worse6:
    print("   %-56s %3d -> %3d" % r)
print()
print("v5 落空的样例（v6 修好的）:")
for r in worse5:
    print("   %-56s %3d -> %3d" % r)
