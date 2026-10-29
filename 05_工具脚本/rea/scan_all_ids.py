#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全文件扫描打包字符串 ID（无步长假设）。

预筛（廉价，纯整数运算）：
    length = v >> 24          要求 2..120
    index  = v & 0xFFFFFF     要求 < 池大小
    解密第一个 8 字节块，前 min(length,8) 字节必须全可打印
通过后再完整解密验证。

输出所有命中位置，按 4KB 桶统计，聚集区即为 ID 数组所在。
"""
import array
import struct
import sys
import time

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT_ALL = r"D:\Carol-start\_rea\bh3_all_ids.txt"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
CHUNK = 4 << 20

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
POOL_SIZE = FSIZE - POOL_ABS

print("文件 %d 字节, 池起点 0x%X, 池可用 %d 字节" % (FSIZE, POOL_ABS, POOL_SIZE), flush=True)

_U64 = struct.Struct("<Q")


def full_decrypt(pid):
    length = (pid >> 24) & 0xFF
    index = pid & 0xFFFFFF
    if length < 2 or length > 120:
        return None
    src = POOL_ABS + index
    nb = (length + 7) >> 3
    if src + nb * 8 > FSIZE:
        return None
    key = (index * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        c = _U64.unpack_from(BUF, src + b * 8)[0]
        out += (c ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    cand = out[:length]
    try:
        s = cand.decode("utf-8")
    except UnicodeDecodeError:
        return None
    for ch in s:
        o = ord(ch)
        if o < 0x20 or o == 0x7F:
            return None
    return s


def quick_ok(pid):
    """廉价预筛：只解第一块"""
    ln = pid >> 24
    if ln < 2 or ln > 120:
        return False
    idx = pid & 0xFFFFFF
    src = POOL_ABS + idx
    if src + 8 > FSIZE:
        return False
    key = (idx * K_MUL + K_ADD) & M64
    plain = _U64.unpack_from(BUF, src)[0] ^ key
    b = plain.to_bytes(8, "little")
    n = ln if ln < 8 else 8
    for i in range(n):
        c = b[i]
        if not (0x20 <= c <= 0x7E or c >= 0x80):
            return False
    return True


hits = []          # (file_offset, pid, string)
cache = {}
t0 = time.time()
scanned = 0
cands = 0

for start in range(0, FSIZE - 4, CHUNK):
    end = min(start + CHUNK, FSIZE)
    chunk = BUF[start:end]
    usable = (len(chunk) // 4) * 4
    arr = array.array("I")
    arr.frombytes(chunk[:usable])
    base = start
    for i, v in enumerate(arr):
        scanned += 1
        ln = v >> 24
        if ln < 2 or ln > 120:
            continue
        if (v & 0xFFFFFF) >= POOL_SIZE:
            continue
        cands += 1
        if v in cache:
            s = cache[v]
        else:
            s = full_decrypt(v) if quick_ok(v) else None
            cache[v] = s
        if s:
            hits.append((base + i * 4, v, s))
    if start % (16 << 20) == 0:
        print("  ... 0x%X  扫描 %d 候选 %d 命中 %d  (%.0fs)" %
              (start, scanned, cands, len(hits), time.time() - t0), flush=True)

print("\n扫描完成: %d 个 int32, %d 个候选, %d 个命中 (%.1fs)" %
      (scanned, cands, len(hits), time.time() - t0))

# 按 4KB 桶统计聚集
from collections import Counter
buckets = Counter((off >> 12) << 12 for off, _, _ in hits)
print("\n命中密度最高的 25 个 4KB 桶:")
for b, c in buckets.most_common(25):
    print("  0x%08X  %d 命中" % (b, c))

with open(OUT_ALL, "w", encoding="utf-8") as f:
    for off, pid, s in hits:
        f.write("%08X\t%08X\t%s\n" % (off, pid, s))
print("\n写出 %s (%d 条)" % (OUT_ALL, len(hits)))

print("\n--- 前 40 条 ---")
for off, pid, s in hits[:40]:
    print("  0x%08X  id=%08X  %s" % (off, pid, s))
