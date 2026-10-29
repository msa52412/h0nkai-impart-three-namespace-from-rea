#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量提取方法名表（0xFA8318，步长 0x20，索引 i 的 PRF 反扰动）。

连续 STREAK 条失败即判定表尾。
"""
import struct
import sys

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT = r"D:\Carol-start\_rea\bh3_methods.txt"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x20
STREAK = 300
MAXI = 700000

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
TBL_OFF = (u32va(0x188198E58) - 0x017A3B99) & M32
K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)
POOL_ABS = BASE + POOL_OFF
TBL_ABS = BASE + TBL_OFF
_U64 = struct.Struct("<Q")

# 预计算 PRF（64 位）
PRF = []
for i in range(MAXI + 1):
    x = ((i * 0xB069) ^ 0x3E382F2D) & M64
    x = (x * 0x24147491) & M64
    x = (x ^ 0xF997B4A800) >> 10
    x = (x * 0x3857AACA) & M64
    PRF.append(x >> 0xE)

cache = {}


def decrypt_str(pid):
    s = cache.get(pid)
    if s is not None:
        return s
    length = (pid >> 24) & 0xFF
    if length == 0:
        cache[pid] = ""
        return ""
    if length > 0x100:
        cache[pid] = None
        return None
    index = pid & 0xFFFFFF
    src = POOL_ABS + index
    nb = (length + 7) >> 3
    if src + nb * 8 > FSIZE:
        cache[pid] = None
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
        cache[pid] = None
        return None
    for ch in s:
        o = ord(ch)
        if o < 0x20 or o == 0x7F:
            cache[pid] = None
            return None
    cache[pid] = s
    return s


rows = []
streak = 0
end_i = 0
for i in range(MAXI):
    off = TBL_ABS + i * STEP
    if off + STEP > FSIZE:
        print("到达文件末尾 i=%d" % i)
        break
    raw_id = struct.unpack_from("<I", BUF, off + 0x0C)[0]
    flag = BUF[off + 0x1C]
    p = PRF[i]
    pid = (raw_id ^ p ^ 0x1D64B276) & M32
    s = decrypt_str(pid)
    if s:
        rows.append((i, pid, flag, s))
        streak = 0
        end_i = i
    else:
        streak += 1
        if streak >= STREAK:
            print("连续 %d 条失败，判定表尾 i=%d" % (STREAK, i))
            break
    if i and i % 50000 == 0:
        print("  ... i=%d, 已解 %d 条, 缓存 %d" % (i, len(rows), len(cache)), flush=True)

print("\n方法表条数: %d (最大索引 %d)" % (len(rows), end_i))
print("不同方法名: %d" % len(set(s for _, _, _, s in rows)))

with open(OUT, "w", encoding="utf-8") as f:
    for i, pid, flag, s in rows:
        f.write("%d\t%08X\t%02X\t%s\n" % (i, pid, flag, s))
print("写出 %s" % OUT)

from collections import Counter
c = Counter(s for _, _, _, s in rows)
print("\n--- 出现次数最多的 30 个方法名 ---")
for k, n in c.most_common(30):
    print("  %-45s %5d" % (k, n))

print("\n--- 最长的 20 个 ---")
for s in sorted(set(s for _, _, _, s in rows), key=len, reverse=True)[:20]:
    print("  (%3d) %s" % (len(s), s))
