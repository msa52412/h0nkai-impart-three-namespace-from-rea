#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用字段反混淆常量求解器 v2（考虑 -1 哨兵）

模型： value_i = ((raw_i ^ C) - salt_i) mod 2^32
       value_i ∈ {-1} ∪ [0, T]
求解： 枚举 v0 ∈ {-1,0..T}，C = raw_0 ^ ((salt_0 + v0) mod 2^32)，
       再用多条记录验证 value ∈ {-1} ∪ [0,T]
"""
import struct
import sys

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
PROBES = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 19, 25, 40, 100, 500, 2000)


def solve(pos, Tmax):
    r0, s0 = RAW[0][pos], SALT[0]
    out = []
    for v0 in range(-1, Tmax + 1):
        C = r0 ^ ((s0 + v0) & M32)
        ok = True
        for i in PROBES:
            val = ((RAW[i][pos] ^ C) - SALT[i]) & M32
            if val != M32 and val > Tmax:
                ok = False
                break
        if ok:
            out.append(C)
            if len(out) > 6:
                return out
    return out


print("[校验] pos=8  nestedTypesStart  Tmax=30000")
r = solve(8, 30000)
print("  候选 %d: %s" % (len(r), ["0x%08X" % c for c in r]))
print("  含 0x21FE571D: %s\n" % (0x21FE571D in r))

TARGET = 408461
print("=" * 74)
print("[求解] 目标 Tmax=%d (方法数)" % TARGET)
print("%-4s %-12s %-8s %-12s %-12s %s" % ("pos", "C", "候选", "max", "非-1数", "前 8 值"))
for p in range(23):
    cands = solve(p, TARGET)
    if len(cands) != 1:
        print("%-4d %-12s %-8d" % (p, "--", len(cands)))
        continue
    C = cands[0]
    vals = [((RAW[i][p] ^ C) - SALT[i]) & M32 for i in range(NT)]
    nz = [v for v in vals if v != M32]
    print("%-4d 0x%08X   %-8d %-12d %-12d %s"
          % (p, C, 1, max(nz) if nz else -1, len(nz), [("-%d" % -1) if v == M32 else v for v in vals[:8]]))
