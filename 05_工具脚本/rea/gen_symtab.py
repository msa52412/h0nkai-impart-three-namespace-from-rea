#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_symtab.py —— 合成「RVA → 完全限定方法名 + 签名」符号表，供 Ghidra 重命名用。

输入：bh3_types_v5.txt / bh3_methods_v2.tsv / bh3_method_addr.tsv
输出：bh3_symtab.tsv
  rva  ns  cls  method  ret  params  isStatic  token  module  aliasOf
"""
import csv
import re
import sys
from collections import defaultdict

M32 = 0xFFFFFFFF

# ---------- 类型表 ----------
types = {}
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    types[int(p[0])] = (p[1], p[2])  # (namespace, name)

# ---------- 方法表 ----------
methods = {}
with open("bh3_methods_v2.tsv", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        methods[int(r["idx"])] = r

# ---------- RVA ----------
addr = {}
with open("bh3_method_addr.tsv", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        v = r["rva"].strip()
        if v:
            addr[int(r["idx"])] = (int(v, 16), r["module"])

print("类型 %d / 方法 %d / 有地址方法 %d" % (len(types), len(methods), len(addr)))

BAD = re.compile(r"[^0-9A-Za-z_.$`<>]")


def clean(s, maxlen=120):
    """Ghidra 名字清洗：只留安全字符，` 与 <> 统一成 _，. 换成 _。"""
    if not s:
        return ""
    s = s.replace("`", "_").replace("<>", "_").replace("<", "_").replace(">", "_")
    s = s.replace(".", "_").replace(",", "_").replace(" ", "_").replace("/", "_")
    s = BAD.sub("_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:maxlen]


def split_params(pstr):
    """按顶层逗号切参数（考虑 <> () [] 嵌套）。"""
    if not pstr:
        return []
    out, depth, cur = [], 0, []
    for ch in pstr:
        if ch in "<([":
            depth += 1
        elif ch in ">)]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur).strip())
    return out


rows = []
seen_rva = {}
stat = defaultdict(int)
for idx in sorted(addr):
    rva, module = addr[idx]
    m = methods.get(idx)
    if m is None:
        stat["无方法记录"] += 1
        continue
    ns, cls = types.get(int(m["declTypeIdx"]), ("", m["declType"]))
    name = m["name"]
    gc = m["genericContainer"]
    if gc:
        name = name + "_G"            # 泛型方法标记（形参名见 §9E）
    flags = int(m["flags"], 16) if m["flags"] else 0
    is_static = 1 if (flags & 0x10) else 0
    alias = ""
    if rva in seen_rva:
        alias = seen_rva[rva]          # 泛型共享：同一函数体
        stat["泛型共享别名"] += 1
    else:
        seen_rva[rva] = "%s|%s|%s" % (ns, cls, name)
        stat["唯一函数体"] += 1
    nm = clean(name)
    if name[:1] == ".":
        nm = "_" + nm
    rows.append((rva, ns, clean(cls), nm, clean(m["returnType"], 60),
                 m["params"], is_static, m["token"], module, alias))

print("输出 %d 行；统计 %s" % (len(rows), dict(stat)))

with open("bh3_symtab.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["rva", "ns", "cls", "method", "ret", "params", "isStatic",
                "token", "module", "aliasOf"])
    for r in rows:
        w.writerow([("%X" % r[0])] + list(r[1:]))

# 抽样
print("\n抽样 8 条：")
for r in rows[:4] + rows[len(rows) // 2:len(rows) // 2 + 4]:
    print("  RVA %08X  %s%s::%s  (%s)  static=%d" %
          (r[0], (r[1] + "." if r[1] else ""), r[2], r[3], r[5][:48], r[6]))
