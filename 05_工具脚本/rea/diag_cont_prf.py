#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""确定容器表（0x10/条）的 prf 变体。
反编译原文：
  iVar15 = ((uint)((((ulonglong)uVar14 * 0x6ae9 ^ 0x2e6f3e3d) * 0x2ad3dd28 >> 0x16) *
                   0x4c39b37d >> 10) ^ 0x4dfaa6b0) * 0x22449c6e;
  校验： *(int*)(cont + 0xC) - 0x175A3FDF == iVar15
此处穷举截断/移位顺序变体，统计命中率。
"""
import struct
import itertools

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF

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
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((va, vs, rs, rp))


def u32va(va):
    rva = va - IB
    for vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else struct.unpack_from("<I", d, rptr + (rva - vaddr))[0]


BUF = open(META, "rb").read()
B = 0x118
GP = B + ((u32va(0x188198E40) - 0x77870E75) & M32)
OWN = B + ((u32va(0x188198E00) ^ 0x7497C9EE) & M32)
NGP = 2772
print("GP  = 0x%08X   OWN = 0x%08X" % (GP - B, OWN - B))


def salt(i):
    return ((((i * 0x34D04BA0E4DB + 0xA13EE8C44CC682A) & M64) ^ 0x43427E7D) + 0x10776301) & M64


conts = []
for i in range(NGP):
    r0 = struct.unpack_from("<I", BUF, GP + i * 0x10)[0]
    c = ((salt(i) & M32) ^ r0 ^ 0x6FE8EE1B) & M32
    if c not in conts:
        conts.append(c)
print("容器数 %d  索引范围 %d..%d" % (len(conts), min(conts), max(conts)))

obs = {}
for c in conts:
    d12 = struct.unpack_from("<I", BUF, OWN + c * 0x10 + 0xC)[0]
    obs[c] = (d12 - 0x175A3FDF) & M32


def variants(i):
    out = {}
    a = ((i * 0x6AE9) ^ 0x2E6F3E3D) & M64
    b = (a * 0x2AD3DD28) & M64
    # 变体 1：全 64 位（反编译直译）
    t = ((b >> 0x16) * 0x4C39B37D) & M64
    out["v1_64"] = (((t >> 10) & M32) ^ 0x4DFAA6B0) * 0x22449C6E & M32
    # 变体 2：>>0x16 后截 32
    t = (((b >> 0x16) & M32) * 0x4C39B37D) & M64
    out["v2_trunc22"] = (((t >> 10) & M32) ^ 0x4DFAA6B0) * 0x22449C6E & M32
    # 变体 3：中间截 32 再做 >>10
    t = ((b >> 0x16) * 0x4C39B37D) & M32
    out["v3_trunc_t"] = ((t >> 10) ^ 0x4DFAA6B0) * 0x22449C6E & M32
    # 变体 4：乘 0x22449c6e 在 64 位
    out["v4_mul64"] = (((((t >> 10) & M32) ^ 0x4DFAA6B0) * 0x22449C6E) & M64) & M32
    # 变体 5：先截 uint 再 >>10（等价失败对照）
    out["v5"] = (((b & M32) >> 0x16) * 0x4C39B37D >> 10 ^ 0x4DFAA6B0) * 0x22449C6E & M32
    return out


keys = list(variants(0).keys())
for k in keys:
    hit = 0
    for c in conts:
        if variants(c)[k] == obs[c]:
            hit += 1
    print("  %-14s 命中 %4d / %d" % (k, hit, len(conts)))

# 若都不中，尝试反推：prf 与 obs 的关系
print()
print("样例行（c, d0,d4,d8,d12, obs）")
for c in conts[:6]:
    w = struct.unpack_from("<4I", BUF, OWN + c * 0x10)
    print("  %5d  %08X %08X %08X %08X  obs=%08X  v1=%08X"
          % (c, w[0], w[1], w[2], w[3], obs[c], variants(c)["v1_64"]))
