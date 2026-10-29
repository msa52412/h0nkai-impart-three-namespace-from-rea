#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bh3_layout.py —— 还原每个 C# 类型的实例字段偏移（il2cpp 默认布局）。

规则：
  - class：Il2CppObject 头 16 字节（klass + monitor），基类字段在前，本类字段按声明顺序
  - struct：从 0 开始，字段按声明顺序 + 自然对齐（Pack=0）
  - enum：底层类型大小（默认 4，看 value__）
  - 引用类型字段 / 数组 / 泛型实例 / 泛型形参 → 8

输出：bh3_layout.tsv（typeIdx, typeName, kind, instSize, fieldIdx, fieldName, fieldType, offset）
"""
import csv
import re
import sys
from collections import defaultdict

OBJ_HEADER = 16
PRIM = {
    "bool": 1, "byte": 1, "sbyte": 1, "char": 2, "short": 2, "ushort": 2,
    "int": 4, "uint": 4, "float": 4, "long": 8, "ulong": 8, "double": 8,
    "IntPtr": 8, "UIntPtr": 8, "decimal": 16, "void": 0,
}

# ---------- 载入类型 ----------
types = {}      # idx -> dict
by_name = {}    # "ns.name" -> idx （同名多个时取第一个）
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    idx = int(p[0])
    ns, nm = p[1], p[2]
    types[idx] = {"idx": idx, "ns": ns, "name": nm, "parentIdx": int(p[7]),
                  "parent": p[8], "fields": []}
    key = (ns + "." + nm) if ns else nm
    by_name.setdefault(key, idx)

# ---------- 载入字段 ----------
nfield = 0
with open("bh3_fields.tsv", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        t = int(r["typeIdx"])
        if t in types:
            types[t]["fields"].append((int(r["fieldIdx"]), r["fieldName"], r["fieldType"]))
            nfield += 1
for t in types.values():
    t["fields"].sort()

print("类型 %d / 字段 %d" % (len(types), nfield))

GEN = re.compile(r"<[^<>]*>")


def strip_generic(s):
    prev = None
    while prev != s:
        prev = s
        s = GEN.sub("", s)
    return s


def resolve(tn):
    """fieldType 字符串 → 类型 idx 或 None"""
    s = tn.strip()
    if s.endswith("[]"):
        return None
    if s.endswith("&"):
        s = s[:-1]
    s = strip_generic(s).strip()
    if s in PRIM:
        return None
    return by_name.get(s)


def kind_of(idx):
    t = types[idx]
    p = t["parent"]
    if p == "System.ValueType":
        return "struct"
    if p == "System.Enum":
        return "enum"
    return "class"


memo_size = {}
in_prog = set()
unknown = defaultdict(int)


def size_of_idx(idx):
    if idx in memo_size:
        return memo_size[idx]
    if idx in in_prog:            # 环（只可能出现在错误数据里）
        return 8
    in_prog.add(idx)
    k = kind_of(idx)
    if k == "class":
        s = inst_size(idx)
    elif k == "enum":
        s = 4
        for _fi, fn, ft in types[idx]["fields"]:
            if fn == "value__":
                s = size_of_name(ft)
                break
    else:
        s = struct_size(idx)
    in_prog.discard(idx)
    memo_size[idx] = s
    return s


def size_of_name(tn):
    s = tn.strip()
    if s in PRIM:
        return PRIM[s]
    if s.endswith("[]") or s.startswith("!") or "<" in s:
        return 8
    if s.endswith("&"):
        return 8
    idx = resolve(s)
    if idx is None:
        unknown[s] += 1
        return 8
    return size_of_idx(idx)


def align(v, a):
    return (v + a - 1) // a * a


def struct_size(idx):
    off, maxal = 0, 1
    for _fi, fn, ft in types[idx]["fields"]:
        sz = size_of_name(ft)
        if sz == 0:
            continue
        a = min(sz, 8)
        off = align(off, a)
        off += sz
        maxal = max(maxal, a)
    return align(off, maxal) if off else 1


def parent_size(idx):
    t = types[idx]
    p = t["parent"]
    if not p or p == "System.Object":
        return OBJ_HEADER
    pi = resolve(p)
    if pi is None or pi == idx:
        return OBJ_HEADER
    return size_of_idx(pi)


def inst_size(idx):
    """返回实例总大小"""
    off = parent_size(idx)
    for _fi, fn, ft in types[idx]["fields"]:
        sz = size_of_name(ft)
        if sz == 0:
            continue
        a = min(sz, 8)
        off = align(off, a)
        off += sz
    return align(off, 8)


def layout(idx):
    """返回 [(offset, name, type)]"""
    out = []
    k = kind_of(idx)
    off = 0 if k != "class" else parent_size(idx)
    for _fi, fn, ft in types[idx]["fields"]:
        sz = size_of_name(ft)
        if sz == 0:
            continue
        a = min(sz, 8)
        off = align(off, a)
        out.append((off, fn, ft))
        off += sz
    return out


# ---------- 抽样自检 ----------
def show(name):
    idx = by_name.get(name)
    if idx is None:
        print("  [缺失] %s" % name)
        return
    k = kind_of(idx)
    print("  %-52s kind=%-6s size=%-4d fields=%d" %
          (name, k, size_of_idx(idx), len(types[idx]["fields"])))
    for off, fn, ft in layout(idx)[:8]:
        print("        +0x%02X  %-28s %s" % (off, fn, ft))


print("\n=== 已知类型自检 ===")
for n in ("System.String", "System.Collections.Generic.List`1",
          "System.Collections.Generic.Dictionary`2", "UnityEngine.Vector3",
          "UnityEngine.Vector2", "UnityEngine.Transform", "System.Object"):
    show(n)

# ---------- 全量输出 ----------
bad = 0
with open("bh3_layout.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["typeIdx", "ns", "cls", "kind", "instSize", "offset", "fieldName", "fieldType"])
    for idx in sorted(types):
        t = types[idx]
        try:
            k = kind_of(idx)
            sz = size_of_idx(idx)
            for off, fn, ft in layout(idx):
                w.writerow([idx, t["ns"], t["name"], k, sz, off, fn, ft])
        except Exception:
            bad += 1
print("\n写出 bh3_layout.tsv，异常类型 %d" % bad)
print("未知类型名（按引用 8 字节处理）Top10：")
for k, v in sorted(unknown.items(), key=lambda x: -x[1])[:10]:
    print("  %-50s %d" % (k, v))
