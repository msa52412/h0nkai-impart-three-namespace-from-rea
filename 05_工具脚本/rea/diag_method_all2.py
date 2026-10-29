# -*- coding: utf-8 -*-
"""方法记录 0x20 全字段诊断（v2，prf 截断到 32 位）。"""
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
for i in range(N):
    x = ((i * 0xB069) ^ 0x3E382F2D) & M64
    x = (x * 0x24147491) & M64
    x = (x ^ 0xF997B4A800) >> 10
    x = (x * 0x3857AACA) & M64
    PRF.append((x >> 0xE) & M32)

print("[B] rec[0x14] & 0xFFFFFF = 程序集内方法行号？")
prev = None
resets = []
bad = 0
for i in range(N):
    v = (((struct.unpack_from("<I", BUF, BASE + T + i * 0x20 + 0x14)[0] + 0xBD6FC398) & M32)
         ^ PRF[i]) & 0xFFFFFF
    if prev is not None:
        d = v - prev
        if d == 1:
            pass
        elif d <= 0:
            resets.append((i, prev, v))
        else:
            bad += 1
    prev = v
print("    递增 1 的次数 = %d ; 回退/重置次数 = %d ; 其他跳变 = %d"
      % (N - 1 - len(resets) - bad, len(resets), bad))
print("    前 8 个重置点 = %s" % resets[:8])
print("    末 3 个 = %s" % resets[-3:])

print("\n[C] +0x18 / +0x1C 原始 u32 分布")
for off in (0x18, 0x1C):
    c = collections.Counter()
    for i in range(0, N, 11):
        c[struct.unpack_from("<I", BUF, BASE + T + i * 0x20 + off)[0]] += 1
    tot = len(range(0, N, 11))
    print("     +0x%02X 不同值 %d / %d  top6=%s" % (off, len(c), tot, [("%08X" % k, v) for k, v in c.most_common(6)]))
# u16 视角
for off in (0x18, 0x1A, 0x1C, 0x1E):
    c = collections.Counter()
    for i in range(0, N, 11):
        c[struct.unpack_from("<H", BUF, BASE + T + i * 0x20 + off)[0]] += 1
    print("     u16 +0x%02X 不同值 %d  top5=%s" % (off, len(c), [(hex(k), v) for k, v in c.most_common(5)]))

print("\n[D] +0x1A 泛型形参数")
dx = collections.Counter()
ds = collections.Counter()
for i in range(N):
    raw = struct.unpack_from("<H", BUF, BASE + T + i * 0x20 + 0x1A)[0]
    p16 = PRF[i] & 0xFFFF
    dx[((raw + 0x2641) & 0xFFFF) ^ p16] += 1
    ds[(((raw + 0x2641) & 0xFFFF) - p16) & 0xFFFF] += 1
print("    xor  top6 = %s  <=8 占比 %.2f%%" % (sorted(dx.items())[:6],
                                           100.0 * sum(v for k, v in dx.items() if k <= 8) / N))
print("    sub  top6 = %s  <=8 占比 %.2f%%" % (sorted(ds.items())[:6],
                                           100.0 * sum(v for k, v in ds.items() if k <= 8) / N))
print("    xor 非零比例(<=64) = %.2f%%" % (100.0 * sum(v for k, v in dx.items() if 0 < k <= 64) / N))

print("\n[E] +0x10 是否 parameterStart")
c = collections.Counter()
for i in range(0, N, 7):
    c[struct.unpack_from("<I", BUF, BASE + T + i * 0x20 + 0x10)[0]] += 1
print("     不同值 %d / %d  top5=%s" % (len(c), len(range(0, N, 7)),
                                      [("%08X" % k, v) for k, v in c.most_common(5)]))
