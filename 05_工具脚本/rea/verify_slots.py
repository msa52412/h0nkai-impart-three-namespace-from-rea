# -*- coding: utf-8 -*-
"""验证 usage 槽区基址：反编译体里的 _DAT_18xxxxxxx 槽引用换算 dest 后应命中 strlit 映射"""
import re
from collections import Counter

# 1) 扫反编译体里的槽引用
pat = re.compile(r"DAT_1([0-9a-fA-F]{8})")
c = Counter()
with open(r"D:\Carol-start\_rea\bodies_merged.tsv", "rb") as f:
    for chunk in iter(lambda: f.read(1 << 24), b""):
        for mfind in pat.finditer(chunk.decode("latin-1")):
            c[mfind.group(1).upper()] += 1

slots = sorted(int(a, 16) for a in c)
print("全部 DAT_18 引用: %d 个不同地址" % len(slots))

# 2) usage 槽区（0x189900000..0x189B00000）
region = [a for a in slots if 0x189900000 <= a <= 0x189B00000]
print("槽区引用: %d 个, 范围 0x%X..0x%X" % (len(region), region[0], region[-1]))

# 3) 映射表
m = {}
for ln in open(r"D:\Carol-start\_rea\bh3_strlit_map.tsv", encoding="utf-8"):
    p = ln.rstrip("\r\n").split("\t")
    if p[0] != "destIdx" and len(p) >= 3:
        m[int(p[0])] = p[2]
print("映射条目:", len(m))

# 4) 四个候选基址逐一验证
for base in (0x1899DE380, 0x189A648B0, 0x189B4A190, 0x189B48870):
    hits = 0
    for a in region:
        d = a - base
        if d >= 0 and d % 8 == 0 and d // 8 in m:
            hits += 1
    print("base 0x%X: 命中 %d / %d" % (base, hits, len(region)))

# 5) 最热槽的 top10 都查一遍（0x1899DE380 基）
print("\n最热槽 10 个（base=0x1899DE380）:")
base = 0x1899DE380
for a, n in sorted(c.items(), key=lambda kv: -kv[1])[:10]:
    addr = int(a, 16)
    d = addr - base
    txt = m.get(d // 8, "<映射外>")[:40] if d >= 0 and d % 8 == 0 else "<非 8 对齐/负偏移>"
    print("  0x%X x%-5d dest=%-7d %s" % (addr, n, d // 8 if d >= 0 and d % 8 == 0 else -1, txt))
