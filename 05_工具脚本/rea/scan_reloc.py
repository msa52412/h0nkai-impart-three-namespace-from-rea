#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析 .reloc，寻找「等距 8 字节的 DIR64 重定位游程」
= 静态指针数组所在区域。若存在 408,461 长的游程，即为方法指针表。
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
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

print("文件大小 %.1f MB" % (len(d) / 1048576.0))

relsecs = [(nm, va, rs, rp) for nm, va, vs, rs, rp in SECS if nm == ".reloc"]
print("reloc 段数 =", len(relsecs))

allrel = []   # (rva_delta, type)
for nm, va, rs, rp in relsecs:
    p = rp
    end = rp + rs
    while p + 8 <= end:
        page, blk = struct.unpack_from("<II", d, p)
        if blk < 8 or p + blk > end:
            break
        nent = (blk - 8) // 2
        for k in range(nent):
            w = struct.unpack_from("<H", d, p + 8 + k * 2)[0]
            typ = w >> 12
            off = w & 0xFFF
            allrel.append((page + off, typ))
        p += blk

print("重定位总数 = %d" % len(allrel))
from collections import Counter
print("类型分布 =", Counter(t for _, t in allrel).most_common(6))

# 按类型 10 (DIR64) 提取，找等距 8 游程
dir64 = sorted(set(r for r, t in allrel if t == 10))
print("DIR64 槽位数 = %d" % len(dir64))

runs = []
st = 0
for i in range(1, len(dir64) + 1):
    if i == len(dir64) or dir64[i] - dir64[i - 1] != 8:
        ln = i - st
        if ln >= 32:
            runs.append((dir64[st], ln))
        st = i
runs.sort(key=lambda x: -x[1])
print("\n等距 8 的 DIR64 游程（长度>=32），前 12 段：")
for off, ln in runs[:12]:
    print("  RVA=0x%08X  VA=0x%X  条数=%d" % (off, IB + off, ln))
print("游程总条数 =", len(runs), " 合计槽位 =", sum(r[1] for r in runs))
