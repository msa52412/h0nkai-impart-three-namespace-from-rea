# -*- coding: utf-8 -*-
import sys, struct
from collections import Counter
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4block import lz4_block_decompress

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()
BODIES = [137, 1301, 3052, 5801, 6833, 8427, 14189]

for off in BODIES:
    ms, fs, ver, do = struct.unpack_from(">IIII", lz4_block_decompress(raw[off:off+40]), 0)
    body = lz4_block_decompress(raw[off:], stop_at=fs)
    data = body[do:]
    print("=== body@%-6d file=%-6d dataOff=%-5d 数据区=%-6d ===" % (off, fs, do, len(data)))
    print("   前32B:", data[:32].hex())
    c = Counter(data)
    print("   字节分布 top5:", c.most_common(5))
    # 尾部
    print("   后32B:", data[-32:].hex())
