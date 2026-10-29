#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""穷举属性 type 列的表达式变体，按「能解析成合法 Il2CType」的比例打分"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
TP = 0x1C6766C
CTYPE_TBL = 0x186D41F80
NCT = 354184

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
    nm = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((nm, va, vs, rs, rp))


def va2off(va):
    rva = va - IB
    for nm, vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


BUF = open(META, "rb").read()
ct_off = va2off(CTYPE_TBL)


def prfP(i):
    t = ((i * 0x64D5) & M64) ^ 0x6D7B1F20
    t = (t + 0x10ECA71E) & M64
    t = (t * 0x7737C996) & M64
    return (((t >> 8) & M32) + 0x5505FF6B) & M32


NAMEK = 0xEACB0307

# CTYPE 索引 → 分类字节
TYPEB = []
PTR = []
for k in range(NCT):
    p = struct.unpack_from("<Q", d, ct_off + k * 8)[0]
    po = va2off(p)
    if po is None or po + 16 > len(d):
        TYPEB.append(-1)
        PTR.append(0)
        continue
    TYPEB.append(d[po + 10])
    PTR.append(struct.unpack_from("<Q", d, po)[0])


def valid(k):
    if k >= NCT:
        return 0
    t = TYPEB[k]
    if t in (0x11, 0x12, 0x15, 0x1C, 0x1D):
        return 1
    if 0x02 <= t <= 0x0E:
        return 1
    return 0


N = 5000
recs = []
for gi in range(N):
    o = BASE + TP + gi * 0x14
    p0, p1, p2, p3, p4 = struct.unpack_from("<5I", BUF, o)
    recs.append((p0, p1, p2, p3, p4, (prfP(gi) * NAMEK) & M32))

A = 0x90D97B9A
B = 0x79F46A96

VARS = {
    "((V+A)^B)": lambda v: (((v + A) & M32) ^ B),
    "((v^B)+A)": lambda v: (((v ^ B) + A) & M32),
    "(v^B^A)": lambda v: (v ^ B ^ A),
    "(v+A+B)": lambda v: (v + A + B) & M32,
    "(v^B)": lambda v: (v ^ B),
    "(v+A)": lambda v: (v + A) & M32,
    "((v-A)^B)": lambda v: (((v - A) & M32) ^ B),
    "((v^B)-A)": lambda v: (((v ^ B) - A) & M32),
}

for name, fn in VARS.items():
    n = 0
    for (p0, p1, p2, p3, p4, m) in recs:
        v = (p2 + m) & M32
        if valid(fn(v)):
            n += 1
    print("%-12s 合法率 %5d/%d (%.1f%%)" % (name, n, N, 100.0 * n / N))

print("\n[V 分布] 前 10 条")
for gi in range(10):
    p0, p1, p2, p3, p4, m = recs[gi]
    v = (p2 + m) & M32
    print("  gi=%d p2=%08X m=%08X V=%08X  ((V+A)^B)=%08X" % (gi, p2, m, v, (((v + A) & M32) ^ B)))

print("\n[尝试] 直接 V 作为索引")
n = sum(1 for (p0, p1, p2, p3, p4, m) in recs if valid((p2 + m) & M32))
print("  V 直用合法率 %d/%d" % (n, N))
