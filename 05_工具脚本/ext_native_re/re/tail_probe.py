import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wmv import lz4_decode

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"


def dump(name, data_start, csize):
    p = os.path.join(BASE, name)
    d = open(p, 'rb').read()
    print("=" * 88)
    print(name, "len=", len(d))
    # 全文件里 UnityFS 出现的位置
    pos = []
    i = d.find(b'UnityFS')
    while i >= 0:
        pos.append(i)
        i = d.find(b'UnityFS', i + 1)
    print("  'UnityFS' 出现位置:", pos[:10])
    tail_from = data_start + csize
    print("  dataStart=0x%x csize=%d -> 尾部起点 0x%x, 尾部长度 %d" %
          (data_start, csize, tail_from, len(d) - tail_from))
    if len(d) > tail_from:
        t = d[tail_from:tail_from + 96]
        print("  尾部前 96 字节:")
        for k in range(0, len(t), 16):
            c = t[k:k + 16]
            print("    +%04x  %-47s |%s|" % (k, ' '.join('%02x' % x for x in c),
                                            ''.join(chr(x) if 32 <= x < 127 else '.' for x in c)))
        # 尾部长度统计
        tail = d[tail_from:]
        print("  尾部 uniq bytes=%d" % len(set(tail)))
        print("  尾部熵(粗略)=%.2f bits/byte" % (
            -sum((tail.count(bytes([b])) / len(tail)) *
                 __import__('math').log2(tail.count(bytes([b])) / len(tail))
                 for b in set(tail) if tail.count(bytes([b])) > 0)))
    # 最后 32 字节
    print("  文件最后 32 字节:", ' '.join('%02x' % x for x in d[-32:]))


dump("426491342dde4dcdb8afbb3b895051e6.wmv", 0x73, 4043)
dump("2b869220f02125f5f74351dc3738788e.wmv", 0x73, 9465)
dump("609586e5ebae25e6d182fda32de453dc.wmv", 0x36 + 90, 103293 + 89611 + 81880 + 65462 + 1166)
