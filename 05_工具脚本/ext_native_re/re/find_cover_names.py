"""在指定 .wmv 里枚举全部 Texture2D 名称，用于确认某张封面图到底存不存在。

用法：
    python find_cover_names.py [wmv文件名] [关键词]

不传参数时默认扫 10d8f3ad...wmv（已知含 Cover_Title8），关键词 Cover。
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"


def read_str(b, p):
    n = struct.unpack_from("<i", b, p)[0]
    if n < 0 or n > 4096 or p + 4 + n > len(b):
        return None, p
    return b[p + 4:p + 4 + n].decode("utf-8", "replace"), (p + 4 + n + 3) & ~3


def tex_name(d):
    """Texture2D 的 m_Name 在对象数据最前面。"""
    s, _ = read_str(d, 0)
    return s


def scan(fn, keyword):
    path = os.path.join(BASE, fn)
    data = open(path, "rb").read()
    _, bundles = K.walk(data=data)
    print(f"{fn}: {len(bundles)} 个 bundle")
    hits = []
    for i, b in enumerate(bundles):
        try:
            payload = K.bundle_payload(data, b)
        except Exception as e:
            continue
        try:
            h = K.sf_parse(payload)
        except Exception:
            continue
        for o in h["objects"]:
            if o["name"] != "Texture2D":
                continue
            d = K.sf_objdata(h, payload, o)
            try:
                nm = tex_name(d)
            except Exception:
                continue
            if nm and keyword.lower() in nm.lower():
                hits.append((i, nm, o["byte_size"]))
    for i, nm, sz in hits:
        print(f"  bundle#{i:<6} {nm:<40} objBytes={sz}")
    if not hits:
        print("  没有命中")
    return hits


if __name__ == "__main__":
    fn = sys.argv[1] if len(sys.argv) > 1 else "10d8f3adca3f6d9c0c321cbcf89c72b0.wmv"
    kw = sys.argv[2] if len(sys.argv) > 2 else "Cover"
    scan(fn, kw)
