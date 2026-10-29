#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_fieldA2.py — 把字段记录第 1 dword 当「池索引」解，看是不是字符串"""
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
POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A
FLD_OFF = (u32va(0x188198E84) - 0x2F59FE76) & M32
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6
T0 = BASE + TYPE_OFF
P_ABS = BASE + POOL_OFF
F0 = BASE + FLD_OFF
_u64 = struct.Struct("<Q")

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


_sc = {}


def dec(pid):
    if pid in _sc:
        return _sc[pid]
    L = (pid >> 24) & 0xFF
    if L == 0 or L > 0x40:
        _sc[pid] = None
        return None
    ix = pid & 0xFFFFFF
    src = P_ABS + ix
    nb = (L + 7) >> 3
    if src + nb * 8 > FSIZE:
        _sc[pid] = None
        return None
    key = (ix * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        out += (_u64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    try:
        t = out[:L].decode("utf-8")
    except UnicodeDecodeError:
        _sc[pid] = None
        return None
    for ch in t:
        if ord(ch) < 0x20 or ord(ch) == 0x7F:
            _sc[pid] = None
            return None
    _sc[pid] = t
    return t


S16 = [(SALT[i] & 0xFFFF) - 0x10000 if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]
starts = {}
fcnt = {}
for i in range(NT):
    off = T0 + i * STEP
    r7 = struct.unpack_from("<I", BUF, off + 0x1C)[0]
    v = ((r7 - SALT[i]) + 0xAA6F650E) & M32
    raw16 = struct.unpack_from("<H", BUF, off + 0x4E)[0]
    sr = raw16 - 0x10000 if raw16 & 0x8000 else raw16
    fcnt[i] = (sr - S16[i] - 2) & 0xFFFF
    if v != M32:
        starts[i] = v

# 先看几个已知类型：String / Vector3
KNOWN = {}
for i in range(NT):
    off = T0 + i * STEP
    r = struct.unpack_from("<23I", BUF, off)
    s = SALT[i]
    nm = dec((((r[13] ^ 0x3399EFB) - s) & M32))
    ns = dec(((((r[12] - s) & M32) - 0x4B6ACCC7) & M32)) or ""
    full = (ns + "." if ns else "") + (nm or "?")
    if full in ("System.String", "UnityEngine.Vector3", "UnityEngine.Vector2", "System.Object"):
        KNOWN[full] = i

print("[已知类型索引]", KNOWN)

# 统计：A 当池索引的可解率
hit = miss = 0
samples = []
for ti in sorted(starts, key=lambda x: starts[x]):
    n = fcnt[ti]
    if n <= 0:
        continue
    for k in range(n):
        fi = starts[ti] + k
        if F0 + fi * 0xC + 12 > FSIZE:
            break
        a, b, c = struct.unpack_from("<3I", BUF, F0 + fi * 0xC)
        A = (a - prf(fi)) & M32
        s = dec(A)
        if s is None:
            miss += 1
        else:
            hit += 1
            if len(samples) < 25:
                samples.append((ti, fi, A, s))
print("\n[A 当池索引] 可解 %d / 不可解 %d  (%.2f%%)" % (hit, miss, 100.0 * hit / max(hit + miss, 1)))
print("\n[样本]")
for ti, fi, A, s in samples:
    print("   t%-6d f%-7d 0x%08X  %r" % (ti, fi, A, s))

# 已知类型的完整字段 + A
for name, ti in KNOWN.items():
    if ti not in starts:
        print("\n## %s (t%d) 无字段" % (name, ti))
        continue
    print("\n## %s (t%d)  n=%d" % (name, ti, fcnt[ti]))
    for k in range(min(fcnt[ti], 30)):
        fi = starts[ti] + k
        if F0 + fi * 0xC + 12 > FSIZE:
            break
        a, b, c = struct.unpack_from("<3I", BUF, F0 + fi * 0xC)
        pv = prf(fi)
        A = (a - pv) & M32
        nid = ((c ^ 0x5DAAB140) - pv) & M32
        print("   k=%-3d fi=%-7d fn=%-32r A=0x%08X  dec=%r" % (k, fi, dec(nid), A, dec(A)))
