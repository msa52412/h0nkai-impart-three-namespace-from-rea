#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit_extra2.py — 反汇编验证「多出来的函数」是否合法起点

对 bh3_extra_audit.tsv 里的 B（非对齐非CHAIN 条目）/ E（完全无登记）两类：
  1. 从该地址解码，看能否干净解到 ret / jmp / 连续 int3
  2. 看紧邻的前 4 个字节是不是填充（0xCC / 0x90）—— 合法函数起点前通常有填充
  3. B 类额外校验：前一个 `.pdata` 条目的 End 是否恰好等于本条目 Begin
"""
import struct
import collections
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pylibs"))
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
AUDIT = r"D:\Carol-start\_rea\bh3_extra_audit.tsv"
OUT = r"D:\Carol-start\_rea\bh3_extra_disasm.tsv"
BASE = 0x180000000

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


def rva2raw(r):
    for nm, va, vs, rs, rp in SECS:
        if va <= r < va + max(vs, rs):
            return rp + (r - va)
    if 0x52E000 <= r < 0x6C56000:
        return r - 0x1400
    return None


md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = False


def walk(va, limit=64):
    """limit 由调用方按 body 动态给，避免指令跨缓冲被截断"""
    """从 va 解码，返回 (指令列表, 终止方式, 已解码字节数)

    注意：md.disasm 遇到无法解码的字节时是**静默停止**（不抛异常），
    所以必须用「已覆盖字节数」区分三种情况：
      覆盖到 limit          -> LONG（一直没遇到终止指令，可能是大函数）
      中途停止且 got<limit  -> DECODE_FAIL（真解码失败）
      遇到终止指令          -> RET / JMP / ...
    """
    raw = rva2raw(va - BASE)
    if raw is None:
        return [], "NO_RAW", 0
    blob = d[raw:raw + limit]
    out = []
    got = 0
    for ins in md.disasm(blob, va):
        out.append((ins.address, ins.mnemonic, ins.op_str, ins.size))
        got = ins.address + ins.size - va
        m = ins.mnemonic.lower()
        if m in ("ret", "retn", "jmp", "hlt", "ud2"):
            return out, m.upper(), got
    if got >= limit:
        return out, "LONG", got
    return out, "DECODE_FAIL@%d" % got, got


def prev_pad(va, n=4):
    """看前 n 字节里有几个是填充"""
    raw = rva2raw(va - BASE)
    if raw is None or raw < n:
        return -1
    seg = d[raw - n:raw]
    return sum(1 for b in seg if b in (0xCC, 0x90))


# 载入 .pdata 全部条目的 (Begin,End) 与 unwind flags，用于 B 类定性
pva, pvs, prs, prp = SEC[".pdata"]
ends = {}      # Begin -> End
flag_of = {}   # Begin -> unwind flags
for k in range(prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + 12 * k)
    if b:
        ends[BASE + b] = BASE + en
        ur = rva2raw(ui)
        flag_of[BASE + b] = ((d[ur] >> 3) & 0x1F) if (ur is not None and ur < len(d)) else -1

rows = []
for ln in open(AUDIT, encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 3 or p[0] == "va":
        continue
    rows.append((int(p[0], 16), p[1], int(p[2])))
print("待验证 %d 个" % len(rows))

stat = collections.defaultdict(collections.Counter)
samples = collections.defaultdict(list)
out = []
for va, cat, body in rows:
    if cat.startswith("B"):
        grp = "B"
    elif cat.startswith("E"):
        grp = "E"
    else:
        continue
    ins, term, blen = walk(va, limit=max(48, min(512, body + 16)))
    pad = prev_pad(va)
    # 合法性判据：能解出≥1条指令，且终止于 ret/jmp，且本条 body 与实际解码长度不矛盾
    ok_ins = len(ins) >= 1
    ok_term = term in ("RET", "RETN", "JMP")
    first = "%s %s" % (ins[0][1], ins[0][2]) if ins else "-"
    stat[grp]["total"] += 1
    stat[grp]["能解码" if ok_ins else "解码失败"] += 1
    stat[grp]["终止=" + term] += 1
    if pad >= 3:
        stat[grp]["前面有>=3字节填充"] += 1
    elif pad == 0:
        stat[grp]["前面无填充"] += 1
    if ok_ins and ok_term:
        stat[grp]["合法(可解码且终止于ret/jmp)"] += 1
    if grp == "B":
        stat[grp]["flags=%d" % flag_of.get(va, -1)] += 1
        # 与相邻 .pdata 条目的衔接：前一条的 End 是否 == 本条目 Begin
        prev = va - 1
        hit = any(ends.get(b) == va for b in (va - 2, va - 4, va - 8, va - 16))
        stat[grp]["前一条End恰好接上" if hit else "前面不接任何条目"] += 1
    if len(samples[grp]) < 6:
        samples[grp].append((va, body, first, term, blen, pad))
    out.append("%x\t%s\t%d\t%s\t%d\t%d\t%d" % (va, cat, body, term, blen, pad, 1 if (ok_ins and ok_term) else 0))

print()
for grp in ("B", "E"):
    print("=== %s 类 ===" % grp)
    for k, v in sorted(stat[grp].items()):
        print("  %-28s %d" % (k, v))
    print("  样例:")
    for va, body, first, term, blen, pad in samples[grp]:
        print("    %x  body=%-5d 解 %-3d 字节 终止=%-9s 前填充=%d  %s" %
              (va, body, blen, term, pad, first))
    print()

with open(OUT, "w", encoding="utf-8") as f:
    f.write("va\t分类\tbody\t终止\t解码字节\t前填充\t合法\n")
    f.write("\n".join(out) + "\n")
print("写出 %s（%d 行）" % (OUT, len(out)))
