#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_metric2.py —— 用「物理上正确的」落空口径重算 v5 / v6

旧口径（real_miss）把两类**不可能是布局错误**的偏移也算成错：
  ① 超出类型末尾（tail）   —— 元数据实例字段已排满，没有字段可挪；
                             只可能是通过基类指针访问派生类，或字节/stride 噪声
  ② 末尾对齐 padding        —— 最后一个字段结束到 end 之间的填充字节，
                             若有真字段，元数据 fieldCount 会多出来

新口径 effective_end = 最后一个字段的 off + size（不含尾部对齐），
只有 m < effective_end 且不被任何字段覆盖、也不是合法内部偏移，才算错。

另外单独统计「连续字节步进」（≥3 个连续偏移，stride=1）—— 这是
DumpCtorAccess 中 `param_1[i]` 循环的特征，必然不是字段起点。
"""
import io
import sys
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


def end_last(fl):
    return max((x[4] + x[5] for x in fl), default=0)


def runs(mset):
    out = set()
    for m in mset:
        lo = hi = 0
        while (m - lo - 1) in mset:
            lo += 1
        while (m + hi + 1) in mset:
            hi += 1
        if lo + hi + 1 >= 3:
            out.add(m)
    return out


def score(mod, fl, end, o):
    """返回 (hard, tailpad, beyond, run, hard_list)"""
    if not fl:
        return 0, 0, 0, 0, []
    cov = mod.covered_set(fl)
    el = end_last(fl)
    rest = [m for m in o if m not in cov]
    hard = []
    tailpad = beyond = 0
    for m in rest:
        if m >= end:
            beyond += 1
        elif m >= el:
            tailpad += 1
        else:
            inside = any(x[4] < m < x[4] + x[5] for x in fl)
            if not inside:
                hard.append(m)
    r = runs(set(rest))
    return len(hard), tailpad, beyond, len(r & set(hard)), hard


agg = {k: {"hard": 0, "tailpad": 0, "beyond": 0, "run": 0} for k in ("v5", "v6")}
win = lose = tie = 0
worse = []
ok_types = 0
n = 0

for ti in sorted(types):
    if V6.kind_of(ti) != "class":
        continue
    o = V6.clean_obs(ti, V6.obs_of(ti))
    if not o:
        continue
    fl6, e6 = V6.pack(ti)
    fl5, e5 = V5.pack(ti)
    if not fl6 and not fl5:
        continue
    n += 1
    h6, tp6, b6, r6, l6 = score(V6, fl6, e6, o)
    h5, tp5, b5, r5, l5 = score(V5, fl5, e5, o)
    for mod, vals in (("v5", (h5, tp5, b5, r5)), ("v6", (h6, tp6, b6, r6))):
        for k, v in zip(("hard", "tailpad", "beyond", "run"), vals):
            agg[mod][k] += v
    if h6 < h5:
        win += 1
    elif h6 > h5:
        lose += 1
        worse.append((h6 - h5, h5, h6, types[ti]["full"], sorted(l6)[:8], e5, e6))
    else:
        tie += 1
    if not h6:
        ok_types += 1

print("可比 class 类型: %d\n" % n)
print("%-6s %8s %10s %10s %10s" % ("版本", "hard", "尾padding", "超尾", "其中字节步进"))
for k in ("v5", "v6"):
    a = agg[k]
    print("%-6s %8d %10d %10d %10d" % (k, a["hard"], a["tailpad"], a["beyond"], a["run"]))

print("\nhard 口径逐类型裁决:")
print("  v6 更好 %d / v6 更差 %d / 持平 %d" % (win, lose, tie))
print("  v6 hard=0 的类型 %d / %d（%.2f%%）" % (ok_types, n, ok_types * 100.0 / n))

worse.sort(reverse=True)
print("\nv6 在 hard 口径下变差的类型（前 12）:")
for d, a, b, nm, lst, e5, e6 in worse[:12]:
    print("   +%-2d %-50s v5=%d v6=%d  end5=0x%-4x end6=0x%-4x %s" % (
        d, nm[:49], a, b, e5, e6,
        ",".join("0x%x" % x for x in lst)))
