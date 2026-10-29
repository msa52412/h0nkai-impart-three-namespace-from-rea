#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检验 NetCommand.Partthree 的数组是否真的周期性重复（判断是否取错结构/步长）。"""
import struct

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
IB = 0x180000000
d = open(PATH, "rb").read()


def rva2raw(rva):
    return rva - 0xC00


for name, arr, cnt in (("NetCommand.Partthree.dll", 0x09904AC0, 712),
                       ("ProtobufSerializer.Partninja.dll", 0x099382E0, 59)):
    raw = rva2raw(arr)
    vals = list(struct.unpack_from("<%dQ" % min(cnt, 400), d, raw))
    print("=" * 92)
    print("%s  arr=%08X cnt=%d" % (name, arr, cnt))
    print(" 前 24 项原始内存：")
    for i in range(0, 24, 2):
        print("   [%3d] %016X  [%3d] %016X" % (i, vals[i], i + 1, vals[i + 1]))
    for per in (2, 4, 8, 16, 32, 64):
        eq = sum(1 for i in range(len(vals) - per) if vals[i] == vals[i + per])
        print("   周期 %-3d 相等比例 %.1f%%" % (per, 100.0 * eq / (len(vals) - per)))
    print(" 不同值个数 %d / %d" % (len(set(vals)), len(vals)))
