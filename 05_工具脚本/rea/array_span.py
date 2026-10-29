#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用「数组在内存中连续排列」直接测出每模块数组的确切条数：
   count_k = (arr_{k+1} - arr_k) / 8
   再与 RID 多重集还原出的 188 个尺寸做对照 —— 这是「与顺序相关」的精确配对。
"""
import struct
from collections import Counter

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
IB = 0x180000000
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
SEC = {nm: (va, vs, rs, rp) for nm, va, vs, rs, rp in SECS}


def rva2raw(rva):
    if 0 <= rva < 0x6C56000:
        return rva - 0xC00
    for nm, va, vs, rs, rp in SECS:
        if nm in (".reloc", ".text", ".pdata"):
            continue
        if va <= rva < va + max(vs, rs) and rs:
            return rp + (rva - va)
    return None


def cstr(va):
    if not (IB <= va < IB + 0x12000000):
        return None
    r = rva2raw(va - IB)
    if r is None or r >= len(d):
        return None
    z = d.find(b"\0", r, min(r + 120, len(d)))
    if z < 0:
        return None
    t = d[r:z]
    if len(t) < 4 or any(c < 0x20 or c > 0x7E for c in t):
        return None
    return t.decode("latin1")


def q(rva):
    r = rva2raw(rva)
    return None if r is None else struct.unpack_from("<Q", d, r)[0]


def w32(rva):
    r = rva2raw(rva)
    return None if r is None else struct.unpack_from("<I", d, r)[0]


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
        p = q(A - 0x38)
        if not p:
            continue
        recs.setdefault(p, {"arr": p - IB, "name": s, "A": A})
print("唯一数组 %d 个" % len(recs))

seq = sorted(recs.values(), key=lambda r: r["arr"])
print("数组 RVA 范围 %08X .. %08X" % (seq[0]["arr"], seq[-1]["arr"]))
gaps = Counter()
for i in range(len(seq) - 1):
    g = seq[i + 1]["arr"] - seq[i]["arr"]
    gaps[g % 8] += 1
print("相邻数组间距 mod 8 分布: %s" % gaps.most_common())

measured = []
for i in range(len(seq) - 1):
    measured.append((seq[i]["name"], seq[i]["arr"],
                     (seq[i + 1]["arr"] - seq[i]["arr"]) // 8,
                     seq[i + 1]["arr"] - seq[i]["arr"]))

rid = sorted([int(x) for x in open(r"D:\Carol-start\_rea\_rid_sizes.txt")], reverse=True)
print("RID 尺寸 %d 个，合计 %d" % (len(rid), sum(rid)))
ms = [m[2] for m in measured]
print("实测（连续差值）%d 个，合计 %d（最后一段无法测）" % (len(ms), sum(ms)))

cm = Counter(ms)
cr = Counter(rid)
print("多重集比对：实测 - RID = %s" % dict(list((cm - cr).items())[:10]))
print("            RID - 实测 = %s" % dict(list((cr - cm).items())[:10]))

# 差值为 8 的整数倍的相邻对，说明数组之间无其他数据
bad = [m for m in measured if m[3] % 8]
print("间距非 8 倍数：%d 个" % len(bad))

print()
print("前 20 段（按地址序）：")
print("%-44s %-9s %-8s %-8s" % ("module", "arr", "测得条数", "字节间距"))
for nm, arr, c, by in measured[:20]:
    print("%-44s %08X %-8d %-8d" % (nm[:44], arr, c, by))
print("   ...")
for nm, arr, c, by in measured[-8:]:
    print("%-44s %08X %-8d %-8d" % (nm[:44], arr, c, by))

with open(r"D:\Carol-start\_rea\bh3_array_span.tsv", "w", encoding="utf-8") as f:
    f.write("order\tmodule\tarrayRVA\tspan_count\tspan_bytes\trecA\n")
    for i, (nm, arr, c, by) in enumerate(measured):
        A = next(r["A"] for r in seq if r["arr"] == arr)
        f.write("%d\t%s\t%08X\t%d\t%d\t%08X\n" % (i, nm, arr, c, by, A))
print("\n已写 bh3_array_span.tsv")
