# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4block import lz4_block_decompress

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()

for OFF in (137, 1301):
    probe = lz4_block_decompress(raw[OFF:OFF+40])
    ms, fs, ver, do = struct.unpack_from(">IIII", probe, 0)
    body = lz4_block_decompress(raw[OFF:], stop_at=fs)
    print("=== body@%d meta=%d file=%d dataOff=%d ===" % (OFF, ms, fs, do))
    # 类型表
    print("  typeCount@39 =", struct.unpack_from("<i", body, 39)[0])
    for k in range(3):
        s = 43 + k*23
        cid = struct.unpack_from("<i", body, s)[0]
        print("    type%d @%d classID=%d isStripped=%d scriptIdx=%d hash=%s" % (
            k, s, cid, body[s+4], struct.unpack_from("<h", body, s+5)[0], body[s+7:s+23].hex()))
    print("  @112 =", struct.unpack_from("<i", body, 112)[0])
    print("\n  元数据区 112..%d 逐 4 字节 (LE):" % (34+ms))
    for o in range(112, 34+ms, 4):
        v = struct.unpack_from("<I", body, o)[0]
        print("    @%-4d LE=%-12d BE=%-12d hex=%s" % (o, v, struct.unpack_from(">I", body, o)[0], body[o:o+4].hex()))
    print()
