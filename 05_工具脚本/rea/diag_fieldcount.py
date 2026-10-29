#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断：+0x4E 是否等于每类型字段数（差分）"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"

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


def u32va(va):
    o = va2off(va)
    return None if o is None else struct.unpack_from("<I", d, o)[0]


BUF = open(META, "rb").read()
TYPE_OFF = (u32va(0x188198E08) ^ 0x2B849DB3) & M32
T0 = BASE + TYPE_OFF

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

S16 = [(SALT[i] & 0xFFFF) - 0x10000 if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]

starts = {}
cnt = {}
for i in range(NT):
    off = T0 + i * STEP
    r = struct.unpack_from("<23I", BUF, off)
    s = SALT[i]
    fs = ((r[7] - s) + 0xAA6F650E) & M32
    raw16 = struct.unpack_from("<H", BUF, off + 0x4E)[0]
    sr = raw16 - 0x10000 if raw16 & 0x8000 else raw16
    # +0x4E: *(short*) = (*(short*)(piVar12+0x4e) - sVar10) + -2   =>  value = (raw - s16) - 2
    v = (sr - S16[i] - 2) & 0xFFFF
    cnt[i] = v
    if fs != M32:
        starts[i] = fs

print("有字段类型 %d / %d" % (len(starts), NT))
print("sum(+0x4E 解码) = %d" % sum(cnt.values()))
print("max(start) = %d" % max(starts.values()))
print("start 唯一值 %d" % len(set(starts.values())))
print()

order = sorted(starts.items(), key=lambda kv: kv[1])
# 差分（末类型无后继，跳过）
ok = bad = 0
badsamples = []
for k in range(len(order) - 1):
    ti, st = order[k]
    nxt = order[k + 1][1]
    diff = nxt - st
    if diff == cnt[ti]:
        ok += 1
    else:
        bad += 1
        if len(badsamples) < 12:
            badsamples.append((ti, st, diff, cnt[ti]))
print("差分 vs +0x4E:  一致 %d   不一致 %d  (%.2f%%)" % (ok, bad, 100.0 * ok / max(ok + bad, 1)))
print()
print("%-8s %-9s %-6s %-6s" % ("typeIdx", "start", "diff", "0x4E"))
for ti, st, diff, c in badsamples:
    print("%-8d %-9d %-6d %-6d" % (ti, st, diff, c))
print()

# 末类型 + 起点重复的类型
dup = len(order) - len(set(starts.values()))
print("起点重复（并列）类型数 = %d" % dup)
print("末类型 start=%d  +0x4E=%d" % (order[-1][1], cnt[order[-1][0]]))
print()
print("=== 用 +0x4E 推算的字段总数 = %d ===" % sum(cnt.values()))
print("=== 差分法字段总数（max start + 末类型 count）= %d ===" % (order[-1][1] + cnt[order[-1][0]]))
