#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gap_final.py — 收束总账：真函数集合 / 方法入口集合 / 空档桩集合 的完整关系

输出：
  1. .pdata 三类条目（真函数 / CHAININFO 分片 / 空）
  2. 方法地址 → 去掉 CHAININFO 后的真实命中率
  3. 空档地址按长度与终止方式分桶（条数加权 + 地址加权）
  4. 空档桩是否是其它桩的 jmp 目标（链式）
"""
import struct, bisect, collections
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
d = open(DLL, "rb").read()

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
    for nm, va, vs, rs, rp in SECS:
        if va <= rva < va + max(vs, rs):
            return rp + (rva - va)
    return rva - 0x1400


pva, pvs, prs, prp = SEC[".pdata"]
N = prs // 12
REAL = set()      # 16 对齐 + 非 CHAININFO
CHAIN = set()
ALLB = set()
for k in range(N):
    b, en, ui = struct.unpack_from("<III", d, prp + 12 * k)
    if not b:
        continue
    ALLB.add(b)
    uraw = rva2raw(ui)
    chained = False
    if uraw is not None:
        chained = bool(((d[uraw] >> 3) & 0x1F) & 0x4)
    if b % 16 == 0 and not chained:
        REAL.add(b)
    if chained:
        CHAIN.add(b)

print("=== 1. .pdata 结构 ===")
print("  条目总数            %8d" % N)
print("  CHAININFO 分片      %8d  (%.1f%%)" % (len(CHAIN), 100.0 * len(CHAIN) / N))
print("  真函数起点(16对齐非CHAIN) %8d" % len(REAL))

# 方法表
meth = collections.Counter()   # rva -> 条数
total = 0
for ln in open(r"D:\Carol-start\_rea\bh3_method_addr.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4 or p[0] == "idx" or not p[3]:
        continue
    total += 1
    meth[int(p[3], 16)] += 1

hit = sum(c for a, c in meth.items() if a in REAL)
gap = total - hit
print()
print("=== 2. 方法 → 地址 ===")
print("  方法总数            %8d" % total)
print("  去重地址            %8d" % len(meth))
print("  精确落在真函数起点  %8d  (%.2f%%)" % (hit, 100.0 * hit / total))
print("  落在空档            %8d  (%.2f%%)" % (gap, 100.0 * gap / total))
print("  → 真函数中作为方法入口的比例: %d/%d = %.1f%%" % (hit, len(REAL), 100.0 * hit / len(REAL)))

gapaddrs = sorted(a for a in meth if a not in REAL)
print("  空档去重地址        %8d" % len(gapaddrs))

md = Cs(CS_ARCH_X86, CS_MODE_64)


def walk(r):
    raw = rva2raw(r)
    blob = d[raw:raw + 1024]
    n = 0
    for ins in md.disasm(blob, r):
        n += 1
        if ins.mnemonic in ("ret", "retf", "iret", "iretq"):
            return ins.address + ins.size - r, "ret"
        if ins.mnemonic in ("jmp", "ljmp"):
            tgt = int(ins.op_str, 16) if ins.op_str.startswith("0x") else None
            return ins.address + ins.size - r, "jmp", tgt
        if ins.mnemonic == "int3" and n > 0:
            return ins.address - r, "int3"
        if n > 300:
            return -1, "超长"
    return -1, "中断"


buckets = collections.Counter()
buckets_addr = collections.Counter()
jt = collections.Counter()
kinds = collections.Counter()
for r in gapaddrs:
    res = walk(r)
    L, k = res[0], res[1]
    if k == "jmp" and len(res) > 2 and res[2]:
        jt[res[2]] += 1
    kinds[k] += 1
    if L < 0:
        b = ">256/异常"
    elif L <= 16:
        b = "≤16"
    elif L <= 32:
        b = "17-32"
    elif L <= 64:
        b = "33-64"
    elif L <= 256:
        b = "65-256"
    else:
        b = ">256/异常"
    buckets[(b, k)] += 1
    buckets_addr[b] += meth[r]

print()
print("=== 3. 空档桩：按地址数 / 按方法条数 ===")
print("  %-10s %-6s %8s %10s" % ("长度桶", "终止", "地址数", "覆盖方法条数"))
for (b, k), v in sorted(buckets.items(), key=lambda kv: (kv[0][0], kv[0][1])):
    print("  %-10s %-6s %8d %10d" % (b, k, v, buckets_addr[(b, k)]))
print("  --- 按长度桶合计 ---")
for b in ("≤16", "17-32", "33-64", "65-256", ">256/异常"):
    n = sum(v for (bb, k), v in buckets.items() if bb == b)
    if n:
        print("  %-10s 地址 %6d   方法 %7d" % (b, n, buckets_addr[b]))

print()
print("=== 4. 空档桩之间的链式跳转 ===")
chain_into_gap = sum(v for t, v in jt.items() if t in meth and t not in REAL)
print("  空档桩 jmp 到另一个空档桩的次数: %d" % chain_into_gap)
print("  jmp 目标数 %d，其中落在真函数起点的 %d，落在空档的 %d，其它 %d"
      % (len(jt), sum(v for t, v in jt.items() if t in REAL),
         chain_into_gap, sum(v for t, v in jt.items() if t not in REAL and t not in meth)))

# 写 TSV
with open(r"D:\Carol-start\_rea\bh3_gap_stubs.tsv", "w", encoding="utf-8") as f:
    f.write("rva\tmethods\tlen\tterm\tjmp_target\n")
    for r in gapaddrs:
        res = walk(r)
        L, k = res[0], res[1]
        t = res[2] if (k == "jmp" and len(res) > 2 and res[2]) else ""
        f.write("%X\t%d\t%d\t%s\t%s\n" % (r, meth[r], L, k,
                                          ("%X" % t) if t else ""))
print()
print("已写 bh3_gap_stubs.tsv  %d 行" % len(gapaddrs))
