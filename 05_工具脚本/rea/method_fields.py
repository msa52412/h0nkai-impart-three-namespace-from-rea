#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在方法表记录（0x20 = 8 dword）里找 declaringType 索引字段。
已知 +0x0C = 方法名 ID，+0x1C = flag(byte)。
若某位置的值域落在 [0, 57487) 且随 i 单调不减 -> declaringTypeIndex
"""
import struct
from collections import Counter

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
MSTEP = 0x20
NM = 408461
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


M_OFF = (u32va(0x188198E58) - 0x017A3B99) & M32
with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
MA = BASE + M_OFF

# 方法表 PRF（已验证 100%）
PRF = []
for i in range(NM + 1):
    x = ((i * 0xB069) ^ 0x3E382F2D) & M64
    x = (x * 0x24147491) & M64
    x = (x ^ 0xF997B4A800) >> 10
    x = (x * 0x3857AACA) & M64
    PRF.append(x >> 0xE)

print("方法表 0x%X  条数 %d" % (MA, NM))
print("\n[*] 8 个 dword 位置：v=(raw-prf) 的分布")
print("%-4s %-11s %-11s %-8s %-10s %-10s %s"
      % ("pos", "min", "max", "uniq", "<57487", "<600k", "前6"))
for p in range(8):
    vals = [((struct.unpack_from("<I", BUF, MA + i * MSTEP + p * 4)[0] - PRF[i]) & M32)
            for i in range(NM)]
    print("%-4d %-11d %-11d %-8d %-10d %-10d %s"
          % (p, min(vals), max(vals), len(set(vals)),
             sum(1 for v in vals if v < NT), sum(1 for v in vals if v < 600000),
             vals[:6]))

print("\n[*] 试 XOR 变换")
for p in range(8):
    for c in (0x1D64B276, 0x3399EFB, 0x21FE571D):
        vals = [((struct.unpack_from("<I", BUF, MA + i * MSTEP + p * 4)[0] ^ c) - PRF[i]) & M32
                for i in range(NM)]
        ok = sum(1 for v in vals if v < NT)
        if ok > NM * 0.5:
            inc = sum(1 for i in range(1, NM) if vals[i] >= vals[i - 1])
            print("    pos=%d ^0x%X -> %d/%d 在[0,%d)  递增率 %.1f%%  前8=%s"
                  % (p, c, ok, NM, NT, 100.0 * inc / (NM - 1), vals[:8]))

print("\n[*] 试 (raw ^ C) 全空间暴力：找落在 [0,57487) 最多的 C（pos=0..7）")
for p in range(8):
    best = None
    for c in [0x1D64B276, 0x3399EFB, 0x21FE571D, 0x0, 0xFFFFFFFF]:
        vals = [((struct.unpack_from("<I", BUF, MA + i * MSTEP + p * 4)[0] ^ c) - PRF[i]) & M32
                for i in range(0, NM, 13)]
        ok = sum(1 for v in vals if v < NT)
        if best is None or ok > best[1]:
            best = (c, ok)
    print("    pos=%d best C=0x%X  %d/%d" % (p, best[0], best[1], len(range(0, NM, 13))))
