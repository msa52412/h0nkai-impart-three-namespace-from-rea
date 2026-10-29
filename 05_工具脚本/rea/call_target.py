#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""判定「落在 .pdata 空档里的方法地址」是否真的是可调用入口：
   在 ±窗口内扫描 E8/E9 rel32，看是否有调用/跳转精确指向该地址。
   若有 ⇒ 它是真实入口（.pdata 只是未登记）；若无 ⇒ 存疑。
"""
import struct
import sys

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
IB = 0x180000000
d = open(PATH, "rb").read()
WIN = 0x8000


def rva2raw(rva):
    return rva - 0xC00


def callers(target, win=WIN):
    lo = max(0x1000, target - win)
    hi = min(0x6C56000, target + win)
    raw = rva2raw(lo)
    blob = d[raw:raw + (hi - lo)]
    hits = []
    i = 0
    n = len(blob)
    while True:
        j = blob.find(b"\xE8", i)
        if j < 0 or j + 5 > n:
            break
        rel = struct.unpack_from("<i", blob, j + 1)[0]
        src = lo + j
        if src + 5 + rel == target:
            hits.append(("call", src))
        i = j + 1
    i = 0
    while True:
        j = blob.find(b"\xE9", i)
        if j < 0 or j + 5 > n:
            break
        rel = struct.unpack_from("<i", blob, j + 1)[0]
        src = lo + j
        if src + 5 + rel == target:
            hits.append(("jmp", src))
        i = j + 1
    return hits


SAMPLES = [int(a, 16) for a in sys.argv[1:]] or [
    0x1D1FF70, 0x58FBDF0, 0x6031210, 0x6031220, 0x6031230, 0x67AF5D0,
]
for t in SAMPLES:
    h = callers(t)
    print("RVA %08X  窗口 ±%X 内指向它的 call/jmp: %d 个" % (t, WIN, len(h)))
    for kind, src in h[:8]:
        print("    %s 来自 %08X" % (kind, src))
