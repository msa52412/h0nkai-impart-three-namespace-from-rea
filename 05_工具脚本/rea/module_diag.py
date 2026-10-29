#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""模块诊断：
   1) 数组 RVA 是否与记录物理顺序同序（用于判断「同尺寸并列按序配对」是否成立）
   2) 每模块的 .pdata 精确命中率、空指针率、值聚集度
   输出 bh3_module_diag.tsv
"""
import struct

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


pva, pvs, prs, prp = SEC[".pdata"]
BEG = set()
for k in range(0, prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + k * 12)
    if b:
        BEG.add(b)

mods = []
for ln in open(r"D:\Carol-start\_rea\bh3_modules_v2.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4 or not p[3].isdigit():
        continue
    mods.append({"idx": int(p[0]), "name": p[1], "arr": int(p[2], 16), "cnt": int(p[3])})

print("=== 1) 数组 RVA 与记录顺序的单调性 ===")
print("（bh3_modules_v2.tsv 的行序 = 按条数降序，不是物理序；改用 record A 排序检查）")

# 重新取 record A（与 token_seg 相同的锚点规则）
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


def w32(rva):
    r = rva2raw(rva)
    return None if r is None else struct.unpack_from("<I", d, r)[0]


recA = {}
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
        recA.setdefault(s, A)

seq = [(recA[m["name"]], m["arr"], m["name"]) for m in mods if m["name"] in recA]
seq.sort()
inv = sum(1 for i in range(1, len(seq)) if seq[i][1] < seq[i - 1][1])
print("可配对模块 %d 个；按记录 A 排序后数组 RVA 出现逆序 %d 处" % (len(seq), inv))
for i in range(1, min(len(seq), 12)):
    print("   A %08X -> arr %08X   %s" % (seq[i][0], seq[i][1], seq[i][2][:40]))

print()
print("=== 2) 每模块命中率 ===")
rows = []
for m in mods:
    raw = rva2raw(m["arr"])
    cnt = m["cnt"]
    exact = null = 0
    vals = []
    for i in range(cnt):
        v = struct.unpack_from("<Q", d, raw + i * 8)[0]
        if v == 0:
            null += 1
            continue
        rva = v - IB
        if rva in BEG:
            exact += 1
        vals.append(rva)
    live = cnt - null
    # 聚集度：相邻（排序后）差 == 0x20 的比例（小函数密集区）
    vals.sort()
    near = sum(1 for i in range(1, len(vals)) if vals[i] - vals[i - 1] <= 0x40)
    rows.append((m["name"], cnt, live, exact, null,
                 100.0 * exact / max(1, live), 100.0 * near / max(1, len(vals) - 1)))

rows.sort(key=lambda r: r[5])
print("%-42s %8s %8s %8s %7s %7s %7s" % ("module", "cnt", "live", "exact", "null%", "hit%", "紧密%"))
for r in rows[:8]:
    print("%-42s %8d %8d %8d %6.1f%% %6.1f%% %6.1f%%" % r)
print("   ...")
for r in rows[-8:]:
    print("%-42s %8d %8d %8d %6.1f%% %6.1f%% %6.1f%%" % r)

with open(r"D:\Carol-start\_rea\bh3_module_diag.tsv", "w", encoding="utf-8") as f:
    f.write("module\tcount\tlive\texact\tnull\tarrayRVA\trecA\thit_pct\tdensity_pct\n")
    for r in sorted(rows, key=lambda x: -x[1]):
        name = r[0]
        m = next(x for x in mods if x["name"] == name)
        f.write("%s\t%d\t%d\t%d\t%d\t%08X\t%08X\t%.2f\t%.2f\n"
                % (name, r[1], r[2], r[3], r[4], m["arr"], recA.get(name, 0), r[5], r[6]))
print("\n已写 bh3_module_diag.tsv")
