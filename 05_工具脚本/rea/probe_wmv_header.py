# -*- coding: utf-8 -*-
"""Asb .wmv 包头结构分析：对比多个包的前 96 字节，定位与文件大小相关的字段
   用法: python probe_wmv_header.py [样本数]
"""
import os
import random
import struct
import sys

D = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 8


def dump(tag, b, size):
    print("--- %s  fileSize=%d (0x%X)" % (tag, size, size))
    for off in range(0, min(len(b), 96), 16):
        ch = b[off:off + 16]
        asc = "".join(chr(c) if 32 <= c < 127 else "." for c in ch)
        print("  %04x  %-47s  %s" % (off, ch.hex(" "), asc))


def find_size_fields(b, size):
    """在前 96 字节里找等于 fileSize 的 4/8 字节字段"""
    hits = []
    for off in range(0, min(len(b), 96) - 8):
        for fmt, n in (("<I", 4), (">I", 4), ("<Q", 8), (">Q", 8)):
            try:
                v = struct.unpack_from(fmt, b, off)[0]
            except struct.error:
                continue
            if v == size:
                hits.append((off, fmt, n))
    return hits


def main():
    fs = [f for f in os.listdir(D) if f.endswith(".wmv")]
    random.seed(7)
    sample = random.sample(fs, min(N, len(fs)))
    sizes = []
    for f in sample:
        p = os.path.join(D, f)
        size = os.path.getsize(p)
        with open(p, "rb") as fh:
            b = fh.read(96)
        sizes.append((f, size))
        dump(f[:16], b, size)
        h = find_size_fields(b, size)
        if h:
            print("    ★ 等于文件大小的字段:", h)
        print()

    print("=== 前 20 字节是否恒定 ===")
    heads = []
    for f, _ in sizes:
        with open(os.path.join(D, f), "rb") as fh:
            heads.append(fh.read(20))
    for i in range(20):
        vals = {h[i] for h in heads}
        print("  off %2d: %s%s" % (i, "恒定" if len(vals) == 1 else "变化",
                                   (" = 0x%02x" % list(vals)[0]) if len(vals) == 1 else ""))


if __name__ == "__main__":
    main()
