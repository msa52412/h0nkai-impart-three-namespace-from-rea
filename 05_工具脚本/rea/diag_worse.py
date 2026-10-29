#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_worse.py —— 逐条拆解「v6 落空数反而变多」的类型

用法: python diag_worse.py [数量]
      python diag_worse.py --type System.Security.Cryptography.RC2

对每个样本同时跑 v5 与 v6 的 pack，列出：
  · v6 的 real_miss 偏移，以及每个偏移的几何归属（超尾 / 空隙 / 字段内噪声）
  · v5 在同一批偏移上为什么「不算落空」—— 是被哪个 static 字段挡住了
"""
import sys
import io

_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout6 as V6                                  # noqa: E402
sys.stdout = _bak

types = V6.types
by_name = V6.by_name

# v5 用同样的观测/口径，只换 pack
import importlib.util                                     # noqa: E402

spec = importlib.util.spec_from_file_location("v5", "bh3_layout5.py")
sys.stdout = io.StringIO()
V5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V5)
sys.stdout = _bak


def obs_primary(mod, ti):
    return mod.clean_obs(ti, mod.obs_of(ti))


def classify(mod, fl, end, o):
    """返回 [(offset, 类别)]
    类别: tail=超尾 / gap=空隙 / noise=落在字段字节内但非合法内部偏移
    """
    cov = mod.covered_set(fl)
    out = []
    for m in sorted(o):
        if m in cov:
            continue
        if m >= end:
            out.append((m, "tail"))
            continue
        hit = None
        for owner, fi, fn, ft, off, sz in fl:
            if off < m < off + sz:
                hit = (owner, fn, ft, off, sz)
                break
        if hit:
            out.append((m, "noise", hit))
        else:
            out.append((m, "gap"))
    return out


def dump(name, verbose=True):
    ti = by_name.get(name)
    if ti is None:
        print("!! 未找到类型: %s" % name)
        return None
    o = obs_primary(V6, ti)

    fl6, end6 = V6.pack(ti)
    miss6 = V6.real_miss(fl6, end6, o)
    fl5, end5 = V5.pack(ti)
    miss5 = V5.real_miss(fl5, end5, o)

    print("=" * 90)
    print("%s  ti=%d" % (name, ti))
    print("  v6: 尺寸=0x%-4x 字段=%-3d 落空=%d %s" % (
        end6, len(fl6), len(miss6),
        ",".join("0x%x" % x for x in miss6)))
    print("  v5: 尺寸=0x%-4x 字段=%-3d 落空=%d %s" % (
        end5, len(fl5), len(miss5),
        ",".join("0x%x" % x for x in miss5)))
    print("  观测: %s" % " ".join("0x%x" % x for x in sorted(o)))
    if not verbose:
        return (name, len(miss5), len(miss6))

    # v6 的落空逐条归因
    cls6 = classify(V6, fl6, end6, o)
    # v5 的落空集合
    s5 = set(miss5)
    for item in cls6:
        m, cat = item[0], item[1]
        tag = "v5也落空" if m in s5 else "v5未落空"
        if cat == "noise":
            _ow, fn, ft, off, sz = item[2]
            print("   0x%-4x  %-8s %-10s  被 0x%x 的 %s(%s,size=%d) 覆盖  ← %s" % (
                m, cat, "", off, fn, ft, sz, tag))
        elif cat == "tail":
            print("   0x%-4x  %-8s %-10s  超出 v6 末尾 0x%x（v5 末尾 0x%x）  ← %s" % (
                m, cat, "", end6, end5, tag))
        else:
            print("   0x%-4x  %-8s %-10s  v6 无可覆盖字段  ← %s" % (m, cat, "", tag))

    # v6 有、v5 没有的字段（多半是 v5 剔掉的实例字段）
    n6 = {(fi, fn) for _o, fi, fn, _t, _of, _s in fl6}
    n5 = {(fi, fn) for _o, fi, fn, _t, _of, _s in fl5}
    only6 = n6 - n5
    only5 = n5 - n6
    if only6:
        print("  仅 v6 有（v5 当 static 剔掉了）:")
        for fi, fn in sorted(only6, key=lambda x: x[1])[:40]:
            ft = next((x[3] for x in fl6 if x[1] == fi), "?")
            print("     %-40s %s" % (fn, ft))
    if only5:
        print("  仅 v5 有（v6 判为 static/literal）:")
        for fi, fn in sorted(only5, key=lambda x: x[1])[:40]:
            ft = next((x[3] for x in fl5 if x[1] == fi), "?")
            print("     %-40s %s" % (fn, ft))
    return (name, len(miss5), len(miss6))


args = sys.argv[1:]
if not args:
    # 默认：挑 v6 比 v5 差得最多的
    rows = []
    for ti in sorted(types):
        if V6.kind_of(ti) != "class":
            continue
        o = obs_primary(V6, ti)
        if not o:
            continue
        fl6, end6 = V6.pack(ti)
        if not fl6:
            continue
        fl5, end5 = V5.pack(ti)
        a = len(V5.real_miss(fl5, end5, o))
        b = len(V6.real_miss(fl6, end6, o))
        if b > a:
            rows.append((b - a, b, a, types[ti]["full"]))
    rows.sort(reverse=True)
    print("v6 变差类型共 %d 个，总增 %d 个落空" % (len(rows), sum(r[0] for r in rows)))
    for d, b, a, nm in rows[:12]:
        print("   +%-3d  %-56s v5=%d  v6=%d" % (d, nm, a, b))
    print()
    for _d, _b, _a, nm in rows[:6]:
        dump(nm)
        print()
elif args[0] == "--type":
    for nm in args[1:]:
        dump(nm)
        print()
else:
    n = int(args[0])
    rows = []
    for ti in sorted(types):
        if V6.kind_of(ti) != "class":
            continue
        o = obs_primary(V6, ti)
        if not o:
            continue
        fl6, end6 = V6.pack(ti)
        if not fl6:
            continue
        fl5, end5 = V5.pack(ti)
        a = len(V5.real_miss(fl5, end5, o))
        b = len(V6.real_miss(fl6, end6, o))
        if b > a:
            rows.append((b - a, b, a, types[ti]["full"]))
    rows.sort(reverse=True)
    for _d, _b, _a, nm in rows[:n]:
        dump(nm)
        print()
