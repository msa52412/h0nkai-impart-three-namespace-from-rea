#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐 8 字节标注一段内存：代码指针 / 名字串 / 已知常量 / 零。
   用于精确还原 CodeGenModule 记录与其数组的相对位置。
"""
import struct
import sys

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
IB = 0x180000000
d = open(PATH, "rb").read()

e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
SECS = []
for i in range(nsec):
    o = coff + 20 + optsz + i * 40
    nm = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((nm, va, vs, rs, rp))


def rva2raw(rva):
    if 0 <= rva < 0x6C56000:
        return rva - 0xC00
    for nm, va, vs, rs, rp in SECS:
        if nm in (".reloc", ".text", ".pdata"):
            continue
        if va <= rva < va + max(vs, rs) and rs:
            return rp + (rva - va)
    return None


def cstr(va):
    if not (IB <= va < IB + 0x12000000):
        return None
    r = rva2raw(va - IB)
    if r is None or r >= len(d):
        return None
    z = d.find(b"\0", r, min(r + 120, len(d)))
    if z < 0:
        return None
    t = d[r:z]
    if len(t) < 3 or any(c < 0x20 or c > 0x7E for c in t):
        return None
    return t.decode("latin1")


lo = int(sys.argv[1], 16)
n = int(sys.argv[2]) if len(sys.argv) > 2 else 48
raw = rva2raw(lo)
for i in range(n):
    rva = lo + i * 8
    v = struct.unpack_from("<Q", d, raw + i * 8)[0]
    l32 = v & 0xFFFFFFFF
    tag = ""
    if v == 0:
        tag = "0"
    elif IB <= v < IB + 0x12000000:
        r = v - IB
        s = cstr(v)
        if s:
            tag = "STR " + s
        elif 0x1000 <= r < 0x6C56000:
            tag = "CODE %08X" % r
        else:
            tag = "PTR  %08X" % r
    else:
        tag = "CONST"
        if (l32 >> 24) == 0x3A:
            tag = "HASH 3A121Dxx"
        if v == 0x096249C907083E19:
            tag = "CONST 096249C907083E19"
        if (l32 >> 24) == 0x6A and (l32 & 0xFFF00000) == 0x6AAF6000:
            tag = "CONST 6AAF6xxx"
        if (l32 >> 24) == 0x63:
            tag = "TS 63D5xxxx"
        if (l32 >> 24) == 0x06:
            tag = "TOKEN 06xxxxxx"
    print("  %08X  +%03X  %016X  %s" % (rva, i * 8, v, tag))
