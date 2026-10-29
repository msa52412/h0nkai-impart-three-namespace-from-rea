#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在加密字符串池里按明文前缀暴力匹配（不受长度限制）。"""
import struct, sys, time

META = r"D:\BH3\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
M64 = (1 << 64) - 1
BASE = 0x118
POOL_OFF = 0x024AAC18
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

BUF = open(META, "rb").read()
FSIZE = len(BUF)
POOL_START = BASE + POOL_OFF
LIMIT = min(0xFFFFFF, FSIZE - POOL_START - 8)

targets = [t.encode() for t in (sys.argv[1:] or ["Task_", "Task_1", "Task_3"])]
maxlen = max(len(t) for t in targets)
print("搜索:", [t.decode() for t in targets])

t0 = time.time()
key = K_ADD
hits = {t: [] for t in targets}
for index in range(LIMIT):
    off = POOL_START + index
    c = struct.unpack_from("<Q", BUF, off)[0]
    b = struct.pack("<Q", c ^ key)
    for t in targets:
        if b[:len(t)] == t:
            hits[t].append(index)
    key = (key + K_MUL) & M64

print("耗时 %.1fs" % (time.time() - t0))
for t in targets:
    hs = hits[t]
    print("%-10s 命中 %d  %s" % (t.decode(), len(hs), ["0x%06X" % h for h in hs[:8]]))
