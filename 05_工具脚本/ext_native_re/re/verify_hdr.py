"""验证包头 total 的定点 XOR 公式，并检查 0x19/0x1a 是否编码 csum。

公式（由 hdr_crack 搜索得出）：
  head[0x15] = (total >> 16) & 0xFF ^ 0x9e
  head[0x16] = (total >>  8) & 0xFF ^ 0x77
  head[0x17] = (total >>  0) & 0xFF ^ 0x37
  head[0x18] = (total >> 24) & 0xFF ^ 0x79
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
KEYS = [0x9e, 0x77, 0x37, 0x79]     # 对应 total 字节 2,1,0,3
ORDER = [2, 1, 0, 3]                # head[0x15..0x18] 对应的 total 字节序


def enc_total(total):
    return bytes(((total >> (8 * b)) & 0xFF) ^ k for b, k in zip(ORDER, KEYS))


def dec_total(h):
    v = 0
    for i, (b, k) in enumerate(zip(ORDER, KEYS)):
        v |= (h[0x15 + i] ^ k) << (8 * b)
    return v


ok = bad = 0
samples = []
files = sorted(f for f in os.listdir(BASE) if f.endswith(".wmv"))
for fn in files:
    p = os.path.join(BASE, fn)
    if os.path.getsize(p) > 4 * 1024 * 1024:
        continue
    data = open(p, 'rb').read()
    _, bs = K.walk(data=data)
    for b in bs:
        if not b["ok"]:
            continue
        hd = b["head_raw"]
        if dec_total(hd) == b["total"]:
            ok += 1
        else:
            bad += 1
            if len(samples) < 5:
                samples.append((fn, b["start"], b["total"], dec_total(hd), hd.hex()))
    if ok + bad > 3000:
        break

print("total 公式验证: OK=%d  BAD=%d" % (ok, bad))
for s in samples:
    print("  不匹配:", s)

# 检查 0x19 是否编码 csum / bi_len
print("\n--- 0x19 等位置相关性 ---")
recs = []
for fn in files[:40]:
    p = os.path.join(BASE, fn)
    if os.path.getsize(p) > 2 * 1024 * 1024:
        continue
    data = open(p, 'rb').read()
    _, bs = K.walk(data=data)
    for b in bs:
        if b["ok"]:
            recs.append(b)
print("样本:", len(recs))
for i in range(0x08, 0x36):
    vs = set(b["head_raw"][i] for b in recs)
    if len(vs) == 1:
        continue
    # 试与 csum/bi_len/usum 的字节做 XOR 看是否恒定
    for name, f in (("csum", lambda b: sum(x[1] for x in b["blocks"])),
                    ("bi_len", lambda b: b["bi_len"]),
                    ("usum", lambda b: sum(x[0] for x in b["blocks"]))):
        for j in range(4):
            keys = set(b["head_raw"][i] ^ ((f(b) >> (8 * j)) & 0xFF) for b in recs)
            if len(keys) == 1:
                print("  0x%02x <-> %s 字节%d  XOR 0x%02x" % (i, name, j, keys.pop()))
