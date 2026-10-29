#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dump_attrs.py —— 逐字段打印某类型的 attrs 真值，用于人工核对 flags

用法: python dump_attrs.py System.Globalization.GregorianCalendar [...]
"""
import sys
import io
import csv

_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout6 as V6                                   # noqa: E402
sys.stdout = _bak

# attrs 原始值
F_ATTRS = {}
for _r in csv.DictReader(open("bh3_field_flags.tsv", encoding="utf-8"), delimiter="\t"):
    F_ATTRS[int(_r["fieldIdx"])] = _r.get("attrs", "?")

FN = {-1: "-", 0: "PrivateScope", 1: "Private", 2: "FamANDAssem", 3: "Assembly",
      4: "Family", 5: "FamORAssem", 6: "Public"}
FLAGS = [(0x0010, "STATIC"), (0x0020, "INITONLY"), (0x0040, "LITERAL"),
         (0x0080, "NOTSERIALIZED"), (0x0100, "SPECIALNAME"),
         (0x0200, "RTSPECIALNAME"), (0x0400, "HASFIELDRVA"),
         (0x1000, "HASDEFAULT"), (0x2000, "HASFIELDMARSHAL"),
         (0x4000, "HASFIELD", ), (0x8000, "??0x8000")]


def fmt(a):
    return "|".join(n for b, n in FLAGS if a & b) or "instance"


def dump(name, ti):
    t = V6.types[ti]
    print("=" * 92)
    print("%s   ti=%d   metadata fieldCount(第10列) 见下" % (name, ti))
    print("=" * 92)
    print("%-38s %-46s %-6s %-7s %s" % ("字段", "类型", "attrs", "访问", "占用"))
    print("-" * 92)
    total_inst = 0
    for fi, fn, ft in V6.fields.get(ti, []):
        a = F_ATTRS.get(fi)
        st = "STATIC" if fi in V6.f_static else ""
        lt = "LITERAL" if fi in V6.f_literal else ""
        occ = "跳过" if (st or lt) else "占位"
        if not (st or lt):
            total_inst += 1
        print("%-38s %-46s %-6s %-7s %s" % (
            fn[:37], (ft or "")[:45], a if a is not None else "?",
            (st + ("/" if st and lt else "") + lt) or "实例", occ))
    print("-" * 92)
    fl, end = V6.pack(ti)
    print("实例字段数(本类型) = %d   打包后字段数(含继承) = %d   尺寸 = 0x%x" % (
        total_inst, len(fl), end))
    print("\n打包布局:")
    o = V6.clean_obs(ti, V6.obs_of(ti))
    offs = {x[4] for x in fl}
    for owner, fi, fn, ft, off, sz in fl:
        mark = "  ← 有观测" if off in o else ""
        own = "" if owner == ti else " [来自 %s]" % V6.types[owner]["full"]
        print("  0x%-4x %-40s %-40s size=%d%s%s" % (
            off, fn[:39], (ft or "")[:39], sz, own, mark))
    print("观测: %s" % " ".join("0x%x" % x for x in sorted(o)))
    print("落空: %s" % " ".join("0x%x" % x for x in sorted(o - offs)))
    print("真落空(real_miss): %s" % " ".join(
        "0x%x" % x for x in V6.real_miss(fl, end, o)))


if __name__ == "__main__":
    names = sys.argv[1:] or [
        "System.Globalization.GregorianCalendar",
        "System.Security.Cryptography.X509Certificates.X509BasicConstraintsExtension",
    ]
    for nm in names:
        ti = V6.by_name.get(nm)
        if ti is None:
            print("!! 未找到: %s" % nm)
            continue
        dump(nm, ti)
        print()
