#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dump_type.py —— 打印指定类型的完整「打包布局 vs 观测偏移」对照

用法: python dump_type.py <类型名> [类型名 ...]
      python dump_type.py --auto 8      自动挑 A 类落空最多的 8 个类型
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


def primary(ti):
    return clean_obs(ti, (obs_all.get(ti) or obs_3.get(ti) or set()))


def show(name, ti):
    t = types[ti]
    fl, end = pack(ti)
    o = primary(ti)
    offs = {x[4] for x in fl}
    miss = o - offs
    print("=" * 84)
    print("%s   ti=%d  kind=%s  打包尺寸=0x%x(%d)  观测=%d  覆盖=%d  落空=%d" % (
        t["full"], ti, kind_of(ti), end, end, len(o), len(o & offs), len(miss)))
    print("  观测: %s" % " ".join("%x" % x for x in sorted(o)))
    print("=" * 84)
    allpos = sorted(set(offs) | set(o))
    fmap = {x[4]: x for x in fl}
    for p in allpos:
        f = fmap.get(p)
        mk = "  ← 观测有、打包无  ✗" if (p in o and p not in offs) else ""
        if f:
            owner, fi, fn, ft, off, sz = f
            print("  0x%-4x %-34s %-42s size=%-4d %s" % (
                p, fn, ft, sz, mk))
        else:
            print("  0x%-4x %s" % (p, mk))


args = sys.argv[1:]
if not args:
    args = ["--auto", "6"]

names = []
if args[0] == "--auto":
    limit = int(args[1]) if len(args) > 1 else 6
    scored = []
    for ti in sorted(types):
        if kind_of(ti) != "class":
            continue
        fl, end = pack(ti)
        if not fl:
            continue
        o = primary(ti)
        offs = {x[4] for x in fl}
        miss = o - offs
        if not miss:
            continue
        na = 0
        for m in miss:
            for x in fl:
                if x[4] <= m < x[4] + x[5]:
                    na += 1
                    break
        if na:
            scored.append((na, types[ti]["full"]))
    scored.sort(reverse=True)
    names = [n for _, n in scored[:limit]]
else:
    names = args

for nm in names:
    ti = L.by_name.get(nm)
    if ti is None:
        print("!! 未找到类型: %s" % nm)
        continue
    show(nm, ti)
    print()
