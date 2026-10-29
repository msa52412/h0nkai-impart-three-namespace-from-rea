#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cg_path.py — 沿调用图做「向上追根 / 向下展开」

用法：
    python cg_path.py up   0x180043FC0 [0x18003EC20 ...]  --depth 6
    python cg_path.py down 0x180043FC0 --depth 3

为什么需要
----------
路线 B 已经定位到 metadata 解密的各个零件（LoadMetadataFile / 记录读取器 /
两个 XOR 常量表 …），但它们「被谁在什么时候调用」一直靠人肉 xref。
全量调用图（429,850 函数 / 4,373,442 边）导出来之后，可以一次性把
「向上追到 DllMain / il2cpp_init」和「向下展开完整解密流水线」都算出来。

关键细节：
  * 边里的 callee 可能是 tailjmp 桩，必须穿透（复用 bh3_thunks.tsv）
  * 向上追时只走「直接调用」边；虚调用/间接调用在静态图里没有边，
    所以追不到根 ≠ 没有调用者，要在报告里写清楚
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

tailjmp = {}
with open(THUNKS, encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 4 and p[2] == "tailjmp" and p[3]:
            tailjmp[int(p[0], 16)] = int(p[3], 16)


def resolve(va):
    n = 0
    while va in tailjmp and n < 8:
        va = tailjmp[va]
        n += 1
    return va


va2method, mod_of = {}, {}
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

fn_body, fn_name = {}, {}
with open(FUNCS, encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) < 4:
            continue
        fn_body[int(p[0], 16)] = int(p[1])
        fn_name[int(p[0], 16)] = p[3]


def label(va):
    return va2method.get(va) or fn_name.get(va) or ("FUN_%x" % va)


up = collections.defaultdict(set)
down = collections.defaultdict(set)
with open(EDGES, encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) < 3:
            continue
        c, t = int(p[0], 16), resolve(int(p[1], 16))
        up[t].add(c)
        down[c].add(t)
print("图已载入：%d 个有出边的函数 / %d 个有入边的函数" % (len(down), len(up)))


def walk(start, adj, depth, name):
    seen = {start: 0}
    q = collections.deque([start])
    levels = collections.defaultdict(list)
    while q:
        cur = q.popleft()
        d = seen[cur]
        if d >= depth:
            continue
        for nx in adj.get(cur, ()):
            if nx in seen:
                continue
            seen[nx] = d + 1
            levels[d + 1].append(nx)
            q.append(nx)
    print("\n--- %s 展开（深度 %d，共 %d 个节点）---" % (name, depth, len(seen) - 1))
    for lv in sorted(levels):
        row = levels[lv]
        print("  L%d  %d 个" % (lv, len(row)))
        for va in row[:24]:
            print("      %-11x body=%-7s %s" % (va, fn_body.get(va, "-"), label(va)))
        if len(row) > 24:
            print("      ...（另 %d 个）" % (len(row) - 24))
    roots = [v for v in seen if v != start and not up.get(v)]
    if roots:
        print("  其中「无进一步直接调用者」的根节点 %d 个：" % len(roots))
        for va in roots[:12]:
            print("      %-11x %s" % (va, label(va)))


def main():
    mode = sys.argv[1]
    depth = 4
    if "--depth" in sys.argv:
        depth = int(sys.argv[sys.argv.index("--depth") + 1])
    targets = []
    for a in sys.argv[2:]:
        if a.startswith("--"):
            break
        targets.append(int(a, 16))

    for t in targets:
        print("\n" + "=" * 78)
        print("目标 0x%X  %s  body=%s" % (t, label(t), fn_body.get(t, "-")))
        if mode == "up":
            walk(t, up, depth, "向上（谁调用它）")
        else:
            walk(t, down, depth, "向下（它调用谁）")


if __name__ == "__main__":
    main()
