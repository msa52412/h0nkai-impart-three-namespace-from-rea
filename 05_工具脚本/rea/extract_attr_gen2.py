# -*- coding: utf-8 -*-
"""generator 表完整版 v2：0x60(方法 0x06xxxxxx) + 0xC0(类型 0x0Cxxxxxx?) 双 token
   表 @0xA3F44C .. 0xB025B4，0000 填充 379 处
   每个 owner 一条 token 记录 —— 131,382+1,673 = 133,055 ≈ owner 引用总数"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
S = 0xA3F44C
END = 0xB025B4

names = {}
for ln in open(r"D:\Carol-start\_rea\bh3_methods.txt", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 4:
        names[int(p[0])] = p[3]

n60 = nC0 = n00 = 0
with open(r"D:\Carol-start\_rea\bh3_attr_generators.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("recIdx\tkind\tmethodIdx\tmethodName\n")
    k = 0
    for o in range(S, END, 4):
        b3 = BUF[o + 3]
        if BUF[o:o + 4] == b"\x00\x00\x00\x00":
            n00 += 1
            continue
        if b3 not in (0x60, 0xC0):
            continue
        midx = BUF[o] | BUF[o + 1] << 8 | BUF[o + 2] << 16
        if midx > 0xFFFFFF:
            continue
        kind = "M" if b3 == 0x60 else "T"
        f.write("%d\t%s\t%d\t%s\n" % (k, kind, midx, names.get(midx, "") if kind == "M" else ""))
        if b3 == 0x60:
            n60 += 1
        else:
            nC0 += 1
        k += 1
print("记录: 方法类 %d + 类型类 %d = %d, 00 填充 %d" % (n60, nC0, n60 + nC0, n00))

# 0xC0 类的 idx 是什么域？抽 10 个看
print("\n0xC0 类样例:")
cnt = 0
for o in range(S, END, 4):
    if BUF[o + 3] == 0xC0:
        midx = BUF[o] | BUF[o + 1] << 8 | BUF[o + 2] << 16
        print("  0x%X: idx=%d (0x%X)" % (o, midx, midx))
        cnt += 1
        if cnt >= 8:
            break
