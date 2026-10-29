"""修正 RectTransform 字段偏移 + dump TitleImgOWE 的 Image 组件。"""
import os
import struct
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
FN = "0a95a3510bffb1a31fdef2cae36e8783.wmv"
BIDX = 848


def rs(b, p):
    n = struct.unpack_from("<i", b, p)[0]
    if n < 0 or n > 4096 or p + 4 + n > len(b):
        return None, p
    return b[p + 4:p + 4 + n], (p + 4 + n + 3) & ~3


data = open(os.path.join(BASE, FN), 'rb').read()
_, bs = K.walk(data=data)
b = bs[BIDX]
pl = K.bundle_payload(data, b)
cab = [nd for nd in b["nodes"] if not nd["path"].endswith(".resS")][0]
seg = pl[cab["offset"]:cab["offset"] + cab["size"]]
h = K.sf_parse(seg)
by = {o["path_id"]: o for o in h["objects"]}
od = {o["path_id"]: K.sf_objdata(h, seg, o) for o in h["objects"]}

print("对象类型分布:", Counter(o["name"] for o in h["objects"]).most_common())

gname = {}
for o in h["objects"]:
    if o["name"] != "GameObject":
        continue
    d = od[o["path_id"]]
    n = struct.unpack_from("<i", d, 0)[0]
    s, _ = rs(d, 4 + n * 12 + 4)
    if s:
        gname[o["path_id"]] = s.decode("utf-8", "replace")

tf = {}
for o in h["objects"]:
    if o["name"] not in ("Transform", "RectTransform"):
        continue
    d = od[o["path_id"]]
    gpid = struct.unpack_from("<q", d, 4)[0]
    p = 12 + 16 + 12 + 12
    cn = struct.unpack_from("<i", d, p)[0]
    p += 4
    kids = [struct.unpack_from("<q", d, p + i * 12 + 4)[0] for i in range(cn)]
    p += cn * 12
    fpid = struct.unpack_from("<q", d, p + 4)[0]
    rt = None
    if o["name"] == "RectTransform":
        q = p + 12
        rt = dict(
            ancmin=struct.unpack_from("<2f", d, q),
            ancmax=struct.unpack_from("<2f", d, q + 8),
            ap=struct.unpack_from("<2f", d, q + 16),
            sd=struct.unpack_from("<2f", d, q + 24),
            piv=struct.unpack_from("<2f", d, q + 32),
        )
    tf[o["path_id"]] = (gpid, fpid, kids, rt)

go2tf = {v[0]: k for k, v in tf.items()}

for gpid, nm in gname.items():
    if nm != "TitleImgOWE":
        continue
    t = go2tf[gpid]
    rt = tf[t][3]
    print("\nTitleImgOWE rect:")
    print("  anchorMin=%s anchorMax=%s anchoredPos=%s sizeDelta=%s pivot=%s" %
          (rt["ancmin"], rt["ancmax"], rt["ap"], rt["sd"], rt["piv"]))
    d = od[gpid]
    n = struct.unpack_from("<i", d, 0)[0]
    for i in range(n):
        cpid = struct.unpack_from("<q", d, 8 + i * 12)[0]
        co = by.get(cpid)
        print("  组件[%d] %s pid=%d size=%d" %
              (i, co["name"] if co else "?", cpid, co["byte_size"] if co else -1))
        if co and co["name"] == "Image":
            cd = od[cpid]
            print("    hex:", cd.hex())
            # 尾部：m_Type(i32) m_PreserveAspect(u8) m_FillCenter(u8) ...
            for off in range(len(cd) - 4, 0, -1):
                pass
        if co and co["name"] == "RectTransform":
            print("    rt.hex:", od[cpid].hex())

# 全 Task_N Cover 的 Image 尺寸（修正后）
print("\n=== 所有名为 TitleImgOWE / TitleImg 的 rect ===")
for gpid, nm in sorted(gname.items(), key=lambda x: x[1]):
    if nm not in ("TitleImgOWE", "TitleImg"):
        continue
    t = go2tf[gpid]
    rt = tf[t][3]
    print("  %-6s sizeDelta=%-16s anchoredPos=%s" % (nm, rt["sd"], rt["ap"]))
