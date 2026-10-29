#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_internal.py —— 验证「A 类落空是内联结构体的子字段访问」

若成立：把每个内联结构体字段的内部偏移（递归）也加入覆盖集后，P! 应大幅下降，
且被吸收的落空偏移与结构体内部偏移逐一对应（不是随便凑）。

同时输出「吸收后仍落空」的残余，那才是真正的漏字段/尺寸错。
"""
import sys
import io
from collections import Counter

_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout5 as L                                   # noqa: E402
sys.stdout = _bak

types = L.types
kind_of, pack = L.kind_of, L.pack
obs_all, obs_3, clean_obs = L.obs_all, L.obs_3, L.clean_obs
known_size = getattr(L, "KNOWN_STRUCT_SIZE", {})


def primary(ti):
    return clean_obs(ti, (obs_all.get(ti) or obs_3.get(ti) or set()))


def covered_plus_internal(ti, fl):
    """字段起点 + 内联结构体的内部偏移（递归已由 pack 展平）"""
    s = set()
    for owner, fi, fn, ft, off, sz in fl:
        s.add(off)
        fti = L.by_name.get((ft or "").strip())
        if fti is None:
            continue
        if kind_of(fti) != "struct":
            continue
        sub, sub_end = pack(fti)
        for _o, _f, _n, _t, soff, _sz in sub:
            if soff < sz:                     # 只承认落在该字段字节范围内的子偏移
                s.add(off + soff)
    return s


P0 = Pb0 = Pq0 = 0
P1 = Pb1 = Pq1 = 0
absorbed = 0
resid = Counter()
resid_type = Counter()
multi = Counter()

for ti in sorted(types):
    if kind_of(ti) != "class":
        continue
    fl, end = pack(ti)
    if not fl:
        continue
    o = primary(ti)
    if not o:
        Pq0 += 1
        continue
    offs = {x[4] for x in fl}
    offs2 = covered_plus_internal(ti, fl)

    if o - offs:
        Pb0 += 1
    else:
        P0 += 1
    m2 = o - offs2
    if m2:
        Pb1 += 1
        for x in m2:
            resid[x] += 1
        resid_type[types[ti]["full"]] += 1
        multi[len(m2)] += 1
    else:
        P1 += 1
    absorbed += len((o - offs) - (o - offs2))

print("=" * 76)
print("覆盖集：字段起点")
print("  P=%d  P!=%d  P?=%d" % (P0, Pb0, Pq0))
print("覆盖集：字段起点 + 内联结构体内部偏移")
print("  P=%d  P!=%d  P?=%d" % (P1, Pb1, Pq1))
print("  被吸收的落空偏移: %d" % absorbed)
print()
print("残余落空偏移 TOP 20（真正需要修的）")
for x, c in resid.most_common(20):
    print("   0x%-5x %6d" % (x, c))
print()
print("残余落空个数分布")
for k in sorted(multi):
    print("   %d 个: %d" % (k, multi[k]))
print()
print("残余最多的类型 TOP 10")
for nm, c in resid_type.most_common(10):
    print("   %-56s %d" % (nm, c))
