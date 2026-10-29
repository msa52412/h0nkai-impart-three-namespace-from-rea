"""检查 bundle#848 的 SerializedFile metadata 区（externals / 字符串），
并定位 a760d70e 里 Cover_Title11 的归属 CAB。
"""
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


def load(fn, bidx):
    path = os.path.join(BASE, fn)
    data = open(path, 'rb').read()
    _, bs = K.walk(data=data)
    b = bs[bidx]
    pl = K.bundle_payload(data, b)
    cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")]
    return data, b, pl, cab


print("=" * 90)
data, b, pl, cabs = load("0a95a3510bffb1a31fdef2cae36e8783.wmv", 848)
cab = cabs[0]
seg = pl[cab["offset"]:cab["offset"] + cab["size"]]
h = K.sf_parse(seg)
meta = seg[:h["data_offset"]]
print("bundle#848 CAB=%s  metadata 区 0x10..0x%04x (%d 字节)" %
      (cab["path"], h["data_offset"], len(meta)))
strs = re.findall(rb"[\x20-\x7e]{4,}", meta)
print("metadata 里的可读串 (%d 条):" % len(strs))
for s in strs:
    print("   ", s.decode("ascii", "replace"))

print("\n=== CAB 节点名 ===  (本 bundle 内的 asset 容器)")
for nd in b["nodes"]:
    print("   ", nd["path"], "size=", nd["size"])

print("\n" + "=" * 90)
print("扫描 a760d70e…wmv 的 Cover_Title*")
fn2 = "a760d70e"
files = [f for f in os.listdir(BASE) if f.startswith(fn2)]
print("匹配文件:", files)
if files:
    fn2 = files[0]
    path2 = os.path.join(BASE, fn2)
    sz = os.path.getsize(path2)
    print("%s  %d bytes" % (fn2, sz))
    data2 = open(path2, 'rb').read()
    _, bs2 = K.walk(data=data2)
    print("bundles=%d ok=%d" % (len(bs2), sum(1 for x in bs2 if x["ok"])))
    for bi, bb in enumerate(bs2[:600]):
        if not bb["ok"]:
            print("  bundle#%d 解析失败" % bi)
            continue
        try:
            p2 = K.bundle_payload(data2, bb)
        except Exception as e:
            print("  bundle#%d payload 失败 %s" % (bi, e))
            continue
        for nd in bb["nodes"]:
            if nd["path"].endswith(".resS"):
                continue
            sg = p2[nd["offset"]:nd["offset"] + nd["size"]]
            if b"Cover_Title11" in sg[:200000]:
                print("  hit bundle#%d @%d %s size=%d" %
                      (bi, bb["start"], nd["path"], nd["size"]))
                hh = K.sf_parse(sg)
                print("     对象数=%d dataOffset=%d" % (hh["object_count"], hh["data_offset"]))
                for o in hh["objects"]:
                    if o["name"] in ("Sprite", "Texture2D"):
                        d = K.sf_objdata(hh, sg, o)
                        s, q = rs(d, 0)
                        nm = s.decode("utf-8", "replace") if s else "?"
                        if "Cover" in nm or "cover" in nm:
                            extra = ""
                            if o["name"] == "Texture2D":
                                pp = q + 4 + 1
                                pp = (pp + 3) & ~3
                                w, hgt = struct.unpack_from("<ii", d, pp)
                                extra = " %dx%d" % (w, hgt)
                            print("       %-10s pid=%-22d %-24r%s" %
                                  (o["name"], o["path_id"], nm, extra))
