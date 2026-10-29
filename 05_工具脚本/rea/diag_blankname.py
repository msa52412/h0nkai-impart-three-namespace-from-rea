#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 IFix.IDMAP4 尾部 8 个空字段名的原始记录"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
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
FSIZE = len(BUF)


def u32va(va):
    o = va2off(va)
    return None if o is None else struct.unpack_from("<I", d, o)[0]


POOL = u32va(0x188198E50) ^ 0x7483FF7A
FLD = (u32va(0x188198E84) - 0x2F59FE76) & M32
P = BASE + POOL
F0 = BASE + FLD
KM = (-0x394A88E12FFFF3A0) & M64
KA = 0x53DB1FC7E9ECC644
KS = 0x64C7CE0352814CF6
_u64 = struct.Struct("<Q")


def dec(pid):
    L = (pid >> 24) & 0xFF
    if L == 0 or L > 0x80:
        return None
    ix = pid & 0xFFFFFF
    src = P + ix
    nb = (L + 7) >> 3
    if src + nb * 8 > FSIZE:
        return None
    key = (ix * KM + KA) & M64
    out = bytearray()
    for b in range(nb):
        out += (_u64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
        key = (key + KS) & M64
    try:
        return out[:L].decode("utf-8")
    except UnicodeDecodeError:
        return None


K1 = 0x7740EEFF55F40540
K2 = 0x49ED7F5AFCC4AF8


def prf(i):
    return (((i * K1 + K2) & M64) >> 0x11) & M32


for fi in (418325, 418326, 418327, 418397, 418398, 418399, 418401, 418402, 418403, 418404):
    a, b, c = struct.unpack_from("<3I", BUF, F0 + fi * 0xC)
    pv = prf(fi)
    nid = ((c ^ 0x5DAAB140) - pv) & M32
    tidx = ((b - pv) - 0xF2A3D7F) & M32
    print("fi=%-7d  raw=(%08X,%08X,%08X)  nameId=%08X L=%3d ix=%06X -> %r   typeIdx=%d"
          % (fi, a, b, c, nid, (nid >> 24) & 0xFF, nid & 0xFFFFFF, dec(nid), tidx))
