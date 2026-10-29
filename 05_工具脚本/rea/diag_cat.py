#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_cat.py —— 把落空按几何类别（gap / tail / noise）全量配账，v5 vs v6

分类定义（与 bh3_layout6.real_miss 一致）：
  noise  落在某个字段字节之内，但不是合法内部偏移 —— 已知噪声，不计错
  gap    落在两个字段之间的空隙里（或头部对齐空洞）—— ★唯一可操作的布局错误
  tail   超出该类型计算出的末尾 —— 说明「还有数据在我们最后字段之后」

tail 的性质特殊：如果元数据的实例字段已经全部放置完毕（fieldCount 用尽），
那么超尾偏移不可能是「我们漏放了字段」，只可能是
  (a) 通过基类指针访问派生类字段，(b) memset / 字节步进噪声。
这两种都不是我们布局的错误，所以不能用来比较 v5 / v6 的优劣。
"""
import sys
import io
import importlib.util

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


def cat(mod, fl, end, o):
    cov = mod.covered_set(fl)
    c = {"noise": 0, "gap": 0, "tail": 0}
    gaps, tails = [], []
    for m in o:
        if m in cov:
            continue
        if m >= end:
            c["tail"] += 1
            tails.append(m)
            continue
        for owner, fi, fn, ft, off, sz in fl:
            if off < m < off + sz:
                c["noise"] += 1
                break
        else:
            c["gap"] += 1
            gaps.append(m)
    return c, gaps, tails


tot = {"v5": {"noise": 0, "gap": 0, "tail": 0}, "v6": {"noise": 0, "gap": 0, "tail": 0}}
n_cmp = 0
gap_better6 = gap_worse6 = gap_tie = 0
gap_types6 = gap_types5 = 0
tail_better6 = tail_worse6 = tail_tie = 0
both_zero = 0

worse_gap = []          # v6 在 gap 上变差的类型（真正需要警惕的）
for ti in sorted(types):
    if V6.kind_of(ti) != "class":
        continue
    o = V6.clean_obs(ti, V6.obs_of(ti))
    fl6, end6 = V6.pack(ti)
    fl5, end5 = V5.pack(ti)
    if not fl6 and not fl5:
        continue
    if not o:
        continue
    n_cmp += 1
    c6, g6, t6 = cat(V6, fl6, end6, o)
    c5, g5, t5 = cat(V5, fl5, end5, o)
    for k in ("noise", "gap", "tail"):
        tot["v6"][k] += c6[k]
        tot["v5"][k] += c5[k]
    if c6["gap"] < c5["gap"]:
        gap_better6 += 1
    elif c6["gap"] > c5["gap"]:
        gap_worse6 += 1
        worse_gap.append((c6["gap"] - c5["gap"], c5["gap"], c6["gap"],
                          types[ti]["full"], sorted(g6)[:6]))
    else:
        gap_tie += 1
    if c5["gap"]:
        gap_types5 += 1
    if c6["gap"]:
        gap_types6 += 1
    if c6["tail"] < c5["tail"]:
        tail_better6 += 1
    elif c6["tail"] > c5["tail"]:
        tail_worse6 += 1
    else:
        tail_tie += 1
    if not c5["gap"] and not c6["gap"]:
        both_zero += 1

print("可比 class 类型: %d（有观测且有实例字段）\n" % n_cmp)
print("%-8s %10s %10s %10s" % ("口径", "noise", "gap", "tail"))
for k in ("v5", "v6"):
    print("%-8s %10d %10d %10d" % (k, tot[k]["noise"], tot[k]["gap"], tot[k]["tail"]))

print("\n-- gap（唯一可操作类别）--")
print("  v6 更少 %d / v6 更多 %d / 持平 %d" % (gap_better6, gap_worse6, gap_tie))
print("  有 gap 落空的类型: v5=%d  v6=%d" % (gap_types5, gap_types6))
print("  两版 gap 均为 0 的类型: %d（%.1f%%）" % (both_zero, both_zero * 100.0 / n_cmp))

print("\n-- tail（不可操作，v5 靠 end 变大偶然覆盖）--")
print("  v6 更少 %d / v6 更多 %d / 持平 %d" % (tail_better6, tail_worse6, tail_tie))

worse_gap.sort(reverse=True)
print("\n-- v6 在 gap 上变差的类型（前 15）--")
for d, a, b, nm, g in worse_gap[:15]:
    print("   +%-2d %-52s v5=%d v6=%d  偏移=%s" % (
        d, nm, a, b, ",".join("0x%x" % x for x in g)))
