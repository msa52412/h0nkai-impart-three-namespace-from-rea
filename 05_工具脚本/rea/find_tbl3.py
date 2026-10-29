#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定位表3（408,458 × 8 字节）

思路：若表3 是方法指针数组，DLL 内应存在一段长游程的 u64 全部落在 .text 区间。
     扫描全 DLL，输出所有长度 >= 1000 的游程。
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
    name = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((name, IB + va, IB + va + max(vs, rs), rp, rp + rs))
    print("SEC %-10s VA=[0x%X,0x%X) off=[0x%X,0x%X)" % (name, IB + va, IB + va + max(vs, rs), rp, rp + rs))

# .text 判定区间
TXT_LO, TXT_HI = IB + 0x1000, IB + 0x52D800
print("\n.text VA = [0x%X, 0x%X)" % (TXT_LO, TXT_HI))

# 遍历所有可读区段内的 8 字节对齐位置
runs = []
for name, lo, hi, rp, rend in SECS:
    if rend <= rp or rend - rp < 8:
        continue
    start = None
    n = (rend - rp) // 8
    for i in range(n):
        v = struct.unpack_from("<Q", d, rp + i * 8)[0]
        if TXT_LO <= v < TXT_HI:
            if start is None:
                start = i
        else:
            if start is not None and i - start >= 1000:
                runs.append((name, i - start, rp + start * 8, IB + 0))
            start = None
    if start is not None and n - start >= 1000:
        runs.append((name, n - start, rp + start * 8, 0))

print("\n=== 长度 >= 1000 的 .text 指针游程 ===")
for name, cnt, off, _ in sorted(runs, key=lambda x: -x[1])[:20]:
    print("  %-8s 条数=%-8d 文件偏移=0x%08X" % (name, cnt, off))

print("\n表3 目标条数 = 408,458")
for name, cnt, off, _ in runs:
    if abs(cnt - 408458) < 5000:
        print("  *** 候选: %s 条数=%d 偏移=0x%X (差 %d)" % (name, cnt, off, cnt - 408458))
