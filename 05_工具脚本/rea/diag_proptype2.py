#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""属性 type 列：按汇编精确公式重算，并按已知类型反推偏移"""
import struct
import csv

M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
BASE = 0x118
TP = 0x1C6766C
BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()


def prfP(i):
    t = ((i * 0x64D5) & M64) ^ 0x6D7B1F20
    t = (t + 0x10ECA71E) & M64
    t = (t * 0x7737C996) & M64
    return (((t >> 8) & M32) + 0x5505FF6B) & M32


NAMEK = 0xEACB0307


def payload(gi):
    o = BASE + TP + gi * 0x14
    p0, p1, p2, p3, p4 = struct.unpack_from("<5I", BUF, o)
    m = (prfP(gi) * NAMEK) & M32
    v = (p2 + m) & M32                 # rec2 - EBP
    return v, ((v - 0x6F268466) & M32)


print("[1] 全表 payload 高位分布")
hi = {}
for gi in range(56137):
    v, pre = payload(gi)
    k = pre >> 24
    hi[k] = hi.get(k, 0) + 1
for k in sorted(hi, key=lambda x: -hi[x])[:8]:
    print("    top byte 0x%02X : %d 条" % (k, hi[k]))

print("\n[2] 末 8 条")
for gi in range(56129, 56137):
    v, pre = payload(gi)
    print("    gi=%d  rec2-EBP=%08X  pre-xor=%08X  fin=%08X" % (gi, v, pre, pre ^ 0x79F46A96))

print("\n[3] 已知属性定位 (System.String)")
rows = list(csv.DictReader(open(r"D:\Carol-start\_rea\bh3_properties.tsv", encoding="utf-8"), delimiter="\t"))
sub = [r for r in rows if r["typeName"] == "System.String"]
for r in sub:
    gi = int(r["propIdx"])
    v, pre = payload(gi)
    print("    %-10s gi=%-6s rec2-EBP=%08X pre-xor=%08X fin=%08X get=%s" %
          (r["propName"], gi, v, pre, pre ^ 0x79F46A96, r["getIdx"]))

print("\n[4] 若 pre-xor 是 ~idx 的补：idx = -pre ?")
for gi in (0, 1, 2, 100, 5000):
    v, pre = payload(gi)
    print("    gi=%-6d  -pre=%08X  pre^0x79f46a96=%08X" % (gi, (-pre) & M32, pre ^ 0x79F46A96))
