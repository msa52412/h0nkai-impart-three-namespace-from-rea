"""按压缩态偏移定位 bundle，导出其中的 Cover_Title* / ActPic* 纹理。"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K

from PIL import Image

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
OUT = r"D:/BH3/7.0/_ext/tmp/tex"
os.makedirs(OUT, exist_ok=True)

# (文件, 压缩态偏移, 标签)
TASKS = [
    ("10d8f3adca3f6d9c0c321cbcf89c72b0.wmv", 31797393, "t12"),
    ("10d8f3adca3f6d9c0c321cbcf89c72b0.wmv", 31806360, "t8a"),
    ("f5ee331203a685423e94d1bec0bbdb4e.wmv", 47628062, "t5"),
    ("f5ee331203a685423e94d1bec0bbdb4e.wmv", 47637192, "t9a"),
    ("5ca670844a1a73364a8ac9d00bfab2c0.wmv", 19830173, "t9b"),
    ("5ca670844a1a73364a8ac9d00bfab2c0.wmv", 10176465, "quantum"),
    ("6d45a4650aab5060c5c31b5431e37bc8.wmv", 750186, "t8b"),
]


def rs(b, p):
    n = struct.unpack_from("<i", b, p)[0]
    if n < 0 or n > 4096 or p + 4 + n > len(b):
        return None, p
    return b[p + 4:p + 4 + n], (p + 4 + n + 3) & ~3


def parse_tex(d):
    s, q = rs(d, 0)
    if s is None:
        return None
    name = s.decode("utf-8", "replace")
    p = q + 5
    p = (p + 3) & ~3
    w, h = struct.unpack_from("<ii", d, p); p += 8
    cis = struct.unpack_from("<i", d, p)[0]; p += 4
    tf = struct.unpack_from("<i", d, p)[0]
    q2 = d.find(b"archive:/")
    if q2 < 0:
        return {"name": name, "w": w, "h": h, "fmt": tf, "size": cis, "off": None}
    off, size, plen = struct.unpack_from("<III", d, q2 - 12)
    return {"name": name, "w": w, "h": h, "fmt": tf, "size": cis, "off": off}


def find_bundle(data, off):
    p = 0
    while p < len(data):
        b = K.try_bundle(data, p)
        if not b:
            return None
        if b["start"] <= off < b["start"] + b["total"]:
            return b
        p = b["start"] + b["total"]
    return None


cache = {}
for fn, off, tag in TASKS:
    if fn not in cache:
        cache[fn] = open(os.path.join(BASE, fn), 'rb').read()
    data = cache[fn]
    b = find_bundle(data, off)
    if not b:
        print("%-8s %s @%d 定位失败" % (tag, fn[:12], off))
        continue
    pl = K.bundle_payload(data, b)
    cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")]
    if not cab:
        print("%-8s 无 CAB node" % tag)
        continue
    nd0 = cab[0]
    seg = pl[nd0["offset"]:nd0["offset"] + nd0["size"]]
    if seg[:4] != b"\x00\x00\x00\x00" and len(seg) < 64:
        continue
    try:
        h = K.sf_parse(seg)
    except Exception as e:
        print("%-8s sf 解析失败 %s" % (tag, e))
        continue
    print("=" * 90)
    print("%-8s %s bundle@%d  %s  对象=%d" %
          (tag, fn[:12], b["start"], nd0["path"], h["object_count"]))
    res = [nd for nd in b["nodes"] if nd["path"].endswith(".resS")]
    for o in h["objects"]:
        if o["name"] != "Texture2D":
            continue
        d = K.sf_objdata(h, seg, o)
        t = parse_tex(d)
        if not t or t["off"] is None:
            continue
        if not any(k in t["name"] for k in ("Cover", "cover", "ActPic", "Title")):
            continue
        raw = pl[res[0]["offset"] + t["off"]:
                 res[0]["offset"] + t["off"] + t["size"]] if res else b""
        if t["fmt"] != 4 or len(raw) < t["w"] * t["h"] * 4:
            print("   %-24s %dx%d fmt=%d (跳过)" % (t["name"], t["w"], t["h"], t["fmt"]))
            continue
        img = Image.frombytes("RGBA", (t["w"], t["h"]), raw[:t["w"] * t["h"] * 4])
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        o2 = "%s_%s_%dx%d.png" % (tag, t["name"].replace("/", "_"), t["w"], t["h"])
        bg = Image.new("RGBA", img.size, (40, 44, 52, 255))
        bg.alpha_composite(img)
        bg.convert("RGB").resize((img.width * 2, img.height * 2),
                                 Image.LANCZOS).save(os.path.join(OUT, o2))
        print("   %-24s %4dx%-4d -> %s" % (t["name"], t["w"], t["h"], o2))
