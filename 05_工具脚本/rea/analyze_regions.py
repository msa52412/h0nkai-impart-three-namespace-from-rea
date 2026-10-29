# -*- coding: utf-8 -*-
"""分析槽区命中/未命中的地址分段结构"""
import re
from collections import Counter

pat = re.compile(r"DAT_1([0-9a-fA-F]{8})")
c = Counter()
with open(r"D:\Carol-start\_rea\bodies_merged.tsv", "rb") as f:
    for chunk in iter(lambda: f.read(1 << 24), b""):
        for mm in pat.finditer(chunk.decode("latin-1")):
            c[0x100000000 | int(mm.group(1), 16)] += 1
region = sorted(a for a in c if 0x189900000 <= a <= 0x189B00000)

m = {}
for ln in open(r"D:\Carol-start\_rea\bh3_strlit_map.tsv", encoding="utf-8"):
    p = ln.rstrip("\r\n").split("\t")
    if p[0] != "destIdx" and len(p) >= 3:
        m[int(p[0])] = p[2]

base = 0x1899DE380
hs = set()
for a in region:
    d = a - base
    if d >= 0 and d % 8 == 0 and d // 8 in m:
        hs.add(a)
hit_a = [a for a in region if a in hs]
miss_a = [a for a in region if a not in hs]
print("命中槽范围: 0x%X..0x%X (%d 个)" % (hit_a[0], hit_a[-1], len(hit_a)))
print("未命中范围: 0x%X..0x%X (%d 个)" % (miss_a[0], miss_a[-1], len(miss_a)))
h = Counter(a >> 20 for a in miss_a)
print("未命中按 1MB 段:", dict(sorted(h.items())))
# 命中的 dest 分布上限
dests = sorted((a - base) // 8 for a in hit_a)
print("命中 dest 范围: %d..%d" % (dests[0], dests[-1]))
# 映射表覆盖 0..116710，命中 77049 —— 未命中但在 [0,116710*8) 内的槽：
in_rng_miss = [a for a in miss_a if 0 <= a - base < 116711 * 8]
print("在映射范围内但未命中的槽: %d 个" % len(in_rng_miss))
