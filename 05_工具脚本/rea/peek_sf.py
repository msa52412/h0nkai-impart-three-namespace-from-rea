# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4block import lz4_block_decompress

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()
body = lz4_block_decompress(raw[137:], stop_at=5088)
print("body len", len(body))
print("\n=== body[0:200] ===")
for r in range(0, 200, 16):
    c = body[r:r+16]
    print("  %04d  %-47s  %s" % (r, c.hex(), "".join(chr(x) if 32<=x<127 else "." for x in c)))

print("\n=== raw[1540:2000] ===")
for r in range(1540, 2000, 16):
    c = raw[r:r+16]
    print("  %05d  %-47s  %s" % (r, c.hex(), "".join(chr(x) if 32<=x<127 else "." for x in c)))
