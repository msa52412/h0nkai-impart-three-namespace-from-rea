#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bh3_layout2.py —— 用「代码观测到的 this 偏移集合」重建实例字段布局

输入：
  bh3_types_v5.txt      类型表（idx / ns / name / parent）
  bh3_fields.tsv        字段表（typeIdx / typeName / fieldIdx / fieldName / fieldType）
  bh3_layout_obs.tsv    观测（typeIdx / offsets / nAccess / nLines）

输出：
  bh3_layout.tsv        typeIdx / fieldIdx / fieldName / fieldType / size / isStatic / offset / conf
  bh3_layout_stat.txt   统计

核心：IL2CPP 按「声明顺序」给实例字段分配偏移，static 字段不占实例空间。
所以问题 = 在字段序列里选出一个子序列当实例字段，使算出的偏移集合 == 观测集合。

conf 等级：
  H  唯一解，且观测集合被完全消费
  M  多解（取了「实例字段最多」的那个）
  L  无解 → 退化为「全部字段按声明顺序算」；offset 仅供参考
  X  没有任何观测，完全无法判定

DP 状态 (i, j, cur)：i=字段下标，j=已消费的观测偏移数，cur=当前偏移
"""
import csv
import re
import sys
from collections import defaultdict

MAXSTEP = 400000          # 搜索步数上限，超了就算 L
MAXSOL = 3                # 找到 3 个解就够判歧义

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


# ---------- 类型 ----------
types = {}
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    if len(p) < 9:
        continue
    i = int(p[0])
    ns, nm, parent = p[1], p[2], p[8]
    full = (ns + "." if ns else "") + nm
    types[i] = {"i": i, "ns": ns, "name": nm, "full": full, "parent": parent,
                "parentIdx": int(p[7]) if p[7] not in ("", "-1") else -1}

by_name = {}
for t in types.values():
    by_name.setdefault(t["full"], t["i"])

# ---------- 字段 ----------
fields = defaultdict(list)
with open("bh3_fields.tsv", encoding="utf-8", errors="replace") as f:
    rd = csv.DictReader(f, delimiter="\t")
    for r in rd:
        fields[int(r["typeIdx"])].append((int(r["fieldIdx"]), r["fieldName"], r["fieldType"]))

# ---------- 观测 ----------
OBS_PATH = sys.argv[1] if len(sys.argv) > 1 else "bh3_layout_obs.tsv"
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "bh3_layout.tsv"
obs = {}
try:
    with open(OBS_PATH, encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            s = r["offsets"].strip()
            o = []
            if s:
                for x in s.split(","):
                    try:
                        o.append(int(x, 16))
                    except ValueError:
                        pass
            obs[int(r["typeIdx"])] = sorted(set(o))
except FileNotFoundError:
    print("[!] 没有 %s" % OBS_PATH)
    sys.exit(1)

print("类型 %d / 有字段类型 %d / 有观测类型 %d"
      % (len(types), len(fields), sum(1 for v in obs.values() if v)))


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
    # 父类本身是 struct/enum 的（极少）沿用
    pi = t["parentIdx"]
    if pi >= 0 and pi in types:
        pk = kind_of(pi)
        return "class" if pk in ("class",) else pk
    return "class"


_size_memo = {}


def size_of_type_name(nm):
    """字段类型名 → 字节大小。未知一律当引用 8。"""
    if not nm:
        return 8
    nm = nm.strip()
    if nm in PRIM:
        return PRIM[nm]
    # 指针 / 引用形态
    if nm.endswith("*") or nm.endswith("&"):
        return 8
    if nm.startswith("!") or nm.startswith("!!"):
        return 8                      # 泛型参数 → 引用
    if "[" in nm:
        return 8                      # 数组 → 引用
    if "<" in nm:
        # 泛型：只有 Nullable<T>/ValueTuple 等值类型才有内联布局，这里保守当引用
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
    """递归求实例大小（值类型 = 字段和；类 = 头 + 字段）。深度保护。"""
    if idx in _size_memo:
        return _size_memo[idx]
    if depth > 12:
        return 8
    _size_memo[idx] = 8               # 占位防环
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
        cur = align(cur, min(s, 8)) + s
    cur = align(cur, 8)
    _size_memo[idx] = cur
    return cur


def layout_given_instance(idx, inst_flags, base):
    """按 inst_flags 算出每个字段的偏移，返回 (offsets, end)"""
    cur = base
    out = []
    for (fi, fn, ft), isinst in zip(fields.get(idx, []), inst_flags):
        if not isinst:
            out.append(None)
            continue
        s = size_of_type_name(ft)
        cur = align(cur, min(s, 8))
        out.append(cur)
        cur += s
    return out, cur


def solve(idx):
    """返回 (conf, inst_flags, base)

    模型：IL2CPP 按声明顺序给实例字段分配偏移，static 不占实例空间。
    问题：在字段序列里选一个子序列当实例字段，使算出的偏移集合 == 观测集合。

    conf:
      H  精确命中（观测集合被完全消费）
      R  松弛命中（允许 ≤3 个没被任何方法访问过的实例字段）
      L  无解 → 退化为「前缀全实例」，仅供参考
      X  没有任何观测
    """
    fl = fields.get(idx, [])
    n = len(fl)
    O = list(obs.get(idx, []))
    k = kind_of(idx)
    if k == "enum":
        return "X", [True] * n, 0
    base0 = 0 if k == "struct" else 16

    # ★ 补偏移 0：x64 对 [this+0] 常写成 [rcx] 或 [rcx+0]，扫描器已能取到 0；
    #   若值类型观测里没有 0（首字段没人访问），补上它——值类型首实例字段必然在 0
    if k == "struct" and O and O[0] != 0:
        O = [0] + O

    cand_base = [base0]
    if k == "class":
        t = types[idx]
        pi = t["parentIdx"]
        if pi >= 0 and pi in types:
            pb = inst_size(pi, 0)
            if pb not in cand_base:
                cand_base.append(pb)
        if O and 16 <= O[0] <= 0x2000 and O[0] not in cand_base:
            cand_base.append(O[0])

    if not O:
        return "X", [True] * n, cand_base[0]

    sizes = [size_of_type_name(ft) for _fi, _fn, ft in fl]

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
            a = align(cur, min(s, 8))
            if j < len(Oset) and a == Oset[j]:
                # 优先：正好命中下一个观测偏移
                flags.append(True)
                dfs(i + 1, j + 1, a + s, ex)
                flags.pop()
            # 其次：static
            flags.append(False)
            dfs(i + 1, j, cur, ex)
            flags.pop()
            if j < len(Oset) and a < Oset[j] and ex < maxex:
                # 最后：没人访问过的实例字段（ctor 漏写）
                flags.append(True)
                dfs(i + 1, j, a + s, ex + 1)
                flags.pop()
            # a > Oset[j]：越过待命中偏移 → 只能 static（上面已试）

        dfs(0, 0, base, 0)
        return sols

    for base in cand_base:
        Ob = [o for o in O if o >= base]
        if not Ob:
            continue
        sols = search(base, Ob, 0)
        if sols:
            return "H", sols[0][0], sols[0][1]

    for base in cand_base:
        Ob = [o for o in O if o >= base]
        if not Ob:
            continue
        sols = search(base, Ob, 3)
        if sols:
            return "R", sols[0][0], sols[0][1]

    # L：退化为「前缀全实例」—— 一直算到越过最后一个观测偏移为止
    mx = O[-1]
    cur = cand_base[0]
    flags = []
    for s in sizes:
        if s <= 0:
            flags.append(False)
            continue
        a = align(cur, min(s, 8))
        if a > mx:
            flags.append(False)
            continue
        flags.append(True)
        cur = a + s
    return "L", flags, cand_base[0]


def main():
    out = open(OUT_PATH, "w", encoding="utf-8", newline="")
    w = csv.writer(out, delimiter="\t")
    w.writerow(["typeIdx", "typeName", "fieldIdx", "fieldName", "fieldType",
                "size", "isStatic", "offset", "conf"])

    stat = defaultdict(int)
    conf_of_type = {}
    nrow = 0
    for ti in sorted(fields):
        conf, flags, base = solve(ti)
        stat[conf] += 1
        conf_of_type[ti] = conf
        offs, end = layout_given_instance(ti, flags, base)
        tn = types.get(ti, {}).get("full", "?")
        for (fi, fn, ft), isinst, off in zip(fields[ti], flags, offs):
            s = size_of_type_name(ft)
            w.writerow([ti, tn, fi, fn, ft, s,
                        0 if isinst else 1,
                        off if off is not None else -1, conf])
            nrow += 1
    out.close()

    print("\n[每类型置信度]")
    for c in "HRLX":
        print("   %s : %6d  (%.1f%%)" % (c, stat[c], 100.0 * stat[c] / max(sum(stat.values()), 1)))
    print("输出 %d 行 → %s" % (nrow, OUT_PATH))

    # 关键类型自检
    print("\n[自检]")
    for nm, want in (("UnityEngine.Vector3", 12), ("UnityEngine.Vector2", 8),
                     ("UnityEngine.Vector4", 16), ("UnityEngine.Quaternion", 16),
                     ("UnityEngine.Color", 16), ("UnityEngine.Matrix4x4", 64)):
        ti = by_name.get(nm)
        if ti is None:
            print("   %-26s 类型未找到" % nm)
            continue
        conf, flags, base = solve(ti)
        offs, end = layout_given_instance(ti, flags, base)
        inst = [(fn, ft, o) for (fi, fn, ft), f2, o in zip(fields[ti], flags, offs) if f2]
        print("   %-26s conf=%s size=%d (期望 %d) 实例字段=%d"
              % (nm, conf, end, want, len(inst)))
        for fn, ft, o in inst[:8]:
            print("        +0x%-4X %-10s %s" % (o, ft, fn))

    with open("bh3_layout_stat.txt", "w", encoding="utf-8") as f:
        for c in "HRLX":
            f.write("%s\t%d\n" % (c, stat[c]))
    return conf_of_type


if __name__ == "__main__":
    main()
