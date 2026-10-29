#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查若干「抽样方法地址」在 .pdata 中的归属与近邻边界，判定它们是
   (1) 已登记函数的入口  (2) 无 unwind 的叶子函数  (3) 函数体内的中段地址
"""
import bisect
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


# .pdata
pva, pvs, prs, prp = SEC[".pdata"]
FUNCS = []
for k in range(0, prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + k * 12)
    if b:
        FUNCS.append((b, en, ui))
FUNCS.sort()
BEG = [f[0] for f in FUNCS]
END = [f[1] for f in FUNCS]


def find(rva):
    i = bisect.bisect_right(BEG, rva) - 1
    if i < 0:
        return None
    if BEG[i] <= rva < END[i]:
        return FUNCS[i]
    return None


def near(rva, k=6):
    i = bisect.bisect_left(BEG, rva)
    lo = max(0, i - k)
    return FUNCS[lo:i + k]


NAMES = {
    0x1D1FF70: "System.Object::.ctor / Finalize",
    0x58FBDF0: "System.String::.ctor",
    0x6031220: "System.Object::GetType",
    0x6031210: "System.Object::GetHashCode",
    0x67AF5D0: "System.Object::Equals(object)",
}

for rva in sorted(NAMES):
    raw = rva2raw(rva)
    f = find(rva)
    print("=" * 78)
    print("%-34s RVA %08X  raw %08X" % (NAMES[rva], rva, raw))
    if f:
        print("  in .pdata : True   func=[%08X,%08X) unwind=%08X  offset+%d  len=%d"
              % (f[0], f[1], f[2], rva - f[0], f[1] - f[0]))
    else:
        print("  in .pdata : False")
    # 前后最近边界
    print("  近邻 .pdata 边界:")
    for b, en, ui in near(rva, 3):
        mark = "  <== 命中" if b == rva else ""
        print("     [%08X,%08X) len=%-5d unwind=%08X%s" % (b, en, en - b, ui, mark))
    # ± 若干字节窗口
    for delta in (-0x10, -8, 0, 8, 0x10):
        r2 = rva + delta
        rr = rva2raw(r2)
        bs = d[rr:rr + 12]
        print("     %+04X  %08X  %s" % (delta, r2, " ".join("%02X" % c for c in bs)))

print()
print("=" * 78)
print("统计：944 个 .pdata 函数中，有多少个其 BeginAddress 之前 0x10 内存在「另一个函数尾部」")
print(".pdata 函数总数 %d，RVA 范围 %08X..%08X" % (len(FUNCS), FUNCS[0][0], FUNCS[-1][1]))
