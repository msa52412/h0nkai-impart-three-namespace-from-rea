# -*- coding: utf-8 -*-
"""扫描 blob 字面量池，导出所有可读字符串（含中文优先）
   用法: python scan_blobs.py [out.tsv]
   输出: idx \t byteLen \t text
"""
import sys
import struct
import re

sys.path.insert(0, r"D:\Carol-start\_rea")
from meta_writer import (MetaWriter, TBL_BLOB, DATA_BLOB, M32, M64,
                         key_row, blob_seed, BLOB_STEP)

SRC = r"D:\Carol-start\_rea\work_metadata.dat"
OUT = sys.argv[1] if len(sys.argv) > 1 else r"D:\Carol-start\_rea\blobs_all.tsv"
NROWS = 77396

CJK = re.compile(r"[\u4e00-\u9fff]")


def main():
    w = MetaWriter(SRC)
    buf = w.buf
    rows = []
    for i in range(NROWS):
        off = TBL_BLOB + i * 8
        k = key_row(i)
        o = ((struct.unpack_from("<I", buf, off)[0] ^ 0x2BE4EEE9) - k) & M32
        l = (struct.unpack_from("<I", buf, off + 4)[0] - k - 0x25C2F1A9) & M32
        if l == 0 or l > 4096 or DATA_BLOB + o + l > len(buf):
            continue
        kk = blob_seed(i)
        out = bytearray()
        for q in range((l + 7) >> 3):
            base = DATA_BLOB + o + q * 8
            if base + 8 > len(buf):
                break
            out += (struct.unpack_from("<Q", buf, base)[0] ^ kk).to_bytes(8, "little")
            kk = (kk + BLOB_STEP) & M64
        raw = bytes(out[:l])
        try:
            s = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if not s or "\x00" in s:
            continue
        if not all(ch.isprintable() or ch in "\n\t" for ch in s):
            continue
        rows.append((i, l, s))

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for i, l, s in rows:
            f.write("%d\t%d\t%s\n" % (i, l, s.replace("\n", "\\n").replace("\t", "\\t")))

    cjk = [r for r in rows if CJK.search(r[2])]
    print("可读字面量: %d 条，其中含中文: %d 条 -> %s" % (len(rows), len(cjk), OUT))


if __name__ == "__main__":
    main()
