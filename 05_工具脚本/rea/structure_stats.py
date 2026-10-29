#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对清洗后的字符串做结构化统计，输出游戏内部结构概览。
"""
import re
from collections import Counter, defaultdict

INP = r"D:\Carol-start\_rea\bh3_strings_clean.txt"
OUT = r"D:\Carol-start\_rea\bh3_structure_overview.txt"

rows = []
with open(INP, encoding="utf-8") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) == 2:
            rows.append((int(p[0], 16), p[1]))

print("读取 %d 条" % len(rows))

# 三段式：命名空间-类-方法
three = []
two = []
single = []
for off, s in rows:
    parts = s.split("-")
    if len(parts) >= 3:
        three.append((off, parts))
    elif len(parts) == 2:
        two.append((off, parts))
    else:
        single.append((off, s))

print("三段式 %d / 两段式 %d / 单段 %d" % (len(three), len(two), len(single)))

ns = Counter(p[0] for _, p in three)
cls = Counter(p[1] for _, p in three)
meth = Counter(p[-1] for _, p in three)

print("\n=== 顶层命名空间 Top 30 ===")
for k, c in ns.most_common(30):
    print("  %-40s %5d" % (k, c))

print("\n=== 类名 Top 30 ===")
for k, c in cls.most_common(30):
    print("  %-50s %4d 方法" % (k, c))

print("\n=== 方法名 Top 30 ===")
for k, c in meth.most_common(30):
    print("  %-45s %4d" % (k, c))

# 模块分类：MoleMole-XXX 里的 XXX
mods = Counter()
for _, p in three:
    if p[0].startswith("MoleMole") and len(p) >= 3:
        mods[p[1]] += 1

print("\n=== 按类名统计最多的 20 个（含方法数）===")
for k, c in cls.most_common(20):
    print("  %s  -> %d" % (k, c))

# 关键业务词
KEYS = ["Battle", "Avatar", "Weapon", "Monster", "Skill", "Level", "Quest",
        "Activity", "Shop", "Gacha", "Tower", "World", "Story", "Mission",
        "Team", "Item", "Material", "Player", "UI", "Dialog", "Config"]
print("\n=== 业务领域命中统计 ===")
for kw in KEYS:
    n = sum(1 for _, s in rows if kw.lower() in s.lower())
    if n:
        print("  %-12s %5d" % (kw, n))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("# 崩坏3 metadata 字符串结构概览\n\n")
    f.write("总计有效字符串: %d\n" % len(rows))
    f.write("三段式 %d / 两段式 %d / 单段 %d\n\n" % (len(three), len(two), len(single)))
    f.write("== 顶层命名空间 ==\n")
    for k, c in ns.most_common():
        f.write("%-45s %5d\n" % (k, c))
    f.write("\n== 类名 Top 200 ==\n")
    for k, c in cls.most_common(200):
        f.write("%-60s %4d\n" % (k, c))
    f.write("\n== 方法名 Top 200 ==\n")
    for k, c in meth.most_common(200):
        f.write("%-50s %4d\n" % (k, c))
    f.write("\n== 全部三段式全名 ==\n")
    for _, p in sorted(three, key=lambda x: "-".join(x[1])):
        f.write("-".join(p) + "\n")

print("\n写出 %s" % OUT)
