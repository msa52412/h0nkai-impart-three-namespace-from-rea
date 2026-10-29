"""把 global-metadata.dat 按熵分块，画出明文/密文地图"""
import math, sys

p = r'BH3_Data/Managed/Metadata/global-metadata.dat'
data = open(p, 'rb').read()
N = len(data)
CHUNK = 4096

def entropy(b):
    if not b: return 0
    counts = [0]*256
    for x in b: counts[x] += 1
    e = 0.0
    n = len(b)
    for c in counts:
        if c:
            p_ = c/n
            e -= p_*math.log2(p_)
    return e

# 分块算熵
rows = []
for off in range(0, N, CHUNK):
    chunk = data[off:off+CHUNK]
    e = entropy(chunk)
    rows.append((off, e))

# 压缩成区间：连续同档(明文<5 / 半明文5-7 / 高熵>7)的块合并
def cls(e): return 'PLAIN' if e < 5.0 else ('MID' if e < 7.0 else 'HIGH')

regions = []
cur_cls, cur_start = None, 0
for off, e in rows:
    c = cls(e)
    if c != cur_cls:
        if cur_cls is not None:
            regions.append((cur_start, off, cur_cls))
        cur_cls, cur_start = c, off
regions.append((cur_start, N, cur_cls))

print(f'文件大小 {N/1048576:.1f} MB，分块 {CHUNK}B 熵扫描：')
print(f'{"区间起始":>12} {"结束":>12} {"大小":>10}  类型')
for s, e, c in regions:
    print(f'{s:>12} {e:>12} {(e-s)/1048576:>8.2f}MB  {c}')
