"""测量：真实 block 的 csize vs 重编码长度，评估等长重编码余量。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K
import lz4repack as L

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"

CASES = [
    "426491342dde4dcdb8afbb3b895051e6.wmv",
    "2b869220f02125f5f74351dc3738788e.wmv",
    "0a95a3510bffb1a31fdef2cae36e8783.wmv",
]

for fn in CASES:
    path = os.path.join(BASE, fn)
    data = open(path, 'rb').read()
    _, bs = K.walk(data=data)
    print("=" * 100)
    print("%s  %d bytes  bundles=%d (ok=%d)" %
          (fn, len(data), len(bs), sum(1 for b in bs if b["ok"])))
    # 只看前几个 bundle 的每个 block
    shown = 0
    for b in bs[:6]:
        if not b["ok"]:
            print("  !! bundle@%d 解析失败" % b["start"])
            continue
        p = b["data_start"]
        for bi, (usize, csize, flags) in enumerate(b["blocks"]):
            if flags not in (2, 3):
                print("  bundle@%-9d blk%d usize=%-8d csize=%-8d flags=%d (未压缩)" %
                      (b["start"], bi, usize, csize, flags))
                p += csize
                continue
            chunk = data[p:p + csize]
            pl, used, clean, _, _ = K.lz4_decode(chunk, b"")
            ratios = []
            for mm, ch in ((4, 1), (4, 4), (4, 16), (5, 8), (6, 8), (8, 4)):
                sq = L.encode(pl, min_match=mm, chain=ch)
                ratios.append((mm, ch, len(L.build(sq))))
            best = min(r[2] for r in ratios)
            print("  bundle@%-9d blk%d usize=%-8d csize=%-8d 重编码最好=%d (%+d) 各档=%s" %
                  (b["start"], bi, usize, csize, best, best - csize,
                   ",".join("%d/%d:%d" % r for r in ratios)))
            p += csize
            shown += 1
            if shown >= 10:
                break
        if shown >= 10:
            break
