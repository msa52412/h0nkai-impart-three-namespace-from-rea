# -*- coding: utf-8 -*-
"""解析 .wmv 内的 UnityFS 头"""
import struct, sys
sys.path.insert(0, r"D:/Carol-start/_rea")

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()

p = 0
sig = raw[0:8].split(b"\x00")[0]
print("签名:", sig)
p = 8
ver = struct.unpack_from(">I", raw, p)[0]; p += 4
print("格式版本:", ver)
def cstr(b, p):
    e = b.index(b"\x00", p)
    return b[p:e].decode("ascii", "replace"), e + 1
uv, p = cstr(raw, p)
ur, p = cstr(raw, p)
print("unityVersion:", uv, " unityRevision:", ur)
size, cbis, ubis, flags = struct.unpack_from(">qIII", raw, p); p += 20
print("bundleSize=%d compressedBlocksInfoSize=%d uncompressedBlocksInfoSize=%d flags=0x%x" % (size, cbis, ubis, flags))
print("头长度 =", p)
print("\n头部原始 hex[0:160]:")
for r in range(0, 160, 16):
    c = raw[r:r+16]
    print("  %04d  %-47s  %s" % (r, c.hex(), "".join(chr(x) if 32<=x<127 else "." for x in c)))
