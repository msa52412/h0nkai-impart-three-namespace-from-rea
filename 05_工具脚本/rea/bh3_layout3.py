#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bh3_layout3.py —— 重建实例字段布局（v3）

相比 v2 的两处升级：
  1) 双观测集回退：先试「全部实例方法」的观测（更完整），失败再试「前 3 个方法」的观测（更干净）
  2) 属性约束：get_X / set_X 的观测把「字段名 → 偏移」直接绑定，作为 DP 的硬约束
     —— 这是消解「同尺寸相邻字段谁是谁」歧义的唯一可靠手段
     （例：Vector3 的 kEpsilon/x/y/z 四个 float，光看偏移集合分不出谁是谁）

输入：
  bh3_types_v5.txt / bh3_fields.tsv
  bh3_layout_obs_all.tsv    主观测（全部实例方法）
  bh3_layout_obs2.tsv       备观测（前 3 个方法）
  bh3_prop_obs.tsv          属性访问器观测（syntheticIdx 主键）
  bh3_prop_map.tsv          syntheticIdx → (typeIdx, propName, kind)
输出：
  bh3_layout.tsv

conf:
  H  精确命中
  R  松弛命中（允许 ≤3 个未观测实例字段）
  L  无解 → 退化为「前缀全实例」，仅供参考
  X  没有观测
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

