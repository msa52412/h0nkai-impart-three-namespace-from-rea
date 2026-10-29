# -*- coding: utf-8 -*-
import hashlib, os, struct
ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
TARGET = b"f65865df27ea6a9e58bf8f1f3b01bdcd.wmv"
W1 = 0xf65865df27ea6a9e
W2 = 0x58bf8f1f3b01bdcd

for xmf in ("Blocks.xmf", "Blocks_7_0.xmf", "BlockMeta.xmf"):
    p = os.path.join(ASB, xmf)
    d = open(p, "rb").read()
    print("=== %s  size=%d  md5=%s" % (xmf, len(d), hashlib.md5(d).hexdigest()))
    i = d.find(TARGET)
    print("   ASCII 名出现位置:", i)
    if i >= 0:
        s = max(0, i - 32)
        print("   上下文 hex:", d[s:i + 64].hex())
        # 找 w1/w2 大端/小端出现
        for label, pat in (("md51BE", struct.pack(">Q", W1)), ("md51LE", struct.pack("<Q", W1))):
            j = d.find(pat)
            print("   %s 位置: %s" % (label, j))
    print()
