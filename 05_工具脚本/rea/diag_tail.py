#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_tail.py —— 尾部漏字段的形状分析

对一个「观测超出类型末尾」的落空，问三个问题：
  1) 超出多少字节？(miss - end)
  2) 是不是一段连续 4 字节步长的游走？（数组步进噪声的特征）
  3) 该类型的元数据 fieldCount 与我们的打包字段数是否一致？
     —— 若一致，说明字段齐全，超尾观测必然是坏基址噪声，不是漏字段
"""
import sys
import io
from collections import Counter

_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout5 as L                                   # noqa: E402
sys.stdout = _bak

types = L.types
kind_of, pack = L.kind_of, L.pack
obs_all, obs_3, clean_obs = L.obs_all, L.obs_3, L.clean_obs
packed_size = L.packed_size


def primary(ti):
    return clean_obs(ti, (obs_all.get(ti) or obs_3.get(ti) or set()))


# 元数据 fieldCount
declared = {}
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    if len(p) >= 10:
        try:
            declared[int(p[0])] = int(p[9])
        except ValueError:
            pass

delta = Counter()
run_len = Counter()
cnt_match = 0
cnt_mismatch = 0
tail_types = 0
run_samples = []

for ti in sorted(types):
    if kind_of(ti) != "class":
        continue
    fl, end = pack(ti)
    if not fl:
        continue
    o = primary(ti)
    if not o:
        continue
    cov = L.covered_set(fl)
    tail = sorted(x for x in o if x >= end and x not in cov)
    if not tail:
        continue
    tail_types += 1
    for x in tail:
        delta[x - end] += 1
    # 连续段长度（步长 4）
    seg = 1
    best = 1
    for a, b in zip(tail, tail[1:]):
        if b - a == 4:
            seg += 1
            best = max(best, seg)
        else:
            seg = 1
    run_len[best] += 1
    n_own = len([1 for _ in fl if _[0] == ti])
    d = declared.get(ti)
    if d is not None and d == n_own:
        cnt_match += 1
        if len(run_samples) < 6 and best >= 4:
            run_samples.append((types[ti]["full"], end, tail[:16], best))

print("=" * 78)
print("有尾部漏字段的类型: %d" % tail_types)
print("  元数据 fieldCount == 本类型字段数 : %d" % cnt_match)
print("  不一致                            : %d" % cnt_mismatch)
print()
print("超出末尾的字节数分布 TOP 20")
for k, c in delta.most_common(20):
    print("   +%-5d %6d" % (k, c))
print()
print("最长连续 4 字节段长度分布")
for k in sorted(run_len):
    print("   %d 个连续: %d" % (k, run_len[k]))
print()
print("字段齐全但仍有长连续超尾游走的样例：")
for nm, end, tail, best in run_samples:
    print("   %-46s end=0x%-4x run=%d  obs=%s" % (
        nm[:46], end, best, " ".join("%x" % x for x in tail)))
