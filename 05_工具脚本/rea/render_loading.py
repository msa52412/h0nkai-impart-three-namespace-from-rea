# -*- coding: utf-8 -*-
import sys, os, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4src import lz4_srcmap
from pngtool import write_png

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
raw = open(ASB + r"\1be3f3aece7c8e0f08a2768ff33a3af4.wmv", "rb").read()
OUT = r"D:/Carol-start/_rea/tex"
os.makedirs(OUT, exist_ok=True)

body, _, _, used = lz4_srcmap(raw[199:])
fs = struct.unpack_from(">I", body, 4)[0]
px = body[fs:]
print("SF=%d 像素交付=%d 字节 = %.2f 行(1024宽RGBA)" % (fs, len(px), len(px)/(1024*4)))
rows = len(px) // (1024*4)
print("可渲染 %d 行" % rows)
if rows > 0:
    write_png(os.path.join(OUT, "loading_part.png"), 1024, rows, px[:rows*1024*4])
    print("已写出 loading_part.png  %dx%d" % (1024, rows))
