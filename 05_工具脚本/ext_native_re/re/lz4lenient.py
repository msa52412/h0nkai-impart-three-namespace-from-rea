def lz4_lenient(src, prefix=b'', max_out=8*1024*1024):
    """宽容版：出错即停，返回已解出的数据 + 消费字节数 + 是否正常结束。"""
    out = bytearray(prefix)
    base = len(prefix)
    produced = 0
    i = 0
    n = len(src)
    clean = False
    while i < n:
        token = src[i]; i += 1
        lit = token >> 4
        if lit == 15:
            while True:
                if i >= n: return bytes(out), i, False
                b = src[i]; i += 1
                lit += b
                if b != 255: break
        if i + lit > n: return bytes(out), i, False
        out += src[i:i+lit]; i += lit
        produced += lit
        if len(out) - base > max_out: return bytes(out), i, False
        if i >= n:
            clean = True
            break
        if i + 2 > n: return bytes(out), i, False
        off = src[i] | (src[i+1] << 8); i += 2
        if off == 0 or off > len(out): return bytes(out), i, False
        ml = (token & 0x0F) + 4
        if (token & 0x0F) == 15:
            while True:
                if i >= n: return bytes(out), i, False
                b = src[i]; i += 1
                ml += b
                if b != 255: break
        st = len(out) - off
        for k in range(ml):
            out.append(out[st + k])
        produced += ml
    return bytes(out), i, clean
