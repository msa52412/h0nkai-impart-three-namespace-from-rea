#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_structs.py —— 从 bh3_layout.tsv 生成 Ghidra 结构体规格

输出 bh3_structs.tsv：
  typeIdx \t catPath \t name \t size \t conf \t nInst \t fields

fields 形如  off:kind:name  ，用 ; 分隔
  kind:
    i1 u1 i2 u2 i4 u4 i8 u8 f4 f8   —— 定长标量（Ghidra 里长度必须精确匹配）
    ref                             —— 引用 / 指针（8 字节，先统一 void*）
    st:<depIdx>                     —— 内联值类型，指向另一个结构体
    pad:<n>                         —— 空洞填充

为什么要分「值类型优先」的顺序：值类型字段会内联进父结构体，
所以必须先建好被依赖的那个。类字段是指针，不存在循环依赖问题。

只输出 conf ∈ {H, R} 的类型：L 的偏移是推测的，X 完全没有观测。
"""
import csv
import re
from collections import defaultdict

PRIM_KIND = {
    1: None, 2: None, 4: None, 8: None,
}
TYPE2KIND = {
    "bool": "u1", "byte": "u1", "sbyte": "i1", "char": "u2",
    "short": "i2", "ushort": "u2", "int": "i4", "uint": "u4",
    "float": "f4", "long": "i8", "ulong": "u8", "double": "f8",
    "System.Boolean": "u1", "System.Byte": "u1", "System.SByte": "i1",
    "System.Char": "u2", "System.Int16": "i2", "System.UInt16": "u2",
    "System.Int32": "i4", "System.UInt32": "u4", "System.Single": "f4",
    "System.Int64": "i8", "System.UInt64": "u8", "System.Double": "f8",
    "System.IntPtr": "u8", "System.UIntPtr": "u8",
}

# ---------- 类型 ----------
types = {}
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    if len(p) < 9:
        continue
    ti = int(p[0])
    ns, nm, parent = p[1], p[2], p[8]
    types[ti] = {"i": ti, "ns": ns, "name": nm, "parent": parent}
by_name = {}
for t in types.values():
    by_name.setdefault((t["ns"] + "." if t["ns"] else "") + t["name"], t["i"])


def kind_of(ti):
    t = types.get(ti)
    if not t:
        return "?"
    pa = t["parent"]
    if pa == "System.ValueType":
        return "struct"
    if pa == "System.Enum":
        return "enum"
    return "class"


# ---------- 字段布局 ----------
by_type = defaultdict(list)
with open("bh3_layout.tsv", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        by_type[int(r["typeIdx"])].append(r)

GOOD = ("H", "R")
BADNAME = re.compile(r"[^0-9A-Za-z_]")


def clean(s, maxlen=90):
    if not s:
        return "t"
    s = s.replace("`", "_").replace("<", "_").replace(">", "_").replace(",", "_")
    s = BADNAME.sub("_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s or s[0].isdigit():
        s = "t_" + s
    return s[:maxlen]


# 先确定每个类型可用的实例字段（无重叠、偏移有效）
cand = {}
for ti, fl in by_type.items():
    if fl[0]["conf"] not in GOOD:
        continue
    inst = [r for r in fl if r["isStatic"] == "0"]
    inst = [r for r in inst if int(r["offset"]) >= 0 and int(r["size"]) > 0]
    if not inst:
        continue
    inst.sort(key=lambda r: (int(r["offset"]), int(r["fieldIdx"])))
    # 去重叠：后一个起点 < 前一个终点就丢弃（不应发生，防御性）
    keep = []
    prev = -1
    for r in inst:
        o = int(r["offset"])
        if o < prev:
            continue
        keep.append(r)
        prev = o + int(r["size"])
    if not keep:
        continue
    size = max(int(r["offset"]) + int(r["size"]) for r in keep)
    if size > 0x4000:          # 明显异常，跳过
        continue
    cand[ti] = (keep, size)

print("候选类型 %d" % len(cand))

# 值类型依赖图（只有 struct 之间可能内联）
deps = defaultdict(set)
for ti, (keep, _sz) in cand.items():
    if kind_of(ti) != "struct":
        continue
    for r in keep:
        ft = r["fieldType"].strip()
        if ft in TYPE2KIND:
            continue
        if ft.endswith("*") or ft.endswith("&") or ft.startswith("!") or "[" in ft or "<" in ft:
            continue
        d = by_name.get(ft)
        if d is not None and d != ti and kind_of(d) == "struct" and d in cand:
            deps[ti].add(d)

# 拓扑排序（值类型之间不应成环；成环则断开）
order = []
state = {}


def dfs(u):
    st = state.get(u, 0)
    if st == 1:          # 环 → 放弃这条依赖
        return False
    if st == 2:
        return True
    state[u] = 1
    ok = True
    for v in sorted(deps.get(u, ())):
        if not dfs(v):
            deps[u].discard(v)
    state[u] = 2
    order.append(u)
    return ok


for ti in sorted(cand):
    if kind_of(ti) == "struct":
        dfs(ti)
for ti in sorted(cand):
    if kind_of(ti) != "struct":
        order.append(ti)

print("拓扑顺序 %d（struct %d 在前）"
      % (len(order), sum(1 for x in order if kind_of(x) == "struct")))

# 命名去重
used = set()
name_of = {}
for ti in order:
    t = types[ti]
    ns = clean(t["ns"]) if t["ns"] else "Global"
    nm = clean(t["name"])
    key = (ns, nm)
    if key in used:
        nm = "%s_%d" % (nm, ti)
    used.add(key)
    name_of[ti] = (ns, nm)

# 输出
rows = 0
with open("bh3_structs.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["typeIdx", "catPath", "name", "size", "conf", "nInst", "fields"])
    for ti in order:
        keep, size = cand[ti]
        parts = []
        cur = 0
        # 类实例前 16 字节是 IL2CPP 对象头：{ Il2CppClass* klass; void* monitor; }
        if kind_of(ti) == "class" and int(keep[0]["offset"]) >= 16:
            parts.append("0:ref:__klass")
            parts.append("8:ref:__monitor")
            cur = 16
        for r in keep:
            o = int(r["offset"])
            s = int(r["size"])
            ft = r["fieldType"].strip()
            fn = clean(r["fieldName"], 60) or "f_%d" % int(r["fieldIdx"])
            if o > cur:
                parts.append("%d:pad:%d" % (cur, o - cur))
            if ft in TYPE2KIND and int(r["size"]) in (1, 2, 4, 8):
                kd = TYPE2KIND[ft]
            else:
                d = by_name.get(ft)
                if (d is not None and d != ti and kind_of(d) == "struct"
                        and d in cand and cand[d][1] == s):
                    kd = "st:%d" % d
                else:
                    kd = "ref" if s == 8 else "pad"
            if kd == "pad":
                parts.append("%d:pad:%d" % (o, s))
            else:
                parts.append("%d:%s:%s" % (o, kd, fn))
            cur = o + s
        w.writerow([ti, "/bh3/" + name_of[ti][0], name_of[ti][1], size,
                    by_type[ti][0]["conf"], len(keep), ";".join(parts)])
        rows += 1

print("→ bh3_structs.tsv  %d 个结构体" % rows)

# 抽样
print("\n抽样：")
for ti in order[:6]:
    keep, size = cand[ti]
    print("   t%-6d %-42s size=%-4d %d 字段"
          % (ti, name_of[ti][0] + "/" + name_of[ti][1], size, len(keep)))
