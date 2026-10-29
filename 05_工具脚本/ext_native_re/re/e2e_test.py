"""端到端验证：解析 -> 同长度原地补丁 -> 复检结构完好。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K

CASES = [
    (r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/426491342dde4dcdb8afbb3b895051e6.wmv",
     [b"MonoMoleMole", b"CAB-"]),
    (r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/2b869220f02125f5f74351dc3738788e.wmv",
     [b"Mono", b"CAB-"]),
]


def show_sf(data, b, tag):
    pl = K.bundle_payload(data, b)
    for nd in b["nodes"]:
        if nd["path"].endswith(".resS"):
            continue
        seg = pl[nd["offset"]:nd["offset"] + nd["size"]]
        h = K.sf_parse(seg)
        print("   %s %s: %d 个对象, dataOffset=%d, classes=%d" %
              (tag, nd["path"][:20], h["object_count"], h["data_offset"],
               h["type_count"]))
        # 找第一个 MonoBehaviour 的可读字符串
        for o in h["objects"]:
            if o["name"] == "MonoBehaviour":
                d = K.sf_objdata(h, seg, o)
                strs = [s for s in d.split(b"\0") if len(s) >= 4 and
                        all(32 <= c < 127 for c in s)]
                if strs:
                    print("      MonoBehaviour#%d size=%d 字符串=%r" %
                          (o["path_id"], o["byte_size"], strs[:3]))
                    return seg, h, o, strs
        return seg, h, None, None
    return None, None, None, None


for path, keys in CASES:
    print("=" * 90)
    print(os.path.basename(path))
    data, bs = K.walk(path)
    print("  bundles=%d all_ok=%s" % (len(bs), all(b["ok"] for b in bs)))
    b = bs[0]
    print("  @%d total=%d bi=%d blocks=%d nodes=%d" %
          (b["start"], b["total"], b["bi_len"], b["block_count"], b["node_count"]))
    seg, h, o, strs = show_sf(data, b, "orig")
    if not o:
        continue
    # 选一个字符串做同长度补丁
    target = strs[0]
    new = target[:-1] + (b"Z" if target[-1:] != b"Z" else b"Y")
    payload_off = (0 if b["nodes"][0]["path"].endswith(".resS")
                   else b["nodes"][0]["offset"]) + h["data_offset"] + o["byte_start"]
    idx = seg.find(target, h["data_offset"] + o["byte_start"])
    payload_off = (b["nodes"][0]["offset"]) + idx if not b["nodes"][0]["path"].endswith(".resS") else idx
    print("  目标: %r -> %r  (payload 偏移 %d)" % (target, new, payload_off))
    buf = bytearray(data)
    ok, msg = K.patch_same_length(buf, b, payload_off, target, new)
    print("  补丁:", ok, msg)
    if not ok:
        continue
    good, nb = K.verify_file(path, buf)
    print("  复检: 结构完好=%s bundles=%d 文件长度 %d -> %d" %
          (good, nb, len(data), len(buf)))
    # 补丁后重新解码，确认字符串已变
    _, bs2 = K.walk(data=bytes(buf))
    pl = K.bundle_payload(bytes(buf), bs2[0])
    seg2 = pl[b["nodes"][0]["offset"]:b["nodes"][0]["offset"] + b["nodes"][0]["size"]]
    print("  补丁后 payload 含新串:", new in seg2, " 含旧串:", target in seg2)
    h2 = K.sf_parse(seg2)
    print("  补丁后对象数:", h2["object_count"], " dataOffset:", h2["data_offset"])
    if len(sys.argv) > 1 and sys.argv[1] == "--write":
        out = path.replace(".wmv", ".patched.wmv")
        open(out, 'wb').write(buf)
        print("  已写出:", out)
