#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""module_fold.py — 逐模块：方法数 / 去重地址数 / 折叠率 / 桩占比 / .pdata 命中率

验证命题：「模块命中率低」 ⇔ 「该模块大量方法被编译折叠成转发桩」
"""
import struct, collections

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
d = open(DLL, "rb").read()

e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
SECS = []
for i in range(nsec):
    o = coff + 20 + optsz + i * 40
    nm = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((nm, va, vs, rs, rp))
SEC = {nm: (va, vs, rs, rp) for nm, va, vs, rs, rp in SECS}


def rva2raw(rva):
    for nm, va, vs, rs, rp in SECS:
        if va <= rva < va + max(vs, rs):
            return rp + (rva - va)
    return rva - 0x1400


pva, pvs, prs, prp = SEC[".pdata"]
REAL = set()
for k in range(prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + 12 * k)
    if not b or b % 16:
        continue
    uraw = rva2raw(ui)
    if uraw is None:
        continue
    if ((d[uraw] >> 3) & 0x1F) & 0x4:
        continue
    REAL.add(b)

mods = collections.defaultdict(list)
with open(r"D:\Carol-start\_rea\bh3_method_addr.tsv", encoding="utf-8") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 7 or not p[3]:
            continue
        mods[p[2]].append(int(p[3], 16))

rows = []
for m, addrs in mods.items():
    n = len(addrs)
    uniq = len(set(addrs))
    hit = sum(1 for a in addrs if a in REAL)
    rows.append((m, n, uniq, 100.0 * uniq / n, 100.0 * hit / n))

rows.sort(key=lambda r: -r[1])
print("%-46s %8s %8s %8s %8s" % ("模块", "方法数", "去重地址", "去重率%", "命中率%"))
print("-" * 88)
for m, n, u, ur, hr in rows[:25]:
    print("%-46s %8d %8d %7.1f %8.2f" % (m[:46], n, u, ur, hr))
print("...")
for m, n, u, ur, hr in rows[-12:]:
    print("%-46s %8d %8d %7.1f %8.2f" % (m[:46], n, u, ur, hr))

# 分组统计
def grp(pred):
    sub = [r for r in rows if pred(r[0])]
    N = sum(r[1] for r in sub)
    U = sum(r[2] for r in sub)
    H = sum(r[1] * r[4] / 100.0 for r in sub)
    return len(sub), N, U, 100.0 * U / N if N else 0, 100.0 * H / N if N else 0


print()
print("%-30s %6s %9s %9s %8s %8s" % ("分组", "模块数", "方法数", "去重地址", "去重率%", "命中率%"))
for name, pred in [("ProtobufSerializer.*", lambda s: s.startswith("ProtobufSerializer.")),
                   ("NetCommand.*", lambda s: s.startswith("NetCommand.")),
                   ("UnityEngine.*", lambda s: s.startswith("UnityEngine.")),
                   ("mscorlib.dll", lambda s: s == "mscorlib.dll"),
                   ("Assembly-CSharp.dll", lambda s: s == "Assembly-CSharp.dll"),
                   ("MetaData.dll", lambda s: s == "MetaData.dll")]:
    a, b, c, d_, e_ = grp(pred)
    print("%-30s %6d %9d %9d %8.1f %8.2f" % (name, a, b, c, d_, e_))

tot_n = sum(r[1] for r in rows)
tot_u = sum(r[2] for r in rows)
print()
print("全局：方法 %d，去重地址 %d，折叠率 %.1f%%" % (tot_n, tot_u, 100.0 * (1 - tot_u / tot_n)))

with open(r"D:\Carol-start\_rea\bh3_module_fold.tsv", "w", encoding="utf-8") as f:
    f.write("module\tmethods\tuniq_addr\tuniq_pct\thit_pct\n")
    for m, n, u, ur, hr in sorted(rows, key=lambda r: -r[1]):
        f.write("%s\t%d\t%d\t%.2f\t%.2f\n" % (m, n, u, ur, hr))
print("已写 bh3_module_fold.tsv")
