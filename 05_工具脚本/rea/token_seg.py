#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立证据：用 CodeGenModule 头里的 A-0x70（本模块最后一个方法 token）做分段。

若各模块按 token 升序排列，则相邻 last_token 之差 = 本模块方法数，
这个「差值多重集」应与「数组条数多重集」完全一致 —— 从而给出与顺序相关的精确配对。
"""
import struct

IB = 0x180000000
PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
d = open(PATH, "rb").read()

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


def rva2raw(rva):
    if 0 <= rva < 0x6C56000:
        return rva - 0xC00
    for nm, va, vs, rs, rp in SECS:
        if nm in (".reloc", ".text", ".pdata"):
            continue
        if va <= rva < va + max(vs, rs) and rs:
            return rp + (rva - va)
    return None


def q(rva):
    r = rva2raw(rva)
    return None if r is None else struct.unpack_from("<Q", d, r)[0]


def w32(rva):
    r = rva2raw(rva)
    return None if r is None else struct.unpack_from("<I", d, r)[0]


def cstr(va):
    if not (IB <= va < IB + 0x12000000):
        return None
    r = rva2raw(va - IB)
    if r is None or r >= len(d):
        return None
    z = d.find(b"\0", r, min(r + 160, len(d)))
    if z < 0:
        return None
    t = d[r:z]
    if len(t) < 4 or any(c < 0x20 or c > 0x7E for c in t):
        return None
    return t.decode("latin1")


recs = {}
for nm, va, vs, rs, rp in SECS:
    if nm not in (".data", ".rdata") or rs == 0:
        continue
    end = rp + min(rs, vs if vs else rs)
    for r in range(rp, min(end, len(d)) - 8, 8):
        v = struct.unpack_from("<Q", d, r)[0]
        if not (IB <= v < IB + 0x12000000):
            continue
        s = cstr(v)
        if not s or not s.lower().endswith(".dll"):
            continue
        A = va + (r - rp) + 0x18
        ts = w32(A - 8)
        if not ts or not (0x5A000000 <= ts <= 0x6A000000):
            continue
        recs.setdefault(A, {"A": A, "name": s, "ts": ts})

print("模块记录 %d 个" % len(recs))

# 读 A-0x70 的 last token
for A, r in recs.items():
    r["last"] = w32(A - 0x70)

rows = sorted(recs.values(), key=lambda r: r["A"])
print()
print("按物理地址排序的前 20 条记录头：")
print("%-44s %-10s %-10s %-10s" % ("module", "A", "A-0x70", "A-0x74"))
for r in rows[:20]:
    print("%-44s %08X   0x%08X 0x%08X" % (r["name"][:44], r["A"], r["last"] or 0, w32(r["A"] - 0x74) or 0))

# 校验：last token 是否都是 0x06 开头
bad = [r for r in rows if not r["last"] or (r["last"] >> 24) != 0x06]
print("\nA-0x70 不是 0x06xxxxxx 的记录：%d 个" % len(bad))
for r in bad[:10]:
    print("   %-44s 0x%08X" % (r["name"][:44], r["last"] or 0))

good = [r for r in rows if r["last"] and (r["last"] >> 24) == 0x06]
print("有效 last-token 记录 %d 个" % len(good))

# 按 token 排序，求相邻差
good.sort(key=lambda r: r["last"])
diffs = []
prev = 0
for r in good:
    rid = r["last"] & 0xFFFFFF
    r["rid"] = rid
    diffs.append(rid - prev)
    prev = rid
print("末位 last-RID = %d（应为 408458）" % good[-1]["rid"])
print("差值合计 %d" % sum(diffs))
print("差值 < 0 的个数 %d" % sum(1 for x in diffs if x <= 0))

# 与数组条数多重集比较
cnts = []
for ln in open(r"D:\Carol-start\_rea\bh3_modules_v2.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4 or not p[3].isdigit():
        continue
    cnts.append(int(p[3]))
print("数组条数 %d 个，合计 %d" % (len(cnts), sum(cnts)))

from collections import Counter
cd = Counter(d for d in diffs if d > 0)
cc = Counter(cnts)
print("差值多重集 == 条数多重集 ? %s" % (cd == cc))
only_d = cd - cc
only_c = cc - cd
print("仅在差值中: %d 种 %s" % (len(only_d), list(only_d.items())[:10]))
print("仅在条数中: %d 种 %s" % (len(only_c), list(only_c.items())[:10]))

with open(r"D:\Carol-start\_rea\bh3_token_seg.tsv", "w", encoding="utf-8") as f:
    f.write("order\tmodule\tA\trva_last_token\trid_last\tdiff\tarrayRVA\tcount\n")
    arr = {}
    for ln in open(r"D:\Carol-start\_rea\bh3_modules_v2.tsv", encoding="utf-8"):
        p = ln.rstrip("\n").split("\t")
        if len(p) < 4 or not p[3].isdigit():
            continue
        arr[p[1]] = (p[2], int(p[3]))
    for i, (r, df) in enumerate(zip(good, diffs)):
        a, c = arr.get(r["name"], ("", 0))
        f.write("%d\t%s\t%08X\t%08X\t%d\t%d\t%s\t%d\n"
                % (i, r["name"], r["A"], r["last"], r["rid"], df, a, c))
print("\n已写 bh3_token_seg.tsv")
