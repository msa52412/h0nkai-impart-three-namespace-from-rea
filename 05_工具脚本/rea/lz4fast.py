# -*- coding: utf-8 -*-
"""可提前停止的 LZ4 块解码器（只需要 SerializedFile 元数据时用，跳过 .resS 像素）。"""


def lz4_decode_limit(src, limit):
    """解压 raw LZ4 块，输出达到 limit 字节即停。

    返回 (out_bytes, consumed_input)。数据不足时返回已解出的部分。
    """
    n = len(src)
    i = 0
    out = bytearray()
    while i < n:
        if len(out) >= limit:
            break
        tok = src[i]
        i += 1
        lit = tok >> 4
        if lit == 15:
            while i < n:
                b = src[i]
                i += 1
                lit += b
                if b != 255:
                    break
        if lit:
            if i + lit > n:
                out += src[i:n]
                i = n
                break
            out += src[i:i + lit]
            i += lit
        if i >= n or len(out) >= limit:
            break
        if i + 2 > n:
            break
        off = src[i] | (src[i + 1] << 8)
        i += 2
        if off == 0:
            break
        ml = tok & 0x0F
        if ml == 15:
            while i < n:
                b = src[i]
                i += 1
                ml += b
                if b != 255:
                    break
        ml += 4
        st = len(out) - off
        if st < 0:
            break
        need = min(ml, limit - len(out))
        if need <= 0:
            break
        if off >= need:
            out += out[st:st + need]
        else:
            for k in range(need):
                out.append(out[st + k])
    return bytes(out), i


if __name__ == "__main__":
    import sys
    sys.path.insert(0, r"D:\Carol-start\_rea")
    from lz4src import lz4_srcmap
    p = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc\f65865df27ea6a9e58bf8f1f3b01bdcd.wmv"
    raw = open(p, "rb").read()
    for off in (137, 1301, 3052, 5801, 6833, 8427, 14189):
        full, _, _, _ = lz4_srcmap(raw[off:])
        part, used = lz4_decode_limit(raw[off:], 4096)
        ok = part == full[:len(part)]
        print("off=%-6d full=%-6d part=%-5d 一致=%s" % (off, len(full), len(part), ok))
