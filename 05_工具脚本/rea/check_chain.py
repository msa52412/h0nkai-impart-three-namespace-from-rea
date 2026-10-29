# -*- coding: utf-8 -*-
"""检查 fdv 表 fi 链是否中途断裂（表可能更长）；统计枚举覆盖度"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
POOL = 0x1D79938
TBL = 0x564210

# 1) 在断点后重新锚定：从 0x5F94E4 起找下一个 fi 递增起点
#    断点处 raw:
off = 0x5F94E4
print("断点 raw 3 行:")
for i in range(3):
    print("  ", struct.unpack_from("<3I", BUF, off + i * 12))

# 2) 容错扫描：全区间 [0x564210, 0xAC1050) 内，允许 fi 链断裂后重锁
#    判据: c1 单调不减 且 < POOL 范围 (0xA3000) 且 fi < 419568 且 fi 在 literal
lit = set()
with open(r"D:\Carol-start\_rea\bh3_field_flags.tsv", encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 5 and p[4] == "1":
            lit.add(int(p[0]))

# 收集所有 12B 对齐的"可信行": c1 < 0xA3000 且 (c1 % 4 == 0) 且 fi in lit
rows = []
off = 0x564210
while off + 12 <= 0xAC1050:
    fi, c1, c2 = struct.unpack_from("<3I", BUF, off)
    if fi in lit and 0 <= c1 < 0xA3000 and c1 % 4 == 0:
        rows.append((off, fi, c1, c2))
    off += 12
print("容错扫描可信行: %d" % len(rows))
# 按 fi 去重（取首现）
seen = {}
for off_, fi, c1, c2 in rows:
    if fi not in seen:
        seen[fi] = (c1, c2)
print("唯一 literal fi: %d / %d" % (len(seen), len(lit)))

# 3) 断裂形态：0x5F94E4 后第一行是什么
for i in range(5):
    o = 0x5F94E4 + i * 12
    fi, c1, c2 = struct.unpack_from("<3I", BUF, o)
    print("  +[%d] fi=%-8d c1=%-8d c2=%-8d" % (i, fi, c1, c2))
