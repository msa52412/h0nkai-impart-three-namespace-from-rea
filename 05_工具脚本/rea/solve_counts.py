#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1) 验证 pos=5 是否 methodStart（单调性 / 覆盖）
2) 对 8 个 u16 位置求解 count 的 XOR 常量（16 位暴力，T 小）
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
N_METHOD = 408461

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

# ---------- 1. pos=5 ----------
w5 = [((RAW[i][5] - SALT[i]) & M32) for i in range(NT)]
C5 = min(w5)
v5 = [x - C5 for x in w5]
print("[pos=5]  C=0x%08X  v范围=[%d, %d]  跨度=%d" % (C5, min(v5), max(v5), max(v5)))
print("        唯一值 %d 个, 重复值 %d 个" % (len(set(v5)), NT - len(set(v5))))
neg = sum(1 for i in range(NT - 1) if v5[i + 1] < v5[i])
print("        递减处 %d, 最大回退 %d" % (neg, max(v5[i] - v5[i + 1] for i in range(NT - 1) if v5[i + 1] < v5[i]) if neg else 0))
print("        是否 0..%d 的排列: %s" % (max(v5), sorted(v5) == list(range(max(v5) + 1))))

# 递减点的记录特征
bad = [i for i in range(NT - 1) if v5[i + 1] < v5[i]]
print("        前 6 个递减点 i=%s" % bad[:6])
for i in bad[:3]:
    print("          i=%-6d v5=%-8d -> v5=%-8d" % (i, v5[i], v5[i + 1]))

# ---------- 2. u16 count 求解 ----------
print("\n" + "=" * 78)
print("[u16 count]  T=8192，验证 value ∈ [0,T]")
PROBES = (0, 1, 2, 3, 4, 5, 7, 11, 12, 19, 25, 40, 100, 500, 2000)
U16 = {}
for off in (0x44, 0x46, 0x48, 0x4A, 0x4C, 0x4E, 0x50, 0x52):
    U16[off] = [struct.unpack_from("<H", BUF, T0 + i * STEP + off)[0] for i in range(NT)]

for off, arr in U16.items():
    s0 = SALT[0] & 0xFFFF
    r0 = arr[0]
    Tmax = 8192
    cands = []
    for v0 in range(-1, Tmax + 1):
        C = (r0 ^ ((s0 + v0) & 0xFFFF)) & 0xFFFF
        ok = True
        for i in PROBES:
            val = ((arr[i] ^ C) - (SALT[i] & 0xFFFF)) & 0xFFFF
            if val != 0xFFFF and val > Tmax:
                ok = False
                break
        if ok:
            cands.append(C)
            if len(cands) > 4:
                break
    if len(cands) == 1:
        C = cands[0]
        vals = [((arr[i] ^ C) - (SALT[i] & 0xFFFF)) & 0xFFFF for i in range(NT)]
        nz = [v for v in vals if v != 0xFFFF]
        print("  0x%02X  C=0x%04X  sum=%-8d 非-1=%-7d max=%-6d 前10=%s"
              % (off, C, sum(nz), len(nz), max(nz) if nz else -1, vals[:10]))
    else:
        print("  0x%02X  候选 %d 个" % (off, len(cands)))
