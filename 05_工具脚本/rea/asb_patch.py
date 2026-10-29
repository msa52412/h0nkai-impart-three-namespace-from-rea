# -*- coding: utf-8 -*-
"""Asb 包原地补丁器：只改 LZ4 字面量字节，文件尺寸完全不变
   原理：LZ4 字面量是原样拷贝进输出的，所以改压缩流里的字面量字节
        就能改解压后的内容，且不影响任何长度/偏移/容器头
"""
import os
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")


def lz4_decompress_map(src, stop_at):
    """解压并返回 (out, srcmap)
       srcmap[i] = 该输出字节在 src 中的来源下标；-1 表示由拷贝产生"""
    out = bytearray()
    srcmap = []
    i = 0
    n = len(src)
    try:
        while i < n:
            if len(out) >= stop_at:
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
                    lit = n - i
                for k in range(lit):
                    out.append(src[i + k])
                    srcmap.append(i + k)
                i += lit
            if i >= n:
                break
            if i + 2 > n:
                break
            off = src[i] | (src[i + 1] << 8)
            i += 2
            if off == 0 or off > len(out):
                raise ValueError("bad offset")
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
            for k in range(ml):
                out.append(out[st + k])
                srcmap.append(srcmap[st + k] if srcmap[st + k] >= 0 else -1)
    except ValueError:
        pass
    if len(out) > stop_at:
        return bytes(out[:stop_at]), srcmap[:stop_at]
    return bytes(out), srcmap


def patch_block(buf, start, stop_at, newval=0xFF):
    """把该块所有字面量字节改成 newval，返回 (新buf, 改动字节数, 无法改的字节数)"""
    body, smap = lz4_decompress_map(buf[start:], stop_at)
    changed = set()
    skipped = 0
    for pos, s in enumerate(smap):
        if s < 0:
            skipped += 1
            continue
        changed.add(start + s)
    out = bytearray(buf)
    for p in changed:
        out[p] = newval
    return bytes(out), len(changed), skipped, len(body)
