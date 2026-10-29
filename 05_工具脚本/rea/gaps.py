# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4map2 import lz4_ex

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()
BODIES = [137, 1301, 3052, 5801, 6833, 8427, 14189]

spans = []
for off in BODIES:
    probe, _ = lz4_ex(raw[off:off+40])
    ms, fs, ver, do = struct.unpack_from(">IIII", probe, 0)
    body, used = lz4_ex(raw[off:], stop_at=fs)
    spans.append((off, off + used, fs, len(body)))
    print("body@%-6d 压缩流 %d..%d (%d B) -> 解压 %d" % (off, off, off+used, used, len(body)))

spans.sort()
print("\n=== 未被压缩流覆盖的区间 ===")
cur = 0
for a, b, fs, ln in spans:
    if a > cur:
        gap = raw[cur:a]
        print("  [%5d..%5d] %4d B  前16B=%s  %s" % (cur, a, a-cur, gap[:16].hex(), "".join(chr(c) if 32<=c<127 else "." for c in gap[:40])))
    cur = max(cur, b)
if cur < len(raw):
    gap = raw[cur:]
    print("  [%5d..%5d] %4d B  前16B=%s  %s" % (cur, len(raw), len(raw)-cur, gap[:16].hex(), "".join(chr(c) if 32<=c<127 else "." for c in gap[:40])))
