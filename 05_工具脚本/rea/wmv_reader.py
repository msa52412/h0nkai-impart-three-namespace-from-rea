# -*- coding: utf-8 -*-
"""Asb .wmv 完整解析器
   结构: [自定义头 0x36] [表 24B] [CAB- + 32位hex GUID + NUL] [LZ4 block -> SerializedFile]
   用法: python wmv_reader.py <文件...>
"""
import os
import struct
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")
from lz4block import lz4_block_decompress

D = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc"


class Wmv:
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            self.raw = f.read()

    def locate(self):
        i = self.raw.find(b"CAB-")
        if i < 0:
            raise ValueError("找不到 CAB-")
        self.cab_off = i
        guid = self.raw[i + 4:i + 36]
        self.guid_hex = guid.decode("ascii", "replace")
        # CAB- 头之后可能有额外字段，自动探测真正的 LZ4 起点
        base = i + 36
        if self.raw[base] == 0:
            base += 1
        self.body_off = None
        self.body = None
        for cand in range(base, min(base + 96, len(self.raw) - 8)):
            probe = lz4_block_decompress(self.raw[cand:cand + 64])
            if len(probe) < 8:
                continue
            meta_size, file_size = struct.unpack_from(">II", probe, 0)
            if not (0 < meta_size < (1 << 24) and 0 < file_size < (1 << 28)):
                continue
            full = lz4_block_decompress(self.raw[cand:], stop_at=file_size)
            if len(full) == file_size:
                self.body_off = cand
                self.body = full
                break
        if self.body is None:
            raise ValueError("找不到可解压的 LZ4 体（已试 %d 个起点）" % 96)
        return self

    def header(self):
        b = self.body
        meta_size, file_size, ver, data_off = struct.unpack_from(">IIII", b, 0)
        endian = b[16]
        p = 20
        unity = ""
        if ver >= 22:
            e = b.index(b"\x00", p)
            unity = b[p:e].decode("ascii", "replace")
        return {
            "meta_size": meta_size,
            "file_size": file_size,
            "version": ver,
            "data_offset": data_off,
            "endian": "big" if endian == 0 else "little",
            "unity": unity,
            "body_len": len(b),
            "file_size_match": file_size == len(b),
        }

    def summary(self):
        self.locate()
        h = self.header()
        return {
            "file": os.path.basename(self.path),
            "raw": len(self.raw),
            "cab_off": self.cab_off,
            "guid": self.guid_hex,
            "body_off": self.body_off,
            **h,
        }


def main():
    args = sys.argv[1:] or [
        "426491342dde4dcdb8afbb3b895051e6.wmv",
        "fe814a28803e0d370d2392b2136b1f2e.wmv",
        "2b869220f02125f5f74351dc3738788e.wmv",
    ]
    for a in args:
        p = a if os.path.isabs(a) else os.path.join(D, a)
        try:
            s = Wmv(p).summary()
            print("%-40s raw=%-9d cab@%-6d body=%-8d ver=%-3d data_off=%-6d 匹配=%s"
                  % (s["file"][:38], s["raw"], s["cab_off"], s["body_len"],
                     s["version"], s["data_offset"], s["file_size_match"]))
        except Exception as e:
            print("%-40s 失败: %s" % (os.path.basename(p)[:38], e))


if __name__ == "__main__":
    main()
