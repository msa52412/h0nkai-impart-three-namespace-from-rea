#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract_blob.py —— metadata blob 区完整解密（§9W）

链路（全部由 0x18043ACF0 反汇编还原，300/300 行可读验证）：
  描述表  E90 全局 → 段偏移 0x1EC6620，绝对 0x118+ = 0x1EC6738
          77,396 行 × 8B，表尾恰好 = 字段表起点 0x1F5D9D8
          key_row(i) = ((((i * 0x1AB6B1E4CD9A) >> 0xB) * 0x6595FC2F
                         ^ 0x790A43A40000) >> 0x11) & M32
          col0(offset) = ((raw0 ^ 0x2BE4EEE9) - key_row) & M32
          col1(length) = (raw1 - key_row - 0x25C2F1A9) & M32
  数据区  E5C 全局 → 段偏移 0x3185984，绝对 0x118+ = 0x3185A9C
          blob 区 0x3185A9C .. 0x33996B1（尾部与 E64 段 0x33996B4 3 字节对齐相接）
  流密码  seed(i) = (((i*0x54CCBD2A6C08DF18 ^ 0x25450C2973B42381)
                       * 0x174BDB9B4B2EC230 ^ 0x6F7A46CC48B4908D)
                     * 0x2BB71BC476FEFD2E - 0x0EEA8D685E597BCC) & M64
          每 8 字节：plain = cipher ^ key; key += 0x5BB8DBE022B62203

输出：bh3_blob.tsv（row / offset / len / text）
"""
import struct
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT = r"D:\Carol-start\_rea\bh3_blob.tsv"

M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
TBL = 0x118 + 0x1EC6620
DATA = 0x3185A9C
N = 77396


def key_row(i):
    v = (i * 0x1AB6B1E4CD9A) & M64
    v >>= 0xB
    v = (v * 0x6595FC2F) & M64
    v ^= 0x790A43A40000
    v >>= 0x11
    return v & M32


def seed(i):
    v = (i * 0x54CCBD2A6C08DF18) & M64
    v ^= 0x25450C2973B42381
    v = (v * 0x174BDB9B4B2EC230) & M64
    v ^= 0x6F7A46CC48B4908D
    v = (v * 0x2BB71BC476FEFD2E) & M64
    v = (v - 0x0EEA8D685E597BCC) & M64
    return v


STEP = 0x5BB8DBE022B62203


def main():
    buf = open(META, "rb").read()
    ok_str = 0
    rows = []
    for i in range(N):
        off = TBL + i * 8
        k = key_row(i)
        o = ((struct.unpack_from("<I", buf, off)[0] ^ 0x2BE4EEE9) - k) & M32
        l = (struct.unpack_from("<I", buf, off + 4)[0] - k - 0x25C2F1A9) & M32
        src = DATA + o
        kk = seed(i)
        out = bytearray()
        for q in range((l + 7) >> 3):
            out += (struct.unpack_from("<Q", buf, src + q * 8)[0] ^ kk).to_bytes(8, "little")
            kk = (kk + STEP) & M64
        b = bytes(out[:l])
        try:
            s = b.decode("utf-8")
            printable = all(31 < ord(c) < 127 or c in "\r\n\t" for c in s)
        except UnicodeDecodeError:
            s = None
            printable = False
        if printable:
            ok_str += 1
        rows.append((i, o, l, s if printable else b.hex()))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("row\toffset\tlen\ttext\n")
        for i, o, l, t in rows:
            if isinstance(t, bytes):
                f.write("%d\t0x%X\t%d\t[binary]%s\n" % (i, o, l, t[:96].decode("ascii", "replace")))
            else:
                f.write("%d\t0x%X\t%d\t%s\n" % (i, o, l, t.replace("\t", "\\t").replace("\n", "\\n")))
    print("blob 行 %d，可读字符串 %d (%.1f%%)" % (N, ok_str, 100.0 * ok_str / N))
    print("→ %s" % OUT)
    # 展示前几行
    for i, o, l, t in rows[:8]:
        v = t if isinstance(t, str) else t[:40].decode("ascii", "replace")
        print("  row%-6d len=%-4d %r" % (i, l, v[:70]))


if __name__ == "__main__":
    main()
