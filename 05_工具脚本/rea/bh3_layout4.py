#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bh3_layout4.py —— 按「声明顺序 + 对齐规则」纯打包重建实例字段布局（v4）

为什么要换算法：
  v3 用「观测偏移集合 → 字段记录」做 DP 匹配，并把没观测到的字段判成 static。
  但 proto 类实际上几乎没有 static 字段，于是大量实例字段被误判 static 并从偏移序列里
  剔除，导致其后所有字段名整体前移。实测 /bh3/proto 下 44.5% 的字段被标 static。

  地面真值（proto.BulletinActivityConfig 构造函数，0x186637860）逐条核对：
    0x10 8B=0   → activity_id + activity_type
    0x18 8B=0   → begin_time + end_time
    0x20 4B=0   → bulletin_id
    0x28 8B ptr → mission_ids   (new List)
    0x30 8B ptr → type_param_list
    0x38 8B str → type_param_str
    0x40 8B=0   → min_player_level + max_player_level
    0x48 8B ptr → item_list
    0x50..0x70  → title_name/title_image/image_path/link_button/description
    0x78 4B=0   → weight
    0x80,0x88   → background_path / text_image_path
    0x90 8B ptr → currency_list
    0x98 8B str → unlock_param_str
    （extensionObject 构造函数没写 → 在 0xA0，实例尺寸 0xA8=168）
  ⇒ 全部 22 个字段都是实例字段，零 static，纯声明顺序对齐打包完全吻合。

算法：
  1) 展平继承链：基类字段在前，自身字段在后；类从 +16（IL2CPP 对象头）起，值类型从 0 起
  2) 逐个对齐打包：cur = align(cur, 自然对齐); offset = cur; cur += 尺寸
  3) 用观测偏移做校验（只校验，不参与定位）
  4) conf：
       P   打包结果覆盖了全部观测偏移（高置信）
       P!  有观测偏移不落在任何打包边界上（存在真实 static 或类型尺寸推断错）
       P?  该类型没有任何观测

