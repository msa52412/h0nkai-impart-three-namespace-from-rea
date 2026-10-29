#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cg_hub2.py — 穿透编译器桩之后重算调用图 hub

为什么要重算
------------
第一版 cg_analyze.py 的入度 Top1 是 `FUN_1804fe400`（10 字节，946,440 次调用），
Top2/3/6/7/12/18 也全是 0x1804FE000 页里的 5 字节 `jmp rel32`。
这些是 MSVC 冷区跳板，不是业务函数，会把排名彻底搅乱。

本脚本做三件事：
  1. tailjmp 桩链穿透（最多 8 层），把边重定向到真实目标
  2. throw 桩单独归档：统计「异常抛出点」总数，按 noreturn 目标分组
  3. 重算入度/出度，输出「真实业务 hub」Top 列表

另外顺带回答两个问题：
  * 入度 0 的 24.9 万个函数真的是死代码吗？（→ 按「能否映射到 il2cpp 方法」拆分）
  * 热点 hub 的调用点落在函数体的什么位置？（→ 判断是不是序言检查）

输出：bh3_cg_hubs2.tsv / bh3_cg_throw.tsv
"""
import collections
import os
import sys

BASE = 0x180000000
D = os.path.dirname(os.path.abspath(__file__))
MADDR = os.path.join(D, "bh3_method_addr.tsv")
FUNCS = os.path.join(D, "bh3_cg_funcs.tsv")
EDGES = os.path.join(D, "bh3_cg_edges.tsv")
THUNKS = os.path.join(D, "bh3_thunks.tsv")
OUT_HUB = os.path.join(D, "bh3_cg_hubs2.tsv")
OUT_THROW = os.path.join(D, "bh3_cg_throw.tsv")

# ---------- 1. 桩表 ----------
tailjmp = {}
throw_of = {}
kind_of = {}
with open(THUNKS, encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) < 4:
            continue
        va = int(p[0], 16)
        kind = p[2]
        kind_of[va] = kind
        if p[3]:
            if kind == "tailjmp":
                tailjmp[va] = int(p[3], 16)
            elif kind == "throw":
                throw_of[va] = int(p[3], 16)
print("tailjmp 桩 %d 个，throw 桩 %d 个" % (len(tailjmp), len(throw_of)))


def resolve(va, depth=8):
    """穿透 tailjmp 链；返回 (最终目标, 穿透了几层)"""
    n = 0
    seen = set()
    while va in tailjmp and n < depth and va not in seen:
        seen.add(va)
        va = tailjmp[va]
        n += 1
    return va, n


# ---------- 2. 方法名 / 模块 ----------
va2method = {}
mod_of = {}
with open(MADDR, encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) < 7 or not p[3]:
            continue
        try:
            va = BASE + int(p[3], 16)
        except ValueError:
            continue
        va2method[va] = "%s::%s" % (p[4], p[5])
        mod_of[va] = p[2]
print("方法地址映射 %d 条" % len(va2method))

fn_body = {}
fn_name = {}
with open(FUNCS, encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) < 4:
            continue
        va = int(p[0], 16)
        fn_body[va] = int(p[1])
        fn_name[va] = p[3]
print("Ghidra 函数 %d 个" % len(fn_body))

# ---------- 3. 边上穿透 + 统计 ----------
indeg = collections.Counter()          # 穿透后入度（含 throw 桩）
outdeg = collections.Counter()
callers = collections.defaultdict(set)
throw_hits = collections.Counter()     # noreturn 目标 -> 抛出点次数
throw_callers = collections.defaultdict(set)
raw_to_stub = collections.Counter()    # 原始目标 -> 边数（看桩吃掉多少）
off_hist = collections.defaultdict(collections.Counter)   # hub -> 调用点偏移分布
n_edge = 0
n_collapsed = 0

WATCH = None      # 先跑一遍收集，再回填；这里用两遍策略：先统计 Top，再算偏移

# 第一遍：只做入度，记录 Top 后再补偏移太麻烦 —— 直接把每条的偏移都记下来代价太大。
# 折中：先把 (callee, insn-caller) 的偏移直方图只对「穿透后入度 >= 3000」的目标记录。
# 由于入度要全量跑完才知道，所以这里记录所有 偏移<=256 的样本到 Counter（约 4.37M 条，可接受）。

with open(EDGES, encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) < 3:
            continue
        c, t, insn = int(p[0], 16), int(p[1], 16), int(p[2], 16)
        t2, dep = resolve(t)
        if dep:
            n_collapsed += 1
        outdeg[c] += 1
        if t in throw_of:
            # throw 桩不是业务目标：边单独记，不进 indeg（否则异常桩霸榜）
            throw_hits[throw_of[t]] += 1
            throw_callers[throw_of[t]].add(c)
        else:
            indeg[t2] += 1
            callers[t2].add(c)
            d = insn - c
            if 0 <= d <= 4096:
                off_hist[t2][d] += 1
        raw_to_stub[t] += 1
        n_edge += 1

print("调用边 %d 条，其中穿透桩 %d 条 = %.1f%%"
      % (n_edge, n_collapsed, 100.0 * n_collapsed / n_edge))


def label(va):
    return va2method.get(va, fn_name.get(va, "FUN_%x" % va))


def sec_of(va):
    rva = va - BASE
    if 0x1000 <= rva < 0x52C800:
        return ".text"
    if 0x52E000 <= rva < 0x52E000 + 0x6727C00:
        return "il2cpp"
    return "?"


print("\n=== 业务 hub Top30（穿透 tailjmp + 剔除 throw 桩） ===")
print("  %-12s %8s %8s %8s  %-8s %s"
      % ("VA", "调用次数", "不同调用者", "body", "节", "方法"))
for va, cnt in indeg.most_common(30):
    print("  %-12x %8d %8d %8d  %-8s %s"
          % (va, cnt, len(callers[va]), fn_body.get(va, -1), sec_of(va), label(va)))

print("\n=== 出度 Top20（巨型分发/初始化函数） ===")
for va, cnt in outdeg.most_common(20):
    print("  %-12x %8d %-9s %s" % (va, cnt, fn_body.get(va, -1), label(va)))

print("\n=== 异常抛出点统计（throw 桩被调次数） ===")
tot_thr = sum(throw_hits.values())
for tgt, cnt in throw_hits.most_common(12):
    print("  noreturn 0x%-10X 抛出点 %8d 次，来自 %6d 个函数（%.1f%%）"
          % (tgt, cnt, len(throw_callers[tgt]), 100.0 * cnt / tot_thr))
print("  异常抛出点合计 %d = 全部边的 %.1f%%" % (tot_thr, 100.0 * tot_thr / n_edge))

print("\n=== 桩吃掉多少边 ===")
for va, c in raw_to_stub.most_common(10):
    tag = "tailjmp→%x" % tailjmp[va] if va in tailjmp else (
          "throw→%x" % throw_of[va] if va in throw_of else kind_of.get(va, "?"))
    print("  0x%-11X %8d 条  %s" % (va, c, tag))

# ---------- 4. 入度 0 拆解 ----------
iso = [va for va in fn_body if indeg.get(va, 0) == 0]
iso_named = [va for va in iso if va in va2method]
iso_unnamed = len(iso) - len(iso_named)
print("\n=== 入度 0 拆解 ===")
print("  总数 %d（%.1f%% of %d）" % (len(iso), 100.0 * len(iso) / len(fn_body), len(fn_body)))
print("    能映射到 il2cpp 方法 %6d  → 虚拟/委托/反射调用，无直接静态调用者"
      % len(iso_named))
print("    无方法名            %6d  → 辅助函数/桩/未被识别的入口" % iso_unnamed)
m_iso = collections.Counter(mod_of.get(va, "?") for va in iso_named)
print("  入度 0 的方法按模块 Top10：")
for m, c in m_iso.most_common(10):
    print("    %-42s %6d" % (m, c))

# ---------- 5. 调用点偏移分布 ----------
print("\n=== 热点 hub 的调用点偏移分布（判断是否为序言检查） ===")
for va in [v for v, _ in indeg.most_common(8)]:
    h = off_hist.get(va)
    if not h:
        continue
    tot = sum(h.values())
    at0 = h.get(0, 0)
    small = sum(c for d, c in h.items() if d <= 64)
    print("  0x%-11X %-52s 采样 %7d  偏移0: %5.1f%%  ≤64: %5.1f%%"
          % (va, label(va)[:52], tot, 100.0 * at0 / tot, 100.0 * small / tot))

# ---------- 6. 落盘 ----------
with open(OUT_HUB, "w", encoding="utf-8") as f:
    f.write("va\tindeg\tdistinct_callers\toutdeg\tbody\tsection\tmethod\tmodule\n")
    for va in sorted(fn_body, key=lambda v: -indeg.get(v, 0)):
        f.write("%x\t%d\t%d\t%d\t%d\t%s\t%s\t%s\n" % (
            va, indeg.get(va, 0), len(callers[va]), outdeg.get(va, 0),
            fn_body[va], sec_of(va), label(va), mod_of.get(va, "")))
print("\n写出 %s" % OUT_HUB)

with open(OUT_THROW, "w", encoding="utf-8") as f:
    f.write("noreturn_target\tsites\tdistinct_callers\n")
    for tgt, cnt in throw_hits.most_common():
        f.write("%x\t%d\t%d\n" % (tgt, cnt, len(throw_callers[tgt])))
print("写出 %s" % OUT_THROW)
