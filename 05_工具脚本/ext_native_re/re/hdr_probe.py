import glob
import os
from collections import defaultdict

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
fs = sorted(glob.glob(os.path.join(BASE, "*.wmv")), key=os.path.getsize)


def hx(b):
    return ' '.join('%02x' % c for c in b)


rows = []
for f in fs:
    d = open(f, 'rb').read(0x60)
    rows.append((os.path.getsize(f), os.path.basename(f), d))

print("=== 最小的 12 个 ===")
for sz, n, d in rows[:12]:
    print("%9d  0x14-0x23: %-47s | 0x32-0x35: %s" %
          (sz, hx(d[0x14:0x24]), hx(d[0x32:0x36])))

print()
print("=== 最大的 8 个 ===")
for sz, n, d in rows[-8:]:
    print("%9d  0x14-0x23: %-47s | 0x32-0x35: %s" %
          (sz, hx(d[0x14:0x24]), hx(d[0x32:0x36])))

print()
print("=== 0x32-0x35 == '6d 72 30 6b' (mr0k) 的包 ===")
for sz, n, d in rows:
    if d[0x32:0x36] == b'mr0k':
        print("%9d  %s  0x14-0x23: %s" % (sz, n, hx(d[0x14:0x24])))

print()
print("=== 0x14 的两种取值 ===")
for sz, n, d in rows:
    if d[0x14] != 0x3b:
        print("  %02x  %9d  %s" % (d[0x14], sz, n))

print()
print("=== 检查：0x15..0x17 与文件大小的关系 ===")
print("size_hex    0x15 0x16 0x17   0x1a 0x1b  0x1e 0x1f")
for sz, n, d in rows[:24]:
    print("%08x    %02x   %02x   %02x     %02x   %02x    %02x   %02x" %
          (sz, d[0x15], d[0x16], d[0x17], d[0x1a], d[0x1b], d[0x1e], d[0x1f]))

print()
print("=== 高位锁定统计 ===")
for i in range(0x14, 0x24):
    hi = set(d[i] >> 4 for _, _, d in rows)
    lo = set(d[i] & 15 for _, _, d in rows)
    print("  0x%02x  hi_nib%02d  lo_nib%02d  uniq%02d" % (i, len(hi), len(lo),
                                                        len(set(d[i] for _, _, d in rows))))
