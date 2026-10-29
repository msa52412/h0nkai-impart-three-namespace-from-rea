#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按 FUN_18043EC20 解出的布局，dump global-metadata.dat 的表记录区，验证结构。
"""
import struct

META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
BASE = 0x118  # s_GlobalMetadata = buf + 0x118

# 从 resolve_layout.py 得到的段偏移（相对 buf+0x118）
SEG = {
    "表5 描述记录  (步长 0x28, 192 条)": (0x01C2A198, 0x28, 192),
    "表7 记录      (步长 0x10, 192 条)": (0x0242D2E8, 0x10, 192),
    "表8 记录      (步长 0x2C, 192 条)": (0x01C6556C, 0x2C, 192),
    "表9 记录      (步长 0x5C)        ": (0x000512A0, 0x5C, 12),
}

with open(META, "rb") as f:
    f.seek(0, 2)
    fsize = f.tell()
    print("global-metadata.dat 大小 = %d (0x%X)" % (fsize, fsize))

    for label, (off, step, cnt) in SEG.items():
        abs_off = BASE + off
        end = abs_off + step * cnt
        print()
        print("=" * 92)
        print("%s  相对 0x%X -> 文件 0x%X, 需 %d 字节, 结束于 0x%X (文件 %d)" %
              (label, off, abs_off, step * cnt, end, fsize))
        print("=" * 92)
        if end > fsize:
            print("!! 超出文件范围")
            continue
        f.seek(abs_off)
        blob = f.read(step * cnt)

        nint = step // 4
        show = min(cnt, 8)
        for i in range(show):
            vals = struct.unpack_from("<%dI" % nint, blob, i * step)
            print("  [%3d] " % i + " ".join("%08X" % v for v in vals))

        # 统计：把每个字段位置当 uint32，看是否有明显规律
        print("  --- 各字段位统计（全部 %d 条）---" % cnt)
        for k in range(nint):
            col = [struct.unpack_from("<I", blob, i * step + k * 4)[0] for i in range(cnt)]
            mn, mx = min(col), max(col)
            uniq = len(set(col))
            # 相邻差值是否恒定
            diffs = {col[i + 1] - col[i] for i in range(cnt - 1)}
            const_diff = ("步长=%d" % diffs.pop()) if len(diffs) == 1 else ""
            print("    +0x%02X: min=%08X max=%08X uniq=%3d %s" % (k * 4, mn, mx, uniq, const_diff))
