#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hexdump_at.py — 在若干 RVA 处反汇编 64 字节，并标出 .pdata 起点位置"""
import sys, struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

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
BEG = set()
for k in range(prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + k * 12)
    if b:
        BEG.add(b)

def rva2raw(rva):
    for nm, va, vs, rs, rp in SECS:
        if va <= rva < va + max(vs, rs):
            return rp + (rva - va)
    return rva - 0x1400  # il2cpp 区：节头被篡改，但与 .text 在 raw 上连续

md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = False

for a in sys.argv[1:]:
    rva = int(a, 16)
    raw = rva2raw(rva)
    print("=" * 78)
    print("RVA %X   VA %X   raw 0x%X   .pdata起点? %s" % (rva, 0x180000000 + rva, raw, rva in BEG))
    buf = d[raw:raw + 64]
    print("bytes: " + buf.hex(" "))
    n = 0
    for ins in md.disasm(buf, 0x180000000 + rva):
        mark = ""
        if ins.address - 0x180000000 in BEG:
            mark = "   <== .pdata 起点"
        print("  %X  %-24s %s %s%s" % (ins.address, ins.bytes.hex(" "), ins.mnemonic, ins.op_str, mark))
        n += 1
        if n >= 14:
            break
