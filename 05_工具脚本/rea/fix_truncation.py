#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正长度：不再用"最长可打印"（会粘垃圾字符），改用频次统计。

原理：
  同一个 index 在文件里可能出现多次，但只有真实 length 会高频出现
  （因为 ID 数组里同一个字符串 ID 会重复引用）；偶然命中产生的
  length 是随机分布的。所以取每个 index 的 length 众数。
"""
import re
import struct
from collections import defaultdict, Counter

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
INP = r"D:\Carol-start\_rea\bh3_all_ids.txt"
OUT = r"D:\Carol-start\_rea\bh3_strings_final.txt"

BASE = 0x118
M64 = (1 << 64) - 1

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
_U64 = struct.Struct("<Q")


def decrypt_at(idx, length):
    src = POOL_ABS + idx
    nb = (length + 7) >> 3
    if src + nb * 8 > FSIZE:
        return None
    key = (idx * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        c = _U64.unpack_from(BUF, src + b * 8)[0]
        out += (c ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    return bytes(out[:length])


# 收集 (index -> length 频次)
freq = defaultdict(Counter)
with open(INP, encoding="utf-8") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) != 3:
            continue
        pid = int(p[1], 16)
        idx = pid & 0xFFFFFF
        length = pid >> 24
        freq[idx][length] += 1

print("唯一 index: %d" % len(freq))

ALLOWED = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_<>`[]-.+:/ ")


def ok_bytes(b):
    if not b:
        return False
    for c in b:
        if c >= 0x80 or c not in ALLOWED:
            return False
    return True


final = {}
confident = 0
for idx, counter in freq.items():
    if not counter:
        continue
    # 1) 最长全合法长度
    lmax = None
    smax = None
    for length in range(120, 3, -1):
        b = decrypt_at(idx, length)
        if b and ok_bytes(b):
            lmax = length
            smax = b.decode("ascii")
            break
    if lmax is None:
        continue

    # 2) 频次众数长度
    top_count = max(counter.values())
    cands = sorted([l for l, c in counter.items() if c == top_count], reverse=True)
    lmode = None
    smode = None
    for length in cands:
        b = decrypt_at(idx, length)
        if b and ok_bytes(b):
            lmode = length
            smode = b.decode("ascii")
            break

    # 3) 若众数版是最长版的前缀且差距很小，说明最长版尾部粘了垃圾 -> 取众数版
    chosen = smax
    if lmode and smode and smax.startswith(smode) and 0 <= (lmax - lmode) <= 2:
        chosen = smode
        confident += 1

    if len(chosen) >= 5:
        final[idx] = chosen

print("还原: %d 条 (其中用众数修正掉尾巴: %d)" % (len(final), confident))

# 过滤：含分隔符或驼峰
IDENT = re.compile(r"^[A-Za-z_<\[][A-Za-z0-9_<>`\[\].\-+:/ ]*$")


def good(s):
    if not IDENT.match(s):
        return False
    if len(s) < 6:
        return False
    has_sep = any(c in s for c in "-_<>`[].")
    has_camel = re.search(r"[a-z][A-Z]", s) is not None
    return has_sep or has_camel


kept = {i: s for i, s in final.items() if good(s)}
print("过滤后: %d" % len(kept))

with open(OUT, "w", encoding="utf-8") as f:
    for idx in sorted(kept):
        f.write("%06X\t%s\n" % (idx, kept[idx]))

three = [s for s in kept.values() if s.startswith("MoleMole") and s.count("-") >= 2]
print("米哈游三段式: %d" % len(three))

print("\n--- 前 25 条 ---")
for idx in sorted(kept)[:25]:
    print("  %06X  %s" % (idx, kept[idx]))

print("\n--- 最长的 15 条 ---")
for s in sorted(kept.values(), key=len, reverse=True)[:15]:
    print("  (%3d) %s" % (len(s), s))
