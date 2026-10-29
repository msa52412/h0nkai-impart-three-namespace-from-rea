#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
类型表终版产物 v2 —— 全字段版

本版相对 v1 的变化：
  * methodStart C 修正为 0x2822B502（-1 哨兵语义，差分总和精确 = 408,461）
  * methodCount 改用独立字段 +0x48（与差分 57486/57487 一致）
  * 新增 token、parentIdx、nestedCount、interfaces/interfacesCount
"""
import json
import struct
from collections import Counter

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT_TXT = r"D:\Carol-start\_rea\bh3_types_full.txt"
OUT_JSON = r"D:\Carol-start\_rea\bh3_types.json"
METH = r"D:\Carol-start\_rea\bh3_methods.txt"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
N_METHOD = 408461

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
POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
T0 = BASE + TYPE_OFF
P_ABS = BASE + POOL_OFF
_U64 = struct.Struct("<Q")

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
        out += (_U64.unpack_from(BUF, src + b * 8)[0] ^ key).to_bytes(8, "little")
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


def u16c(i, reloff, C, isxor):
    r = struct.unpack_from("<H", BUF, T0 + i * STEP + reloff)[0]
    s = r - 0x10000 if r & 0x8000 else r
    v = ((s ^ C) if isxor else (s - C)) - S16[i]
    return v & 0xFFFF


recs = []
tot_m = tot_n = 0
for i in range(NT):
    off = T0 + i * STEP
    d = struct.unpack_from("<23I", BUF, off)
    s = SALT[i]
    name = dec((((d[13] ^ 0x3399EFB) - s) & M32))
    ns = dec(((((d[12] - s) & M32) - 0x4B6ACCC7) & M32)) or ""
    ms = ((d[5] - 0x2822B502) - s) & M32
    mc = u16c(i, 0x48, -0x1950, False)
    nc = u16c(i, 0x46, 0x7883, True)
    ns8 = ((d[8] ^ 0x21FE571D) - s) & M32
    tok = ((d[22] ^ 0x78647F39) - s) & M32
    par = ((d[0] - 0x15F045CB) - s) & M32
    if ms != M32:
        tot_m += mc
    if ns8 != M32:
        tot_n += nc
    recs.append({
        "i": i, "ns": ns, "name": name,
        "ms": -1 if ms == M32 else ms, "mc": mc,
        "nested": -1 if ns8 == M32 else ns8, "ncc": nc,
        "token": tok, "parent": -1 if par == M32 else par,
    })

print("sum(methodCount)=%d  sum(nestedCount)=%d" % (tot_m, tot_n))
print("token 唯一=%d  parent 有效=%d" % (
    len(set(r["token"] for r in recs)), sum(1 for r in recs if r["parent"] >= 0)))

MNAME = {}
with open(METH, encoding="utf-8") as f:
    for line in f:
        p = line.rstrip("\n").split("\t", 3)
        if len(p) == 4:
            MNAME[int(p[0])] = p[3]

with open(OUT_TXT, "w", encoding="utf-8") as f:
    f.write("index\tnamespace\ttype\ttoken\tmethodStart\tmethodCount\tnestedStart\tnestedCount\tparent\n")
    for r in recs:
        f.write("%d\t%s\t%s\t%08X\t%d\t%d\t%d\t%d\t%d\n"
                % (r["i"], r["ns"], r["name"] or "", r["token"], r["ms"], r["mc"],
                   r["nested"], r["ncc"], r["parent"]))

# 类型->方法 v2（用独立 count）
with open(r"D:\Carol-start\_rea\bh3_types_methods.txt", "w", encoding="utf-8") as f:
    for r in recs:
        if r["ms"] < 0 or r["mc"] <= 0:
            continue
        full = (r["ns"] + "." if r["ns"] else "") + (r["name"] or "?")
        f.write("\n=== %s  (start=%d, count=%d) ===\n" % (full, r["ms"], r["mc"]))
        for k in range(r["ms"], min(r["ms"] + r["mc"], N_METHOD)):
            f.write("  %s\n" % MNAME.get(k, "<missing:%d>" % k))

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump({"count": NT, "types": recs}, f, ensure_ascii=False)

print("[+] %s (v2)" % OUT_TXT)
print("[+] bh3_types_methods.txt (v2, 独立 count)")
print("[+] %s (v2)" % OUT_JSON)

print("\n[抽查]")
for want in ("System.String", "UnityEngine.GameObject", "MoleMole.BaseActor"):
    ns, _, tn = want.rpartition(".")
    r = next((x for x in recs if x["name"] == tn and x["ns"] == ns), None)
    if r:
        print("  %-28s token=%08X ms=%-6d mc=%-4d parent=%d"
              % (want, r["token"], r["ms"], r["mc"], r["parent"]))
