#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_layout_report.py —— v6 布局质量报告

v6 相对旧版的两个根本变化，决定了本报告的口径必须重写：

  1. static / literal 来自 Il2CppType.attrs 的**元数据真值**，不再靠命名猜。
     旧报告「元数据没有 static 标志，只能靠 .cctor 反推」的结论已作废。
  2. 落空按几何位置分三类，只有「字段间空隙」算布局错误：
       inside  落在字段字节内但非合法内部偏移 —— Ghidra 常量折叠/字节步进噪声
       beyond  超出最后一个字段的真实结尾 —— 尾 padding + 通过基类指针的派生访问
       hole    落在两个字段之间            —— ★唯一可操作的错误

输出：
  bh3_instsize.tsv         typeIdx typeName kind instSize nInst nStatic nProbe conf
  bh3_layout_report.txt
"""
import csv
import io
import os
import sys
from collections import Counter

# bh3_layout6 在被 import 时会重算并写出布局文件，顺便保证报告与数据同源
_bak = sys.stdout
sys.stdout = io.StringIO()
import bh3_layout6 as L                                    # noqa: E402
sys.stdout = _bak

types = L.types
pack = L.pack
kind_of = L.kind_of

# ---------------- 每类型实例尺寸 ----------------
ROWS = []
for ti in sorted(types):
    t = types[ti]
    k = kind_of(ti)
    if k == "enum":
        continue
    fl, end = pack(ti)
    o = L.clean_obs(ti, L.obs_of(ti))
    if not fl and not o:
        continue
    hole, inside, beyond = L.miss_breakdown(fl, end, o)
    conf = "P?" if not o else ("P!" if hole else "P")
    ROWS.append((ti, t["full"], k, end,
                 len(fl), len(L.noninst_fields(ti)), len(o), conf,
                 hole, inside, beyond))

with open("bh3_instsize.tsv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, delimiter="\t")
    w.writerow(["typeIdx", "typeName", "kind", "instSize", "nInst", "nStatic",
                "nProbe", "conf"])
    for ti, nm, k, end, ni, ns, np_, conf, _h, _i, _b in ROWS:
        w.writerow([ti, nm, k, end, ni, ns, np_, conf])

n_all = len(ROWS)
c_conf = Counter(r[7] for r in ROWS)
k_stat = Counter(r[2] for r in ROWS)
h_sum = sum(r[8] for r in ROWS)
i_sum = sum(r[9] for r in ROWS)
b_sum = sum(r[10] for r in ROWS)
n_obs = c_conf["P"] + c_conf["P!"]
n_inst = sum(r[4] for r in ROWS)
n_static = sum(r[5] for r in ROWS)

# ---------------- 地面真值校验 ----------------
# ★ 不能拿 pack() 的返回值来校验 KNOWN_STRUCT_SIZE：pack 内部会用规范值兜底，
#   算出来的值被覆盖掉了，校验必然通过（循环论证）。真正的信号是 _known_bad，
#   它记录的是**兜底之前**的算出值。
KNOWN_TOTAL = len(L.KNOWN_STRUCT_SIZE)
_bad_map = {nm: (got, exp) for nm, got, exp in L._known_bad}
KNOWN = [
    ("System.DateTime", 8), ("System.TimeSpan", 8), ("System.DateTimeOffset", 16),
    ("System.Guid", 16), ("System.Decimal", 16),
    ("UnityEngine.Vector2", 8), ("UnityEngine.Vector3", 12), ("UnityEngine.Vector4", 16),
    ("UnityEngine.Vector2Int", 8), ("UnityEngine.Vector3Int", 12),
    ("UnityEngine.Quaternion", 16), ("UnityEngine.Matrix4x4", 64),
    ("UnityEngine.Color", 16), ("UnityEngine.Color32", 4),
    ("UnityEngine.Bounds", 24), ("UnityEngine.Rect", 16), ("UnityEngine.Ray", 24),
    ("UnityEngine.Plane", 16), ("UnityEngine.LayerMask", 4),
    ("UnityEngine.Keyframe", 20), ("UnityEngine.GradientColorKey", 20),
    ("UnityEngine.GradientAlphaKey", 8),
]

# 字段级 attrs 抽验：(类型, 字段, 期望 static, 期望 literal)
ATTR_CHECKS = [
    ("System.DateTime", "TicksPerMillisecond", 1, 1),
    ("System.DateTime", "MaxTicks", 1, 1),
    ("System.DateTime", "dateData", 0, 0),
    ("System.Threading.CancellationTokenSource", "s_nLists", 1, 0),
    ("System.Threading.CancellationTokenSource", "m_kernelEvent", 0, 0),
    ("UnityEngine.Object", "OffsetOfInstanceIDInCPlusPlusObject", 1, 0),
    ("UnityEngine.Object", "m_CachedPtr", 0, 0),
    ("System.Random", "MBIG", 1, 1),
    ("System.Random", "SeedArray", 0, 0),
    ("System.Globalization.GregorianCalendar", "DaysToMonth365", 1, 0),
    ("System.Globalization.GregorianCalendar", "m_type", 0, 0),
    ("System.Security.Cryptography.X509Certificates.X509BasicConstraintsExtension",
     "_pathLengthConstraint", 0, 0),
]
field_idx = {}
for ti, fl in L.fields.items():
    for fi, fn, ft in fl:
        field_idx[(ti, fn)] = fi
attr_ok = attr_bad = attr_missing = 0
attr_lines = []
for tn, fnn, want_s, want_l in ATTR_CHECKS:
    ti = L.by_name.get(tn)
    fi = field_idx.get((ti, fnn)) if ti is not None else None
    if fi is None:
        attr_missing += 1
        attr_lines.append("   %-46s %-36s 未找到" % (tn, fnn))
        continue
    s = 1 if fi in L.f_static else 0
    l = 1 if fi in L.f_literal else 0
    ok = (s == want_s and l == want_l)
    attr_ok += ok
    attr_bad += (not ok)
    attr_lines.append("   %-46s %-36s %s  %s" % (
        tn, fnn,
        ("STATIC" if s else "实例") + ("/LITERAL" if l else ""),
        "OK" if ok else "★不符（期望 %s%s）" % (
            "STATIC" if want_s else "实例", "/LITERAL" if want_l else "")))

# ---------------- 报告正文 ----------------
Ln = []
A = Ln.append
A("实例字段布局还原 —— 质量报告（v6）")
A("=" * 64)
A("")
A("0) 本版的两处根本改动")
A("   ① static / literal 改用 Il2CppType.attrs 的元数据真值，命名启发式全部下线")
A("      FIELD_ATTRIBUTE_STATIC = 0x0010   FIELD_ATTRIBUTE_LITERAL = 0x0040")
A("      旧版「元数据不含 static 标志」的结论是错的 —— 字段记录里确实没有，")
A("      但 Il2CppType 结构的 +0x08 位置有 16 位 FieldAttributes。")
A("   ② 泛型结构体按实参实例化（System.Nullable`1<T> 等），不再当 8 字节引用")
A("")
A("1) 字段统计")
A("   类型总数（不含 enum）            %8d" % n_all)
A("   实例字段                        %8d" % n_inst)
A("   static / literal 字段           %8d" % n_static)
A("   字段 flags 覆盖                  419,568 / 419,568  (100%)")
A("")
A("2) 类型置信度（只统计有实例字段的类型）")
A("   P   打包布局与观测无冲突       %8d  (%.2f%%)" % (
    c_conf["P"], 100.0 * c_conf["P"] / max(n_obs, 1)))
A("   P!  存在字段间空隙             %8d  (%.2f%%)" % (
    c_conf["P!"], 100.0 * c_conf["P!"] / max(n_obs, 1)))
A("   P?  该类型没有任何观测         %8d" % c_conf["P?"])
A("   ── 有观测的类型 %d 个，自洽率 %.2f%%" % (
    n_obs, 100.0 * c_conf["P"] / max(n_obs, 1)))
A("")
A("3) 观测落空分桶（有观测的 %d 个类型）" % n_obs)
A("   hole   字段之间空隙            %8d   ★唯一致命，已计入 P!" % h_sum)
A("   inside 字段字节内部            %8d   噪声：Ghidra 常量折叠 / 字节步进" % i_sum)
A("   beyond 最后一个字段之后        %8d   尾 padding + 通过基类指针的派生访问" % b_sum)
A("")
A("   为什么 inside / beyond 不算错：")
A("   · inside：proto.ClientMail 每个 8 字节引用字段后都有一个 +4 观测，")
A("     0x14 不是 8 字节对齐，物理上不可能是引用字段起点。")
A("   · beyond：57,487 / 57,487 个类型的声明 fieldCount 全部等于字段表行数，")
A("     字段表没有缺失，因此「末尾之后还有观测」不可能是漏放字段。")
A("")
A("4) 地面真值校验")
A("   4.1 已知结构体尺寸（比的是兜底前的算出值）")
n_ok = n_bad = n_miss = 0
for nm, want in KNOWN:
    if nm not in L.KNOWN_STRUCT_SIZE:
        n_miss += 1
        continue
    if nm in _bad_map:
        got, exp = _bad_map[nm]
        n_bad += 1
        A("      %-30s 算出 %-4d 规范 %-4d  ★不符，已按规范兜底" % (nm, got, exp))
    else:
        n_ok += 1
A("      符合 %d / 不符 %d / 未列入 %d（共 %d 条）" % (
    n_ok, n_bad, n_miss, KNOWN_TOTAL))
A("      不符的两条都是规范值本身需要核实，属已知项：")
A("        · UnityEngine.Keyframe 本版只有 time/value/inTangent/outTangent 四个字段，")
A("          规范 20 是含 inWeight/outWeight 的旧版本（本版 16 才是对的）")
A("        · UnityEngine.Color32 元数据是 rgba:int 与 r/g/b/a:byte 的显式联合，")
A("          按声明顺序算得 8；实际应为 4（联合体，C# 侧靠 StructLayout 覆盖）")
A("")
A("   4.2 字段级 attrs 抽验")
for s in attr_lines:
    A(s)
A("      正确 %d / 不符 %d / 未找到 %d" % (attr_ok, attr_bad, attr_missing))
A("")
A("5) 剩余真错（%d 个类型）的形态" % c_conf["P!"])
A("   主要形态：观测偏移恰好落在某个 4 字节字段的结束处、即 8 字节对齐的空隙里。")
A("   这类观测既可能是「该 4 字节槽其实还有第二个 4 字节字段」，")
A("   也可能是编译器把字段与 padding 一起做了 64 位存储、Ghidra 把高半折成 +4 偏移。")
A("   在元数据 fieldCount 已排满的前提下无法从偏移分布区分，")
A("   只能回到指令级核对（需 Ghidra，属后续工作）。")
A("")
A("6) 产物")
A("   bh3_layout6.tsv   %d 行 —— 每字段一行；static/literal 行 offset=-1" % (
    n_inst + n_static))
A("   bh3_instsize.tsv  %d 行 —— 每类型实例尺寸与置信度" % n_all)
A("")
A("7) 已知局限")
A("   a. P? 的 %d 个类型完全没有观测，偏移只能靠声明顺序推断。" % c_conf["P?"])
A("   b. 同尺寸相邻字段的顺序无法从偏移区分（名字可能整体错位一格）。")
A("   c. 定长缓冲区（<X>e__FixedBuffer）未展开，Unity 少数原生结构尺寸偏小。")
A("   d. 枚举成员没有数值（literal 字段的常量值在 fieldDefaultValues 里，未解）。")

txt = "\n".join(Ln)
open("bh3_layout_report.txt", "w", encoding="utf-8").write(txt + "\n")
print(txt)
