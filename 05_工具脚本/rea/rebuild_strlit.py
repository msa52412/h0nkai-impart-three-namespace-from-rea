# -*- coding: utf-8 -*-
"""重建纯 type5 映射并与旧版（5+6 混合）对比槽命中率；确定槽区正确基址"""
import struct
import re
from collections import Counter

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
E64 = 0x118 + 0x339959C
N_PAIRS = 263700  # 表真实边界

TBL = 0x118 + 0x1EC6620
DATA = 0x3185A9C
STEP = 0x5BB8DBE022B62203


def ukey(u):
    t = (u * 0x150B976713A1 + 0xB6E1C2778CFDB7D) & M64
    t >>= 0x17
    t = (t * 0x6FC15411) & M64
    t ^= 0x21CFF42D00
    t >>= 8
    return t & M32


def key_row(i):
    v = (i * 0x1AB6B1E4CD9A) & M64
    v >>= 0xB
    v = (v * 0x6595FC2F) & M64
    v ^= 0x790A43A40000
    v >>= 0x11
    return v & M32


def seed(i):
    v = (i * 0x54CCBD2A6C08DF18) & M64
    v ^= 0x25450C2973B42381
    v = (v * 0x174BDB9B4B2EC230) & M64
    v ^= 0x6F7A46CC48B4908D
    v = (v * 0x2BB71BC476FEFD2E) & M64
    return (v - 0x0EEA8D685E597BCC) & M64


def blob(i):
    off = TBL + i * 8
    k = key_row(i)
    o = ((struct.unpack_from("<I", BUF, off)[0] ^ 0x2BE4EEE9) - k) & M32
    l = (struct.unpack_from("<I", BUF, off + 4)[0] - k - 0x25C2F1A9) & M32
    kk = seed(i)
    out = bytearray()
    for q in range((l + 7) >> 3):
        out += (struct.unpack_from("<Q", BUF, DATA + o + q * 8)[0] ^ kk).to_bytes(8, "little")
        kk = (kk + STEP) & M64
    return bytes(out[:l]).decode("utf-8", "replace")


# 解 pairs
m5 = {}   # 纯 type5: dest -> text
m56 = {}  # 旧版 5+6
n5 = n6 = 0
for u in range(N_PAIRS):
    off = E64 + u * 8
    r0 = struct.unpack_from("<I", BUF, off)[0]
    r1 = struct.unpack_from("<I", BUF, off + 4)[0]
    k = ukey(u)
    c1 = ((r1 - 0x48BC5F9E) & M32) ^ k
    c0 = ((r0 - 0x330F6527) & M32) ^ k
    t = c1 >> 29
    idx = c1 & 0x1FFFFFFF
    if idx < 77396 and c0 < 300000:
        if t == 5:
            m5[c0] = idx
            n5 += 1
        elif t == 6:
            m56[c0] = idx
            n6 += 1
        if t in (5, 6):
            m56.setdefault(c0, idx)
print("type5 pairs: %d, type6(字符串域内): %d, 合计唯一 dest: %d" % (n5, n6, len(m56)))

# 反编译体槽引用
pat = re.compile(r"DAT_1([0-9a-fA-F]{8})")
slot_refs = Counter()
with open(r"D:\Carol-start\_rea\bodies_merged.tsv", "rb") as f:
    for chunk in iter(lambda: f.read(1 << 24), b""):
        for mm in pat.finditer(chunk.decode("latin-1")):
            a = 0x100000000 | int(mm.group(1), 16)
            if 0x189900000 <= a <= 0x189B00000:
                slot_refs[a] += 1
print("槽区引用: %d 个不同槽" % len(slot_refs))

base = 0x1899DE380
for name, mm in (("纯type5", m5), ("5+6混合", m56)):
    hits = sum(n for a, n in slot_refs.items()
               if (a - base) >= 0 and (a - base) % 8 == 0 and (a - base) // 8 in mm)
    tot = sum(slot_refs.values())
    print("%s 映射: 槽种类命中 %d, 引用次数覆盖 %d/%d" %
          (name, sum(1 for a in slot_refs if (a-base) >= 0 and (a-base) % 8 == 0 and (a-base)//8 in mm), hits, tot))

# 输出纯 type5 版映射
with open(r"D:\Carol-start\_rea\bh3_strlit_map.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("destIdx\tliteralIdx\ttext\n")
    for d in sorted(m5):
        f.write("%d\t%d\t%s\n" % (d, m5[d], blob(m5[d]).replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")))
print("已重写 bh3_strlit_map.tsv（纯 type5）")

# 槽地址 -> 文本 直查表（供源码生成用）
with open(r"D:\Carol-start\_rea\bh3_slot_text.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("slotVA\tdestIdx\ttext\n")
    for d in sorted(m5):
        f.write("0x%X\t%d\t%s\n" % (base + d * 8, d, blob(m5[d]).replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")))
print("已写 bh3_slot_text.tsv")
