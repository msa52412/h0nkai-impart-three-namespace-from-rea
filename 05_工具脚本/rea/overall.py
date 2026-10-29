#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""overall.py — 一眼看全「崩坏3 源码还原」的整体进度

用法:
    python overall.py          # 打一次
    python overall.py -w 60    # 每 60 秒刷新

分四块：
    A. 反编译体导出   —— 双机实时覆盖 / 速率 / 缺口 / ETA
    B. 方法还原率     —— 已导出的原生地址反查回 C# 方法，算「有真实函数体的方法占比」
    C. 源码树规模     —— 本地 src/ 的文件数、体积、类型/方法数
    D. 路线图         —— 11 个步骤各自的状态 + 仍未展开的待办

B 是唯一能回答「现在到底还原了多少 C#」的指标：
光看地址进度会高估（头部地址被上千个方法共用），
光看文件数会低估（签名和字段早就齐了，只差函数体）。
"""
import argparse
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "_pylibs"))
sys.path.insert(0, HERE)

import dual_prog

TOTAL_ADDR = 311382
TOTAL_METHODS = 408458

# 路线图：(编号, 名称, 状态, 说明)
ROADMAP = [
    ("1",  "字符串批量提取",        "done",  "34,949 条"),
    ("2",  "类型表",                "done",  "57,487 个（含 namespace/token/嵌套/parent）"),
    ("3",  "字段表",                "done",  "419,568 个（含类型）"),
    ("4",  "实例字段偏移还原",       "done",  "顺序打包求解，地面真值 8/9 命中"),
    ("5",  "字段布局写回 Ghidra",    "done",  "46,147 结构体 / 704,396 字段 / 118,756 个 this 重定型"),
    ("6",  "参数签名写回",          "done",  "303,143 函数 / 271,753 参数带真实类型"),
    ("7",  "属性 / 事件表",         "done",  "56,137 属性 / 415 事件"),
    ("8",  "热点未命名函数命名",     "done",  "13 个符号，未命名调用边 59.6%→17.4%"),
    ("9",  "源码树生成",            "done",  "467 个 .cs，57,487 类型 / 408,458 方法"),
    ("10", "嵌套类型归位",          "done",  "21,429 个嵌套类型 → 10,390 个父类"),
    ("11", "反编译体全量导出",       "done",  "311,382 个地址，双机并行完成；97.5% 方法有真实函数体"),
]

TODO = [
    ("P1", "剩余 6 个未命名热点函数", "Ghidra 已空闲，可以开工了"),
    ("P1", "static 字段混进实例布局", "6,812 个 P! 类型；判据：只被 .cctor 写、从不被 .ctor 写"),
    ("P2", "枚举无数值",             "8,547 个枚举只有成员名与顺序，常量表未解"),
    ("P2", "没有 attribute",         "CustomAttribute 表未解"),
    ("P2", "调用点未跟着更新",        "改签名后需在 Ghidra 里 Re-analyze"),
    ("P3", "早期 probe 命名残留",     "如 probe_186ad0af0，需按地址清理"),
    ("P3", "65 个地址反编译失败",     "104 有 58 个 / 105 有 7 个 empty，可单独重试"),
]


def bar(frac, width=42):
    k = max(0, min(width, int(frac * width)))
    return "█" * k + "·" * (width - k)


def fmt_secs(s):
    if not s or s <= 0:
        return "—"
    return "%.0f 分钟" % (s / 60) if s < 3600 else "%.1f 小时" % (s / 3600)


# ---------- A. 双机导出 ----------

def part_export():
    a104 = dual_prog.snapshot(dual_prog.L104)
    a105 = dual_prog.snapshot(dual_prog.L105)
    n104 = max(dual_prog.prog_n(a104["progs"]), a104["lines"])
    n105 = max(dual_prog.prog_n(a105["progs"]), a105["lines"])

    st = dual_prog._load_state()
    r104 = dual_prog.wallclock_rate("104", n104, st) or dual_prog.steady_rate(a104["progs"]) or 0.0
    r105 = dual_prog.wallclock_rate("105", n105, st) or dual_prog.steady_rate(a105["progs"]) or 0.0
    dual_prog._save_state(st)

    covered = min(TOTAL_ADDR, n104 + n105)
    gap = TOTAL_ADDR - covered
    frac = covered / float(TOTAL_ADDR)

    print("A. 反编译体导出（双机并行）")
    print("   %s  %5.1f%%   %s / %s"
          % (bar(frac), frac * 100, f"{covered:,}", f"{TOTAL_ADDR:,}"))
    print("   104 头部 %s (%.1f 个/秒)  ←→  105 尾部 %s (%.1f 个/秒)"
          % (f"{n104:,}", r104, f"{n105:,}", r105))
    if gap > 0:
        sp = r104 + r105
        eta = gap / sp if sp > 0.05 else None
        print("   中间缺口 %s 个   合拢 %.1f 个/秒   →  %s 后全部覆盖"
              % (f"{gap:,}", sp, fmt_secs(eta)))
    else:
        print("   ✅ 全部覆盖。如需重新合并： python merge_bodies.py --gen")
    print()
    return n104, n105, covered, gap, r104 + r105


# ---------- B. 方法还原率 ----------

def load_rva_methods():
    """rva -> 该地址被多少个 C# 方法共用"""
    p = os.path.join(HERE, "bh3_method_addr.tsv")
    d = {}
    if not os.path.exists(p):
        return d
    with io.open(p, encoding="utf-8", errors="replace") as f:
        f.readline()
        for ln in f:
            q = ln.rstrip("\r\n").split("\t")
            if len(q) < 5 or not q[3]:
                continue
            try:
                d[int(q[3], 16)] = d.get(int(q[3], 16), 0) + 1
            except ValueError:
                pass
    return d


