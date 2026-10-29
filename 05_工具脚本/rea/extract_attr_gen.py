# -*- coding: utf-8 -*-
"""customAttributeGenerators 表全解：
   表 @0xA3F44D（c1[0] 低 24 位 + 0x118），4B/条 = generator 方法 token
   条数 76,737（与 T5 c2 差分、方法表 +0x14 列三方一致）
   token → 方法行号 = token - 0x06000000（1 基）"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
TBL = 0xA3F44D
N = 76737

rows = []
bad = 0
for i in range(N):
    t = struct.unpack_from("<I", BUF, TBL + i * 4)[0]
    m = t - 0x06000000
    if not (1 <= m <= 251708):
        bad += 1
        if bad <= 3:
            print("越界 token @%d: 0x%08X" % (i, t))
        continue
    rows.append((i + 1, t, m))

print("generator tokens: 有效 %d / %d, 越界 %d" % (len(rows), N, bad))
with open(r"D:\Carol-start\_rea\bh3_attr_generators.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("attrIdx\tgeneratorToken\tmethodRow(1基)\n")
    for a, t, m in rows:
        f.write("%d\t%08X\t%d\n" % (a, t, m))
print("已写 bh3_attr_generators.tsv")

# 抽查: attrIdx=1 → 方法 14。mscorlib 方法 14 是什么？
names = {}
for ln in open(r"D:\Carol-start\_rea\bh3_methods.txt", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 4:
        names[int(p[0])] = p[3]
for a, t, m in rows[:5]:
    print("  attrIdx=%d token=%08X → 方法 %d = %s" % (a, t, m - 1, names.get(m - 1, "?")))
PYEOF = None
