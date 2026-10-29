# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4src import lz4_srcmap

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
raw = open(ASB + r"\1be3f3aece7c8e0f08a2768ff33a3af4.wmv", "rb").read()
body, _, _, _ = lz4_srcmap(raw[199:])
fs = struct.unpack_from(">I", body, 4)[0]
data = body[fs:fs + 900000]
total = 1499136

print("总像素字节 =", total, " 若 bpp=4 则像素数 =", total//4)
res = []
for w in range(64, 2049, 1):
    if total % (w*4): continue
    h = total // (w*4)
    if h < 16 or h > 2048: continue
    stride = w*4
    tot = 0; n = 0
    for i in range(0, min(len(data) - stride*2, 300000), stride):
        for ch in range(4):
            tot += abs(data[i+ch] - data[i+stride+ch]); n += 1
    res.append((tot/max(n,1), w, h))
res.sort()
print("垂直相邻差最小的候选宽高:")
for d, w, h in res[:10]:
    print("   %4dx%-4d 平均差 %.2f" % (w, h, d))
