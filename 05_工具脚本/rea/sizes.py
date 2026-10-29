#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sizes.py —— 粗略值类型尺寸（只用于「返回类型是否走 sret」的判定，不追求精确）"""
import csv
from collections import defaultdict

PRIM = {
    "bool": 1, "byte": 1, "sbyte": 1, "char": 2, "short": 2, "ushort": 2,
    "int": 4, "uint": 4, "float": 4, "long": 8, "ulong": 8, "double": 8,
    "System.Boolean": 1, "System.Byte": 1, "System.SByte": 1, "System.Char": 2,
    "System.Int16": 2, "System.UInt16": 2, "System.Int32": 4, "System.UInt32": 4,
    "System.Single": 4, "System.Int64": 8, "System.UInt64": 8, "System.Double": 8,
    "System.IntPtr": 8, "System.UIntPtr": 8, "System.TypedReference": 8,
    "System.Decimal": 16, "void": 0,
}


def align(v, a):
    return v if a <= 1 else (v + a - 1) // a * a


types = {}
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    if len(p) < 9:
        continue
    types[int(p[0])] = (p[1], p[2], p[8], int(p[7]) if p[7] not in ("", "-1") else -1)

by_name = {}
for i, (ns, nm, pa, pi) in types.items():
    by_name.setdefault((ns + "." if ns else "") + nm, i)

fields = defaultdict(list)
with open("bh3_fields.tsv", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        fields[int(r["typeIdx"])].append(r["fieldType"])

_memo = {}

# ★ 若已产出 bh3_layout.tsv，就用「已解出的实例布局」回填真实尺寸
#   （粗略求和会把 static 字段算进去，导致 Vector2 这种 8 字节结构被误判成 sret）
_SOLVED = {}
try:
    import os
    if os.path.exists("bh3_layout.tsv"):
        with open("bh3_layout.tsv", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                if r["conf"] not in ("H", "R"):
                    continue
                try:
                    off = int(r["offset"])
                    sz = int(r["size"])
                except ValueError:
                    continue
                if off < 0 or sz <= 0:
                    continue
                ti = int(r["typeIdx"])
                e = off + sz
                if e > _SOLVED.get(ti, 0):
                    _SOLVED[ti] = e
        print("[sizes] 已回填 %d 个类型的解出尺寸" % len(_SOLVED))
except Exception as _e:
    print("[sizes] 未回填:", _e)


def kind_of(idx):
    t = types.get(idx)
    if not t:
        return "?"
    pa = t[2]
    if pa == "System.ValueType":
        return "struct"
    if pa == "System.Enum":
        return "enum"
    return "class"


def size_of_name(nm):
    if not nm:
        return 8
    nm = nm.strip()
    if nm in PRIM:
        return PRIM[nm]
    if nm.endswith("*") or nm.endswith("&") or nm.startswith("!") or "[" in nm or "<" in nm:
        return 8
    ti = by_name.get(nm)
    if ti is None:
        return 8
    k = kind_of(ti)
    if k == "enum":
        return 4
    if k == "struct":
        return struct_size(ti)
    return 8


def struct_size(idx, depth=0):
    if idx in _memo:
        return _memo[idx]
    if idx in _SOLVED:
        return _SOLVED[idx]
    if depth > 8:
        return 8
    _memo[idx] = 8
    cur = 0
    for ft in fields.get(idx, []):
        s = size_of_name(ft)
        if s == 0:
            continue
        cur = align(cur, min(s, 8)) + s
    cur = align(cur, 8)
    _memo[idx] = cur
    return cur


def is_sret(ret_name):
    """返回类型是否是「按值返回的大结构体」→ MS x64 用 rcx 传隐藏返回缓冲区"""
    if not ret_name:
        return False
    nm = ret_name.strip()
    if nm in PRIM or nm.endswith("*") or nm.endswith("&") or nm.startswith("!"):
        return False
    if "[" in nm:
        return False
    ti = by_name.get(nm)
    if ti is None:
        return False
    if kind_of(ti) != "struct":
        return False
    return struct_size(ti) > 8
