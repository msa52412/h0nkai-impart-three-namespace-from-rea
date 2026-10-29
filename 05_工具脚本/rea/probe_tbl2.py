#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第二张指针表 PTR_PTR_1881a35f0 探测
FUN_180430980:
  puVar9 = *(uint**)(PTR_PTR_1881a35f0 + typedefIdx*8)
  +0x100 = puVar9[2] + 0xd5afdcdb
  +0x104 = puVar9[1] ^ 0x10f25b04
  +0x110 = puVar9[3] + 0xf3c1e707
  +0x114 = +0x11C = puVar9[0] ^ 0x6203cc4e
用 sum 与 metadata 已知 count 对齐，判定各字段语义。
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
TBL2_VA = 0x18901BAE0

d = open(DLL, "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", d, opt + 24)[0]
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    name = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((name, va, vs, rs, rp))


def va2off(va):
    rva = va - IB
    for name, vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


o2 = va2off(TBL2_VA)
print("PTR_PTR_1881a35f0 = 0x%X -> file 0x%X" % (TBL2_VA, o2))

# 探测表2 是否指针数组
cnt_ok = 0
for i in range(20):
    p = struct.unpack_from("<Q", d, o2 + i * 8)[0]
    if va2off(p) is not None:
        cnt_ok += 1
print("前 20 项落在镜像内: %d/20  首项=0x%X" % (cnt_ok, struct.unpack_from("<Q", d, o2)[0]))

# metadata 侧
BUF = open(META, "rb").read()
TYPE_OFF = (struct.unpack_from("<I", d, va2off(0x188198E08))[0] ^ 0x2B849DB3) & M32
T0 = BASE + TYPE_OFF
SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)
S16 = [(SALT[i] & 0xFFFF) - 0x10000 if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]

# metadata u16 counts
META_SUM = Counter()
meta_vals = {}
for i in range(NT):
    off = T0 + i * STEP
    s = SALT[i]
    s16 = S16[i]
    vals = {}
    r = struct.unpack_from("<I", BUF, off + 0x44)[0]
    vals[0x44] = ((r & 0xFFFF) ^ 0x910A) - s16 & 0xFFFF
    r = struct.unpack_from("<H", BUF, off + 0x46)[0]
    vals[0x46] = ((r ^ 0x7883) - s16) & 0xFFFF
    r = struct.unpack_from("<H", BUF, off + 0x48)[0]
    sr = r - 0x10000 if r & 0x8000 else r
    vals[0x48] = (sr + 0x1950 - s16) & 0xFFFF
    r = struct.unpack_from("<H", BUF, off + 0x4A)[0]
    sr = r - 0x10000 if r & 0x8000 else r
    vals[0x4A] = (sr + 0x17A3 - s16) & 0xFFFF
    r = struct.unpack_from("<H", BUF, off + 0x4C)[0]
    vals[0x4C] = ((r ^ 0x5BE4) - s16) & 0xFFFF
    r = struct.unpack_from("<H", BUF, off + 0x4E)[0]
    sr = r - 0x10000 if r & 0x8000 else r
    vals[0x4E] = (sr + 2 - s16) & 0xFFFF
    r = struct.unpack_from("<H", BUF, off + 0x50)[0]
    sr = r - 0x10000 if r & 0x8000 else r
    vals[0x50] = (sr + 0x27E6 - s16) & 0xFFFF
    r = struct.unpack_from("<H", BUF, off + 0x52)[0]
    sr = r - 0x10000 if r & 0x8000 else r
    vals[0x52] = (sr + 0x1197 - s16) & 0xFFFF
    meta_vals[i] = vals
    for k, v in vals.items():
        META_SUM[k] += v

print("\n[metadata u16 字段 sum]")
for k in sorted(META_SUM):
    print("  +0x%02X = %d" % (k, META_SUM[k]))

# 表2 解码
T2_SUM = Counter()
t2_vals = {}
bad = 0
for i in range(NT):
    p = struct.unpack_from("<Q", d, o2 + i * 8)[0]
    po = va2off(p)
    if po is None:
        bad += 1
        t2_vals[i] = None
        continue
    a, b, c, dd = struct.unpack_from("<4I", d, po)
    v = {0: (a ^ 0x6203CC4E) & M32, 1: (b ^ 0x10F25B04) & M32,
         2: (c + 0xD5AFDCDB) & M32, 3: (dd + 0xF3C1E707) & M32}
    t2_vals[i] = v
    for k, x in v.items():
        T2_SUM[k] += x

print("\n[表2 四字段 sum]  坏指针 %d" % bad)
for k in sorted(T2_SUM):
    print("  [%d] = %d" % (k, T2_SUM[k]))

print("\n[对照] 已知: method 408,458/408,461  property 56,137  nested 21,429  "
      "interfaces 22,464  event 58,954  vtable 782,396")

# 逐条相关性：表2 各字段 vs metadata 各字段 命中率
print("\n[逐条命中率] 表2[i] == metadata[i] 的条数")
for k2 in sorted(T2_SUM):
    best = []
    for k1 in sorted(META_SUM):
        hit = sum(1 for i in range(NT)
                  if t2_vals[i] and t2_vals[i][k2] == meta_vals[i][k1])
        best.append((hit, k1))
    best.sort(reverse=True)
    top = best[0]
    print("  表2[%d] -> metadata +0x%02X  命中 %d/%d (%.1f%%)  次优 +0x%02X %d"
          % (k2, top[1], top[0], NT, 100.0 * top[0] / NT, best[1][1], best[1][0]))
