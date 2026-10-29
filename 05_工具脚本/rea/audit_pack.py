# -*- coding: utf-8 -*-
"""审计：对 /bh3/proto 下的类，按「全部字段都是实例字段」纯顺序对齐打包，
   与 bh3_layout.tsv 现有 offset 比对，统计偏差规模。

用法: python audit_pack.py [prefix=/bh3/proto] [limit=0]
"""
import sys
from collections import defaultdict

PREFIX = sys.argv[1] if len(sys.argv) > 1 else "/bh3/proto"
LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else 0

# ---- 读结构体表：typeIdx -> (catPath, name, size) ----
tinfo = {}
with open("bh3_structs.tsv", encoding="utf-8", errors="replace") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 7:
            continue
        ti = int(p[0])
        if not p[1].startswith(PREFIX):
            continue
        tinfo[ti] = (p[1], p[2], int(p[3]))

# ---- 读字段记录：typeIdx -> [(fieldIdx, name, typeName)] ----
fields = defaultdict(list)
with open("bh3_fields.tsv", encoding="utf-8", errors="replace") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 5:
            continue
        ti = int(p[0])
        if ti not in tinfo:
            continue
        fields[ti].append((int(p[2]), p[3], p[4]))

# ---- 读现有布局：typeIdx -> {fieldIdx: (offset, size, isStatic)} ----
cur = {}
with open("bh3_layout.tsv", encoding="utf-8", errors="replace") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 10:
            continue
        ti = int(p[0])
        if ti not in tinfo:
            continue
        cur[(ti, int(p[2]))] = (int(p[7]), int(p[5]), int(p[6]))


def align(x, a):
    if a <= 1:
        return x
    return (x + a - 1) // a * a


def fsize(sz):
    """字段对齐 = 自身对齐上限 8（第 4 步修正过的规则）"""
    return min(sz, 8) if sz > 0 else 1


n_types = 0
n_same = 0
n_diff = 0
shift_hist = defaultdict(int)     # 偏差字节数分布
n_static_marked = 0
n_shifted_field = 0
n_total_field = 0
samples = []

for ti, (cp, nm, size) in tinfo.items():
    fl = sorted(fields.get(ti, []))
    if not fl:
        continue
    n_types += 1
    if LIMIT and n_types > LIMIT:
        break
    # 纯打包
    packed = {}
    c = 16
    for fidx, fname, ftype in fl:
        rec = cur.get((ti, fidx))
        fsz = rec[1] if rec and rec[1] > 0 else 8
        a = fsize(fsz)
        c = align(c, a)
        packed[fidx] = (c, fsz)
        c += fsz
    packed_end = c

    # 与现有比对
    diffs = []
    nstat = 0
    for fidx, fname, ftype in fl:
        rec = cur.get((ti, fidx))
        n_total_field += 1
        if rec is None:
            continue
        off, fsz, isst = rec
        if isst:
            nstat += 1
            n_static_marked += 1
            continue
        po = packed[fidx][0]
        if off != po:
            diffs.append((fname, off, po, fsz))
            n_shifted_field += 1
    if diffs:
        n_diff += 1
        shift_hist[diffs[0][1] - diffs[0][2]] += 1
        if len(samples) < 12:
            samples.append((nm, size, packed_end, diffs[:4]))
    else:
        n_same += 1

print("prefix=%s  类型数=%d" % (PREFIX, n_types))
print("  完全一致     : %d (%.1f%%)" % (n_same, 100.0 * n_same / max(n_types, 1)))
print("  存在偏移差异 : %d (%.1f%%)" % (n_diff, 100.0 * n_diff / max(n_types, 1)))
print("  字段总数=%d  被标 static=%d (%.1f%%)  偏移不符字段=%d"
      % (n_total_field, n_static_marked,
         100.0 * n_static_marked / max(n_total_field, 1), n_shifted_field))
print("  首个差异(现有-打包) 分布 top10:")
for k, v in sorted(shift_hist.items(), key=lambda x: -x[1])[:10]:
    print("     %+d 字节 : %d 个类型" % (k, v))
print("  样例:")
for nm, size, pe, diffs in samples:
    print("   %-38s size=%-4d pack_end=%-4d" % (nm, size, pe))
    for fname, off, po, fsz in diffs:
        print("       %-24s 现有=0x%-4x 打包=0x%-4x size=%d" % (fname, off, po, fsz))
