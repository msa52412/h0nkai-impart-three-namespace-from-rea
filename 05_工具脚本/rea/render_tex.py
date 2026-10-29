# -*- coding: utf-8 -*-
import sys, struct, os
from collections import Counter
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4map2 import lz4_ex
from pngtool import write_png

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()
OUT = r"D:/Carol-start/_rea/tex"
os.makedirs(OUT, exist_ok=True)

# (起点, SF大小, 宽, 高, 名字)
SPECS = [(137, 5088, 32, 32, "Add"), (1301, 5044, 88, 48, "BackIcon")]

for off, sfsize, w, h, name in SPECS:
    full, used = lz4_ex(raw[off:])
    px = full[sfsize:]
    print("%s: 流解压 %d B, 像素区 %d B, 期望 %d (%dx%d RGBA)" % (name, len(full), len(px), w*h*4, w, h))
    c = Counter()
    for i in range(0, len(px), 4):
        c[px[i:i+4]] += 1
    print("   颜色 top6:", [(k.hex(), v) for k, v in c.most_common(6)])
    p = write_png(os.path.join(OUT, name + "_orig.png"), w, h, px[:w*h*4])
    print("   已写出:", p)
