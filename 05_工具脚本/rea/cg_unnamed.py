#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cg_unnamed.py — 按入度统计「仍未命名」的被调函数

之前那版统计有 bug：用 bh3_method_addr.tsv 判定是否命名，而该表只含
「元数据里有 C# 方法」的函数；il2cpp 运行时/桥接/桩函数本来就不在表里，
于是把已经被 ApplySymbols 命名的函数也一律当成未命名（得出「未命名 =
全部被调函数」的荒谬结论）。

正确做法：以 Ghidra 里函数**当前的真实名字**为准（names_all.tsv 导出），
只有名字仍形如 FUN_ / thunk_FUN_ / SUB_ 才算未命名。

用法: python cg_unnamed.py names_all.tsv [topN]
"""
import sys, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
EDGES = os.path.join(HERE, "bh3_cg_edges.tsv")

AUTO_PREFIX = ("FUN_", "thunk_FUN_", "SUB_", "thunk_SUB_", "LAB_")


def main():
    names_path = sys.argv[1] if len(sys.argv) > 1 else "names_all.tsv"
    topn = int(sys.argv[2]) if len(sys.argv) > 2 else 40

    # 1) Ghidra 真实名字
    name = {}
    size = {}
    isthunk = {}
    with open(names_path, "r", encoding="utf-8", errors="replace") as f:
        hdr = f.readline()
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 3:
                continue
            va = int(p[0], 16)
            name[va] = p[1]
            try:
                size[va] = int(p[2])
            except ValueError:
                size[va] = 0
            isthunk[va] = (len(p) > 3 and p[3].strip() == "1")

    def is_auto(n):
        return n.startswith(AUTO_PREFIX)

    # 2) 入度
    indeg = collections.Counter()
    total_edges = 0
    with open(EDGES, "r", encoding="utf-8", errors="replace") as f:
        f.readline()
        for ln in f:
            p = ln.split("\t")
            if len(p) < 2:
                continue
            total_edges += 1
            indeg[int(p[1], 16)] += 1

    # 3) 分组
    named_edges = 0
    auto_edges = 0
    unk_edges = 0          # 被调地址在 Ghidra 里没有函数（数据/外部/未识别）
    auto_funcs = 0
    named_funcs = 0
    for va, c in indeg.items():
        n = name.get(va)
        if n is None:
            unk_edges += c
        elif is_auto(n):
            auto_edges += c
            auto_funcs += 1
        else:
            named_edges += c
            named_funcs += 1

    print("调用边总数            : %d" % total_edges)
    print("被调函数去重数        : %d" % len(indeg))
    print("  ├ 已具名            : %7d 个函数, %9d 条边 (%.1f%%)"
          % (named_funcs, named_edges, 100.0 * named_edges / total_edges))
    print("  ├ 仍是自动名 FUN_   : %7d 个函数, %9d 条边 (%.1f%%)"
          % (auto_funcs, auto_edges, 100.0 * auto_edges / total_edges))
    print("  └ 无对应函数        : %7d 个地址, %9d 条边 (%.1f%%)"
          % (len(indeg) - named_funcs - auto_funcs, unk_edges,
             100.0 * unk_edges / total_edges))
    print()

    # 4) 自动名的 Top N
    rows = []
    for va, c in indeg.items():
        n = name.get(va)
        if n is None or not is_auto(n):
            continue
        rows.append((c, va, n, size.get(va, 0), isthunk.get(va, False)))
    rows.sort(reverse=True)

    print("Top %d 未命名（按入度）" % topn)
    print("%-12s %9s %6s %3s  %s" % ("VA", "入度", "字节", "thk", "名字"))
    for c, va, n, s, t in rows[:topn]:
        print("%-12X %9d %6d %3s  %s" % (va, c, s, "T" if t else "", n))

    # 5) 按入度区间分布，判断「命名多少个能覆盖多少调用」
    print()
    print("覆盖率模拟：命名 Top K 个未命名函数后，自动名调用边剩余多少")
    cum = 0
    marks = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    mi = 0
    for i, (c, va, n, s, t) in enumerate(rows, 1):
        cum += c
        while mi < len(marks) and i == marks[mi]:
            print("  Top %-6d 覆盖 %9d 条边 (占自动名边 %.1f%%)，剩余 %d"
                  % (i, cum, 100.0 * cum / auto_edges, auto_edges - cum))
            mi += 1


if __name__ == "__main__":
    main()
