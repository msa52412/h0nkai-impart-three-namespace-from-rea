# -*- coding: utf-8 -*-
import os
ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
d = open(os.path.join(ASB, "BlockMeta.xmf"), "rb").read()

def dump(off, n=96, base=None):
    base = off if base is None else base
    print("  off=%d" % off)
    for r in range(0, n, 16):
        chunk = d[off+r:off+r+16]
        print("    +%03d  %-47s  %s" % (r, chunk.hex(), "".join(chr(c) if 32 <= c < 127 else "." for c in chunk)))

print("=== 文件头 ===")
dump(0, 96)
print("\n=== idx0 md5 附近 (6021) ===")
dump(6021 - 32, 96, 6021 - 32)
print("\n=== 目标 md5 附近 (11973) ===")
dump(11973 - 32, 96, 11973 - 32)
print("\n=== 文件尾 ===")
dump(len(d) - 96, 96)
