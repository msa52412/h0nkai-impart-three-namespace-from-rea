"""用「metadata 必须完整闭合到 0xF25E」反推 Types / Objects / Externals 的边界。"""
import struct
import sys

import sf


def parse_tail(data, p, meta_end):
    """从 p 解析 Externals -> RefTypes -> UserInfo -> AssetBundle，必须正好结束在 meta_end。"""
    try:
        n = struct.unpack_from("<i", data, p)[0]
        if not (0 <= n <= 4096):
            return None
        p += 4
        exts = []
        for _ in range(n):
            e = data.index(b"\0", p)
            tmp = data[p:e]
            p = e + 1
            e = data.index(b"\0", p)
            path = data[p:e]
            p = e + 1
            p += 16
            t = struct.unpack_from("<i", data, p)[0]
            p += 4
            exts.append((tmp.decode('latin1'), path.decode('latin1'), t))
        if p + 4 > meta_end:
            return None
        nref = struct.unpack_from("<i", data, p)[0]
        if not (0 <= nref <= 4096):
            return None
        p += 4
        for _ in range(nref):
            e = data.index(b"\0", p)
            p = e + 1
            p += 16 + 4 + 4
        e = data.index(b"\0", p)
        userinfo = data[p:e]
        p = e + 1
        rest = meta_end - p
        if rest < 0:
            return None
        return {"ext": exts, "nref": nref, "userinfo": userinfo, "rest": rest,
                "end": p}
    except (ValueError, struct.error):
        return None


def scan(path):
    h, data = sf.parse(data=open(path, 'rb').read())
    fs, do, tc = h["file_size"], h["data_offset"], h["type_count"]
    meta_end = 0x14 + h["metadata_size"]
    print("fileSize=%d dataOffset=%d typeCount=%d metaEnd=0x%x" % (fs, do, tc, meta_end))
    best = []
    for o in range(0x20, meta_end - 8):
        cnt = struct.unpack_from("<i", data, o)[0]
        if not (1 <= cnt <= 100000):
            continue
        p = o + 4
        prev = do
        types = []
        ok = True
        maxend = 0
        for _ in range(cnt):
            if p + 20 > meta_end:
                ok = False
                break
            pid = struct.unpack_from("<q", data, p)[0]
            p += 8
            p = (p + 3) & ~3
            bs, bz, tid = struct.unpack_from("<IIi", data, p)
            p += 12
            if tid < 0 or tid >= tc or bs < do or bz == 0 or bs + bz > fs or bs < prev:
                ok = False
                break
            prev = bs
            maxend = max(maxend, bs + bz)
            types.append(tid)
        if not ok or maxend != fs:
            continue
        t = parse_tail(data, p, meta_end)
        if not t:
            continue
        best.append((o, cnt, p, t))
    print("自洽候选 %d 个" % len(best))
    for o, cnt, p, t in best[:6]:
        print("  @0x%-6x count=%-6d 表尾=0x%-6x externals=%d refTypes=%d userinfo=%r rest=%d"
              % (o, cnt, p, len(t["ext"]), t["nref"], t["userinfo"], t["rest"]))
        for x in t["ext"][:8]:
            print("      ext: %r %r type=%d" % x)
    return h, data, best


if __name__ == "__main__":
    scan(sys.argv[1])
