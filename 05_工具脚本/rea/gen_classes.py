#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bh3_classes.txt —— 类定义视图：类型 + 父类 + 字段 + 属性 + 事件

输入：bh3_types_v5.txt（父类/计数）
      bh3_fields.tsv     （字段名 + 字段类型）
      bh3_properties.tsv （属性名 + token + getter/setter）
      bh3_events.tsv     （事件名 + token + add/remove）
"""
import collections

T5 = r"D:\Carol-start\_rea\bh3_types_v5.txt"
FL = r"D:\Carol-start\_rea\bh3_fields.tsv"
PR = r"D:\Carol-start\_rea\bh3_properties.tsv"
EV = r"D:\Carol-start\_rea\bh3_events.tsv"
OUT = r"D:\Carol-start\_rea\bh3_classes.txt"

types = {}
for ln in open(T5, encoding="utf-8").readlines()[1:]:
    p = ln.rstrip("\n").split("\t")
    if len(p) < 10:
        continue
    idx = int(p[0])
    full = (p[1] + "." if p[1] else "") + p[2]
    types[idx] = {"idx": idx, "full": full, "token": p[3],
                  "mc": int(p[5]), "parent": p[8], "fc": int(p[9])}

fields = collections.OrderedDict()
for ln in open(FL, encoding="utf-8").readlines()[1:]:
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 5:
        fields.setdefault(int(p[0]), []).append((p[3], p[4]))

props = collections.OrderedDict()
for ln in open(PR, encoding="utf-8").readlines()[1:]:
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 10:
        props.setdefault(int(p[0]), []).append(p)

events = collections.OrderedDict()
for ln in open(EV, encoding="utf-8").readlines()[1:]:
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 6:
        events.setdefault(int(p[0]), []).append(p)

n_f = n_p = n_e = 0
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# 崩坏3 类型定义视图（由 global-metadata.dat 离线解出）\n")
    f.write("# 格式: 类型全名 : 父类    [方法数 / 字段数 / 属性数 / 事件数]\n")
    f.write("#        缩进行 = 字段 | 属性(prop) | 事件(event)\n")
    f.write("# 类型 %d / 字段 %d / 属性 %d / 事件 %d\n\n"
            % (len(types), sum(len(v) for v in fields.values()),
               sum(len(v) for v in props.values()), sum(len(v) for v in events.values())))
    for idx in sorted(types):
        t = types[idx]
        fs = fields.get(idx, [])
        ps = props.get(idx, [])
        es = events.get(idx, [])
        f.write("\n%s : %s    [%d 方法 / %d 字段 / %d 属性 / %d 事件]\n"
                % (t["full"], t["parent"] or "(无)", t["mc"], t["fc"], len(ps), len(es)))
        for fn, ft in fs:
            f.write("    %-46s %s\n" % (ft, fn))
            n_f += 1
        for p in ps:
            getter = p[7].split(":", 1)[1] if p[7] else ""
            setter = p[9].split(":", 1)[1] if p[9] else ""
            acc = ""
            if getter or setter:
                acc = "  {%s%s}" % (getter, (" " + setter) if setter else "")
            f.write("    属性[%s]%s%s\n" % (p[4], p[3], acc))
            n_p += 1
        for e in es:
            f.write("    事件  %-40s %s  (add=%s remove=%s)\n"
                    % (e[3], e[4], e[5], e[6]))
            n_e += 1

print("写入 %s" % OUT)
print("类型 %d  字段 %d  属性 %d  事件 %d" % (len(types), n_f, n_p, n_e))
print("有字段 %d  有属性 %d  有事件 %d"
      % (len(fields), len(props), len(events)))
