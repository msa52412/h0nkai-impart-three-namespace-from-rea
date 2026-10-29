# -*- coding: utf-8 -*-
"""定位引用 Native/UserAssembly.dll 字符串的代码，并反汇编其上下文"""
import sys, struct, re
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

P = r"D:\BH3\7.0\UnityPlayer.dll"
pe = pefile.PE(P, fast_load=False)
ib = pe.OPTIONAL_HEADER.ImageBase

# 文件偏移 -> VA
def off2va(off):
    for s in pe.sections:
        if s.PointerToRawData <= off < s.PointerToRawData + s.SizeOfRawData:
            return ib + s.VirtualAddress + (off - s.PointerToRawData)
    return None

d = open(P, "rb").read()
off = d.find(b"Native/UserAssembly.dll")
sva = off2va(off)
print("字符串 Native/UserAssembly.dll  文件偏移=%#x  VA=%#x" % (off, sva))

# 在 .text 里找 lea reg,[rip+disp] 指向该串
text = None
for s in pe.sections:
    if b".text" in s.Name:
        text = s; break
tva = ib + text.VirtualAddress
code = text.get_data()

refs = []
for i in range(len(code) - 7):
    b0 = code[i]
    # 48/4C 8D xx disp32   (lea r64, [rip+disp])
    if b0 in (0x48, 0x4C) and code[i+1] == 0x8D and (code[i+2] & 0xC7) == 0x05:
        disp = struct.unpack_from("<i", code, i+3)[0]
        if tva + i + 7 + disp == sva:
            refs.append(tva + i)
    # 48/4C 8D /r32 无 rip 的情况不覆盖
print("引用该字符串的 lea 指令:", [hex(x) for x in refs])

md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = False

def dump(va, before=0x80, after=0xC0, title=""):
    print("\n--- %s %#x ---" % (title, va))
    start = va - before
    o = None
    for s in pe.sections:
        if s.VirtualAddress <= (start - ib) < s.VirtualAddress + s.Misc_VirtualSize:
            o = s.PointerToRawData + (start - ib - s.VirtualAddress)
            break
    if o is None:
        print("  无法映射"); return
    blob = d[o:o + before + after]
    for insn in md.disasm(blob, start):
        mark = "  <<<" if abs(insn.address - va) < 8 else ""
        print("  %#010x  %-8s %-40s%s" % (insn.address, insn.mnemonic, insn.op_str, mark))

for r in refs[:3]:
    dump(r, 0x60, 0x80, "字符串引用点")
