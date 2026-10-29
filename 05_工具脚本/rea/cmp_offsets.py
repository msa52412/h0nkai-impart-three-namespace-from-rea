#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对比候选「方法指针数组」偏移：A-0x38 vs A（记录名槽之后紧邻）。
   用每模块 .pdata 精确命中率做判据。
"""
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


def rva2raw(rva):
    if 0 <= rva < 0x6C56000:
        return rva - 0xC00
    for nm, va, vs, rs, rp in SECS:
        if nm in (".reloc", ".text", ".pdata"):
            continue
        if va <= rva < va + max(vs, rs) and rs:
            return rp + (rva - va)
    return None


pva, pvs, prs, prp = SEC[".pdata"]
BEG = set()
for k in range(0, prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + k * 12)
    if b:
        BEG.add(b)


def q(rva):
    r = rva2raw(rva)
    return None if r is None else struct.unpack_from("<Q", d, r)[0]


def w32(rva):
    r = rva2raw(rva)
    return None if r is None else struct.unpack_from("<I", d, r)[0]


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


recs = {}
for nm, va, vs, rs, rp in SECS:
    if nm not in (".data", ".rdata") or rs == 0:
        continue
    end = rp + min(rs, vs if vs else rs)
    for r in range(rp, min(end, len(d)) - 8, 8):
        v = struct.unpack_from("<Q", d, r)[0]
        if not (IB <= v < IB + 0x12000000):
            continue
        s = cstr(v)
        if not s or not s.lower().endswith(".dll"):
            continue
        A = va + (r - rp) + 0x18
        ts = w32(A - 8)
        if not ts or not (0x5A000000 <= ts <= 0x6A000000):
            continue
        recs.setdefault(A, {"A": A, "name": s})
print("记录 %d 个" % len(recs))

cnts = {}
for ln in open(r"D:\Carol-start\_rea\bh3_modules_v2.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) > 3 and p[3].isdigit():
        cnts[p[1]] = int(p[3])
print("已知条数 %d 个" % len(cnts))


def hitrate(arr, cnt):
    raw = rva2raw(arr)
    if raw is None or cnt <= 0:
        return -1, 0
    exact = live = 0
    for i in range(cnt):
        v = struct.unpack_from("<Q", d, raw + i * 8)[0]
        if not v:
            continue
        live += 1
        if (v - IB) in BEG:
            exact += 1
    return (100.0 * exact / live if live else -1), live


print()
print("%-42s %7s %10s %10s %10s %10s" % ("module", "cnt", "A-0x38", "hit%", "A", "hit%"))
tot38 = totA = totn = 0
better = 0
for A, r in sorted(recs.items(), key=lambda kv: -cnts.get(kv[1]["name"], 0))[:30]:
    c = cnts.get(r["name"], 0)
    a38 = q(A - 0x38)
    if not c or not a38:
        continue
    h38, _ = hitrate(a38 - IB, c)
    hA, _ = hitrate(A, c)
    tot38 += h38
    totA += hA
    totn += 1
    if hA > h38 + 1:
        better += 1
    print("%-42s %7d %10s %9.1f%% %10s %9.1f%%" % (
        r["name"][:42], c, "%08X" % (a38 - IB), h38, "%08X" % A, hA))
print()
print("前 30 大模块平均命中率：A-0x38 = %.1f%%   A = %.1f%%   A 更优的模块数 %d/%d"
      % (tot38 / totn, totA / totn, better, totn))