def load_list():
    p = os.path.join(HERE, "_dump", "body_list.txt")
    if not os.path.exists(p):
        return []
    return [l.strip() for l in io.open(p, encoding="utf-8", errors="replace") if l.strip()]


def part_methods(n104, n105):
    amap = load_rva_methods()
    lst = load_list()
    if not amap or not lst:
        print("B. 方法还原率    （缺 bh3_method_addr.tsv 或 _dump/body_list.txt，跳过）")
        print()
        return 0.0
    # 两段可能重叠（104 跑到汇合点后不会停，会继续做 105 已完成的段）。
    # 必须按列表下标取并集再求和，否则重叠部分的地址会被算两遍 —— 之前就
    # 因此算出过 102.5% 这种超过 100% 的数。
    idx = set(range(min(n104, TOTAL_ADDR)))
    idx.update(range(max(0, TOTAL_ADDR - n105), TOTAL_ADDR))
    hit = 0
    for i in idx:
        try:
            hit += amap.get(int(lst[i], 16) - 0x180000000, 0)
        except ValueError:
            pass
    frac = hit / float(TOTAL_METHODS)
    print("B. 方法还原率（有真实函数体的 C# 方法）")
    print("   %s  %5.1f%%   %s / %s"
          % (bar(min(1.0, frac)), frac * 100, f"{hit:,}", f"{TOTAL_METHODS:,}"))
    print("   （%s 个已导出地址，平均每地址服务 %.2f 个方法）"
          % (f"{len(idx):,}", hit / float(max(1, len(idx)))))
    print()
    return frac


# ---------- C. 源码树 ----------

def part_src():
    d = os.path.join(HERE, "src")
    n = 0
    size = 0
    if os.path.isdir(d):
        for root, _dirs, files in os.walk(d):
            for fn in files:
                if fn.endswith(".cs"):
                    n += 1
                    try:
                        size += os.path.getsize(os.path.join(root, fn))
                    except OSError:
                        pass
    meta = {}
    p = os.path.join(d, "_index.json")
    if os.path.exists(p):
        try:
            with io.open(p, encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = {}
    print("C. 源码树（本地 src/）")
    if not n:
        print("   还没有生成，跑： python gen_cs.py --out src --bodies bodies_merged.tsv")
        print()
        return
    print("   %d 个 .cs / %.0f MB" % (n, size / 1048576.0))
    if isinstance(meta, dict) and isinstance(meta.get("types"), list):
        # 类型条目是定长数组，第 7 位是 methodCount（见 gen_cs.py 的 entries.append）
        tis = meta["types"]
        methods = 0
        for e in tis:
            if isinstance(e, list) and len(e) > 7 and isinstance(e[7], int):
                methods += e[7]
        nss = meta.get("namespaces")
        print("   类型 %s / 方法 %s / 命名空间 %s / 嵌套 %s"
              % (f"{len(tis):,}", f"{methods:,}",
                 f"{len(nss):,}" if isinstance(nss, dict) else "—",
                 f"{meta.get('nested', 0):,}"))
    print()


# ---------- D. 路线图 ----------

def _w(s):
    """显示宽度：中日韩字符算 2 列"""
    n = 0
    for ch in s:
        n += 2 if ord(ch) > 0x1100 and (
            '\u2e80' <= ch <= '\u9fff' or '\uac00' <= ch <= '\ud7a3'
            or '\uff00' <= ch <= '\uff60' or '\u3000' <= ch <= '\u303f') else 1
    return n


def _pad(s, width):
    return s + " " * max(0, width - _w(s))


def part_roadmap():
    print("D. 路线图")
    for no, name, st, note in ROADMAP:
        mark = "✓" if st == "done" else "▶"
        print("   %s %s %s %s %s"
              % (mark, _pad(no, 3), _pad(name, 22),
                 _pad("完成" if st == "done" else "进行中", 9), note))
    print()
    print("   待办")
    for pri, name, note in TODO:
        print("   [%s] %s %s" % (pri, _pad(name, 26), note))
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-w", "--watch", type=int, default=0)
    a = ap.parse_args()

    def once():
        print("\033[2J\033[H", end="")
        print("═══ 崩坏3 源码还原 · 整体进度 ═══  %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
        print()
        n104, n105, covered, gap, sp = part_export()
        part_methods(n104, n105)
        part_src()
        part_roadmap()
        print("   命令： dual_prog.py（细节） / overall.py -w 60（本页刷新） / merge_bodies.py --gen（收尾）")

    if a.watch <= 0:
        once()
        return
    try:
        while True:
            once()
            time.sleep(max(10, a.watch))
    except KeyboardInterrupt:
        print("\n退出")


if __name__ == "__main__":
    main()
