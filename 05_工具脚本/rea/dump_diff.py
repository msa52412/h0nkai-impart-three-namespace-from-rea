#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dump_diff.py —— 只看某个类型的「落空偏移」及其覆盖字段

用法: python dump_diff.py <类型名>
      python dump_diff.py --boolgap <N>    找出「bool 后空隙 = N」的类型
"""
import sys
import io

_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout5 as L                                   # noqa: E402
sys.stdout = _bak

types = L.types
kind_of, pack = L.kind_of, L.pack
obs_all, obs_3, clean_obs = L.obs_all, L.obs_3, L.clean_obs


def primary(ti):
    return clean_obs(ti, (obs_all.get(ti) or obs_3.get(ti) or set()))


def diff(name):
    ti = L.by_name.get(name)
    if ti is None:
        print("未找到 %s" % name)
        return
    fl, end = pack(ti)
    o = primary(ti)
    offs = {x[4] for x in fl}
    miss = sorted(o - offs)
    fl_sorted = sorted(fl, key=lambda x: x[4])
    print("=" * 88)
    print("%s  ti=%d  打包=0x%x  观测=%d  覆盖=%d  落空=%d" % (
        name, ti, end, len(o), len(o & offs), len(miss)))
    print("=" * 88)
    for m in miss:
        cov = None
        pred = None
        for f in fl_sorted:
            if f[4] <= m:
                pred = f
            if f[4] <= m < f[4] + f[5]:
                cov = f
                break
        if cov:
            print("  miss 0x%-4x  落在 <%s %s@0x%x+%d> 内 (+%d)" % (
                m, cov[2], cov[3], cov[4], cov[5], m - cov[4]))
        elif m >= end:
            print("  miss 0x%-4x  超出末尾 0x%x (+%d)   最后字段 <%s %s@0x%x+%d>" % (
                m, end, m - end, pred[2], pred[3], pred[4], pred[5]))
        else:
            print("  miss 0x%-4x  空隙  pred=<%s %s@0x%x+%d>  gap=%d" % (
                m, pred[2], pred[3], pred[4], pred[5], m - (pred[4] + pred[5])))


def find_boolgap(n):
    cnt = 0
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
        fl_sorted = sorted(fl, key=lambda x: x[4])
        for m in miss:
            pred = None
            inside = False
            for f in fl_sorted:
                if f[4] <= m:
                    pred = f
                if f[4] <= m < f[4] + f[5]:
                    inside = True
                    break
            if inside or pred is None or m >= end:
                continue
            if pred[5] == 1 and m - (pred[4] + pred[5]) == n:
                print("\n>>> %s  ti=%d" % (types[ti]["full"], ti))
                diff(types[ti]["full"])
                cnt += 1
                if cnt >= 3:
                    return


a = sys.argv[1:]
if a and a[0] == "--boolgap":
    find_boolgap(int(a[1]) if len(a) > 1 else 3)
else:
    for nm in a:
        diff(nm)
