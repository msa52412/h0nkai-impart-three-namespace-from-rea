#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成「方法 → 模块 → 原生地址」全表，并用 .pdata 函数起点集校验。

方法到地址：
    module = 方法所在块对应的模块（按条数配对）
    rid    = token & 0xFFFFFF
    addr   = *(module.array + (rid-1)*8)      // 0 表示无编译代码
"""
import struct
import csv
from collections import Counter, defaultdict

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


# ---------- 1. .pdata 函数起点集 ----------
pdata = []
for nm, va, vs, rs, rp in SECS:
    if nm != ".pdata":
        continue
    for k in range(0, rs // 12):
        b, en, ui = struct.unpack_from("<III", d, rp + k * 12)
        if b == 0:
            continue
        pdata.append(b)
pdata = sorted(set(pdata))
pstart = set(pdata)
print(".pdata 函数起点 %d 个，RVA 范围 %X..%X" % (len(pstart), pdata[0], pdata[-1]))

# ---------- 2. 模块表 ----------
mods = []
with open(r'D:\Carol-start\_rea\bh3_modules_v2.tsv', encoding='utf-8') as f:
    r = csv.reader(f, delimiter='\t')
    next(r)
    for a in r:
        mods.append({"name": a[1], "arr": int(a[2], 16), "cnt": int(a[3])})
print("模块 %d 个" % len(mods))

# ---------- 3. 方法块 ----------
blocks = []
with open(r'D:\Carol-start\_rea\bh3_method_blocks.tsv', encoding='utf-8') as f:
    r = csv.reader(f, delimiter='\t')
    next(r)
    for a in r:
        blocks.append({"start": int(a[1]), "cnt": int(a[2])})
print("方法块 %d 个" % len(blocks))

# ---------- 4. 按条数配对（同尺寸按物理序 / 元数据序对齐）----------
by_size_mod = defaultdict(list)
for m in mods:
    by_size_mod[m["cnt"]].append(m)
for k in by_size_mod:
    by_size_mod[k].sort(key=lambda x: x["arr"])

by_size_blk = defaultdict(list)
for b in blocks:
    by_size_blk[b["cnt"]].append(b)
for k in by_size_blk:
    by_size_blk[k].sort(key=lambda x: x["start"])

unmatched = 0
ties = 0
for c, ms in by_size_mod.items():
    bs = by_size_blk.get(c, [])
    if len(bs) != len(ms):
        print("  [尺寸不匹配] %d：模块 %d / 块 %d" % (c, len(ms), len(bs)))
        unmatched += len(ms)
        continue
    if len(ms) > 1:
        ties += len(ms)
    for m, b in zip(ms, bs):
        m["start"] = b["start"]
        b["mod"] = m
print("未匹配模块 %d 个；同尺寸并列涉及模块 %d 个" % (unmatched, ties))
assert all("start" in m for m in mods), "存在未配对模块"

# ---------- 5. 方法表 ----------
meths = []
with open(r'D:\Carol-start\_rea\bh3_methods_v2.tsv', encoding='utf-8') as f:
    r = csv.reader(f, delimiter='\t')
    next(r)
    for a in r:
        meths.append((int(a[0]), int(a[1], 16), a[3], a[4], a[7]))
print("方法 %d 条" % len(meths))

# 每模块的块起点 → 反查模块
start2mod = {}
for m in mods:
    start2mod[m["start"]] = m

# ---------- 6. 解析地址 ----------
arr_cache = {}
for m in mods:
    raw = rva2raw(m["arr"])
    arr_cache[m["name"]] = (raw, m["cnt"])

ok_code = 0
zero = 0
other = 0
hit_pdata = 0
out = open(r'D:\Carol-start\_rea\bh3_method_addr.tsv', 'w', encoding='utf-8')
out.write("idx\ttoken\tmodule\trva\tname\treturnType\tparams\n")

# 为每个方法找模块：按 start 排序 + 二分
starts = sorted(start2mod)
import bisect

for idx, tok, name, ret, params in meths:
    p = bisect.bisect_right(starts, idx) - 1
    m = start2mod[starts[p]]
    rid = tok & 0xFFFFFF
    raw, cnt = arr_cache[m["name"]]
    if 1 <= rid <= cnt:
        v = struct.unpack_from("<Q", d, raw + (rid - 1) * 8)[0]
    else:
        v = 0
    if v == 0:
        zero += 1
        rva = ""
    elif LO <= v < HI:
        ok_code += 1
        rva = v - IB
        if rva in pstart:
            hit_pdata += 1
    else:
        other += 1
        rva = v - IB
    out.write("%d\t%06X\t%s\t%s\t%s\t%s\t%s\n"
              % (idx, tok, m["name"], ("%X" % rva) if rva != "" else "", name, ret, params))
out.close()

print()
print("有代码地址 %d（%.2f%%）" % (ok_code, 100.0 * ok_code / len(meths)))
print("  其中落在 .pdata 函数起点 %d（%.2f%% of 有地址）" % (hit_pdata, 100.0 * hit_pdata / max(1, ok_code)))
print("空指针 %d（%.2f%%）" % (zero, 100.0 * zero / len(meths)))
print("越界值 %d" % other)
print("已写 bh3_method_addr.tsv")
