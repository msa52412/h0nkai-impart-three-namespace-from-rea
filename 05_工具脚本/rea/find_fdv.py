#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""find_fdv.py —— 在 global-metadata.dat 里定位 fieldDefaultValues 表

已知模式（沿用字段表的经验）：
  · 每条记录 12 字节，可能为 {A, fieldIndex_obf, dataIndex_obf}
  · 逐记录混淆 prf(i) = ((i*K1 + K2) >> 0x11) & 0xFFFFFFFF（K1/K2 与字段表相同）
  · 解出的 fieldIndex 必须严格递增、落在 [0, 419568)、且全部属于 literal 字段集合
  · 「严格递增」与未知加性常数无关 —— 先用它做无参筛，再解常数

输出：候选表位置 + 解出的常数 C + 命中 literal 集合的比例
"""
import struct

META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
FLAGS = r"D:\Carol-start\_rea\bh3_field_flags.tsv"
M32 = 0xFFFFFFFF

K1 = 0x7740EEFF55F40540
K2 = 0x49ED7F5AFCC4AF8
M64 = (1 << 64) - 1
N_FIELDS = 419568


def prf(i):
    return (((i * K1 + K2) & M64) >> 0x11) & M32


def load_literal():
    lit = set()
    with open(FLAGS, encoding="utf-8") as f:
        next(f)
        for ln in f:
            p = ln.split("\t")
            if len(p) >= 5 and p[4] == "1":
                lit.add(int(p[0]))
    return lit


def main():
    buf = open(META, "rb").read()
    lit = load_literal()
    print("literal 字段 %d 个 / 全字段 %d" % (len(lit), N_FIELDS))
    print("metadata 大小 0x%X" % len(buf))

    PRF = [prf(i) for i in range(4096)]

    hits = []
    # 12 字节对齐扫描；每处检查前 64 条记录 col=1（fieldIndex 候选列，同字段表布局）
    NCHK = 64
    step = 12
    for S in range(0x118, len(buf) - step * NCHK, step):
        ok = True
        prev = None
        for i in range(NCHK):
            v = (struct.unpack_from("<I", buf, S + i * step + 4)[0] - PRF[i]) & M32
            if v >= N_FIELDS:
                ok = False
                break
            if prev is not None and v <= prev:
                ok = False
                break
            prev = v
        if ok:
            hits.append(S)
    print("12B/col1 单调候选: %d 个" % len(hits))
    for S in hits[:20]:
        print("   0x%X" % S)
    return buf, lit, hits


if __name__ == "__main__":
    main()
