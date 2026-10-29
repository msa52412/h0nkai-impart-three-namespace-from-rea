# -*- coding: utf-8 -*-
"""扫全 .text 找引用 E90(blob 描述表全局 0x188198E90) 的指令点"""
import struct
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")
from probe_thunk import PE
import capstone
from capstone.x86 import X86_OP_MEM, X86_REG_RIP

pe = PE(r"D:\Carol-start\_rea\UserAssembly_slim.dll")
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True

targets = {0x188198E90}

# 从 PE 头解析 .text 范围（RVA 0x1000 起）
# 解析节表
e_lfanew = struct.unpack_from("<I", pe.d, 0x3C)[0]
nsec = struct.unpack_from("<H", pe.d, e_lfanew + 6)[0]
opt_size = struct.unpack_from("<H", pe.d, e_lfanew + 20)[0]
sec0 = e_lfanew + 24 + opt_size
text_rva = text_size = 0
for i in range(nsec):
    o = sec0 + i * 40
    name = pe.d[o:o + 8].rstrip(b"\0").decode("latin-1")
    vsize = struct.unpack_from("<I", pe.d, o + 8)[0]
    rva = struct.unpack_from("<I", pe.d, o + 12)[0]
    if name == ".text":
        text_rva, text_size = rva, vsize
        print(".text RVA=0x%X size=0x%X" % (rva, vsize))
# 文件偏移 <-> RVA 转换直接用 va2off（VA = 0x180000000 + RVA）

hits = []
CH = 0x8000
for base_rva in range(text_rva, text_rva + text_size, CH):
    code = pe.bytes_at(pe.base + base_rva, CH)
    if not code:
        continue
    for ins in md.disasm(code, pe.base + base_rva):
        for op in ins.operands:
            if op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP:
                if ins.address + ins.size + op.mem.disp in targets:
                    hits.append(hex(ins.address))
    if base_rva % 0x100000 == 0:
        print("  ...扫描到 RVA 0x%X" % base_rva, flush=True)
print("E90 引用点 %d 个:" % len(hits))
for h in hits:
    print("  ", h)
