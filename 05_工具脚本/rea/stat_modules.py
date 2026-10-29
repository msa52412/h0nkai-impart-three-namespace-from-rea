#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按模块统计「方法指针命中 .pdata 函数起点」的比例。
   目的：判定 17.68% 的异常是「个别模块取错数组」还是「全局现象」。
"""
import bisect
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
    if rva < 0x6C56000:
        return rva - 0xC00
    for nm, va, vs, rs, rp in SECS:
        if nm in (".reloc", ".text", ".pdata"):
            continue
        if va <= rva < va + max(vs, rs) and rs:
            return rp + (rva - va)
    return None


pva, pvs, prs, prp = SEC[".pdata"]
BEG = set()
RANGES = []
for k in range(0, prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + k * 12)
    if b:
        BEG.add(b)
        RANGES.append((b, en))
RANGES.sort()
RB = [r[0] for r in RANGES]
print(".pdata 函数 %d" % len(BEG))


def in_func(rva):
    j = bisect.bisect_right(RB, rva) - 1
    return j >= 0 and RANGES[j][0] <= rva < RANGES[j][1]


mods = []
for ln in open(r"D:\Carol-start\_rea\bh3_modules_v2.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4 or not p[3].isdigit():
        continue
    mods.append((p[1], int(p[2], 16), int(p[3])))
print("模块 %d" % len(mods))

print()
print("%-42s %8s %8s %8s %8s %7s" % ("module", "count", "exact", "hit%", "body%", "null%"))
tot = totx = totb = 0
bad = []
rows = []
for name, arr, cnt in mods:
    raw = rva2raw(arr)
    exact = infunc = null = 0
    for i in range(cnt):
        v = struct.unpack_from("<Q", d, raw + i * 8)[0]
        if v == 0:
            null += 1
            continue
        rva = v - IB
        if rva in BEG:
            exact += 1
        elif in_func(rva):
            infunc += 1
    live = cnt - null
    rows.append((name, cnt, live, exact, infunc, null))
    tot += cnt
    totx += exact
    totb += infunc
    if live and exact * 2 < live:
        bad.append((name, cnt, live, exact, null))

rows.sort(key=lambda r: (r[3] / max(1, r[2])))
for r in rows[:15] + [("...", 0, 0, 0, 0, 0)] + rows[-8:]:
    name, cnt, live, exact, infunc, null = r
    if name == "...":
        print("   ...")
        continue
    print("%-42s %8d %8d %7.1f%% %7.1f%% %6.1f%%" % (
        name, cnt, exact, 100.0 * exact / max(1, live), 100.0 * infunc / max(1, live),
        100.0 * null / cnt))
print()
print("合计 %d，精确命中 %d（%.2f%%），落在函数体内 %d" % (tot, totx, 100.0 * totx / tot, totb))
print("命中率 < 50%% 的模块：%d 个" % len(bad))
for b in bad[:20]:
    print("    %-40s cnt=%-7d live=%-7d exact=%-7d null=%d" % b)
