#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_fc.py —— 核实 bh3_types_v5.txt 第 10 列（下标 9）确实是 fieldCount

若「声明 fieldCount == 字段表行数」在全体类型上成立，
则字段表是完整的，超尾观测不可能来自我们漏放的字段。
"""
import io
import sys
from collections import Counter

_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout6 as V6                                   # noqa: E402
sys.stdout = _bak

types = V6.types

# 直接从原始表取第 10 列（下标 9 = fieldCount）
fc_of = {}
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    if len(p) < 10:
        continue
    try:
        fc_of[int(p[0])] = int(p[9])
    except ValueError:
        pass

cols = Counter()
sample = []

n_match = n_less = n_more = 0
for ti, t in types.items():
    n = len(V6.fields.get(ti, []))
    fc = fc_of.get(ti, -1)
    if fc < 0:
        continue
    if fc == n:
        n_match += 1
    elif fc > n:
        n_less += 1
        if len(sample) < 12:
            sample.append((t["full"], n, fc))
    else:
        n_more += 1

print("fieldCount == 字段表行数 : %d" % n_match)
print("fieldCount >  字段表行数 : %d" % n_less)
print("fieldCount <  字段表行数 : %d" % n_more)
print("合计 %d" % (n_match + n_less + n_more))
if sample:
    print("\n不匹配样例（类型 / 行数 / 声明）:")
    for nm, n, fc in sample:
        print("   %-56s %d / %d" % (nm[:55], n, fc))
