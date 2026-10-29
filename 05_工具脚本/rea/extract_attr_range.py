# -*- coding: utf-8 -*-
"""CustomAttribute 范围表（E7C）全解：
   表基 = E7C ^ 0x2A721817 + metadata
   条数 = E54 ^ 0x6A0BFD5D
   每条 12B，扫描匹配: matchVal = ((方法表[i]+0x14 处 + 0xEA530370) ^ PRF[i])
   即 col0 = attrIdx（owner 的 attr 起始，1 基）—— attrIdx 已知可直接对照！
   col1/col2 = ? (count / dataOffset?)"""
import struct
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")
from probe_thunk import PE

pe = PE(r"D:\Carol-start\_rea\UserAssembly_slim.dll")
BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF

raw_e7c = struct.unpack_from("<I", pe.d, pe.va2off(0x188198E7C))[0]
raw_e54 = struct.unpack_from("<I", pe.d, pe.va2off(0x188198E54))[0]
SEG = raw_e7c ^ 0x2A721817
N = raw_e54 ^ 0x6A0BFD5D
TBL = 0x118 + SEG
print("E7C 表: 段偏移 0x%X → 表基 0x%X, 条数 %d (12B/条 → 0x%X 字节)" % (SEG, TBL, N, N * 12))

# dump 前 10 条
for i in range(10):
    r = struct.unpack_from("<3I", BUF, TBL + i * 12)
    print("  [%d] col0=%-8d col1=%-8d col2=0x%08X" % (i, r[0], r[1], r[2]))
print("表尾后 16B:", BUF[TBL + N*12:TBL + N*12 + 16].hex(" "))

# 已知方法0 attrIdx=1: col0 应含 1
found = [(i, r) for i in range(min(N, 2000)) for r in [struct.unpack_from("<3I", BUF, TBL + i*12)] if r[0] == 1]
print("col0==1 的前 2 条:", found[:2])
