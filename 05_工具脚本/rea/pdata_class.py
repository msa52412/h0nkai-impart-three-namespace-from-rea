#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pdata_class.py — 判定 .pdata 每条目的类型：
   - 是否 16 字节对齐
   - UnwindInfo 首字节的 Flags 是否含 UNW_FLAG_CHAININFO(0x4) / EHANDLER(0x1) / UHANDLER(0x2)
   - 是否"真函数起点"（前一字节为填充/ret，且本条对齐）
"""
import struct, collections

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


def rva2raw(rva):
    for nm, va, vs, rs, rp in SECS:
        if va <= rva < va + max(vs, rs):
            return rp + (rva - va)
    if 0x52E000 <= rva < 0x6C56000:
        return rva - 0xC00
    return None


pva, pvs, prs, prp = SEC[".pdata"]
N = prs // 12
print(".pdata 条目数 %d" % N)

stats = collections.Counter()
flag_cnt = collections.Counter()
aligned = []
unaligned = []
for k in range(N):
    b, en, ui = struct.unpack_from("<III", d, prp + 12 * k)
    if not b:
        stats["begin=0"] += 1
        continue
    ur = rva2raw(ui)
    fl = None
    if ur is not None:
        b0 = d[ur]
        ver = b0 & 0x7
        flags = (b0 >> 3) & 0x1F
        fl = flags
        flag_cnt[flags] += 1
    if fl is not None and (fl & 0x4):
        stats["CHAININFO"] += 1
    if b % 16 == 0:
        stats["16对齐"] += 1
        aligned.append((b, en, ui, fl))
    else:
        stats["非16对齐"] += 1
        unaligned.append((b, en, ui, fl))

print()
for k, v in sorted(stats.items()):
    print("  %-14s %d" % (k, v))
print()
print("UnwindInfo flags 分布（0=无, 1=EHANDLER, 2=UHANDLER, 4=CHAININFO, 5=EH+CHAIN, 6=UH+CHAIN）：")
for k, v in sorted(flag_cnt.items()):
    print("   flags=%-2d  %8d" % (k, v))

print()
print("=== 交叉表：对齐 × 是否 CHAININFO ===")
cross = collections.Counter()
for b, en, ui, fl in aligned:
    cross[("16对齐", "CHAIN" if (fl or 0) & 4 else "正常")] += 1
for b, en, ui, fl in unaligned:
    cross[("非16对齐", "CHAIN" if (fl or 0) & 4 else "正常")] += 1
for k, v in sorted(cross.items()):
    print("  %-10s %-6s %8d" % (k[0], k[1], v))
