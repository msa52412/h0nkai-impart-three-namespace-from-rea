#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_unresolved.py —— 统计「类型名无法解析、退回 8 字节」的实例字段

这类字段是布局错误的系统性来源：一个算错，其后整条布局全错。
"""
import io
import sys
from collections import Counter

_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout6 as V6                                   # noqa: E402
sys.stdout = _bak

types = V6.types
by_name = V6.by_name
PRIM = V6.PRIM

unknown = Counter()
unknown_ex = {}
n_all = 0
n_unknown = 0

for ti, fl in V6.fields.items():
    for fi, fn, ft in fl:
        if fi in V6.f_static or fi in V6.f_literal:
            continue
        n_all += 1
        nm = (ft or "").strip()
        if not nm:
            continue
        if nm in PRIM:
            continue
        if nm.endswith("*") or nm.endswith("&") or nm.startswith("!") or nm.startswith("!!"):
            continue
        if "<" in nm or "[" in nm:
            continue
        if nm in by_name:
            continue
        n_unknown += 1
        unknown[nm] += 1
        if nm not in unknown_ex:
            unknown_ex[nm] = (types[ti]["full"], fn)

print("实例字段总数: %d" % n_all)
print("类型名无法解析、退回 8 字节: %d（%.2f%%）\n" % (n_unknown, n_unknown * 100.0 / n_all))
print("TOP 40 无法解析的类型名:")
for nm, c in unknown.most_common(40):
    t, f = unknown_ex[nm]
    print("  %-56s %6d   首次出现 %s.%s" % (nm[:55], c, t[:38], f[:24]))
print("\n不同名字数量: %d" % len(unknown))
