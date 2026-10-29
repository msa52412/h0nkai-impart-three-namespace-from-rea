#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_decomp.py —— 把 v6 相对 v5 新增的每一个落空，精确归因到「为什么 v5 没落空」

对每个落空偏移 m，判定 v5 侧的豁免来源：
   S  v5 在 m 处有一个**字段起点**            → v5 真的认为那里有字段
   E  v5 的 end > m，m 落在 v5 末尾之内但非起点（空隙内）
   N  m 落在 v5 的某个字段字节之内
   X  v5 也落空（真·共同落空，与本次改动无关）

同时对 m 打「噪声嫌疑」标签：
   run   与同类型内其他连续偏移构成 ≥3 连续字节步进（param_1[i] 循环）
   unal  不是 4 的倍数，且类型不是 struct（引用/整型字段都至少 4 对齐）
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


def run_flag(miss_set):
    """返回 miss 中被判为「连续字节步进」的偏移集合"""
    out = set()
    for m in miss_set:
        lo = hi = 0
        while (m - lo - 1) in miss_set:
            lo += 1
        while (m + hi + 1) in miss_set:
            hi += 1
        if lo + hi + 1 >= 3:
            out.add(m)
    return out


stat = {"S": 0, "E": 0, "N": 0, "X": 0}
stat_runs = {"S": [0, 0], "E": [0, 0], "N": [0, 0], "X": [0, 0]}   # [run, unal]
new_miss_total = 0
v6_tail_under_end5 = 0
v6_tail_total = 0
gap_under_end5 = 0
gap_total = 0

by_cause_samples = {"S": [], "E": [], "N": []}

for ti in sorted(types):
    if V6.kind_of(ti) != "class":
        continue
    o = V6.clean_obs(ti, V6.obs_of(ti))
    if not o:
        continue
    fl6, end6 = V6.pack(ti)
    fl5, end5 = V5.pack(ti)
    if not fl6:
        continue
    offs5 = {x[4] for x in fl5}
    miss6 = set(V6.real_miss(fl6, end6, o))
    miss5 = set(V5.real_miss(fl5, end5, o))
    new = miss6 - miss5
    if not new:
        continue
    new_miss_total += len(new)
    for m in new:
        if m in offs5:
            c = "S"
        elif m >= end5:
            c = "X"
        else:
            inside5 = any(x[4] < m < x[4] + x[5] for x in fl5)
            c = "N" if inside5 else "E"
        stat[c] += 1
        if c == "X":
            v6_tail_total += 1 if m >= end6 else 0
        if m >= end6:
            v6_tail_total += 0
        if c in ("S", "E"):
            if m < end5:
                if m >= end6:
                    v6_tail_under_end5 += 1
                else:
                    gap_under_end5 += 1
        if len(by_cause_samples[c]) < 6:
            by_cause_samples[c].append((types[ti]["full"], m, end5, end6))
    r = run_flag(new)
    for m in new:
        c = ("S" if m in offs5 else "X" if m >= end5 else
             "N" if any(x[4] < m < x[4] + x[5] for x in fl5) else "E")
        stat_runs[c][0] += 1 if m in r else 0
        stat_runs[c][1] += 1 if (m % 4 and V6.kind_of(ti) == "class") else 0

print("v6 相对 v5 新增落空总数: %d\n" % new_miss_total)
print("归因:")
print("  S  v5 在该偏移有字段起点（v6 把那个字段判成 static，占位消失）  %6d" % stat["S"])
print("  E  v5 的 end 更大，该偏移落在 v5 末尾内的空隙/超尾                 %6d" % stat["E"])
print("  N  落在 v5 某个字段字节内部                                       %6d" % stat["N"])
print("  X  v5 也落空（共同落空，与本次改动无关）                          %6d" % stat["X"])
print("  合计                                                              %6d" %
      sum(stat.values()))

print("\n噪声嫌疑（对新增落空）:")
for k in ("S", "E", "N", "X"):
    tot = stat[k]
    if not tot:
        continue
    print("  %s  连续字节步进 %5d (%.0f%%)   非4对齐 %5d (%.0f%%)" % (
        k, stat_runs[k][0], stat_runs[k][0] * 100.0 / tot,
        stat_runs[k][1], stat_runs[k][1] * 100.0 / tot))

print("\n按类别抽样:")
for k in ("S", "E", "N"):
    if not by_cause_samples[k]:
        continue
    print("  [%s]" % k)
    for nm, m, e5, e6 in by_cause_samples[k]:
        print("     %-52s 0x%-4x  v5.end=0x%-4x v6.end=0x%-4x" % (nm, m, e5, e6))
