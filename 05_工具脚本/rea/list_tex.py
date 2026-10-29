# -*- coding: utf-8 -*-
"""列出 .wmv 内 SerializedFile 及 Texture2D（用 CAB- 标记快速定位）"""
import sys, os, struct
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4src import lz4_srcmap
from lz4block import lz4_block_decompress

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"


def cab_bodies(raw, win=48):
    """以 CAB- 为锚点找 LZ4 体起点"""
    offs = []
    i = 0
    while True:
        i = raw.find(b"CAB-", i)
        if i < 0: break
        offs.append(i); i += 4
    cands = set()
    for o in offs:
        for d in range(32, 32 + win):
            cands.add(o + d)
    return sorted(cands), offs


def valid_body(raw, off):
    if off + 40 > len(raw): return None
    probe = lz4_block_decompress(raw[off:off+40])
    if len(probe) < 24: return None
    ms, fs, ver, do = struct.unpack_from(">IIII", probe, 0)
    if ver != 17 or not (0 < ms < (1 << 20)) or not (0 < fs < (1 << 26)) or do < ms or do > fs:
        return None
    body, _, _, _ = lz4_srcmap(raw[off:])
    if len(body) < fs: return None
    return body, fs


def rd_str(b, p):
    n = struct.unpack_from("<i", b, p)[0]; p += 4
    if n < 0 or n > 4096: raise ValueError
    s = b[p:p+n].decode("utf-8", "replace"); p += n
    p += (-p) % 4
    return s, p


def main(name):
    raw = open(os.path.join(ASB, name), "rb").read()
    cands, caboffs = cab_bodies(raw)
    print("文件 %s  %d 字节  CAB- 标记 %d 个" % (name, len(raw), len(caboffs)))
    seen = set()
    n = 0
    for off in cands:
        r = valid_body(raw, off)
        if not r: continue
        body, fs = r
        key = (off, fs)
        if key in seen: continue
        seen.add(key)
        try:
            nt = struct.unpack_from("<i", body, 39)[0]
            if not (0 < nt <= 64): continue
            types = [struct.unpack_from("<i", body, 43 + k*23)[0] for k in range(nt)]
            oc_off = 43 + nt*23
            oc = struct.unpack_from("<i", body, oc_off)[0]
            if not (0 <= oc <= 4096): continue
            do = struct.unpack_from(">I", body, 12)[0]
            p = oc_off + 4
            objs = []
            for _ in range(oc):
                pid = struct.unpack_from("<q", body, p)[0]
                bs = struct.unpack_from("<I", body, p+8)[0]
                bz = struct.unpack_from("<I", body, p+12)[0]
                tid = struct.unpack_from("<i", body, p+16)[0]
                objs.append((do+bs, bz, types[tid] if 0 <= tid < len(types) else -1))
                p += 20
        except Exception:
            continue
        n += 1
        print("  body@%-7d SF=%-7d 流总长=%-8d 后缀=%d  类型=%s" % (off, fs, len(body), len(body)-fs, types))
        for st, sz, cls in objs:
            if cls != 28: continue
            try:
                nm, q = rd_str(body, st)
            except Exception:
                continue
            tail = body[q:st+sz]
            k = tail.rfind(b"archive:/")
            ss = None; pth = None
            if k >= 8:
                ln = struct.unpack_from("<i", tail, k-4)[0]
                if 0 < ln <= 512:
                    pth = tail[k:k+ln].decode("utf-8", "replace")
                    ss = struct.unpack_from("<I", tail, k-8)[0]
            dims = ""
            for o2 in range(q, min(q+64, st+sz-8), 4):
                a, b = struct.unpack_from("<ii", body, o2)
                if 1 <= a <= 8192 and 1 <= b <= 8192 and (a*b*4 == ss or a*b*4*2 == ss or a*b == ss):
                    dims = "%dx%d" % (a, b); break
            print("     Texture2D %-28r %-10s streamSize=%-9s 后缀=%d" % (nm, dims, ss, len(body)-fs))
        if n > 30: break
    print("共 %d 个 SerializedFile" % n)


if __name__ == "__main__":
    main(sys.argv[1])
