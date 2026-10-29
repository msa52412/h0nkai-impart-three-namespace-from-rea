#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_fieldA.py — 判定字段记录第 1 个 dword 的真实语义
候选：token / fieldOffset / flags / 索引自校验
"""
import struct
from collections import Counter

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
BASE = 0x118

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


def u32va(va):
    o = va2off(va)
    return None if o is None else struct.unpack_from("<I", d, o)[0]


BUF = open(META, "rb").read()
FSIZE = len(BUF)
TYPE_OFF = (u32va(0x188198E08) ^ 0x2B849DB3) & M32
FLD_OFF = (u32va(0x188198E84) - 0x2F59FE76) & M32
T0 = BASE + TYPE_OFF
F0 = BASE + FLD_OFF

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

K1 = 0x7740EEFF55F40540
K2 = 0x49ED7F5AFCC4AF8


def prf(i):
    return (((i * K1 + K2) & M64) >> 0x11) & M32


# 收集所有类型的 fieldStart / fieldCount
S16 = [(SALT[i] & 0xFFFF) - 0x10000 if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]
starts = {}
fcnt = {}
for i in range(NT):
    off = T0 + i * STEP
    r7 = struct.unpack_from("<I", BUF, off + 0x1C)[0]
    v = ((r7 - SALT[i]) + 0xAA6F650E) & M32
    raw16 = struct.unpack_from("<H", BUF, off + 0x4E)[0]
    sr = raw16 - 0x10000 if raw16 & 0x8000 else raw16
    n = (sr - S16[i] - 2) & 0xFFFF
    fcnt[i] = n
    if v != M32:
        starts[i] = v

# 全部字段记录
order = sorted(starts.items(), key=lambda kv: kv[1])
tot = 0
A_list = []
for ti, st in order:
    n = fcnt[ti]
    if n <= 0:
        continue
    for k in range(n):
        fi = st + k
        if F0 + fi * 0xC + 12 > FSIZE:
            break
        a, b, c = struct.unpack_from("<3I", BUF, F0 + fi * 0xC)
        A = (a - prf(fi)) & M32
        A_list.append((fi, ti, k, A))
        tot += 1
print("[字段] 总记录 %d   A 范围 [0x%X, 0x%X]" % (tot, min(x[3] for x in A_list), max(x[3] for x in A_list)))

# 1) A 与 fi 的关系
diff = Counter((A - fi) & M32 for fi, ti, k, A in A_list)
print("\n[A - fi] Top8:")
for v, c in diff.most_common(8):
    print("   0x%08X  x%d" % (v, c))

# 2) 是否像 token (0x04xxxxxx)
tok = sum(1 for _, _, _, A in A_list if (A >> 24) == 0x04)
print("\n[A>>24==0x04 占比] %.2f%%" % (100.0 * tok / max(tot, 1)))

# 3) 是否像小偏移 (0..0x1000)
small = sum(1 for _, _, _, A in A_list if A < 0x2000)
print("[A < 0x2000 占比] %.2f%%" % (100.0 * small / max(tot, 1)))

# 4) 低位 bit 分布（找 flags 特征）
bits = [0] * 32
for _, _, _, A in A_list:
    for b in range(32):
        if A >> b & 1:
            bits[b] += 1
print("\n[bit 置位率]")
for b in range(24, 32):
    print("   bit%-2d  %6.2f%%" % (b, 100.0 * bits[b] / max(tot, 1)))

# 5) 抽样：Vector3 / Vector2 / String
def full(i):
    off = T0 + i * STEP
    r = struct.unpack_from("<23I", BUF, off)
    return i

print("\n[抽样类型 A 序列]")
for ti in order:
    st, n = starts[ti], fcnt[ti]
    if n < 6 or n > 20:
        continue
    seq = []
    for k in range(n):
        fi = st + k
        if F0 + fi * 0xC + 12 > FSIZE:
            break
        a, b, c = struct.unpack_from("<3I", BUF, F0 + fi * 0xC)
        seq.append((a - prf(fi)) & M32)
    d2 = set((seq[k + 1] - seq[k]) & M32 for k in range(len(seq) - 1))
    if len(d2) <= 2:
        print("   type %-6d n=%-3d A=%s" % (ti, n, " ".join("%08X" % x for x in seq)))
        if ti > 40000:
            break
