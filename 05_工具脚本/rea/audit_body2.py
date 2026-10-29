#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit_body2.py — 验证「Ghidra body 比 .pdata 长」是否因为函数被 CHAININFO 拆成多段

假设：`.pdata` 里一个函数的主条目 EndAddress 只覆盖第一段，
后续段由 UNW_FLAG_CHAININFO 的分片条目接力。
于是 Ghidra（靠流分析走完整个函数）的 body 会**大于**单条主条目的 (End-Begin)。

判据：若某函数的 .pdata End 恰好等于某个 CHAININFO 条目的 Begin，且该分片的 End 更远，
则「偏大」是**正确行为**，不是错误。

同时定位 body 异常巨大的函数（>16K 且远超 .pdata）。
"""
import struct
import collections

BASE = 0x180000000
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


def rva2raw(r):
    for nm, va, vs, rs, rp in SECS:
        if va <= r < va + max(vs, rs):
            return rp + (r - va)
    if 0x52E000 <= r < 0x6C56000:
        return r - 0x1400
    return None


pva, pvs, prs, prp = SEC[".pdata"]
chain_begin = {}     # CHAININFO 分片的 Begin -> End
main_end = {}        # 主条目 Begin -> End
for k in range(prs // 12):
    b, en, ui = struct.unpack_from("<III", d, prp + 12 * k)
    if not b:
        continue
    ur = rva2raw(ui)
    fl = ((d[ur] >> 3) & 0x1F) if (ur is not None and ur < len(d)) else 0
    if fl & 4:
        chain_begin[BASE + b] = BASE + en
    elif b % 16 == 0:
        main_end[BASE + b] = BASE + en

print("主条目 %d   CHAININFO 分片 %d" % (len(main_end), len(chain_begin)))

gh = {}
for ln in open(r"D:\Carol-start\_rea\bh3_ghidra_funcs.txt", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) < 4:
        continue
    gh[int(p[0], 16)] = int(p[1])

bigger = []       # Ghidra body > .pdata 长度
for a, end in main_end.items():
    if a not in gh:
        continue
    pl = end - a
    gl = gh[a]
    if gl > pl:
        bigger.append((a, pl, gl, end))

print("Ghidra body 比 .pdata 长的：%d 个" % len(bigger))

# 判据一：End 恰好是某个 CHAININFO 分片的 Begin
hit1 = sum(1 for a, pl, gl, end in bigger if end in chain_begin)
# 判据二：End 处是填充（0xCC/0x90）—— 说明 .pdata End 含对齐填充，Ghidra 多吃到下一个函数
hit2 = 0
hit_none = []
for a, pl, gl, end in bigger:
    if end in chain_begin:
        continue
    raw = rva2raw(end - BASE)
    if raw is None:
        continue
    seg = d[raw:raw + 4]
    if seg and all(x in (0xCC, 0x90) for x in seg):
        hit2 += 1
    else:
        hit_none.append((a, pl, gl, end))

print("  其中 .pdata End 恰好是 CHAININFO 分片起点 : %d" % hit1)
print("  其中 .pdata End 之后紧跟填充(CC/90)      : %d" % hit2)
print("  两者都不符合                            : %d" % len(hit_none))

print("\n=== 异常巨大的 Ghidra body（>16K 且远超 .pdata） ===")
all_big = [(a, gh[a], main_end.get(a, 0) - a if a in main_end else -1)
           for a in gh if gh[a] > 16384]
all_big.sort(key=lambda r: -r[1])
for a, gl, pl in all_big[:15]:
    tag = "主条目" if pl > 0 else "非主条目"
    print("  %-12x body=%-7d .pdata长度=%-7d [%s]" % (a, gl, pl, tag))

print("\n=== 两者都不符合的前 12 个（真正需要复查的） ===")
for a, pl, gl, end in sorted(hit_none, key=lambda r: -(r[2] - r[1]))[:12]:
    raw = rva2raw(end - BASE)
    seg = d[raw:raw + 8].hex() if raw else "-"
    print("  %-12x .pdata=%-7d Ghidra=%-7d  End=%x  End处字节=%s" %
          (a, pl, gl, end, seg))
