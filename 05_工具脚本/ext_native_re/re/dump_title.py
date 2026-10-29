"""列出 bundle#848 CAB 的完整 externals（带索引），并 dump Cover_Title7 的 Texture2D 字段。"""
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"


def rs(b, p):
    n = struct.unpack_from("<i", b, p)[0]
    if n < 0 or n > 4096 or p + 4 + n > len(b):
        return None, p
    return b[p + 4:p + 4 + n], (p + 4 + n + 3) & ~3


def cab_of(fn, bidx):
    path = os.path.join(BASE, fn)
    data = open(path, 'rb').read()
    _, bs = K.walk(data=data)
    b = bs[bidx]
    pl = K.bundle_payload(data, b)
    cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")][0]
    seg = pl[cab["offset"]:cab["offset"] + cab["size"]]
    return data, b, pl, cab, seg, K.sf_parse(seg)


data, b, pl, cab, seg, h = cab_of("0a95a3510bffb1a31fdef2cae36e8783.wmv", 848)
meta = seg[:h["data_offset"]]
ext = re.findall(rb"archive:/cab-[0-9a-f]{32}/cab-[0-9a-f]{32}", meta)
print("externals 数量:", len(ext))
# externals 在 metadata 里按顺序排列，索引从 1 开始（fileID）
# 找每个串在 meta 中的位置，排序后即为 externals 顺序
pos = []
for m in re.finditer(rb"archive:/cab-([0-9a-f]{32})/cab-([0-9a-f]{32})", meta):
    pos.append((m.start(), m.group(1).decode()))
pos.sort()
for i, (p0, g) in enumerate(pos):
    mark = ""
    if g in ("9d12ad6e8cb18cbeebdff01d80e45c89", "1a091a812f66ddbd55d12f8638adb8d7"):
        mark = "   <<<<<< Cover_Title11 所在 CAB"
    print("  fileID=%-4d cab-%s%s" % (i + 1, g, mark))

print("\n=== Cover_Title7 相关信息 ===")
for o in h["objects"]:
    if o["name"] not in ("Texture2D", "Sprite"):
        continue
    d = K.sf_objdata(h, seg, o)
    s, q = rs(d, 0)
    nm = s.decode("utf-8", "replace") if s else "?"
    if "Cover_Title" not in nm and "EventLab" not in nm:
        continue
    print("\n  %s pid=%d size=%d name=%r" % (o["name"], o["path_id"], o["byte_size"], nm))
    print("    hex:", d.hex())
    if o["name"] == "Texture2D":
        p = q
        fmt = struct.unpack_from("<i", d, p)[0]; p += 4
        ds = d[p]; p += 1
        p = (p + 3) & ~3
        w, hh = struct.unpack_from("<ii", d, p); p += 8
        cis = struct.unpack_from("<i", d, p)[0]; p += 4
        tf = struct.unpack_from("<i", d, p)[0]; p += 4
        print("    forcedFallbackFmt=%d downscale=%d %dx%d completeImageSize=%d textureFormat=%d" %
              (fmt, ds, w, hh, cis, tf))
