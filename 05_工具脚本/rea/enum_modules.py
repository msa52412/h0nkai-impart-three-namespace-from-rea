#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""枚举 CodeGenModule 记录（以数组起点 A 为锚）。

实测布局：
    A-0x40  u64   （首记录为 0）
    A-0x38  u64   -> 前一个模块的 methodPointers（链表）
    A-0x30  u64   hash
    A-0x28  u32   ?
    A-0x20  u64   0
    A-0x18  u64   -> moduleName
    A-0x10  u64   -> moduleNameNoExt
    A-0x08  u32   timestamp
    A       u64[] methodPointers[count]     count = (A_next - A - 0x38) / 8
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


dir64 = set()
for nm, va, vs, rs, rp in SECS:
    if nm != ".reloc":
        continue
    p, end = rp, rp + rs
    while p + 8 <= end:
        page, blk = struct.unpack_from("<II", d, p)
        if blk < 8 or p + blk > end:
            break
        for k in range((blk - 8) // 2):
            x = struct.unpack_from("<H", d, p + 8 + k * 2)[0]
            if (x >> 12) == 10:
                dir64.add(page + (x & 0xFFF))
        p += blk
dir64 = sorted(dir64)

runs = []
st = 0
for i in range(1, len(dir64) + 1):
    if i == len(dir64) or dir64[i] - dir64[i - 1] != 8:
        if i - st >= 16:
            runs.append((dir64[st], i - st))
        st = i


def code_ratio(rva, ln, steps=64):
    r = rva2raw(rva)
    if r is None or r < 0 or r + ln * 8 > len(d):
        return 0.0
    step = max(1, ln // steps)
    nc = n = 0
    for k in range(0, ln, step):
        v = struct.unpack_from("<Q", d, r + k * 8)[0]
        n += 1
        if LO <= v < HI:
            nc += 1
    return nc / n if n else 0.0


cand = [(rva, ln) for rva, ln in runs if code_ratio(rva, ln) > 0.5]
print("DIR64 %d 槽；游程(>=16) %d；代码数组候选 %d，合计 %d 条"
      % (len(dir64), len(runs), len(cand), sum(c[1] for c in cand)))

# ---- 以 A-0x18 读名字 ----
mods = []
others = []
for rva, ln in cand:
    nm = cstr(q(rva - 0x18)) if q(rva - 0x18) else None
    if nm and ("." in nm or nm.endswith("dll") or ".dll" in nm.lower()):
        mods.append([rva, ln, nm, cstr(q(rva - 0x10)), w32(rva - 8), q(rva - 0x38)])
    else:
        others.append((rva, ln, nm))

print("识别为模块记录 %d 个；未识别 %d 个" % (len(mods), len(others)))

# ---- 用链表补精确 count ----
byA = {m[0]: m for m in mods}
pred = {}
for m in mods:
    p = m[5]
    if p is not None:
        pr = p - IB
        if pr in byA:
            pred[pr] = m[0]

for m in mods:
    A = m[0]
    succ = pred.get(A)
    if succ and succ > A:
        c = (succ - A - 0x38) // 8
        if 0 < c < 300000 and (succ - A - 0x38) % 8 == 0:
            m[1] = c

mods.sort(key=lambda x: -x[1])
print()
print("%-44s %-10s %-7s %-11s %s" % ("模块名", "数组RVA", "条数", "时间戳", "链表prev"))
tot = 0
for rva, ln, nm, nm2, ts, pv in mods:
    tot += ln
    print("%-44s %08X  %-7d %08X  %s" % (nm[:44], rva, ln, ts or 0,
                                          ("%08X" % (pv - IB)) if pv else "-"))
print()
print("模块 %d 个，方法指针合计 %d 条（目标 408458，差 %d）"
      % (len(mods), tot, tot - 408458))

if others:
    print("\n未识别为模块的代码数组 %d 个，合计 %d 条，前 15：" % (len(others), sum(o[1] for o in others)))
    for rva, ln, nm in sorted(others, key=lambda x: -x[1])[:15]:
        print("  RVA %08X %6d 条  A-0x18=%s" % (rva, ln, nm))
