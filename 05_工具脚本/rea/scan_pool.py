#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描 BH3 global-metadata.dat 加密字符串池，按关键词提取字符串。

原理（见 bh3_meta_decrypt.py）:
  字符串池明文从 BASE+POOL_OFF 开始；起始下标 index 的密钥
      key(index) = index*K_MUL + K_ADD  (mod 2^64)
  每个 8 字节块 plain = cipher ^ key，块间 key += K_STEP。

扫描策略: 对每个可能的下标 index，试解一个块；若 8 字节全可打印则
继续解到不可打印为止，得到一个候选字符串。再按关键词过滤。
"""
import struct, sys, json, os, time

META = r"D:\BH3\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
M64 = (1 << 64) - 1
BASE = 0x118
POOL_OFF = 0x024AAC18
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6
IDX_MAX = 0xFFFFFF

BUF = open(META, "rb").read()
FSIZE = len(BUF)
POOL_START = BASE + POOL_OFF
print("metadata %d B, 池起点 0x%X, 可用 %d B" % (FSIZE, POOL_START, FSIZE - POOL_START))


def printable8(off, key):
    c = struct.unpack_from("<Q", BUF, off)[0]
    p = c ^ key
    b = struct.pack("<Q", p)
    for ch in b:
        if ch < 0x20 or ch > 0x7E:
            return None
    return b


def full(off, key, maxlen=160):
    out = bytearray()
    k = key
    while len(out) < maxlen and off + 8 <= FSIZE:
        c = struct.unpack_from("<Q", BUF, off)[0]
        b = struct.pack("<Q", c ^ k)
        for ch in b:
            if ch < 0x20 or ch > 0x7E:
                return out.decode("ascii", "replace")
            out.append(ch)
        off += 8
        k = (k + K_STEP) & M64
    return out.decode("ascii", "replace")


KEYS = sys.argv[1:] or ["PageContext", "StubPage", "Task_", "OpenWorld", "SinDemonEx"]

t0 = time.time()
hits = []
key = (0 * K_MUL + K_ADD) & M64
limit = min(IDX_MAX, FSIZE - POOL_START - 8)
cnt = 0
for index in range(0, limit):
    off = POOL_START + index
    if printable8(off, key) is not None:
        s = full(off, key)
        if any(k in s for k in KEYS):
            hits.append((index, s))
            cnt += 1
            if cnt % 200 == 0:
                print("  ... %d 命中, 已扫 %d (%.1fs)" % (cnt, index, time.time() - t0), flush=True)
    key = (key + K_MUL) & M64

print("\n扫描完成 %.1fs, 命中 %d" % (time.time() - t0, len(hits)))
out = r"D:\Carol-start\_rea\meta_pool_hits.txt"
with open(out, "w", encoding="utf-8") as f:
    for idx, s in hits:
        f.write("%08X\t%s\n" % (idx, s))
print("[+] " + out)

# 摘要：只看包含 PageContext 的
seen = set()
for idx, s in hits:
    if "PageContext" in s or "StubPage" in s:
        k = s.strip()
        if k in seen:
            continue
        seen.add(k)
        print("  0x%06X  %s" % (idx, k[:90]))
