#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XOR 型字段求解：窗口太大 = XOR 型或大值字段

假设值域 value ∈ {-1} ∪ [B, B+T]：
  - parentIndex:  B=0,          T=351,794 (Il2CppType 表)
  - token:        B=0x02000000, T=60,000   (TypeDef token)
  - declaringTypeIndex: B=0,    T=57,487
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
T0 = BASE + TYPE_OFF

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

RAW = [struct.unpack_from("<23I", BUF, T0 + i * STEP) for i in range(NT)]
PROBES = (0, 1, 2, 3, 4, 5, 7, 11, 12, 19, 25, 40, 100, 500, 2000, 5000, 20000, 50000)
POS = (2, 11, 16, 17, 18, 19, 20, 22)


def solve_xor(pos, B, T):
    r0, s0 = RAW[0][pos], SALT[0]
    out = []
    v0list = [M32]  # -1
    for delta in range(0, T + 1, max(1, T // 4000)):  # 粗扫加速：窗口内采样
        v0list.append((B + delta) & M32)
    for v0 in v0list:
        C = r0 ^ ((s0 + v0) & M32)
        ok = True
        for i in PROBES:
            val = ((RAW[i][pos] ^ C) - SALT[i]) & M32
            if val != M32 and not (B <= val <= B + T):
                ok = False
                break
        if ok:
            out.append((C, v0))
            if len(out) > 5:
                break
    return out


print("[*] XOR 求解：B/T 组合逐 pos 扫描（粗扫）")
for B, T, tag in [(0, 351794, "parentIndex?"), (0x02000000, 60000, "token?"), (0, 57487, "declaring?")]:
    print("\n--- 假设 %s  B=0x%08X T=%d ---" % (tag, B, T))
    for p in POS:
        hits = solve_xor(p, B, T)
        if hits:
            for C, v0 in hits[:3]:
                vals = [((RAW[i][p] ^ C) - SALT[i]) & M32 for i in range(NT)]
                nz = [v for v in vals if v != M32]
                if not nz:
                    continue
                inb = sum(1 for v in nz if B <= v <= B + T)
                print("  pos=%-3d C=0x%08X  有效=%d/%d 命中窗口=%d uniq=%d"
                      % (p, C, len(nz), NT, inb, len(set(nz))))
