# -*- coding: utf-8 -*-
"""扫 attribute 数据表本体：
   形态 A: customAttributeStarter {start, count} 8B 对，start ∈ [0, 28071)
   形态 B: 加密表 —— 用 attr 总数 28070 在全局簇找条数编码
   先扫明文形态 A"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
N = len(BUF)
N_ATTR = 28071   # start 末值 28070 + 1

# 形态 A: 8B {start, count}, start 严格递增 < 28071, count 小
print("扫 {start<28071 递增, count 小} run...")
results = []
i = 0x118
run0 = runlen = 0
prev_s = -1
while i + 8 <= N:
    s, c = struct.unpack_from("<2I", BUF, i)
    if s > prev_s and s < N_ATTR and c <= 2000 and (s + c) <= N_ATTR:
        if runlen == 0:
            run0 = i
            prev_s = -1
            s0, _ = struct.unpack_from("<2I", BUF, run0)
            prev_s = s0
        runlen += 1
        prev_s = s
        i += 8
    else:
        if runlen >= 50:
            results.append((run0, runlen))
        runlen = 0
        i += 8
if runlen >= 50:
    results.append((run0, runlen))
results.sort(key=lambda x: -x[1])
for a, L in results[:6]:
    first = struct.unpack_from("<2I", BUF, a)
    print("  0x%X 长 %d 对, 首 (%d,%d) 末 (%d,%d)" %
          (a, L, first[0], first[1], *struct.unpack_from("<2I", BUF, a + (L-1)*8)))