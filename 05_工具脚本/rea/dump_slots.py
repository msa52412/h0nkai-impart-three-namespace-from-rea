#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""以 ImageConversionModule 的 7 个方法指针为中心，dump 其所在 0x100 字节窗口，看 16 字节槽里到底是什么。"""
import struct

from capstone import Cs, CS_ARCH_X86, CS_MODE_64

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
d = open(PATH, "rb").read()


def rva2raw(rva):
    return rva - 0xC00


md = Cs(CS_ARCH_X86, CS_MODE_64)

for base, n in ((0x06B13890, 0x90), (0x01D1FF40, 0x60)):
    raw = rva2raw(base)
    blob = d[raw:raw + n]
    print("=" * 90)
    print("窗口 RVA %08X  (raw %08X)" % (base, raw))
    # 逐 16 字节分块 hex
    for off in range(0, n, 16):
        chunk = blob[off:off + 16]
        print("  +%03X  %08X  %s" % (off, base + off, " ".join("%02X" % c for c in chunk)))
    print("  ---- 从窗口起点线性反汇编 ----")
    for ins in md.disasm(blob, base):
        print("    %08X  %-20s %s %s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str))
