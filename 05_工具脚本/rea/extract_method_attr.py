# -*- coding: utf-8 -*-
"""方法表 attribute 列（+0x14）全解：
   attrIdx = ((raw + 0xBD6FC398) ^ PRF[i]) & 0xFFFFFF   [1 基，0=无]
   PRF = ((i*0xB069 ^ 0x3E382F2D)*0x24147491 ^ 0x3E65ED2A)*0x3857AACA >> 0xE
   （PRF 已在 extract_methods.py 验证 —— 名字列同源）
   期望：非零条数 ≤ 76,737（attr 总数），且与 T5 c1/c2 范围咬合"""
import struct
from collections import Counter

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
TBL = 0x118 + 0xFA8318
STEP = 0x20
N_METH = 408461

def prf(i):
    x = ((i * 0xB069) ^ 0x3E382F2D) & M64
    x = (x * 0x24147491) & M64
    x = (x ^ 0xF997B4A800) >> 10
    x = (x * 0x3857AACA) & M64
    return x >> 0xE

vals = Counter()
n_zero = n_over = 0
max_seen = 0
dist = Counter()
for i in range(N_METH):
    raw = struct.unpack_from("<I", BUF, TBL + i * STEP + 0x14)[0]
    idx = ((raw + 0xBD6FC398) & M32 ^ prf(i)) & 0xFFFFFF
    if idx == 0:
        n_zero += 1
    elif idx > 76737:
        n_over += 1
    else:
        vals[idx] += 1
        max_seen = max(max_seen, idx)
print("方法 %d: 无attr %d, 越界(>76737) %d, 有效 %d, 最大 idx %d"
      % (N_METH, n_zero, n_over, sum(vals.values()), max_seen))
print("idx 分布（前 12）:", sorted(vals)[:12])
print("idx 唯一值数:", len(vals))
# 有效 idx 的直方图（1..76737 均匀度）
top = vals.most_common(5)
print("重复最多的 idx:", top)
PYEOF = None
