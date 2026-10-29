# -*- coding: utf-8 -*-
"""纯 Python LZ4 block 解压（不需要预知解压后大小，输入耗尽即结束）
   Unity 的 AssetBundle 用的是 raw LZ4 block，不是 LZ4 frame
"""


def lz4_block_decompress(src, stop_at=None):
    """stop_at: 解到该字节数就停（Unity 的块后面可能紧跟其它数据）
       解析出错时返回已解出的部分，由调用方按 file_size 校验"""
    out = bytearray()
    i = 0
    n = len(src)
    try:
        while i < n:
            if stop_at is not None and len(out) >= stop_at:
                break
            token = src[i]
            i += 1
            lit = token >> 4
            if lit == 15:
                while i < n:
                    b = src[i]
                    i += 1
                    lit += b
                    if b != 255:
                        break
            if lit:
                if i + lit > n:
                    lit = n - i
                out += src[i:i + lit]
                i += lit
            if i >= n:
                break
            if i + 2 > n:
                break
            offset = src[i] | (src[i + 1] << 8)
            i += 2
            if offset == 0 or offset > len(out):
                raise ValueError("bad offset %d at %d (out=%d)" % (offset, i, len(out)))
            mlen = token & 0x0F
            if mlen == 15:
                while i < n:
                    b = src[i]
                    i += 1
                    mlen += b
                    if b != 255:
                        break
            mlen += 4
            start = len(out) - offset
            for k in range(mlen):
                out.append(out[start + k])
    except ValueError:
        pass
    if stop_at is not None and len(out) > stop_at:
        return bytes(out[:stop_at])
    return bytes(out)


if __name__ == "__main__":
    import sys
    data = open(sys.argv[1], "rb").read()
    off = int(sys.argv[2], 0)
    r = lz4_block_decompress(data[off:])
    print("输入 %d 字节 -> 解压 %d 字节" % (len(data) - off, len(r)))
    print("前 32 字节:", r[:32].hex())
    print("可读:", "".join(chr(c) if 32 <= c < 127 else "." for c in r[:80]))
