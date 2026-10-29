#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫 .text 内所有 RIP 相对指令，找引用指定全局 VA 的位置"""
import struct
import sys

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
d = open(DLL, "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", d, opt + 24)[0]
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    name = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((name, va, vs, rs, rp))

TXT = next(s for s in SECS if s[0] == ".text")
_, tva, tvs, trs, trp = TXT
TEXT = d[trp:trp + trs]
BASE = IB + tva

MODRM = {0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0x3D}


def scan(target):
    out = []
    n = len(TEXT)
    for i in range(n - 8):
        b0 = TEXT[i]
        if b0 == 0x48:
            op, moff = TEXT[i + 1], 2
        elif b0 in (0x8B, 0x8D, 0x89, 0xC7, 0x3B, 0x39):
            op, moff = b0, 0
        else:
            continue
        if moff >= n - i:
            continue
        if TEXT[i + moff] not in MODRM:
            continue
        # disp32 紧跟 ModRM
        disp = struct.unpack_from("<i", TEXT, i + moff + 1)[0]
        # 指令长度 = moff + 1(ModRM) + 4(disp)  （若带 imm 则后面还有）
        for ilen in (moff + 5,):
            va = BASE + i + ilen + disp
            if va == target:
                out.append((BASE + i, op))
    return out


for tgt in (0x1899DBBF8, 0x1899DBBE8, 0x1899DBBF0):
    hits = scan(tgt)
    print("目标 0x%X: %d 处引用" % (tgt, len(hits)))
    for a, op in hits[:12]:
        print("   0x%X  op=0x%02X" % (a, op))
