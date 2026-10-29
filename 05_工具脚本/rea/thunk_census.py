#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""thunk_census.py — 全量普查「落在 .pdata 空档」的 70,432 个方法地址到底是什么

判据（il2cpp 区正确映射 raw = rva - 0x1400）：
  从地址线性解码，记录指令序列、终止指令、终止后是否 int3 填充、jmp 目标
  分类：
    T1 纯 jmp(/jmp [rip+x])            —— 纯跳板
    T2 add/sub rcx|rdx,imm + jmp       —— 调整 this 后尾跳
    T3 mov/lea 写 [rcx+K] + jmp        —— 字段初始化后尾跳
    T4 其他以 jmp 结尾且长度<=24
    NF 非跳板（长度>24 或非 jmp 结尾） —— 真函数但缺 unwind
"""
import struct, collections
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
BEG = set()
RANGES = []
for k in range(prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + 12 * k)
    if b:
        BEG.add(b)
        RANGES.append((b, en))
RANGES.sort()
RB = [r[0] for r in RANGES]
import bisect


def in_body(rva):
    j = bisect.bisect_right(RB, rva) - 1
    return j >= 0 and RANGES[j][0] <= rva < RANGES[j][1]


holes = []
for ln in open(r"D:\Carol-start\_rea\bh3_method_addr.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4 or p[0] == "idx" or not p[3]:
        continue
    r = int(p[3], 16)
    if r not in BEG:
        holes.append(r)
holes = sorted(set(holes))
print("空档去重地址 %d 个" % len(holes))

md = Cs(CS_ARCH_X86, CS_MODE_64)
cls = collections.Counter()
seqs = collections.Counter()
targets = collections.Counter()
lens = collections.Counter()
pad_ok = 0
nofit = 0

for r in holes:
    raw = rva2raw(r)
    blob = d[raw:raw + 40]
    ins_list = []
    for ins in md.disasm(blob, r):
        ins_list.append((ins.mnemonic, ins.op_str, ins.size, ins.address))
        if len(ins_list) >= 8:
            break
    if not ins_list:
        cls["DECODE-FAIL"] += 1
        continue
    last = ins_list[-1]
    total = last[3] + last[2] - r
    lens[total] += 1
    # 终止后是否填充
    tail = d[raw + total:raw + total + 6]
    if tail and all(x == 0xCC for x in tail):
        pad_ok += 1
    sig = " ; ".join("%s %s" % (m, o) for m, o, s, a in ins_list[:4])
    seqs[sig] += 1

    if last[0] in ("jmp", "ljmp"):
        if last[1].startswith("0x"):
            targets[int(last[1], 16)] += 1
        body = ins_list[:-1]
        if not body:
            cls["T1 纯jmp"] += 1
        elif len(body) == 1 and body[0][0] in ("add", "sub") and ("rcx" in body[0][1] or "rdx" in body[0][1]):
            cls["T2 调整this+jmp"] += 1
        elif total <= 32 and (body[0][0] in ("mov", "lea", "xor") or body[0][0].startswith("mov")):
            cls["T3 初始化字段+jmp"] += 1
        elif total <= 32:
            cls["T4 其他短jmp"] += 1
        else:
            cls["T5 长体+jmp(>32)"] += 1
    else:
        cls["NF 非jmp结尾"] += 1

print()
print("=== 分类 ===")
tot = len(holes)
for k, v in sorted(cls.items(), key=lambda kv: -kv[1]):
    print("  %-22s %7d  (%5.2f%%)" % (k, v, 100.0 * v / tot))

print()
print("=== 跳板长度分布 top12 ===")
for k, v in lens.most_common(12):
    print("  %3d 字节 : %6d" % (k, v))
print("终止后 6 字节全为 CC(int3) 的：%d (%.1f%%)" % (pad_ok, 100.0 * pad_ok / tot))

print()
print("=== jmp 目标 top15（共 %d 个不同目标）===" % len(targets))
for k, v in targets.most_common(15):
    print("  %X  <- %6d" % (k, v))

print()
print("=== 指令序列 top20 ===")
for k, v in seqs.most_common(20):
    print("  %6d  %s" % (v, k))
