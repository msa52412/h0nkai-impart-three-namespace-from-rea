import glob, os, struct
from wmv import lz4_decode, HEADER_LEN

base = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
fs = sorted(glob.glob(os.path.join(base, "*.wmv")), key=os.path.getsize)

def try_parse(buf, s, bcw):
    n = len(buf)
    if s + bcw > n: return None
    bc = int.from_bytes(buf[s:s+bcw], 'big')
    if not (0 < bc <= 2048): return None
    p = s + bcw
    blocks = []
    for _ in range(bc):
        if p + 10 > n: return None
        usize = int.from_bytes(buf[p:p+4], 'big')
        csize = int.from_bytes(buf[p+4:p+8], 'big')
        flags = int.from_bytes(buf[p+8:p+10], 'big')
        if usize == 0 or csize == 0 or usize > (1<<31) or csize > (1<<31): return None
        blocks.append((usize, csize, flags)); p += 10
    if p + 4 > n: return None
    nc = int.from_bytes(buf[p:p+4], 'big')
    if not (0 < nc <= 20000): return None
    p += 4
    nodes = []
    for _ in range(nc):
        if p + 20 > n: return None
        off = int.from_bytes(buf[p:p+8], 'big')
        size = int.from_bytes(buf[p+8:p+16], 'big')
        fl = int.from_bytes(buf[p+16:p+20], 'big')
        p += 20
        e = buf.find(b'\0', p)
        if e < 0: return None
        path = buf[p:e]
        if not path or len(path) > 400: return None
        if not all(32 <= c < 127 for c in path): return None
        nodes.append((off, size, fl, path.decode('ascii')))
        p = e + 1
    return {'bc': bc, 'blocks': blocks, 'nc': nc, 'nodes': nodes, 'end': p, 's': s, 'bcw': bcw}

for f in fs[:6]:
    d = open(f, 'rb').read(); fsize = len(d)
    print('='*90); print(os.path.basename(f), fsize)
    found = []
    for P in range(0, 25):
        out, used, clean, bounds = lz4_decode(d[HEADER_LEN:], bytes(P))
        for bi_len, out_len in bounds:
            if bi_len > 0x8000: continue
            buf = out[:out_len]
            for s in range(0, 25):
                for bcw in (1, 2, 4):
                    r = try_parse(buf, s, bcw)
                    if not r: continue
                    if sum(b[1] for b in r['blocks']) != fsize - HEADER_LEN - bi_len: continue
                    if r['end'] != out_len: continue
                    found.append((P, bi_len, out_len, s, bcw, r))
    seen = set()
    for P, bi_len, out_len, s, bcw, r in found:
        key = (P, bi_len, s, bcw)
        if key in seen: continue
        seen.add(key)
        print("  P=%-2d bi_len=%-4d out=%-4d start=%-2d bcw=%d | nodes=%d blocks=%s" %
              (P, bi_len, out_len, s, bcw, r['nc'], r['blocks']))
        for nd in r['nodes'][:2]:
            print("        off=%d size=%d flags=%d path=%s" % nd)
