# -*- coding: utf-8 -*-
"""SerializedFile (Unity 2017.4, ver 17) 解析：类型树 + 对象表 + Texture2D 头部"""
import struct, sys, os
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4block import lz4_block_decompress


class R:
    def __init__(self, b, pos=0):
        self.b, self.p = b, pos
    def u8(self):  v = self.b[self.p]; self.p += 1; return v
    def i16(self): v = struct.unpack_from(">h", self.b, self.p)[0]; self.p += 2; return v
    def u16(self): v = struct.unpack_from(">H", self.b, self.p)[0]; self.p += 2; return v
    def i32(self): v = struct.unpack_from(">i", self.b, self.p)[0]; self.p += 4; return v
    def u32(self): v = struct.unpack_from(">I", self.b, self.p)[0]; self.p += 4; return v
    def i64(self): v = struct.unpack_from(">q", self.b, self.p)[0]; self.p += 8; return v
    def f32(self): v = struct.unpack_from(">f", self.b, self.p)[0]; self.p += 4; return v
    def raw(self, n): v = self.b[self.p:self.p + n]; self.p += n; return v
    def align(self, n=4):
        r = self.p % n
        if r: self.p += n - r
    def string(self):
        n = self.i32()
        if n < 0 or n > 65536: raise ValueError("bad string len %d @%d" % (n, self.p - 4))
        s = self.b[self.p:self.p + n].decode("utf-8", "replace")
        self.p += n
        self.align(4)
        return s


def read_typetree(r, ver):
    n = r.i32()
    bufsz = r.i32()
    sbuf = r.raw(bufsz)
    def s_at(off):
        e = sbuf.find(b"\x00", off)
        if e < 0: e = len(sbuf)
        return sbuf[off:e].decode("utf-8", "replace")
    nodes = []
    for _ in range(n):
        d = {}
        d["ver"] = r.u16()
        d["level"] = r.u8()
        d["flags"] = r.u8()
        d["type_off"] = r.u32()
        d["name_off"] = r.u32()
        d["size"] = r.i32()
        d["index"] = r.i32()
        d["meta"] = r.i32()
        if ver >= 19: r.i64()
        nodes.append(d)
    for d in nodes:
        d["type"] = s_at(d["type_off"] & 0x7FFFFFFF)
        d["name"] = s_at(d["name_off"] & 0x7FFFFFFF)
    return nodes


def parse(body, label):
    r = R(body)
    meta_size = r.u32(); file_size = r.u32(); ver = r.u32(); data_off = r.u32()
    endian = r.u8(); r.raw(3)
    print("--- %s ---" % label)
    print("  meta=%d file=%d ver=%d dataOff=%d endian=%d bodyLen=%d" % (meta_size, file_size, ver, data_off, endian, len(body)))
    if ver >= 22:
        e = body.index(b"\x00", r.p); r.p = e + 1
    r.i32()  # target platform
    has_tree = r.u8()
    print("  typeTree=%d" % has_tree)
    types = []
    if has_tree:
        nt = r.i32()
        for _ in range(nt):
            cid = r.i32(); r.u8()
            if ver >= 16: r.i16()
            if cid == 114: r.raw(16)
            if ver >= 21: r.raw(16)
            nodes = read_typetree(r, ver)
            types.append((cid, nodes))
        print("  类型数=%d" % len(types))
        for cid, nodes in types:
            print("    classID=%-6d 节点=%-4d 根=%s" % (cid, len(nodes), nodes[0]["type"] if nodes else "?"))
    oc = r.i32()
    print("  对象数=%d" % oc)
    objs = []
    for _ in range(oc):
        r.align(4)
        pid = r.i64()
        start = r.u32() if ver < 22 else r.i64()
        size = r.u32()
        tid = r.i32()
        objs.append((pid, start, size, tid))
    for pid, start, size, tid in objs:
        tn = types[tid][0]["type"] if 0 <= tid < len(types) else "?"
        print("    pathID=%-6d type=%-16s tid=%-3d start=%-8d size=%-8d" % (pid, tn, tid, start, size))
    return dict(ver=ver, data_off=data_off, types=types, objs=objs, body=body)


if __name__ == "__main__":
    path = sys.argv[1]
    raw = open(path, "rb").read()
    print("文件 %s  %d 字节" % (os.path.basename(path), len(raw)))
    # 枚举所有 CAB- 起点
    offs = []
    i = 0
    while True:
        i = raw.find(b"CAB-", i)
        if i < 0: break
        offs.append(i); i += 4
    print("CAB- 起点:", offs)
    ok = 0
    for o in offs:
        base = o + 36
        if base < len(raw) and raw[base] == 0: base += 1
        for cand in range(base, min(base + 40, len(raw) - 8)):
            probe = lz4_block_decompress(raw[cand:cand + 64])
            if len(probe) < 20: continue
            try:
                ms, fs = struct.unpack_from(">II", probe, 0)
                if not (0 < ms < (1 << 24) and 0 < fs < (1 << 28)): continue
                full = lz4_block_decompress(raw[cand:], stop_at=fs)
                if len(full) != fs: continue
                parse(full, "CAB@%d body@%d" % (o, cand))
                ok += 1
                break
            except Exception as e:
                continue
    print("\n成功解析 %d/%d 个 CAB 段" % (ok, len(offs)))
