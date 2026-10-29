#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""定位并解析方法指针大数组（.data raw 0x8D08958 起）

现象：raw 0x8D08958 起是 8 字节步长的代码指针数组，值大致随序递增
（IL2CPP 按方法索引顺序发射函数体），间有重复（共享函数体）。

目标：确定条数，并用 raw 0x98B5580 处的 {token, ptr} 表（System.dll，448 条）
反查索引，验证「数组下标 == 方法索引」。
"""
import struct

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
LO = 0x180001000
HI = 0x186C56000
START = 0x8D08958

d = open(PATH, "rb").read()
mv = memoryview(d)


def is_code(off):
    v = struct.unpack_from("<Q", mv, off)[0]
    return LO <= v < HI, v


# 1. 从 START 向后统计（允许少量空洞）
ok = 0
gap = 0
maxgap = 0
off = START
end = len(d) - 8
n_zero = 0
while off < end:
    good, v = is_code(off)
    if good:
        ok += 1
        gap = 0
    else:
        if v == 0:
            n_zero += 1
        gap += 1
        maxgap = max(maxgap, gap)
        if gap >= 64:
            break
    off += 8

span = (off - START) // 8
print("[*] 自 raw %08X 起" % START)
print("    跨度 %d 条（含空洞），命中代码指针 %d 条，零值 %d 条，最大连续空洞 %d" % (span, ok, n_zero, maxgap))
print("    目标 408,458 条方法")
print("    终止于 raw %08X" % off)

# 2. 用 System.dll 的 {token,ptr} 表反查
TP = 0x98B5580
NTP = 448
print()
print("[*] System.dll 映射表 raw %08X, %d 条" % (TP, NTP))
pairs = []
for k in range(NTP):
    tok, z, ptr = struct.unpack_from("<IIQ", d, TP + k * 0x10)
    pairs.append((tok, ptr))
print("    首 %08X -> %X   末 %08X -> %X" % (pairs[0][0], pairs[0][1], pairs[-1][0], pairs[-1][1]))

# 在数组里建 ptr -> 首次出现下标
first = {}
for k in range(span):
    v = struct.unpack_from("<Q", mv, START + k * 8)[0]
    if v not in first:
        first[v] = k

hit = 0
rows = []
for tok, ptr in pairs:
    k = first.get(ptr)
    if k is not None:
        hit += 1
        rows.append((tok, ptr, k))
print("    能在数组中定位的 %d / %d" % (hit, NTP))
print()
print("    token       ptr          数组下标")
for tok, ptr, k in rows[:12]:
    print("    %08X    %X   %d" % (tok, ptr, k))

# 3. 看下标与 token row 的关系
print()
print("    token_row - 下标 的差值分布（前 12 条）")
for tok, ptr, k in rows[:12]:
    print("    %08X  row=%d  idx=%d  diff=%d" % (tok, tok & 0xFFFFFF, k, (tok & 0xFFFFFF) - k))
