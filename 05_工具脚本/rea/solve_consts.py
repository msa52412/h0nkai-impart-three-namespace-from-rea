#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用字段反混淆常量求解器

模型：value_i = ((raw_i ^ C) - salt_i) mod 2^32，且 value_i ∈ [0, T]
则   C ∈ raw_i ^ [salt_i, salt_i + T]  （对每个 i 都成立）
取若干 i 的集合交集，即可唯一确定 C。

先用已知的 pos=8 / C=0x21FE571D 做正确性校验。
"""
import struct

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
T = BASE + TYPE_OFF

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

RAW = [[struct.unpack_from("<I", BUF, T + i * STEP + p * 4)[0] for p in range(23)] for i in range(NT)]


def solve(pos, Tmax, probes=(0, 1, 2, 3, 4, 5, 7, 11)):
    """返回满足所有 probe 的 C 候选集合"""
    cur = None
    for i in probes:
        s, r = SALT[i], RAW[i][pos]
        cand = set()
        for v in range(Tmax + 1):
            cand.add(r ^ ((s + v) & M32))
        cur = cand if cur is None else (cur & cand)
        if not cur:
            return set()
        if len(cur) <= 4:
            break
    return cur


print("=" * 70)
print("[校验] pos=8 (nestedTypesStart), Tmax=30000")
res = solve(8, 30000)
print("  候选 %d 个: %s" % (len(res), ["0x%08X" % c for c in sorted(res)[:6]]))
print("  期望包含 0x21FE571D -> %s" % ("OK" if 0x21FE571D in res else "MISS"))

print("\n" + "=" * 70)
print("[求解] 对 23 个位置，Tmax=500000")
print("%-4s %-12s %-10s %-12s %s" % ("pos", "C", "候选数", "value_max", "value 前 6"))
for p in range(23):
    r = solve(p, 500000)
    if len(r) != 1:
        print("%-4d %-12s %-10d -" % (p, "(无解/多解)", len(r)))
        continue
    C = r.pop()
    vals = [((RAW[i][p] ^ C) - SALT[i]) & M32 for i in range(NT)]
    print("%-4d 0x%08X   %-10d %-12d %s" % (p, C, 1, max(vals), vals[:6]))
