#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为 rea/IDA 生成 UserAssembly.dll 的「瘦身版」。

为什么需要
----------
原文件 182 MB，其中：
    il2cpp   103 MB   <- 路线 B 完全用不到（明文机器码，但我们的目标函数不在里面）
    .tvm0     11 MB   <- 腾讯虚拟化节，IDA 分析它纯属浪费
    .text    5.4 MB   <- ★ 我们全部目标函数都在这里
    .rdata    32 MB   <- 字符串锚点 + XOR 混淆常量
    .data     12 MB   <- 初始化数据
    .pdata    10 MB   <- 函数边界表（必须保留）

13 GB 内存跑全量 auto-analysis 会 OOM / 超时。
本脚本把 il2cpp 与 .tvm0 的 raw 数据摘掉（SizeOfRawData=0、PointerToRawData=0、
清掉 CODE/EXECUTE 标志、VirtualSize 压到 0x1000），
IDA 就不会去反汇编那 114 MB，分析量降到约 1/3，且**所有 RVA 完全不变**。

关键：只改节表头 4 个字段，不动任何字节内容，也不移动任何节的偏移，
所以 .text / .rdata / .data / .pdata 的 PointerToRawData 依然有效。

用法：
    python slim_pe.py                     # 生成 UserAssembly_slim.dll
    python slim_pe.py --verify            # 生成后校验目标 RVA 字节一致
"""
import os
import struct
import sys

import pefile

SRC = r"Z:\AI\7.0\BH3_Data\Native\UserAssembly.dll"
DST = r"Z:\AI\7.0\_ext\re\UserAssembly_slim.dll"

# 要摘掉 raw 数据的节
STRIP = {b"il2cpp", b".tvm0"}

# 需要校验的 RVA（本轮路线 B 用到的全部锚点）
CHECK_RVAS = [
    0x043FC0,   # LoadMetadataFile 入口
    0x044079,   # 引用 "global-metadata.dat" 的那条 lea
    0x03EC20,   # metadata 初始化函数入口
    0x03EC45,   # 调用 LoadMetadataFile 的位置
    0x01C210,   # 按索引读记录的底层函数
    0x04F1B20,  # 取文件大小 + malloc
    0x04ED510,  # mov [global],ecx; ret 的 setter
    0x04F09A0,  # malloc 包装
    0x03F4CC0,  # 打开文件
    0x03F0DD0,  # 关闭文件
    0x81A2478,  # "global-metadata.dat" 字符串
    0x81A2490,  # "Metadata" 字符串
    0x81993F4,  # 期望版本常量 23
    0x81A3640,  # XOR 混淆常量 1
    0x8198E78,  # XOR 混淆常量 2
]


def main():
    verify = "--verify" in sys.argv

    print("读取 %s ..." % SRC)
    data = bytearray(open(SRC, "rb").read())
    pe = pefile.PE(data=bytes(data), fast_load=True)
    ib = pe.OPTIONAL_HEADER.ImageBase

    sec_table = (pe.OPTIONAL_HEADER.get_file_offset()
                 + pe.FILE_HEADER.SizeOfOptionalHeader)
    print("ImageBase=0x%X  节表偏移=0x%X  节数=%d"
          % (ib, sec_table, pe.FILE_HEADER.NumberOfSections))

    # 记录瘦身前各节的 RVA 映射，用于校验
    before = {}
    for s in pe.sections:
        n = s.Name.rstrip(b"\0")
        before[n] = (s.VirtualAddress, s.PointerToRawData, s.SizeOfRawData)

    print()
    print("%-10s %10s %10s %10s   %s" % ("节", "RVA", "RawPtr", "RawSize", "处理"))
    print("-" * 62)
    stripped = 0
    for i, s in enumerate(pe.sections):
        name = s.Name.rstrip(b"\0")
        hdr = sec_table + i * 40
        if name in STRIP:
            struct.pack_into("<I", data, hdr + 8, 0x1000)      # VirtualSize
            struct.pack_into("<I", data, hdr + 16, 0)          # SizeOfRawData
            struct.pack_into("<I", data, hdr + 20, 0)          # PointerToRawData
            struct.pack_into("<I", data, hdr + 36, 0x40000040)  # INITIALIZED_DATA|READ
            stripped += s.SizeOfRawData
            act = "摘掉 raw (-%.1f MB)" % (s.SizeOfRawData / 1048576)
        else:
            act = "保留"
        print("%-10s 0x%08X 0x%08X 0x%08X   %s"
              % (name.decode(errors="replace"), s.VirtualAddress,
                 s.PointerToRawData, s.SizeOfRawData, act))

    open(DST, "wb").write(bytes(data))
    print()
    print("已写出 %s  (%.1f MB, 摘掉 %.1f MB raw)"
          % (DST, len(data) / 1048576, stripped / 1048576))

    if not verify:
        return

    print()
    print("=== 校验：目标 RVA 的字节必须与原文件完全一致 ===")
    orig = open(SRC, "rb").read()
    slim = open(DST, "rb").read()

    def va2off(pe_, d, va):
        rva = va - pe_.OPTIONAL_HEADER.ImageBase
        for s_ in pe_.sections:
            if s_.VirtualAddress <= rva < s_.VirtualAddress + max(s_.Misc_VirtualSize, s_.SizeOfRawData):
                return s_.PointerToRawData + (rva - s_.VirtualAddress)
        return None

    ok = 0
    bad = 0
    for rva in CHECK_RVAS:
        va = ib + rva
        o1 = va2off(pe, orig, va)
        if o1 is None:
            print("  0x%08X  原文件无法映射" % rva)
            bad += 1
            continue
        # 瘦身版用「新节表」重新解析
        pe2 = pefile.PE(data=slim, fast_load=True)
        o2 = va2off(pe2, slim, va)
        if o2 is None:
            print("  0x%08X  瘦身版无法映射  <-- 失败" % rva)
            bad += 1
            continue
        a = orig[o1:o1 + 16]
        b = slim[o2:o2 + 16]
        if a == b:
            ok += 1
        else:
            print("  0x%08X  字节不一致" % rva)
            print("     原: %s" % a.hex(" "))
            print("     新: %s" % b.hex(" "))
            bad += 1
    print("  一致 %d / %d，不一致 %d" % (ok, len(CHECK_RVAS), bad))
    print("  结论：%s" % ("PASS —— 可以直接拿去分析" if bad == 0 else "FAIL"))


if __name__ == "__main__":
    main()
