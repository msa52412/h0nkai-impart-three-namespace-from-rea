#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tbl5_verify.py —— 验证「表5 = 程序集映像表，192 个类型区间恰好铺满 0..57,486」。

段偏移 0x1C2A198，192 条 × 0x28，字段公式取自 §4.3。
"""
M32 = 0xFFFFFFFF
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
OFF = 0x1C2A198
N = 192
N_TYPES = 57487

d = open(META, "rb").read()


def prf(i):
    return ((((i * 0x14C3BD9234D3) >> 9) + 0x48C65E21) * 0x22343DDF >> 21) & M32


def u32(v):
    return v & M32


def s32(v):
    v &= M32
    return v - (1 << 32) if v & 0x80000000 else v


rows = []
for i in range(N):
    o = BASE + OFF + i * 0x28
    rec = [int.from_bytes(d[o + k * 4:o + k * 4 + 4], "little") for k in range(10)]
    p = prf(i)
    start = s32(((rec[8] - 0x3D2E6FE3 - p) & M32) ^ 0x1D3B2899)
    cnt = s32(((rec[4] - 0x7C293E16 - p) & M32) ^ 0x53C69178)
    rows.append((i, start, cnt))

bad = [r for r in rows if r[1] < 0 or r[2] < 0]
print("负数区间: %d" % len(bad))
rows2 = [r for r in rows if r[1] >= 0 and r[2] >= 0]
print("有效区间: %d / %d" % (len(rows2), N))
rows2.sort(key=lambda r: r[1])

print("\n前 8 个区间")
for r in rows2[:8]:
    print("  asm[%3d]  typeStart=%6d  typeCount=%6d  end=%6d" % (r[0], r[1], r[2], r[1] + r[2]))

# 连续性
gaps = 0
overl = 0
prev_end = 0
for r in rows2:
    if r[1] > prev_end:
        gaps += 1
    elif r[1] < prev_end:
        overl += 1
    prev_end = max(prev_end, r[1] + r[2])
print("\n区间接缝: 空隙 %d 段 / 重叠 %d 段" % (gaps, overl))
print("总覆盖 = %d，类型总数 = %d，差值 = %d" % (prev_end, N_TYPES, prev_end - N_TYPES))
