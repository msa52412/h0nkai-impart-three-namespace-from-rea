#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按实测布局枚举 CodeGenModule 记录并汇总方法指针数组。

实测记录布局（从数组引用槽位 slot 反推）：
    slot-0x28  u64   hash（每记录不同，疑似校验）
    slot-0x20  u64   unk（多为 0，或小整数）
    slot-0x18  u64   -> moduleName   ("XXX.dll")
    slot-0x10  u64   -> moduleNameNoExt
    slot-0x08  u32   timestamp
    slot       u64[] methodPointers[count]
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


def w(rva):
    r = rva2raw(rva)
    return None if r is None or r < 0 or r + 4 > len(d) else struct.unpack_from("<I", d, r)[0]


def cstr(va):
    if not (IB <= va < IB + 0x12000000):
        return None
    r = rva2raw(va - IB)
    if r is None or r < 0 or r >= len(d):
        return None
    z = d.find(b"\0", r, min(r + 128, len(d)))
    if z < 0:
        return None
    t = d[r:z]
    if len(t) < 3 or any(c < 0x20 or c > 0x7E for c in t):
        return None
    return t.decode("latin1")


# ---- DIR64 ----
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
        if i - st >= 32:
            runs.append((dir64[st], i - st))
        st = i


def code_ratio(rva, ln, steps=48):
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


cand = [(rva, ln) for rva, ln in runs if ln >= 32 and code_ratio(rva, ln) > 0.5]
print("DIR64 %d 槽，游程(>=32) %d 个，代码指针数组 %d 个，合计 %d 条"
      % (len(dir64), len(runs), len(cand), sum(c[1] for c in cand)))

candVA = {IB + rva: (rva, ln) for rva, ln in cand}

# ---- 反查引用，取名字 ----
mods = []
unnamed = []
for s in dir64:
    v = q(s)
    if v is None:
        continue
    t = candVA.get(v)
    if not t:
        continue
    rva, ln = t
    nm = cstr(q(s - 0x18)) if q(s - 0x18) else None
    nm2 = cstr(q(s - 0x10)) if q(s - 0x10) else None
    ts = w(s - 8)
    rec = (nm or nm2, rva, ln, s, ts, q(s - 0x28), q(s - 0x20))
    if nm or nm2:
        mods.append(rec)
    else:
        unnamed.append(rec)

print("带模块名的记录 %d 个，无名记录 %d 个" % (len(mods), len(unnamed)))
print()
print("%-46s %-10s %-8s %-10s %-10s %s" % ("模块名", "数组RVA", "条数", "槽位RVA", "时间戳", "hash"))
seen = set()
tot = 0
for nm, rva, ln, s, ts, h1, h2 in sorted(mods, key=lambda x: x[0].lower()):
    if rva in seen:
        continue
    seen.add(rva)
    tot += ln
    print("%-46s %08X  %-8d %08X  %08X  %016X" % (nm[:46], rva, ln, s, ts or 0, h1 or 0))
print()
print("有名模块合计：%d 个，%d 条方法指针（目标 408458）" % (len(seen), tot))

if unnamed:
    print("\n无名代码数组（前 20）：")
    for nm, rva, ln, s, ts, h1, h2 in unnamed[:20]:
        print("  RVA %08X  %6d 条  槽位 %08X  ts %s  hash %016X" % (rva, ln, s, ts, h1 or 0))
    print("  无名合计 %d 条" % sum(x[2] for x in unnamed))
