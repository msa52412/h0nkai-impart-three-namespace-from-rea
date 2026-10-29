#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""网格搜索属性表 prfP 的正确形态"""
import struct
import itertools

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
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


N = 1200
recs = []
for i in range(N):
    o = BASE + TP + i * 0x14
    p0 = struct.unpack_from("<I", BUF, o)[0]
    recs.append(p0)


def s32(v):
    v &= M32
    return v - (1 << 32) if v & 0x80000000 else v


def build(i, mulwidth, shift, mode):
    x = (i * 0x64D5) & (M64 if mulwidth == 64 else M32)
    x ^= 0x6D7B1F20
    x = (x + 0x10ECA71E) & (M64 if mulwidth == 64 else M32)
    y = (x * 0x7737C996) & (M64 if mulwidth == 64 else M32)
    if mode == "shr64":
        t = (y >> shift) & M32
    elif mode == "sar32":
        t = (s32(y) >> shift) & M32
    elif mode == "shr32":
        t = ((y & M32) >> shift) & M32
    return (t + 0x5505FF6B) & M32


best = []
for mulwidth in (64, 32):
    for shift in (6, 7, 8, 9, 0xA, 0xC, 0x11, 0x15):
        for mode in ("shr64", "sar32", "shr32"):
            hit = 0
            sample = []
            for i, p0 in enumerate(recs):
                m = (build(i, mulwidth, shift, mode) * 0xEACB0367) & M32
                v = dec(((p0 ^ 0x5566C15D) + m) & M32)
                if v and len(v) >= 4:
                    hit += 1
                    if len(sample) < 3:
                        sample.append(v)
            best.append((hit, mulwidth, shift, mode, sample))

best.sort(reverse=True)
for h, w, s, mode, smp in best[:10]:
    print("命中 %4d/%d   mul%d shift=0x%X %-6s  %s" % (h, N, w, s, mode, ", ".join(smp)))
