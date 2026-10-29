# -*- coding: utf-8 -*-
"""fieldDefaultValues 完整提取器
   表 @0x564210 (12B 行: {fieldIndex, dataIndex, col2})，值池 @0x1D79938 明文"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
POOL = 0x1D79938

# 1) 表起点探测：从 0x564210 向前找 fi 递增链的头
# 行结构: fi 严格递增, c1 递增(每字段+4 或共享), c2 小整数
S = 0x564210
# 向前走：若 [S-12] 的 fi < [S] 的 fi 且在域内，表更早开始
head = S
while head - 12 >= 0x118:
    fi0 = struct.unpack_from("<I", BUF, head - 12)[0]
    fi1 = struct.unpack_from("<I", BUF, head)[0]
    c1_0 = struct.unpack_from("<I", BUF, head - 8)[0]
    if fi0 < fi1 and c1_0 < struct.unpack_from("<I", BUF, head + 4)[0] and fi0 < 419568:
        head -= 12
    else:
        break
print("表头探测: 0x%X (向前延伸 %d 行)" % (head, (S - head) // 12))

# 2) 全表扫描（从探测头开始，容许 c1 相等=共享值）
rows = []
off = head
prev_fi = -1
prev_c1 = -1
while off + 12 <= len(BUF):
    fi, c1, c2 = struct.unpack_from("<3I", BUF, off)
    if fi >= 419568 or fi <= prev_fi or c1 < prev_c1 or POOL + c1 + 4 > len(BUF):
        break
    rows.append((fi, c1, c2))
    prev_fi, prev_c1 = fi, c1
    off += 12
print("表行数: %d, 尾 @0x%X" % (len(rows), head + len(rows) * 12))

# 3) literal 覆盖检查
lit = set()
flags = {}
with open(r"D:\Carol-start\_rea\bh3_field_flags.tsv", encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 5:
            flags[int(p[0])] = (p[1], p[3], p[4] == "1")
            if p[4] == "1":
                lit.add(int(p[0]))
hit = sum(1 for fi, _, _ in rows if fi in lit)
print("literal 命中: %d / %d (%.1f%%)" % (hit, len(rows), 100.0 * hit / max(len(rows), 1)))

# 4) 全表读值（按类型宽度），写 TSV
# 类型宽度: 用 flags 表的 type 列（p[1] 是完整类型名？看 bh3_fields 列序 typeIdx,nameIdx? 之前 p[1]=类型名 p[3]=字段名）
def read_val(fi, c1):
    # 简化: 全按 4 字节读，后续按字段类型重解释
    return struct.unpack_from("<I", BUF, POOL + c1)[0]

with open(r"D:\Carol-start\_rea\bh3_field_defaults.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("fieldIdx\tdataOffset\tcol2\tvalueU32\n")
    for fi, c1, c2 in rows:
        f.write("%d\t%d\t%d\t%d\n" % (fi, c1, c2, read_val(fi, c1)))
print("已写 bh3_field_defaults.tsv")

# 5) col2 语义采样：col2 分布
from collections import Counter
cc = Counter(c2 for _, _, c2 in rows)
print("col2 top10:", cc.most_common(10))

# 6) 值池的尾端
maxoff = max(c1 for _, c1, _ in rows)
print("值池最大偏移 0x%X → 池尾 0x%X" % (maxoff, POOL + maxoff))
# 该处后面是什么
print("池尾后 32B:", BUF[POOL + maxoff:POOL + maxoff + 32].hex())