# ---------------- 字段 ----------------
fields = defaultdict(list)
with open("bh3_fields.tsv", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        fields[int(r["typeIdx"])].append((int(r["fieldIdx"]), r["fieldName"], r["fieldType"]))

# 字段名 → 该类型内的下标
fidx_of = {}
for ti, fl in fields.items():
    d = {}
    for k, (_fi, fn, _ft) in enumerate(fl):
        d.setdefault(fn, k)
    fidx_of[ti] = d

# ---------------- 观测 ----------------
def load_obs(path):
    o = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                s = (r.get("offsets") or "").strip()
                arr = []
                if s:
                    for x in s.split(","):
                        try:
                            arr.append(int(x, 16))
                        except ValueError:
                            pass
                o[int(r["typeIdx"])] = sorted(set(arr))
    except FileNotFoundError:
        print("[!] 缺少 %s" % path)
    return o


obs_all = load_obs("bh3_layout_obs_all.tsv")
obs_3 = load_obs("bh3_layout_obs_3.tsv")
print("观测：all=%d 次=%d" % (len(obs_all), len(obs_3)))

# ---------------- 属性约束 ----------------
cons = {}          # (typeIdx, fieldIdx) -> offset ；-1 表示 static
ncons = 0
try:
    pmap = {}
    with open("bh3_prop_map.tsv", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            pmap[int(r["syntheticIdx"])] = (int(r["typeIdx"]), r["propName"], r["kind"])
    pobs = {}
    with open("bh3_prop_obs.tsv", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            s = (r.get("offsets") or "").strip()
            arr = []
            if s:
                for x in s.split(","):
                    try:
                        arr.append(int(x, 16))
                    except ValueError:
                        pass
            pobs[int(r["typeIdx"])] = sorted(set(arr))
    for sid, (ti, pn, kind) in pmap.items():
        arr = pobs.get(sid)
        if arr is None or len(arr) != 1:
            continue                      # 空 / 多偏移都不够确定，不用
        d = fidx_of.get(ti)
        if not d:
            continue
        k = d.get(pn)
        if k is None:
            k = d.get("<%s>k__BackingField" % pn)
        if k is None:
            continue
        cons[(ti, k)] = arr[0]
        ncons += 1
except FileNotFoundError:
    pass
print("属性硬约束 %d 条" % ncons)

# 每类型被探针覆盖的实例方法数（越少 → 观测越可能不完整，字段名越可能错位）
nprobe = {}
try:
    with open("bh3_layout_probe_all.tsv", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            nprobe[int(r["typeIdx"])] = len(r["rvas"].split(","))
except FileNotFoundError:
    pass
print("探针方法数已载入 %d 个类型" % len(nprobe))

# ---------------- 类型分类与尺寸 ----------------
def kind_of(idx):
    t = types.get(idx)
    if not t:
        return "?"
    p = t["parent"]
    if p == "System.ValueType":
        return "struct"
    if p == "System.Enum":
        return "enum"
    if p == "System.Object" or p == "":
        return "class"
    pi = t["parentIdx"]
    if pi >= 0 and pi in types:
        pk = kind_of(pi)
        return "class" if pk == "class" else pk
    return "class"


_size_memo = {}
_align_memo = {}


def align_of_name(nm):
    """字段类型的自然对齐。结构体取「其字段对齐的最大值」（上限 8），
    不是 min(size,8)——Vector3 是 12 字节但对齐只有 4。"""
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
        return inst_size(ti, 0)
    return 8


def inst_size(idx, depth=0):
    if idx in _size_memo:
        return _size_memo[idx]
    if depth > 12:
        return 8
    _size_memo[idx] = 8
    t = types.get(idx)
    if not t:
        return 8
    k = kind_of(idx)
    if k == "enum":
        _size_memo[idx] = 4
        return 4
    base = 0 if k == "struct" else 16
    if k == "class" and t["parentIdx"] >= 0:
        p = t["parentIdx"]
        if p in types and p != idx:
            base = inst_size(p, depth + 1)
    cur = base
    for _fi, _fn, ft in fields.get(idx, []):
        s = size_of_type_name(ft)
        if s == 0:
            continue
        cur = align(cur, align_of_name(ft)) + s
    cur = align(cur, 8)
    _size_memo[idx] = cur
    return cur


# ---------------- 求解 ----------------
def solve(idx):
    fl = fields.get(idx, [])
    n = len(fl)
    k = kind_of(idx)
    if k == "enum":
        return "X", [True] * n, 0
    base0 = 0 if k == "struct" else 16

    Oall = obs_all.get(idx, [])
    O3 = obs_3.get(idx, [])
    if k == "struct":
        for arr in (Oall, O3):
            if arr and arr[0] != 0:
                arr.insert(0, 0)
    if not Oall and not O3:
        return "X", [True] * n, base0

    cand_base = [base0]
    if k == "class":
        t = types[idx]
        pi = t["parentIdx"]
        if pi >= 0 and pi in types:
            pb = inst_size(pi, 0)
            if pb not in cand_base:
                cand_base.append(pb)
        ref = Oall or O3
        if ref and 16 <= ref[0] <= 0x2000 and ref[0] not in cand_base:
            cand_base.append(ref[0])

    sizes = [size_of_type_name(ft) for _fi, _fn, ft in fl]
    als = [align_of_name(ft) for _fi, _fn, ft in fl]
    mycons = {f: o for (t, f), o in cons.items() if t == idx}

    def search(base, Oset, maxex, budget=200000):
        sols = []
        steps = [0]
        memo = set()
        flags = []

        def dfs(i, j, cur, ex):
            if sols or steps[0] > budget:
                return
            steps[0] += 1
            if i == n:
                if j == len(Oset):
                    sols.append((list(flags), base, ex, cur))
                return
            key = (i, j, cur, ex)
            if key in memo:
                return
            memo.add(key)
            s = sizes[i]
            if s <= 0:
                flags.append(False)
                dfs(i + 1, j, cur, ex)
                flags.pop()
                return
            a = align(cur, als[i])
            c = mycons.get(i)
            if c is not None:
                # 硬约束：属性访问器已经把「名字 → 偏移」钉死了
                if c < 0:
                    flags.append(False)
                    dfs(i + 1, j, cur, ex)
                    flags.pop()
                elif a == c and j < len(Oset) and Oset[j] == c:
                    flags.append(True)
                    dfs(i + 1, j + 1, a + s, ex)
                    flags.pop()
                return
            if j < len(Oset) and a == Oset[j]:
                flags.append(True)
                dfs(i + 1, j + 1, a + s, ex)
                flags.pop()
            flags.append(False)
            dfs(i + 1, j, cur, ex)
            flags.pop()
            if j < len(Oset) and a < Oset[j] and ex < maxex:
                flags.append(True)
                dfs(i + 1, j, a + s, ex + 1)
                flags.pop()

        dfs(0, 0, base, 0)
        return sols

    sets = []
    if Oall:
        sets.append(Oall)
    if O3 and O3 != Oall:
        sets.append(O3)

    for Oset in sets:
        for base in cand_base:
            Ob = [o for o in Oset if o >= base]
            if not Ob:
                continue
            sols = search(base, Ob, 0)
            if sols:
                return "H", sols[0][0], sols[0][1]
    for Oset in sets:
        for base in cand_base:
            Ob = [o for o in Oset if o >= base]
            if not Ob:
                continue
            sols = search(base, Ob, 3)
            if sols:
                return "R", sols[0][0], sols[0][1]

    mx = (Oall or O3)[-1]
    cur = cand_base[0]
    flags = []
    for k2, s in enumerate(sizes):
        if s <= 0:
            flags.append(False)
            continue
        a = align(cur, als[k2])
        if a > mx:
            flags.append(False)
            continue
        flags.append(True)
        cur = a + s
    return "L", flags, cand_base[0]


def layout(idx, flags, base):
    cur = base
    out = []
    for (fi, fn, ft), isinst in zip(fields.get(idx, []), flags):
        if not isinst:
            out.append(None)
            continue
        s = size_of_type_name(ft)
        cur = align(cur, align_of_name(ft))
        out.append(cur)
        cur += s
    return out, cur


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "bh3_layout.tsv"
    order = sorted(fields)

    # 迭代：先用粗略尺寸解一遍，再用「解出的实例大小」回填，重解。
    # 目的：结构体套结构体时（如 Bounds 含两个 Vector3），尺寸必须用解出的值而不是字段求和。
    results = {}
    for it in range(4):
        results = {ti: solve(ti) for ti in order}
        newmemo = {}
        for ti, (conf, flags, base) in results.items():
            if conf not in ("H", "R"):
                continue
            _o, end = layout(ti, flags, base)
            if end > 0:
                newmemo[ti] = end
        changed = 0
        for ti, v in newmemo.items():
            if _size_memo.get(ti) != v:
                changed += 1
            _size_memo[ti] = v
        nH = sum(1 for c, _f, _b in results.values() if c == "H")
        print("  迭代 %d: H=%d  尺寸更新 %d" % (it + 1, nH, changed))
        if changed == 0:
            break

    out = open(out_path, "w", encoding="utf-8", newline="")
    w = csv.writer(out, delimiter="	")
    w.writerow(["typeIdx", "typeName", "fieldIdx", "fieldName", "fieldType",
                "size", "isStatic", "offset", "conf", "nProbe"])
    stat = defaultdict(int)
    nrow = 0
    for ti in order:
        conf, flags, base = results[ti]
        stat[conf] += 1
        offs, _end = layout(ti, flags, base)
        tn = types.get(ti, {}).get("full", "?")
        for (fi, fn, ft), isinst, off in zip(fields[ti], flags, offs):
            w.writerow([ti, tn, fi, fn, ft, size_of_type_name(ft),
                        0 if isinst else 1,
                        off if off is not None else -1, conf, nprobe.get(ti, 0)])
            nrow += 1
    out.close()

    tot = sum(stat.values())
    print("\n[每类型置信度]")
    for c in "HRLX":
        print("   %s : %6d  (%5.1f%%)" % (c, stat[c], 100.0 * stat[c] / max(tot, 1)))
    print("输出 %d 行 → %s" % (nrow, out_path))

    print("\n[自检]")
    for nm, want in (("UnityEngine.Vector3", 12), ("UnityEngine.Vector2", 8),
                     ("UnityEngine.Vector4", 16), ("UnityEngine.Quaternion", 16),
                     ("UnityEngine.Color", 16), ("UnityEngine.Matrix4x4", 64),
                     ("UnityEngine.Rect", 16), ("UnityEngine.Bounds", 24),
                     ("System.String", 22), ("System.DateTime", 8)):
        ti = by_name.get(nm)
        if ti is None:
            print("   %-24s 未找到" % nm)
            continue
        conf, flags, base = results[ti]
        offs, end = layout(ti, flags, base)
        inst = [(fn, ft, o) for (fi, fn, ft), f2, o in zip(fields[ti], flags, offs) if f2]
        print("   %-24s conf=%s size=%d (期望 %d) 实例字段=%d"
              % (nm, conf, end, want, len(inst)))
        for fn, ft, o in inst[:6]:
            print("        +0x%-4X %-10s %s" % (o, ft, fn))

    with open("bh3_layout_stat.txt", "w", encoding="utf-8") as f:
        for c in "HRLX":
            f.write("%s\t%d\n" % (c, stat[c]))


if __name__ == "__main__":
    main()
