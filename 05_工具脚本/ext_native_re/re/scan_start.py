import glob, os, struct
from lz4lenient import lz4_lenient
base = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
fs = sorted(glob.glob(os.path.join(base, "*.wmv")), key=os.path.getsize)
for f in fs[:2]:
    d = open(f, 'rb').read()
    print("="*80); print(os.path.basename(f), len(d))
    best = []
    for s in range(0x20, 0x80):
        for plen in (0, 16):
            pre = d[s-plen:s] if plen else b''
            out, used, clean = lz4_lenient(d[s:], pre)
            body = out[len(pre):]
            if not body: continue
            pr = sum(1 for c in body if 32 <= c < 127) / len(body)
            cab = body.count(b'CAB-')
            if cab or pr > 0.5:
                best.append((cab, pr, s, plen, len(body), used, clean, body))
    best.sort(key=lambda x: (-x[0], -x[1], -x[4]))
    for cab, pr, s, plen, ln, used, clean, body in best[:8]:
        print("  s=%#04x pre=%d out=%d used=%d clean=%s printable=%.2f cab=%d" % (s, plen, ln, used, clean, pr, cab))
        print("     %s" % ''.join(chr(c) if 32<=c<127 else '.' for c in body[:80]))
