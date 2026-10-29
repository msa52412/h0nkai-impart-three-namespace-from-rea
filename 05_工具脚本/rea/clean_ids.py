#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清洗全文件扫描结果，分级并分析 ID 数组的位置结构。
"""
import re
import struct
from collections import Counter, defaultdict

INP = r"D:\Carol-start\_rea\bh3_all_ids.txt"
OUT_CLEAN = r"D:\Carol-start\_rea\bh3_strings_clean.txt"
OUT_REPORT = r"D:\Carol-start\_rea\bh3_scan_report.txt"

# 代码标识符字符集：字母数字 + 下划线 + 常见符号
IDENT = re.compile(r"^[A-Za-z_<\[][A-Za-z0-9_<>`\[\].\-]*$")
# 米哈游三段式
MM = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*(-[A-Za-z0-9_<>`\[\].]+){1,4}$")

rows = []
with open(INP, encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        off = int(parts[0], 16)
        pid = int(parts[1], 16)
        s = parts[2]
        rows.append((off, pid, s))

print("原始命中: %d" % len(rows))


def grade(s):
    if not s:
        return "X"
    # 必须全 ASCII
    try:
        s.encode("ascii")
    except UnicodeEncodeError:
        return "X"
    n = len(s)
    if n < 5:
        return "D"
    if MM.match(s) and n >= 10:
        return "A"        # 米哈游三段式，几乎肯定是真
    if IDENT.match(s) and n >= 8:
        # 驼峰或下划线分隔
        has_camel = re.search(r"[a-z][A-Z]", s) is not None
        has_sep = ("_" in s) or ("-" in s) or ("<" in s)
        if has_camel or has_sep:
            return "B"
        return "C"
    return "D"


buckets = defaultdict(list)
for off, pid, s in rows:
    g = grade(s)
    buckets[g].append((off, pid, s))

print("\n分级:")
for g in "ABCDX":
    print("  %s: %d" % (g, len(buckets[g])))

good = buckets["A"] + buckets["B"] + buckets["C"]
good.sort()

print("\n有效字符串 (A+B+C): %d" % len(good))

# 按 4KB 桶看聚集
bk = Counter((off >> 12) << 12 for off, _, _ in good)
print("\n有效字符串密度最高的 20 个 4KB 桶:")
for b, c in bk.most_common(20):
    print("  0x%08X  %3d 条" % (b, c))

# 找连续 ID 数组：相邻命中位置差 <= 8
print("\n--- 连续 ID 数组段（相邻间隔 <= 8 字节，长度 >= 20）---")
runs = []
cur = [good[0]] if good else []
for prev, nxt in zip(good, good[1:]):
    if nxt[0] - prev[0] <= 8:
        cur.append(nxt)
    else:
        if len(cur) >= 20:
            runs.append(cur)
        cur = [nxt]
if len(cur) >= 20:
    runs.append(cur)

runs.sort(key=len, reverse=True)
for r in runs[:15]:
    span = r[-1][0] - r[0][0]
    gaps = Counter(r[i + 1][0] - r[i][0] for i in range(len(r) - 1))
    main_gap = gaps.most_common(1)[0]
    print("  0x%08X - 0x%08X  %4d 条  跨度 0x%X  主间隔 %d 字节 (占 %d/%d)" %
          (r[0][0], r[-1][0], len(r), span, main_gap[0], main_gap[1], len(r) - 1))

with open(OUT_CLEAN, "w", encoding="utf-8") as f:
    for off, pid, s in good:
        f.write("%08X\t%s\n" % (off, s))
print("\n写出 %s (%d 条)" % (OUT_CLEAN, len(good)))

with open(OUT_REPORT, "w", encoding="utf-8") as f:
    f.write("原始命中 %d, 有效 %d\n" % (len(rows), len(good)))
    f.write("分级: A=%d B=%d C=%d D=%d X=%d\n\n" %
            (len(buckets["A"]), len(buckets["B"]), len(buckets["C"]),
             len(buckets["D"]), len(buckets["X"])))
    f.write("== 密度最高的 40 个 4KB 桶 ==\n")
    for b, c in bk.most_common(40):
        f.write("0x%08X\t%d\n" % (b, c))
    f.write("\n== 连续 ID 数组段 ==\n")
    for r in runs[:40]:
        f.write("0x%08X - 0x%08X\t%d 条\n" % (r[0][0], r[-1][0], len(r)))
print("写出 %s" % OUT_REPORT)

print("\n--- A 级（米哈游三段式）抽样 25 条 ---")
for off, pid, s in buckets["A"][:25]:
    print("  0x%08X  %s" % (off, s))
