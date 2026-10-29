"""把「压缩态字节偏移」映射到 bundle，并解出该 bundle 的 payload 与节点。"""
import bisect
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wmv import lz4_decode

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
IDX = r"D:/BH3/7.0/_ext/tmp/wmv_index.json"
OUT = r"D:/BH3/7.0/_ext/unpack"


def payload_of(data, b):
    p = b["data_start"]
    buf = bytearray()
    detail = []
    for usize, csize, flags in b["blocks"]:
        chunk = data[p:p + csize]
        if len(chunk) != csize:
            return None, detail
        if flags in (2, 3):
            d, u, c, _ = lz4_decode(chunk, b"")
            if not c or u != csize:
                return None, detail
            buf += d
        else:
            buf += chunk
        detail.append((p, csize, flags, usize, len(buf)))
        p += csize
    return bytes(buf), detail


def locate(name, key):
    idx = json.load(open(IDX))
    rec = idx[name]
    bs = rec["bundles"]
    path = os.path.join(BASE, name)
    data = open(path, 'rb').read()
    off = data.find(key)
    hits = []
    while off >= 0:
        hits.append(off)
        off = data.find(key, off + 1)
    print("=" * 92)
    print(name, len(data), "bundles=", len(bs), " 关键字", key, "命中", len(hits))
    starts = [b["start"] for b in bs]
    for h in hits[:20]:
        i = bisect.bisect_right(starts, h) - 1
        b = bs[i] if i >= 0 else None
        where = "?"
        if b:
            if h < b["data_start"]:
                where = "blocksInfo"
            else:
                where = "data+%d" % (h - b["data_start"])
        print("   raw@%-9d -> bundle#%d @%d total=%d  %s" %
              (h, i, b["start"] if b else -1, b["total"] if b else -1, where))
    # 解出涉及的 bundle
    done = set()
    for h in hits:
        i = bisect.bisect_right(starts, h) - 1
        if i < 0 or i in done:
            continue
        done.add(i)
        b = bs[i]
        pl, det = payload_of(data, b)
        if pl is None:
            print("   bundle#%d 解压失败" % i)
            continue
        os.makedirs(OUT, exist_ok=True)
        safe = name.replace('.wmv', '')
        for k, nd in enumerate(b["nodes"]):
            seg = pl[nd["offset"]:nd["offset"] + nd["size"]]
            fn = os.path.join(OUT, "%s_b%d_n%d_%s" %
                              (safe, i, k, nd["path"].replace('/', '_')))
            open(fn, 'wb').write(seg)
            print("   bundle#%d node%d %s size=%d -> %s" %
                  (i, k, nd["path"], nd["size"], os.path.basename(fn)))
        if key in pl:
            print("   bundle#%d payload 内含关键字，payload=%d" % (i, len(pl)))


if __name__ == "__main__":
    locate(sys.argv[1], sys.argv[2].encode())
