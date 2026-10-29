#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读 dec_targets.c 里所有关键全局的实际值，算出文件偏移，并 dump 对应区域。
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118

with open(DLL, "rb") as f:
    data = f.read()

e = struct.unpack_from("<I", data, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", data, coff + 2)[0]
optsz = struct.unpack_from("<H", data, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", data, opt + 24)[0]
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    vs, va, rs, rp = struct.unpack_from("<IIII", data, o + 8)
    SECS.append((va, vs, rs, rp))


def u32va(va):
    rva = va - IB
    for vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            if rsize == 0:
                return None
            return struct.unpack_from("<I", data, rptr + (rva - vaddr))[0]
    return None


with open(META, "rb") as f:
    BUF = f.read()
FSIZE = len(BUF)

print("=" * 80)
print("关键全局值 与 推算出的段偏移")
print("=" * 80)

ITEMS = [
    ("DAT_188198E04 - 0x1FE83754", 0x188198E04, -0x1FE83754, "程序集描述符数组 (dec_targets.c:299)"),
    ("DAT_188198E6C - 0x3670DF73", 0x188198E6C, -0x3670DF73, "int32 索引数组 (dec_targets.c:308)"),
    ("DAT_188198E08 ^ 0x2B849DB3", 0x188198E08, None, "表10/类型表基址 (dec_targets.c:499)"),
    ("DAT_188198E58 - 0x17A3B99", 0x188198E58, -0x017A3B99, "表9 基址 (dec_targets.c:523)"),
    ("DAT_1881A3630 ^ 0x421DD17C", 0x1881A3630, None, "类型条目数量 (dec_targets.c:584)"),
]

for label, va, const, desc in ITEMS:
    v = u32va(va)
    if v is None:
        print("%-32s 读取失败" % label)
        continue
    if const is not None:
        val = (v + const) & 0xFFFFFFFF
        val_s = val - (1 << 32) if val >= (1 << 31) else val
        print("%-32s 0x%08X  ->  %d (0x%X)" % (label, v, val_s, val & 0xFFFFFFFF))
        if 0 <= val_s < FSIZE:
            print("    文件偏移 0x%X  ✓ 在文件内" % (BASE + val_s))
    else:
        mask = 0x2B849DB3 if "2B849DB3" in label else 0x421DD17C
        val = v ^ mask
        print("%-32s 0x%08X  ^ 0x%08X = %d (0x%X)" % (label, v, mask, val, val))
        if "2B849DB3" in label and val < FSIZE:
            print("    文件偏移 0x%X  ✓ 在文件内" % (BASE + val))

print()
print("=" * 80)
print("表10（类型表）区域 dump —— offset 由上面算出")
print("=" * 80)

t10 = u32va(0x188198E08) ^ 0x2B849DB3
abs10 = BASE + t10
print("表10 绝对偏移 0x%X，步长 0x5C" % abs10)

# 按 0x5C 步长看前 20 条，每条的 23 个 int32
for i in range(20):
    off = abs10 + i * 0x5C
    if off + 0x5C > FSIZE:
        break
    vals = struct.unpack_from("<23I", BUF, off)
    print("  [%3d] " % i + " ".join("%08X" % v for v in vals[:8]))
    print("        " + " ".join("%08X" % v for v in vals[8:16]))
    print("        " + " ".join("%08X" % v for v in vals[16:]))

print()
print("=" * 80)
print("程序集描述符数组 (每条 8 字节) dump")
print("=" * 80)
d = (u32va(0x188198E04) - 0x1FE83754) & 0xFFFFFFFF
absd = BASE + d
print("绝对偏移 0x%X" % absd)
for i in range(24):
    off = absd + i * 8
    if off + 8 > FSIZE:
        break
    a, b = struct.unpack_from("<2I", BUF, off)
    print("  [%3d] %08X %08X   (%d, %d)" % (i, a, b, a, b))

print()
print("=" * 80)
print("int32 索引数组 dump")
print("=" * 80)
x = (u32va(0x188198E6C) - 0x3670DF73) & 0xFFFFFFFF
absx = BASE + x
print("绝对偏移 0x%X" % absx)
vals = struct.unpack_from("<40I", BUF, absx)
print("  前 40 个: " + " ".join("%08X" % v for v in vals[:20]))
print("            " + " ".join("%08X" % v for v in vals[20:]))
print("  作为十进制: " + " ".join("%d" % v for v in vals[:20]))
