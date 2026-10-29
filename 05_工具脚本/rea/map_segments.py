#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解码全部 metadata 段全局，按偏移排序输出段布局"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
FS = 0x35D387C

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


def raw(addr):
    return struct.unpack_from("<I", d, va2off(addr))[0]


XOR = {
    0x188198E00: 0x7497C9EE, 0x188198E08: 0x2B849DB3, 0x188198E14: 0x5F613838,
    0x188198E1C: 0x72267500, 0x188198E20: 0x20910E12, 0x188198E24: 0x3A73133E,
    0x188198E28: 0x3CB812E1, 0x188198E30: 0x7EA603B1, 0x188198E38: 0x58BB89EB,
    0x188198E4C: 0x6F3F9184, 0x188198E50: 0x7483FF7A, 0x188198E60: 0x371B8070,
    0x188198E70: 0x0561C6FD, 0x188198E8C: 0x227CD810, 0x188198E88: None,
}
SUB = {
    0x188198E04: 0x1FE83754, 0x188198E34: 0x75CBFDCC, 0x188198E40: 0x77870E75,
    0x188198E48: 0x180A3D3B, 0x188198E58: 0x17A3B99, 0x188198E68: 0x1408DBF1,
    0x188198E6C: 0x3670DF73, 0x188198E78: 0x0A4FFD99, 0x188198E80: 0x1E7E75AD,
    0x188198E84: 0x2F59FE76, 0x188198E94: 0x72626879, 0x188198E98: 0x56CA4FE4,
}
NAME = {
    0x188198E04: "程序集描述符", 0x188198E08: "类型表", 0x188198E1C: "表5 描述符",
    0x188198E24: "事件表", 0x188198E50: "字符串池", 0x188198E58: "表9 方法定义",
    0x188198E60: "表7", 0x188198E70: "表8", 0x188198E84: "字段表",
    0x188198E8C: "TBL_PTR", 0x188198E94: "?", 0x188198E98: "TBL_08",
}

rows = []
for a, c in XOR.items():
    if c is None:
        continue
    r = raw(a)
    rows.append((a, r, "XOR", c, (r ^ c) & 0xFFFFFFFF))
for a, c in SUB.items():
    r = raw(a)
    rows.append((a, r, "SUB", c, (r - c) & 0xFFFFFFFF))

rows.sort(key=lambda x: x[4])
print("%-12s %-10s %-4s %-8s %-10s %s" % ("全局", "raw", "op", "值", "值(hex)", "段名"))
prev = None
for a, r, op, c, v in rows:
    tag = NAME.get(a, "")
    gap = "" if prev is None else "  Δ=0x%X" % (v - prev)
    print("0x%X  %08X   %-4s %08X 0x%-8X %s%s" % (a, r, op, v, v, tag, gap))
    prev = v

print()
print("=== 按偏移排序的段布局（相对 buf+0x118） ===")
for a, r, op, c, v in rows:
    print("  0x%08X  %s" % (v, NAME.get(a, "?")))
print()
print("metadata 文件大小 0x%X；相对偏移空间 0x%X" % (FS, FS - 0x118))
