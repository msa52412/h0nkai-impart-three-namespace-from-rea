#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bh3_classes.txt v2 —— 类定义视图（含完整方法签名）

输入：
  bh3_types_v5.txt       类型 / 父类 / 方法数 / 字段数
  bh3_methods_v2.tsv     方法（declType / 签名 / flags / token）
  bh3_fields.tsv         字段（名字 + 类型）
  bh3_properties_v2.tsv  属性（名字 + 类型）
  bh3_events.tsv         事件

输出格式：
  Namespace.Type : Parent    [N 方法 / N 字段 / N 属性 / N 事件]
      public static void Foo(int a, string b)
      int _field
      string Prop {get_Prop set_Prop}
      event EventHandler Bar
"""
import collections

T5 = r"D:\Carol-start\_rea\bh3_types_v5.txt"
ME = r"D:\Carol-start\_rea\bh3_methods_v2.tsv"
FL = r"D:\Carol-start\_rea\bh3_fields.tsv"
PR = r"D:\Carol-start\_rea\bh3_properties_v2.tsv"
EV = r"D:\Carol-start\_rea\bh3_events.tsv"
OUT = r"D:\Carol-start\_rea\bh3_classes.txt"

ACC = {0: "private", 1: "private", 2: "private protected", 3: "internal",
       4: "protected", 5: "protected internal", 6: "public"}


def flags_str(fl):
    v = int(fl, 16)
    s = [ACC.get(v & 7, "?")]
    for bit, nm in ((0x10, "static"), (0x20, "final"), (0x40, "virtual"),
                    (0x400, "abstract"), (0x800, "specialname"),
                    (0x1000, "rtspecialname")):
        if v & bit:
            s.append(nm)
    return " ".join(s)


types = {}
for ln in open(T5, encoding="utf-8").readlines()[1:]:
    p = ln.rstrip("\n").split("\t")
    if len(p) < 10:
        continue
    idx = int(p[0])
    types[idx] = {"full": (p[1] + "." if p[1] else "") + p[2], "token": p[3],
                  "mc": int(p[5]), "parent": p[8], "fc": int(p[9])}

methods = collections.OrderedDict()
for ln in open(ME, encoding="utf-8").readlines()[1:]:
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 12:
        methods.setdefault(int(p[2]), []).append(p)

fields = collections.OrderedDict()
for ln in open(FL, encoding="utf-8").readlines()[1:]:
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 5:
        fields.setdefault(int(p[0]), []).append((p[3], p[4]))

props = collections.OrderedDict()
for ln in open(PR, encoding="utf-8").readlines()[1:]:
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 8:
        props.setdefault(int(p[0]), []).append(p)

events = collections.OrderedDict()
for ln in open(EV, encoding="utf-8").readlines()[1:]:
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 6:
        events.setdefault(int(p[0]), []).append(p)

nf = np_ = ne = nm = 0
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# 崩坏3 类型定义视图（离线解出 global-metadata.dat）\n")
    f.write("# 类型 %d / 方法 %d / 字段 %d / 属性 %d / 事件 %d\n"
            % (len(types), sum(len(v) for v in methods.values()),
               sum(len(v) for v in fields.values()),
               sum(len(v) for v in props.values()),
               sum(len(v) for v in events.values())))
    f.write("# 行首无缩进 = 类型；4 空格 = 成员\n")
    f.write("# 方法格式: <访问级> [修饰] 返回类型 名称(参数...)\n\n")
    for idx in sorted(types):
        t = types[idx]
        ms = methods.get(idx, [])
        fs = fields.get(idx, [])
        ps = props.get(idx, [])
        es = events.get(idx, [])
        f.write("\n%s : %s    [%d 方法 / %d 字段 / %d 属性 / %d 事件]\n"
                % (t["full"], t["parent"] or "(无)", t["mc"], t["fc"], len(ps), len(es)))
        for m in ms:
            f.write("    %s %s %s(%s)\n" % (flags_str(m[6]), m[5], m[4], m[11]))
            nm += 1
        for fn, ft in fs:
            f.write("    %-44s %s\n" % (ft, fn))
            nf += 1
        for p in ps:
            getter = p[6].split(":", 1)[1] if p[6] else ""
            setter = p[7].split(":", 1)[1] if p[7] else ""
            acc = " {%s%s}" % (getter, (" " + setter) if setter else "") if (getter or setter) else ""
            f.write("    %-40s %s%s\n" % (p[4], p[3], acc))
            np_ += 1
        for ev in es:
            f.write("    event %-36s %s\n" % (ev[4], ev[3]))
            ne += 1

print("写入 %s" % OUT)
print("类型 %d  方法 %d  字段 %d  属性 %d  事件 %d" % (len(types), nm, nf, np_, ne))
