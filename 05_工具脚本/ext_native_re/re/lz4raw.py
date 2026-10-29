"""纯 Python LZ4 block 解码器（不依赖 lz4 库，可返回消费的输入字节数）。"""
def lz4_block_decompress(src, max_out=64*1024*1024):
    out = bytearray()
    i = 0
    n = len(src)
    while i < n:
        token = src[i]; i += 1
        lit = token >> 4
        if lit == 15:
            while True:
                if i >= n: return None, i
                b = src[i]; i += 1
                lit += b
                if b != 255: break
        if i + lit > n: return None, i
        out += src[i:i+lit]; i += lit
        if len(out) > max_out: return None, i
        if i >= n: break            # 最后一段只有字面量
        if i + 2 > n: return None, i
        off = src[i] | (src[i+1] << 8); i += 2
        if off == 0 or off > len(out): return None, i
        ml = token & 0x0F
        if ml == 15:
            while True:
                if i >= n: return None, i
                b = src[i]; i += 1
                ml += b
                if b != 255: break
        ml += 4
        start = len(out) - off
        for k in range(ml):
            out.append(out[start + k])
        if len(out) > max_out: return None, i
    return bytes(out), i
