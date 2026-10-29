# -*- coding: utf-8 -*-
"""解码 editor_compressed 明文包（mr0k + 16B hash + LZ4 零字典块）"""
import sys
sys.path.insert(0, r"D:\BH3\7.0\_ext\re")
import wmvkit as w

def decode_bundle(path):
    d = open(path, "rb").read()
    b = w.try_bundle(d, 0)
    if not b:
        raise SystemExit("try_bundle 失败")
    pos = b["data_start"]
    out = bytearray()
    info = []
    for i, (usize, csize, flag) in enumerate(b["blocks"]):
        blk = d[pos:pos + csize]
        pos += csize
        if blk[:4] != b"mr0k":
            raise SystemExit("块 %d 头异常: %s" % (i, blk[:8].hex()))
        r = w.lz4_decode(blk[20:], bytes(65536), max_out=1 << 22)
        dec = r[0][65536:]
        info.append((i, usize, csize, len(dec), r[1], r[2]))
        out += dec
    return bytes(out), b, info

if __name__ == "__main__":
    P = sys.argv[1] if len(sys.argv) > 1 else \
        r"D:\BH3\7.0\runtime\web\asset_bundle\overseas01\1.1\data\editor_compressed\data\excel_output_048D75C08DBC4E4884FA09216FE4E7C0C087C702"
    OUT = sys.argv[2] if len(sys.argv) > 2 else r"D:\Carol-start\_rea\excel_output.bin"
    data, b, info = decode_bundle(P)
    for i, usize, csize, n, used, clean in info:
        print("块%d usize=%d csize=%d -> %d used=%d clean=%s" % (i, usize, csize, n, used, clean))
    print("总计:", len(data), "期望:", b["nodes"][0]["size"])
    open(OUT, "wb").write(data)
    print("写出", OUT)
