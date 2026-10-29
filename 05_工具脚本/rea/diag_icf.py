#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_icf.py —— ICF 修复前后观测对比：WWW 样例 + P!/hole 计数预演"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, ".")
import bh3_layout6 as L


def load_obs(path):
    o = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            next(f)
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) < 2:
                    continue
                s = set()
                for x in p[1].split(","):
                    x = x.strip()
                    if x:
                        try:
                            s.add(int(x, 16))
                        except ValueError:
                            pass
                o[int(p[0])] = s
    except FileNotFoundError:
        pass
    return o


obs_old = load_obs("bh3_layout_obs_all.tsv")
obs_new = load_obs("bh3_layout_obs_all_v2.tsv")
obs3 = load_obs("bh3_layout_obs_3.tsv")


def obs_of2(o1, o2, ti):
    return o1.get(ti) or o2.get(ti) or set()


# 1) WWW 样例前后对比
ti = L.by_name.get("UnityEngine.WWW")
if ti:
    print("=== UnityEngine.WWW (typeIdx %d) ===" % ti)
    oo = obs_of2(obs_old, obs3, ti)
    on = obs_of2(obs_new, obs3, ti)
    fl, end = L.pack(ti)
    offs = sorted(x[4] for x in fl)
    print("打包字段起点: %s" % [hex(x) for x in offs])
    print("旧观测:       %s" % [hex(x) for x in sorted(oo)])
    print("新观测:       %s" % [hex(x) for x in sorted(on)])
    h1 = L.miss_breakdown(fl, end, oo)
    h2 = L.miss_breakdown(fl, end, on)
    print("旧 (hole,inside,beyond) = %s   miss=%s" % (h1, L.real_miss(fl, end, oo)))
    print("新 (hole,inside,beyond) = %s   miss=%s" % (h2, L.real_miss(fl, end, on)))

# 2) 全量指标预演
print()
print("=== 全量指标（新观测） ===")
nP = nPb = nPq = nobs = 0
b_hole = b_in = b_byd = 0
samples = []
for ti in L.types:
    fl, end = L.pack(ti)
    if not fl:
        continue
    o = obs_of2(obs_new, obs3, ti)
    if o:
        nobs += 1
        h, i_, b_ = L.miss_breakdown(fl, end, o)
        b_hole += h
        b_in += i_
        b_byd += b_
    m = L.real_miss(fl, end, o)
    if not o:
        nPq += 1
    elif m:
        nPb += 1
        if len(samples) < 10:
            samples.append((L.types[ti]["full"], end, sorted(o)[:8],
                            sorted(x[4] for x in fl)[:8], m[:4]))
    else:
        nP += 1
print("类型: P=%d  P!=%d  P?=%d  (P+P!=%d, 自洽率 %.2f%%)"
      % (nP, nPb, nPq, nP + nPb, 100.0 * nP / (nP + nPb)))
print("hole=%d  inside=%d  beyond=%d" % (b_hole, b_in, b_byd))
print()
print("剩余 P! 样例（前 10）:")
for nm, end, o, offs, m in samples:
    print("  %-55s end=0x%x" % (nm, end))
    print("     观测: %s" % [hex(x) for x in o])
    print("     打包: %s   空隙: %s" % ([hex(x) for x in offs], [hex(x) for x in m]))
