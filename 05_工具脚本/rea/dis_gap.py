#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对抽样方法地址做「线性扫描」判定：
   目标地址是否落在指令边界上；其所在的 .pdata 空档段真正从哪里开始像函数序言。
"""
import bisect
import struct

from capstone import Cs, CS_ARCH_X86, CS_MODE_64

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
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
FUNCS = []
for k in range(0, prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + k * 12)
    if b:
        FUNCS.append((b, en, ui))
FUNCS.sort()
BEG = [f[0] for f in FUNCS]

md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = False


def gap_of(rva):
    i = bisect.bisect_right(BEG, rva) - 1
    lo = FUNCS[i][1] if i >= 0 else 0x1000
    hi = FUNCS[i + 1][0] if i + 1 < len(FUNCS) else 0x6C56000
    return lo, hi


SAMPLES = [
    (0x1D1FF70, "System.Object::.ctor / Finalize"),
    (0x58FBDF0, "System.String::.ctor"),
    (0x6031210, "System.Object::GetHashCode"),
    (0x6031220, "System.Object::GetType"),
    (0x67AF5D0, "System.Object::Equals(object)"),
]

for rva, name in SAMPLES:
    lo, hi = gap_of(rva)
    print("=" * 90)
    print("%-32s RVA %08X   空档段 [%08X,%08X)  %d 字节" % (name, rva, lo, hi, hi - lo))
    # 从空档段起点线性扫描
    raw = rva2raw(lo)
    blob = d[raw:raw + (hi - lo) + 16]
    boundary = False
    lines = []
    for ins in md.disasm(blob, lo):
        mark = ""
        if ins.address == rva:
            boundary = True
            mark = "   <<<<< 目标"
        lines.append("    %08X  %-24s %s %s%s" % (
            ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str, mark))
        if ins.address > rva:
            break
    for ln in lines[-14:]:
        print(ln)
    print("  → 目标是否落在指令边界: %s" % boundary)
    # 扫序言
    print("  空档段内「像序言」的位置：")
    for off in range(0, hi - lo):
        b0 = d[raw + off]
        b1 = d[raw + off + 1] if off + 1 < len(blob) else 0
        pat = None
        if b0 == 0x48 and b1 == 0x83:            # sub rsp,imm8 (REX.W 83 /5)
            pat = "48 83 /5"
        elif b0 == 0x48 and b1 == 0x81:
            pat = "48 81 /5"
        elif b0 == 0x48 and b1 == 0x8B and off + 2 < len(blob) and d[raw + off + 2] == 0xC4:
            pat = "mov rax,rsp"
        elif b0 == 0x40 and b1 in (0x53, 0x55, 0x56, 0x57, 0x41):
            pat = "push (REX)"
        elif b0 in (0x53, 0x55, 0x56, 0x57) and b1 == 0x8B:
            pat = "push/mov"
        if pat:
            print("     +%03X  %08X  %s  (%s)" % (off, lo + off, pat, "目标" if lo + off == rva else ""))
