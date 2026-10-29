# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4map2 import lz4_ex

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
raw = open(ASB + r"\1be3f3aece7c8e0f08a2768ff33a3af4.wmv", "rb").read()

TOTAL_PX = 1499136
BLOCK1_PX = 224*4096          # 917504
NEED = TOTAL_PX - BLOCK1_PX   # 581632
print("需要剩余像素 %d 字节 (%d 行)" % (NEED, NEED//4096))

for off in range(562100, 562220):
    out, used = lz4_ex(raw[off:], stop_at=NEED)
    if len(out) == NEED:
        print("命中! 起点=%d 消耗=%d" % (off, used))
        print("  前16B:", out[:16].hex())
        break
else:
    print("未找到正好 %d 的块" % NEED)
    # 退一步：看看 562132 起能解多少
    out, used = lz4_ex(raw[562132:])
    print("  562132 起无限制解压 -> %d 字节, 消耗 %d" % (len(out), used))
