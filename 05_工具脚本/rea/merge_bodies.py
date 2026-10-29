#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merge_bodies.py — 合并两台机器导出的反编译体（流式，低内存）

104 → bodies.tsv      （头部正向）
105 → bodies_b.tsv    （尾部倒序 + 后续接力轮次）

两台的分工有重叠（104 跑到汇合点后不会自动停，会继续做 105 已完成的段），
所以必须按 VA 去重。

**不能用 dict 装函数体**：两个文件合计约 1 GB / 332,875 行，
本机可用内存只有 1 GB 上下（`kryptex_krig-miner` 常驻吃 8 GB），
`{va: body}` 会直接触发换页。改成：
    Pass 1  扫 104，记 VA 集合 + 每行字节偏移，同时原样写出
    Pass 2  扫 105，VA 不在集合里就追加；在集合里就抽样回读 104 对应行比对
内存只有 VA 集合（13 万个短字符串）+ 偏移表，约 30 MB。

用法:
    python merge_bodies.py                 # 拉取 + 合并 + 统计
    python merge_bodies.py --gen           # 合并后直接跑 gen_cs.py
    python merge_bodies.py --keep          # 保留中间文件
"""
import argparse
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "_pylibs"))
import rsh2

REMOTE = {
    # sftp 的路径不展开 ~，必须绝对路径（踩过：FileNotFoundError）
    "a": ("104", "/home/nas/re/sym/bodies.tsv", "bodies_a.tsv"),
    "b": ("105", "/home/nas/re/sym/bodies_b.tsv", "bodies_b.tsv"),
}
PY = sys.executable
SAMPLE = 200          # 重叠部分抽样比对多少条


def pull(tag):
    host, remote, local = REMOTE[tag]
    path = os.path.join(HERE, local)
    size = 0
    print("  拉取 %s:%s → %s ..." % (host, remote, local), end="")
    sys.stdout.flush()
    cli = rsh2.conn(host, timeout=60)
    cli.get_transport().set_keepalive(30)
    try:
        sf = cli.open_sftp()
        try:
            sf.get(remote, path)
        finally:
            sf.close()
    finally:
        cli.close()
    size = os.path.getsize(path)
    n = 0
    with io.open(path, "rb") as f:
        for _ in f:
            n += 1
    print(" %.0f MB / %s 行" % (size / 1048576.0, f"{n:,}"))
    return path, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--out", default="bodies_merged.tsv")
    a = ap.parse_args()

    print("═══ 合并反编译体 ═══")
    pa, na = pull("a")
    pb, nb = pull("b")
    out_path = os.path.join(HERE, a.out)

    # ---- Pass 1: 104 全量写出，同时记 VA 集合 + 行偏移 ----
    print("  Pass 1  写出 104 并建索引 ...", end="")
    sys.stdout.flush()
    seen = set()
    offsets = {}                      # va -> 该行在 pa 里的字节偏移
    off = 0
    out_bytes = 0
    written = 0
    with io.open(pa, "rb") as fa, io.open(out_path, "wb") as fo:
        for ln in fa:
            t = ln.find(b"\t")
            if t > 0:
                va = ln[:t]
                seen.add(va)
                offsets[va] = off
                fo.write(ln)
                out_bytes += len(ln)
                written += 1
            off += len(ln)
    print(" %s 条 / 索引 %s 个" % (f"{written:,}", f"{len(offsets):,}"))

    # ---- Pass 2: 105 去重追加，重叠部分抽样比对 ----
    print("  Pass 2  追加 105 的去重部分 ...", end="")
    sys.stdout.flush()
    added = 0
    overlap = 0
    checked = 0
    mismatch = []
    with io.open(out_path, "ab") as fo, io.open(pb, "rb") as fb:
        for ln in fb:
            t = ln.find(b"\t")
            if t <= 0:
                continue
            va = ln[:t]
            if va in seen:
                overlap += 1
                if len(mismatch) < 3 and checked < SAMPLE and (overlap % 37 == 1):
                    checked += 1
                    old = read_line_at(pa, offsets[va])
                    if old is not None and old.rstrip(b"\r\n") != ln.rstrip(b"\r\n"):
                        mismatch.append((va.decode(), len(old), len(ln)))
                continue
            seen.add(va)
            fo.write(ln)
            added += 1
    print(" 新增 %s / 重叠 %s" % (f"{added:,}", f"{overlap:,}"))

    total = written + added
    print("  重叠比对 %d 条 → %s"
          % (checked, "全部一致" if not mismatch else "⚠ %d 条不一致" % len(mismatch)))
    for va, la, lb in mismatch:
        print("     VA 0x%s：104 行 %d 字节 / 105 行 %d 字节" % (va, la, lb))

    print("  写出 %s：%s 个 / %.0f MB"
          % (a.out, f"{total:,}", os.path.getsize(out_path) / 1048576.0))

    if not a.keep:
        for _h, _r, local in REMOTE.values():
            try:
                os.remove(os.path.join(HERE, local))
            except OSError:
                pass

    if a.gen:
        print("\n═══ 生成源码树 ═══")
        rc = subprocess.call([PY, os.path.join(HERE, "gen_cs.py"),
                              "--out", "src", "--bodies", a.out], cwd=HERE)
        print("gen_cs.py rc=%d" % rc)


def read_line_at(path, off):
    with io.open(path, "rb") as f:
        f.seek(off)
        return f.readline()


if __name__ == "__main__":
    main()
