#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描全部 Il2CType 条目，统计 VAR(0x13)/MVAR(0x1E) 的全局形参索引分布。
目的：确定全局泛型形参总数 N，用于在 192 张表中反查形参名表。
"""
import struct, collections

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
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
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((va, vs, rs, rp))


def va2off(va):
    rva = va - IB
    for vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


def u32va(va):
    o = va2off(va)
    return None if o is None else struct.unpack_from("<I", d, o)[0]


CT = va2off(0x186D41F80)
NCTYPE = 354184

var = collections.Counter()
mvar = collections.Counter()
byty = collections.Counter()
nread = 0
for idx in range(NCTYPE):
    p = struct.unpack_from("<Q", d, CT + idx * 8)[0]
    po = va2off(p)
    if po is None or po + 11 > len(d):
        continue
    nread += 1
    ty = d[po + 10]
    byty[ty] += 1
    if ty in (0x13, 0x1E):
        data = struct.unpack_from("<Q", d, po)[0]
        (var if ty == 0x13 else mvar)[data] += 1

print("Il2CType 条目可读 = %d / %d" % (nread, NCTYPE))
print()
print("== type 码分布 top12 ==")
for k, v in byty.most_common(12):
    print("  ty=%02X  %8d" % (k, v))
print()
for name, c in (("VAR(0x13)", var), ("MVAR(0x1E)", mvar)):
    if not c:
        print("%s: 无" % name)
        continue
    ks = sorted(c)
    print("%s: 条目 %d  去重 %d  最小 %d  最大 %d  连续=%s"
          % (name, sum(c.values()), len(ks), ks[0], ks[-1], ks == list(range(ks[0], ks[-1] + 1))))
    print("   前 20 个索引: %s" % ks[:20])
    print("   引用次数 top8: %s" % c.most_common(8))
print()
# 合并视图（若二者共用同一索引空间则会重叠）
allk = sorted(set(var) | set(mvar))
print("合并去重 %d, 最小 %d, 最大 %d" % (len(allk), allk[0], allk[-1]))
