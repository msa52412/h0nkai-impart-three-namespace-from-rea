# -*- coding: utf-8 -*-
"""generator 表修正版 v3：真实域 0xA3F44C..0xAC1050（132,865 条 4B 记录位）
   只统计 [m0 m1 m2 0x60/0xC0] 形态，00 填充跳过"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
S, END = 0xA3F44C, 0xAC1050

names = {}
for ln in open(r"D:\Carol-start\_rea\bh3_methods.txt", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 4:
        names[int(p[0])] = p[3]

n60 = nC0 = n00 = nother = 0
with open(r"D:\Carol-start\_rea\bh3_attr_generators.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("recIdx\tkind\tmethodIdx\tmethodName\n")
    k = 0
    for o in range(S, END, 4):
        b = BUF[o:o + 4]
        if b == b"\x00\x00\x00\x00":
            n00 += 1
            continue
        if b[3] in (0x60, 0xC0):
            midx = b[0] | b[1] << 8 | b[2] << 16
            if midx <= 0xFFFFFF:
                kind = "M" if b[3] == 0x60 else "T"
                f.write("%d\t%s\t%d\t%s\n" % (k, kind, midx, names.get(midx, "") if kind == "M" else ""))
                if b[3] == 0x60:
                    n60 += 1
                else:
                    nC0 += 1
                k += 1
                continue
        nother += 1
print("方法类 %d + 类型类 %d = %d, 00 填充 %d, 非常规 %d / 132,865" % (n60, nC0, n60 + nC0, n00, nother))
