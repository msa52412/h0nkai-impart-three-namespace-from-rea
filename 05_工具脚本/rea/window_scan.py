#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环形窗口分析：一次性解出所有 SUB 型字段

原理：SUB 型 value = (raw - C - salt) mod 2^32 ∈ {-1} ∪ [0,T]
      即 w = (raw - salt) mod 2^32 ∈ {(C-1)} ∪ [C, C+T]  (mod 2^32)
      —— w 必聚在一个长度 T+1 的环形窗口内
      排序后找最大 circular gap，窗口起点即 C-1 或 C

对每个 pos 输出：窗口大小（即 T+1）、起点、value 分布
"""
import struct
from collections import Counter

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487

with open(DLL, "rb") as f:
    dll = f.read()
e = struct.unpack_from("<I", dll, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", dll, coff + 2)[0]
optsz = struct.unpack_from("<H", dll, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", dll, opt + 24)[0]
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    vs, va, rs, rp = struct.unpack_from("<IIII", dll, o + 8)
    SECS.append((va, vs, rs, rp))


def u32va(va):
    rva = va - IB
    for vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else struct.unpack_from("<I", dll, rptr + (rva - vaddr))[0]
    return None


TYPE_OFF = (u32va(0x188198E08) ^ 0x2B849DB3) & M32
with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
T0 = BASE + TYPE_OFF

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

RAW = [struct.unpack_from("<23I", BUF, T0 + i * STEP) for i in range(NT)]

REF = {5: "methodStart(已知)", 8: "nestedStart(XOR,不会命中)", 12: "namespace(已知)",
       13: "name(XOR,不会命中)"}

print("%-4s %-12s %-11s %-9s %-8s %s" % ("pos", "窗口T+1", "C(guess)", "-1数", "max", "标注"))
results = {}
for p in range(23):
    w = sorted(((RAW[i][p] - SALT[i]) & M32) for i in range(NT))
    n = len(w)
    # circular max gap
    maxgap = 0
    gappos = -1
    for k in range(n):
        nxt = w[(k + 1) % n]
        gap = (nxt - w[k]) & M32
        if k == n - 1:
            gap = (w[0] + (1 << 32) - w[k]) & M32
        if gap > maxgap:
            maxgap = gap
            gappos = k
    if gappos == -1:
        continue
    start = w[(gappos + 1) % n]  # 窗口起点
    T1 = ((1 << 32) - maxgap) & M32  # 窗口大小
    if T1 > FSIZE:
        print("%-4d %-12s 窗口太大(%d)" % (p, "--", T1))
        results[p] = None
        continue
    # C 候选：start 或 start+1（窗口内首值可能是 -1 哨兵）
    # 窗口起点 = C-1（若 -1 哨兵存在且是窗口最小值）
    cands = [start, (start + 1) & M32]
    best = None
    for C in cands:
        vals = [((RAW[i][p] - C - SALT[i]) & M32) for i in range(NT)]
        nm1 = sum(1 for v in vals if v == M32)
        valid = [v for v in vals if v != M32]
        if max(valid) < 0x300000 and len(valid) >= 3:
            best = (C, nm1, max(valid), min(valid), len(set(valid)))
    if best is None:
        print("%-4d %-12s 验证失败 T1=%d" % (p, "--", T1))
        results[p] = None
        continue
    C, nm1, mx, mn, uniq = best
    print("%-4d %-12d 0x%08X  %-9d %-8d min=%d uniq=%d %s"
          % (p, T1, C, nm1, mx, mn, uniq, REF.get(p, "")))
    results[p] = (C, nm1, mx, T1)
