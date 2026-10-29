#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xrefscan.py — 按 .pdata 函数体逐个反汇编，找「引用了指定全局 VA」的指令

为什么不用线性扫描
------------------
.text 有 5.4 MB，中间夹着数据/填充/伪代码区，从头线性反汇编会失步，
找出来的 xref 一半是假的。按 .pdata 的 (Begin, End) 逐函数反汇编则天然对齐。

为什么要找 xref
--------------
表2 / 表4 目前只有「条数」没有「文件偏移」：
    表2  count = (DAT_188198E78 - 0x0A4FFD99) / 0x28 = 132,220
    表4  count =  DAT_1881A35EC ^ 0x7CC59670        = 213,854
已经解出的表都是「一个全局给条数、另一个全局给段偏移」的成对结构，
所以只要找到读这两个全局的指令，它前后几条指令里就一定有对应的偏移全局。

用法：
    python xrefscan.py 0x188198E78 0x1881A35EC --sec text
    python xrefscan.py 0x188198E78 --sec all --ctx 12
"""
import collections
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_pylibs"))
from capstone import Cs, CS_ARCH_X86, CS_MODE_64  # noqa: E402
from capstone.x86 import X86_OP_IMM, X86_OP_MEM  # noqa: E402

DLL = r"Z:\AI\7.0\BH3_Data\Native\UserAssembly.dll"
PDATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bh3_pdata_truth.tsv")

SECTIONS = {
    "text":  {"rva": 0x001000,  "span": 0x52C800,  "raw": 0x000400},
    "il2cpp": {"rva": 0x052E000, "span": 0x6727C00, "raw": 0x52CC00},
}
BASE = 0x180000000


def main():
    targets = set()
    secs = ["text"]
    ctx = 10
    i = 1
    while i < len(sys.argv):
        a = sys.argv[i]
        if a == "--sec":
            secs = [sys.argv[i + 1]] if sys.argv[i + 1] != "all" else ["text", "il2cpp"]
            i += 2
        elif a == "--ctx":
            ctx = int(sys.argv[i + 1])
            i += 2
        else:
            targets.add(int(a, 16))
            i += 1
    print("目标全局 %d 个: %s" % (len(targets), ", ".join("0x%X" % t for t in sorted(targets))))

    data = open(DLL, "rb").read()

    # 只取落在所请求节里的函数
    lo = min(BASE + SECTIONS[s]["rva"] for s in secs)
    hi = max(BASE + SECTIONS[s]["rva"] + SECTIONS[s]["span"] for s in secs)
    funcs = []
    with open(PDATA, encoding="utf-8") as f:
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 2:
                continue
            b, e = int(p[0], 16), int(p[1], 16)
            if lo <= b < hi and 0 < e - b <= 0x20000:
                funcs.append((b, e))
    funcs.sort()
    print("待扫函数 %d 个（节 %s）" % (len(funcs), ",".join(secs)))

    def r2o(va):
        rva = va - BASE
        for s in secs:
            d = SECTIONS[s]
            if d["rva"] <= rva < d["rva"] + d["span"]:
                return d["raw"] + (rva - d["rva"])
        return None

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True

    hits = collections.defaultdict(list)
    n_ins = 0
    for b, e in funcs:
        off = r2o(b)
        if off is None:
            continue
        blob = data[off:off + (e - b)]
        for ins in md.disasm(blob, b):
            n_ins += 1
            for op in ins.operands:
                if op.type == X86_OP_MEM and op.mem.base == 0x29:      # RIP
                    t = ins.address + ins.size + op.mem.disp
                    if t in targets:
                        hits[t].append((ins.address, ins.mnemonic + " " + ins.op_str, b))
                elif op.type == X86_OP_IMM and op.imm in targets:
                    hits[op.imm].append((ins.address, ins.mnemonic + " " + ins.op_str, b))
    print("反汇编 %d 条指令\n" % n_ins)

    for t in sorted(targets):
        hl = hits.get(t, [])
        print("=" * 78)
        print("全局 0x%X  被引用 %d 处" % (t, len(hl)))
        seen_func = collections.Counter(f for _, _, f in hl)
        print("  涉及 %d 个函数" % len(seen_func))
        for fn, c in seen_func.most_common(8):
            print("    0x%-11X %d 处" % (fn, c))
        for va, txt, fn in hl[:40]:
            print("  0x%-11X  %-44s  [in 0x%X]" % (va, txt, fn))

        # 上下文：重新解码该函数，围绕引用点打印
        if hl:
            print("\n  --- 上下文 ---")
            for va, txt, fn in hl[:8]:
                off = r2o(fn)
                if off is None:
                    continue
                body = data[off:off + 0x4000]
                seq = []
                for ins in md.disasm(body, fn):
                    seq.append(ins)
                    if ins.address > va + 32:
                        break
                idx = next((k for k, x in enumerate(seq) if x.address == va), None)
                if idx is None:
                    continue
                print("  ┌ 0x%X  %s   [in 0x%X]" % (va, txt, fn))
                for k in range(max(0, idx - ctx), min(len(seq), idx + ctx + 1)):
                    x = seq[k]
                    mark = "  <<<" if x.address == va else ""
                    print("  │ %08X  %-24s %s %s%s"
                          % (x.address, x.bytes.hex(" "), x.mnemonic, x.op_str, mark))
                print("  └")


if __name__ == "__main__":
    main()
