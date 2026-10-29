import glob, os, struct
from lz4raw import lz4_block_decompress

base = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
files = sorted(glob.glob(os.path.join(base, "*.wmv")), key=os.path.getsize)
f = files[0]
data = open(f,'rb').read()
print("file:", os.path.basename(f), len(data))

def looks_like_blocksinfo(b):
    if len(b) < 32: return False
    # i32 blockCount @16 (LE), 之后是 blockCount*10 字节
    cnt = struct.unpack_from('<i', b, 16)[0]
    if not (0 < cnt < 5000): return False
    p = 20 + cnt*10
    if p+4 > len(b): return False
    ncnt = struct.unpack_from('<i', b, p)[0]
    if not (0 < ncnt < 20000): return False
    q = p+4
    paths = 0
    for _ in range(ncnt):
        if q+24 > len(b): return False
        q += 24
        e = b.find(b'\0', q)
        if e < 0 or e == q or e-q > 300: return False
        path = b[q:e]
        if not all(32 <= c < 127 for c in path): return False
        if b'CAB-' in path: paths += 1
        q = e+1
    return paths, ncnt, cnt

for off in range(0x20, 0x80):
    out, used = lz4_block_decompress(data[off:], 32*1024*1024)
    if out is None:
        continue
    r = looks_like_blocksinfo(out)
    tag = "  <== HIT" if r else ""
    print("off=%#04x outlen=%d used=%d first=%s%s" % (off, len(out), used, out[:48].hex(' '), tag))
    if r:
        print("   blocks=%d nodes=%d cab=%d" % (r[2], r[1], r[0]))
