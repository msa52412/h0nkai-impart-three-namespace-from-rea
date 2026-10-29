#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v5 = v4 + fieldCount 列（metadata typedef +0x4E, SUB -2）
不重算其他列，避免回归风险。
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
SRC = r"D:\Carol-start\_rea\bh3_types_v4.txt"
DST = r"D:\Carol-start\_rea\bh3_types_v5.txt"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487

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

fcnt = []
for i in range(NT):
    raw = struct.unpack_from("<H", BUF, T0 + i * STEP + 0x4E)[0]
    sr = raw - 0x10000 if raw & 0x8000 else raw
    fcnt.append((sr - 2 - S16[i]) & 0xFFFF)

lines = open(SRC, encoding="utf-8").read().split("\n")
hdr = lines[0].rstrip() + "\tfieldCount"
out = [hdr]
n = 0
for ln in lines[1:]:
    if not ln.strip():
        continue
    p = ln.split("\t")
    idx = int(p[0])
    out.append(ln.rstrip("\n") + "\t%d" % fcnt[idx])
    n += 1

with open(DST, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

print("写入 %s  行数 %d" % (DST, n))
print("fieldCount 合计 = %d" % sum(fcnt))
print("非零字段类型数 = %d" % sum(1 for x in fcnt if x))
