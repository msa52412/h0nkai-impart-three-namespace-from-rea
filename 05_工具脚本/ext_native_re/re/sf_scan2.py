"""用强不变量定位对象表：对象在数据区里是【紧密排列】的，
即  byteStart[i+1] == align8(byteStart[i] + byteSize[i])  且 byteStart[0] ≈ dataOffset。
"""
import struct
import sys

import sf


def try_at(data, o, cnt, do, fs, meta_end, tc):
    p = o + 4
    prev_end = do
    out = []
    for _ in range(cnt):
        if p + 20 > meta_end:
            return None
        pid = struct.unpack_from("<q", data, p)[0]
        p += 8
        p = (p + 3) & ~3
        bs, bz, tid = struct.unpack_from("<IIi", data, p)
        p += 12
        if tid < 0 or tid >= tc:
            return None
        if bs < do or bz == 0 or bs + bz > fs:
            return None
        if bs != prev_end:
            return None
        prev_end = (bs + bz + 7) & ~7
        out.append((pid, bs, bz, tid))
    return out, p


def scan(path, verbose=True):
    h, data = sf.parse(data=open(path, 'rb').read())
    fs, do, tc = h["file_size"], h["data_offset"], h["type_count"]
    meta_end = 0x14 + h["metadata_size"]
    hits = []
    for o in range(0x20, meta_end - 8):
        # 第一对象必须紧贴 dataOffset
        cnt = struct.unpack_from("<i", data, o)[0]
        if not (1 <= cnt <= 200000):
            continue
        r = try_at(data, o, cnt, do, fs, meta_end, tc)
        if not r:
            continue
        objs, end = r
        hits.append((o, cnt, end, objs[-1][1] + objs[-1][2]))
    hits.sort(key=lambda x: -x[1])
    if verbose:
        print("fileSize=%d dataOffset=%d typeCount=%d metaEnd=0x%x" % (fs, do, tc, meta_end))
        print("命中 %d 个候选（按 count 降序）:" % len(hits))
        for o, cnt, end, last in hits[:8]:
            print("  @0x%-6x count=%-6d 表尾=0x%-6x 末对象结束=%d 余量=%d" %
                  (o, cnt, end, last, meta_end - end))
    return h, data, hits


if __name__ == "__main__":
    scan(sys.argv[1])
