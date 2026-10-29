#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan_seg.py —— 分段扫描探针表（scan_this 的驱动器）

背景：全量 37,752 行在一个进程里跑会在中途无声音地死掉（faulthandler 都抓不到栈，
重放同样的行又都正常）。分段跑 + 每段落盘，哪段死了只重跑哪段。

用法: python scan_seg.py <lo> <hi> <out.tsv>   （行号从 1 计，含 lo 不含 hi）
"""
import csv
import os
import sys
import time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "_pylibs"))
sys.path.insert(0, HERE)
import scan_this  # noqa: E402


def build_icf():
    mv2 = {r["idx"]: r["declType"] for r in csv.DictReader(
        open(os.path.join(HERE, "bh3_methods_v2.tsv"), encoding="utf-8", errors="replace"),
        delimiter="\t")}
    rva_types = defaultdict(set)
    for r in csv.DictReader(
            open(os.path.join(HERE, "bh3_method_addr.tsv"), encoding="utf-8", errors="replace"),
            delimiter="\t"):
        if r["rva"].strip():
            rva_types[r["rva"]].add(mv2.get(r["idx"], ""))
    return {k for k, v in rva_types.items() if len(v) > 1}


def main():
    lo, hi, out_path = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    icf_bad = build_icf()
    print("[seg %d-%d] icf=%d" % (lo, hi, len(icf_bad)), flush=True)

    out = open(out_path, "w", encoding="utf-8")
    out.write("typeIdx\toffsets\tnAccess\tnInsn\n")
    n = hit = 0
    t0 = time.time()
    with open(os.path.join(HERE, "bh3_layout_probe_all.tsv"),
              encoding="utf-8", errors="replace") as f:
        next(f)
        for i, line in enumerate(f, 1):
            if i < lo:
                continue
            if i >= hi:
                break
            p = line.rstrip("\n").split("\t")
            if len(p) < 2:
                continue
            ti = int(p[0])
            n += 1
            offs = set()
            nins = 0
            for rs in p[1].split(","):
                rs = rs.strip()
                if not rs:
                    continue
                sr = 0
                if ":" in rs:
                    rs, s2 = rs.split(":", 1)
                    try:
                        sr = int(s2)
                    except ValueError:
                        sr = 0
                if rs.upper() in icf_bad:
                    continue
                try:
                    rva = int(rs, 16)
                except ValueError:
                    continue
                o, k = scan_this.scan(rva, sr)
                offs |= o
                nins += k
            if offs:
                hit += 1
            out.write("%d\t%s\t%d\t%d\n" % (
                ti, ",".join("0x%x" % x for x in sorted(offs)), len(offs), nins))
            if n % 4000 == 0:
                out.flush()
                print("  %d hit=%d %.1fs" % (n, hit, time.time() - t0), flush=True)
    out.close()
    print("[seg %d-%d] DONE rows=%d hit=%d %.1fs" % (lo, hi, n, hit, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
