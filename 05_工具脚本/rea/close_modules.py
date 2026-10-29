#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""闭合「模块 → 方法指针数组」。

实测 CodeGenModule 记录布局（锚点 A，紧跟在 A 之后就是下一个模块的数组）：
    A-0x38  u64  -> methodPointers（本模块的方法指针数组）
    A-0x30  u64  hash
    A-0x28  u32
    A-0x20  u64  0
    A-0x18  u64  -> moduleName
    A-0x10  u64  -> moduleNameNoExt
    A-0x08  u32  timestamp

精确条数：用 metadata 的 RID 多重集还原出的 188 个模块尺寸对齐
（数组区按 (代码指针|0) 连续延伸，长度 = 真实条数 + 1~3）。
"""
import struct
import csv

IB = 0x180000000
LO = 0x180001000
HI = 0x186C56000
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
    return None if r is None or r < 0 or r + 8 > len(d) else struct.unpack_from("<Q", d, r)[0]


def w32(rva):
    r = rva2raw(rva)
    return None if r is None or r < 0 or r + 4 > len(d) else struct.unpack_from("<I", d, r)[0]


def cstr(va):
    if not (IB <= va < IB + 0x12000000):
        return None
    r = rva2raw(va - IB)
    if r is None or r < 0 or r >= len(d):
        return None
    z = d.find(b"\0", r, min(r + 160, len(d)))
    if z < 0:
        return None
    t = d[r:z]
    if len(t) < 4 or any(c < 0x20 or c > 0x7E for c in t):
        return None
    return t.decode("latin1")


def run_len(rva, cap=400000):
    """数组区按 (代码指针 | 0) 连续延伸的长度。"""
    raw = rva2raw(rva)
    if raw is None or raw < 0:
        return 0
    n = 0
    while n < cap and raw + (n + 1) * 8 <= len(d):
        v = struct.unpack_from("<Q", d, raw + n * 8)[0]
        if LO <= v < HI or v == 0:
            n += 1
        else:
            break
    return n


# ---- 1. 收集 module 记录（名字槽 + 0x18 = A）----
recs = []
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
        recs.append({"A": A, "name": s, "ts": ts,
                     "arr": (q(A - 0x38) - IB) if q(A - 0x38) else None})
uniq = {}
for r in recs:
    uniq.setdefault(r["A"], r)
recs = [uniq[k] for k in sorted(uniq)]
print("模块记录 %d 个" % len(recs))

# ---- 2. 读数组长度 ----
for r in recs:
    r["run"] = run_len(r["arr"]) if r["arr"] else 0
recs = [r for r in recs if r["run"] > 0]
print("有有效数组的记录 %d 个，游程合计 %d" % (len(recs), sum(r["run"] for r in recs)))

# ---- 3. 与 RID 尺寸多重集对齐 ----
rid = sorted([int(x) for x in open(r"D:\Carol-start\_rea\_rid_sizes.txt")], reverse=True)
print("RID 尺寸 %d 个，合计 %d" % (len(rid), sum(rid)))

pairs = sorted(recs, key=lambda r: -r["run"])
n = min(len(pairs), len(rid))
ok = 0
for i in range(n):
    r = pairs[i]
    c = rid[i]
    r["cnt"] = c
    d_ = r["run"] - c
    if 0 <= d_ <= 4:
        ok += 1
print("对齐 %d 对，其中 run-rid ∈ [0,4] 的 %d 对" % (n, ok))
print("对齐后合计 %d（目标 408458）" % sum(r["cnt"] for r in pairs[:n]))

print()
print("%-42s %-9s %-10s %-8s %-7s %s" % ("模块", "数组RVA", "条数", "游程", "差", "时间戳"))
for r in pairs[:25]:
    print("%-42s %08X  %-10d %-8d %-7d %08X" % (r["name"][:42], r["arr"], r["cnt"],
                                                r["run"], r["run"] - r["cnt"], r["ts"]))

with open(r"D:\Carol-start\_rea\bh3_modules_v2.tsv", "w", encoding="utf-8") as f:
    f.write("idx\tmodule\tarrayRVA\tcount\trun\tdelta\ttimestamp\n")
    for i, r in enumerate(pairs):
        c = r.get("cnt", r["run"])
        f.write("%d\t%s\t%08X\t%d\t%d\t%d\t%08X\n"
                % (i, r["name"], r["arr"], c, r["run"], r["run"] - c, r["ts"]))
print("\n已写 bh3_modules_v2.tsv")
