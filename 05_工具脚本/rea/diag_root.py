#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_root.py —— 把残余落空归因到「定义该区间的类型」，找出根因基类

原理：pack(S) 里每个字段都带 owner（它定义在继承链的哪一层）。若类型 S 的某个
观测偏移 m 落空，取 m 之前最近的字段，它的 owner=B 说明 m 就在 B 的区间里
——错误很可能出在 B（或 B 的某个基类），而不在 S。

因为基类只算一次，一个基类错会让它**所有子类**都报同一批落空偏移。
所以按 owner 聚合能直接排出根因榜；修一个基类等于修一片。
"""
import sys
import io
from collections import Counter, defaultdict

_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout5 as L                                   # noqa: E402
sys.stdout = _bak

types = L.types
kind_of, pack = L.kind_of, L.pack
obs_all, obs_3, clean_obs = L.obs_all, L.obs_3, L.clean_obs


def primary(ti):
    return clean_obs(ti, (obs_all.get(ti) or obs_3.get(ti) or set()))


def covered_plus_internal(fl):
    s = set()
    for owner, fi, fn, ft, off, sz in fl:
        s.add(off)
        fti = L.by_name.get((ft or "").strip())
        if fti is None or kind_of(fti) != "struct":
            continue
        sub, _ = pack(fti)
        for _o, _f, _n, _t, soff, _sz in sub:
            if soff < sz:
                s.add(off + soff)
    return s


own_miss = Counter()          # 归到 owner 的落空次数
own_child = defaultdict(set)  # owner -> 受影响子类集合
own_gap = Counter()           # (owner, gap) -> 次数
self_miss = Counter()         # 落空落在类型自身区间（不是基类问题）
tail_by_owner = Counter()

for ti in sorted(types):
    if kind_of(ti) != "class":
        continue
    fl, end = pack(ti)
    if not fl:
        continue
    o = primary(ti)
    if not o:
        continue
    cov = covered_plus_internal(fl)
    miss = o - cov
    if not miss:
        continue
    fl_sorted = sorted(fl, key=lambda x: x[4])
    for m in miss:
        pred = None
        for f in fl_sorted:
            if f[4] <= m:
                pred = f
            else:
                break
        if pred is None:
            continue
        if m >= end:
            tail_by_owner[pred[0]] += 1
            continue
        b = pred[0]
        own_miss[b] += 1
        own_child[b].add(ti)
        own_gap[(b, m - (pred[4] + pred[5]))] += 1
        if b == ti:
            self_miss[ti] += 1

print("=" * 90)
print("根因榜：按「落空归属类型」聚合（影响子类数 = 修好它能连带修好的类型数）")
print("=" * 90)
print("%-56s %8s %8s" % ("归属类型", "影响子类", "落空次数"))
rank = sorted(own_child.items(), key=lambda kv: (-len(kv[1]), -own_miss[kv[0]]))
for b, ch in rank[:30]:
    print("%-56s %8d %8d" % (types[b]["full"][:56], len(ch), own_miss[b]))

print()
print("=" * 90)
print("尾部漏字段：按最后一个字段的归属类型聚合")
print("=" * 90)
for b, c in tail_by_owner.most_common(15):
    print("%-56s %8d" % (types[b]["full"][:56], c))

print()
print("=" * 90)
print("根因类型自身的落空情况（落在自己定义的区间里）")
print("=" * 90)
for b, c in self_miss.most_common(15):
    print("%-56s %8d" % (types[b]["full"][:56], c))

print()
print("=" * 90)
print("TOP 12 根因基类的典型空隙")
print("=" * 90)
for b, ch in rank[:12]:
    gs = Counter()
    for (bb, g), c in own_gap.items():
        if bb == b:
            gs[g] += c
    print("%-50s → %s" % (types[b]["full"][:50],
                          ", ".join("+%d×%d" % (g, c) for g, c in gs.most_common(6))))
