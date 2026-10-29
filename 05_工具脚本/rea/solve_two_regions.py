# -*- coding: utf-8 -*-
"""分别验证 type5(字符串) 与 type6(MethodRef) 的槽区基址；
   产出正确的 slotVA->文本 表（仅字符串槽）"""
import struct
import re
from collections import Counter

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
E64 = 0x118 + 0x339959C
N_PAIRS = 263700


def ukey(u):
    t = (u * 0x150B976713A1 + 0xB6E1C2778CFDB7D) & M64
    t >>= 0x17
    t = (t * 0x6FC15411) & M64
    t ^= 0x21CFF42D00
    t >>= 8
    return t & M32


# 解 pairs：type5(字符串) 与 type6(MethodRef) 分开
m5 = {}
m6 = {}
for u in range(N_PAIRS):
    off = E64 + u * 8
    r0 = struct.unpack_from("<I", BUF, off)[0]
    r1 = struct.unpack_from("<I", BUF, off + 4)[0]
    k = ukey(u)
    c1 = ((r1 - 0x48BC5F9E) & M32) ^ k
    c0 = ((r0 - 0x330F6527) & M32) ^ k
    t = c1 >> 29
    idx = c1 & 0x1FFFFFFF
    if t == 5 and idx < 77396 and c0 < 300000:
        m5[c0] = idx
    elif t == 6 and idx < 408461 and c0 < 300000:
        m6[c0] = idx
print("type5 dest: %d, type6 dest: %d" % (len(m5), len(m6)))

# 槽引用
pat = re.compile(r"DAT_1([0-9a-fA-F]{8})")
slot_refs = Counter()
with open(r"D:\Carol-start\_rea\bodies_merged.tsv", "rb") as f:
    for chunk in iter(lambda: f.read(1 << 24), b""):
        for mm in pat.finditer(chunk.decode("latin-1")):
            a = 0x100000000 | int(mm.group(1), 16)
            if 0x189900000 <= a <= 0x189B00000:
                slot_refs[a] += 1

B5 = 0x1899DE380   # 字符串缓存
B6 = 0x189A648B0   # MethodRef 缓存
h5 = sum(1 for a in slot_refs if (a - B5) >= 0 and (a - B5) % 8 == 0 and (a - B5) // 8 in m5)
h6 = sum(1 for a in slot_refs if (a - B6) >= 0 and (a - B6) % 8 == 0 and (a - B6) // 8 in m6)
both = sum(1 for a in slot_refs
           if (a - B5) >= 0 and (a - B5) % 8 == 0 and (a - B5) // 8 in m5
           and (a - B6) >= 0 and (a - B6) % 8 == 0 and (a - B6) // 8 in m6)
print("字符串槽区基 0x%X: type5 命中 %d / %d 槽" % (B5, h5, len(slot_refs)))
print("MethodRef 槽区基 0x%X: type6 命中 %d / %d 槽" % (B6, h6, len(slot_refs)))
print("两区重叠命中（应为 0 或极少）: %d" % both)
covered = sum(1 for a in slot_refs
              if ((a - B5) >= 0 and (a - B5) % 8 == 0 and (a - B5) // 8 in m5)
              or ((a - B6) >= 0 and (a - B6) % 8 == 0 and (a - B6) // 8 in m6))
print("两类合计覆盖: %d / %d (%.1f%%)" % (covered, len(slot_refs), 100.0 * covered / len(slot_refs)))
