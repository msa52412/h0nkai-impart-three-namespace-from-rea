"""反推 SerializedFile 的对象表位置。

对象记录（version 17, 小端）：
  i64 pathID; (align4) u32 byteStart; u32 byteSize; i32 typeID
判据：typeID ∈ [0, typeCount)；byteStart 单调不减且 ∈ [dataOffset, fileSize)；
      byteStart+byteSize ≤ fileSize；count ∈ [1, 200000]。
"""
import struct
import sys

import sf


def scan(path):
    h, data = sf.parse(data=open(path, 'rb').read())
    fs = h["file_size"]
    do = h["data_offset"]
    tc = h["type_count"]
    meta_end = 0x14 + h["metadata_size"]
    print("fileSize=%d dataOffset=%d typeCount=%d metaEnd=0x%x" % (fs, do, tc, meta_end))
    cands = []
    for o in range(0x20, meta_end - 4):
        cnt = struct.unpack_from("<i", data, o)[0]
        if not (0 < cnt <= 200000):
            continue
        p = o + 4
        ok = True
        prev = do
        last_end = 0
        for _ in range(cnt):
            if p + 16 > meta_end:
                ok = False
                break
            # pathID 占 8 字节，随后 align4
            p += 8
            p = (p + 3) & ~3
            if p + 12 > meta_end:
                ok = False
                break
            bs, bz, tid = struct.unpack_from("<IIi", data, p)
            p += 12
            if tid < 0 or tid >= tc:
                ok = False
                break
            if bs < do or bs > fs or bs + bz > fs:
                ok = False
                break
            if bs < prev - 0 and bs != 0:
                ok = False
                break
            prev = bs
            last_end = max(last_end, bs + bz)
        if ok:
            cands.append((o, cnt, p, last_end))
    print("候选对象表起点 %d 个：" % len(cands))
    for o, cnt, end, last_end in cands[:12]:
        print("  @0x%-6x count=%-6d 表尾=0x%-6x 数据末尾=%d  (剩余 metadata %d 字节)" %
              (o, cnt, end, last_end, meta_end - end))
    return h, data, cands


if __name__ == "__main__":
    scan(sys.argv[1])
