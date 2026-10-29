#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""看具体模块的数组内容形态：0% 命中的模块和 100% 命中的模块，值长什么样。
"""
import bisect
import collections
import struct
import sys

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
for k in range(0, prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + k * 12)
    if b:
        BEG.add(b)
BL = sorted(BEG)

mods = {}
for ln in open(r"D:\Carol-start\_rea\bh3_modules_v2.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4 or not p[3].isdigit():
        continue
    mods[p[1]] = (int(p[2], 16), int(p[3]))

TARGETS = sys.argv[1:] or [
    "UnityEngine.ImageConversionModule.dll",
    "NetCommand.Partthree.dll",
    "ProtobufSerializer.Partninja.dll",
    "UnityEngine.CoreModule.dll",
]

for name in TARGETS:
    if name not in mods:
        print("!! 未知模块", name)
        continue
    arr, cnt = mods[name]
    raw = rva2raw(arr)
    vals = list(struct.unpack_from("<%dQ" % cnt, d, raw))
    print("=" * 92)
    print("%s  count=%d  arrayRVA=%08X" % (name, cnt, arr))
    for i, v in enumerate(vals[:12]):
        rva = v - IB if v else 0
        tag = "NULL" if v == 0 else ("BEG" if rva in BEG else ("code" if 0x1000 <= rva < 0x6C56000 else "OTHER"))
        nb = ""
        if tag == "code":
            j = bisect.bisect_left(BL, rva)
            nb = "nextBEG=+%d prevBEG=-%d" % (BL[j] - rva, rva - BL[j - 1])
        print("   [%3d] %016X  rva=%08X  %-5s %s" % (i, v, rva, tag, nb))
    # 全模块统计
    hit = sum(1 for v in vals if v and (v - IB) in BEG)
    nul = sum(1 for v in vals if v == 0)
    other = sum(1 for v in vals if v and not (0x1000 <= v - IB < 0x6C56000))
    deltas = collections.Counter()
    for v in vals:
        if v and (v - IB) not in BEG and 0x1000 <= v - IB < 0x6C56000:
            rva = v - IB
            j = bisect.bisect_left(BL, rva)
            deltas[BL[j] - rva] += 1
    print("   统计: 命中 %d / 空 %d / 非代码 %d / 共 %d" % (hit, nul, other, cnt))
    print("   到「下一个 .pdata 起点」的距离 top10: %s" % deltas.most_common(10))
