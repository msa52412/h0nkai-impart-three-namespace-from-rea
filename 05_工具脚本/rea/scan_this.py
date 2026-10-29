#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan_this.py —— 本地扫汇编，提取「this + 偏移」的访问集合（不依赖 Ghidra 反编译器）

动机：Ghidra 的 DecompInterface 在这份 190MB / 44 万函数的样本上会卡死（连 timeout 都不触发），
      而实例字段布局只需要「非静态方法的第 1 个参数 this 被访问了哪些偏移」，
      这完全可以靠 x64 汇编 + 寄存器传播本地算出来，速度快几个数量级且确定性强。

原理（Win64 thiscall / MS ABI）：
  入口 RCX = this
  跟踪一个「持有 this 的寄存器集合」：
    mov dst, src  且 src ∈ 集合        → dst 入集合
    其它任何写 dst                     → dst 出集合
    call 之后 rcx 被破坏                → rcx 出集合
  出现 [reg + disp] 且 reg ∈ 集合、disp ∈ [0, 0x4000]  → 记录 disp（disp=0 记 0）

输入：bh3_layout_probe2.tsv（typeIdx \t rva1[,rva2,...] \t fieldCount）
输出：bh3_layout_obs2.tsv（typeIdx \t offsets \t nAccess \t nInsn）
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pylibs"))
import capstone  # noqa: E402

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
IB = 0x180000000
# ★ il2cpp 节头被清零（§9F.10），必须硬编码 (rva, raw, span)
IL2CPP = (0x052E000, 0x52CC00, 0x6727C00)

MAXINS = 1200
MAXBYTE = 8000
DISP_MAX = 0x4000

