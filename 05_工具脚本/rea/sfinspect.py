# -*- coding: utf-8 -*-
"""miHoYo SerializedFile 通用检查器。

用法:
    python sfinspect.py <bundle.wmv> [--off N] [--names] [--dump pathID]

列出类型表、对象表，抽取 GameObject / Transform / MonoBehaviour 的名称，
并可导出指定对象的原始序列化字节。
"""
import os, sys, struct
sys.path.insert(0, r"D:\Carol-start\_rea")
from lz4fast import lz4_decode_limit

ASB = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc"


def find_sfs(raw, max_anchor=600):
    """返回 [(off, fileSize)]"""
    out = []
    i = 0
    n = 0
    while n < max_anchor:
        i = raw.find(b"CAB-", i)
        if i < 0:
            break
        n += 1
        for d in range(32, 32 + 48):
            off = i + d
            h, _ = lz4_decode_limit(raw[off:off + 48], 24)
            if len(h) < 24:
                continue
            ms, fs, ver, do = struct.unpack_from(">IIII", h, 0)
            if ver == 17 and 0 < ms < (1 << 20) and 0 < fs < (1 << 27) and ms <= do <= fs:
                out.append((off, fs))
                break
        i += 4
    return out


def parse(body):
    nt = struct.unpack_from("<i", body, 39)[0]
    types = []
    for k in range(nt):
        cid = struct.unpack_from("<i", body, 43 + k * 23)[0]
        types.append(cid)
    oc_off = 43 + nt * 23
    oc = struct.unpack_from("<i", body, oc_off)[0]
    do = struct.unpack_from("<I", body, 12)[0]
    p = oc_off + 4
    objs = []
    for _ in range(oc):
        pid = struct.unpack_from("<q", body, p)[0]
        bs = struct.unpack_from("<I", body, p + 8)[0]
        bz = struct.unpack_from("<I", body, p + 12)[0]
        tid = struct.unpack_from("<i", body, p + 16)[0]
        objs.append({"pathID": pid, "start": do + bs, "size": bz,
                     "classID": types[tid] if 0 <= tid < len(types) else -1})
        p += 20
    return types, objs, do


def rd_str(b, p, limit=512):
    n = struct.unpack_from("<i", b, p)[0]
    p += 4
    if n < 0 or n > limit:
        raise ValueError("bad len %d" % n)
    s = b[p:p + n].decode("utf-8", "replace")
    return s, p + n + ((-(p + n)) % 4)


def main():
    args = sys.argv[1:]
    name = args[0]
    path = name if os.path.isabs(name) else os.path.join(ASB, name)
    raw = open(path, "rb").read()
    sfs = find_sfs(raw)
    print("文件 %s  %d B  发现 %d 个 SerializedFile" % (os.path.basename(path), len(raw), len(sfs)))
    only_off = None
    if "--off" in args:
        only_off = int(args[args.index("--off") + 1])
    for off, fs in sfs:
        if only_off is not None and off != only_off:
            continue
        body, _ = lz4_decode_limit(raw[off:], fs)
        try:
            types, objs, do = parse(body)
        except Exception as e:
            print("  body@%d 解析失败 %s" % (off, e))
            continue
        print("\n== body@%d  SF=%-8d 类型=%s 对象=%d dataOffset=%d" % (off, fs, types, len(objs), do))
        for o in objs:
            if o["classID"] not in (1, 4, 114, 224):
                continue
            nm = ""
            try:
                nm, _ = rd_str(body, o["start"])
            except Exception:
                pass
            print("   %-9s pathID=%-20d cls=%-4d size=%-6d %r" % (
                {1: "GameObject", 4: "Transform", 114: "MonoBehaviour", 224: "RectTransform"}.get(o["classID"], "?"),
                o["pathID"], o["classID"], o["size"], nm[:60]))
        if "--dump" in args:
            pid = int(args[args.index("--dump") + 1])
            for o in objs:
                if o["pathID"] == pid:
                    seg = body[o["start"]:o["start"] + o["size"]]
                    print("\n-- dump pathID=%d size=%d --" % (pid, o["size"]))
                    print(seg[:2048].hex())
                    break


if __name__ == "__main__":
    main()
