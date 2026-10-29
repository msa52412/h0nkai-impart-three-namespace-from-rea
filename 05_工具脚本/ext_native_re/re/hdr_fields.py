"""用多 bundle 统计法反推包头 46 字节里各 u32 字段的位置与 XOR key。

思路：某偏移上如果编码的是字段 F，那么 raw4 ^ F 对所有 bundle 恒定。
对 bi_len / uncompressed_bi_size / total 分别扫描。
"""
import os
import struct
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K
import repack as R

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
FILES = ["0a95a3510bffb1a31fdef2cae36e8783.wmv",
         "10d8f3adca3f6d9c0c321cbcf89c72b0.wmv",
         "f5ee331203a685423e94d1bec0bbdb4e.wmv"]


def collect(limit=400):
    rows = []
    for fn in FILES:
        data = open(os.path.join(BASE, fn), 'rb').read()
        _, bs = K.walk(data=data)
        for b in bs:
            if not b.get("ok"):
                continue
            body = R.bi_body(data, b)
            rows.append(dict(raw=b["head_raw"][8:54], bi_len=b["bi_len"],
                             bi_u=len(body), total=b["total"],
                             nblocks=len(b["blocks"]), fn=fn))
            if len(rows) >= limit:
                return rows
    return rows


rows = collect()
print("样本 %d 个 bundle" % len(rows))
print("bi_len 取值分布:", Counter(r["bi_len"] for r in rows).most_common(6))
print("bi_u   取值分布:", Counter(r["bi_u"] for r in rows).most_common(6))

FIELDS = {
    "bi_len": lambda r: r["bi_len"],
    "bi_u": lambda r: r["bi_u"],
    "bi_u+16": lambda r: r["bi_u"] + 16,
    "total": lambda r: r["total"],
    "nblocks": lambda r: r["nblocks"],
}

best = {}
for name, fn in FIELDS.items():
    vals = [fn(r) for r in rows]
    if len(set(vals)) < 5:
        print("%-8s 取值种类太少(%d)，跳过" % (name, len(set(vals))))
        continue
    for off in range(0, 46 - 4 + 1):
        for perm in ((0, 1, 2, 3), (3, 2, 1, 0), (2, 1, 0, 3), (1, 0, 3, 2),
                     (0, 2, 1, 3), (3, 1, 0, 2)):
            keys = Counter()
            ok = True
            for r, v in zip(rows, vals):
                raw = r["raw"]
                vb = [(v >> (8 * i)) & 0xFF for i in range(4)]
                k = tuple(raw[off + perm[i]] ^ vb[i] for i in range(4))
                keys[k] += 1
            if len(keys) == 1:
                print("%-8s @%2d perm=%s key=%s  (全部 %d 样本一致)" %
                      (name, off, perm, list(keys)[0], len(rows)))
                best.setdefault(name, (off, perm, list(keys)[0]))
                break
        else:
            continue
        break

print("\n=== 结论 ===")
for k, v in best.items():
    print("  %-8s off=%d perm=%s key=%s" % (k, v[0], v[1], v[2]))
