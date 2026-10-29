# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
raw = open(ASB + r"\1be3f3aece7c8e0f08a2768ff33a3af4.wmv", "rb").read()

START = 562136
NEED = 1499136 - 917540   # 剩余像素字节
print("候选原始像素区 %d..%d (%d 字节)" % (START, START+NEED, NEED))
seg = raw[START:START+NEED]
print("长度够:", len(seg) == NEED)
# alpha 检查（每 4 字节第 4 个）
alpha = seg[3::4]
from collections import Counter
c = Counter(alpha)
print("alpha 通道分布 top4:", c.most_common(4))
print("alpha==255 占比: %.1f%%" % (100.0 * c[255] / len(alpha)))
# 若 RGBA，则 1024x366 的剩余部分应是整数行
print("剩余字节/4 =", NEED/4, " 行数 =", NEED/4/1024)
