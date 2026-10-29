"""攻克包头：46 字节（0x08~0x35）里是否藏有可改的 size 字段。

思路：收集全部 bundle 的 (head_raw, total, bi_len, csum)，然后做穷举相关性搜索：
  若存在位置 i 与数值 v 的字节 j 满足  head[i] ^ vbyte_j  恒定
  则说明该字段是「定点 XOR」变换，可以任意改。
同时直接找明文（BE/LE）匹配。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
IDX = r"D:/BH3/7.0/_ext/tmp/wmv_index.json"


def collect(limit_files=None, limit_bundles=400):
    recs = []
    files = sorted(os.listdir(BASE))
    if limit_files:
        files = files[:limit_files]
    for fn in files:
        if not fn.endswith(".wmv"):
            continue
        path = os.path.join(BASE, fn)
        sz = os.path.getsize(path)
        if sz > 6 * 1024 * 1024:      # 跳过超大文件，避免全读
            continue
        data = open(path, 'rb').read()
        _, bs = K.walk(data=data)
        for b in bs:
            if not b["ok"]:
                continue
            recs.append({
                "head": bytes(b["head_raw"]),
                "total": b["total"],
                "bi_len": b["bi_len"],
                "csum": sum(x[1] for x in b["blocks"]),
                "usum": sum(x[0] for x in b["blocks"]),
                "bc": b["block_count"],
                "nc": b["node_count"],
            })
            if len(recs) >= limit_bundles:
                return recs
    return recs


recs = collect()
print("样本 bundle 数:", len(recs))
if len(recs) < 20:
    print("样本太少")
    sys.exit(0)

FIELDS = [("total", lambda r: r["total"]),
          ("bi_len", lambda r: r["bi_len"]),
          ("csum", lambda r: r["csum"]),
          ("usum", lambda r: r["usum"]),
          ("bc", lambda r: r["bc"]),
          ("nc", lambda r: r["nc"])]

H = [r["head"] for r in recs]          # 54 字节，0..7 是 UnityFS

print("\n--- 1) 直接找明文（BE/LE）---")
hits = 0
for name, f in FIELDS:
    for width in (2, 4, 8):
        for bo in ("big", "little"):
            for i in range(8, 54 - width + 1):
                ok = True
                for r in recs:
                    v = f(r) & ((1 << (8 * width)) - 1)
                    if H[recs.index(r)][i:i + width] != v.to_bytes(width, bo):
                        ok = False
                        break
                if ok:
                    print("  命中 %s width=%d %s @0x%02x" % (name, width, bo, i))
                    hits += 1
print("  明文命中数:", hits)

print("\n--- 2) 定点 XOR 搜索（head[i] ^ vbyte_j 是否恒定）---")
found = []
for name, f in FIELDS:
    for j in range(8):
        vals = [(f(r) >> (8 * j)) & 0xFF for r in recs]
        if len(set(vals)) < 2:
            continue                       # 该字节恒定，无区分度
        for i in range(8, 54):
            keys = set(h[i] ^ vals[k] for k, h in enumerate(H))
            if len(keys) == 1:
                found.append((name, j, i, keys.pop()))
if found:
    for name, j, i, key in found:
        print("  %s 字节%d  <-> head[0x%02x]  XOR key=0x%02x" % (name, j, i, key))
else:
    print("  无定点 XOR")

print("\n--- 3) 每个头部位置的取值复杂度 ---")
for i in range(8, 54):
    vs = set(h[i] for h in H)
    if len(vs) <= 4:
        print("  0x%02x: %d 值  %s" % (i, len(vs), sorted(vs)))
    else:
        print("  0x%02x: %d 值" % (i, len(vs)))

print("\n--- 4) 位置间字节差（是否为置换/差分编码）---")
# 若头部是 y[i] = x[i] ^ keystream[i]，则恒定位置说明明文恒定
# 检查 head[i] ^ head[i+1] 的复杂度
for i in range(8, 53):
    vs = set(h[i] ^ h[i + 1] for h in H)
    if len(vs) <= 3:
        print("  0x%02x^0x%02x: %d 值" % (i, i + 1, len(vs)))
