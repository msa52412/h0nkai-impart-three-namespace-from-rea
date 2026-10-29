#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描 call rel32 / jmp rel32，定位指定函数的所有调用者。
用 .pdata 反查调用者所属函数，统计每个函数里的调用次数。
"""
import struct
import bisect
import sys

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"

TARGETS = {
    0x18043AB50: "FUN_18043ab50  字符串解密",
}

with open(DLL, "rb") as f:
    data = f.read()

e = struct.unpack_from("<I", data, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", data, coff + 2)[0]
optsz = struct.unpack_from("<H", data, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", data, opt + 24)[0]
secs = {}
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    name = data[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", data, o + 8)
    secs[name] = (va, vs, rs, rp)

t_va, t_vs, t_rs, t_rp = secs[".text"]
TEXT = data[t_rp:t_rp + t_rs]
TEXT_VA = IB + t_va

p_va, p_vs, p_rs, p_rp = secs[".pdata"]
nfunc = p_rs // 12
begins = []
ends = []
for i in range(nfunc):
    b, en = struct.unpack_from("<II", data, p_rp + i * 12)
    begins.append(b)
    ends.append(en)
order = sorted(range(nfunc), key=lambda i: begins[i])
sb = [begins[i] for i in order]
se = [ends[i] for i in order]


def func_of(rva):
    k = bisect.bisect_right(sb, rva) - 1
    if k < 0:
        return None
    if rva < se[k]:
        return sb[k]
    return sb[k] if rva - sb[k] < 0x8000 else None


# 扫 call/jmp rel32
calls = {va: [] for va in TARGETS}
n = len(TEXT)
for i in range(n - 5):
    op = TEXT[i]
    if op not in (0xE8, 0xE9):
        continue
    disp = struct.unpack_from("<i", TEXT, i + 1)[0]
    target = TEXT_VA + i + 5 + disp
    if target in calls:
        calls[target].append((TEXT_VA + i, op))

for va, desc in TARGETS.items():
    hits = calls[va]
    byfunc = {}
    for addr, op in hits:
        fb = func_of(addr - IB)
        byfunc.setdefault(fb, []).append((addr, op))
    print("\n" + "=" * 80)
    print("%s  (0x%X)" % (desc, va))
    print("  调用点 %d 处，分布在 %d 个函数" % (len(hits), len(byfunc)))
    for fb, lst in sorted(byfunc.items(), key=lambda kv: -len(kv[1])):
        tag = "FUN_%X" % (IB + fb) if fb is not None else "<无>"
        ops = "".join("C" if o == 0xE8 else "J" for _, o in lst)
        print("    %-14s %2d 处  %s  %s" %
              (tag, len(lst), ops, ", ".join("0x%X" % a for a, _ in lst[:8])))
