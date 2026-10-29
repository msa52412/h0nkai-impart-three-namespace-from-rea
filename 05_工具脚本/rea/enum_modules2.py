#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用「模块名字符串指针」正向枚举全部 CodeGenModule 记录。

记录锚点 A（= methodPointers 数组起点），字段：
    A-0x38  u64  -> 前一个模块 A
    A-0x18  u64  -> moduleName（"XXX.dll"）
    A-0x10  u64  -> moduleNameNoExt
    A-0x08  u32  timestamp
    A       u64[] methodPointers
记录连续排列：count_i = (A_{i+1} - A_i - 0x38) / 8
空指针不产生 DIR64 重定位，所以不能用游程起点当 A。
"""
import struct

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
IB = 0x180000000
LO = 0x180001000
HI = 0x186C56000
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
DATA = [(nm, va, vs, rs, rp) for nm, va, vs, rs, rp in SECS]


def rva2raw(rva):
    if 0 <= rva < 0x6C56000:
        return rva - 0xC00
    for nm, va, vs, rs, rp in DATA:
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


def string_at_va(va):
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


# ---- 收集 .data/.rdata 里所有指向 "*.dll" 的字符串指针 ----
recs = []
for nm, va, vs, rs, rp in DATA:
    if nm in (".reloc", ".text", ".pdata") or rs == 0:
        continue
    if nm not in (".data", ".rdata"):
        continue
    end = rp + min(rs, vs) if vs else rp + rs
    for r in range(rp, min(end, len(d)) - 8, 8):
        v = struct.unpack_from("<Q", d, r)[0]
        if not (IB <= v < IB + 0x12000000):
            continue
        s = string_at_va(v)
        if not s or not s.lower().endswith(".dll"):
            continue
        # 该槽位即 moduleName 字段 → A = S + 0x18
        srva = va + (r - rp)
        A = srva + 0x18
        ts = w32(A - 8)
        prev = q(A - 0x38)
        nm2 = string_at_va(q(A - 0x10)) if q(A - 0x10) else None
        recs.append({"A": A, "name": s, "name2": nm2, "ts": ts, "prev": prev, "slot": srva})

# 去重（同一 A 可能被 name 与 name2 两次命中）
uniq = {}
for r in recs:
    uniq.setdefault(r["A"], r)
recs = [uniq[k] for k in sorted(uniq)]
print("命中 *.dll 名字槽 %d 个，去重后候选记录 %d 个" % (len(recs), len(recs)))

# ---- 时间戳校验（IL2CPP 汇编时间戳量级 0x5C000000..0x68000000）----
good = [r for r in recs if r["ts"] and 0x5A000000 <= r["ts"] <= 0x6A000000]
print("时间戳合理 %d 个" % len(good))

# ---- 连续性校验：A_{i+1} - A_i - 0x38 能被 8 整除且 > 0 ----
good.sort(key=lambda r: r["A"])
kept = []
for i, r in enumerate(good):
    if i + 1 < len(good):
        span = good[i + 1]["A"] - r["A"] - 0x38
        r["cnt"] = span // 8 if span > 0 and span % 8 == 0 else None
    else:
        r["cnt"] = None
    kept.append(r)

# 深度优先保留「count 合理」的连续链
chain = []
for r in kept:
    if r["cnt"] is not None and 1 <= r["cnt"] <= 200000:
        chain.append(r)

print("连续链中记录 %d 个" % len(chain))
tot = sum(r["cnt"] for r in chain)
print("方法指针合计 %d 条（目标 408458，差 %d）" % (tot, tot - 408458))
print()
print("%-46s %-9s %-7s %-11s %s" % ("模块名", "数组RVA", "条数", "时间戳", "prev"))
for r in sorted(chain, key=lambda x: -x["cnt"])[:45]:
    print("%-46s %08X  %-7d %08X  %s" % (r["name"][:46], r["A"], r["cnt"],
                                         r["ts"], ("%08X" % (r["prev"] - IB)) if r["prev"] else "-"))

with open(r"D:\Carol-start\_rea\bh3_modules.tsv", "w", encoding="utf-8") as f:
    f.write("idx\tmodule\tarrayRVA\tcount\ttimestamp\tprevRVA\n")
    for i, r in enumerate(sorted(chain, key=lambda x: x["A"])):
        f.write("%d\t%s\t%08X\t%d\t%08X\t%s\n"
                % (i, r["name"], r["A"], r["cnt"], r["ts"],
                   ("%08X" % (r["prev"] - IB)) if r["prev"] else ""))
print("\n已写 bh3_modules.tsv")
