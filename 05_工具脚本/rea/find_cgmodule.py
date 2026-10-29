#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""反查 721 个「代码指针数组」的宿主结构体。

原理：任何对数据数组的指针引用必然在 .reloc 里登记为 DIR64 槽位。
所以只在 DIR64 槽位上扫，命中值是候选数组 VA 的即为一次引用。

命中后按 IL2CPP 的 Il2CppCodeGenModule 常规布局做形状判定：
    +0x00 const char* moduleName
    +0x08 uint32_t    methodPointerCount
    +0x10 const Il2CppMethodPointer* methodPointers
判据：*(u32*)(slot-8) == 数组条数  → 认为 slot 就是 methodPointers 字段。
"""
import struct

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
IB = 0x180000000
LO = 0x180001000
HI = 0x186C56000
M32 = 0xFFFFFFFF

d = open(PATH, "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
opt = coff + 20
sh = opt + optsz
SECS = []
for i in range(nsec):
    o = sh + i * 40
    nm = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((nm, va, vs, rs, rp))

print("== 节表 ==")
for nm, va, vs, rs, rp in SECS:
    print("  %-8s VA %08X VSize %9d RawPtr %08X RawSize %9d" % (nm, va, vs, rp, rs))


def rva2raw(rva):
    """返回 raw 偏移。注意 .text 被篡改，用真实映射 VA=raw+0xC00。"""
    if rva < 0x6C56000:
        return rva - 0xC00
    for nm, va, vs, rs, rp in SECS:
        if nm in (".reloc", ".text", ".pdata"):
            continue
        if va <= rva < va + max(vs, rs) and rs:
            return rp + (rva - va)
    return None


# ---- 1. 重建 DIR64 集合 ----
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
            w = struct.unpack_from("<H", d, p + 8 + k * 2)[0]
            if (w >> 12) == 10:
                dir64.add(page + (w & 0xFFF))
        p += blk
dir64 = sorted(dir64)
print("\nDIR64 槽位 %d" % len(dir64))

# ---- 2. 重建代码指针数组候选 ----
runs = []
st = 0
for i in range(1, len(dir64) + 1):
    if i == len(dir64) or dir64[i] - dir64[i - 1] != 8:
        if i - st >= 64:
            runs.append((dir64[st], i - st))
        st = i

cand = []          # (rva, len)
for rva, ln in runs:
    raw = rva2raw(rva)
    if raw is None or raw < 0 or raw + ln * 8 > len(d):
        continue
    nc = 0
    for k in range(0, ln, max(1, ln // 64)):        # 抽样判定，足够
        v = struct.unpack_from("<Q", d, raw + k * 8)[0]
        if LO <= v < HI:
            nc += 1
    if nc > (ln // max(1, ln // 64)) * 0.5:
        cand.append((rva, ln))
print("代码指针数组候选 %d 个，合计 %d 条" % (len(cand), sum(c[1] for c in cand)))

cand_va = {IB + rva: (rva, ln) for rva, ln in cand}

# ---- 3. 在 DIR64 槽位上反查引用 ----
hits = {}          # candRVA -> [(slotRVA, value)]
for s in dir64:
    raw = rva2raw(s)
    if raw is None or raw < 0 or raw + 8 > len(d):
        continue
    v = struct.unpack_from("<Q", d, raw)[0]
    t = cand_va.get(v)
    if t:
        hits.setdefault(t[0], []).append((s, v))

print("命中引用的数组 %d / %d" % (len(hits), len(cand)))

# ---- 4. 形状判定 ----
def u32_at(rva):
    raw = rva2raw(rva)
    if raw is None or raw < 0 or raw + 4 > len(d):
        return None
    return struct.unpack_from("<I", d, raw)[0]


def u64_at(rva):
    raw = rva2raw(rva)
    if raw is None or raw < 0 or raw + 8 > len(d):
        return None
    return struct.unpack_from("<Q", d, raw)[0]


def cstr_at(va):
    if not (IB <= va < IB + len(d) + 0x2000):
        return None
    raw = rva2raw(va - IB)
    if raw is None or raw < 0 or raw >= len(d):
        return None
    z = d.find(b"\0", raw, min(raw + 128, len(d)))
    if z < 0:
        return None
    t = d[raw:z]
    if len(t) < 2 or any(c < 0x20 or c > 0x7E for c in t):
        return None
    return t.decode("latin1")


print("\n%-10s %-8s %-10s %-10s %-8s %s" % ("数组RVA", "条数", "槽位RVA", "slot-8(u32)", "匹配", "slot-0x10 名字"))
ok = []
for rva, ln in sorted(cand, key=lambda x: -x[1]):
    for s, v in hits.get(rva, []):
        cnt = u32_at(s - 8)
        nmva = u64_at(s - 0x10)
        nm = cstr_at(nmva) if nmva else None
        m = "YES" if cnt == ln else ""
        if cnt == ln:
            ok.append((rva, ln, s, nm))
        if len(hits.get(rva, [])) <= 3:
            print("%08X   %-8d %08X   %-10s %-8s %s" % (rva, ln, s, cnt, m, nm))

print("\n== 形状命中（*(slot-8)==条数）%d 个 ==" % len(ok))
for rva, ln, s, nm in ok[:60]:
    print("  数组 %08X  %6d 条   字段槽 %08X   名字 %s" % (rva, ln, s, nm))
print("形状命中合计条数 %d" % sum(x[1] for x in ok))
