# -*- coding: utf-8 -*-
"""T5 (images) 列语义修正：
   代码证据：尾循环用 r[8]+0x14(缓存) 作 start、r[4]+0x1C 作 count，
   迭代 0x5C 步长记录（=类型定义表，E78=0x50B364=57487×92 恰为表长）
   → c8=typeStart, c4=typeCount。
   剩余候选列里找 customAttributeStart/Count：c1 差分疑似 = c2，全 192 镜像验证"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
T5 = 0x118 + 0x1C2A198
N = 192

def ikey(i):
    v = (i * 0x14C3BD9234D3) & M64
    v >>= 9
    v = (v + 0x48C65E21) & M64
    v = (v * 0x22343DDF) & M64
    v >>= 0x15
    return v & M32

cols = {j: [] for j in range(10)}
for i in range(N):
    r = struct.unpack_from("<10I", BUF, T5 + i * 0x28)
    k = ikey(i)
    # 按初始化代码精确解（缓存读取时才减的常量此处不重复加减）：
    cols[0].append((r[0] - 0x36D7455A - k) & M32)
    cols[1].append((r[1] - k) & M32)                       # 缓存里 +0x1298B083 是存储态
    cols[2].append((r[2] - 0x3B4B92FD - k) & M32)
    cols[3].append((r[3] - k - 0x3640F13B) & M32)
    cols[4].append((r[4] - 0x7C293E16 - k) & M32)          # typeCount
    cols[6].append((r[6] - 0x12813D35 - k) & M32)          # assemblyIdx
    cols[7].append(((r[7] ^ 0x16A0E2A5) - k) & M32)
    cols[8].append((r[8] - 0x3D2E6FE3 - k) & M32)          # typeStart
    cols[9].append(((r[9] ^ 0x0CA5B561) - k) & M32)

# 1) c1 差分 == c2 ?
match = sum(1 for i in range(191) if (cols[1][i+1] - cols[1][i]) & M32 == cols[2][i])
print("c1[i+1]-c1[i] == c2[i]: %d / 191" % match)
print("c1 前 6:", cols[1][:6])
print("c2 前 6:", cols[2][:6])
print("c1 单调:", all(cols[1][i] <= cols[1][i+1] for i in range(191)))
total_attr = (cols[1][191] - cols[1][0]) + cols[2][191]
print("attr 总数 = c1[末]-c1[0]+c2[末] = %d  (sum(c2)=%d)" % (total_attr, sum(cols[2])))

# 2) typeStart 拼接验证（应有空洞）
gaps = [(i, cols[8][i], cols[4][i]) for i in range(191)
        if cols[8][i] + cols[4][i] != cols[8][i+1]]
print("typeStart 不严格拼接的边界: %d 处（前 5: %s）" %
      (len(gaps), [(g[0], g[1], g[1]+g[2]) for g in gaps[:5]]))

# 3) 其余列形态
for j in (0, 3, 7, 9):
    v = cols[j]
    print("c%d: 前6=%s  唯一值数=%d" % (j, v[:6], len(set(v))))
