#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
类型表字段语义识别（N=57487 已验证）

约束：
  sum(method_count) == 408461   (方法表已独立解出)
  sum(field_count)  == 字段表大小
  methodStart / fieldStart 应单调铺满
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
T_ABS = BASE + TYPE_OFF

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

REC = [struct.unpack_from("<23I", BUF, T_ABS + i * STEP) for i in range(NT)]

print("N = %d" % NT)
print("\n[*] 每个位置 v = (raw - salt) mod 2^32 的统计")
print("%-4s %-11s %-11s %-8s %-9s %-9s %s" % ("pos", "min", "max", "uniq", "max<1e5", "max<1e6", "前5值"))
for p in range(23):
    vals = [((REC[i][p] - SALT[i]) & M32) for i in range(NT)]
    print("%-4d %-11d %-11d %-8d %-9s %-9s %s"
          % (p, min(vals), max(vals), len(set(vals)),
             max(vals) < 100000, max(vals) < 1000000,
             " ".join("%d" % v for v in vals[:5])))

print("\n[*] 用 sum(count)==%d 定位 method_count" % N_METHOD)
for p in range(23):
    vals = [((REC[i][p] - SALT[i]) & M32) for i in range(NT)]
    base = min(vals)
    d = [v - base for v in vals]
    tot = sum(x for x in d if x < 200000)
    if abs(tot - N_METHOD) < N_METHOD * 0.05:
        print("    pos=%d  base=%d  sum=%d  差=%+d" % (p, base, tot, tot - N_METHOD))
        print("        最大值=%d  前10=%s" % (max(d), d[:10]))

print("\n[*] 找 offset 型字段（值 < 文件大小且随 i 递增）")
for p in range(23):
    vals = [((REC[i][p] - SALT[i]) & M32) for i in range(NT)]
    base = min(vals)
    d = [v - base for v in vals]
    if max(d) > FSIZE:
        continue
    inc = sum(1 for i in range(1, min(NT, 5000)) if d[i] >= d[i - 1])
    print("    pos=%-3d base=%-10d max=%-10d 递增率=%.1f%%  前6=%s"
          % (p, base, max(d), 100.0 * inc / 4999, d[:6]))
