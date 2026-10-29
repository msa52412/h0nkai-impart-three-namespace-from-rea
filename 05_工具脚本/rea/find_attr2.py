# -*- coding: utf-8 -*-
"""找 customAttributeIndexRange：8B 对 {start, count}，start 递增、count 小
   及 customAttributeStarter pairs。同时检查剩余未归属段"""
import struct
from collections import Counter

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
N = len(BUF)

# 已归属段（绝对地址）
known = [
    (0x118, 0x513B8, "E3C-iface索引"),
    (0x513B8, 0x513B8 + 57487 * 76, "TYPE(0x4C/条?)"),  # 长度未知，占位
    (0xEC7724, 0x7C4F64, "fdv表"),
    (0x7C4F64, 0xAC1050, "???"),
]

# 全库扫 8B 对 {a,b}: a 严格递增, b in [0,1000], run >= 1000
print("扫 {start递增, count小} 的 8B run...")
i = 0x118
best = []
run0 = 0
runlen = 0
prev_a = -1
while i + 8 <= N:
    a, b = struct.unpack_from("<2I", BUF, i)
    if a > prev_a and b <= 1000:
        if runlen == 0:
            run0 = i
            prev_a = -1
            a2, _ = struct.unpack_from("<2I", BUF, run0)
            prev_a = a2
        runlen += 1
        prev_a = a
        i += 8
    else:
        if runlen >= 1000:
            best.append((run0, runlen))
        runlen = 0
        i += 8
if runlen >= 1000:
    best.append((run0, runlen))
best.sort(key=lambda x: -x[1])
for a, L in best[:8]:
    print("  0x%X 长 %d 对, 首 %s" % (a, L, struct.unpack_from("<2I", BUF, a)))
