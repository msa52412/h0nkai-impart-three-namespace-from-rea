# -*- coding: utf-8 -*-
"""确认 LJMINEONAFF 里 status=2 那处返回的原始字节

0x180A52398  mov eax, 2      ; b8 02 00 00 00
把立即数 2 改成 3，就让「等级介于 UnlockLevel 与 UnlockHintLevel 之间」
的入口从「未解锁」变成「已解锁」。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall

RVA = 0xA52398
N = 16

b = icall.file_bytes(RVA, N)
print("文件 @RVA %#x: %s" % (RVA, b.hex(" ")))
print("  前 5 字节 = %s  （期望 b8 02 00 00 00）" % b[:5].hex(" "))
if b[:5] == b"\xb8\x02\x00\x00\x00":
    print("  ✓ 与预期一致：mov eax, 2")
elif b[:5] == b"\xb8\x03\x00\x00\x00":
    print("  ! 已经是 mov eax, 3（改过了？）")
else:
    print("  ✗ 与预期不符，先别改")
