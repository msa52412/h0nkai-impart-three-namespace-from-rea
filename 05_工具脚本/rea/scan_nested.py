#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
找 nestedTypesStart：判据不用已知列，用**结构性质**。
nestedTypes 数组存的是 TypeDefinitionIndex，所以该字段必须满足：
  1) 值域落在 [0, NT]（NT=57487），不能像 parentIdx 那样到 35 万
  2) 非递减（数组按类型顺序排）
  3) 首值接近 0、末值接近 NT
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487

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
TYPE_OFF = (struct.unpack_from("<I", d, va2off(0x188198E08))[0] ^ 0x2B849DB3) & M32
T0 = BASE + TYPE_OFF

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)
S16 = [(SALT[i] & 0xFFFF) - 0x10000 if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]
S32 = SALT

print("[*] 扫描 32 位字段：找值域 [0,%d] 的非递减序列" % NT)
cands = []
for o in range(0, STEP - 3, 4):
    v = []
    ok = True
    for i in range(NT):
        raw = struct.unpack_from("<I", BUF, T0 + i * STEP + o)[0]
        x = (raw - S32[i]) & M32
        if x > NT + 8:          # 超范围，立刻否掉
            ok = False
            break
        v.append(x)
    if not ok or len(v) < NT:
        continue
    bad = sum(1 for i in range(NT - 1) if v[i + 1] < v[i])
    cands.append((o, v[0], v[-1], bad, max(v)))
    print("  +0x%02X  首=%-7d 末=%-7d 逆序=%-6d 最大=%-7d" % (o, v[0], v[-1], bad, max(v)))

print("\n[*] 扫描 16 位字段（同判据）")
for o in range(0, STEP - 1, 2):
    v = []
    ok = True
    for i in range(NT):
        raw = struct.unpack_from("<H", BUF, T0 + i * STEP + o)[0]
        sr = raw - 0x10000 if raw & 0x8000 else raw
        x = (sr - S16[i]) & 0xFFFF
        if x > NT + 8:
            ok = False
            break
        v.append(x)
    if not ok or len(v) < NT:
        continue
    bad = sum(1 for i in range(NT - 1) if v[i + 1] < v[i])
    print("  +0x%02X  首=%-7d 末=%-7d 逆序=%-6d 最大=%-7d" % (o, v[0], v[-1], bad, max(v)))