输出：bh3_layout4.tsv
"""
import csv
import sys
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
    if a <= 1:
        return v
    return (v + a - 1) // a * a


# ---------------- 类型 ----------------
types = {}
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    if len(p) < 9:
        continue
    i = int(p[0])
    ns, nm, parent = p[1], p[2], p[8]
    types[i] = {"i": i, "ns": ns, "name": nm,
                "full": (ns + "." if ns else "") + nm,
                "parent": parent,
                "parentIdx": int(p[7]) if p[7] not in ("", "-1") else -1}
by_name = {}
for t in types.values():
    by_name.setdefault(t["full"], t["i"])

# ★ 注意：bh3_types_v5.txt 第 8 列（下标 7）不是父类型索引 ——
#   实测 t6158 的父类名是 System.Object，而该列值为 1（指向 <>f__AnonymousType0`1），
#   按它走继承链会把无关字段继承进来，把整张表的偏移推后 8 字节。
#   父类只能按名字反查。
for t in types.values():
    pn = (t["parent"] or "").strip()
    pi = by_name.get(pn, -1) if pn else -1
    if pi == t["i"]:
        pi = -1
    t["parentIdx"] = pi

# ---------------- 字段 ----------------
fields = defaultdict(list)
with open("bh3_fields.tsv", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        fields[int(r["typeIdx"])].append(
            (int(r["fieldIdx"]), r["fieldName"], r["fieldType"]))
for ti in fields:
    fields[ti].sort()

# ---------------- kind ----------------
_kind_memo = {}


def kind_of(idx, depth=0):
    if idx in _kind_memo:
        return _kind_memo[idx]
    t = types.get(idx)
    if not t:
        return "class"
    if depth > 24:
        return "class"
    _kind_memo[idx] = "class"          # 防环
    nm = t["full"]
    r = "class"
    if t["parent"] == "System.Enum":
        r = "enum"
    elif t["parent"] == "System.ValueType" or nm == "System.ValueType":
        r = "struct"
    else:
        pi = t["parentIdx"]
        if pi >= 0 and pi in types and pi != idx:
            pk = kind_of(pi, depth + 1)
            r = "class" if pk == "class" else pk
    _kind_memo[idx] = r
    return r


_align_memo = {}
_size_memo = {}


def align_of_name(nm):
    if not nm:
        return 8
    nm = nm.strip()
    if nm in PRIM:
        return max(1, min(PRIM[nm], 8))
    if nm.endswith("*") or nm.endswith("&") or nm.startswith("!") or nm.startswith("!!"):
        return 8
    if "[" in nm or "<" in nm:
        return 8
    ti = by_name.get(nm)
    if ti is None:
        return 8
    k = kind_of(ti)
    if k == "enum":
        return 4
    if k == "struct":
        return align_of_struct(ti)
    return 8


def align_of_struct(idx, depth=0):
    if idx in _align_memo:
        return _align_memo[idx]
    if depth > 12:
        return 8
    _align_memo[idx] = 1
    a = 1
    for _fi, _fn, ft in fields.get(idx, []):
        a = max(a, align_of_name(ft))
    a = min(a, 8)
    _align_memo[idx] = a
    return a


def size_of_type_name(nm):
    if not nm:
        return 8
    nm = nm.strip()
    if nm in PRIM:
        return PRIM[nm]
    if nm.endswith("*") or nm.endswith("&"):
        return 8
    if nm.startswith("!") or nm.startswith("!!"):
        return 8
    if "[" in nm or "<" in nm:
        return 8
    ti = by_name.get(nm)
    if ti is None:
        return 8
    k = kind_of(ti)
    if k == "enum":
        return 4
    if k == "struct":
        return packed_size(ti, 0)
    return 8


# ---------------- 继承链展平 ----------------
def chain(idx, depth=0):
    """返回 [最基类, ..., idx]（去掉接口/System.Object 之前的）"""
    out = []
    cur = idx
    seen = set()
    while cur >= 0 and cur in types and cur not in seen and depth < 32:
        seen.add(cur)
        out.append(cur)
        pi = types[cur]["parentIdx"]
        if pi == cur:
            break
        cur = pi
        depth += 1
    out.reverse()
    return out


def all_fields(idx):
    """展平后的 (ownerTypeIdx, fieldIdx, name, typeName) 列表，基类在前

    ★ 值类型（struct）不展平：它的 parent 是 System.ValueType，那只是个语义基类，
      本身没有任何数据成员。若把它当基类继承，会把 System.ValueType 的字段排在
      偏移 0 之前，把 Vector3 撑成 96 字节（实测踩过）。
    ★ 类也要在 System.Object / System.ValueType / System.Enum 处截断。
    """
    if kind_of(idx) != "class":
        return [(idx, fi, fn, ft) for fi, fn, ft in fields.get(idx, [])]
    STOP = ("System.Object", "System.ValueType", "System.Enum")
    out = []
    for t in chain(idx):
        if types.get(t, {}).get("full") in STOP:
            continue
        if kind_of(t) != "class":
            continue
        for fi, fn, ft in fields.get(t, []):
            out.append((t, fi, fn, ft))
    return out


def base_start(idx):
    k = kind_of(idx)
    if k == "enum":
        return 0
    if k == "struct":
        return 0
    return 16


# ---------------- 纯打包 ----------------
_pack_memo = {}


_SELF_STATIC = {}


_ALIAS = {
    "string": "System.String", "object": "System.Object",
    "bool": "System.Boolean", "byte": "System.Byte", "sbyte": "System.SByte",
    "char": "System.Char", "short": "System.Int16", "ushort": "System.UInt16",
    "int": "System.Int32", "uint": "System.UInt32", "long": "System.Int64",
    "ulong": "System.UInt64", "float": "System.Single", "double": "System.Double",
}


def skip_in_struct(idx, fn, ft):
    """值类型里排除「不占实例空间」的字段。

    元数据里没有 static/literal 标志，但值类型有两条几乎不会出错的结构性判据：
      1) 字段类型 == 声明类型自身 → 必然是 static readonly 单例
         （Vector3.zeroVector / Quaternion.identity / String.Empty …），
         实例字段不可能自包含
      2) 名字形如 kXxx 的基元类型 → Unity 惯例的 public const（literal，无存储）
         例：Vector3.kEpsilon、Mathf.kEpsilonNormalSqrt
    ★ 比较前要展开 C# 别名：元数据里 String.Empty 的类型写作 "string"，
      而声明类型全名是 "System.String"，不展开就漏判。
    """
    full = types.get(idx, {}).get("full")
    if ft and full:
        f2 = ft.strip()
        if _ALIAS.get(f2, f2) == full:
            return True
    if fn and len(fn) > 1 and fn[0] == "k" and fn[1].isupper():
        if ft and ft.strip() in PRIM:
            return True
    return False


def pack(idx, depth=0):
    """返回 [(owner, fieldIdx, name, typeName, offset, size)]，以及总尺寸"""
    if idx in _pack_memo:
        return _pack_memo[idx]
    if depth > 12:
        return [], 8
    _pack_memo[idx] = ([], 8)          # 防环
    k = kind_of(idx)
    if k == "enum":
        _pack_memo[idx] = ([], 4)
        return [], 4
    cur = base_start(idx)
    maxa = 1
    out = []
    for owner, fi, fn, ft in all_fields(idx):
        if k != "class" and skip_in_struct(idx, fn, ft):
            continue
        s = size_of_type_name(ft)
        if s <= 0:
            continue
        a = align_of_name(ft)
        maxa = max(maxa, a)
        cur = align(cur, a)
        out.append((owner, fi, fn, ft, cur, s))
        cur += s
    end = align(cur, maxa)
    _pack_memo[idx] = (out, end)
    return out, end


def packed_size(idx, depth=0):
    return pack(idx, depth)[1]


# ---------------- 观测 ----------------
def load_obs(path):
    o = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            next(f)
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) < 4:
                    continue
                s = set()
                for x in p[1].split(","):
                    x = x.strip()
                    if not x:
                        continue
                    try:
                        s.add(int(x, 16))
                    except ValueError:
                        pass
                o[int(p[0])] = s
    except FileNotFoundError:
        pass
    return o


obs_all = load_obs("bh3_layout_obs_all.tsv")
obs_3 = load_obs("bh3_layout_obs_3.tsv")

# ---------------- 主循环 ----------------
out = open("bh3_layout4.tsv", "w", encoding="utf-8", newline="")
w = csv.writer(out, delimiter="\t", lineterminator="\n")
w.writerow(["typeIdx", "typeName", "fieldIdx", "fieldName", "fieldType",
            "size", "isStatic", "offset", "conf", "nProbe"])

nP = nPb = nPq = 0
n_field = 0
bad_samples = []
for ti in sorted(types):
    t = types[ti]
    if kind_of(ti) == "enum":
        continue
    fl, end = pack(ti)
    if not fl:
        continue
    o = obs_all.get(ti, set())
    if not o:
        o = obs_3.get(ti, set())
    offs = set(x[4] for x in fl)
    miss = o - offs
    if not o:
        conf = "P?"
        nPq += 1
    elif miss:
        conf = "P!"
        nPb += 1
        if len(bad_samples) < 15:
            bad_samples.append((t["full"], end, sorted(o)[:12],
                                sorted(offs)[:12], sorted(miss)[:8]))
    else:
        conf = "P"
        nP += 1
    for owner, fi, fn, ft, off, s in fl:
        w.writerow([ti, t["full"], fi, fn, ft, s, 0, off, conf, len(o)])
        n_field += 1
out.close()

print("类型: P=%d  P!=%d  P?=%d  字段=%d" % (nP, nPb, nPq, n_field))
print("\n存在观测冲突的样例（前 15）：")
for full, end, o, offs, miss in bad_samples:
    print("  %-44s end=%-5d" % (full, end))
    print("     观测: %s" % ",".join("0x%x" % x for x in o))
    print("     打包: %s" % ",".join("0x%x" % x for x in offs))
    print("     未命中: %s" % ",".join("0x%x" % x for x in miss))
