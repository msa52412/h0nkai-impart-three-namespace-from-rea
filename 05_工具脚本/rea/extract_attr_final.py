# -*- coding: utf-8 -*-
"""CustomAttribute 数据层完整落盘 v1：
   ① generator 表（0xA3F44C，4B [m0 m1 m2 0x60]，共 85,973 token + 275 填充）
   ② 方法表 +0x14 → attrIdx（251,707 条，1 基，域 1..76737）
   ③ T5 c1/c2 → 每镜像 attrData 字节范围（总 34,494B？—— 复核）
   注: 76,737 是 owner 记录数；85,973 是 generator 记录数（一 owner 可多 attr）"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
S = 0xA3F44C
END = 0xA93B0C

gens = []
with open(r"D:\Carol-start\_rea\bh3_attr_generators.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("genIdx\tmethodIdx\tmethodName\n")
    # 方法名
    names = {}
    for ln in open(r"D:\Carol-start\_rea\bh3_methods.txt", encoding="utf-8"):
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 4:
            names[int(p[0])] = p[3]
    k = 0
    for o in range(S, END, 4):
        if BUF[o + 3] != 0x60:
            continue
        midx = BUF[o] | BUF[o + 1] << 8 | BUF[o + 2] << 16
        if midx > 460000:
            continue
        f.write("%d\t%d\t%s\n" % (k, midx, names.get(midx, "?")))
        gens.append(midx)
        k += 1
print("generator 记录 %d 条（首个=方法 %d）" % (len(gens), gens[0]))

# 复核 T5: c1/c2 是 attrData 的什么? 总差分 34494 但 generator 表 345,792B
# → c1/c2 不是字节范围而是【owner 记录范围】（76,737 来自方法表 attrIdx 唯一值数）
# c1 差分 = c2 → c1 = attrOwnerStart（1 基记录号），c2 = ownerCount!
# 验证: c1[0]-base 应=0 且 mscorlib owner 记录号范围 = [c1[0], c1[0]+1499)
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
T5 = 0x118 + 0x1C2A198
def ikey(i):
    v = (i * 0x14C3BD9234D3) & M64
    v >>= 9
    v = (v + 0x48C65E21) & M64
    v = (v * 0x22343DDF) & M64
    v >>= 0x15
    return v & M32
c1 = []
for i in range(192):
    r1 = struct.unpack_from("<I", BUF, T5 + i * 0x28 + 4)[0]
    c1.append((r1 - ikey(i)) & M32)
print("c1[0]=%d (若=1 则 1 基) 差分和=%d" % (c1[0], c1[191] - c1[0]))
# 方法 attrIdx 域 1..76737 与 c1 关系: mscorlib 段 idx∈[c1[0], c1[0]+c2[0])
# c1[0]≈2.6 亿 —— 不是 1 基小数。c1 是【加密偏移】，c2 是 ownerCount
PYEOF = None
