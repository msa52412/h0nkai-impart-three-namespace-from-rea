#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
暴力法定位全部 RIP 相对引用：对 .text 每个字节位置 p 读 s32 disp，
计算 target = VA(p+4) + disp，若命中目标全局则记录。
（随机误命中概率 ~1e-3，可视为精确）

输出：每个全局 -> 引用点 VA、所在函数起始 RVA。
"""
import struct
import bisect

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
TARGETS = {
    0x188198E04: "asmDesc",
    0x188198E08: "typeTable",
    0x188198E14: "?C77140",
    0x188198E1C: "tbl5",
    0x188198E20: "sizeC00",
    0x188198E24: "events",
    0x188198E28: "props",
    0x188198E30: "genParam(0xAC0F38)",
    0x188198E34: "tbl5tail",
    0x188198E38: "?203098",
    0x188198E40: "?1C1F458",
    0x188198E48: "?7C4E48",
    0x188198E4C: "size1E00",
    0x188198E50: "strPool",
    0x188198E58: "methods",
    0x188198E60: "tbl7",
    0x188198E68: "?1C56D6C",
    0x188198E6C: "?1C57D10",
    0x188198E70: "tbl8",
    0x188198E78: "?50B364",
    0x188198E80: "tbl7tail",
    0x188198E84: "fields",
    0x188198E8C: "TBL_PTR",
    0x188198E94: "?1C41E98",
    0x188198E98: "tbl08",
    0x1881A3628: "PTR_PTR(ctype)",
    0x1881A3618: "PTR(tokens)",
}

data = open(DLL, "rb").read()
e = struct.unpack_from("<I", data, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", data, coff + 2)[0]
optsz = struct.unpack_from("<H", data, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", data, opt + 24)[0]
secs = {}
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    name = data[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", data, o + 8)
    secs[name] = (va, vs, rs, rp)

t_va, t_vs, t_rs, t_rp = secs[".text"]
TEXT = data[t_rp:t_rp + t_rs]
TEXT_VA = IB + t_va

p_va, p_vs, p_rs, p_rp = secs[".pdata"]
nfunc = p_rs // 12
begins = []
for i in range(nfunc):
    b, en = struct.unpack_from("<II", data, p_rp + i * 12)
    begins.append(b)
sb = sorted(begins)


def func_of(rva):
    k = bisect.bisect_right(sb, rva) - 1
    if k < 0:
        return None
    return sb[k] if rva - sb[k] < 0x8000 else None


hits = {}
n = len(TEXT)
offs = range(0, n - 4)
for p in offs:
    disp = struct.unpack_from("<i", TEXT, p)[0]
    tgt = TEXT_VA + p + 4 + disp
    if tgt in TARGETS:
        hits.setdefault(tgt, []).append(TEXT_VA + p)

print("总计命中 %d 个全局" % len(hits))
for tgt, nm in sorted(TARGETS.items()):
    lst = hits.get(tgt, [])
    fs = sorted({func_of(v - IB) for v in lst})
    print("\n%-22s 0x%X  %3d 处 / %d 个函数" % (nm, tgt, len(lst), len(fs)))
    print("   函数: " + ", ".join("FUN_%X" % (IB + f) for f in fs[:14]))
