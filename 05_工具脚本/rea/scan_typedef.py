#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫 TypeDefinition 记录（步长 0x5C）的字段偏移。

方法：已知列（methodStart / methodCount / nestedCount / parentIdx / fieldCount）
已经解出来了，把它们当模板，对每个候选偏移 o 计算
    seq_o[i] = f(BUF[T0 + i*0x5C + o])
然后看 seq_o[i] - known[i] 是不是**恒定常数**。
恒定即命中——这比猜结构体定义可靠。
"""
import struct, sys

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
TYPES = r"D:\Carol-start\_rea\bh3_types_v5.txt"

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
S32 = [SALT[i] for i in range(NT)]

# 读已知列
rows = [l.rstrip("\n").split("\t") for l in open(TYPES, encoding="utf-8")][1:]
rows = [r for r in rows if len(r) >= 10]
COL = {"methodStart": 4, "methodCount": 5, "nestedCount": 6, "parentIdx": 7, "fieldCount": 9}
known = {k: [int(r[c]) for r in rows] for k, c in COL.items()}
print("已知列已读：%d 行" % len(rows))
for k, v in known.items():
    print("  %-12s min=%-8d max=%-10d" % (k, min(v), max(v)))


def test16(o, kname, kv):
    """候选 16 位字段：seq[i] = sign_extend(u16) - S16[i]，看与 kv 的差是否恒定"""
    diff = None
    for i in range(0, NT, 7):          # 抽样，快
        raw = struct.unpack_from("<H", BUF, T0 + i * STEP + o)[0]
        sr = raw - 0x10000 if raw & 0x8000 else raw
        v = (sr - S16[i]) & 0xFFFF
        dd = v - kv[i]
        if diff is None:
            diff = dd
        elif dd != diff:
            return None
    # 全量复核
    bad = 0
    for i in range(NT):
        raw = struct.unpack_from("<H", BUF, T0 + i * STEP + o)[0]
        sr = raw - 0x10000 if raw & 0x8000 else raw
        if ((sr - S16[i]) & 0xFFFF) - kv[i] != diff:
            bad += 1
            if bad > 3:
                return None
    return diff


def test32(o, kname, kv):
    diff = None
    for i in range(0, NT, 7):
        raw = struct.unpack_from("<I", BUF, T0 + i * STEP + o)[0]
        v = (raw - S32[i]) & M32
        dd = v - kv[i]
        if diff is None:
            diff = dd
        elif dd != diff:
            return None
    bad = 0
    for i in range(NT):
        raw = struct.unpack_from("<I", BUF, T0 + i * STEP + o)[0]
        if ((raw - S32[i]) & M32) - kv[i] != diff:
            bad += 1
            if bad > 3:
                return None
    return diff


print("\n[*] 16 位字段扫描")
hits = []
for o in range(0, STEP - 1, 2):
    for kname, kv in known.items():
        if max(kv) > 0xFFFF:
            continue
        r = test16(o, kname, kv)
        if r is not None:
            print("  命中 +0x%02X  <-  %s  (差值常量 %d)" % (o, kname, r))
            hits.append((o, kname, 16, r))

print("\n[*] 32 位字段扫描")
for o in range(0, STEP - 3, 2):
    for kname, kv in known.items():
        r = test32(o, kname, kv)
        if r is not None:
            print("  命中 +0x%02X  <-  %s  (差值常量 %d)" % (o, kname, r))
            hits.append((o, kname, 32, r))

print("\n[*] 已命中偏移：%s" % sorted(set(h[0] for h in hits)))
