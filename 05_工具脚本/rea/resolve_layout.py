#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析 UserAssembly_slim.dll 的 PE 节表，按 VA 读取常量，
再套用 FUN_18043EC20 伪代码里的解密公式，还原 metadata 表布局。

对应 Ghidra 伪代码（D:\Carol-start\_rea\dec_targets.c 174-500 行）。
"""
import struct
import sys

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"

# ---- PE 解析 ----
with open(DLL, "rb") as f:
    data = f.read()

e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
assert data[e_lfanew:e_lfanew + 4] == b"PE\0\0", "not a PE"
coff = e_lfanew + 4
nsec = struct.unpack_from("<H", data, coff + 2)[0]
opt_size = struct.unpack_from("<H", data, coff + 16)[0]
opt = coff + 20
magic = struct.unpack_from("<H", data, opt)[0]
image_base = struct.unpack_from("<Q", data, opt + 24)[0] if magic == 0x20B else struct.unpack_from("<I", data, opt + 28)[0]
size_of_image = struct.unpack_from("<I", data, opt + 56)[0]

secs = []
sh = opt + opt_size
for i in range(nsec):
    o = sh + i * 40
    name = data[o:o + 8].rstrip(b"\0").decode("latin1")
    vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
    secs.append((name, vaddr, vsize, rawsize, rawptr))

print("image_base = 0x%X  size_of_image = 0x%X (%d MB)" % (image_base, size_of_image, size_of_image >> 20))
print("%-10s %-12s %-12s %-12s %-12s" % ("section", "RVA", "VSize", "RawSize", "RawPtr"))
for name, vaddr, vsize, rawsize, rawptr in secs:
    flag = "  <== STRIPPED" if rawsize == 0 else ""
    print("%-10s 0x%-10X 0x%-10X 0x%-10X 0x%-10X%s" % (name, vaddr, vsize, rawsize, rawptr, flag))
print()


def va2off(va):
    rva = va - image_base
    for name, vaddr, vsize, rawsize, rawptr in secs:
        if vaddr <= rva < vaddr + max(vsize, rawsize):
            if rawsize == 0:
                return None, name
            return rawptr + (rva - vaddr), name
    return None, "?"


def u32(va):
    off, sec = va2off(va)
    if off is None:
        return None
    return struct.unpack_from("<I", data, off)[0]


def s32(va):
    v = u32(va)
    return None if v is None else struct.unpack("<i", struct.pack("<I", v))[0]


# ---- 伪代码里引用的全局 ----
GLOBALS = {
    0x188198DF4: "版本期望值 (与文件 +4 比较)",
    0x1881A3640: "表1 count 源  (^ 0x7CD3B5B8)",
    0x188198E78: "表2 count 源  (- 0x0A4FFD99) / 0x28",
    0x188198E14: "表3 count 源  (^ 0x5F613838) >> 5",
    0x1881A35EC: "表4 count 源  (^ 0x7CC59670)",
    0x188198E4C: "表5 count 源  (^ 0x6F3F9184) / 0x28",
    0x188198E20: "表6 count 源  (^ 0x20910E12) >> 4",
    0x188198E1C: "表5 数据 offset (^ 0x72267500)",
    0x188198E60: "表7 数据 offset (^ 0x371B8070)",
    0x188198E70: "表8 数据 offset (^ 0x0561C6FD)",
    0x188198E08: "表9 数据 offset (^ 0x2B849DB3)",
    0x188198E58: "表10 数据 offset (- 0x017A3B99)",
    0x1881396AC: "FUN_1804ed510 参数",
    0x1881396D8: "循环上界源 (比较 0x18A8540C)",
}

print("=" * 78)
print("原始全局值")
print("=" * 78)
raw = {}
for va, desc in sorted(GLOBALS.items()):
    v = u32(va)
    raw[va] = v
    if v is None:
        print("0x%X  %-46s <无法读取>" % (va, desc))
    else:
        print("0x%X  0x%08X (%11d)  %s" % (va, v, v, desc))
print()

# ---- 套用伪代码公式 ----
print("=" * 78)
print("套用 FUN_18043EC20 的解密公式")
print("=" * 78)


def show(label, expr, value, extra=""):
    print("%-34s %-40s = %s %s" % (label, expr, value, extra))


# 表1: count = (int)(DAT_1881a3640 ^ 0x7cd3b5b8), 元素 8 字节
v = raw[0x1881A3640]
if v is not None:
    show("表1 (0x8/elem)", "0x%08X ^ 0x7CD3B5B8" % v, "%d" % (v ^ 0x7CD3B5B8))

# 表2: count = ((x - 0xa4ffd99) / 0x28)   魔数除法
v = raw[0x188198E78]
if v is not None:
    x = (v - 0x0A4FFD99) & 0xFFFFFFFF
    show("表2 (0x28/elem)", "(0x%08X - 0x0A4FFD99)/0x28" % v, "%d" % (x // 0x28))

# 表3: count = (int)(x ^ 0x5f613838) >> 5
v = raw[0x188198E14]
if v is not None:
    show("表3 (0x8/elem)", "(0x%08X ^ 0x5F613838)>>5" % v, "%d" % ((v ^ 0x5F613838) >> 5))

# 表4: count = (int)(x ^ 0x7cc59670)
v = raw[0x1881A35EC]
if v is not None:
    show("表4 (0x8/elem)", "0x%08X ^ 0x7CC59670" % v, "%d" % (v ^ 0x7CC59670))

# 表5: count = (x ^ 0x6f3f9184) / 0x28, 元素 0x50
v = raw[0x188198E4C]
if v is not None:
    x = (v ^ 0x6F3F9184)
    n5 = x // 0x28
    show("表5 (0x50/elem)", "(0x%08X ^ 0x6F3F9184)/0x28" % v, "%d" % n5)

# 表6: count = (x ^ 0x20910e12) >> 4, 元素 0x60
v = raw[0x188198E20]
if v is not None:
    x = (v ^ 0x20910E12)
    n6 = x >> 4
    show("表6 (0x60/elem)", "(0x%08X ^ 0x20910E12)>>4" % v, "%d" % n6)

print()
print("--- 数据段偏移 (相对 s_GlobalMetadata = buf + 0x118) ---")
offsets = {}
for va, mask, label in [
    (0x188198E1C, 0x72267500, "表5 记录区 (步长 0x28)"),
    (0x188198E60, 0x371B8070, "表7 记录区 (步长 0x10)"),
    (0x188198E70, 0x0561C6FD, "表8 记录区 (步长 0x2C)"),
    (0x188198E08, 0x2B849DB3, "表9 记录区 (步长 0x5C)"),
]:
    v = raw[va]
    if v is not None:
        off = v ^ mask
        offsets[label] = off
        print("%-30s 0x%08X ^ 0x%08X = 0x%08X (%d)" % (label, v, mask, off, off))

v = raw[0x188198E58]
if v is not None:
    off = (v - 0x017A3B99) & 0xFFFFFFFF
    offsets["表10 记录区 (步长 0x20)"] = off
    print("%-30s 0x%08X - 0x017A3B99 = 0x%08X (%d)" % ("表10 记录区 (步长 0x20)", v, off, off))

print()
print("--- 循环上界 ---")
v = raw[0x1881396D8]
if v is not None:
    print("DAT_1881396D8 = 0x%08X ; 上界 = v + 0xE757ABF4 = %d" % (v, (v + 0xE757ABF4) & 0xFFFFFFFF))
    print("  是否等于 0x18A8540C ? %s" % (v == 0x18A8540C))

# ---- 与文件实际内容对照 ----
print()
print("=" * 78)
print("与 global-metadata.dat 头部对照")
print("=" * 78)
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
try:
    with open(META, "rb") as f:
        head = f.read(0x140)
    print("magic            : %r" % head[0:4])
    print("+0x00 (uint32)   : 0x%08X" % struct.unpack_from("<I", head, 0)[0])
    print("+0x04 (uint32)   : 0x%08X   <-- 与版本期望值比较" % struct.unpack_from("<I", head, 4)[0])
    print("+0x08 (uint32)   : 0x%08X" % struct.unpack_from("<I", head, 8)[0])
    print("+0x118 (uint32)  : 0x%08X" % struct.unpack_from("<I", head, 0x118)[0])
    print()
    exp = raw[0x188198DF4]
    actual = struct.unpack_from("<I", head, 4)[0]
    print("版本期望值       : 0x%08X" % exp)
    print("文件 +4 实际值   : 0x%08X" % actual)
    print("相等?            : %s" % (exp == actual))
except Exception as e:
    print("无法读取 metadata: %s" % e)
