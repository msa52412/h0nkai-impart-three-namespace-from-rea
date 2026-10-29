# -*- coding: utf-8 -*-
"""补丁包端到端校验：结构/长度/各块解码结果对比原件"""
import os, sys, hashlib
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4block import lz4_block_decompress

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
NAME = "f65865df27ea6a9e58bf8f1f3b01bdcd.wmv"
ORIG = os.path.join(ASB, NAME)
PATCH = os.path.join(r"D:/Carol-start/_rea/patch_asb", NAME)

a = open(ORIG, "rb").read()
b = open(PATCH, "rb").read()
print("原件 %d 字节 md5=%s" % (len(a), hashlib.md5(a).hexdigest()))
print("补丁 %d 字节 md5=%s" % (len(b), hashlib.md5(b).hexdigest()))
print("长度一致:", len(a) == len(b))

diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
print("差异字节数: %d  范围: %s..%s" % (len(diff), diff[0] if diff else "-", diff[-1] if diff else "-"))

# 结构：CAB- 位置
for tag, buf in (("原件", a), ("补丁", b)):
    pos = []
    i = 0
    while True:
        i = buf.find(b"CAB-", i)
        if i < 0: break
        pos.append(i); i += 4
    print("%s CAB- 位置: %s" % (tag, pos))

# 三个块解码
def blocks(buf):
    out = {}
    for start, size in ((137, 5088), (1245, 5044), (1925, 16898)):
        d = lz4_block_decompress(buf[start:], stop_at=size)
        out[start] = d
    return out

ba, bb = blocks(a), blocks(b)
for s in ba:
    da, db = ba[s], bb[s]
    same = da == db
    print("块 @%-5d 解码 %d/%d 字节  相同=%s" % (s, len(da), len(db), same))
    if not same:
        from collections import Counter
        print("        改后最常见字节:", Counter(db).most_common(2))
