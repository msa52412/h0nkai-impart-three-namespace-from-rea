"""dump Task_3 链上 RectTransform 的 sizeDelta / anchoredPosition / scale。"""
import os
import struct
import sys

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
        vals = struct.unpack_from("<8f", d, q)
        sd = struct.unpack_from("<2f", d, q + 4 * 4)   # sizeDelta
        ap = struct.unpack_from("<2f", d, q + 4 * 2)   # anchoredPosition
        ancmin = struct.unpack_from("<2f", d, q)
        ancmax = struct.unpack_from("<2f", d, q + 8)
        piv = struct.unpack_from("<2f", d, q + 8 * 4)
        rt = dict(ancmin=ancmin, ancmax=ancmax, ap=ap, sd=sd, piv=piv)
    tf[o["path_id"]] = (gpid, fpid, kids, rt)

go2tf = {v[0]: k for k, v in tf.items()}
gscale = {}
for tpid, (gpid, fpid, kids, rt) in tf.items():
    d = od[tpid]
    gscale[gpid] = struct.unpack_from("<3f", d, 12 + 16 + 12)

sizes = []
for o in h["objects"]:
    if o["name"] == "Image":
        # Image 组件: m_GameObject, m_Enabled, m_Script, m_Material, m_Color, m_RaycastTarget,
        # m_RaycastPadding, m_Maskable, m_OnCullStateChanged, m_Sprite, m_Type, ...
        sizes.append(o["path_id"])


def path_of(gpid, depth=0):
    if depth > 40:
        return []
    t = go2tf.get(gpid)
    if t is None:
        return ["?"]
    father = tf[t][1]
    up = path_of(tf[father][0], depth + 1) if father in tf else []
    return up + [gname.get(gpid, "?")]


def find(name):
    for gpid, nm in gname.items():
        if nm == name:
            yield gpid


print("=== 关键节点 RectTransform ===")
for want in ("Challenge", "Task_3", "Cover", "TitleImgOWE", "TitleImg", "PopUp",
             "VideoUGUI", "Frame", "Line", "Mask"):
    for gpid in list(find(want))[:1]:
        t = go2tf.get(gpid)
        if t is None:
            continue
        rt = tf[t][3]
        pth = "/".join(path_of(gpid))
        sc = gscale.get(gpid, (1, 1, 1))
        print("%-12s %s" % (want, pth))
        if rt:
            print("     sizeDelta=(%.1f, %.1f) anchoredPos=(%.1f, %.1f) scale=(%.2f,%.2f,%.2f)" %
                  (rt["sd"][0], rt["sd"][1], rt["ap"][0], rt["ap"][1], sc[0], sc[1], sc[2]))
            print("     anchorMin=(%.2f,%.2f) anchorMax=(%.2f,%.2f) pivot=(%.2f,%.2f)" %
                  (rt["ancmin"][0], rt["ancmin"][1], rt["ancmax"][0], rt["ancmax"][1],
                   rt["piv"][0], rt["piv"][1]))

# 所有 Task_N 的 Cover 子树尺寸，看是否等宽
print("\n=== 全部 Task_N -> TitleImgOWE 尺寸 ===")
for gpid, nm in sorted(gname.items(), key=lambda x: x[1]):
    if nm != "TitleImgOWE":
        continue
    t = go2tf.get(gpid)
    rt = tf[t][3] if t else None
    pth = "/".join(path_of(gpid))
    if rt:
        print("  %-70s sizeDelta=(%.1f, %.1f)" % (pth, rt["sd"][0], rt["sd"][1]))
