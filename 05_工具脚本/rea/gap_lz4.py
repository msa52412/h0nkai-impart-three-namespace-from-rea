# -*- coding: utf-8 -*-
import sys, struct
from collections import Counter
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4map2 import lz4_ex

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()
GAPS = [(0,137),(763,1301),(1932,3052),(3805,5801),(6406,6833),(7485,8427),(14074,14189)]

for a, b in GAPS:
    seg = raw[a:b]
    print("=== 空洞 [%d..%d] %d B ===" % (a, b, len(seg)))
    best = None
    for s in range(0, min(32, len(seg))):
        out, used = lz4_ex(seg[s:])
        if used < 16: continue
        # 判断是否为“完整”流：消耗接近剩余长度
        if best is None or used > best[2]:
            best = (s, len(out), used)
    if best:
        s, ol, used = best
        out, _ = lz4_ex(seg[s:])
        print("   最佳 LZ4 起点 +%d -> 解压 %d B, 消耗 %d/%d B" % (s, ol, used, len(seg) - s))
        print("   前32B:", out[:32].hex())
        print("   分布:", Counter(out).most_common(4))
        # 猜尺寸
        for bpp, name in ((4, "RGBA"), (3, "RGB"), (1, "A8/DXT5"), (0.5, "DXT1")):
            px = ol / bpp
            r = int(px ** 0.5)
            if r * r == px: print("     可能是 %s %dx%d" % (name, r, r))
    else:
        print("   非 LZ4")
