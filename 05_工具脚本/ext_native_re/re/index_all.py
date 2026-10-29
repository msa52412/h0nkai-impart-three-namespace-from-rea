"""用 seek 方式遍历 440 个 .wmv（只读每个 bundle 的包头附近），建立节点索引。

产出：D:/BH3/7.0/_ext/tmp/wmv_index.json
  {file: {size, bundles:[{start,total,bi_len,blocks,nodes:[{path,offset,size,flags}]}],
          fails:[start,...]}}
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wmv import lz4_decode

HEADER_LEN = 0x36
MAGIC = b"UnityFS\0"
WIN = 0x36 + 262144        # 每个 bundle 读取窗口


def _u(b, off, n):
    return int.from_bytes(b[off:off + n], 'big')


def parse_bi(buf, s=16):
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
        usize = _u(buf, p, 4)
        csize = _u(buf, p + 4, 4)
        flags = _u(buf, p + 8, 2)
        if usize == 0 or csize == 0 or usize > (1 << 31) or csize > (1 << 31):
            return None
        if flags not in (0, 1, 2, 3, 4, 5):
            return None
        blocks.append([usize, csize, flags])
        p += 10
    if p + 4 > n:
        return None
    nc = _u(buf, p, 4)
    if not (0 < nc <= 40000):
        return None
    p += 4
    nodes = []
    for _ in range(nc):
        if p + 20 > n:
            return None
        off = _u(buf, p, 8)
        size = _u(buf, p + 8, 8)
        fl = _u(buf, p + 16, 4)
        p += 20
        e = buf.find(b"\0", p)
        if e < 0:
            return None
        path = buf[p:e]
        if not path or len(path) > 512 or not all(32 <= c < 127 for c in path):
            return None
        nodes.append({"offset": off, "size": size, "flags": fl,
                      "path": path.decode("ascii")})
        p = e + 1
    return {"block_count": bc, "blocks": blocks, "node_count": nc,
            "nodes": nodes, "end": p}


def try_bundle(fh, p, fsize):
    fh.seek(p)
    buf = fh.read(min(WIN, fsize - p))
    if buf[:8] != MAGIC:
        return None
    out, used, clean, bounds = lz4_decode(buf[HEADER_LEN:], bytes(16), max_out=1 << 20)
    for bi_len, out_len in bounds:
        if bi_len > 1 << 17:
            break
        r = parse_bi(out[:out_len], 16)
        if not r or r["end"] != out_len:
            continue
        total = HEADER_LEN + bi_len + sum(b[1] for b in r["blocks"])
        if p + total > fsize:
            continue
        nxt = p + total
        if nxt != fsize:
            fh.seek(nxt)
            if fh.read(8) != MAGIC:
                continue
        r.update(start=p, bi_len=bi_len, total=total,
                 data_start=p + HEADER_LEN + bi_len,
                 head_raw=buf[:HEADER_LEN].hex())
        return r
    return None


def index_file(path):
    fsize = os.path.getsize(path)
    rec = {"size": fsize, "bundles": [], "fails": []}
    with open(path, 'rb') as fh:
        p = 0
        while p < fsize:
            b = try_bundle(fh, p, fsize)
            if not b:
                rec["fails"].append(p)
                break
            rec["bundles"].append(b)
            p = b["start"] + b["total"]
    return rec


def main():
    base = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
    outdir = r"D:/BH3/7.0/_ext/tmp"
    os.makedirs(outdir, exist_ok=True)
    fs = sorted(glob.glob(os.path.join(base, "*.wmv")), key=os.path.getsize)
    idx = {}
    nb_tot = 0
    nfail = 0
    for i, f in enumerate(fs):
        try:
            rec = index_file(f)
        except Exception as e:
            rec = {"error": repr(e), "bundles": [], "fails": [-1]}
        name = os.path.basename(f)
        idx[name] = rec
        nb_tot += len(rec["bundles"])
        if rec["fails"]:
            nfail += 1
        if i % 20 == 0:
            print("... %d/%d bundles=%d 有失败的文件=%d" % (i, len(fs), nb_tot, nfail), flush=True)
    with open(os.path.join(outdir, "wmv_index.json"), "w", encoding="utf-8") as fp:
        json.dump(idx, fp)
    print()
    print("文件总数=%d  文件级失败=%d  bundle 总数=%d" % (len(fs), nfail, nb_tot))
    print("节点总数=%d" % sum(len(b["nodes"]) for r in idx.values() for b in r["bundles"]))
    # 特有节点类型统计
    from collections import Counter
    ext = Counter()
    for r in idx.values():
        for b in r["bundles"]:
            for nd in b["nodes"]:
                pa = nd["path"]
                ext[pa.rsplit('.', 1)[-1] if '.' in pa else '(noext)'] += 1
    print("节点后缀分布:", ext.most_common(15))
    return idx


if __name__ == "__main__":
    main()
