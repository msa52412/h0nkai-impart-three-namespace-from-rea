import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wmv import lz4_decode

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"

CASES = [
    ("426491342dde4dcdb8afbb3b895051e6.wmv", 0x73, 17240),
    ("2b869220f02125f5f74351dc3738788e.wmv", 0x73, 32556),
    ("fe814a28803e0d370d2392b2136b1f2e.wmv", 0x73, None),
]

for name, start, expect in CASES:
    d = open(os.path.join(BASE, name), 'rb').read()
    print("=" * 80)
    print(name, "len=", len(d), "dataStart=0x%x rest=%d expect=%s" %
          (start, len(d) - start, expect))
    # 从 start 起解码，看能否消费到 EOF
    out, used, clean, bounds = lz4_decode(d[start:], b"", max_out=1 << 26)
    print("  noprefix : out=%d used=%d/%d clean=%s" % (len(out), used, len(d) - start, clean))
    if out and len(out) >= 24:
        print("  head:", ' '.join('%02x' % c for c in out[:24]))
        print("  sf: meta=%d fileSize=%d ver=%d dataOff=%d endian=%d" %
              (int.from_bytes(out[0:4], 'big'), int.from_bytes(out[4:8], 'big'),
               int.from_bytes(out[8:12], 'big'), int.from_bytes(out[12:16], 'big'),
               out[16]))
        print("  unityVer=%r" % out[0x14:0x14 + 20])
    out2, used2, clean2, _ = lz4_decode(d[start:], bytes(16), max_out=1 << 26)
    print("  prefix16 : out=%d used=%d clean=%s" % (len(out2) - 16, used2, clean2))
    if expect:
        print("  expect match:", len(out) == expect)
