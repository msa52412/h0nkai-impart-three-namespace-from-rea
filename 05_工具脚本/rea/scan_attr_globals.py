# -*- coding: utf-8 -*-
"""全 .text 扫 0x188198E00..0x188198F00 全局簇的引用点，按全局分组统计
   找出 attribute 相关读取器（引用未归属全局的函数）"""
import struct
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")
from probe_thunk import PE
import capstone
from capstone.x86 import X86_OP_MEM, X86_REG_RIP

pe = PE(r"D:\Carol-start\_rea\UserAssembly_slim.dll")
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True

# 全局簇范围
LO, HI = 0x188198E00, 0x188198F00
refs = {}   # global -> [insn addr]

text_rva = 0x1000
text_size = 0x52C7E6
CH = 0x8000
for base_rva in range(text_rva, text_rva + text_size, CH):
    code = pe.bytes_at(pe.base + base_rva, CH)
    if not code:
        continue
    for ins in md.disasm(code, pe.base + base_rva):
        for op in ins.operands:
            if op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP:
                t = ins.address + ins.size + op.mem.disp
                if LO <= t < HI:
                    refs.setdefault(t, []).append(ins.address)

print("被引用的全局 %d 个:" % len(refs))
for g in sorted(refs):
    # 已归属的标记
    known = {0x188198E08: "TYPE", 0x188198E04: "ASM", 0x188198E24: "EVENT", 0x188198E28: "PROP",
             0x188198E30: "PARAM", 0x188198E40: "GENPAR", 0x188198E50: "STRPOOL", 0x188198E58: "METHOD",
             0x188198E60: "T7", 0x188198E70: "T8", 0x188198E84: "FIELD", 0x188198E00: "GENCONT",
             0x188198E90: "blob描述表", 0x188198E64: "pairs", 0x188198E5C: "blob数据区",
             0x188198E10: "ifaceOffsets", 0x188198E74: "ifaceOffsets2", 0x188198E3C: "iface索引",
             0x188198E1C: "T5", 0x188198E14: "方法规格缓存", 0x188198E54: "槽初值表",
             0x188198E6C: "?", 0x188198E38: "?", 0x188198E2C: "?", 0x188198E34: "?",
             0x188198E44: "?", 0x188198E48: "?", 0x188198E7C: "?", 0x188198E88: "metadataUsage?",
             0x188198E4C: "?", 0x188198E18: "?", 0x188198E0C: "?", 0x188198E68: "?"}
    tag = known.get(g, "★未归属")
    print("  0x%X %-18s 引用 %d 处: %s" % (g, tag, len(refs[g]), [hex(a) for a in refs[g][:4]]))
