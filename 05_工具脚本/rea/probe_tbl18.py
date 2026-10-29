#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉死 typedef+0x18 语义（疑似 propertyStart），并解 TBL_18 (0x242AC00, 0x18 记录)

FUN_18044b230 原文:
  uVar11 = (int)((((i*0x7a00 ^ 0x3b79566a) * 0x3ea7abc3 ^ 0x52121a98000) >> 0xc) * 0x20cf3f69)
  start  = (*(uint*)(td+0x18) ^ 0x689a417f) - klassSalt
  name   = dec(uVar11 ^ ((piVar1[4] + 0xbfc65639) & M32))
  type   = ((piVar1[3] + 0xfcc28a65) ^ uVar11)
  getter = (piVar1[1] ^ uVar11)   哨兵 0xfa50c32f
  setter = (piVar1[2] ^ uVar11)   哨兵 0xa1b22b0e
  attrs  = (piVar1[5] + 0xce2556fd) ^ uVar11 ^ 0x3081751a
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
TBL18 = 0x242AC00

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
TYPE_OFF = (u32va(0x188198E08) ^ 0x2B849DB3) & M32
POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A
T0 = BASE + TYPE_OFF
P = BASE + POOL_OFF
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


SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

S16 = [(SALT[i] & 0xFFFF) - 0x10000 if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]

recs = []
for i in range(NT):
    off = T0 + i * STEP
    r = struct.unpack_from("<23I", BUF, off)
    s = SALT[i]
    nm = dec((((r[13] ^ 0x3399EFB) - s) & M32))
    ns = dec(((((r[12] - s) & M32) - 0x4B6ACCC7) & M32)) or ""
    # 各计数
    raw44 = struct.unpack_from("<H", BUF, off + 0x44)[0]
    c44 = ((raw44 ^ 0x910A) - S16[i]) & 0xFFFF
    raw46 = struct.unpack_from("<H", BUF, off + 0x46)[0]
    c46 = ((raw46 ^ 0x7883) - S16[i]) & 0xFFFF
    raw48 = struct.unpack_from("<H", BUF, off + 0x48)[0]
    sr = raw48 - 0x10000 if raw48 & 0x8000 else raw48
    c48 = (sr + 0x1950 - S16[i]) & 0xFFFF
    raw4a = struct.unpack_from("<H", BUF, off + 0x4A)[0]
    sr = raw4a - 0x10000 if raw4a & 0x8000 else raw4a
    c4a = (sr + 0x17A3 - S16[i]) & 0xFFFF
    raw4c = struct.unpack_from("<H", BUF, off + 0x4C)[0]
    c4c = ((raw4c ^ 0x5BE4) - S16[i]) & 0xFFFF
    raw4e = struct.unpack_from("<H", BUF, off + 0x4E)[0]
    sr = raw4e - 0x10000 if raw4e & 0x8000 else raw4e
    c4e = (sr - 2 - S16[i]) & 0xFFFF
    recs.append({"i": i, "ns": ns, "name": nm, "r": r, "s": s,
                 "c44": c44, "c46": c46, "c48": c48, "c4a": c4a, "c4c": c4c, "c4e": c4e})


def full(i):
    return (recs[i]["ns"] + "." if recs[i]["ns"] else "") + (recs[i]["name"] or "?")


def find(t):
    for r in recs:
        if full(r["i"]) == t:
            return r
    return None


# typedef+0x18 起点（XOR 0x689A417F）
def start18(r):
    return ((r["r"][6] ^ 0x689A417F) - r["s"]) & M32


def start1c(r):
    return ((r["r"][7] - r["s"]) + 0xAA6F650E) & M32


def start14(r):
    return ((r["r"][5] - r["s"]) + 0x2822B502) & M32


print("%-34s %-6s %-8s %-8s %-8s | %s" % ("类型", "c48", "start14", "start1c", "start18",
                                          "计数 4a/4c/4e/44/46"))
for t in ("System.String", "System.Exception", "System.Int32", "System.Object",
          "UnityEngine.MonoBehaviour", "System.Collections.Generic.List`1"):
    r = find(t)
    if not r:
        print("  未找到", t)
        continue
    print("%-34s %-6d %-8d %-8d %-8d | %d/%d/%d/%d/%d"
          % (t, r["c48"], start14(r), start1c(r), start18(r),
             r["c4a"], r["c4c"], r["c4e"], r["c44"], r["c46"]))

print()
print("=== 全局 start18 范围 ===")
sv = sorted(start18(r) for r in recs if start18(r) != M32)
print("  [%d, %d]  唯一 %d  (非 -1 的类型数 %d)"
      % (sv[0], sv[-1], len(set(sv)), len(sv)))

print()
print("=== 用 start18 + 各种计数 解 TBL_18 ===")


def prf18(i):
    t = ((i * 0x7A00) ^ 0x3B79566A) & M64
    t = (t * 0x3EA7ABC3) & M64
    t = (t ^ 0x52121A98000) & M64
    t = t >> 0xC
    return (t & M32) * 0x20CF3F69 & M32


def tbl18_name(i, r):
    st = start18(r)
    if st == M32:
        return None
    o = BASE + TBL18 + (st + i) * 0x18
    if o + 0x18 > len(BUF):
        return None
    p0, p1, p2, p3, p4, p5 = struct.unpack_from("<6I", BUF, o)
    v = prf18(st + i)
    nid = (v ^ ((p4 + 0xBFC65639) & M32)) & M32
    return (dec(nid), (p3 + 0xFCC28A65) & M32 ^ v,
            (p1 ^ v), (p2 ^ v), ((p5 + 0xCE2556FD) & M32) ^ v ^ 0x3081751A)


for t in ("System.String", "System.Exception", "System.Int32"):
    r = find(t)
    if not r:
        continue
    print("\n  [%s] start18=%d  计数4a=%d 4c=%d 4e=%d 44=%d 46=%d"
          % (t, start18(r), r["c4a"], r["c4c"], r["c4e"], r["c44"], r["c46"]))
    for k in range(6):
        out = tbl18_name(k, r)
        if out is None:
            print("    -")
            continue
        nm, ty, g, s, at = out
        print("    %-28s type=%-6d getter=%-10X setter=%-10X attrs=%08X" % (nm, ty, g, s, at))
