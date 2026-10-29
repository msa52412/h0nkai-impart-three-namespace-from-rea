# -*- coding: utf-8 -*-
"""返回 (解压结果, 消耗的输入字节数)"""
import struct

def lz4_ex(src, stop_at=None):
    out = bytearray(); i = 0; n = len(src)
    try:
        while i < n:
            if stop_at is not None and len(out) >= stop_at: break
            token = src[i]; i += 1
            lit = token >> 4
            if lit == 15:
                while i < n:
                    b = src[i]; i += 1; lit += b
                    if b != 255: break
            if lit:
                if i + lit > n: lit = n - i
                out += src[i:i + lit]; i += lit
            if i >= n: break
            if stop_at is not None and len(out) >= stop_at: break
            if i + 2 > n: break
            off = src[i] | (src[i+1] << 8); i += 2
            if off == 0 or off > len(out): raise ValueError("bad off")
            ml = token & 0x0F
            if ml == 15:
                while i < n:
                    b = src[i]; i += 1; ml += b
                    if b != 255: break
            ml += 4
            st = len(out) - off
            for k in range(ml): out.append(out[st + k])
    except ValueError:
        pass
    if stop_at is not None and len(out) > stop_at:
        out = out[:stop_at]
    return bytes(out), i
