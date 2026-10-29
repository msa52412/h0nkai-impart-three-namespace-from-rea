#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 408,458 条方法平铺成 188 个模块块。

约束：块 [p, p+c) 内 RID 集合必须恰为 {1..c}。
尺寸取自 RID 多重集还原（188 个，和 = 408458）。
贪心：p 处取「RID 互异的最长前缀」ℓ，则 c ≤ ℓ 且 c = max(RID[p..p+c)) 且 c ∈ 剩余多重集。
"""
import csv
from collections import Counter

rows = []
with open(r'D:\Carol-start\_rea\bh3_methods_v2.tsv', encoding='utf-8') as f:
    r = csv.reader(f, delimiter='\t')
    next(r)
    for a in r:
        rows.append(int(a[1], 16) & 0xFFFFFF)
n = len(rows)
print("方法 %d" % n)

sizes = Counter(int(x) for x in open(r'D:\Carol-start\_rea\_rid_sizes.txt'))
print("尺寸多重集 %d 个，和 %d" % (sum(sizes.values()), sum(k * v for k, v in sizes.items())))

# 每位置起「RID 互异最长前缀」
nxt = [0] * (n + 1)
last = {}
run = 0
distinct_end = [0] * n
i = n - 1
end = n
seen = {}
limit = [n] * n
lastpos = {}
for i in range(n - 1, -1, -1):
    rid = rows[i]
    if rid in lastpos:
        end = min(end, lastpos[rid])
    lastpos[rid] = i
    limit[i] = end
    # 该位置最长互异前缀长度 = limit[i] - i

pos = 0
blocks = []
remain = Counter(sizes)
maxc = max(sizes)
while pos < n:
    ℓ = limit[pos] - pos
    cand = None
    # 尝试：c 从大到小，需 c<=ℓ 且 RIDs[pos..pos+c) 的 max==c 且全在 1..c
    tried = 0
    for c in sorted([k for k in remain if remain[k] > 0 and k <= ℓ], reverse=True):
        tried += 1
        seg = rows[pos:pos + c]
        s = set(seg)
        if len(s) == c and max(s) == c:
            cand = c
            break
        if tried > 60:
            break
    if cand is None:
        print("  [失败] pos=%d ℓ=%d 剩余尺寸数=%d" % (pos, ℓ, len([k for k in remain if remain[k] > 0])))
        break
    blocks.append((pos, cand))
    remain[cand] -= 1
    pos += cand

print("平铺出块 %d 个，覆盖到 %d / %d" % (len(blocks), pos, n))
print("剩余尺寸:", {k: v for k, v in remain.items() if v > 0})

if pos == n and not any(v > 0 for v in remain.values()):
    with open(r'D:\Carol-start\_rea\bh3_method_blocks.tsv', 'w', encoding='utf-8') as f:
        f.write("idx\tstart\tcount\tmaxRID\n")
        for i, (st, c) in enumerate(blocks):
            f.write("%d\t%d\t%d\t%d\n" % (i, st, c, max(rows[st:st + c])))
    print("\n成功：已写 bh3_method_blocks.tsv")
    for i, (st, c) in enumerate(blocks[:15]):
        print("  块 %3d  start %7d  count %7d" % (i, st, c))
