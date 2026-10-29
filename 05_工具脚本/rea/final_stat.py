#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""收束统计：对齐性、命中/空/异常三类计数、以及「异常值到最近 .pdata 起点」的分布。"""
import bisect
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
SEC = {nm: (va, vs, rs, rp) for nm, va, vs, rs, rp in SECS}

pva, pvs, prs, prp = SEC[".pdata"]
BEGL = []
RANGES = []
for k in range(0, prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + k * 12)
    if b:
        BEGL.append(b)
        RANGES.append((b, en))
BEGL.sort()
RANGES.sort()
RB = [r[0] for r in RANGES]
BEG = set(BEGL)
n16 = sum(1 for b in BEGL if b % 16 == 0)
print(".pdata 起点 %d 个，其中 16 字节对齐 %d（%.1f%%）" % (len(BEGL), n16, 100.0 * n16 / len(BEGL)))


def in_body(rva):
    j = bisect.bisect_right(RB, rva) - 1
    return j >= 0 and RANGES[j][0] <= rva < RANGES[j][1]


n_all = n_null = n_hit = n_body = n_hole = 0
a16 = 0
delta = collections.Counter()
prevbeg = collections.Counter()
modbad = 0
for ln in open(r"D:\Carol-start\_rea\bh3_method_addr.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4 or p[0] == "idx":
        continue
    n_all += 1
    if not p[3]:
        n_null += 1
        continue
    rva = int(p[3], 16)
    if rva % 16 == 0:
        a16 += 1
    if rva in BEG:
        n_hit += 1
    elif in_body(rva):
        n_body += 1
    else:
        n_hole += 1
        j = bisect.bisect_left(BEGL, rva)
        if j < len(BEGL):
            delta[BEGL[j] - rva] += 1
        if j > 0:
            prevbeg[rva - BEGL[j - 1]] += 1

live = n_all - n_null
print("方法总数 %d / 空指针 %d / 有地址 %d" % (n_all, n_null, live))
print("有地址中 16 字节对齐 %d（%.2f%%）" % (a16, 100.0 * a16 / live))
print("精确落在 .pdata 起点 %d（%.2f%% of live）" % (n_hit, 100.0 * n_hit / live))
print("落在 .pdata 函数体内  %d（%.2f%%）" % (n_body, 100.0 * n_body / live))
print("落在 .pdata 空档      %d（%.2f%%）" % (n_hole, 100.0 * n_hole / live))
print("空档值「到下一个起点」距离 top12: %s" % delta.most_common(12))
print("空档值「到上一个起点」距离 top12: %s" % prevbeg.most_common(12))
