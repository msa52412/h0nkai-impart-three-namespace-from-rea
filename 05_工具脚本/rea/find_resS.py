# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4map2 import lz4_ex

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()
GAPS = [(0,137),(763,1301),(1932,3052),(3805,5801),(6406,6833),(7485,8427),(14074,14189)]
WANT = {4096, 16896, 4224, 1024, 16384, 2048}

for a, b in GAPS:
    seg = raw[a:b]
    print("=== 空洞 [%d..%d] %d B ===" % (a, b, len(seg)))
    for s in range(0, len(seg) - 8):
        for target in (4096, 16896):
            out, used = lz4_ex(seg[s:], stop_at=target)
            if len(out) == target:
                print("   +%-5d -> 解压 %-6d B 消耗 %-5d B  前16B=%s" % (s, target, used, out[:16].hex()))
                break
