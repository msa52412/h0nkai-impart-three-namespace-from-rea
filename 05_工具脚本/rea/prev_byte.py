#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对照检验：命中 .pdata 起点的方法地址 vs 落在空档的方法地址，
   看「前一个字节」的分布是否都是填充符 —— 判断后者是否也是函数起点。"""
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
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((d[o:o + 8].rstrip(b"\0").decode("latin1"), va, vs, rs, rp))
SEC = {nm: (va, vs, rs, rp) for nm, va, vs, rs, rp in SECS}

pva, pvs, prs, prp = SEC[".pdata"]
BEG = set()
for k in range(0, prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + k * 12)
    if b:
        BEG.add(b)

hit_prev = collections.Counter()
hole_prev = collections.Counter()
hole_first = collections.Counter()
hit_first = collections.Counter()

for ln in open(r"D:\Carol-start\_rea\bh3_method_addr.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4 or p[0] == "idx" or not p[3]:
        continue
    rva = int(p[3], 16)
    if rva < 0x1001 or rva - 0xC00 >= len(d):
        continue
    pb = d[rva - 0xC00 - 1]
    fb = d[rva - 0xC00]
    if rva in BEG:
        hit_prev[pb] += 1
        hit_first[fb] += 1
    else:
        hole_prev[pb] += 1
        hole_first[fb] += 1


def show(name, c, total):
    print("  %s（样本 %d）" % (name, total))
    for b, n in c.most_common(6):
        print("     %02X : %7d  %5.1f%%" % (b, n, 100.0 * n / total))


th = sum(hit_prev.values())
tl = sum(hole_prev.values())
print("前一个字节分布：")
show("命中 .pdata 起点", hit_prev, th)
show("空档", hole_prev, tl)
print()
print("首字节分布：")
show("命中 .pdata 起点", hit_first, th)
show("空档", hole_first, tl)
pad = sum(n for b, n in hole_prev.items() if b in (0xCC, 0x00, 0x90))
print()
print("空档地址前一字节为填充（CC/00/90）的比例：%.1f%%" % (100.0 * pad / tl))
pad_h = sum(n for b, n in hit_prev.items() if b in (0xCC, 0x00, 0x90))
print("命中地址前一字节为填充的比例：%.1f%%" % (100.0 * pad_h / th))
