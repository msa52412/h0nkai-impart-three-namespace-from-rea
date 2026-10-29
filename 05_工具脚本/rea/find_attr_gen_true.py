# -*- coding: utf-8 -*-
"""纠正: 0x7C4F64 数组是 vtable/usage 类数据（ToString/Equals/GetHashCode/Finalize
   ×类型数），非 attr generator。重扫 TYPE 表尾(0x3907FC)..fdv(0x564210) 找
   customAttributeGenerators: 4B/条，值 ∈ {-1} ∪ [0, 408461]，attr ctor 方法号重复出现"""
import struct
from collections import Counter

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
LO, HI = 0x3907FC, 0x564210

# 扫 4B 流: 值 == 0xFFFFFFFF 或 < 408462 的连续 run（>=1000）
best = []
i = LO
run0 = runlen = 0
while i + 4 <= HI:
    v = struct.unpack_from("<I", BUF, i)[0]
    if v == 0xFFFFFFFF or v <= 408461:
        if runlen == 0:
            run0 = i
        runlen += 1
    else:
        if runlen >= 1000:
            best.append((run0, runlen))
        runlen = 0
    i += 4
if runlen >= 1000:
    best.append((run0, runlen))
best.sort(key=lambda x: -x[1])
print("候选 run:")
for a, L in best[:5]:
    print("  0x%X 长 %d (%.1f%% of 408461)" % (a, L, 100.0 * L / 408461))

if best:
    S, L = best[0]
    vals = [struct.unpack_from("<I", BUF, S + k * 4)[0] for k in range(min(L, 500000))]
    c = Counter(v for v in vals if v != 0xFFFFFFFF)
    print("\n首 12:", vals[:12])
    print("最常见值 top8:", c.most_common(8))
    print("-1 占比: %.1f%%" % (100.0 * sum(1 for v in vals if v == 0xFFFFFFFF) / len(vals)))
