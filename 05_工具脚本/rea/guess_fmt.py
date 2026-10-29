# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4src import lz4_srcmap

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
raw = open(ASB + r"\1be3f3aece7c8e0f08a2768ff33a3af4.wmv", "rb").read()
body, _, _, _ = lz4_srcmap(raw[199:])
fs = struct.unpack_from(">I", body, 4)[0]
data = body[fs:fs + 400000]

def smooth(d, bpp, ch=0, width=None):
    """同通道相邻像素平均差，越小越像真图"""
    tot = 0; n = 0
    for i in range(0, len(d) - bpp*2, bpp):
        a = d[i+ch]; b = d[i+bpp+ch]
        tot += abs(a-b); n += 1
    return tot/max(n, 1)

print("按 bpp 估计同通道相邻差（越小越像真图）:")
for bpp, name in ((4, "RGBA32"), (3, "RGB24"), (2, "RG16"), (1, "R8/DXT")):
    best = min((smooth(data, bpp, ch), ch) for ch in range(bpp))
    print("  %-8s 最佳通道 %d, 平均差 %.2f" % (name, best[1], best[0]))

# 随机基线
import random
rnd = bytes(random.randrange(256) for _ in range(200000))
print("  随机基线 平均差 %.2f" % smooth(rnd, 4, 0))

# 也试试整体偏移
print("\n试不同起始偏移(bpp=4):")
for off in range(0, 40):
    print("   off=%-3d 平均差 %.2f" % (off, smooth(data[off:], 4, 0)))
