# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4map2 import lz4_ex

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()
for OFF in (137, 1301, 3052, 5801, 6833, 8427, 14189):
    out, used = lz4_ex(raw[OFF:])
    print("body@%-6d 无停止解压 -> %-7d B, 消耗 %-6d / 剩余 %-6d" % (OFF, len(out), used, len(raw)-OFF))
