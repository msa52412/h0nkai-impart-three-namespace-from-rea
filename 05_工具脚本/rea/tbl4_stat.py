#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tbl4_stat.py —— 表4 明文描述符表（.rdata 0x187127630，12 字节/条）全量统计。"""
import struct
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")
from rd import d, va2off  # noqa: E402

BASE = 0x187127630
N = 213854
STRIDE = 12

o = va2off(BASE)
print("基址 0x%X  RVA 0x%X  文件偏移 0x%X" % (BASE, BASE - 0x180000000, o))
print("假设条数 %d × %d = %d 字节，结束 RVA 0x%X"
      % (N, STRIDE, N * STRIDE, BASE - 0x180000000 + N * STRIDE))

cnt_neg = [0, 0, 0]
mx = [-1, -1, -1]
mn = [1 << 30, 1 << 30, 1 << 30]
dist_c = {}
zero_all = 0
rows = []
for i in range(N):
    a, b, c = struct.unpack_from("<iii", d, o + i * STRIDE)
    t = (a, b, c)
    for k in range(3):
        if t[k] == -1:
            cnt_neg[k] += 1
        else:
            if t[k] > mx[k]:
                mx[k] = t[k]
            if t[k] < mn[k]:
                mn[k] = t[k]
    if t == (-1, -1, -1):
        zero_all += 1
    if i < 40 or i > N - 6:
        rows.append((i, t))

print("\n各字段统计（-1 = 空）")
for k, nm in enumerate(("f0", "f1", "f2")):
    print("  %s: -1 计 %d (%.2f%%)  min=%d  max=%d"
          % (nm, cnt_neg[k], 100.0 * cnt_neg[k] / N, mn[k], mx[k]))
print("  全 -1 行: %d" % zero_all)

print("\n前 40 条 / 后 5 条")
for i, t in rows:
    print("  [%6d] %8d %8d %8d" % (i, t[0], t[1], t[2]))

# f2 是否单调 / 分布
vals = []
for i in range(N):
    c = struct.unpack_from("<i", d, o + i * STRIDE + 8)[0]
    vals.append(c)
inc = sum(1 for i in range(1, N) if vals[i] >= vals[i - 1])
print("\nf2 相邻不减比例: %d/%d = %.1f%%" % (inc, N - 1, 100.0 * inc / (N - 1)))
print("f2 去重后条数: %d" % len(set(vals)))
uniq_sorted = sorted(set(v for v in vals if v >= 0))
print("f2 唯一值范围: %d .. %d, 共 %d 个" % (uniq_sorted[0], uniq_sorted[-1], len(uniq_sorted)))
# 是否 0..N-1 全覆盖
if uniq_sorted[-1] < 500000:
    miss = 500000 - len(uniq_sorted)
    print("  0..499999 缺 %d 个" % miss)
