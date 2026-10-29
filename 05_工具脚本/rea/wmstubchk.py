# -*- coding: utf-8 -*-
"""离线校验 build_click_stub 生成的机器码（不碰游戏）"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmpick  # noqa: E402
from capstone import Cs, CS_ARCH_X86, CS_MODE_64  # noqa: E402

PAGE = 0x00000000D40000
SLOT = PAGE + 0x40
MB = PAGE
META = 0x00007000C558450
MOD = 0x00007000B604DD0
BASE = 0x00007FFEC8D70000
GOTO = BASE + 0x19C5E00
ORIG = bytes.fromhex("4055565741544155415641574883ec70")
RESUME = BASE + 0x2CFB880 + 16
STUB = PAGE + 0x6000

blob = wmpick.build_click_stub(SLOT, MB, META, MOD, GOTO, ORIG, RESUME)
print("长度 %d 字节\n" % len(blob))
md = Cs(CS_ARCH_X86, CS_MODE_64)
for ins in md.disasm(blob, STUB):
    print("  %#x  %-24s %-8s %s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str))
