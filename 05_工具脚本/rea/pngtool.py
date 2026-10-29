# -*- coding: utf-8 -*-
import zlib, struct

def write_png(path, w, h, rgba):
    assert len(rgba) == w*h*4, "像素长度不符 %d != %d" % (len(rgba), w*h*4)
    raw = bytearray()
    stride = w*4
    for y in range(h):
        raw.append(0)
        raw += rgba[y*stride:(y+1)*stride]
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += chunk(b"IEND", b"")
    open(path, "wb").write(out)
    return path
