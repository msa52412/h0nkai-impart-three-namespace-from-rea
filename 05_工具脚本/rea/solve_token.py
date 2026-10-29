#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1) pos=22 token 假设精确求解（B=0x02000000, T=60000, 全枚举）
2) pos=10 fieldStart 单调性验证 + 字段总数差分
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
T0 = BASE + TYPE_OFF

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

RAW = [struct.unpack_from("<23I", BUF, T0 + i * STEP) for i in range(NT)]
PROBES = (0, 1, 2, 3, 4, 5, 7, 11, 12, 19, 25, 40, 100, 500, 2000, 5000, 20000, 50000)

# ---------- 1. pos=22 token 精确求解 ----------
print("=" * 70)
print("[pos=22 token] B=0x02000000 T=60000 全枚举")
B, T = 0x02000000, 60000
r0, s0 = RAW[0][22], SALT[0]
cands = []
for v0 in [M32] + list(range(B, B + T + 1)):
    C = r0 ^ ((s0 + v0) & M32)
    ok = True
    for i in PROBES:
        val = ((RAW[i][22] ^ C) - SALT[i]) & M32
        if val != M32 and not (B <= val <= B + T):
            ok = False
            break
    if ok:
        cands.append(C)
        if len(cands) > 8:
            break
print("候选 %d: %s" % (len(cands), ["0x%08X" % c for c in cands]))
if len(cands) >= 1:
    for C in cands:
        vals = [((RAW[i][22] ^ C) - SALT[i]) & M32 for i in range(NT)]
        nz = [v for v in vals if v != M32]
        inb = sum(1 for v in nz if B <= v <= B + T)
        print("  C=0x%08X 有效=%d 窗口内=%d uniq=%d" % (C, len(nz), inb, len(set(nz))))

# ---------- 2. fieldStart (pos=10) ----------
print("\n" + "=" * 70)
print("[pos=10 fieldStart]  C=0x67B0A1F5")
C10 = 0x67B0A1F5
v10 = [((RAW[i][10] - C10 - SALT[i]) & M32) for i in range(NT)]
nm1 = sum(1 for v in v10 if v == M32)
nz = [i for i in range(NT) if v10[i] != M32]
print("  -1 数=%d  非空=%d  值域=[%d, %d]" % (nm1, len(nz), min(v10[i] for i in nz), max(v10[i] for i in nz)))
desc = sum(1 for k in range(len(nz) - 1) if v10[nz[k + 1]] < v10[nz[k]])
print("  非空子序列递减处 = %d" % desc)
if desc == 0:
    cnts = []
    for k in range(len(nz)):
        if k + 1 < len(nz):
            cnts.append(v10[nz[k + 1]] - v10[nz[k]])
    print("  差分 count: 前10=%s max=%d =0数=%d" % (cnts[:10], max(cnts), sum(1 for c in cnts if c == 0)))
    print("  最后 fieldStart=%d → 字段总数 ≥ %d + last_count" % (v10[nz[-1]], v10[nz[-1]]))
    # 严格 0..max 排列检查（fieldStart 无空段时应为连续覆盖）
    s = sorted(v10[i] for i in nz)
    gaps = [(a, b) for a, b in zip(s, s[1:]) if b - a > 1]
    print("  连续性: min=%d max=%d 间隔>1 处=%d" % (s[0], s[-1], len(gaps)))
    if gaps[:5]:
        print("    间隔样本:", [(hex(a), hex(b), b - a) for a, b in gaps[:5]])
