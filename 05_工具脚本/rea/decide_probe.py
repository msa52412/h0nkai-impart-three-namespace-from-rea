#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""判决性检验：把「精确命中 .pdata 起点」的地址（对照组）与「落在空档」的地址（实验组）
   放在同一套判据下比较，看实验组是否也具备"函数入口"的形态。

判据：
  A. 从地址起能否解出至少一条合法指令
  B. 解到第一条终止指令（ret / jmp / 无条件 call+int3 之外）所需字节数是否合理(<4096)
  C. 终止指令之前是否出现过非法/无法解码字节
  D. 解出的指令流是否"自洽"：不出现 16 字节内连续 >2 条 int3
"""
import bisect
import random
import struct

from capstone import Cs, CS_ARCH_X86, CS_MODE_64

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

pva, pvs, prs, prp = SEC[".pdata"]
BEG = set()
RANGES = []
for k in range(0, prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + k * 12)
    if b:
        BEG.add(b)
        RANGES.append((b, en))
RANGES.sort()
RB = [r[0] for r in RANGES]


def in_body(rva):
    j = bisect.bisect_right(RB, rva) - 1
    return j >= 0 and RANGES[j][0] <= rva < RANGES[j][1]


hits = []
holes = []
for ln in open(r"D:\Carol-start\_rea\bh3_method_addr.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4 or p[0] == "idx" or not p[3]:
        continue
    rva = int(p[3], 16)
    if rva in BEG:
        hits.append(rva)
    elif not in_body(rva):
        holes.append(rva)

print("样本池：命中 %d，空档 %d" % (len(hits), len(holes)))
random.seed(20261023)
SH = random.sample(hits, 4000)
SL = random.sample(holes, 4000)

md = Cs(CS_ARCH_X86, CS_MODE_64)
TERM = ("ret", "jmp", "ljmp", "iret", "iretq", "sysret")


def probe(rva, limit=4096):
    raw = rva - 0xC00
    blob = d[raw:raw + limit]
    n = 0
    for ins in md.disasm(blob, rva):
        n += 1
        if ins.mnemonic in TERM:
            return n, ins.address + ins.size - rva
        if n > 600:
            return n, -1
    return n, -2          # 没遇到终止指令（含解码失败中断）


def stat(name, sample):
    ok1 = ok2 = 0
    lens = []
    fail = 0
    for rva in sample:
        n, ln = probe(rva)
        if n == 0:
            fail += 1
            continue
        ok1 += 1
        if ln > 0:
            ok2 += 1
            lens.append(ln)
    lens.sort()
    med = lens[len(lens) // 2] if lens else 0
    print("  %-10s 能解码首条指令 %5.1f%%   能解到终止指令 %5.1f%%   终止前字节数中位数 %4d  (解码失败 %d)"
          % (name, 100.0 * ok1 / len(sample), 100.0 * ok2 / len(sample), med, fail))


print()
print("判据：从地址起线性解码")
stat("命中组", SH)
stat("空档组", SL)

# 附加：第一条指令的形态统计（是否典型 prologue）
PAT = {
    "mov [rsp+x],rcx/rdx": lambda b: b[:1] == b"\x48" and b[1:2] == b"\x89" and b[2:3] in (b"\x4c", b"\x54"),
    "push rbp/rdi/rsi/rbx": lambda b: b[:1] in (b"\x55", b"\x57", b"\x56", b"\x53"),
    "sub rsp,imm": lambda b: b[:2] in (b"\x48\x83", b"\x48\x81") and (b[2] & 0x38) == 0x28,
    "mov rax,rsp": lambda b: b[:3] == b"\x48\x8b\xc4",
    "xor eax,eax": lambda b: b[:2] == b"\x33\xc0",
}


def patstat(name, sample):
    c = {k: 0 for k in PAT}
    for rva in sample[:2000]:
        b = d[rva - 0xC00:rva - 0xC00 + 4]
        for k, f in PAT.items():
            try:
                if f(b):
                    c[k] += 1
            except IndexError:
                pass
    tot = min(2000, len(sample))
    print("  %s:" % name)
    for k, v in c.items():
        print("     %-24s %5.1f%%" % (k, 100.0 * v / tot))


print()
print("首指令形态对比")
patstat("命中组", SH)
patstat("空档组", SL)
