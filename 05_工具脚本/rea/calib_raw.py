#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calib_raw.py — 用 .pdata 的 (Begin,End) 校准 il2cpp 区 VA→raw 的常量偏移

原理：对一个真函数起点 B，其真实长度 L = End - Begin。
      在 raw = B - delta 处线性解码，若 delta 正确，解码恰好铺满 L 字节
      （最后一条指令的末尾 == End）。对多个 delta 打分，取最优。
"""
import struct, random, collections
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
pva, pvs, prs, prp = SEC[".pdata"]


def rva2raw_rdata(rva):
    for nm, va, vs, rs, rp in SECS:
        if va <= rva < va + max(vs, rs):
            return rp + (rva - va)
    return None


# 收集「16 对齐 + 非 CHAININFO」的真函数，且长度在 32..600 之间
real = []
for k in range(prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + 12 * k)
    if not b or b % 16 or en <= b:
        continue
    ur = rva2raw_rdata(ui)
    if ur is None:
        continue
    if (d[ur] >> 3) & 0x1F & 0x4:
        continue
    L = en - b
    if 32 <= L <= 600:
        real.append((b, en))
print("候选真函数（16 对齐、非 CHAIN、长度 32..600）: %d" % len(real))

random.seed(7)
S = random.sample(real, min(3000, len(real)))
md = Cs(CS_ARCH_X86, CS_MODE_64)

score = collections.Counter()
for delta in range(0x200, 0x2401, 0x200):
    ok = 0
    for b, en in S:
        raw = b - delta
        if raw < 0:
            continue
        blob = d[raw:raw + (en - b) + 16]
        pos = 0
        good = True
        for ins in md.disasm(blob, b):
            if ins.address + ins.size > en:
                good = False
                break
            if ins.address + ins.size == en:
                pos = 1
                break
        if pos:
            ok += 1
    score[delta] = ok

print()
print("delta  精确铺满函数体的比例")
for delta, ok in sorted(score.items(), key=lambda kv: -kv[1]):
    print("  0x%04X  %5d / %d  = %5.1f%%" % (delta, ok, len(S), 100.0 * ok / len(S)))
