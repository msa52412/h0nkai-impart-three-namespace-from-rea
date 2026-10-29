#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描 global-metadata.dat 字符串池（快速版）。

优化：一次解密 BLOCKS 个 8 字节块，取第一个 \0 作为长度。
  理由：正确长度 len 一定满足 len < nblocks*8，而池里下一个字符串
  从 nblocks*8 开始、用不同的 key。所以第一个 \0 必然落在正确区内。
"""
import struct
import sys

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT = r"D:\Carol-start\_rea\bh3_strings_pool.txt"

BASE = 0x118
M64 = (1 << 64) - 1
BLOCKS = 48                     # 一次解密 384 字节
SCAN_LIMIT = 4 * 1024 * 1024    # 最多扫 4 MB 池

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
            if rsize == 0:
                return None
            return struct.unpack_from("<I", dll, rptr + (rva - vaddr))[0]
    return None


POOL_OFF = u32va(0x188198E50) ^ 0x7483FF7A
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
POOL_ABS = BASE + POOL_OFF

print("pool 绝对偏移 = 0x%X, 文件大小 = 0x%X" % (POOL_ABS, FSIZE), flush=True)
print("可扫范围 = %d 字节, 上限 %d" % (FSIZE - POOL_ABS, SCAN_LIMIT), flush=True)

PACK = struct.Struct("<%dQ" % BLOCKS)
LIMIT = min(FSIZE - POOL_ABS, SCAN_LIMIT) - BLOCKS * 8


def try_at(idx):
    """返回 (length, string) 或 None"""
    ciphers = PACK.unpack_from(BUF, POOL_ABS + idx)
    key = (idx * K_MUL + K_ADD) & M64
    out = bytearray()
    for c in ciphers:
        out += (c ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    p = out.find(0)
    if p <= 0 or p > 200:
        return None
    cand = out[:p]
    try:
        s = cand.decode("utf-8")
    except UnicodeDecodeError:
        return None
    for ch in s:
        o = ord(ch)
        if o < 0x20 or o == 0x7F:
            return None
    return p, s


results = []
idx = 0
misses = 0
step_report = 0x8000

while idx < LIMIT:
    r = try_at(idx)
    if r:
        length, s = r
        nblocks = (length + 7) >> 3
        results.append((idx, s))
        idx += nblocks * 8
        misses = 0
    else:
        idx += 8
        misses += 1
        if misses > 3000:
            print("连续 %d 个位置未命中，在 0x%X 处停止" % (misses, idx), flush=True)
            break
    if idx >= step_report:
        print("  ... 0x%X, 已解 %d 条" % (idx, len(results)), flush=True)
        step_report += 0x8000

print("总计解出 %d 条字符串，覆盖到 index 0x%X" % (len(results), idx), flush=True)

with open(OUT, "w", encoding="utf-8") as f:
    for i, s in results:
        f.write("%08X\t%s\n" % (i, s))
print("写出 %s" % OUT, flush=True)

print("\n--- 前 30 条 ---")
for i, s in results[:30]:
    print("  %08X  %s" % (i, s))

print("\n--- 抽样：Unity/System 相关 15 条 ---")
n = 0
for i, s in results:
    if ("Unity" in s or "System" in s or "Game" in s) and n < 15:
        print("  %08X  %s" % (i, s))
        n += 1
