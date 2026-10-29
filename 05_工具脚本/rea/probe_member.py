#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探测 12 字节记录表：base = DAT_188198e84 - 0x2F59FE76

来自 FUN_18044b7f0：
  lVar7 = (DAT_188198e84 + -0x2f59fe76) + DAT_1899dbaf8
  piVar1 = (int *)(lVar7 + uVar6 * 0xc)              // 12 字节记录
  iVar8  = (int)(uVar6 * 0x7740eeff55f40540 + 0x49ed7f5afcc4af8 >> 0x11)
  typeIdx = (*(int*)(rec+4) - iVar8) + (-0xf2a3d7f)
  name    = FUN_18043ab50((rec[2] ^ 0x5daab140) - iVar8)
  rec[0]  -> (rec[0] - iVar8) + 0xfd930efc ^ 0x1c64e9e

每类型的 (start, count)：
  start = (record[0x1C] - salt) + 0xAA6F650E
  count = metadata +0x4E
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
TBL_CTYPE = 0x186D41F80

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
    name = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((name, va, vs, rs, rp))


def va2off(va):
    rva = va - IB
    for name, vaddr, vsize, rsize, rptr in SECS:
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
NEWTBL = (u32va(0x188198E84) - 0x2F59FE76) & M32
print("TYPE_OFF=0x%X POOL=0x%X NEWTBL=0x%X (abs 0x%X)" % (TYPE_OFF, POOL_OFF, NEWTBL, BASE + NEWTBL))

K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6
T0 = BASE + TYPE_OFF
P_ABS = BASE + POOL_OFF
_u64 = struct.Struct("<Q")

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)
S16 = [(SALT[i] & 0xFFFF) - 0x10000 if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]

_sc = {}


def dec(pid):
    if pid in _sc:
        return _sc[pid]
    L = (pid >> 24) & 0xFF
    if L == 0 or L > 0x80:
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


v4 = {int(p[0]): p for p in (l.rstrip("\n").split("\t") for l in open(
    r"D:\Carol-start\_rea\bh3_types_v4.txt", encoding="utf-8").readlines()[1:])}

tbl_off = va2off(TBL_CTYPE)
K1 = 0x7740EEFF55F40540
K2 = 0x49ED7F5AFCC4AF8


def prf(i):
    return (((i * K1 + K2) & M64) >> 0x11) & M32


def rec_off(i):
    return BASE + NEWTBL + i * 0xC


def ctype_name(idx):
    if idx == M32 or idx >= 354184:
        return "<nil>"
    p = struct.unpack_from("<Q", d, tbl_off + idx * 8)[0]
    po = va2off(p)
    if po is None:
        return "<badptr>"
    data = struct.unpack_from("<Q", d, po)[0]
    ty = d[po + 10]
    if ty in (0x11, 0x12) and data < NT:
        r = v4[data]
        return (r[1] + "." if r[1] else "") + r[2]
    return "<ty%02X>" % ty


for idx in (301, 259, 218, 383, 32753):
    off = T0 + idx * STEP
    r = struct.unpack_from("<23I", BUF, off)
    s = SALT[idx]
    cnt = ((struct.unpack_from("<H", BUF, off + 0x4E)[0] - 0x10000
            if struct.unpack_from("<H", BUF, off + 0x4E)[0] & 0x8000
            else struct.unpack_from("<H", BUF, off + 0x4E)[0]) + 2 - S16[idx]) & 0xFFFF
    start = ((r[7] - s) + 0xAA6F650E) & M32
    nm = v4[idx][1] + "." + v4[idx][2]
    print("\n=== [%d] %s  count=%d start=%d ===" % (idx, nm, cnt, start))
    for k in range(min(cnt, 12)):
        i = (start + k) & M32
        o = rec_off(i)
        if o + 12 > FSIZE:
            print("   out of file")
            break
        a, b, c = struct.unpack_from("<3I", BUF, o)
        pv = prf(i)
        tidx = ((b - pv) - 0xF2A3D7F) & M32
        nid = (((c ^ 0x5DAAB140) - pv) & M32)
        token = ((((a - pv) & M32) + 0xFD930EFC) & M32) ^ 0x1C64E9E
        print("   [%3d] name=%-30s type=%-38s tok=0x%08X"
              % (i, str(dec(nid)), ctype_name(tidx), token))
