#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""反向引用查询：某个数组 RVA 在 .data/.rdata 中被哪些槽指向，
   并给出该槽相对「最近模块名槽」的偏移 —— 从而实测「数组字段」的真实偏移。
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
SEC = {nm: (va, vs, rs, rp) for nm, va, vs, rs, rp in SECS}


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
    if len(t) < 4 or any(c < 0x20 or c > 0x7E for c in t):
        return None
    return t.decode("latin1")


# 先收集所有「模块名槽」RVA（值是 "*.dll" 字符串指针）
name_slots = []
for nm, va, vs, rs, rp in SECS:
    if nm not in (".data", ".rdata") or rs == 0:
        continue
    end = rp + min(rs, vs if vs else rs)
    for r in range(rp, min(end, len(d)) - 8, 8):
        v = struct.unpack_from("<Q", d, r)[0]
        if not (IB <= v < IB + 0x12000000):
            continue
        s = cstr(v)
        if s and s.lower().endswith(".dll"):
            name_slots.append((va + (r - rp), s))
name_slots.sort()
print("模块名槽 %d 个" % len(name_slots))


def nearest_slot(rva_ref):
    best = None
    for s, sname in name_slots:
        dd = rva_ref - s
        if best is None or abs(dd) < abs(best[0]):
            best = (dd, sname, s)
    return best


for arg in sys.argv[1:]:
    t = int(arg, 16)
    tv = t + IB
    print("=" * 80)
    print("查询：谁指向 RVA %08X" % t)
    found = 0
    for nm, va, vs, rs, rp in SECS:
        if nm not in (".data", ".rdata") or rs == 0:
            continue
        end = rp + min(rs, vs if vs else rs)
        for r in range(rp, min(end, len(d)) - 8, 8):
            v = struct.unpack_from("<Q", d, r)[0]
            if v != tv:
                continue
            ref = va + (r - rp)
            dd, sname, s = nearest_slot(ref)
            print("   槽 RVA %08X  偏移相对名槽 %+d  → %s" % (ref, dd, sname))
            found += 1
    print("   命中 %d 处" % found)
