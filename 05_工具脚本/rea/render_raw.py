# -*- coding: utf-8 -*-
import sys, struct, os
sys.path.insert(0, r"D:/Carol-start/_rea")
from pngtool import write_png

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
raw = open(ASB + r"\1be3f3aece7c8e0f08a2768ff33a3af4.wmv", "rb").read()
OUT = r"D:/Carol-start/_rea/tex"

def score(d, stride, n=40000):
    tot=0; c=0
    for i in range(0, min(len(d)-stride*2, n), stride):
        for ch in range(4):
            tot += abs(d[i+ch]-d[i+stride+ch]); c+=1
    return tot/max(c,1)

# 在 562000..562400 附近找垂直相关性最好的起点
best=None
for off in range(562000, 562400):
    s = score(raw[off:off+200000], 4096)
    if best is None or s < best[0]: best=(s, off)
print("最佳原始像素起点: off=%d 垂直差=%.2f" % (best[1], best[0]))
off = best[1]
rows = 142
write_png(os.path.join(OUT,"loading_raw.png"), 1024, rows, raw[off:off+rows*4096])
print("已写出 loading_raw.png 1024x%d" % rows)
