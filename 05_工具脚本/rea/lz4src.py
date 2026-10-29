# -*- coding: utf-8 -*-
"""LZ4 解压 + 每个输出字节的“字面量来源”溯源"""

def lz4_srcmap(src):
    out = bytearray()
    src_of = []      # 输出字节 -> 源下标；-1 表示拷贝派生
    origin = []      # 输出字节 -> 最终字面量源下标
    i = 0; n = len(src)
    try:
        while i < n:
            token = src[i]; i += 1
            lit = token >> 4
            if lit == 15:
                while i < n:
                    b = src[i]; i += 1; lit += b
                    if b != 255: break
            if lit:
                if i + lit > n: lit = n - i
                for k in range(lit):
                    out.append(src[i + k]); src_of.append(i + k); origin.append(i + k)
                i += lit
            if i >= n: break
            if i + 2 > n: break
            off = src[i] | (src[i + 1] << 8); i += 2
            if off == 0 or off > len(out): raise ValueError("bad off")
            ml = token & 0x0F
            if ml == 15:
                while i < n:
                    b = src[i]; i += 1; ml += b
                    if b != 255: break
            ml += 4
            st = len(out) - off
            for k in range(ml):
                out.append(out[st + k])
                src_of.append(-1)
                origin.append(origin[st + k])
    except ValueError:
        pass
    return bytes(out), src_of, origin, i
