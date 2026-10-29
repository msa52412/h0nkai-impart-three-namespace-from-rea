# -*- coding: utf-8 -*-
"""找 attribute range 表（76,737 个 owner 的 {start, count}）：
   明文判据：start 单调递增覆盖 [0, 76737)，count 小；generator 表前后扫"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
N_ATTR = 76737
GEN_S, GEN_E = 0xA3F44C, 0xA93B0C

def scan(lo, hi, tag):
    best = (0, 0)
    run0 = runlen = 0
    prev = -1
    i = lo
    while i + 8 <= hi:
        s, c = struct.unpack_from("<2I", BUF, i)
        if prev < s < N_ATTR and 0 <= c <= 64:
            if runlen == 0:
                run0 = i
                prev = -1
                s0, _ = struct.unpack_from("<2I", BUF, run0)
                prev = s0
            runlen += 1
            prev = s
            if runlen > best[1]:
                best = (run0, runlen)
        else:
            runlen = 0
        i += 8
    if runlen >= 100:
        print("  %s: run @0x%X 长 %d" % (tag, best[0], best[1]))
    return best

# 生成器表之前的区（PARAM 表 0xAC1050 之后到 GEN_S）
print("generator 表周边扫 {start<76737 递增, count<=64}:")
scan(0xAC2050, GEN_S, "GEN 前")
scan(GEN_E, 0xFA8430, "GEN 后")

# 也扫 {start, count} 反序（count, start）
def scan2(lo, hi, tag):
    best = (0, 0)
    run0 = runlen = 0
    prev = -1
    i = lo
    while i + 8 <= hi:
        c, s = struct.unpack_from("<2I", BUF, i)
        if prev < s < N_ATTR and 0 <= c <= 64:
            if runlen == 0:
                run0 = i
                prev = -1
                _, s0 = struct.unpack_from("<2I", BUF, run0)
                prev = s0
            runlen += 1
            prev = s
            if runlen > best[1]:
                best = (run0, runlen)
        else:
            runlen = 0
        i += 8
    if best[1] >= 100:
        print("  %s(反序): run @0x%X 长 %d" % (tag, best[0], best[1]))
    return best

scan2(0xAC2050, GEN_S, "GEN 前")
scan2(GEN_E, 0xFA8430, "GEN 后")
print("完成")
