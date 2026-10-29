"""二维穷举：流起点 s×前缀长度 P，找能闭合 csize 的规范解。"""
import glob
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wmv import lz4_decode, HEADER_LEN

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"


def parse_bi(buf, s):
    n = len(buf)
    if s + 1 > n:
        return None
    bc = buf[s]
    if not (0 < bc <= 4096):
        return None
    p = s + 1
    blocks = []
    for _ in range(bc):
        if p + 10 > n:
            return None
        usize = int.from_bytes(buf[p:p + 4], 'big')
        csize = int.from_bytes(buf[p + 4:p + 8], 'big')
        flags = int.from_bytes(buf[p + 8:p + 10], 'big')
        if usize == 0 or csize == 0 or usize > (1 << 31) or csize > (1 << 31):
            return None
        if csize > usize:
            return None
        if flags not in (0, 1, 2, 3, 4, 5):
            return None
        blocks.append((usize, csize, flags))
        p += 10
    if p + 4 > n:
        return None
    nc = int.from_bytes(buf[p:p + 4], 'big')
    if not (0 < nc <= 40000):
        return None
    p += 4
    nodes = []
    for _ in range(nc):
        if p + 20 > n:
            return None
        off = int.from_bytes(buf[p:p + 8], 'big')
        size = int.from_bytes(buf[p + 8:p + 16], 'big')
        fl = int.from_bytes(buf[p + 16:p + 20], 'big')
        p += 20
        e = buf.find(b'\0', p)
        if e < 0:
            return None
        path = buf[p:e]
        if not path or len(path) > 512:
            return None
        if not all(32 <= c < 127 for c in path):
            return None
        nodes.append((off, size, fl, path.decode('ascii')))
        p = e + 1
    return {'bc': bc, 'blocks': blocks, 'nc': nc, 'nodes': nodes, 'end': p}


def solve(d, starts, plens):
    fsize = len(d)
    hits = []
    for s in starts:
        for P in plens:
            out, used, clean, bounds = lz4_decode(d[s:], bytes(P), max_out=1 << 20)
            for in_pos, out_len in bounds:
                bi_len = (s - HEADER_LEN) + in_pos
                if bi_len <= 0 or bi_len > 0x20000:
                    continue
                buf = out[:out_len]
                r = parse_bi(buf, P)
                if not r or r['end'] != out_len:
                    continue
                if sum(b[1] for b in r['blocks']) != fsize - HEADER_LEN - bi_len:
                    continue
                hits.append((s - HEADER_LEN, P, bi_len, r))
    return hits


if __name__ == "__main__":
    fs = sorted(glob.glob(os.path.join(BASE, "*.wmv")), key=os.path.getsize)
    starts = list(range(HEADER_LEN, HEADER_LEN + 12))
    plens = [0, 4, 8, 12, 16, 20, 24, 32]
    combo = Counter()
    nok = 0
    detail = []
    for fi, f in enumerate(fs):
        if os.path.getsize(f) > 2 * 1024 * 1024:
            continue
        d = open(f, 'rb').read()
        hits = solve(d, starts, plens)
        if hits:
            nok += 1
            combo[(hits[0][0], hits[0][1])] += 1
            detail.append((os.path.basename(f), len(d), len(hits),
                           [(h[0], h[1], h[2]) for h in hits[:4]]))
        if fi % 40 == 0:
            print("... %d/%d ok=%d" % (fi, len(fs), nok), flush=True)
    print("OK=%d / %d" % (nok, len(fs)))
    print("(s-0x36, P) 分布:", combo.most_common(20))
    print()
    for r in detail[:20]:
        print(r)
