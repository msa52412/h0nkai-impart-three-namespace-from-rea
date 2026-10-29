# -*- coding: utf-8 -*-
"""验证 0x564210 表 = fieldDefaultValues：
   用已知枚举值（DayOfWeek/DateTimeKind/AttributeTargets/Int32.MaxValue）交叉验证"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
TBL = 0x564210

# 1) 找已知常量字段的 fieldIdx
known = {}
for ln in open(r"D:\Carol-start\_rea\bh3_fields.tsv", encoding="utf-8", errors="replace"):
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 5 and p[0] != "typeIdx":
        key = (p[1], p[3])
        if key in (("System.DayOfWeek", "Sunday"), ("System.DayOfWeek", "Wednesday"), ("System.DayOfWeek", "Saturday"),
                   ("System.DateTimeKind", "Utc"), ("System.DateTimeKind", "Local"),
                   ("System.AttributeTargets", "Class"), ("System.AttributeTargets", "Method"), ("System.AttributeTargets", "Assembly"),
                   ("System.Int32", "MaxValue"), ("System.Int32", "MinValue"), ("System.Byte", "MaxValue"),
                   ("System.Boolean", "TrueString"), ("System.String", "Empty")):
            known[key] = int(p[2])
print("已知字段:", {("%s.%s" % k): v for k, v in known.items()})

# 2) 读表的行：先确定表起终点（col0 严格递增域内 fi）
# 找包含这些 fi 的行: 扫表 col0
rows = {}
import bisect
fis = []
off = TBL
# 表可能从 0x564210 前就开始了（run 起点），先从 run 起点扫 3 万行
i = 0
while i < 40000:
    o = TBL + i * 12
    if o + 12 > len(BUF):
        break
    fi = struct.unpack_from("<I", BUF, o)[0]
    if fi > 419567:
        break
    rows[fi] = (struct.unpack_from("<I", BUF, o + 4)[0],
                struct.unpack_from("<I", BUF, o + 8)[0],
                TBL + i * 12)
    i += 1
print("表行数(按 fi 索引):", len(rows), " fi 范围:", min(rows), "..", max(rows))

# 3) 已知字段的行
pool_guess = [0x1D79EA8, 0x1D79F08, 0x1D997F4]
for key, fi in sorted(known.items(), key=lambda kv: kv[1]):
    r = rows.get(fi)
    if not r:
        print("%s.%s fi=%d: 不在表内" % (key[0].split(".")[-1], key[1], fi))
        continue
    c1, c2, a = r
    # 试 pool @ col1/4 与 col2 直接当值
    vals = []
    for P in pool_guess:
        if P + c1 + 4 <= len(BUF):
            vals.append(struct.unpack_from("<I", BUF, P + c1)[0])
    print("%-14s.%-10s fi=%-6d c1=%-8d c2=%-8d pool@c1=%s" %
          (key[0].split(".")[-1], key[1], fi, c1, c2, [hex(v) for v in vals]))
