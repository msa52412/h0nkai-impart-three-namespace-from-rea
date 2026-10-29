#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""观察某个候选数组及其「引用槽位」周边的原始内存，判断真实结构。"""
import struct
import sys

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
IB = 0x180000000
LO = 0x180001000
HI = 0x186C56000
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
    if rva < 0x6C56000:
        return rva - 0xC00
    for nm, va, vs, rs, rp in SECS:
        if nm in (".reloc", ".text", ".pdata"):
            continue
        if va <= rva < va + max(vs, rs) and rs:
            return rp + (rva - va)
    return None


def tag(v):
    if v == 0:
        return "0"
    if LO <= v < HI:
        return "CODE"
    if IB <= v < IB + 0x12000000:
        return "PTR"
    return ""


def dump(rva, n=24, label=""):
    raw = rva2raw(rva)
    print("---- %s RVA %08X (raw %08X) ----" % (label, rva, raw if raw else 0))
    for i in range(n):
        v = struct.unpack_from("<Q", d, raw + i * 8)[0]
        lo = struct.unpack_from("<I", d, raw + i * 8)[0]
        hi = struct.unpack_from("<I", d, raw + i * 8 + 4)[0]
        extra = ""
        if tag(v) == "PTR" or tag(v) == "CODE":
            r = rva2raw(v - IB)
            if r and 0 <= r < len(d):
                z = d.find(b"\0", r, min(r + 64, len(d)))
                t = d[r:z] if z > r else b""
                if len(t) >= 4 and all(0x20 <= c <= 0x7E for c in t):
                    extra = repr(t.decode("latin1"))
        print("  +%03X  %016X   lo=%-10u hi=%-10u %-5s %s" % (i * 8, v, lo, hi, tag(v), extra))


for a in sys.argv[1:]:
    base = int(a, 16)
    dump(base - 0x40, 10, "数组前")
    dump(base, 12, "数组头")
