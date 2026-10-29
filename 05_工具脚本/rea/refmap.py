#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对每个数组引用槽，扫描 ±0x48 内所有 .dll 名字指针，统计「名字槽相对数组槽」的偏移分布。
   若偏移不唯一，说明记录布局存在变体，需要按变体解析名字。
"""
import collections
import struct

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


def q(rva):
    r = rva2raw(rva)
    return None if r is None else struct.unpack_from("<Q", d, r)[0]


def cstr(va):
    if not (IB <= va < IB + 0x12000000):
        return None
    r = rva2raw(va - IB)
    if r is None or r < 0 or r >= len(d):
        return None
    z = d.find(b"\0", r, min(r + 120, len(d)))
    if z < 0:
        return None
    t = d[r:z]
    if len(t) < 4 or any(c < 0x20 or c > 0x7E for c in t):
        return None
    return t.decode("latin1")


refs = collections.defaultdict(list)
for nm, va, vs, rs, rp in SECS:
    if nm not in (".data", ".rdata") or rs == 0:
        continue
    end = rp + min(rs, vs if vs else rs)
    for r in range(rp, min(end, len(d)) - 8, 8):
        v = struct.unpack_from("<Q", d, r)[0]
        if IB <= v < IB + 0x40000000:
            refs[v].append(va + (r - rp))

arrs = []
for ln in open(r"D:\Carol-start\_rea\bh3_modules_v2.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4 or not p[3].isdigit():
        continue
    arrs.append((p[1], int(p[2], 16)))

offs = collections.Counter()
rows = []
for name, arr in arrs:
    r = refs.get(arr + IB, [])
    if len(r) != 1:
        continue
    slot = r[0]
    found = None
    for o in range(-0x48, 0x8C, 8):
        v = q(slot + o)
        if not v:
            continue
        s = cstr(v)
        if s and s.lower().endswith(".dll"):
            offs[o] += 1
            if o == 0x20:
                found = s
            if found is None:
                found = s
    rows.append((name, arr, slot, found))

print("「名字槽相对数组引用槽」偏移分布：%s" % offs.most_common(8))
print("每模块第一个命中：")
for name, arr, slot, found in rows[:10]:
    print("   %-44s arr=%08X slot=%08X name=%s%s" % (name[:44], arr, slot, found, "" if found == name else "   << 不一致"))
mis = [r for r in rows if r[3] and r[3] != r[0]]
print("名字与 TSV 记录不一致的模块：%d 个" % len(mis))
for r in mis[:10]:
    print("   %-40s TSV=%s  实际=%s" % (r[2], r[0][:40], r[3]))
