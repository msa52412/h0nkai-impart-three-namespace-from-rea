#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_sigs.py —— 生成「函数签名规格」，供 Ghidra 侧 ApplySig.java 重定型

输入：
  bh3_methods_v2.tsv   idx token declTypeIdx declType name returnType flags slot iflags
                       paramCount genericContainer params
  bh3_method_addr.tsv  idx token module rva declType methodName ??
  bh3_structs2.tsv     typeIdx catPath name size conf nInst fields
  bh3_types_v5.txt     类型表（名字 → typeIdx）

输出 bh3_sigs.tsv：
  rva  isStatic  retKind  retName  params

  params 形如  kind:name  ，用 ; 分隔（kind 里不会出现 ; 和 :）
  kind:
    v             void
    i1 u1 i2 u2 i4 u4 i8 u8 f4 f8    定长标量（按真实宽度）
    p:<typeIdx>  指向该类型结构体的指针（引用类型 / 数组 / 泛型 / 大值类型）
    p            无结构体的裸指针（void*）
    s:<typeIdx>  按值传的小值类型（尺寸 ≤ 8，MS x64 走寄存器）

为什么要区分 s / p：
  MS x64 下 >8 字节的值类型按隐藏指针传递，≤8 字节走寄存器。搞错会让整串参数错位。
"""
import csv
import re
import sys
from collections import defaultdict

# ---------- 类型表 ----------
types = {}
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    if len(p) < 9:
        continue
    ti = int(p[0])
    types[ti] = {"i": ti, "ns": p[1], "name": p[2], "parent": p[8],
                 "full": (p[1] + "." if p[1] else "") + p[2]}
by_name = {}
for t in types.values():
    by_name.setdefault(t["full"], t["i"])


def kind_of(ti):
    t = types.get(ti)
    if not t:
        return "?"
    if t["parent"] == "System.Enum":
        return "enum"
    if t["parent"] == "System.ValueType":
        return "struct"
    return "class"


# ---------- 结构体尺寸 ----------
ssize = {}
for line in open("bh3_structs2.tsv", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    ssize[int(p[0])] = int(p[3])

# ---------- 标量 ----------
PRIM_KIND = {
    "bool": "u1", "byte": "u1", "sbyte": "i1", "char": "u2",
    "short": "i2", "ushort": "u2", "int": "i4", "uint": "u4",
    "float": "f4", "long": "i8", "ulong": "u8", "double": "f8",
    "System.Boolean": "u1", "System.Byte": "u1", "System.SByte": "i1",
    "System.Char": "u2", "System.Int16": "i2", "System.UInt16": "u2",
    "System.Int32": "i4", "System.UInt32": "u4", "System.Single": "f4",
    "System.Int64": "i8", "System.UInt64": "u8", "System.Double": "f8",
    "System.IntPtr": "i8", "System.UIntPtr": "u8",
    "void": "v", "System.Void": "v",
}


def tkind(tn):
    """C# 类型名 → kind"""
    tn = (tn or "").strip()
    if not tn:
        return "p"
    if tn in PRIM_KIND:
        return PRIM_KIND[tn]
    # 数组 / 泛型实例 / 泛型形参 → 一律按指针
    if tn.endswith("[]") or "[" in tn or "<" in tn or "`" in tn:
        return "p"
    if re.fullmatch(r"!{0,2}\d+", tn) or re.fullmatch(r"[A-Z]\w{0,3}", tn):
        # 泛型形参 T / TOutput / !0 / !!0
        if tn not in by_name:
            return "p"
    ti = by_name.get(tn)
    if ti is None:
        return "p"
    k = kind_of(ti)
    if k == "enum":
        return "u4"
    if k == "struct":
        sz = ssize.get(ti)
        if sz is not None and 0 < sz <= 8:
            return "s:%d" % ti
        return "p:%d" % ti if ti in ssize else "p"
    return "p:%d" % ti if ti in ssize else "p"


def split_params(s):
    """按 ", " 切分参数表，但要跳过 <> 内部的逗号
    （例：System.Converter`2<TInput,TOutput> converter）"""
    if not s:
        return []
    out = []
    depth = 0
    cur = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch in "<([":
            depth += 1
        elif ch in ">)]":
            depth -= 1
        if ch == "," and depth == 0 and i + 1 < len(s) and s[i + 1] == " ":
            out.append("".join(cur))
            cur = []
            i += 2
            continue
        cur.append(ch)
        i += 1
    if cur:
        out.append("".join(cur))
    return [x.strip() for x in out if x.strip()]


def clean_name(s):
    s = re.sub(r"[^0-9A-Za-z_]", "_", s or "")
    s = re.sub(r"_+", "_", s).strip("_")
    if not s or s[0].isdigit():
        s = "a_" + s
    return s[:40]


# ---------- 方法表 ----------
methods = {}
with open("bh3_methods_v2.tsv", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        try:
            methods[int(r["idx"])] = r
        except (ValueError, KeyError):
            continue

# ---------- 地址表 ----------
addr = {}
with open("bh3_method_addr.tsv", encoding="utf-8", errors="replace") as f:
    next(f)
    for line in f:
        p = line.rstrip("\r\n").split("\t")
        if len(p) < 4:
            continue
        rva = p[3].strip()
        if not rva:
            continue
        try:
            addr[int(p[0])] = int(rva, 16)
        except ValueError:
            pass

print("方法 %d  有 rva %d" % (len(methods), len(addr)))

n_out = 0
n_static = 0
n_skip = 0
stat_kind = defaultdict(int)
seen_rva = set()
with open("bh3_sigs.tsv", "w", encoding="utf-8", newline="") as out:
    out.write("rva\tisStatic\tthisKind\tretKind\tretName\tparams\n")
    for idx, rva in sorted(addr.items(), key=lambda x: x[1]):
        r = methods.get(idx)
        if not r:
            n_skip += 1
            continue
        dti = int(r["declTypeIdx"])
        # 只处理能建出结构体的声明类型：否则 this 没意义，参数也无从对齐
        if dti not in ssize:
            n_skip += 1
            continue
        try:
            flags = int(r["flags"], 16)
        except ValueError:
            flags = 0
        is_static = 1 if (flags & 0x10) else 0
        ret = tkind(r["returnType"])
        if ret == "v":
            ret_kind, ret_name = "v", ""
        else:
            ret_kind, ret_name = ret, clean_name("ret")
        ps = []
        for i, one in enumerate(split_params(r["params"])):
            parts = one.rsplit(" ", 1)
            if len(parts) == 2:
                tn, pn = parts
            else:
                tn, pn = one, "a%d" % i
            k = tkind(tn)
            if k == "v":
                continue
            ps.append("%s:%s" % (k, clean_name(pn) or ("a%d" % i)))
            stat_kind[k.split(":")[0]] += 1
        if rva in seen_rva:
            continue
        seen_rva.add(rva)
        this_kind = "p:%d" % dti
        out.write("%X\t%d\t%s\t%s\t%s\t%s\n"
                  % (rva, is_static, this_kind, ret_kind, ret_name, ";".join(ps)))
        n_out += 1
        if is_static:
            n_static += 1

print("→ bh3_sigs.tsv  %d 行（其中 static %d，跳过 %d）" % (n_out, n_static, n_skip))
print("参数 kind 分布:", dict(sorted(stat_kind.items(), key=lambda x: -x[1])))
