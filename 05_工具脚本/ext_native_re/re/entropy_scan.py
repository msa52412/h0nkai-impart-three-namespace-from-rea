import os, glob, collections
base = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
files = sorted(glob.glob(os.path.join(base, "*.wmv")))
N = 0x100
cols = [collections.Counter() for _ in range(N)]
samples = []
for f in files:
    with open(f,'rb') as fh:
        h = fh.read(N)
    if len(h) < N: continue
    N2 = N
    samples.append((os.path.basename(f), os.path.getsize(f), h))
    for i in range(N2):
        cols[i][h[i]] += 1
print("files scanned:", len(samples))
print("off   uniq  top-byte(count)   hexdump-of-common")
for i in range(0, N):
    c = cols[i]
    u = len(c)
    top, cnt = c.most_common(1)[0]
    print("%#04x  %3d   %02x(%3d)   %s" % (i, u, top, cnt, " ".join("%02x"%top for _ in range(1))), end="")
    # 也打印该列最常见的 4 个值
    print("   common:", " ".join("%02x:%d"%(v,n) for v,n in c.most_common(4)))
