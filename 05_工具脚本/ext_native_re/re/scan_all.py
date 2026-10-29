"""对 440 个 .wmv 全量扫描：用 (P=16 零前缀, start=16, bcw=1) 规范形式解 blocksInfo，
统计自洽率，并对失败包做诊断。

自洽判据：
  1) 能解析出 blockCount(1B) + blocks + nodeCount + nodes，path 全 ASCII
  2) sum(csize) == fileSize - 0x36 - bi_len   （数据区长度严格闭合）
  3) 解析末尾 end == 该 LZ4 段解压长度      （blocksInfo 内部无多余字节）
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wmv import lz4_decode, HEADER_LEN

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"


def parse_bi(buf, s, bcw):
    n = len(buf)
    if s + bcw > n:
        return None
    bc = int.from_bytes(buf[s:s + bcw], 'big')
    if not (0 < bc <= 4096):
        return None
    p = s + bcw
    blocks = []
    for _ in range(bc):
        if p + 10 > n:
            return None
        usize = int.from_bytes(buf[p:p + 4], 'big')
        csize = int.from_bytes(buf[p + 4:p + 8], 'big')
        flags = int.from_bytes(buf[p + 8:p + 10], 'big')
        if usize == 0 or csize == 0 or usize > (1 << 31) or csize > (1 << 31):
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


def solve(d, max_bi=0x20000):
    """返回 (bi_len, info, out, out_len) 或 None。"""
    fsize = len(d)
    out, used, clean, bounds = lz4_decode(d[HEADER_LEN:], bytes(16))
    for bi_len, out_len in bounds:
        if bi_len > max_bi:
            break
        buf = out[:out_len]
        r = parse_bi(buf, 16, 1)
        if not r:
            continue
        if r['end'] != out_len:
            continue
        if sum(b[1] for b in r['blocks']) != fsize - HEADER_LEN - bi_len:
            continue
        return bi_len, r, out, out_len
    return None


def main():
    fs = sorted(glob.glob(os.path.join(BASE, "*.wmv")), key=os.path.getsize)
    ok = []
    bad = []
    for f in fs:
        d = open(f, 'rb').read()
        r = solve(d)
        if r:
            ok.append((os.path.basename(f), len(d), r[0], r[1]))
        else:
            bad.append((os.path.basename(f), len(d)))
    print("TOTAL=%d  OK=%d  FAIL=%d" % (len(fs), len(ok), len(bad)))
    print()
    print("--- 成功的包（按大小排序，前 25）---")
    for name, sz, bi_len, info in ok[:25]:
        paths = [n[3] for n in info['nodes']]
        print("%-42s %9d bi=%-6d blk=%-3d node=%-3d %s" %
              (name, sz, bi_len, info['bc'], info['nc'],
               paths[0][:60] if paths else ''))
    print()
    nb = [b for b in ok if b[1] >= 100000]
    print("成功包中 >=100KB 的共 %d 个" % len(nb))
    print()
    print("--- 失败的包（前 25）---")
    for name, sz in bad[:25]:
        print("%-42s %9d" % (name, sz))
    print()
    print("失败包大小区间: %d ~ %d" % (min([b[1] for b in bad], default=0),
                                    max([b[1] for b in bad], default=0)))
    return ok, bad


if __name__ == "__main__":
    main()
