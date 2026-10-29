"""对比 260x56 迪拉克之海 与 204x56 Cover_Title7 的字形度量。"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K

import numpy as np
from PIL import Image

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"


def rs(b, p):
    n = struct.unpack_from("<i", b, p)[0]
    if n < 0 or n > 4096 or p + 4 + n > len(b):
        return None, p
    return b[p + 4:p + 4 + n], (p + 4 + n + 3) & ~3


def find_bundle(data, off):
    i = data.find(b"UnityFS\0")
    while 0 <= i <= off:
        b = K.try_bundle(data, i)
        if b and b["start"] <= off < b["start"] + b["total"]:
            return b
        i = data.find(b"UnityFS\0", i + 1)
    return None


def texs(fn, off_hint, bidx=None):
    data = open(os.path.join(BASE, fn), 'rb').read()
    if bidx is None:
        b = find_bundle(data, off_hint)
    else:
        _, allb = K.walk(data=data)
        b = allb[bidx]
    pl = K.bundle_payload(data, b)
    cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")][0]
    res = [nd for nd in b["nodes"] if nd["path"].endswith(".resS")][0]
    seg = pl[cab["offset"]:cab["offset"] + cab["size"]]
    h = K.sf_parse(seg)
    out = {}
    for o in h["objects"]:
        if o["name"] != "Texture2D":
            continue
        d = K.sf_objdata(h, seg, o)
        s, q = rs(d, 0)
        if s is None:
            continue
        nm = s.decode("utf-8", "replace")
        p = (q + 4 + 1 + 3) & ~3
        w, hh = struct.unpack_from("<ii", d, p); p += 8
        cis = struct.unpack_from("<i", d, p)[0]; p += 4
        tf = struct.unpack_from("<i", d, p)[0]
        q2 = d.find(b"archive:/")
        off = struct.unpack_from("<I", d, q2 - 12)[0]
        raw = pl[res["offset"] + off: res["offset"] + off + cis]
        if tf == 4 and len(raw) >= w * hh * 4:
            # Unity 底部朝上 -> 翻转成正立
            arr = np.frombuffer(raw[:w * hh * 4], np.uint8).reshape(hh, w, 4)
            out[nm] = np.flipud(arr).copy()
    return out


def metrics(a, name):
    al = a[:, :, 3].astype(np.int32)
    ys, xs = np.where(al > 8)
    if len(ys) == 0:
        print("%-16s 全透明" % name)
        return
    print("%-16s %dx%d  bbox x=[%d,%d] y=[%d,%d]  w=%d h=%d  alpha>8 占比=%.3f  max=%d" %
          (name, a.shape[1], a.shape[0], xs.min(), xs.max(), ys.min(), ys.max(),
           xs.max() - xs.min() + 1, ys.max() - ys.min() + 1,
           (al > 8).mean(), al.max()))
    # 每列是否有内容，用于观察字间距
    col = (al > 8).any(0)
    runs = []
    s = None
    for i, v in enumerate(col):
        if v and s is None:
            s = i
        elif not v and s is not None:
            runs.append((s, i - 1)); s = None
    if s is not None:
        runs.append((s, len(col) - 1))
    print("                 列游程: %s" % runs)


d = texs("10d8f3adca3f6d9c0c321cbcf89c72b0.wmv", 31806037)
c = texs("0a95a3510bffb1a31fdef2cae36e8783.wmv", 21042500, 848)
print("迪拉克源:", list(d.keys()))
print("目标:", list(c.keys()))
for k, v in d.items():
    metrics(v, "SRC " + k)
for k, v in c.items():
    metrics(v, "TGT " + k)
