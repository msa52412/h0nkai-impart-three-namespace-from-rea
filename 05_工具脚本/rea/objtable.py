# -*- coding: utf-8 -*-
"""定位变体 SerializedFile 的对象表。

思路：Unity 写对象表时 pathID 严格递增，且每条记录
(pathID i64, byteStart u32, byteSize u32, typeID i32) 必须落在数据区内。
用「最长 pathID 严格递增的合法记录串」当指纹。
"""
import sys, struct
sys.path.insert(0, r"D:\Carol-start\_rea")
from lz4fast import lz4_decode_limit

BUNDLE = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc\0a95a3510bffb1a31fdef2cae36e8783.wmv"
OFF, FS = 21042663, 412587


def load():
    raw = open(BUNDLE, "rb").read()
    body, _ = lz4_decode_limit(raw[OFF:], FS)
    return body


def find_table(body, do, fs, ntype_max=400):
    best = (0, 0, 0)
    for o in range(100, do - 20, 4):
        p = o
        k = 0
        last_pid = -1
        while p + 20 <= do:
            pid = struct.unpack_from("<q", body, p)[0]
            bs = struct.unpack_from("<I", body, p + 8)[0]
            bz = struct.unpack_from("<I", body, p + 12)[0]
            tid = struct.unpack_from("<i", body, p + 16)[0]
            if not (0 < pid < (1 << 45)) or pid <= last_pid:
                break
            if bz == 0 or do + bs + bz > fs:
                break
            if not (0 <= tid < ntype_max):
                break
            last_pid = pid
            k += 1
            p += 20
        if k > best[0]:
            best = (k, o, p)
    return best


if __name__ == "__main__":
    body = load()
    do = struct.unpack_from(">I", body, 12)[0]
    print("body=%d dataOffset=%d" % (len(body), do))
    k, o, end = find_table(body, do, FS)
    print("最长递增记录串: 条数=%d 起点=%d 终点=%d" % (k, o, end))
    if k:
        print("表前 4 字节 =", struct.unpack_from("<i", body, o - 4)[0] if o >= 4 else None)
        for i in range(min(k, 12)):
            p = o + i * 20
            pid = struct.unpack_from("<q", body, p)[0]
            bs = struct.unpack_from("<I", body, p + 8)[0]
            bz = struct.unpack_from("<I", body, p + 12)[0]
            tid = struct.unpack_from("<i", body, p + 16)[0]
            print("   #%-3d pathID=%-22d start=%-7d size=%-7d type=%-4d" % (i, pid, do + bs, bz, tid))
