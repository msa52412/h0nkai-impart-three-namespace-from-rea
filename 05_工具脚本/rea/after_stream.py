# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4src import lz4_srcmap

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
raw = open(ASB + r"\1be3f3aece7c8e0f08a2768ff33a3af4.wmv", "rb").read()

for OFF in (199, 3240226):
    body, src_of, origin, used = lz4_srcmap(raw[OFF:])
    print("body@%d: 解压 %d B, 消耗 %d B -> 结束于 %d" % (OFF, len(body), used, OFF + used))
    fs = struct.unpack_from(">I", body, 4)[0]
    print("   SF=%d, 后缀像素=%d" % (fs, len(body) - fs))
    nxt = OFF + used
    print("   之后 64B:", raw[nxt:nxt+64].hex())
    print("   之后可读:", "".join(chr(c) if 32 <= c < 127 else "." for c in raw[nxt:nxt+64]))
