#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_nullable.py —— Nullable<T> 尺寸修正的验证与全量影响预估"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, ".")
import bh3_layout6 as L  # noqa: E402

ti = L.by_name.get("System.Nullable`1")
print("System.Nullable`1 (typeIdx %s) kind=%s" % (ti, L.kind_of(ti) if ti else None))
for fi, fn, ft in L.inst_fields(ti):
    print("   %-20s %s" % (fn, ft))

# 影响面：多少字段是 Nullable<...>
n_nullable = 0
for t in L.fields.values():
    for fi, fn, ft in t:
        if ft and ft.startswith("System.Nullable`1<"):
            n_nullable += 1
print("Nullable<...> 字段总数:", n_nullable)
