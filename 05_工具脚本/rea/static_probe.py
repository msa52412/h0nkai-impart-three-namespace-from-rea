#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""static_probe.py — 判定 P! 低置信度类型里哪些字段其实是 static

不依赖 Ghidra：函数体已全量落盘在 bodies_merged.tsv（905 MB），
直接用正则从反编译文本里提取「this->字段名」的访问事实。

三条判据，按强度递减：

  S1  .cctor 写 / .ctor 不写     —— 最强，但只有同类型同时存在两个构造器时可用
  S2  字段名在全量 body 中从未作为 this->X 出现 —— 覆盖全，但会误伤「死字段」
  S3  字段名只在 static 上下文出现（_DAT_ 全局） —— 弱，仅作交叉验证

用法:
  python static_probe.py                 # 全量扫描并输出报告
  python static_probe.py --max 50000     # 只扫前 N 个 body（调试）
输出:
  bh3_static_cand.tsv    typeIdx / fieldIdx / fieldName / verdict / 证据
  bh3_static_stat.txt    汇总
"""
import io
import json
import os
import re
import sys
import time
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
BODIES = os.path.join(HERE, "bodies_merged.tsv")
LAYOUT = os.path.join(HERE, "bh3_layout4.tsv")
SYMTAB = os.path.join(HERE, "bh3_symtab.tsv")
INDEX = os.path.join(HERE, "src", "_index.json")

# this->name  —— Ghidra 已把实例字段重定型成结构体成员
P_THIS = re.compile(r"this->([A-Za-z_<>][\w<>`$]*)")
# this + 0xNN  —— 尚未重定型的裸偏移
P_OFF = re.compile(r"(?:param_1|this)\s*\+\s*0x([0-9a-fA-F]+)")
# 全局写： _DAT_xxx = ...   或   *_DAT_xxx = ...
P_GWRITE = re.compile(r"\*?_DAT_[0-9a-fA-F]+\s*=\s*[^=]")

# Ghidra 自动生成的噪声成员名，不代表真实字段访问
NOISE = {"__klass", "__monitor", "__vtable", "pad", "field_0", "fields"}

# symtab 里的 rva 是相对地址，bodies 里是含镜像基址的 VA
IMAGE_BASE = 0x180000000


def va2rva(va_hex):
    try:
        return "%X" % (int(va_hex, 16) - IMAGE_BASE)
    except ValueError:
        return None


def load_layout():
    """返回 {typeIdx: [(fieldIdx, fieldName, fieldType, conf), ...]}, 以及 P! 集合"""
    out = collections.defaultdict(list)
    conf_of = {}
    with io.open(LAYOUT, "r", encoding="utf-8", errors="replace") as f:
        next(f, None)
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 10:
                continue
            ti = int(p[0])
            name = p[3]
            if name in NOISE or name.startswith("pad_"):
                continue
            out[ti].append((p[2], name, p[4]))
            conf_of[ti] = p[8]
    bang = {t for t, c in conf_of.items() if c == "P!"}
    return out, bang


def load_ctor_map():
    """{typeIdx: {'cctor': set(rva), 'ctor': set(rva)}}"""
    m = json.load(io.open(INDEX, encoding="utf-8"))
    by_nscls = collections.defaultdict(list)
    for i, e in enumerate(m["types"]):
        by_nscls[(e[0], e[1])].append(i)
    res = collections.defaultdict(lambda: {"cctor": set(), "ctor": set()})
    with io.open(SYMTAB, "r", encoding="utf-8", errors="replace") as f:
        next(f, None)
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 4 or p[3] not in ("_cctor", "_ctor"):
                continue
            rva = p[0].upper()
            if not rva:
                continue
            key = "cctor" if p[3] == "_cctor" else "ctor"
            for i in by_nscls.get((p[1], p[2]), ()):
                res[i][key].add(rva)
    return res


def normalize(name):
    """去掉属性 backing field 后缀，让 <X>k__BackingField 与 X 能对上"""
    if name.startswith("<") and ">k__BackingField" in name:
        return name[1:name.index(">")]
    return name


def scan_bodies(max_lines=0):
    """一趟扫描，返回:
         norm_seen   全量 body 中出现过的 this-> 名字（规范化后）
         cctor_seen  出现在 .cctor 里被 this-> 访问的名字
         ctor_seen   出现在 .ctor 里被 this-> 访问的名字
         cctor_gwrite  .cctor 里有过全局写入的 rva 集合
    """
    cctor_rvas, ctor_rvas = set(), set()
    norm_seen = set()
    cctor_seen, ctor_seen = set(), set()
    cctor_gwrite = set()
    n = 0
    t0 = time.time()
    with io.open(BODIES, "r", encoding="utf-8", errors="replace") as f:
        for ln in f:
            n += 1
            if max_lines and n > max_lines:
                break
            tab = ln.find("\t")
            if tab < 0:
                continue
            va = ln[:tab].strip().upper()
            body = ln[tab + 1:]
            names = P_THIS.findall(body)
            if names:
                for x in names:
                    if x in NOISE or x.startswith("pad_"):
                        continue
                    norm_seen.add(normalize(x))
            if n % 50000 == 0:
                sys.stdout.write("\r  扫描 %d 行  %s  %.0f 秒" %
                                 (n, "%.1f%%" % (100.0 * n / 311317), time.time() - t0))
                sys.stdout.flush()
    sys.stdout.write("\r  扫描完成 %d 行  %.1f 秒            \n" % (n, time.time() - t0))
    return norm_seen


def scan_ctors(ctor_map):
    """第二趟：只挑出构造器所在行，提取各自的 this-> 集合"""
    want = {}
    for ti, d in ctor_map.items():
        for rva in d["cctor"]:
            want[rva] = (ti, "cctor")
        for rva in d["ctor"]:
            want[rva] = (ti, "ctor")
    if not want:
        return {}, {}
    cctor_seen = collections.defaultdict(set)
    ctor_seen = collections.defaultdict(set)
    got = 0
    with io.open(BODIES, "r", encoding="utf-8", errors="replace") as f:
        for ln in f:
            tab = ln.find("\t")
            if tab < 0:
                continue
            va = va2rva(ln[:tab].strip())
            if not va:
                continue
            hit = want.get(va)
            if not hit:
                continue
            ti, kind = hit
            got += 1
            body = ln[tab + 1:]
            names = {normalize(x) for x in P_THIS.findall(body)
                     if x not in NOISE and not x.startswith("pad_")}
            if kind == "cctor":
                cctor_seen[ti] |= names
            else:
                ctor_seen[ti] |= names
    print("  构造器命中 %d / %d" % (got, len(want)))
    return cctor_seen, ctor_seen


def main():
    max_lines = 0
    if "--max" in sys.argv:
        max_lines = int(sys.argv[sys.argv.index("--max") + 1])

    print("═══ static 字段判定 ═══")
    t0 = time.time()
    fields, bang = load_layout()
    total_rows = sum(len(v) for t, v in fields.items() if t in bang)
    print("P! 类型 %d 个 / 字段 %d 个" % (len(bang), total_rows))

    ctor_map = load_ctor_map()
    print("构造器索引就绪：%d 个类型有 .cctor/._ctor 记录" %
          sum(1 for d in ctor_map.values() if d["cctor"] or d["ctor"]))

    print("\n[1/2] 全量 body 扫描（提取 this-> 访问事实）")
    norm_seen = scan_bodies(max_lines)

    print("\n[2/2] 构造器专项扫描")
    cctor_seen, ctor_seen = scan_ctors(ctor_map)

    rows = []
    stat = collections.Counter()
    for ti in sorted(bang):
        fl = fields[ti]
        cc = cctor_seen.get(ti, set())
        ct = ctor_seen.get(ti, set())
        for fi, name, ftype in fl:
            nn = normalize(name)
            ev = []
            verdict = "?"
            if nn in ct:
                verdict = "instance"
                ev.append("ctor写")
            elif nn in cc:
                verdict = "static"
                ev.append("cctor写")
            elif nn not in norm_seen:
                verdict = "static?"
                ev.append("全库无this访问")
            else:
                verdict = "instance?"
                ev.append("仅非构造器访问")
            if ftype.startswith("!"):
                ev.append("泛型")
            rows.append((ti, fi, name, ftype, verdict, ",".join(ev)))
            stat[verdict] += 1

    out = os.path.join(HERE, "bh3_static_cand.tsv")
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("typeIdx\tfieldIdx\tfieldName\tfieldType\tverdict\tevidence\n")
        for r in rows:
            f.write("%d\t%s\t%s\t%s\t%s\t%s\n" % r)

    lines = []
    lines.append("P! 类型 %d 个 / 字段 %d 个" % (len(bang), total_rows))
    lines.append("")
    lines.append("判定分布：")
    for k in ("static", "static?", "instance", "instance?", "?"):
        if stat[k]:
            lines.append("  %-10s %7d  (%.1f%%)" % (k, stat[k], 100.0 * stat[k] / len(rows)))
    lines.append("")
    lines.append("总计 %.1f 秒" % (time.time() - t0))
    txt = "\n".join(lines)
    print("\n" + txt)
    io.open(os.path.join(HERE, "bh3_static_stat.txt"), "w", encoding="utf-8").write(txt + "\n")
    print("\n输出: bh3_static_cand.tsv (%d 行)" % len(rows))


if __name__ == "__main__":
    main()
