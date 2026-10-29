# -*- coding: utf-8 -*-
"""方法记录 0x20 全字段诊断。"""
import struct
import collections

M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
BASE = 0x118
T = 0xFA8318
N = 408461
NT = 57487
NCTYPE = 354184

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
PRF = []


def build_prf(n):
    for i in range(n):
        x = ((i * 0xB069) ^ 0x3E382F2D) & M64
        x = (x * 0x24147491) & M64
        x = (x ^ 0xF997B4A800) >> 10
        x = (x * 0x3857AACA) & M64
        PRF.append(x >> 0xE)


build_prf(N)

DECL_K = 0xE5AF14B4
RET_K = 0xAEAE5FEE
GEN_K = 0xEA530370
TOK_K = 0xBD6FC398

print("[A] rec[0] 声明类型  /  rec[8] 返回类型")
oor_d = []
oor_r = []
for i in range(N):
    o = BASE + T + i * 0x20
    r0, r8 = struct.unpack_from("<II", BUF, o)[0], struct.unpack_from("<I", BUF, o + 8)[0]
    if (((r0 + DECL_K) & M32) ^ PRF[i]) >= NCTYPE:
        oor_d.append(i)
    if (((r8 + RET_K) & M32) ^ PRF[i]) >= NCTYPE:
        oor_r.append(i)
print("    声明类型越界索引 = %s" % oor_d)
print("    返回类型越界索引 = %s" % oor_r)

print("\n[B] rec[0x14]  (const 0xBD6FC398)")
hi = collections.Counter()
deltas = collections.Counter()
prev = None
for i in range(N):
    v = ((struct.unpack_from("<I", BUF, BASE + T + i * 0x20 + 0x14)[0] + TOK_K) & M32) ^ PRF[i]
    hi[v >> 24] += 1
    if i < 40:
        print("      i=%-5d v=%08X" % (i, v))
    m = v & 0xFFFFFF
    if prev is not None:
        deltas[(m - prev) & 0xFFFFFF] += 1
    prev = m
print("    高字节分布 = %s" % dict(hi))
print("    低 24 位差分 top10 = %s" % deltas.most_common(10))

print("\n[C] rec[0x10] / rec[0x18] / rec[0x1C] 原始分布")
for off in (0x10, 0x18, 0x1C):
    c = collections.Counter()
    for i in range(0, N, 37):
        c[struct.unpack_from("<I", BUF, BASE + T + i * 0x20 + off)[0]] += 1
    print("     +0x%02X 不同值 %d / 抽样 %d  top5=%s" % (off, len(c), len(range(0, N, 37)),
                                                        [("%08X" % k, v) for k, v in c.most_common(5)]))

print("\n[D] +0x1A 泛型形参数 (raw+0x2641 ^ prf16  vs  sub)")
xor_hit = sub_hit = 0
dist = collections.Counter()
for i in range(N):
    raw = struct.unpack_from("<H", BUF, BASE + T + i * 0x20 + 0x1A)[0]
    p16 = PRF[i] & 0xFFFF
    xv = ((raw + 0x2641) & 0xFFFF) ^ p16
    sv = ((raw + 0x2641) & 0xFFFF) - p16 & 0xFFFF
    dist[sv] += 1
    if xv <= 6:
        xor_hit += 1
    if sv <= 6:
        sub_hit += 1
print("    xor 版本 <=6 : %d (%.2f%%)" % (xor_hit, 100.0 * xor_hit / N))
print("    sub 版本 <=6 : %d (%.2f%%)" % (sub_hit, 100.0 * sub_hit / N))
print("    sub 分布 top8 = %s" % dist.most_common(8))
print("    sub 合计 = %d" % sum(k * v for k, v in dist.items() if k < 100))
