#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""thunk_census2.py — 空档地址全量普查（不截断解码）

对每个「不在 .pdata 起点」的方法地址：
  线性解码直到 ret / jmp / 连续 int3 / 无法解码 / 超过 512 字节
  记录：终止指令、终止偏移、终止后 4 字节是否 int3、jmp 目标
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
BEG = set()
RANGES = []
for k in range(prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + 12 * k)
    if b:
        BEG.add(b)
        RANGES.append((b, en))
RANGES.sort()
RB = [r[0] for r in RANGES]


def in_body(rva):
    j = bisect.bisect_right(RB, rva) - 1
    return j >= 0 and RANGES[j][0] <= rva < RANGES[j][1]


holes = set()
for ln in open(r"D:\Carol-start\_rea\bh3_method_addr.tsv", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4 or p[0] == "idx" or not p[3]:
        continue
    r = int(p[3], 16)
    if r not in BEG:
        holes.add(r)
holes = sorted(holes)
print("空档去重地址 %d 个" % len(holes))

md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = False

kind = collections.Counter()
endoff = collections.Counter()
jtgt = collections.Counter()
tmpl = collections.Counter()


def classify(r):
    raw = rva2raw(r)
    blob = d[raw:raw + 512]
    n = 0
    last = None
    prev_cc = 0
    for ins in md.disasm(blob, r):
        n += 1
        b = ins.bytes
        if last is not None and last[0] == "int3" and ins.mnemonic != "int3":
            # 连续 int3 之后又有代码 -> 说明前一 int3 就是结束
            return "int3结束", last[1], None, None
        if ins.mnemonic == "int3":
            last = ("int3", ins.address + ins.size - r, None)
        elif ins.mnemonic in ("ret", "retf", "iret", "iretq"):
            return "ret结束", ins.address + ins.size - r, None, None
        elif ins.mnemonic in ("jmp", "ljmp"):
            tgt = None
            if ins.op_str.startswith("0x"):
                tgt = int(ins.op_str, 16)
            return "jmp结束", ins.address + ins.size - r, tgt, ins.op_str
        else:
            last = (ins.mnemonic, ins.address + ins.size - r, ins.op_str)
        if n > 200:
            return "超长", -1, None, None
    return "解码中断", -1, None, None


for r in holes:
    k, off, tgt, os_ = classify(r)
    kind[k] += 1
    if off > 0:
        endoff[off] += 1
    if tgt:
        jtgt[tgt] += 1

print()
print("=== 终止方式 ===")
for k, v in kind.most_common():
    print("  %-10s %6d  (%5.2f%%)" % (k, v, 100.0 * v / len(holes)))

print()
print("=== 终止偏移（从地址算起）top15 ===")
for k, v in endoff.most_common(15):
    print("  %4d 字节 : %6d" % (k, v))

print()
print("=== jmp 目标（不同 %d 个）top12 ===" % len(jtgt))
for k, v in jtgt.most_common(12):
    print("  %X  <- %5d" % (k, v))
