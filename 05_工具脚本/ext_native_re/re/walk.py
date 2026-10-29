"""不依赖 blocksInfo，直接从数据区扫描并拼接 SerializedFile。"""
import glob, os, struct
from wmv import lz4_decode, HEADER_LEN

def valid_sf_head(b):
    """必须是完整、自洽的 SerializedFile：fileSize 必须等于 buf 长度。"""
    if len(b) < 48: return False
    meta, fsize = struct.unpack_from('>II', b, 0)
    ver = struct.unpack_from('>I', b, 8)[0]
    dataoff = struct.unpack_from('>I', b, 12)[0]
    if not (5 <= ver <= 30): return False
    if fsize != len(b): return False
    if not (0 < meta < fsize): return False
    if not (20 <= dataoff <= fsize): return False
    if not (0x30 <= b[0x14] <= 0x7e): return False   # unityVersion 首字符应是可打印
    return True

def decode_block(data, s):
    """尝试从 s 解一个 LZ4 块；返回 (out, used) 或 None。"""
    if s >= len(data): return None
    out, used, clean, bounds = lz4_decode(data[s:])
    if clean and valid_sf_head(out):
        return out, used
    return None

def walk(path):
    data = open(path, 'rb').read()
    fsize = len(data)
    # 1) 找第一个数据块起点
    start = None
    for s in range(HEADER_LEN, min(fsize - 20, 0x20000)):
        r = decode_block(data, s)
        if r:
            start = s; break
    if start is None:
        return None
    blocks = []
    p = start
    while p < fsize:
        r = decode_block(data, p)
        if not r:
            # 尝试块后半段为补零/垃圾
            break
        out, used = r
        blocks.append((p, used, out))
        p += used
    return {'file': path, 'size': fsize, 'data_start': start,
            'bi_len': start - HEADER_LEN, 'blocks': blocks, 'tail': fsize - p}

base = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
fs = sorted(glob.glob(os.path.join(base, "*.wmv")), key=os.path.getsize)
okc = 0
for f in fs[:12]:
    r = walk(f)
    if not r:
        print("%-40s FAIL" % os.path.basename(f)); continue
    tot = sum(len(b[2]) for b in r['blocks'])
    okc += 1
    print("%-40s len=%-8d dataStart=%#07x biLen=%-5d blocks=%d payload=%-9d tail=%d" %
          (os.path.basename(f), r['size'], r['data_start'], r['bi_len'],
           len(r['blocks']), tot, r['tail']))
