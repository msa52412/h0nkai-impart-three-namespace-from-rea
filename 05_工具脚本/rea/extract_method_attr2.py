# -*- coding: utf-8 -*-
"""方法→attribute 关联表落盘：
   方法表(0x20/条) +0x14 列 = attrIdx（1 基全局行号，0xFFFFFF 域内 76,737 个唯一值）
   PRF 与名字列同源。方法表真实行数 251,708（其后越界）"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
TBL = 0x118 + 0xFA8318
N_METH = 251708
MAX_ATTR = 76737

def prf(i):
    x = ((i * 0xB069) ^ 0x3E382F2D) & M64
    x = (x * 0x24147491) & M64
    x = (x ^ 0xF997B4A800) >> 10
    x = (x * 0x3857AACA) & M64
    return x >> 0xE

n_attr = 0
with open(r"D:\Carol-start\_rea\bh3_method_attr.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("methodIdx\tattrIdx\n")
    for i in range(N_METH):
        raw = struct.unpack_from("<I", BUF, TBL + i * 0x20 + 0x14)[0]
        idx = (((raw + 0xBD6FC398) & M32) ^ prf(i)) & 0xFFFFFF
        if 1 <= idx <= MAX_ATTR:
            f.write("%d\t%d\n" % (i, idx))
            n_attr += 1
print("方法→attr 关联 %d 条（覆盖唯一 blob %d 个中的重复引用）" % (n_attr, MAX_ATTR))

# 与镜像段对齐抽查：mscorlib 方法(0..1698 区间内的前 300) idx 应 ⊆ [1,1499]
in_seg = sum(1 for i in range(300)
             if 1 <= ((((struct.unpack_from("<I", BUF, TBL + i*0x20 + 0x14)[0] + 0xBD6FC398) & M32) ^ prf(i)) & 0xFFFFFF) <= 1499)
print("mscorlib 前 300 方法 idx∈[1,1499]: %d/300" % in_seg)
