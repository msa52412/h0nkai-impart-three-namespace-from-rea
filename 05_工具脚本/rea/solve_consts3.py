#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用字段反混淆常量求解器 v3 —— 同时支持 XOR 型与 SUB 型

  XOR 型: value = ((raw ^ C) - salt) mod 2^32     （如 name、nestedTypesStart）
  SUB 型: value = ((raw - C) - salt) mod 2^32     （如 namespace）

value ∈ {-1} ∪ [0, T]
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
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


TYPE_OFF = (u32va(0x188198E08) ^ 0x2B849DB3) & M32
with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
T0 = BASE + TYPE_OFF

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

RAW = [struct.unpack_from("<23I", BUF, T0 + i * STEP) for i in range(NT)]
PROBES = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 19, 25, 40, 100, 500, 2000, 5000)


def check(mode, pos, C, Tmax):
    for i in PROBES:
        if mode == "X":
            val = ((RAW[i][pos] ^ C) - SALT[i]) & M32
        else:
            val = ((RAW[i][pos] - C) - SALT[i]) & M32
        if val != M32 and val > Tmax:
            return False
    return True


def solve(mode, pos, Tmax):
    r0, s0 = RAW[0][pos], SALT[0]
    out = []
    for v0 in range(-1, Tmax + 1):
        if mode == "X":
            C = r0 ^ ((s0 + v0) & M32)
        else:
            C = (r0 - s0 - v0) & M32
        if check(mode, pos, C, Tmax):
            out.append(C)
            if len(out) > 4:
                return out
    return out


def values(mode, pos, C):
    if mode == "X":
        return [((RAW[i][pos] ^ C) - SALT[i]) & M32 for i in range(NT)]
    return [((RAW[i][pos] - C) - SALT[i]) & M32 for i in range(NT)]


def try_pos(pos, tmps=(408461, 500000, 1 << 20, FSIZE)):
    for Tmax in tmps:
        for mode in ("S", "X"):
            c = solve(mode, pos, Tmax)
            if len(c) == 1:
                return mode, c[0], Tmax
    return None, None, None


print("[校验] pos=8 -> ", end="")
print(try_pos(8, (30000,)))
print("[校验] pos=13 (name) -> ", end="")
print(try_pos(13, (1 << 26,)))

print("\n" + "=" * 82)
print("%-4s %-4s %-12s %-10s %-10s %-9s %s" % ("pos", "型", "C", "Tmax", "max", "非-1数", "前 8 值"))
found = {}
for p in range(23):
    mode, C, Tmax = try_pos(p)
    if mode is None:
        print("%-4d %-4s %-12s %-10s %-10s %-9s" % (p, "?", "--", "--", "--", "--"))
        continue
    vals = values(mode, p, C)
    nz = [v for v in vals if v != M32]
    found[p] = (mode, C, vals)
    print("%-4d %-4s 0x%08X   %-10d %-10d %-9d %s"
          % (p, mode, C, Tmax, max(nz) if nz else -1, len(nz),
             [("nil" if v == M32 else v) for v in vals[:8]]))

import json
json.dump({str(k): [v[0], v[1]] for k, v in found.items()},
          open(r"D:\Carol-start\_rea\type_field_consts.json", "w"), indent=1)
print("\n[+] 写出 type_field_consts.json")
