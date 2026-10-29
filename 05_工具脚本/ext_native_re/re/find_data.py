import glob, os, struct
from lz4raw import lz4_block_decompress

base = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
fs = sorted(glob.glob(os.path.join(base, "*.wmv")), key=os.path.getsize)

def valid_sf(b):
    if b is None or len(b) < 20: return None
    meta, fsize = struct.unpack_from('>II', b, 0)
    if fsize != len(b): return None
    ver = struct.unpack_from('>I', b, 8)[0]
    if not (5 <= ver <= 30): return None
    return meta, fsize, ver

rows = []
for f in fs[:25]:
    d = open(f, 'rb').read()
    hit = None
    for s in range(0x30, min(0x400, len(d))):
        out, used = lz4_block_decompress(d[s:], 64*1024*1024)
        if out is None: continue
        if s + used != len(d): continue
        v = valid_sf(out)
        if v:
            hit = (s, v, out)
            break
    if hit:
        s, v, out = hit
        d0 = d[0x36:s]
        rows.append((len(d), s, s-0x36, v[0], v[1], v[2], d0))
        print("%-38s len=%-8d dataStart=%#06x biLen=%-4d meta=%-6d sfSize=%-8d ver=%d" %
              (os.path.basename(f), len(d), s, s-0x36, v[0], v[1], v[2]))
        print("       0x36..: %s" % ' '.join('%02x' % c for c in d0[:48]))
    else:
        print("%-38s len=%-8d NO LZ4 DATA BLOCK FOUND" % (os.path.basename(f), len(d)))
