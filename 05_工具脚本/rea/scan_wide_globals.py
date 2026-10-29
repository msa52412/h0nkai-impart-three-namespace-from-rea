# -*- coding: utf-8 -*-
"""扩大全局簇扫描：0x188198C00..0x188199800（E00 簇之外）找未被归属的全局引用
   目标：找到指向加密带(段偏移 0x1C68B6C±)的全局"""
import struct
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")
from probe_thunk import PE
import capstone
from capstone.x86 import X86_OP_MEM, X86_REG_RIP

pe = PE(r"D:\Carol-start\_rea\UserAssembly_slim.dll")
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True

# 1) 先列出数据段里 0x188198C00..0x188199800 的所有 raw，找能解出 0x1C68B6C 附近的
cands = []
for g in range(0x188198C00, 0x188199800, 4):
    o = pe.va2off(g)
    if o is None:
        continue
    raw = struct.unpack_from("<I", pe.d, o)[0]
    cands.append((g, raw))
print("全局区 raw 数: %d" % len(cands))

# 2) 扫 .text 元数据区引用这些全局的指令（0x3E0000..0x560000 已扫过 E00 簇，
#    现在扫全部并只统计新簇）
LO, HI = 0x188198C00, 0x188199800
refs = {}
for base_rva in range(0x3E0000, 0x560000, 0x8000):
    code = pe.bytes_at(pe.base + base_rva, 0x8000)
    if not code:
        continue
    for ins in md.disasm(code, pe.base + base_rva):
        for op in ins.operands:
            if op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP:
                t = ins.address + ins.size + op.mem.disp
                if LO <= t < HI:
                    refs.setdefault(t, []).append(ins.address)
print("被引用全局 %d 个（新簇范围）:" % len(refs))
for g in sorted(refs)[:40]:
    o = pe.va2off(g)
    raw = struct.unpack_from("<I", pe.d, o)[0]
    print("  0x%X raw=0x%08X  引用 %d 处 %s" % (g, raw, len(refs[g]), [hex(a) for a in refs[g][:2]]))
