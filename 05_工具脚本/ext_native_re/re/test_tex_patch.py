"""端到端：修改 bundle#848 里 Cover_Title7 的像素 -> 重打包 -> 导出验证。"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K
import repack as R

from PIL import Image

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
FN = "0a95a3510bffb1a31fdef2cae36e8783.wmv"
BIDX = 848
OUT = r"D:/BH3/7.0/_ext/tmp"


def rs(b, p):
    n = struct.unpack_from("<i", b, p)[0]
    if n < 0 or n > 4096 or p + 4 + n > len(b):
        return None, p
    return b[p + 4:p + 4 + n], (p + 4 + n + 3) & ~3


path = os.path.join(BASE, FN)
data, bs = R.read_file(path)
b = bs[BIDX]
pl = bytearray(K.bundle_payload(data, b))
print("bundle#%d total=%d payload=%d blocks=%s" %
      (BIDX, b["total"], len(pl), [(u, c) for u, c, f in b["blocks"]]))

cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")][0]
res = [nd for nd in b["nodes"] if nd["path"].endswith(".resS")][0]
seg = bytes(pl[cab["offset"]:cab["offset"] + cab["size"]])
h = K.sf_parse(seg)

tex = None
for o in h["objects"]:
    if o["name"] != "Texture2D":
        continue
    d = K.sf_objdata(h, seg, o)
    s, q = rs(d, 0)
    if s and s.decode("utf-8", "replace") == "Cover_Title7":
        tex = (o, d, q)
        break
o, d, q = tex
p = q + 4 + 1
p = (p + 3) & ~3
w, hh = struct.unpack_from("<ii", d, p)
q2 = d.find(b"archive:/")
off, size, plen = struct.unpack_from("<III", d, q2 - 12)
print("Cover_Title7 %dx%d off=%d size=%d" % (w, hh, off, size))

tex_abs = res["offset"] + off
raw = bytes(pl[tex_abs:tex_abs + size])
img = Image.frombytes("RGBA", (w, hh), raw).transpose(Image.FLIP_TOP_BOTTOM)
img.save(os.path.join(OUT, "orig_cover7.png"))

# 画一个红色边框 + 斜线，肉眼可辨
img2 = img.copy()
px = img2.load()
for x in range(w):
    for y in range(hh):
        if x < 2 or x >= w - 2 or y < 2 or y >= hh - 2:
            px[x, y] = (255, 40, 40, 255)
for i in range(min(w, hh)):
    px[i, i] = (0, 255, 120, 255)
raw2 = img2.transpose(Image.FLIP_TOP_BOTTOM).tobytes()
assert len(raw2) == size

new_pl = bytes(pl[:tex_abs]) + raw2 + bytes(pl[tex_abs + size:])
assert len(new_pl) == len(pl)

nb, info = R.repack(data, b, new_pl, verbose=True)
if nb is None:
    print("重打包失败:", info)
    sys.exit(1)
print("重打包: total %d -> %d  bi_len %d -> %d" %
      (info["total"], info["new_total"], info["bi_len"], info["new_bi_len"]))

out = data[:b["start"]] + nb + data[b["start"] + b["total"]:]
outp = os.path.join(OUT, FN + ".patched")
open(outp, 'wb').write(out)
print("写出 %s  %d -> %d bytes" % (outp, len(data), len(out)))

# 复检 + 重新导出
_, bs2 = K.walk(data=out)
print("复检: bundles=%d 失败=%d" % (len(bs2), sum(1 for x in bs2 if not x["ok"])))
b2 = bs2[BIDX]
pl2 = K.bundle_payload(out, b2)
seg2 = pl2[cab["offset"]:cab["offset"] + cab["size"]]
print("payload 一致:", K.bundle_payload(out, b2) == new_pl)
raw3 = pl2[tex_abs:tex_abs + size]
im3 = Image.frombytes("RGBA", (w, hh), raw3).transpose(Image.FLIP_TOP_BOTTOM)
im3.save(os.path.join(OUT, "patched_cover7.png"))
print("像素是否已变:", raw3 != raw)
