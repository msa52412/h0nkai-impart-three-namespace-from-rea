# -*- coding: utf-8 -*-
"""wmcrash —— 反汇编崩溃偏移 0x43B2D5E 所在函数，确认它是不是读 [obj+0x20]

崩溃记录（事件查看器 Application / Id 1000）：
    BH3.exe  UserAssembly.dll  c0000005  偏移量 0x00000000043b2d5e

RVA = 0x43B2D5E。已知 AAGPFOHOKJL 在 0x43B2280，
所以崩溃发生在该函数体 +0xADE 处。

本脚本纯离线读 DLL 文件，不碰游戏进程。
用法：python wmcrash.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
from capstone import Cs, CS_ARCH_X86, CS_MODE_64  # noqa: E402

FILE_BASE = 0x180000000
CRASH_RVA = 0x43B2D5E
FN_RVA = 0x43B2280
SPAN = 0xC00


def main():
    print("崩溃 RVA %#x，函数起点 %#x，相对偏移 +%#x"
          % (CRASH_RVA, FN_RVA, CRASH_RVA - FN_RVA))
    raw = icall.file_bytes(FN_RVA, SPAN)
    if not raw:
        print("读不到文件字节")
        return 1
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    hit = None
    lines = []
    for ins in md.disasm(raw, FILE_BASE + FN_RVA):
        mark = "  "
        if ins.address == FILE_BASE + CRASH_RVA:
            mark = "★ "
            hit = ins
        lines.append("%s%#x  %-20s %-8s %s"
                     % (mark, ins.address, ins.bytes.hex(),
                        ins.mnemonic, ins.op_str))
    # 只打印崩溃点前 60 行到崩溃点后 12 行
    if hit:
        idx = next(i for i, l in enumerate(lines) if l.startswith("★"))
    else:
        idx = len(lines) - 1
        print("⚠ 崩溃偏移没落在任何指令边界上（说明是跳转目标错位）")
    lo, hi = max(0, idx - 60), min(len(lines), idx + 13)
    print("\n--- 崩溃点上下文 ---")
    for l in lines[lo:hi]:
        print(l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
