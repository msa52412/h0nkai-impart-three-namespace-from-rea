# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4block import lz4_block_decompress

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()

def objects(body):
    ms, fs, ver, do = struct.unpack_from(">IIII", body, 0)
    nt = struct.unpack_from("<i", body, 39)[0]
    tstart = 43; tstride = 23
    types = []
    for k in range(nt):
        s = tstart + k*tstride
        types.append(struct.unpack_from("<i", body, s)[0])
    oc_off = tstart + nt*tstride
    oc = struct.unpack_from("<i", body, oc_off)[0]
    p = oc_off + 4
    objs = []
    for _ in range(oc):
        pid = struct.unpack_from("<q", body, p)[0]
        bs = struct.unpack_from("<I", body, p+8)[0]
        bz = struct.unpack_from("<I", body, p+12)[0]
        tid = struct.unpack_from("<i", body, p+16)[0]
        objs.append(dict(pathID=pid, start=do+bs, size=bz, typeID=tid, cls=types[tid]))
        p += 20
    return dict(dataOff=do, fileSize=fs, types=types, objs=objs, body=body)

def rd_str(b, p):
    n = struct.unpack_from("<i", b, p)[0]; p += 4
    s = b[p:p+n].decode("utf-8", "replace"); p += n
    p += (-p) % 4
    return s, p

for OFF in (137, 1301):
    probe = lz4_block_decompress(raw[OFF:OFF+40])
    ms, fs, ver, do = struct.unpack_from(">IIII", probe, 0)
    body = lz4_block_decompress(raw[OFF:], stop_at=fs)
    o = objects(body)
    print("=== body@%d 类型=%s ===" % (OFF, o["types"]))
    for ob in o["objs"]:
        print("   pathID=%-20d cls=%-4d start=%-6d size=%-5d" % (ob["pathID"], ob["cls"], ob["start"], ob["size"]))
        if ob["cls"] != 28: continue
        b = body; p = ob["start"]
        name, p = rd_str(b, p)
        p += 8*2   # 两个 PPtr 猜测：m_CorrespondingSourceObject / m_PrefabInternal
        forced, = struct.unpack_from("<i", b, p); p += 4
        down = b[p]; p += 1; p += (-p) % 4
        w, h = struct.unpack_from("<ii", b, p); p += 8
        cis, = struct.unpack_from("<I", b, p); p += 4
        fmt, = struct.unpack_from("<i", b, p); p += 4
        mip = b[p]; p += 1
        readable = b[p]; p += 1; p += (-p) % 4
        print("     name=%r forced=%d down=%d %dx%d completeImageSize=%d format=%d mip=%d readable=%d" % (
            name, forced, down, w, h, cis, fmt, mip, readable))
        # 剩余字节
        print("     剩余 %d 字节: %s" % (ob["start"]+ob["size"]-p, b[p:ob["start"]+ob["size"]].hex()))
    print()
