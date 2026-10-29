#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件表提取

typedef +0x18 (XOR 0x689A417F) = eventStart
typedef +0x52 (SUB -0x1197)   = event_count
表基址 = buf + (u32(DAT_188198E24) ^ 0x3A73133E) = 0x242AC00, 记录 0x18

prf18(i) = ((((i*0x7A00 ^ 0x3B79566A) * 0x3EA7ABC3) ^ 0x52121A98000) >> 0xC) & 0xFFFFFFFF)
           * 0x20CF3F69
记录: [0]add [1]remove [2]raise [3]typeIdx [4]nameId [5]attrs/token
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT = r"D:\Carol-start\_rea\bh3_events.tsv"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
T18 = 0x242AC00
CTYPE_TBL = 0x186D41F80

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
POOL = u32va(0x188198E50) ^ 0x7483FF7A
T0 = BASE + TYPE_OFF
P = BASE + POOL
KM = (-0x394A88E12FFFF3A0) & M64
KA = 0x53DB1FC7E9ECC644
KS = 0x64C7CE0352814CF6
_u64 = struct.Struct("<Q")
ct_off = va2off(CTYPE_TBL)


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
    est = ((r[6] ^ 0x689A417F) - s) & M32
    raw = struct.unpack_from("<H", BUF, off + 0x52)[0]
    sr = raw - 0x10000 if raw & 0x8000 else raw
    ecnt = (sr + 0x1197 - S16[i]) & 0xFFFF
    recs.append({"i": i, "ns": ns, "name": nm, "est": est, "ecnt": ecnt})


def full(i):
    return (recs[i]["ns"] + "." if recs[i]["ns"] else "") + (recs[i]["name"] or "?")


starts = {r["i"]: r["est"] for r in recs if r["est"] != M32}
tot = sum(r["ecnt"] for r in recs)
print("[事件] 有事件的类型 = %d / %d" % (len(starts), NT))
print("  eventStart 范围 [%d, %d]  唯一 %d" % (min(starts.values()), max(starts.values()),
                                              len(set(starts.values()))))
print("  event_count 合计 = %d" % tot)
print("  建表区间 = 0x%X .. 0x%X  (0x%X 字节)"
      % (BASE + T18, BASE + T18 + tot * 0x18, tot * 0x18))

# 差分校验
order = sorted(starts.items(), key=lambda kv: kv[1])
ok = bad = 0
for k in range(len(order) - 1):
    ti, st = order[k]
    if order[k + 1][1] - st == recs[ti]["ecnt"]:
        ok += 1
    else:
        bad += 1
print("  差分 vs +0x52: 一致 %d / 不一致 %d" % (ok, bad))


def prf18(i):
    t = ((i * 0x7A00) ^ 0x3B79566A) & M64
    t = (t * 0x3EA7ABC3) & M64
    t = (t ^ 0x52121A98000) & M64
    t = t >> 0xC
    return (t & M32) * 0x20CF3F69 & M32


def ctype_name(idx):
    if idx == M32 or idx >= 354184:
        return "?"
    p = struct.unpack_from("<Q", d, ct_off + idx * 8)[0]
    po = va2off(p)
    if po is None:
        return "?"
    data = struct.unpack_from("<Q", d, po)[0]
    ty = d[po + 10]
    if ty in (0x11, 0x12):
        return full(data) if data < NT else "?"
    if ty == 0x15:
        go = va2off(data)
        if go is None:
            return "?"
        bi = struct.unpack_from("<I", d, go)[0]
        return (full(bi) if bi < NT else "?") + "<...>"
    if ty == 0x1C:
        return "System.Object"
    return {0x02: "bool", 0x03: "char", 0x08: "int", 0x0E: "string", 0x0C: "float",
            0x0D: "double", 0x0A: "long"}.get(ty, "")


rows = []
for ti in sorted(starts):
    st = starts[ti]
    n = recs[ti]["ecnt"]
    tn = full(ti)
    for k in range(n):
        gi = st + k
        o = BASE + T18 + gi * 0x18
        p0, p1, p2, p3, p4, p5 = struct.unpack_from("<6I", BUF, o)
        v = prf18(gi)
        nm = dec((v ^ ((p4 + 0xBFC65639) & M32)) & M32)
        tidx = ((p3 + 0xFCC28A65) & M32) ^ v
        addi = ((p0 + 0xC617C479) & M32) ^ v
        remi = (p1 ^ v) ^ 0x5AF3CD0
        raii = (p2 ^ v) ^ 0x5E4DD4F1
        tok = ((p5 + 0xCE2556FD) & M32) ^ v ^ 0x3081751A
        rows.append((ti, tn, gi, nm or "", ctype_name(tidx),
                     "" if addi == M32 else addi,
                     "" if (p1 ^ v) == 0xFA50C32F else remi,
                     "" if (p2 ^ v) == 0xA1B22B0E else raii,
                     "%08X" % tok))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("typeIdx\ttypeName\teventIdx\teventName\teventType\taddIdx\tremoveIdx\traiseIdx\ttoken\n")
    for r in rows:
        f.write("\t".join(str(x) for x in r) + "\n")

print("[+] %s  (%d 条事件)" % (OUT, len(rows)))

print("\n[校验] 已知类型事件")
for t in ("System.AppDomain", "UnityEngine.Application", "UnityEngine.SceneManagement.SceneManager",
          "System.Threading.Timer", "UnityEngine.UI.Button"):
    ti = next((r["i"] for r in recs if full(r["i"]) == t), None)
    if ti is None:
        print("  %s 未找到" % t)
        continue
    names = [r[3] for r in rows if r[0] == ti]
    print("  %-44s %2d 事件: %s" % (t, len(names), ", ".join(names)))
