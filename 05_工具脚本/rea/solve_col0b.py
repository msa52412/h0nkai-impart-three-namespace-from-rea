#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""solve_col0b.py —— col0 常数反推（变体：允许 col0 是全局文件偏移而非 blob 内偏移）

E90 表 77,396 行在 metadata 内 TBL=0x1EC6738，表尾=0x1F5D9D8。
若 blob 区在表之后（0x1F5D9D8 + 字段表 + …），col0 可能是【文件全局偏移】，
量级可到 0x35D387C。放宽 MAX 到 0x3600000 重试交集。
另试 col0 = (raw0 ^ key) 混合族。
"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
TBL = 0x118 + 0x1EC6620
N = 77396
FS = len(BUF)


def key(i):
    v = (i * 0x1AB6B1E4CD9A) & M64
    v >>= 0xB
    v = (v * 0x6595FC2F) & M64
    v ^= 0x790A43A40000
    v >>= 0x11
    return v & M32


def try_family(name, decode):
    """decode(raw, k) -> set of C 使 (decode 后) ∈ [0, FS)"""
    cand = None
    for i in range(0, N, N // 24):
        raw = struct.unpack_from("<I", BUF, TBL + i * 8)[0]
        k = key(i)
        s = decode(raw, k)
        cand = s if cand is None else (cand & s)
        if cand is not None and not cand:
            print("  %s: 空集 @ i=%d" % (name, i))
            return
    if not cand:
        print("  %s: 无交集" % name)
        return
    # 单调筛
    ok = []
    for C in cand:
        prev = -1
        good = True
        for i in range(0, N, max(1, N // 100)):
            raw = struct.unpack_from("<I", BUF, TBL + i * 8)[0]
            v = (raw - key(i) - C) & M32 if name == "sub" else ((raw ^ C) - key(i)) & M32
            if v < prev:
                good = False
                break
            prev = v
        if good:
            ok.append(C)
    print("  %s: 候选 %d, 单调 %d: %s" % (name, len(cand), len(ok), [hex(c) for c in ok[:5]]))


def main():
    # 族1: v = (raw - k - C) & M32, v ∈ [0, FS)
    def f1(raw, k):
        base = (raw - k) & M32
        lo = (base - FS + 1) & M32
        if lo <= base:
            return set(range(lo, base + 1))
        return set(range(lo, M32 + 1)) | set(range(0, base + 1))
    try_family("sub", f1)

    # 族2: v = ((raw ^ C) - k) & M32 —— 逆不动（C 未知在 xor 里），穷举代价高，跳过
    print("done")


if __name__ == "__main__":
    main()
