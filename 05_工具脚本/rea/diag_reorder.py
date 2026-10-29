#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_reorder.py —— 检验「il2cpp 对 Auto 布局 class 按尺寸分组重排」假设

对每个 hole>0 的 class，构造两个候选布局：
  A. 元数据顺序（现行 pack）
  B. 按 (size 降序, 声明序) 稳定重排（引用 8 → 4 字节 → 1/2 字节）
比较 hole 数：若 B 系统性更优，说明 il2cpp 真的做了尺寸分组重排。
"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, ".")
import bh3_layout6 as L  # noqa: E402
from collections import Counter  # noqa: E402


def pack_by_order(fl_fields, base):
    """给定 [(fn, ft, s, a)] 序列，按顺序打包，返回 (offsets, end)"""
    cur = base
    maxa = 1
    out = []
    for fn, ft, s, a in fl_fields:
        maxa = max(maxa, a)
        cur = L.align(cur, a)
        out.append((fn, cur, s))
        cur += s
    return out, L.align(cur, maxa)


def holes_of(offsets, o):
    """观测中落在字段间空隙的偏移（class：0/8 视为对象头排除）"""
    starts = set(x[1] for x in offsets)
    eff = max(x[1] + x[2] for x in offsets) if offsets else 0
    cov = set()
    for _fn, off, s in offsets:
        cov.add(off)
        # 内联结构体合法内部偏移
    bad = 0
    for m in o:
        if m in cov or m in (0, 8):
            continue
        if m >= eff:
            continue
        if not any(off < m < off + s for _fn, off, s in offsets):
            bad += 1
    return bad


def main():
    better = worse = same = 0
    examples_better = []
    examples_worse = []
    for ti in L.types:
        if L.kind_of(ti) != "class":
            continue
        fl, end = L.pack(ti)
        if not fl:
            continue
        o = L.obs_of(ti)
        if not o:
            continue
        h_a = sum(1 for m in L.real_miss(fl, end, o))
        if h_a == 0:
            continue
        # 构造 B：按 size 降序稳定重排（只排本类型字段，基类布局维持 A）
        own = [x for x in fl if x[0] == ti]
        if len(own) < 2:
            continue
        base_end = max((x[4] + x[5] for x in fl if x[0] != ti), default=L.base_start(ti))
        own_sorted = sorted(own, key=lambda x: (-x[5], x[1]))
        seq = [(x[2], x[3], x[5], L.align_of_name(x[3])) for x in own_sorted]
        offs_b, end_b = pack_by_order(seq, base_end)
        h_b = holes_of(offs_b, o)
        if h_b < h_a:
            better += 1
            if len(examples_better) < 5:
                examples_better.append((L.types[ti]["full"], h_a, h_b))
        elif h_b > h_a:
            worse += 1
            if len(examples_worse) < 5:
                examples_worse.append((L.types[ti]["full"], h_a, h_b))
        else:
            same += 1
    print("hole>0 的 class 中（重排实验，仅排本类型字段）：")
    print("  重排后更好: %d   更差: %d   不变: %d" % (better, worse, same))
    for e in examples_better:
        print("  BETTER", e)
    for e in examples_worse:
        print("  WORSE ", e)


if __name__ == "__main__":
    main()
