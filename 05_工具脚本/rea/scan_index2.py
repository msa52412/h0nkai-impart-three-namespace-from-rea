# -*- coding: utf-8 -*-
"""补全资产索引：每个 .wmv 只读前 3MB，用 CAB- 锚点解出 SerializedFile，抽路径字符串"""
import os, re, sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4block import lz4_block_decompress

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
OUT = r"D:/Carol-start/_rea/asb_index2.tsv"
LIMIT = 3 * 1024 * 1024

PATH_RE = re.compile(rb"[A-Za-z0-9_./\\-]{8,200}\.(?:png|tga|prefab|mat|fbx|anim|asset|unity3d|controller|playable|shader|txt|json|bytes|resS|dat)", re.I)


def bodies(buf):
    """返回解压后的 SerializedFile 列表"""
    out = []
    i = 0
    anchors = []
    while True:
        i = buf.find(b"CAB-", i)
        if i < 0: break
        anchors.append(i); i += 4
    for a in anchors:
        for d in range(30, 90):
            off = a + d
            if off + 40 > len(buf): break
            probe = lz4_block_decompress(buf[off:off+40])
            if len(probe) < 24: continue
            ms, fs, ver, do = struct.unpack_from(">IIII", probe, 0)
            if ver != 17 or not (0 < ms < (1 << 20)) or not (0 < fs < (1 << 26)) or do < ms or do > fs: continue
            body = lz4_block_decompress(buf[off:], stop_at=fs)
            if len(body) != fs: continue
            out.append(body)
            break
    return out


def main():
    files = sorted(f for f in os.listdir(ASB) if f.endswith(".wmv"))
    print("共 %d 个包" % len(files))
    rows = []
    for k, f in enumerate(files):
        p = os.path.join(ASB, f)
        sz = os.path.getsize(p)
        try:
            with open(p, "rb") as fh:
                buf = fh.read(LIMIT)
        except Exception as e:
            rows.append((f, sz, "")); continue
        paths = set()
        try:
            for body in bodies(buf):
                for m in PATH_RE.finditer(body):
                    s = m.group().decode("utf-8", "replace").replace("\\", "/")
                    if "/" in s and not s.startswith("archive:"):
                        paths.add(s)
        except Exception:
            pass
        rows.append((f, sz, "|".join(sorted(paths))))
        if (k+1) % 50 == 0:
            print("  已处理 %d/%d" % (k+1, len(files)), flush=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("file\tsize\tpaths\n")
        for f, sz, ps in rows:
            fh.write("%s\t%d\t%s\n" % (f, sz, ps))
    hit = sum(1 for _, _, ps in rows if ps)
    print("完成：%d/%d 个包抽到路径 -> %s" % (hit, len(rows), OUT))


if __name__ == "__main__":
    main()
