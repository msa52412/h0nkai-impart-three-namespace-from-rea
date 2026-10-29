# -*- coding: utf-8 -*-
"""定位 UnityPlayer.dll 中对 UserAssembly.dll 的 WinVerifyTrust 调用点"""
import sys, struct
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

P = r"D:\BH3\7.0\UnityPlayer.dll"

pe = pefile.PE(P, fast_load=False)
imagebase = pe.OPTIONAL_HEADER.ImageBase
print("ImageBase = %#x" % imagebase)

# --- 找 WinVerifyTrust 及其它 wintrust 导入 ---
targets = {}
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    dll = entry.dll.decode("ascii", "replace").lower()
    for imp in entry.imports:
        if imp.name:
            n = imp.name.decode("ascii", "replace")
            if n in ("WinVerifyTrust", "WinVerifyTrustEx", "CryptQueryObject"):
                targets[n] = imp.address
                print("  %-22s %-20s IAT VA=%#x" % (dll, n, imp.address))

if not targets:
    print("未找到目标导入")
    sys.exit(1)

# --- 反汇编 .text，找引用这些 IAT 的指令 ---
text = None
for s in pe.sections:
    if b".text" in s.Name:
        text = s
        break
print("\n.text: VA=%#x size=%#x raw=%#x" % (
    imagebase + text.VirtualAddress, text.Misc_VirtualSize, text.PointerToRawData))
code = text.get_data()

md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = True

hits = []
for insn in md.disasm(code, imagebase + text.VirtualAddress):
    for op in insn.operands:
        if op.type == 3 and op.mem.base == 41:  # X86_OP_MEM, RIP
            va = insn.address + insn.size + op.mem.disp
            if va in targets.values():
                hits.append((insn.address, insn.mnemonic, insn.op_str, va))
                break

print("\n引用次数:", len(hits))
name_of = {v: k for k, v in targets.items()}
for addr, mn, ops, va in hits:
    print("  %#x  %-8s %-32s  -> %s" % (addr, mn, ops, name_of.get(va, hex(va))))