d = open(PATH, "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
opt = coff + 20
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    nm = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((nm, va, vs, rs, rp))


def rva2off(rva):
    if IL2CPP[0] <= rva < IL2CPP[0] + IL2CPP[2]:
        return IL2CPP[1] + (rva - IL2CPP[0])
    for nm, va, vs, rs, rp in SECS:
        if va <= rva < va + max(vs, rs):
            return None if rp == 0 else rp + (rva - va)
    return None


md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True
md.skipdata = True

MOVS = {"mov", "movzx", "movsx", "movsxd", "lea", "movsxd"}
STOP = {"ret", "retn", "int3", "ud2", "hlt"}
# 无条件 jmp 后的字节不属于本函数（尾调/分支尾），继续扫会越过函数边界，
# 把下一个函数的序言访问记成本方法的观测。
# 例：proto.LotteryData::.ctor 尾部 jmp 之后是另一函数的
#   mov [rsp+8],rbx / push rdi / mov rdi,rcx / mov dword [rcx+0x14],0
#   ← 0x14 由此混入（该"下一函数"还是 1,583 类型共享的 ICF 体）
UJMP = {"jmp", "jmpq"}


def scan(rva, sret=0):
    """返回 (offsets_set, ninsn)

    sret=1：返回类型是按值返回的大结构体 → MS x64 下 rcx 是隐藏返回缓冲区指针，
            this 在 rdx。搞错这一点会把「写返回值」的偏移误当成字段访问。
    """
    off = rva2off(rva)
    if off is None or off >= len(d):
        return set(), 0
    code = d[off:off + MAXBYTE]
    this_regs = {"rdx"} if sret else {"rcx"}
    offs = set()
    n = 0
    try:
        for ins in md.disasm(code, IB + rva):
            n += 1
            if n > MAXINS:
                break
            mn = ins.mnemonic
            if mn in STOP:
                break
            if mn in UJMP:
                break
            ops = ins.operands
            if not ops:
                continue
            # --- 先记录所有「以 this 寄存器为基址」的内存操作数（读或写都算访问）---
            # ★ 宽度过滤：>8 字节的宽访问（movups xmm 等）是「跨字段快照」，
            #   disp 不是字段起点。例：WWW.Dispose 的 movups xmm0,[rcx+0x14]
            #   拷 16 字节给 trace 函数，0x14 不是任何字段的偏移。
            #   字段最大 8 字节（long/引用），只收 width<=8 的窄访问。
            for op in ops:
                if op.type == capstone.x86.X86_OP_MEM and op.mem.base != 0:
                    bn = ins.reg_name(op.mem.base)
                    if bn in this_regs:
                        dsp = op.mem.disp
                        if 0 <= dsp <= DISP_MAX and op.size <= 8:
                            offs.add(dsp)
            o0 = ops[0]
            # --- 先处理「目标被写」---
            if o0.type == capstone.x86.X86_OP_REG:
                dn = ins.reg_name(o0.reg)
                if mn in MOVS and len(ops) > 1 and ops[1].type == capstone.x86.X86_OP_REG:
                    sn = ins.reg_name(ops[1].reg)
                    if sn in this_regs:
                        this_regs.add(dn)
                    else:
                        this_regs.discard(dn)
                else:
                    this_regs.discard(dn)
            elif o0.type == capstone.x86.X86_OP_MEM:
                pass        # 已在上面统一记录
            if mn == "call" or mn == "callq":
                this_regs.discard("rcx")
                this_regs.discard("rdx")
                this_regs.discard("r8")
                this_regs.discard("r9")
                this_regs.discard("r10")
                this_regs.discard("r11")
    except capstone.CsError:
        pass
    return offs, n


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "bh3_layout_probe2.tsv"
    dst = sys.argv[2] if len(sys.argv) > 2 else "bh3_layout_obs2.tsv"
    lim = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    # ★ ICF 折叠地址黑名单：一个 RVA 被多个不同 declType 的方法指向时，
    #   该地址扫出的 [this+disp] 属于「某一个」类型，对其它类型全是污染。
    #   典型：0x640CE0（mov rax,[rcx+0x58]; ret）被 20+ 类型的 getter 共用，
    #   WWW 的观测里因此混进了 X509Certificate 的 0x58。同类型共享（重载折叠）无害。
    import csv
    from collections import defaultdict
    here = os.path.dirname(os.path.abspath(__file__))
    mv2 = {r["idx"]: r["declType"] for r in csv.DictReader(
        open(os.path.join(here, "bh3_methods_v2.tsv"), encoding="utf-8", errors="replace"),
        delimiter="\t")}
    rva_types = defaultdict(set)
    for r in csv.DictReader(
            open(os.path.join(here, "bh3_method_addr.tsv"), encoding="utf-8", errors="replace"),
            delimiter="\t"):
        if r["rva"].strip():
            rva_types[r["rva"]].add(mv2.get(r["idx"], ""))
    icf_bad = {k for k, v in rva_types.items() if len(v) > 1}
    print("ICF 跨类型折叠地址 %d 个（已排除）" % len(icf_bad))

    out = open(dst, "w", encoding="utf-8")
    out.write("typeIdx\toffsets\tnAccess\tnInsn\n")
    n = hit = skipped = 0
    import time
    t0 = time.time()
    with open(src, encoding="utf-8", errors="replace") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 2:
                continue
            ti = int(p[0])
            n += 1
            if lim and n > lim:
                break
            offs = set()
            nins = 0
            for rs in p[1].split(","):
                rs = rs.strip()
                if not rs:
                    continue
                sr = 0
                if ":" in rs:
                    rs, s2 = rs.split(":", 1)
                    try:
                        sr = int(s2)
                    except ValueError:
                        sr = 0
                if rs.upper() in icf_bad:
                    skipped += 1
                    continue
                try:
                    rva = int(rs, 16)
                except ValueError:
                    continue
                o, k = scan(rva, sr)
                offs |= o
                nins += k
            if offs:
                hit += 1
            out.write("%d\t%s\t%d\t%d\n" % (
                ti, ",".join("0x%x" % x for x in sorted(offs)), len(offs), nins))
            if n % 5000 == 0:
                out.flush()
                print("  %d  hit=%d  %.1fs" % (n, hit, time.time() - t0))
    out.close()
    print("done: %d 行，有偏移 %d (%.1f%%)  跳过 ICF rva %d 个  %.1fs"
          % (n, hit, 100.0 * hit / max(n, 1), skipped, time.time() - t0))


if __name__ == "__main__":
    main()
