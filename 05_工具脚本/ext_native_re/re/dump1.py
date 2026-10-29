import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wmv import lz4_decode, HEADER_LEN

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"

def dump(name):
    p = os.path.join(BASE, name)
    d = open(p, 'rb').read()
    print("=" * 90)
    print(name, "len=", len(d))
    for off in range(0, 0x90, 16):
        chunk = d[off:off + 16]
        hx = ' '.join('%02x' % c for c in chunk)
        asc = ''.join(chr(c) if 32 <= c < 127 else '.' for c in chunk)
        print("  %04x  %-47s  |%s|" % (off, hx, asc))
    # decode from 0x36
    out, used, clean, bounds = lz4_decode(d[HEADER_LEN:], bytes(16))
    print("  decode@0x36: out=%d used=%d clean=%s bounds=%s" %
          (len(out), used, clean, bounds[:6]))
    if out:
        o = out[:16]
        print("  prefix16  :", ' '.join('%02x' % c for c in o))
        print("  out[16:48]:", ' '.join('%02x' % c for c in out[16:48]))
    # decode from 0x36 with no prefix
    out2, used2, clean2, b2 = lz4_decode(d[HEADER_LEN:], b"")
    print("  decode@0x36 noprefix: out=%d used=%d clean=%s bounds=%s" %
          (len(out2), used2, clean2, b2[:6]))


for n in ["426491342dde4dcdb8afbb3b895051e6.wmv",
          "fe814a28803e0d370d2392b2136b1f2e.wmv",
          "2b869220f02125f5f74351dc3738788e.wmv"]:
    dump(n)
