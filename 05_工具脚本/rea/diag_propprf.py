#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""反推属性表 prfP 的正确变体（用名字解密命中率择优）"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
TP = 0x1C6766C

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
POOL = (struct.unpack_from("<I", d, va2off(0x188198E50))[0] ^ 0x7483FF7A) & M32
P = BASE + POOL
KM = (-0x394A88E12FFFF3A0) & M64
KA = 0x53DB1FC7E9ECC644
KS = 0x64C7CE0352814CF6
_u64 = struct.Struct("<Q")


def dec(pid):
    L = (pid >> 24) & 0xFF
    if L == 0:
        return None
    ix = pid & 0xFFFFFF
    src = P + ix
    nb = (L + 7) >> 3
    if src + nb * 8 > len(BUF):
        return None
    key = (ix * KM + KA) & M64
    out = bytearray()
    for b in range(nb):
        out += (_u64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + KS) & M64
    try:
        t = out[:L].decode("utf-8")
    except UnicodeDecodeError:
        return None
    for ch in t:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            return None
    return t


def variants(i):
    x = ((i * 0x64D5) & M64) ^ 0x6D7B1F20
    x = (x + 0x10ECA71E) & M64
    y = (x * 0x7737C996) & M64
    out = {}
    # A: 64 位 >>8 后取低 32
    out["A_shift64"] = (((y >> 8) & M32) + 0x5505FF6B) & M32
    # B: 先截断 32 位再算术右移 8
    t32 = y & M32
    s32 = t32 - (1 << 32) if t32 & 0x80000000 else t32
    out["B_sar32"] = ((s32 >> 8) + 0x5505FF6B) & M32
    # C: 先截断再逻辑右移 8
    out["C_shr32"] = ((t32 >> 8) + 0x5505FF6B) & M32
    # D: 不加尾常量
    out["D_nofinal"] = (y >> 8) & M32
    # E: 32 位乘法
    out["E_mul32"] = ((((x & M32) * 0x7737C996) & M32) >> 8) + 0x5505FF6B & M32
    return out


# 取前 300 条记录测命中率
recs = []
for i in range(300):
    o = BASE + TP + i * 0x14
    p0, p1, p2, p3, p4 = struct.unpack_from("<5I", BUF, o)
    recs.append((i, p0))

for C in (0x5566C15D,):
    print("C = 0x%08X" % C)
    for tag in ("A_shift64", "B_sar32", "C_shr32", "D_nofinal", "E_mul32"):
        hit = 0
        samples = []
        for i, p0 in recs:
            m = (variants(i)[tag] * 0xEACB0367) & M32
            v = dec(((p0 ^ C) + m) & M32)
            if v:
                hit += 1
                if len(samples) < 5:
                    samples.append(v)
        print("  %-12s 命中 %3d/300   %s" % (tag, hit, ", ".join(samples)))
