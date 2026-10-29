#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_structs2.py —— 从 bh3_layout4.tsv（纯打包布局）生成 Ghidra 结构体规格

与 gen_structs.py 的区别：
  * 布局来自「声明顺序对齐打包」，不再依赖观测偏移，因此没有 static 误判
  * 尺寸 = 打包结束位置（对齐到最大字段对齐），不是「观测到的最大偏移」
  * 继承链已展平（基类字段在前），Ghidra 结构体不需要继承概念
  * 只跳过 conf=P! 的类型（观测与打包矛盾，说明存在真实 static 字段，另案处理）

输出：
  bh3_structs2.tsv   typeIdx catPath name size conf nInst fields
  bh3_this2.tsv      rva typeIdx        （从旧 bh3_this.tsv 过滤到新结构体集合）
"""
import csv
import os
import re
from collections import defaultdict

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
    types[ti] = {"i": ti, "ns": p[1], "name": p[2], "parent": p[8]}
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


# ---------- 布局 ----------
LAYOUT_FILE = os.environ.get("BH3_LAYOUT", "bh3_layout6.tsv")
by_type = defaultdict(list)
with open(LAYOUT_FILE, encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        by_type[int(r["typeIdx"])].append(r)

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


def fsize(ft):
    """字段的自然对齐（枚举按 4，引用/未知按 8）"""
    ft = (ft or "").strip()
    if ft in TYPE2KIND:
        return {"u1": 1, "i1": 1, "u2": 2, "i2": 2,
                "u4": 4, "i4": 4, "f4": 4, "u8": 8, "i8": 8, "f8": 8}[TYPE2KIND[ft]]
    d = by_name.get(ft)
    if d is not None and kind_of(d) == "enum":
        return 4
    return 8


def align(v, a):
    return v if a <= 1 else (v + a - 1) // a * a


cand = {}
n_conf = defaultdict(int)
for ti, fl in by_type.items():
    if not fl:
        continue
    # P! 也收：打包本身是按声明顺序对齐算的，观测冲突多来自观测侧失真
    # （例如 UnityEngine.Bounds 观测冲突，但打包给出的 m_Center@0 / m_Extents@12 = 24
    #   恰好就是真值）。conf 会写进结构体描述，需要时可在 Ghidra 里按 conf 过滤。
    n_conf[fl[0]["conf"]] += 1
    fl = sorted(fl, key=lambda r: (int(r["offset"]), int(r["fieldIdx"])))
    keep = []
    prev = -1
    for r in fl:
        o = int(r["offset"])
        s = int(r["size"])
        if s <= 0 or o < prev:
            continue
        keep.append(r)
        prev = o + s
    if not keep:
        continue
    maxa = 1
    for r in keep:
        maxa = max(maxa, fsize(r["fieldType"]))
    size = align(max(int(r["offset"]) + int(r["size"]) for r in keep), maxa)
    if size > 0x4000:
        continue
    cand[ti] = (keep, size, fl[0]["conf"])

print("候选类型 %d   conf=%s" % (len(cand), dict(n_conf)))

# 值类型依赖拓扑排序
deps = defaultdict(set)
for ti, (keep, _sz, _c) in cand.items():
    if kind_of(ti) != "struct":
        continue
    for r in keep:
        ft = r["fieldType"].strip()
        if ft in TYPE2KIND or ft.endswith("*") or ft.endswith("&") \
                or ft.startswith("!") or "[" in ft or "<" in ft:
            continue
        d = by_name.get(ft)
        if d is not None and d != ti and kind_of(d) == "struct" and d in cand:
            deps[ti].add(d)

order = []
state = {}


def dfs(u):
    st = state.get(u, 0)
    if st == 1:
        return False
    if st == 2:
        return True
    state[u] = 1
    for v in sorted(deps.get(u, ())):
        if not dfs(v):
            deps[u].discard(v)
    state[u] = 2
    order.append(u)
    return True


for ti in sorted(cand):
    if kind_of(ti) == "struct":
        dfs(ti)
for ti in sorted(cand):
    if kind_of(ti) != "struct":
        order.append(ti)
print("拓扑顺序 %d（struct %d 在前）"
      % (len(order), sum(1 for x in order if kind_of(x) == "struct")))

used = set()
name_of = {}
for ti in order:
    t = types[ti]
    ns = clean(t["ns"]) if t["ns"] else "Global"
    nm = clean(t["name"])
    if (ns, nm) in used:
        nm = "%s_%d" % (nm, ti)
    used.add((ns, nm))
    name_of[ti] = (ns, nm)

rows = 0
with open("bh3_structs2.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["typeIdx", "catPath", "name", "size", "conf", "nInst", "fields"])
    for ti in order:
        keep, size, conf = cand[ti]
        k = kind_of(ti)
        parts = []
        cur = 0
        if k == "class":
            parts.append("0:ref:__klass")
            parts.append("8:ref:__monitor")
            cur = 16
        for r in keep:
            o, s = int(r["offset"]), int(r["size"])
            ft = r["fieldType"].strip()
            fn = clean(r["fieldName"], 60) or "f_%d" % int(r["fieldIdx"])
            if o > cur:
                parts.append("%d:pad:%d" % (cur, o - cur))
            if ft in TYPE2KIND and s in (1, 2, 4, 8):
                kd = TYPE2KIND[ft]
            else:
                d = by_name.get(ft)
                if d is not None and kind_of(d) == "enum":
                    # 枚举按底层整型宽度落成标量。否则会掉进下面的 pad 分支，
                    # 反编译里就变成 pad_60[0..3] = 0 而不是 device_type = 0。
                    kd = {1: "u1", 2: "u2", 4: "u4", 8: "u8"}.get(s, "u4")
                elif (d is not None and d != ti and kind_of(d) == "struct"
                        and d in cand and cand[d][1] == s):
                    kd = "st.%d" % d
                else:
                    kd = "ref" if s == 8 else "pad"
            if kd == "pad":
                parts.append("%d:pad:%d" % (o, s))
            else:
                parts.append("%d:%s:%s" % (o, kd, fn))
            cur = o + s
        w.writerow([ti, "/bh3/" + name_of[ti][0], name_of[ti][1], size,
                    conf, len(keep), ";".join(parts)])
        rows += 1
print("→ bh3_structs2.tsv  %d 个结构体" % rows)

# ---------- this 清单：过滤旧表到新结构体集合 ----------
n_in = n_out = 0
seen = set()
with open("bh3_this2.tsv", "w", encoding="utf-8", newline="") as f:
    f.write("rva\ttypeIdx\n")
    for line in open("bh3_this.tsv", encoding="utf-8", errors="replace").read().splitlines()[1:]:
        p = line.split("\t")
        if len(p) < 2:
            continue
        n_in += 1
        ti = int(p[1])
        if ti not in cand or p[0] in seen:
            continue
        seen.add(p[0])
        f.write("%s\t%d\n" % (p[0], ti))
        n_out += 1
print("→ bh3_this2.tsv  %d 个函数（旧表 %d，覆盖 %d 个类型）"
      % (n_out, n_in, len(set(int(x.split("\t")[1]) for x in
                              open("bh3_this2.tsv").read().splitlines()[1:]))))

print("\n抽样：")
for ti in order[:5]:
    keep, size, conf = cand[ti]
    print("   t%-6d %-44s size=%-4d %2d 字段  %s"
          % (ti, name_of[ti][0] + "/" + name_of[ti][1], size, len(keep), conf))
for ti in [6158]:
    if ti in cand:
        keep, size, conf = cand[ti]
        print("   t%-6d %-44s size=%-4d %2d 字段  %s"
              % (ti, name_of[ti][0] + "/" + name_of[ti][1], size, len(keep), conf))
