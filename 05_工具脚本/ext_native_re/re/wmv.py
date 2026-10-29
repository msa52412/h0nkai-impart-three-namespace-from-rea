"""BH3 .wmv bundle 解析器（包头已破）。

结构（实测，file 426491342dde... 逐字段验证通过）：
  0x00..0x07  "UnityFS\0"
  0x08..0x35  被米哈游变换过的头字段（46 字节）
  0x36..      blocksInfo（LZ4 流；解压需要 16 字节前置缓冲）
              = hash16 | u32 blockCount | blockCount*(u32 usize,u32 csize,u16 flags)
                | u32 nodeCount | nodeCount*(u64 off,u64 size,u32 flags,path\0)
  ...         数据块（每块独立 LZ4 / LZ4HC，解压后拼成 SerializedFile 序列）

关键点：payload 完全没加密，只有 46 字节包头被变换。
数值字段是大端（BE）。blocksInfo 的 LZ4 流第一条 match 会引用「流开始前」的字节，
必须给解码器一个 16 字节前缀缓冲（内容只影响输出前 16 字节 = hash，不影响后续字段）。
"""
import os
import struct

HEADER_LEN = 0x36
MAGIC = b"UnityFS\0"


# ---------------------------------------------------------------- LZ4
def lz4_decode(src, prefix=b"", max_out=256 * 1024 * 1024, track=False):
    """LZ4 block 解码。返回 (out, consumed, clean, boundaries)。
    boundaries: 每个「字面量段结束」处的 (输入偏移, 当前输出长度)，可用于找流尾。"""
    out = bytearray(prefix)
    pre = len(prefix)
    i, n = 0, len(src)
    clean = False
    bounds = []
    while i < n:
        token = src[i]; i += 1
        lit = token >> 4
        if lit == 15:
            while True:
                if i >= n:
                    return bytes(out), i, False, bounds
                b = src[i]; i += 1
                lit += b
                if b != 255:
                    break
        if i + lit > n:
            return bytes(out), i, False, bounds
        out += src[i:i + lit]
        i += lit
        if len(out) - pre > max_out:
            return bytes(out), i, False, bounds
        bounds.append((i, len(out)))
        if i >= n:
            clean = True
            break
        if i + 2 > n:
            return bytes(out), i, False, bounds
        off = src[i] | (src[i + 1] << 8); i += 2
        if off == 0 or off > len(out):
            return bytes(out), i, False, bounds
        ml = (token & 0x0F) + 4
        if (token & 0x0F) == 15:
            while True:
                if i >= n:
                    return bytes(out), i, False, bounds
                b = src[i]; i += 1
                ml += b
                if b != 255:
                    break
        st = len(out) - off
        if ml <= off:
            out += out[st:st + ml]
        else:
            for k in range(ml):
                out.append(out[st + k])
        if len(out) - pre > max_out:
            return bytes(out), i, False, bounds
    return bytes(out), i, clean, bounds


def lz4_decode_at(src, start=0):
    """从 src[start:] 解一个完整 LZ4 块，返回 (out, consumed) 或 (None, 0)。"""
    if start >= len(src):
        return None, 0
    # 数据块不需要前置缓冲；若失败再用 16 字节零前缀兜底
    out, used, clean, _ = lz4_decode(src[start:], b"")
    if clean and used == len(src) - start:
        return out, used
    out2, used2, clean2, _ = lz4_decode(src[start:], bytes(16))
    if clean2 and used2 == len(src) - start:
        return out2[16:], used2
    return None, 0


