#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_generic.py —— 统计字段里出现的泛型类型，区分「泛型类（引用）」与「泛型结构体（值）」
"""
import io
import sys
import re
from collections import Counter

_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout6 as V6                                   # noqa: E402
sys.stdout = _bak

types = V6.types
by_name = V6.by_name

GEN = re.compile(r"^([^<]+)<(.*)>$")

def defn(nm):
    m = GEN.match((nm or "").strip())
    return m.group(1) if m else None

# 泛型定义本身的 kind 分布
defs = Counter()
unknown = Counter()
kinds = Counter()
for ti in types:
    if "<" in types[ti]["full"]:
        continue

# 直接看类型表里带反引号的定义名
name_kind = {}
for ti, t in types.items():
    nm = t["full"]
    if "`" in nm and "<" not in nm:
        name_kind[nm] = V6.kind_of(ti)

print("类型表中泛型定义(带`)数量: %d" % len(name_kind))
print("其中 struct: %d / class: %d / enum: %d" % (
    sum(1 for v in name_kind.values() if v == "struct"),
    sum(1 for v in name_kind.values() if v == "class"),
    sum(1 for v in name_kind.values() if v == "enum")))
print("\n泛型结构体定义（前 30，按字母）:")
for nm in sorted(n for n, v in name_kind.items() if v == "struct")[:30]:
    print("   %s" % nm)

# 字段层面统计
use = Counter()
resolved_struct = Counter()
n_field = 0
for ti, fl in V6.fields.items():
    for fi, fn, ft in fl:
        if fi in V6.f_static or fi in V6.f_literal:
            continue
        n_field += 1
        d = defn(ft)
        if not d:
            continue
        use[d] += 1
        k = name_kind.get(d)
        if k == "struct":
            resolved_struct[ft] += 1

print("\n实例字段总数: %d" % n_field)
print("其中泛型类型字段: %d" % sum(use.values()))
print("泛型定义可在类型表中查到、且是 struct 的字段: %d" % sum(resolved_struct.values()))
print("\nTOP 泛型定义（按实例字段数）:")
for nm, c in use.most_common(20):
    print("   %-52s %6d  kind=%s" % (nm[:51], c, name_kind.get(nm, "未知")))
print("\n被误当引用的泛型结构体实例（TOP 20）:")
for nm, c in resolved_struct.most_common(20):
    print("   %-62s %5d" % (nm[:61], c))
