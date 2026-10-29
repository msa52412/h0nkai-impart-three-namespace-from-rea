# -*- coding: utf-8 -*-
"""解析 .wmv 包：定位 CAB- 序列化文件，读 Unity SerializedFile 头
   用法: python parse_wmv.py <文件名或路径>
"""
import os
import struct
import sys

D = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc"


def parse_sf(d, off):
    """在 off 处解析 SerializedFile 头（大端）"""
    if d[off:off + 4] != b"CAB-":
        return None
    p = off + 4
    guid = d[p:p + 16]
    p += 16
    meta_size, file_size, ver, data_off = struct.unpack_from(">IIII", d, p)
    p += 16
    endian = d[p]
    p += 1
    p += 3
    info = {
        "off": off,
        "guid": guid.hex(),
        "meta_size": meta_size,
        "file_size": file_size,
        "version": ver,
        "data_offset": data_off,
        "endian": endian,
    }
    # version >= 22 才有 unity 版本串
    if ver >= 22:
        e = d.index(b"\x00", p)
        info["unity"] = d[p:e].decode("ascii", "replace")
        p = e + 1
        info["header_end"] = p
    return info


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if not arg:
        sys.exit("用法: python parse_wmv.py <文件名>")
    p = arg if os.path.isabs(arg) else os.path.join(D, arg)
    d = open(p, "rb").read()
    print("文件:", os.path.basename(p), "大小:", len(d))

    offs = []
    i = 0
    while True:
        i = d.find(b"CAB-", i)
        if i < 0:
            break
        offs.append(i)
        i += 4
    print("CAB- 出现次数:", len(offs), "前几个偏移:", offs[:6])

    for o in offs[:3]:
        info = parse_sf(d, o)
        if info:
            print("\n[偏移 %d]" % o)
            for k, v in info.items():
                print("   %-12s %s" % (k, v))
            # 校验：file_size 是否等于从 CAB- 到下一个 CAB- 的距离或文件尾
            if info["file_size"] and o + info["file_size"] <= len(d):
                nxt = o + info["file_size"]
                print("   预测文件尾 %d, 该处内容: %r" % (nxt, d[nxt:nxt + 8]))


if __name__ == "__main__":
    main()
