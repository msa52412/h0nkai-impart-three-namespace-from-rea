#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读出 nestedTypes 数组并生成父子关系表。

数组位置：metadata + 0x1C43A70，32 位元素，长度 21429
（由「窗口内元素必须全是空 namespace 类型」判据全库唯一命中）

产物 bh3_nested.tsv：childIdx  parentIdx  childName  parentName
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
TYPES = r"D:\Carol-start\_rea\bh3_types_v5.txt"
OUT = r"D:\Carol-start\_rea\bh3_nested.tsv"

BASE = 0x118
M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
STEP = 0x5C
NT = 57487
ARR = 0x1C41FB0
NEED = 21429

dll = open(DLL, "rb").read()
e = struct.unpack_from("<I", dll, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", dll, coff + 2)[0]
optsz = struct.unpack_from("<H", dll, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", dll, opt + 24)[0]
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    vs, va, rs, rp = struct.unpack_from("<IIII", dll, o + 8)
    SECS.append((va, vs, rs, rp))


def u32va(va):
    rva = va - IB
    for vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else struct.unpack_from("<I", dll, rptr + (rva - vaddr))[0]
    return None


TYPE_OFF = (u32va(0x188198E08) ^ 0x2B849DB3) & M32
BUF = open(META, "rb").read()
T0 = BASE + TYPE_OFF

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)

recs = []
for i in range(NT):
    off = T0 + i * STEP
    d = struct.unpack_from("<23I", BUF, off)
    s = SALT[i]
    nest = ((d[8] ^ 0x21FE571D) - s) & M32
    lo16 = struct.unpack_from("<H", BUF, off + 0x46)[0]
    ncnt = ((lo16 ^ 0x7883) - (s & 0xFFFF)) & 0xFFFF
    recs.append({"i": i, "ns": None, "name": None,
                 "start": nest if nest != M32 else -1, "cnt": ncnt})

# 读数组
arr = list(struct.unpack_from("<%dI" % NEED, BUF, ARR))
print("数组前 12 个元素：%s" % arr[:12])
print("数组值域 [%d, %d]  唯一值 %d" % (min(arr), max(arr), len(set(arr))))

# 名字：用 v5 表
rows = [l.rstrip("\n").split("\t") for l in open(TYPES, encoding="utf-8")][1:]
NS = {}
NM = {}
for r in rows:
    if len(r) >= 10:
        NS[int(r[0])] = r[1]
        NM[int(r[0])] = r[2]

bad_ns = [x for x in arr if NS.get(x, "?") != ""]
print("数组中 namespace 非空的元素：%d" % len(bad_ns))
if bad_ns[:5]:
    print("  样本：%s" % [(x, NS.get(x), NM.get(x)) for x in bad_ns[:5]])

# 父段铺满检查
acc = 0
mismatch = 0
for r in sorted([r for r in recs if r["cnt"] > 0], key=lambda x: x["start"]):
    if r["start"] != acc:
        mismatch += 1
    acc += r["cnt"]
print("父段与累加不符：%d   末值 %d" % (mismatch, acc))

# 生成父子表
out = ["childIdx\tparentIdx\tchildName\tparentName\tns"]
n = 0
dup = 0
seen = set()
for r in recs:
    if r["cnt"] <= 0:
        continue
    for k in range(r["start"], min(r["start"] + r["cnt"], NEED)):
        c = arr[k]
        if c in seen:
            dup += 1
        seen.add(c)
        out.append("%d\t%d\t%s\t%s\t%s"
                   % (c, r["i"], NM.get(c, "?"), NM.get(r["i"], "?"), NS.get(r["i"], "")))
        n += 1
print("写出 %d 条父子关系，重复子类型 %d 个" % (n, dup))

# 互补检查：空 namespace 但不在数组里的
empt = set(int(r[0]) for r in rows if len(r) >= 10 and r[1] == "")
left = empt - seen
print("空 namespace 类型 %d，被数组覆盖 %d，剩余 %d（应为真正的顶层无命名空间类）"
      % (len(empt), len(seen & empt), len(left)))
print("  剩余样本：%s" % [(x, NM.get(x)) for x in list(left)[:12]])

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("[+] %s" % OUT)

# 抽查
print("\n[*] 抽查几个已知嵌套")
for want in ("System.Array", "Mono.RuntimeStructs", "System.Collections.Generic.List`1"):
    hit = [r for r in recs if NM.get(r["i"]) == want.split(".")[-1] and NS.get(r["i"], "") == want.rpartition(".")[0]]
    if not hit:
        hit = [r for r in recs if NM.get(r["i"]) == want.split(".")[-1]]
    if not hit:
        print("  %-40s 未找到" % want)
        continue
    r = hit[0]
    kids = [NM.get(arr[k], "?") for k in range(r["start"], min(r["start"] + r["cnt"], NEED))]
    print("  %-40s nested=%d  %s" % (want, r["cnt"], kids[:8]))
