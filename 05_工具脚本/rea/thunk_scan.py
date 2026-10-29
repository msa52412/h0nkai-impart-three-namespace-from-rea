#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""thunk_scan.py — 对全部小体积函数做「编译器桩」分类（读原始 dll，可覆盖 il2cpp 节）

背景
----
调用图入度 Top1 是 `FUN_1804fe400`（body=10 字节，被调用 946,440 次、297,273 个不同调用者）。
看字节就知道不是业务代码：

    1804FE3C0  e9 9b 73 f4 ff              jmp  rel32            <- 尾跳桩
    1804FE3D0  48 83 ec 28  e8 47 9f f4 ff  sub rsp,0x28; call    <- 抛异常桩（无 ret，noreturn）
    1804FE400  48 83 ec 28  e8 67 a5 f4 ff  sub rsp,0x28; call
    1804FE480  e9 db f3 f2 ff              jmp  rel32

MSVC 的「冷区跳板 + 共享抛异常桩」池：热路径里只留一条 5/10 字节的 call，
真正的 throw 逻辑集中在少数几条桩上。所以这些桩的入度高得离谱，但不是「核心业务函数」。

重要：函数的 VA 分布在多个节，其中 **il2cpp 节 103 MB 是主体**
（.text 只有 5.2 MB）。slim dll 把 il2cpp 的 raw 摘掉了，
所以本脚本必须读原始 UserAssembly.dll（只读，不写）。

输出 bh3_thunks.tsv：va body kind target nbytes

kind:
  tailjmp   单条 jmp rel32             （尾调用/跳板，可穿透到 target）
  throw     以 call 结尾且无 ret        （抛异常桩，target = 被调的 noreturn 函数）
  iatjmp    jmp qword [rip+X]          （导入表跳板）
  regjmp    jmp reg / mov+jmp reg      （寄存器跳板）
  retonly   只有 ret / int3 / nop
  short     其它短函数（大概率真业务）
  decode    无法解码
"""
import collections
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pylibs"))
from capstone import Cs, CS_ARCH_X86, CS_MODE_64  # noqa: E402
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_OP_REG  # noqa: E402

DLL = r"Z:\AI\7.0\BH3_Data\Native\UserAssembly.dll"
FUNCS = r"D:\Carol-start\_rea\bh3_cg_funcs.tsv"
OUT = r"D:\Carol-start\_rea\bh3_thunks.tsv"
MAXBODY = 32
STOP = ("ret", "retn", "jmp", "int3", "hlt", "ud2")


def sections(data):
    e = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, e + 6)[0]
    optsz = struct.unpack_from("<H", data, e + 20)[0]
    base = struct.unpack_from("<Q", data, e + 24 + 24)[0]
    sec = e + 24 + optsz
    out = []
    for i in range(nsec):
        o = sec + i * 40
        nm = data[o:o + 8].rstrip(b"\0").decode(errors="replace")
        vsz, va, rsz, rptr = struct.unpack_from("<IIII", data, o + 8)
        out.append((nm, va, max(vsz, rsz), rptr, rsz))
    return base, out


def decode_seq(md, blob, va, maxbytes=48):
    """解码到第一条 ret/jmp/int3 为止（maxbytes 是解码窗口）"""
    seq = []
    got = 0
    try:
        for ins in md.disasm(blob[:maxbytes], va):
            seq.append(ins)
            got = ins.address + ins.size - va
            if ins.mnemonic.lower() in STOP or len(seq) >= 8:
                break
    except Exception:
        pass
    return seq, got


def classify(md, blob, va):
    seq, got = decode_seq(md, blob, va)
    if not seq:
        return "decode", 0, 0
    # 去掉尾部填充（int3/nop），cc 是 MSVC 的函数间填充，不属于函数体
    while len(seq) > 1 and seq[-1].mnemonic.lower() in ("int3", "nop", "hlt", "ud2"):
        seq.pop()
    i0 = seq[0]
    m0 = i0.mnemonic.lower()
    end = seq[-1]
    mend = end.mnemonic.lower()

    if m0 == "jmp" and i0.operands:
        op = i0.operands[0]
        if op.type == X86_OP_IMM:
            return "tailjmp", op.imm, got
        if op.type == X86_OP_MEM:
            if op.mem.base == 0x29:            # RIP
                return "iatjmp", i0.address + i0.size + op.mem.disp, got
            return "regjmp", 0, got
        if op.type == X86_OP_REG:
            return "regjmp", 0, got
    if all(x.mnemonic.lower() in ("ret", "retn", "int3", "nop", "hlt", "ud2", "leave")
           for x in seq):
        return "retonly", 0, got
    if mend == "call" and end.operands and end.operands[0].type == X86_OP_IMM:
        return "throw", end.operands[0].imm, got
    return "short", 0, got


def main():
    print("读取 %s （%.1f MB）..." % (os.path.basename(DLL), os.path.getsize(DLL) / 1048576.0))
    data = open(DLL, "rb").read()
    base, secs = sections(data)
    print("ImageBase=0x%X" % base)
    for nm, va, span, rptr, rsz in secs:
        print("  %-9s RVA 0x%08X  span 0x%08X  raw 0x%08X" % (nm, va, span, rptr))

    def rva2off(rva):
        for nm, va, span, rptr, rsz in secs:
            if va <= rva < va + span and rptr:
                return rptr + (rva - va), nm
        return None, None

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True

    rows = []
    cnt = collections.Counter()
    small = 0
    with open(FUNCS, encoding="utf-8") as f:
        next(f)
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 3:
                continue
            va, body = int(p[0], 16), int(p[1])
            if body <= 0 or body > MAXBODY:
                continue
            small += 1
            off, nm = rva2off(va - base)
            if off is None:
                cnt["nomap"] += 1
                continue
            kind, tgt, nb = classify(md, data[off:off + 64], va)
            cnt[kind] += 1
            rows.append((va, body, kind, tgt, nb, nm))

    print("\nbody<=%d 的函数 %d 个，已分类 %d 个" % (MAXBODY, small, len(rows)))
    for k, v in cnt.most_common():
        print("  %-9s %7d" % (k, v))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("va\tbody\tkind\ttarget\tnbytes\tsection\n")
        for va, body, kind, tgt, nb, nm in rows:
            f.write("%x\t%d\t%s\t%s\t%d\t%s\n"
                    % (va, body, kind, ("%x" % tgt) if tgt else "", nb, nm))
    print("写出 %s" % OUT)

    print("\n=== 桩聚集区（4KB 页，仅 tailjmp/throw/iatjmp/regjmp/retonly） ===")
    page = collections.Counter()
    for va, body, kind, tgt, nb, nm in rows:
        if kind in ("tailjmp", "throw", "iatjmp", "regjmp", "retonly"):
            page[va & ~0xFFF] += 1
    for pg, c in page.most_common(15):
        print("  0x%X  %4d 个桩" % (pg, c))

    print("\n=== 桩的跳转目标 Top20（按不同桩数） ===")
    tc = collections.Counter()
    for va, body, kind, tgt, nb, nm in rows:
        if kind in ("tailjmp", "throw") and tgt:
            tc[tgt] += 1
    for t, c in tc.most_common(20):
        print("  0x%X  %4d 个桩指向它" % (t, c))


if __name__ == "__main__":
    main()
