# -*- coding: utf-8 -*-
"""fieldDefaultValues v2：允许 c1=0xFFFFFFFF 哨兵与 c1 非 4 对齐，全表提取"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
POOL = 0x1D79938
N = len(BUF)
SENT = 0xFFFFFFFF

lit = set()
with open(r"D:\Carol-start\_rea\bh3_field_flags.tsv", encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 5 and p[4] == "1":
            lit.add(int(p[0]))

rows = []
off = 0x564210
prev_fi = -1
prev_c1 = -1
while off + 12 <= N:
    fi, c1, c2 = struct.unpack_from("<3I", BUF, off)
    if fi >= 419568 or fi <= prev_fi:
        break
    if c1 != SENT and (c1 < prev_c1 or POOL + c1 + 8 > N):
        break
    rows.append((fi, c1, c2))
    prev_fi = fi
    if c1 != SENT:
        prev_c1 = c1
    off += 12

n_sent = sum(1 for _, c1, _ in rows if c1 == SENT)
hit = sum(1 for fi, c1, _ in rows if c1 != SENT and fi in lit)
print("表行数: %d (哨兵 %d), 尾 @0x%X" % (len(rows), n_sent, off))
print("literal 命中(非哨兵): %d / %d" % (hit, len(rows) - n_sent))

# 断点后看 3 行
print("断点后 3 行:")
for i in range(3):
    print("  ", struct.unpack_from("<3I", BUF, off + i * 12))

with open(r"D:\Carol-start\_rea\bh3_field_defaults.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("fieldIdx\tdataOffset\tcol2\tvalueU32\n")
    for fi, c1, c2 in rows:
        v = struct.unpack_from("<I", BUF, POOL + c1)[0] if c1 != SENT else -1
        f.write("%d\t%d\t%d\t%d\n" % (fi, c1 if c1 != SENT else -1, c2, v))
print("已写 bh3_field_defaults.tsv")

# 枚举覆盖统计：多少 literal 拿到了值
have = set(fi for fi, c1, _ in rows if c1 != SENT)
print("拿到值的 literal: %d / 207021 (%.1f%%)" % (len(have & lit), 100.0 * len(have & lit) / 207021))
