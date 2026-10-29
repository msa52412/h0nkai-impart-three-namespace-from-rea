#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_inserted.py —— 在「v6 按 hard 口径变差」的类型里，v5 到底多塞了什么字段

如果 v5 靠这些字段把落空「填掉」，而这些字段本身可以独立判定为 static，
那么 v5 的零落空就是侥幸，不构成 v6 的回归。
"""
import io
import sys
import importlib.util
from collections import Counter

_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout6 as V6                                   # noqa: E402
sys.stdout = _bak

spec = importlib.util.spec_from_file_location("v5", "bh3_layout5.py")
sys.stdout = io.StringIO()
V5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V5)
sys.stdout = _bak

types = V6.types


def end_last(fl):
    return max((x[4] + x[5] for x in fl), default=0)


def hard(mod, fl, end, o):
    if not fl:
        return []
    cov = mod.covered_set(fl)
    el = end_last(fl)
    out = []
    for m in o:
        if m in cov:
            continue
        if m >= el:
            continue                      # 尾 padding / 超尾，不算
        if any(x[4] < m < x[4] + x[5] for x in fl):
            continue
        out.append(m)
    return out


name_cnt = Counter()
type_cnt = 0
covered_by_insert = 0
insert_cnt = 0

for ti in sorted(types):
    if V6.kind_of(ti) != "class":
        continue
    o = V6.clean_obs(ti, V6.obs_of(ti))
    if not o:
        continue
    fl6, e6 = V6.pack(ti)
    fl5, e5 = V5.pack(ti)
    if not fl6 or not fl5:
        continue
    h6 = hard(V6, fl6, e6, o)
    h5 = hard(V5, fl5, e5, o)
    if len(h6) <= len(h5):
        continue
    type_cnt += 1
    # v5 有、v6 无的字段
    n6 = {x[1] for x in fl6}
    ins = [x for x in fl5 if x[1] not in n6]
    insert_cnt += len(ins)
    for _o, _fi, fn, _t, off, sz in ins:
        name_cnt[fn] += 1
    # 新增落空里，有多少恰好被这些插入字段覆盖
    newoffs = set(h6) - set(h5)
    hit = 0
    for m in newoffs:
        if any(x[4] <= m < x[4] + x[5] for x in ins):
            hit += 1
    covered_by_insert += hit

print("v6 按 hard 口径变差的类型: %d 个" % type_cnt)
print("v5 在这些类型里多塞的字段: %d 个" % insert_cnt)
print("新增落空中被这些插入字段覆盖的: %d" % covered_by_insert)
print("\nv5 多塞字段的名字 TOP 30（按出现类型数）:")
for nm, c in name_cnt.most_common(30):
    print("  %-52s %d" % (nm[:51], c))
