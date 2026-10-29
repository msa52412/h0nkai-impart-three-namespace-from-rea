# -*- coding: utf-8 -*-
"""找 customAttributeStarter 范围表：~76,738 个单调 uint32（0..780,235）
   4B 步长纯 start 数组；扫全文件未归属区"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
N = len(BUF)
LIM = 780235

best = (0, 0)
i = 0x118
run0 = runlen = 0
prev = -1
while i + 4 <= N:
    v = struct.unpack_from("<I", BUF, i)[0]
    if prev <= v <= LIM:
        if runlen == 0:
            run0 = i
        runlen += 1
        prev = v
        if runlen > best[1]:
            best = (run0, runlen)
    else:
        runlen = 0
        prev = -1
    i += 4
print("最长单调(<=780235) run: @0x%X 长 %d" % best)
S = best[0]
print("首 12:", struct.unpack_from("<12I", BUF, S))
print("尾 4:", struct.unpack_from("<4I", BUF, S + (best[1]-4)*4))
