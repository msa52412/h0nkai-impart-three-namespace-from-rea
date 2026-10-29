# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4block import lz4_block_decompress

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()
body = lz4_block_decompress(raw[137:], stop_at=5088)

# 找 version string 的 null
print("bytes 16..48:", body[16:48].hex())
z = body.find(b"\x00", 20)
print("第一个 null 在", z, " 前面内容:", body[20:z])

for start in range(z, z + 24):
    try:
        tp = struct.unpack_from(">i", body, start)[0]
        tt = body[start + 4]
        if tt not in (0, 1): continue
        oc = struct.unpack_from(">i", body, start + 5)[0]
        if 0 <= oc <= 200:
            print("start=%-4d targetPlatform=%-6d typeTree=%d objectCount=%d" % (start, tp, tt, oc))
    except Exception:
        pass
