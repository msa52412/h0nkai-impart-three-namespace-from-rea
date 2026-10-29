#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
枚举 metadata 段全局 (0x188198E00..0x188198EB0)，
对每段试探已知常量族，判断是不是有效段偏移。
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
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
    nm = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((nm, va, vs, rs, rp))


def va2off(va):
    rva = va - IB
    for nm, vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


BUF = open(META, "rb").read()
FS = len(BUF)
print("metadata 大小 = %d (0x%X)" % (FS, FS))
print()

GA = 0x188198E00
KNOWN = {
    0x188198E08: ("TYPE", "X", 0x2B849DB3),
    0x188198E50: ("STRINGPOOL", "X", 0x7483FF7A),
    0x188198E84: ("FIELD", "S", 0x2F59FE76),
    0x188198E24: ("TBL_18", "X", 0x3A73133E),
    0x188198E98: ("TBL_08", "S", 0x56CA4FE4),
    0x188198E8C: ("TBL_PTR", "X", 0x227CD810),
    0x188198E04: ("ASM", "S", 0x1FE83754),
}
print("%-12s %-10s %-10s %s" % ("全局地址", "raw u32", "已知常量", "解出值"))
for k in range(0, 0xB0, 4):
    a = GA + k
    o = va2off(a)
    if o is None:
        continue
    raw = struct.unpack_from("<I", d, o)[0]
    tag = ""
    val = None
    if a in KNOWN:
        name, mode, c = KNOWN[a]
        val = (raw ^ c) if mode == "X" else (raw - c) & 0xFFFFFFFF
        tag = "%s %s 0x%08X" % (name, mode, c)
    print("0x%X  %08X   %-28s %s" % (a, raw, tag, ("0x%X (%d)" % (val, val)) if val is not None else ""))
