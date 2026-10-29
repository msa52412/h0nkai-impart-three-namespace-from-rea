#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pdata_truth.py — 从 .pdata 提取"真函数起点"地面真值（16 字节对齐 且 非 CHAININFO）

输出 bh3_pdata_truth.tsv: VA(hex) <TAB> EndRVA(hex) <TAB> flags
用于与 Ghidra 建出的函数集合做集合比对。
"""
import struct
import collections

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
OUT = r"D:\Carol-start\_rea\bh3_pdata_truth.tsv"

d = open(DLL, "rb").read()
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
    for nm, va, vs, rs, rp in SECS:
        if va <= rva < va + max(vs, rs):
            return rp + (rva - va)
    if 0x52E000 <= rva < 0x6C56000:
        return rva - 0x1400          # 已校准值（见 §9F.10）
    return None


pva, pvs, prs, prp = SEC[".pdata"]
N = prs // 12
print(".pdata 条目数 %d" % N)

truth = []
cnt = collections.Counter()
for k in range(N):
    b, en, ui = struct.unpack_from("<III", d, prp + 12 * k)
    if not b:
        cnt["begin=0"] += 1
        continue
    ur = rva2raw(ui)
    fl = None
    if ur is not None and ur < len(d):
        fl = (d[ur] >> 3) & 0x1F
    chain = bool((fl or 0) & 0x4)
    if b % 16 == 0 and not chain:
        truth.append((b, en, fl))
        cnt["真函数起点"] += 1
    elif chain:
        cnt["CHAININFO"] += 1
    else:
        cnt["非对齐非CHAIN"] += 1

print()
for k, v in cnt.items():
    print("  %-14s %d" % (k, v))

vas = set(0x180000000 + b for b, en, fl in truth)
print("真函数起点 VA 去重 %d" % len(vas))

with open(OUT, "w", encoding="utf-8") as f:
    for b, en, fl in truth:
        f.write("%x\t%x\t%s\n" % (0x180000000 + b, 0x180000000 + en, fl))
print("写出 %s" % OUT)
