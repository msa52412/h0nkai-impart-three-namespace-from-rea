#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 FUN_18043EC20 里的 PRF(i) 公式，确定字段级解密的精确整数语义。

伪代码（dec_targets.c:340）:
  iVar5 = (int)(((uVar22 * 0x14c3bd9234d3 >> 9) + 0x48c65e21) * 0x22343ddf >> 0x15);
  字符串偏移 = (piVar17[5] + -0x3d7dc690) - iVar5

  uVar21 = (iVar4 * 0x56184a41 + 0x57a94b1fU ^ 0x37f164b8) * 0x10fb44e5 ^ 0x7b1de297;
  uVar23 = (iVar4 * 0x447fce41 ^ 0x120dd35fU) * 0x3e8906da;

判定标准：解密出的偏移若正确，应大量落在 [0, filesize) 内。
"""
import struct

META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118
M32 = 0xFFFFFFFF


def i32(x):
    x &= M32
    return x - (1 << 32) if x >= (1 << 31) else x


def u32(x):
    return x & M32


with open(META, "rb") as f:
    f.seek(0, 2)
    FSIZE = f.tell()
    f.seek(BASE + 0x01C2A198)
    T5 = f.read(0x28 * 192)

print("文件大小 = %d (0x%X)\n" % (FSIZE, FSIZE))

recs = [struct.unpack_from("<10I", T5, i * 0x28) for i in range(192)]

# ---------------- 表5 的 PRF 候选 ----------------
K1 = 0x14C3BD9234D3
C1 = 0x48C65E21
K2 = 0x22343DDF
SH1 = 9
SH2 = 21


def prf_a(i):  # 全 64 位
    return i32(((i * K1) >> SH1) + C1) if False else i32(((((i * K1) >> SH1) + C1) * K2) >> SH2)


def prf_b(i):  # 乘法后截 32 位再右移
    return i32((u32(((((i * K1) >> SH1) + C1)) * K2)) >> SH2)


def prf_c(i):  # 加之后截 32 位，乘 32 位，再右移
    return i32((u32((u32((i * K1) >> SH1) + C1) * K2)) >> SH2)


def prf_d(i):  # 乘法结果 32 位，右移 21，再截 int
    return i32(u32(((((i * K1) >> SH1) + C1) * K2)) >> SH2)


CANDS = {"A_全64位": prf_a, "B_乘后截32": prf_b, "C_加后截32": prf_c, "D_同B": prf_d}

print("=" * 86)
print("表5 字段 +0x14 (piVar17[5]) 字符串偏移解密 —— 各 PRF 解释的命中率")
print("=" * 86)
print("%-14s %-10s %-10s %-12s %s" % ("PRF", "命中数/192", "命中率", "min", "max"))
best = None
for name, fn in CANDS.items():
    vals = []
    for i in range(192):
        v = i32(i32(recs[i][5] - 0x3D7DC690) - fn(i))
        vals.append(v)
    ok = [v for v in vals if 0 <= v < FSIZE]
    print("%-14s %-10s %-10s %-12d %d" % (name, "%d/192" % len(ok), "%.1f%%" % (100.0 * len(ok) / 192), min(vals), max(vals)))
    if best is None or len(ok) > best[1]:
        best = (name, len(ok))

# 基线：完全不加 PRF
vals = [i32(recs[i][5] - 0x3D7DC690) for i in range(192)]
ok = [v for v in vals if 0 <= v < FSIZE]
print("%-14s %-10s %-10s %-12d %d" % ("基线_无PRF", "%d/192" % len(ok), "%.1f%%" % (100.0 * len(ok) / 192), min(vals), max(vals)))

print("\n最佳: %s (%d/192)" % best)

# 用最佳 PRF 打印前 8 条解出的偏移
fn = CANDS[best[0]]
print("\n--- 用 %s 解出的前 8 条记录（仅 +0x14 字段）---" % best[0])
for i in range(8):
    v = i32(i32(recs[i][5] - 0x3D7DC690) - fn(i))
    mark = "OK" if 0 <= v < FSIZE else "--"
    print("  [%3d] %08X -> %12d (0x%08X) %s" % (i, recs[i][5], v, v & M32, mark))
