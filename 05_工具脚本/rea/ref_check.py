#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全局复核：188 个方法指针数组，每个在 .data/.rdata 中被引用的次数与偏移。
   期望：唯一引用，且引用槽 = 模块名槽 − 0x20。
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


refs = collections.defaultdict(list)   # VA -> [槽 RVA]
for nm, va, vs, rs, rp in SECS:
    if nm not in (".data", ".rdata") or rs == 0:
        continue
    end = rp + min(rs, vs if vs else rs)
    for r in range(rp, min(end, len(d)) - 8, 8):
        v = struct.unpack_from("<Q", d, r)[0]
        if IB <= v < IB + 0x40000000:
            refs[v].append(va + (r - rp))
print("引用槽索引完成：%d 个不同目标" % len(refs))

arrs = []
for ln in open(r"D:\Carol-start\_rea\bh3_modules_v2.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4 or not p[3].isdigit():
        continue
    arrs.append((p[1], int(p[2], 16)))
print("数组 %d 个" % len(arrs))

uniq = multi = none = 0
bad = []
for name, arr in arrs:
    r = refs.get(arr + IB, [])
    if len(r) == 1:
        uniq += 1
    elif not r:
        none += 1
        bad.append((name, arr, r))
    else:
        multi += 1
        bad.append((name, arr, r))
print("唯一引用 %d / 多处引用 %d / 无引用 %d" % (uniq, multi, none))
for b in bad[:8]:
    print("   %-40s arr=%08X refs=%s" % (b[0][:40], b[1], ["%08X" % x for x in b[2][:4]]))

# 引用槽与「模块名槽」的关系
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
    if r is None or r < 0 or r >= len(d):
        return None
    z = d.find(b"\0", r, min(r + 120, len(d)))
    if z < 0:
        return None
    t = d[r:z]
    if len(t) < 4 or any(c < 0x20 or c > 0x7E for c in t):
        return None
    return t.decode("latin1")


offs = collections.Counter()
for name, arr in arrs:
    r = refs.get(arr + IB, [])
    if len(r) != 1:
        continue
    slot = r[0]
    # 记录内名字槽应在 slot+0x20
    nmv = struct.unpack_from("<Q", d, slot + 0x20 - 0xC00)[0]
    s = cstr(nmv)
    if s and s.lower().endswith(".dll"):
        offs[0x20] += 1
    else:
        offs[("?", s)] += 1
print()
print("「引用槽 + 0x20 指回模块名」的命中数：%s" % offs.most_common(3))
