#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描 {u32 token(0x06xxxxxx), u32 0, u64 代码指针} 的 16 字节记录游程。

发现点：raw 0x98B5568 处（"System.dll" 名字被引用的结构体 +0x18）是一张
按 token 升序排列的 {token, 0, ptr} 表，ptr 落在真实代码区间。

若全文件存在 408,458 条的同类游程，则方法 → 原生地址一次性闭合。
"""
import struct

PATH = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
LO = 0x180000000
HI = 0x187000000

d = open(PATH, "rb").read()
mv = memoryview(d)
n = len(d)
print("[*] 文件 %d 字节" % n)

run_start = -1
run_len = 0
runs = []
i = 0
END = n - 16
while i < END:
    tok, z, ptr = struct.unpack_from("<IIQ", mv, i)
    ok = (tok >> 24) == 0x06 and z == 0 and LO <= ptr < HI
    if ok:
        if run_start < 0:
            run_start = i
            run_len = 1
        else:
            run_len += 1
        i += 16
    else:
        if run_len >= 8:
            runs.append((run_start, run_len))
        run_start = -1
        run_len = 0
        i += 4
if run_len >= 8:
    runs.append((run_start, run_len))

runs.sort(key=lambda x: -x[1])
print("[*] 长度 >= 8 的游程 %d 个，累计 %d 条" % (len(runs), sum(r[1] for r in runs)))
print()
print("%-12s %-10s %-14s %s" % ("rawOff", "条数", "首 token", "末 token"))
for st, ln in runs[:15]:
    t0 = struct.unpack_from("<I", mv, st)[0]
    t1 = struct.unpack_from("<I", mv, st + (ln - 1) * 16)[0]
    print("%08X     %-10d %08X       %08X" % (st, ln, t0, t1))

print()
print("目标：408,458 条")
