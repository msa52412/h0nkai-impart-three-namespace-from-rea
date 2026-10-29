#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_hole.py —— 定位 408 个真错（字段间空隙）的根因

对每个 hole 偏移，找我们布局里「紧前一个字段」，统计它的类型与计算尺寸。
如果 hole == 前驱字段 off + 4 而前驱被算成 8 字节，就是「4 字节类型被当引用」。
"""
import io
import sys
from collections import Counter, defaultdict

_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout6 as V6                                   # noqa: E402
sys.stdout = _bak

types = V6.types
by_name = V6.by_name

pred_type = Counter()          # 前驱字段类型
pred_detail = defaultdict(list)
sig = Counter()                # (前驱计算尺寸, hole - 前驱off) 分布
n_hole = 0
root_cases = []

for ti in sorted(types):
    k = V6.kind_of(ti)
    if k == "enum":
        continue
    fl, end = V6.pack(ti)
    if not fl:
        continue
    o = V6.clean_obs(ti, V6.obs_of(ti))
    holes = V6.real_miss(fl, end, o)
    if not holes:
        continue
    for m in holes:
        n_hole += 1
        prev = None
        for x in fl:
            if x[4] < m:
                if prev is None or x[4] > prev[4]:
                    prev = x
            else:
                break
        if prev is None:
            pred_type["<无前驱>"] += 1
            sig[(0, m)] += 1
            continue
        _ow, fi, fn, ft, off, sz = prev
        pred_type[ft or "?"] += 1
        sig[(sz, m - off)] += 1
        if len(pred_detail[ft]) < 3:
            pred_detail[ft].append((types[ti]["full"], fn, off, sz, m))
        if sz == 8 and m - off == 4 and len(root_cases) < 20:
            root_cases.append((types[ti]["full"], fn, ft, off, m))

print("真错（hole）总数: %d\n" % n_hole)
print("紧前驱字段的类型 TOP 25:")
for nm, c in pred_type.most_common(25):
    print("  %3d  %s" % (c, nm[:78]))

print("\n(前驱尺寸, hole - 前驱off) 分布 TOP 12:")
for (sz, d), c in sig.most_common(12):
    print("  size=%-3d delta=%-4d  %d" % (sz, d, c))

print("\n『前驱算成 8 字节、hole 恰在 +4』的样例（典型=4字节类型被当引用）:")
for nm, fn, ft, off, m in root_cases:
    print("  %-52s %-32s %-44s 0x%-3x→hole 0x%x" % (
        nm[:51], fn[:31], (ft or "")[:43], off, m))

print("\n可疑类型判定明细（前驱类型不是 enum/struct 但 hole 在 +4）:")
shown = 0
for ft, lst in pred_detail.items():
    if shown >= 15:
        break
    for nm, fn, off, sz, m in lst:
        if sz == 8 and m - off == 4:
            ti = by_name.get(ft.strip()) if ft else None
            kd = V6.kind_of(ti) if ti is not None else "未在类型表"
            print("  %-30s kind=%-8s 用于 %-40s 字段 %s" % (
                (ft or "?")[:29], kd, nm[:39], fn))
            shown += 1
            break


# ---- 具体案例：size=4 delta=4 的上下文 ----
print("\n" + "=" * 88)
print("size=4 delta=4 案例上下文（空隙紧跟在 4 字节字段之后）")
print("=" * 88)
cases = []
for ti in sorted(types):
    if V6.kind_of(ti) == "enum":
        continue
    fl, end = V6.pack(ti)
    if not fl:
        continue
    o = V6.clean_obs(ti, V6.obs_of(ti))
    holes = V6.real_miss(fl, end, o)
    for m in holes:
        prev = None
        for x in fl:
            if x[4] < m and (prev is None or x[4] > prev[4]):
                prev = x
        if not prev:
            continue
        if prev[5] == 4 and m - prev[4] == 4:
            cases.append((ti, fl, m, prev))
            break
    if len(cases) >= 6:
        break

for ti, fl, m, prev in cases:
    print("\n%s  ti=%d" % (types[ti]["full"], ti))
    print("  观测: %s" % " ".join("0x%x" % x for x in sorted(
        V6.clean_obs(ti, V6.obs_of(ti)))))
    lo = max(0.0, prev[4] - 0x10)
    for _ow, fi, fn, ft, off, sz in fl:
        if off < lo or off > m + 0x20:
            continue
        mark = " ★前驱" if (off, fn) == (prev[4], prev[2]) else ""
        hmark = " ← 空隙" if off == m else ""
        print("   0x%-4x %-34s %-42s size=%d%s%s" % (
            off, fn[:33], (ft or "")[:41], sz, mark, hmark))
    print("   0x%-4x %s" % (m, "← 观测有、无字段（空隙）"))
