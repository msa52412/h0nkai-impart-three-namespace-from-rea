#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pick_probe.py — 为指定模块列出「去重后的地址 + 使用次数 + 命中/空档 + 与下一 .pdata 起点的距离」

用法: python pick_probe.py NetCommand.Partswitch.dll
"""
import sys, struct, bisect, collections

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
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

pva, pvs, prs, prp = SEC[".pdata"]
BEG = []
RANGES = []
for k in range(prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + k * 12)
    if b:
        BEG.append(b)
        RANGES.append((b, en))
BEG.sort()
RANGES.sort()
BSET = set(BEG)
RB = [r[0] for r in RANGES]
print(".pdata 起点 %d 个" % len(BEG))


def in_body(rva):
    j = bisect.bisect_right(RB, rva) - 1
    return j >= 0 and RANGES[j][0] <= rva < RANGES[j][1]


def next_start(x):
    i = bisect.bisect_right(BEG, x)
    return BEG[i] if i < len(BEG) else None


mod = sys.argv[1] if len(sys.argv) > 1 else "NetCommand.Partswitch.dll"
rows = []
with open(r"D:\Carol-start\_rea\bh3_method_addr.tsv", "r", encoding="utf-8") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 7 or p[2] != mod:
            continue
        if not p[3]:
            continue
        rows.append((int(p[1], 16), int(p[3], 16), p[4], p[5]))

cnt = collections.Counter(r[1] for r in rows)
print("模块 %s : %d 条, 去重 %d 个地址" % (mod, len(rows), len(cnt)))
print()
print("%-11s %-4s %-4s %-6s %-5s %s" % ("RVA", "次", "命中", "下一距", "内体", "代表方法"))
print("-" * 96)
for addr, c in sorted(cnt.items(), key=lambda kv: -kv[1]):
    nx = next_start(addr)
    gap = (nx - addr) if nx else None
    names = sorted({r[2] + "::" + r[3] for r in rows if r[1] == addr})
    tag = names[0] if len(names) == 1 else "%s 等%d个" % (names[0], len(names))
    print("%-11X %-4d %-4s %-6s %-5s %s" % (
        addr, c, "Y" if addr in BSET else "N",
        gap if gap is not None else "-",
        "Y" if in_body(addr) else "N", tag))

hitcnt = sum(c for a, c in cnt.items() if a in BSET)
print("\n按条数计命中率：%d/%d = %.1f%%" % (hitcnt, len(rows), 100.0 * hitcnt / len(rows)))
