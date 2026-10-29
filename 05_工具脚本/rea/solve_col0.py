#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""solve_col0.py —— E90 blob 描述表 col0（dataOffset）的解密常数反推

已知：
  表 TBL = 0x118 + 0x1EC6620，77,396 行 × 8B，紧贴字段表（表尾 0x1F5D9D8 = F0）
  col1(len) = (raw1 - key(i) - 0x25C2F1A9) & M32      ← 已验证（77,396 行全 < 0x10000）
  key(i) = ((((i * 0x1AB6B1E4CD9A) >> 0xB) * 0x6595FC2F ^ 0x790A43A40000) >> 0x11) & M32
  col0 应是 blob 区内偏移：单调不减，量级 ~ MB

方法：col0 = (raw0 - key(i) - C) & M32。对 i=0..N 抽 64 行，
  把每行可能的 C 值域算出来（v < 0x2000000），求交集。
"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
TBL = 0x118 + 0x1EC6620
N = 77396
MAXBLOB = 0x2000000      # 32 MB 上限（metadata 才 56MB）


def key(i):
    v = (i * 0x1AB6B1E4CD9A) & M64
    v >>= 0xB
    v = (v * 0x6595FC2F) & M64
    v ^= 0x790A43A40000
    v >>= 0x11
    return v & M32


def main():
    import sys
    step = N // 48
    idxs = list(range(0, N, step))[:48]
    cand = None
    for i in idxs:
        raw = struct.unpack_from("<I", BUF, TBL + i * 8)[0]
        k = key(i)
        # v = (raw - k - C) mod 2^32 ∈ [0, MAXBLOB)
        # → C ∈ (raw - k - MAXBLOB, raw - k]  （mod 2^32 的一段区间）
        base = (raw - k) & M32
        lo = (base - MAXBLOB + 1) & M32
        s = set()
        if lo <= base:
            s = set(range(lo, base + 1))
        else:
            # 环绕：两段
            s = set(range(lo, M32 + 1)) | set(range(0, base + 1))
        cand = s if cand is None else (cand & s)
        if not cand:
            print("交集为空 @ i=%d" % i)
            return
    print("候选 C 数量:", len(cand))
    # 用单调性进一步筛
    ok = []
    for C in cand:
        prev = -1
        good = True
        for i in range(0, N, max(1, N // 200)):
            raw = struct.unpack_from("<I", BUF, TBL + i * 8)[0]
            v = (raw - key(i) - C) & M32
            if v < prev:
                good = False
                break
            prev = v
        if good:
            ok.append(C)
    print("单调候选:", [hex(c) for c in ok[:10]])
    if ok:
        C = ok[0]
        mx = 0
        for i in range(N):
            raw = struct.unpack_from("<I", BUF, TBL + i * 8)[0]
            v = (raw - key(i) - C) & M32
            if v > mx:
                mx = v
        print("C=0x%X  maxOffset=0x%X (%.1f MB)" % (C, mx, mx / 1048576))


if __name__ == "__main__":
    main()
