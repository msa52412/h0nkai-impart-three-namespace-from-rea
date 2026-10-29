#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重定位游程 × 值分类：找出「方法指针数组」候选。

对每个等距 8 字节的 DIR64 游程，统计槽位里
  代码指针（0x180001000..0x186C56000） / 零 / 其它
的条数。方法指针数组应是「代码指针占多数或多数字为 NULL」。

已知对齐关系：
  raw = RVA - 0x1800   (.rdata/.data 区)
  raw = RVA - 0xC00    (.text 区, RVA < 0x6C56000)
"""
import struct

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
IB = 0x180000000
LO = 0x180001000
HI = 0x186C56000

d = open(PATH, "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
opt = coff + 20
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    nm = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((nm, va, vs, rs, rp))


def rva2raw(rva):
    for nm, va, vs, rs, rp in SECS:
        if va <= rva < va + max(vs, rs):
            return None if rs == 0 else rp + (rva - va)
    return None


allrel = []
for nm, va, vs, rs, rp in SECS:
    if nm != ".reloc":
        continue
    p, end = rp, rp + rs
    while p + 8 <= end:
        page, blk = struct.unpack_from("<II", d, p)
        if blk < 8 or p + blk > end:
            break
        for k in range((blk - 8) // 2):
            w = struct.unpack_from("<H", d, p + 8 + k * 2)[0]
            if (w >> 12) == 10:
                allrel.append(page + (w & 0xFFF))
        p += blk

dir64 = sorted(set(allrel))
runs = []
st = 0
for i in range(1, len(dir64) + 1):
    if i == len(dir64) or dir64[i] - dir64[i - 1] != 8:
        if i - st >= 64:
            runs.append((dir64[st], i - st))
        st = i

print("游程(>=64) %d 个，合计槽位 %d" % (len(runs), sum(r[1] for r in runs)))
print()
print("%-12s %-9s %-9s %-9s %-9s %s" % ("RVA", "条数", "代码指针", "零", "其它", "判定"))
cand = []
for rva, ln in sorted(runs, key=lambda x: -x[1]):
    raw = rva2raw(rva)
    if raw is None or raw + ln * 8 > len(d):
        print("%08X   %-9d  <无法映射>" % (rva, ln))
        continue
    nc = nz = no = 0
    for k in range(ln):
        v = struct.unpack_from("<Q", d, raw + k * 8)[0]
        if LO <= v < HI:
            nc += 1
        elif v == 0:
            nz += 1
        else:
            no += 1
    tag = ""
    if nc > ln * 0.5:
        tag = "**代码指针数组**"
        cand.append((rva, ln, nc, nz, no))
    elif no > ln * 0.5 and nc == 0:
        tag = "数据指针数组"
    print("%08X   %-9d %-9d %-9d %-9d %s" % (rva, ln, nc, nz, no, tag))

print()
print("== 代码指针数组候选 %d 个 ==" % len(cand))
print("合计条数 %d   （目标：方法 %d）" % (sum(c[1] for c in cand), 408458))
for rva, ln, nc, nz, no in cand[:40]:
    print("   RVA %08X  %d 条（代码 %d / 零 %d / 其它 %d）" % (rva, ln, nc, nz, no))
