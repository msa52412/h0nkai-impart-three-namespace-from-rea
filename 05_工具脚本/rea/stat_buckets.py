#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 1MB 分桶统计 .pdata 覆盖率 与 方法指针精确命中率，判断异常是否与「代码区段」相关。"""
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
BEG = set()
cov = {}
fn = {}
for k in range(0, prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + k * 12)
    if not b:
        continue
    BEG.add(b)
    for bk in range(b >> 20, (en >> 20) + 1):
        lo = max(b, bk << 20)
        hi = min(en, (bk + 1) << 20)
        cov[bk] = cov.get(bk, 0) + max(0, hi - lo)
    fn[b >> 20] = fn.get(b >> 20, 0) + 1

# 方法指针
hit = {}
tot = {}
modof = {}
for ln in open(r"D:\Carol-start\_rea\bh3_method_addr.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4 or not p[3]:
        continue
    try:
        rva = int(p[3], 16)
    except ValueError:
        continue
    bk = rva >> 20
    tot[bk] = tot.get(bk, 0) + 1
    if rva in BEG:
        hit[bk] = hit.get(bk, 0) + 1

print("%6s %10s %10s %9s %9s %9s %9s" % ("桶", ".pdata函数", "覆盖字节", "覆盖率", "指针数", "精确命中", "命中率"))
for bk in range(0, 0x6D):
    c = cov.get(bk, 0)
    n = fn.get(bk, 0)
    t = tot.get(bk, 0)
    h = hit.get(bk, 0)
    if not c and not t:
        continue
    print("%06X %10d %10d %8.1f%% %9d %9d %8.1f%%" % (
        bk << 20, n, c, 100.0 * c / 0x100000, t, h, 100.0 * h / t if t else 0.0))
