# -*- coding: utf-8 -*-
"""解出 excel_output 明文包（按块 LZ4 解压），列出 SerializedFile 对象"""
import sys, os, struct
sys.path.insert(0, r"D:\BH3\7.0\_ext\re")
import wmvkit as w

P = r"D:\BH3\7.0\runtime\web\asset_bundle\overseas01\1.1\data\editor_compressed\data\excel_output_048D75C08DBC4E4884FA09216FE4E7C0C087C702"
OUT = r"D:\Carol-start\_rea\excel_output.bin"

def main():
    d = open(P, "rb").read()
    b = w.try_bundle(d, 0)
    ds = b["data_start"]
    out = bytearray()
    pos = ds
    for i, (usize, csize, flag) in enumerate(b["blocks"]):
        blk = d[pos:pos + csize]
        pos += csize
        dec = w.lz4_decode(blk, max_out=usize)
        if dec is None:
            print("块 %d 解压失败" % i); return
        if len(dec) != usize:
            print("块 %d 长度异常 %d != %d" % (i, len(dec), usize))
        out += dec[:usize]
    print("解压后:", len(out), "期望:", b["nodes"][0]["size"])
    open(OUT, "wb").write(bytes(out))
    print("已写出", OUT)

    sf = w.sf_parse(bytes(out))
    if sf is None:
        print("sf_parse 失败"); return
    print("sf keys:", list(sf.keys()))
    for k, v in sf.items():
        if isinstance(v, list):
            print(" %-16s len=%d" % (k, len(v)))
        elif isinstance(v, (int, str, float)):
            print(" %-16s %s" % (k, v))
    objs = sf.get("objects") or []
    print("\n对象数:", len(objs))
    for i, o in enumerate(objs[:30]):
        print("  #%d %s" % (i, str(o)[:200]))

if __name__ == "__main__":
    main()
