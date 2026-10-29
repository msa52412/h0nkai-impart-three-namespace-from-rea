#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定位 parent Il2CTYPE 条目段

已知 System.String 的 parentIdx = 1，应解出 System.Object (idx 383)
System.Exception 的 parentIdx = 1（同指 Object）
GameObject 的 parentIdx = 6866 → UnityEngine.Object?

候选段（相对 buf+0x118）：
  表7  E60 ^ 0x371B8070 = 0x242D2E8   (0x10 步长)
  表8  E70 ^ 0x0561C6FD = 0x1C6556C   (0x2C 步长)
  E40  - 0x77870E75    = 0x1C1F458   (0x10 泛型实例)
  E00  ^ 0x7497C9EE    = 0x0055C604   (0x10 泛型TypeDef记录)
  E24  ^ 0x3A73133E    = 0x0242AC00
  E28  ^ 0x3CB812E1    = 0x01C6766C
  E30  ^ 0x7EA603B1    = 0x00AC0F38
  E84  - 0x2F59FE76    = 0x01F5D8C0

salt 公式（来自 FUN_18042fe20 泛型实例）：
  s(i) = (u32)(( ((( ((u64)i*0x6ae9) ^ 0x2e6f3e3d) * 0x2ad3dd28 >> 0x16) * 0x4c39b37d >> 10)
               ^ 0x4dfaa6b0) * 0x22449c6e )
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
NT = 57487

with open(DLL, "rb") as f:
    dll = f.read()
e = struct.unpack_from("<I", dll, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", dll, coff + 2)[0]
optsz = struct.unpack_from("<H", dll, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", dll, opt + 24)[0]
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    vs, va, rs, rp = struct.unpack_from("<IIII", dll, o + 8)
    SECS.append((va, vs, rs, rp))


def u32va(va):
    rva = va - IB
    for vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else struct.unpack_from("<I", dll, rptr + (rva - vaddr))[0]
    return None


BUF = open(META, "rb").read()
FS = len(BUF)

SEGS = {
    "表7 E60": ((u32va(0x188198E60) ^ 0x371B8070) & M32, 0x10),
    "表8 E70": ((u32va(0x188198E70) ^ 0x0561C6FD) & M32, 0x2C),
    "E40 泛型inst": ((u32va(0x188198E40) - 0x77870E75) & M32, 0x10),
    "E00 泛型rec": ((u32va(0x188198E00) ^ 0x7497C9EE) & M32, 0x10),
    "E24": ((u32va(0x188198E24) ^ 0x3A73133E) & M32, 8),
    "E28": ((u32va(0x188198E28) ^ 0x3CB812E1) & M32, 8),
    "E30": ((u32va(0x188198E30) ^ 0x7EA603B1) & M32, 8),
    "E84": ((u32va(0x188198E84) - 0x2F59FE76) & M32, 8),
}
for k, (o, s) in SEGS.items():
    print("%-14s  offset=0x%08X  abs=0x%X  步长 0x%X" % (k, o, BASE + o, s))


def gsalt(i):
    x = ((i * 0x6AE9) & M64) ^ 0x2E6F3E3D
    x = (x * 0x2AD3DD28) & M64
    x >>= 0x16
    x = (x * 0x4C39B37D) & M64
    x >>= 10
    x = (x ^ 0x4DFAA6B0) & M32
    return (x * 0x22449C6E) & M32


print("\n[String] parentIdx=1 应解出 System.Object=383")
print("[Exception] parentIdx=1 应解出 System.Object=383")
print("[GameObject] parentIdx=6866 应解出 UnityEngine.Object")

for name, (off, step) in SEGS.items():
    ab = BASE + off
    for idx, want in ((1, 383), (6866, None)):
        rec = ab + idx * step
        if rec + step > FS:
            continue
        raw = struct.unpack_from("<%dI" % (step // 4), BUF, rec)
        s = gsalt(idx)
        # 尝试 +4 字段：typedef = raw[1] - 0x1DF344F8 - salt 等变体
        for pos, C in ((1, 0x1DF344F8), (0, 0x1DF344F8)):
            for op, tag in ((lambda v: ((v - C) - s) & M32, "sub-salt"),
                             (lambda v: ((v - C) + s) & M32, "sub+salt"),
                             (lambda v: ((v ^ C) - s) & M32, "xor-salt")):
                val = op(raw[pos])
                if idx == 1 and val == 383:
                    print("  *** 命中! %s idx=1 pos=%d %s -> 383" % (name, pos, tag))
                if idx == 6866 and want is None:
                    pass
    # 校验字段检查：raw[3](+0xC) - 0x175A3FDF == salt ?
    for idx in (1, 6866):
        rec = ab + idx * step
        if rec + step > FS:
            continue
        raw = struct.unpack_from("<%dI" % (step // 4), BUF, rec)
        s = gsalt(idx)
        chk = ((raw[3] - 0x175A3FDF) & M32) if step >= 16 else None
        if chk is not None:
            ok = chk == s
            if ok:
                print("  *** %s idx=%d 校验通过 (+0xC - 0x175A3FDF == salt)" % (name, idx))
                print("      raw=%s" % " ".join("%08X" % v for v in raw))
                td = ((raw[1] - 0x1DF344F8) - s) & M32
                print("      typedef(+4) = %d" % td)
