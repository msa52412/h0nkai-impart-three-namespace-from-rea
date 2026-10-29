# -*- coding: utf-8 -*-
"""方法记录剩余列：+0x10（-1 哨兵）、+0x18 flags、+0x1C slot、+0x1E paramCount。"""
import struct
import collections

M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
BASE = 0x118
T = 0xFA8318
N = 408458          # 去掉末尾 3 条填充

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
PRF = []
for i in range(N):
    x = ((i * 0xB069) ^ 0x3E382F2D) & M64
    x = (x * 0x24147491) & M64
    x = (x ^ 0xF997B4A800) >> 10
    x = (x * 0x3857AACA) & M64
    PRF.append((x >> 0xE) & M32)


def u32(i, off):
    return struct.unpack_from("<I", BUF, BASE + T + i * 0x20 + off)[0]


def u16(i, off):
    return struct.unpack_from("<H", BUF, BASE + T + i * 0x20 + off)[0]


print("[1] +0x10 ^ prf ^ 0x1A57A870  （-1 哨兵）")
vals = [((u32(i, 0x10) ^ PRF[i] ^ 0x1A57A870) & M32) for i in range(N)]
n1 = sum(1 for v in vals if v == M32)
print("    = -1 的条数 = %d (%.2f%%)" % (n1, 100.0 * n1 / N))
nz = [v for v in vals if v != M32]
print("    非 -1 最小/最大 = %d .. %d" % (min(nz), max(nz)) if nz else "    -")
c = collections.Counter(vals[:5000])
print("    前 5000 条 top6 唯一值数=%d  %s" % (len(c), c.most_common(6)))

print("\n[2] +0x18 -> flags = (raw + 0xAC47) ^ prf16")
f = [((u16(i, 0x18) + 0xAC47) & 0xFFFF) ^ (PRF[i] & 0xFFFF) for i in range(N)]
cf = collections.Counter(f)
print("    不同值 %d  top10 = %s" % (len(cf), [(hex(k), v) for k, v in cf.most_common(10)]))

print("\n[3] +0x1C -> slot = (raw + 0xDAB0) ^ prf16")
s = [((u16(i, 0x1C) + 0xDAB0) & 0xFFFF) ^ (PRF[i] & 0xFFFF) for i in range(N)]
cs = collections.Counter(s)
print("    不同值 %d  最大 %d  top6 = %s" % (len(cs), max(s), [(hex(k), v) for k, v in cs.most_common(6)]))

print("\n[4] +0x1E -> paramCount? = raw ^ prf16 ^ 0x4D12")
p = [(u16(i, 0x1E) ^ (PRF[i] & 0xFFFF) ^ 0x4D12) for i in range(N)]
cp = collections.Counter(p)
print("    不同值 %d  最大 %d" % (len(cp), max(p)))
print("    top10 = %s" % [(k, v) for k, v in cp.most_common(10)])
print("    <=16 占比 %.2f%%   合计(<=64) = %d" % (
    100.0 * sum(v for k, v in cp.items() if k <= 16) / N,
    sum(k * v for k, v in cp.items() if k <= 64)))

print("\n[5] +0x1A -> genericCount (u16) = (raw + 0x2641) ^ prf16")
g = [((u16(i, 0x1A) + 0x2641) & 0xFFFF) ^ (PRF[i] & 0xFFFF) for i in range(N)]
cg = collections.Counter(g)
print("    top6 = %s  合计(<=32) = %d" % ([(k, v) for k, v in cg.most_common(6)],
                                       sum(k * v for k, v in cg.items() if k <= 32)))

print("\n[6] 关键交叉：+0x10 是否 = +0x1E 的基址")
if True:
    both = 0
    for i in range(0, N, 13):
        if vals[i] != M32 and p[i] > 0:
            both += 1
    print("    同时有 +0x10 非 -1 且 paramCount>0 的比例(抽样) = %d" % both)
    print("    抽样明细 (i, +0x10, paramCount, genericCount):")
    k = 0
    for i in range(N):
        if k >= 12:
            break
        if p[i] > 0:
            print("      i=%-6d f10=%-8s pC=%-3d gC=%-3d" % (
                i, "-1" if vals[i] == M32 else vals[i], p[i], g[i]))
            k += 1
