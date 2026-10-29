#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit_extra.py — 审计 Ghidra 建出但不在 `.pdata` 真函数起点集合里的函数

把 Ghidra 的 429,850 个函数减去 `.pdata` 真函数起点（424,760），
对每个"多出来"的地址判定其归属：

  A. 落在某个真函数的 [Begin, End) 区间内  → 几乎必然是**中指令误判**
     （一个函数的体内部不可能是另一个函数的起点）
  B. 属于 `.pdata` 里「非 16 对齐 且 非 CHAININFO」的条目 → 合法的保守收录
  C. 命中我们记录的叶子桩地址（bh3_gap_stubs.tsv）→ Ghidra 把桩建成了函数
  D. 落在未被任何条目覆盖的空档，且既非桩 → 全新发现，需人工看

输出 bh3_extra_audit.tsv，并打印分类统计。
"""
import bisect
import collections

TRUTH = r"D:\Carol-start\_rea\bh3_pdata_truth.tsv"
GHIDRA = r"D:\Carol-start\_rea\bh3_ghidra_funcs.txt"
STUBS = r"D:\Carol-start\_rea\bh3_gap_stubs.tsv"
OUT = r"D:\Carol-start\_rea\bh3_extra_audit.tsv"

BASE = 0x180000000

# ---- 真函数区间 ----
truth = []
for ln in open(TRUTH, encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 2:
        continue
    truth.append((int(p[0], 16), int(p[1], 16)))
truth.sort()
begins = [b for b, e in truth]
truth_set = {b for b, e in truth}
print("真函数区间 %d 条" % len(truth))

# ---- Ghidra 函数 ----
gh = {}
for ln in open(GHIDRA, encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4:
        continue
    gh[int(p[0], 16)] = (int(p[1]), int(p[2]), int(p[3]))
print("Ghidra 函数 %d 条" % len(gh))

# ---- 叶子桩 ----
stubs = set()
try:
    for ln in open(STUBS, encoding="utf-8"):
        p = ln.split("\t")
        if not p:
            continue
        t = p[0].strip()
        if not t or t.lower() == "rva":
            continue
        try:
            stubs.add(int(t, 16) if t.lower().startswith("0x") else int(t, 16))
        except ValueError:
            # 可能是十进制
            try:
                stubs.add(int(t))
            except ValueError:
                pass
except FileNotFoundError:
    pass
print("叶子桩地址 %d 条" % len(stubs))
# 桩表可能是 RVA，统一补成 VA
stub_va = set()
for s in stubs:
    if s < BASE:
        stub_va.add(BASE + s)
    else:
        stub_va.add(s)
stubs = stub_va

# ---- 非对齐非 CHAIN 的 .pdata 条目 ----
import struct
d = open(r"D:\Carol-start\_rea\UserAssembly_slim.dll", "rb").read()
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


def rva2raw(r):
    for nm, va, vs, rs, rp in SECS:
        if va <= r < va + max(vs, rs):
            return rp + (r - va)
    if 0x52E000 <= r < 0x6C56000:
        return r - 0x1400
    return None


pva, pvs, prs, prp = SEC[".pdata"]
nonalign = set()
all_begin = set()
for k in range(prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + 12 * k)
    if not b:
        continue
    all_begin.add(BASE + b)
    ur = rva2raw(ui)
    fl = (d[ur] >> 3) & 0x1F if (ur is not None and ur < len(d)) else 0
    if not (fl & 4) and b % 16:
        nonalign.add(BASE + b)
print("非对齐非CHAIN 条目 %d 条   .pdata 全部 Begin %d 条" % (len(nonalign), len(all_begin)))


def which_func(addr):
    """返回包含 addr 的真函数 (Begin, End)，否则 None"""
    i = bisect.bisect_right(begins, addr) - 1
    if i < 0:
        return None
    b, e2 = truth[i]
    if b <= addr < e2:
        return (b, e2)
    return None


# ---- 审计 ----
extra = sorted(set(gh) - truth_set)
print("\n多出 %d 个，开始分类" % len(extra))

cat = collections.Counter()
rows = []
for a in extra:
    inside = which_func(a)
    if inside:
        c = "A_落在真函数体内"
    elif a in nonalign:
        c = "B_非对齐非CHAIN条目"
    elif a in stubs:
        c = "C_叶子桩"
    elif a in all_begin:
        c = "D_其它pdata条目"      # 理论上不该出现
    else:
        c = "E_完全无登记"
    cat[c] += 1
    body, thunk, ext = gh[a]
    rows.append((a, c, body, thunk, 1 if inside else 0,
                 inside[0] if inside else 0, inside[1] if inside else 0))

print()
for k in sorted(cat):
    print("  %-22s %d" % (k, cat[k]))

# 对齐情况
print("\n按 16 对齐拆分：")
for k in sorted(cat):
    sub = [r for r in rows if r[1] == k]
    al = sum(1 for r in sub if r[0] % 16 == 0)
    print("  %-22s 对齐 %5d / 共 %5d" % (k, al, len(sub)))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("va\t分类\tbody\tthunk\t落在真函数内\t宿主Begin\t宿主End\n")
    for r in rows:
        f.write("%x\t%s\t%d\t%d\t%d\t%x\t%x\n" % r)
print("\n写出 %s（%d 行）" % (OUT, len(rows)))

# 给几个样例
print("\n=== 各类前 5 个样例 ===")
for k in sorted(cat):
    sub = [r for r in rows if r[1] == k][:5]
    if sub:
        print(" [%s]" % k)
        for r in sub:
            if r[4]:
                print("   %x  body=%d  宿主 %x..%x (体内偏移 +%d)" %
                      (r[0], r[2], r[5], r[6], r[0] - r[5]))
            else:
                print("   %x  body=%d  对齐=%s" % (r[0], r[2], r[0] % 16 == 0))
