"""从任意 .wmv（含打过补丁的）导出 bundle#848 的全部纹理，做视觉校验。"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K
import dump_covers2 as D

from PIL import Image

OUT = r"D:/BH3/7.0/_ext/tmp/verify"
os.makedirs(OUT, exist_ok=True)

path = sys.argv[1] if len(sys.argv) > 1 else r"D:/BH3/7.0/_ext/tmp/0a95a3510bffb1a31fdef2cae36e8783.wmv.dirac"
tag = sys.argv[2] if len(sys.argv) > 2 else "patched"

data = open(path, 'rb').read()
_, bs = K.walk(data=data)
b = bs[848]
print("%s  bundle@%d total=%d  ok=%s" % (tag, b["start"], b["total"], b["ok"]))
te, h, cab, res, pl = D.tex_entries(data, b) if hasattr(D, "tex_entries") else (None,) * 5

pl = K.bundle_payload(data, b)
cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")][0]
res = [nd for nd in b["nodes"] if nd["path"].endswith(".resS")][0]
seg = pl[cab["offset"]:cab["offset"] + cab["size"]]
h = K.sf_parse(seg)
print("resS size=%d  对象=%d" % (res["size"], h["object_count"]))
for o in h["objects"]:
    if o["name"] != "Texture2D":
        continue
    d = K.sf_objdata(h, seg, o)
    t = D.parse_tex(d)
    if not t or t["off"] is None:
        continue
    raw = pl[res["offset"] + t["off"]:res["offset"] + t["off"] + t["size"]]
    img = D.to_image(raw, t["w"], t["h"], t["fmt"])
    if img is None:
        print("   %-20s %dx%d fmt=%d 跳过" % (t["name"], t["w"], t["h"], t["fmt"]))
        continue
    base = "%s_%s_%dx%d" % (tag, t["name"], t["w"], t["h"])
    bg = Image.new("RGBA", img.size, (40, 44, 52, 255))
    bg.alpha_composite(img)
    bg.convert("RGB").resize((img.width * 2, img.height * 2),
                             Image.LANCZOS).save(os.path.join(OUT, base + ".png"))
    img.transpose(Image.FLIP_TOP_BOTTOM).save(os.path.join(OUT, "raw_" + base + ".png"))
    print("   %-20s %4dx%-4d fmt=%-3d off=%-8d -> %s.png" %
          (t["name"], t["w"], t["h"], t["fmt"], t["off"], base))
