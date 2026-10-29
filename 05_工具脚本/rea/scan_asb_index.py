# -*- coding: utf-8 -*-
"""扫描全部 .wmv 包，提取包内资源路径，输出清单
   只读每个文件的前 1MB（序列化体很小，够用），快
   用法: python scan_asb_index.py [输出tsv]
"""
import os
import re
import struct
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")
from lz4block import lz4_block_decompress

D = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc"
OUT = sys.argv[1] if len(sys.argv) > 1 else r"D:\Carol-start\_rea\asb_index.tsv"
HEAD = 1 << 20  # 1MB

PATH_RE = re.compile(rb"(?:assets|Assets)/[A-Za-z0-9_./\-]{4,200}")


def parse(raw, filesize):
    i = raw.find(b"CAB-")
    if i < 0:
        return None
    guid = raw[i + 4:i + 36].decode("ascii", "replace")
    base = i + 36
    if base < len(raw) and raw[base] == 0:
        base += 1
    for cand in range(base, min(base + 96, len(raw) - 8)):
        probe = lz4_block_decompress(raw[cand:cand + 64])
        if len(probe) < 8:
            continue
        meta_size, file_size = struct.unpack_from(">II", probe, 0)
        if not (0 < meta_size < (1 << 24) and 0 < file_size < (1 << 28)):
            continue
        body = lz4_block_decompress(raw[cand:], stop_at=file_size)
        if len(body) != file_size:
            continue
        ver, data_off = struct.unpack_from(">II", body, 8)
        return {
            "guid": guid,
            "body_off": cand,
            "body_len": len(body),
            "version": ver,
            "data_offset": data_off,
            "paths": [p.decode("utf-8", "replace") for p in PATH_RE.findall(body)],
            "body": body,
        }
    return None


def main():
    fs = sorted(f for f in os.listdir(D) if f.endswith(".wmv"))
    rows = []
    ok = 0
    for n, f in enumerate(fs):
        p = os.path.join(D, f)
        size = os.path.getsize(p)
        with open(p, "rb") as fh:
            raw = fh.read(HEAD)
        try:
            r = parse(raw, size)
        except Exception:
            r = None
        if r:
            ok += 1
            rows.append((f, size, r["body_len"], r["version"], r["body_off"],
                         "|".join(r["paths"])))
        if (n + 1) % 50 == 0:
            print("  已扫 %d/%d, 成功 %d" % (n + 1, len(fs), ok))
            sys.stdout.flush()

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("file\tsize\tbody\tver\tbodyOff\tpaths\n")
        for row in rows:
            f.write("\t".join(str(x) for x in row) + "\n")
    print("解析成功 %d/%d -> %s" % (ok, len(fs), OUT))


if __name__ == "__main__":
    main()
