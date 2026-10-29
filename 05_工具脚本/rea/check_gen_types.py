# -*- coding: utf-8 -*-
"""验证 generator token 语义：方法→声明类型映射 + generator 声明类型名分布
   若 generator 方法大量挂在 *Attribute 类型上 → 属性名 = 声明类型名"""
import struct
from collections import Counter

# 1) methodIdx -> typeIdx（types_v5: index/ns/name/methodStart/methodCount）
m2t = {}
for ln in open(r"D:\Carol-start\_rea\bh3_types_v5.txt", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if p[0] == "index":
        continue
    try:
        ti, ms, mc = int(p[0]), int(p[4]), int(p[5])
    except (ValueError, IndexError):
        continue
    if ms < 0 or mc <= 0:
        continue
    for k in range(ms, min(ms + mc, 408461)):
        m2t[k] = ti

# 2) typeIdx -> 简名
tname = {}
for ln in open(r"D:\Carol-start\_rea\bh3_types_v5.txt", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if p[0] == "index":
        continue
    try:
        tname[int(p[0])] = (p[1] + "." if p[1] else "") + p[2]
    except (ValueError, IndexError):
        continue
print("方法→类型映射 %d 条, 类型名 %d" % (len(m2t), len(tname)))

# 3) generator 数组的声明类型分布
BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
GEN_S, GEN_E = 0x7C4F64, 0xAC1050
cnt = Counter()
n_attr_type = 0
n_tot = 0
for o in range(GEN_S, GEN_E, 4):
    b = BUF[o:o+4]
    if b[3] != 0x60:
        continue
    midx = b[0] | b[1] << 8 | b[2] << 16
    if midx > 0xFFFFFF:
        continue
    n_tot += 1
    ti = m2t.get(midx)
    if ti is None:
        cnt["<无映射>"] += 1
        continue
    tn = tname.get(ti, "?")
    cnt[tn] += 1
    if tn.endswith("Attribute"):
        n_attr_type += 1
print("generator 总数 %d, 声明类型以 Attribute 结尾: %d (%.1f%%)"
      % (n_tot, n_attr_type, 100.0 * n_attr_type / n_tot))
print("\nTop 20 声明类型:")
for k, v in cnt.most_common(20):
    print("  %-58s %7d" % (k[:58], v))
