#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""由「指针数组簇」反查持有它的模块描述符，读出 (条数, 指针) 对。

已定位 .data(raw 0x8D08800 起, VA 0x8D0A000) 内有 12 个代码指针簇，
合计 409,142 条 ≈ 方法总数 408,458 + 684。逐个簇找 8 字节引用者，
再读引用者前后的 u32 字段，确认是否是 {count, methodPointers} 结构。
"""
import struct

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
IB = 0x180000000
DATA_RAW = 0x8D08800
DATA_VA = 0x8D0A000
LO = 0x180001000
HI = 0x186C56000

d = open(PATH, "rb").read()


def va_of(raw):
    if raw >= DATA_RAW:
        return IB + DATA_VA + (raw - DATA_RAW)
    if raw >= 0x6C54800:
        return IB + 0x6C56000 + (raw - 0x6C54800)
    return IB + 0x1000 + (raw - 0x400)


CLUSTERS = [
    0x8D85240, 0x8F27690, 0x8D08958, 0x98F3E28, 0x912B2D8, 0x9886B80,
    0x98C5718, 0x9857CF8, 0x98B51F8, 0x9931C60, 0x98802C0, 0x98F0B30,
]

print("%-10s %-14s %-8s %s" % ("簇raw", "簇VA", "引用数", "引用点"))
for c in CLUSTERS:
    va = va_of(c)
    pat = struct.pack("<Q", va)
    hits = []
    i = -1
    while True:
        i = d.find(pat, i + 1)
        if i < 0:
            break
        hits.append(i)
    print("%08X   %012X   %-8d %s" % (c, va, len(hits), [hex(h) for h in hits[:4]]))
    for h in hits[:2]:
        print("        引用点 raw %08X 前后 0x30:" % h)
        for k in range(-6, 7):
            o = h + k * 4
            if o < 0:
                continue
            u = struct.unpack_from("<I", d, o)[0]
            q = struct.unpack_from("<Q", d, o)[0]
            tag = ""
            if IB + LO - IB <= q < IB + (HI - IB):
                tag = "  <-codeptr"
            print("           %+4d %08X  u32=%-12d %016X%s" % (k * 4, o, u, q, tag))
    print()
