#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract_usage.py —— metadataUsagePairs 解码（§9W 第二部分）

链路（0x180440500 / 0x180440C10 反汇编还原）：
  E74 全局 ^0x3D61FF56 → usageRanges 表（段偏移 0xEC760C）
  E64 全局 ^0x128883A7 → usagePairs 表（段偏移 0x339959C，绝对 0x118+ = 0x33996B4）
  每 pair 8 字节：
    key(u) = ((((u*0x150B976713A1 + 0xB6E1C2778CFDB7D) >> 0x17) * 0x6FC15411
               ^ 0x21CFF42D00) >> 8) & M32
    col1 = ((raw1 - 0x48BC5F9E) & M32) ^ key     ← (type<<29 | index)
    col0 = ((raw0 - 0x330F6527) & M32) ^ key     ← destinationIndex
  type 枚举（il2cpp MetadataUsage）：
    0 Invalid / 1 TypeInfo / 2 Type / 3 MethodDef / 4 FieldInfo
    5 StringLiteral / 6 MethodRef / 7 FieldRef
  （本二进制实测分布对应：{6:83469, 5:80904, 1:72325, 3:40272, 4:4329, 7:3544, 2:3538, 0:3516}）

已验证：type6（本表语义下的 StringLiteral）的 index 连续段 5723..5727
  ↔ bh3_blob.tsv 行 5723..5727（UnityWebRequest 错误消息连续字符串）★

已知问题（下轮收尾）：
  · 行号不从 0 连续合法 —— 最长连续合法段 [185499, 263699)。
    ranges 表（E74）给出 {start,count}，真实行号 = range.start + 局部序，
    而非全局 0..N。需要先解 ranges 表再重算 key（key 用【真实行号】）。
"""
import struct
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT = r"D:\Carol-start\_rea\bh3_usage.tsv"

M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
E64 = 0x118 + 0x339959C
N = 291897

TYPE_NAMES = {0: "Invalid", 1: "TypeInfo", 2: "Type", 3: "MethodDef",
              4: "FieldInfo", 5: "StringLiteral", 6: "MethodRef", 7: "FieldRef"}


def ukey(u):
    t = (u * 0x150B976713A1 + 0xB6E1C2778CFDB7D) & M64
    t >>= 0x17
    t = (t * 0x6FC15411) & M64
    t ^= 0x21CFF42D00
    t >>= 8
    return t & M32


def main():
    buf = open(META, "rb").read()
    lim = {1: 57487, 2: 419568, 3: 57487, 4: 408461, 5: 419568,
           6: 77396, 7: 351719}
    from collections import Counter
    tc = Counter()
    ok_n = 0
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("u\tcol0(dest)\ttype\ttypeName\tindex\n")
        for u in range(N):
            off = E64 + u * 8
            if off + 8 > len(buf):
                break
            r0 = struct.unpack_from("<I", buf, off)[0]
            r1 = struct.unpack_from("<I", buf, off + 4)[0]
            k = ukey(u)
            c1 = ((r1 - 0x48BC5F9E) & M32) ^ k
            c0 = ((r0 - 0x330F6527) & M32) ^ k
            t = c1 >> 29
            idx = c1 & 0x1FFFFFFF
            valid = idx < lim.get(t, 1 << 21)
            tc[t] += 1
            if valid:
                ok_n += 1
            f.write("%d\t%d\t%d\t%s\t%d%s\n" %
                    (u, c0, t, TYPE_NAMES.get(t, "?"), idx, "" if valid else "\tOVER"))
    print("pairs %d，合法 %d (%.1f%%)" % (N, ok_n, 100.0 * ok_n / N))
    for t, n in tc.most_common():
        print("  type%-2d %-14s %d" % (t, TYPE_NAMES.get(t, "?"), n))
    print("→ %s" % OUT)


if __name__ == "__main__":
    main()
