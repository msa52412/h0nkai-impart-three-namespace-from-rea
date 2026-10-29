# -*- coding: utf-8 -*-
"""扫 .text 找立即数落在加密带段偏移域 [0x1C6766C, 0x1D79820] 的指令
   （带 +0x118 后为绝对地址）"""
import struct
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")
from probe_thunk import PE
import capstone
from capstone.x86 import X86_OP_IMM

pe = PE(r"D:\Carol-start\_rea\UserAssembly_slim.dll")
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True

LO, HI = 0x1C6766C, 0x1D79820   # 段偏移域
hits = []
for base_rva in range(0x3E0000, 0x560000, 0x8000):
    code = pe.bytes_at(pe.base + base_rva, 0x8000)
    if not code:
        continue
    for ins in md.disasm(code, pe.base + base_rva):
        for op in ins.operands:
            if op.type == X86_OP_IMM:
                v = op.imm & 0xFFFFFFFF
                if LO <= v <= HI:
                    hits.append((ins.address, ins.mnemonic, ins.op_str, v))
print("立即数落在加密带域的指令 %d 条:" % len(hits))
for a, m, o, v in hits[:20]:
    print("  0x%X  %s %s   (段偏移 0x%X → 绝对 0x%X)" % (a, m, o, v, v + 0x118))
