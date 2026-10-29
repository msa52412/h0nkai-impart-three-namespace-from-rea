#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全文件扫描：找出所有落在「真实代码区间」的 u64 指针，并统计连续游程。

背景：UserAssembly.dll 的 .text 节头声称 VSize=5,425,126（RawSize 同），
但 .text 原始数据末尾(raw 0x52E800) 与 .rdata 起始(raw 0x6C54800) 之间有
99.5 MB 的实际 x64 代码（熵 6.0~6.4，指令可读）。节头被篡改过。

.text   raw 0x00000400 -> VA 0x00001000   delta = 0xC00
.rdata  raw 0x6C54800 -> VA 0x6C56000   delta = 0x1800

故把 raw 0x400..0x6C54800 整体视为代码，VA = raw + 0xC00，
真实代码 VA 区间 = 0x180001000 .. 0x186C56000（约 108 MB）。
"""
import struct
import sys

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
LO = 0x180001000
HI = 0x186C56000
CODE_RAW_START = 0x400
CODE_RAW_END = 0x6C54800

d = open(PATH, "rb").read()
print("[*] 文件 %d 字节 (0x%X)" % (len(d), len(d)))
print("[*] 代码 VA 区间 0x%X .. 0x%X" % (LO, HI))

# 1. 逐 8 字节扫描
runs = []          # (起始 raw 偏移, 长度)
cur_start = -1
cur_len = 0
hit_total = 0
step = 8
mv = memoryview(d)
for off in range(0, len(d) - 8, step):
    v = struct.unpack_from("<Q", mv, off)[0]
    if LO <= v < HI:
        hit_total += 1
        if cur_start < 0:
            cur_start = off
            cur_len = 1
        else:
            cur_len += 1
    else:
        if cur_len >= 16:
            runs.append((cur_start, cur_len))
        cur_start = -1
        cur_len = 0
if cur_len >= 16:
    runs.append((cur_start, cur_len))

print("[*] 命中指针总数 %d" % hit_total)
print("[*] 长度 >= 16 的连续游程 %d 个" % len(runs))
runs.sort(key=lambda x: -x[1])
print()
print("== 最长 25 个游程 ==")
print("%-12s %-10s %-12s %s" % ("rawOff", "条数", "对应VA", "备注"))
tot = 0
for st, ln in runs[:25]:
    print("%08X     %-10d %08X" % (st, ln, st + 0xC00))
for st, ln in runs:
    tot += ln
print()
print("[*] 所有游程累计 %d 条" % tot)
print("[*] 目标：408,458 条方法指针")
