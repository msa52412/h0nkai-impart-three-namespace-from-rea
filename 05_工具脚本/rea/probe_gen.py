#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探针：Il2CTYPE 表中 type==0x15 (GENERICINST) 条目的真实布局
  - 打印 20 字节原始 hex
  - 检验 *(u64)entry 是否落在镜像 VA 区间（即是否为指针）
  - 若为指针，看目标结构前 32 字节（应为 Il2CppGenericClass: +0 u32 typedefIdx, +8 generic context）
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
BASE = 0x118
TBL_VA = 0x186D41F80
NT = 57487

d = open(DLL, "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", d, opt + 24)[0]
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    name = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((name, va, vs, rs, rp))
    print("SEC %-10s va=0x%08X vs=0x%08X rp=0x%08X rs=0x%08X" % (name, va, vs, rp, rs))


def va2off(va):
    rva = va - IB
    for name, vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


tbl_off = va2off(TBL_VA)
print("\n指针表 off=0x%X" % tbl_off)

# 收集 type 分布
from collections import Counter
cnt = Counter()
gens = []
for idx in range(NT):
    p = struct.unpack_from("<Q", d, tbl_off + idx * 8)[0]
    po = va2off(p)
    if po is None:
        continue
    ty = d[po + 10]
    cnt[ty] += 1
    if ty == 0x15 and len(gens) < 20:
        gens.append((idx, p, po))

print("\ntype 分布:", {hex(k): v for k, v in sorted(cnt.items(), key=lambda x: -x[1])})

print("\n=== 前 20 个 0x15 条目 ===")
for idx, p, po in gens:
    raw = d[po:po + 24]
    u64 = struct.unpack_from("<Q", raw, 0)[0]
    tgt = va2off(u64)
    print("typedef[%6d] entryVA=0x%X  %s" % (idx, p, raw.hex(" ")))
    print("      *(u64)=0x%X  inImage=%s" % (u64, tgt is not None))
    if tgt is not None:
        g = d[tgt:tgt + 32]
        f0 = struct.unpack_from("<I", g, 0)[0]
        f4 = struct.unpack_from("<I", g, 4)[0]
        p8 = struct.unpack_from("<Q", g, 8)[0]
        p16 = struct.unpack_from("<Q", g, 16)[0]
        p24 = struct.unpack_from("<Q", g, 24)[0]
        print("      GC: +0=0x%X(%d) +4=0x%X +8=0x%X +16=0x%X +24=0x%X"
              % (f0, f0, f4, p8, p16, p24))
