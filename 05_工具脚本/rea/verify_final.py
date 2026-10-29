# -*- coding: utf-8 -*-
import sys, os, hashlib
from collections import Counter
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4src import lz4_srcmap

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
NAME = "f65865df27ea6a9e58bf8f1f3b01bdcd.wmv"
a = open(os.path.join(ASB, NAME + ".orig"), "rb").read()
b = open(os.path.join(r"D:/Carol-start/_rea/patch_asb", NAME), "rb").read()

print("原件 %d B md5=%s" % (len(a), hashlib.md5(a).hexdigest()))
print("补丁 %d B md5=%s" % (len(b), hashlib.md5(b).hexdigest()))
print("长度一致:", len(a) == len(b))
diff = [i for i in range(len(a)) if a[i] != b[i]]
print("差异 %d 字节, 区间 %d..%d\n" % (len(diff), diff[0], diff[-1]))

BODIES = [137, 1301, 3052, 5801, 6833, 8427, 14189]
PX = {137: (5088, 4096), 1301: (5044, 16896)}
allok = True
for off in BODIES:
    oa, _, _, ua = lz4_srcmap(a[off:])
    ob, _, _, ub = lz4_srcmap(b[off:])
    same_len = len(oa) == len(ob)
    if off in PX:
        sfsz, pxsz = PX[off]
        meta_same = oa[:sfsz] == ob[:sfsz]
        px_same = oa[sfsz:sfsz+pxsz] == ob[sfsz:sfsz+pxsz]
        c = Counter(ob[sfsz+i:sfsz+i+4] for i in range(0, min(pxsz, 4096), 4))
        print("body@%-6d 长度 %d/%d 元数据相同=%s 像素改变=%s 消耗 %d/%d" % (
            off, len(oa), len(ob), meta_same, not px_same, ua, ub))
        print("            改后颜色 top3: %s" % [(k.hex(), v) for k, v in c.most_common(3)])
        allok &= meta_same and not px_same and same_len
    else:
        same = oa == ob
        print("body@%-6d 长度 %d/%d 内容完全相同=%s 消耗 %d/%d" % (off, len(oa), len(ob), same, ua, ub))
        allok &= same

print("\n整体校验:", "通过" if allok else "失败")