# ---------------------------------------------------------------- 结构解析
def parse_blocks_info(buf, start=16, file_size=None, bi_len=None):
    """在 buf[start:] 尝试解析 blocksInfo。返回 dict 或 None。"""
    n = len(buf)
    if start + 4 > n:
        return None
    try:
        block_count = struct.unpack_from(">I", buf, start)[0]
    except struct.error:
        return None
    if not (0 < block_count <= 4096):
        return None
    p = start + 4
    if p + block_count * 10 > n:
        return None
    blocks = []
    for _ in range(block_count):
        usize, csize = struct.unpack_from(">II", buf, p)
        flags = struct.unpack_from(">H", buf, p + 8)[0]
        if usize == 0 or csize == 0:
            return None
        if usize > 1 << 30 or csize > 1 << 30:
            return None
        blocks.append((usize, csize, flags))
        p += 10
    if p + 4 > n:
        return None
    node_count = struct.unpack_from("<I", buf, p)[0]
    p += 4
    if not (0 < node_count <= 20000):
        return None
    nodes = []
    for _ in range(node_count):
        if p + 24 > n:
            return None
        off, size = struct.unpack_from(">QQ", buf, p)
        nflags = struct.unpack_from(">I", buf, p + 16)[0]
        p += 20
        e = buf.find(b"\0", p)
        if e < 0:
            return None
        path = buf[p:e]
        p = e + 1
        if not path or len(path) > 512:
            return None
        if not all(32 <= c < 127 for c in path):
            return None
        nodes.append({"offset": off, "size": size, "flags": nflags,
                      "path": path.decode("ascii")})
    res = {"block_count": block_count, "blocks": blocks,
           "node_count": node_count, "nodes": nodes,
           "end": p, "start": start}
    if file_size is not None and bi_len is not None:
        if sum(b[1] for b in blocks) != file_size - HEADER_LEN - bi_len:
            return None
    return res


def parse_bundle(path):
    """完整解析一个 .wmv。返回 dict。"""
    data = open(path, "rb").read()
    fsize = len(data)
    if data[:8] != MAGIC:
        raise ValueError("not UnityFS: %r" % data[:8])
    head_raw = data[:HEADER_LEN]

    # 1) 在 0x36 起做一次长解码，拿到所有「字面量段结束」候选
    out, used, clean, bounds = lz4_decode(data[HEADER_LEN:], bytes(16))
    best = None
    for in_pos, out_len in bounds:
        bi_len = in_pos
        if bi_len > 0x4000:
            continue
        for start in range(15, 24):
            r = parse_blocks_info(out[:out_len], start, fsize, bi_len)
            if r:
                r["prefix_bytes"] = start
                r["bi_len"] = bi_len
                r["hash_raw"] = out[:16]
                best = r
                break
        if best:
            break
    if not best:
        return {"file": path, "size": fsize, "ok": False}

    # 2) 按 block 表解压数据区
    best["file"] = path
    best["size"] = fsize
    best["ok"] = True
    best["head_raw"] = head_raw
    payload = bytearray()
    p = HEADER_LEN + best["bi_len"]
    ok_data = True
    blocks_detail = []
    for usize, csize, flags in best["blocks"]:
        chunk = data[p:p + csize]
        if len(chunk) != csize:
            ok_data = False
            break
        if flags == 3 or flags == 2:      # LZ4HC / LZ4
            d, u = lz4_decode_at(chunk, 0)
            if d is None:
                # 单块也试一下带前缀
                d2, u2, c2, _ = lz4_decode(chunk, bytes(16))
                d = d2[16:] if c2 and u2 == csize else None
            if d is None:
                ok_data = False
                blocks_detail.append((p, usize, csize, flags, False))
                p += csize
                continue
            payload += d
            blocks_detail.append((p, usize, csize, flags, len(d) == usize))
        else:
            payload += chunk
            blocks_detail.append((p, usize, csize, flags, True))
        p += csize
    best["blocks_detail"] = blocks_detail
    best["data_ok"] = ok_data and p == fsize
    best["payload"] = bytes(payload)
    return best


if __name__ == "__main__":
    import sys, glob
    base = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc"
    files = sorted(glob.glob(os.path.join(base, "*.wmv")), key=os.path.getsize)
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    for f in files[:20]:
        r = parse_bundle(f)
        if not r["ok"]:
            print("%-40s FAIL" % os.path.basename(f))
            continue
        print("%-40s bi_len=%-4d start=%-2d blocks=%d nodes=%d data_ok=%s payload=%d" %
              (os.path.basename(f), r["bi_len"], r["prefix_bytes"],
               r["block_count"], r["node_count"], r["data_ok"], len(r["payload"])))
        for nd in r["nodes"][:3]:
            print("      %s  off=%d size=%d flags=%d" %
                  (nd["path"], nd["offset"], nd["size"], nd["flags"]))
