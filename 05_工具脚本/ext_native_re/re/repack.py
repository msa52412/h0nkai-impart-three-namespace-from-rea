"""repack —— bundle 重打包器（可改变 bundle 长度）

已攻破的三件事：
  1. blocksInfo 解压后就是 body（无 hash，从 offset 0 直接是 blockCount），
     但解码器需要 16 字节全零虚拟前缀（Unity 变体 LZ4 的初始窗口）
  2. 头部 total 是定点 XOR：
       head[0x15] = (total>>16 & 0xFF) ^ 0x9e
       head[0x16] = (total>> 8 & 0xFF) ^ 0x77
       head[0x17] = (total>> 0 & 0xFF) ^ 0x37
       head[0x18] = (total>>24 & 0xFF) ^ 0x79
  3. block 数据是纯 LZ4 块；原文件用 LZ4HC(level≈12)，
     用 lz4.block high_compression=12 可压缩到同等甚至更小

于是「改任意字节」不再受等长约束：
  csize 变了改 blocksInfo -> bi_len 变了改 total -> 完全闭环。
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wmvkit as K
import lz4repack as L

try:
    import lz4.block as LB
except ImportError:
    raise SystemExit("需要 lz4 模块: pip install lz4")

PRE = bytes(16)
TOTAL_POS = 0x15
TOTAL_KEYS = (0x9E, 0x77, 0x37, 0x79)
TOTAL_ORDER = (2, 1, 0, 3)          # head[0x15..0x18] 对应的 total 字节序号
HC_LEVELS = (12, 16, 9, 6, 3, 1)


# ------------------------------------------------------------- 头部
def enc_total(total):
    return bytes(((total >> (8 * b)) & 0xFF) ^ k
                 for b, k in zip(TOTAL_ORDER, TOTAL_KEYS))


def dec_total(head):
    v = 0
    for i, (b, k) in enumerate(zip(TOTAL_ORDER, TOTAL_KEYS)):
        v |= (head[TOTAL_POS + i] ^ k) << (8 * b)
    return v


def set_total(head, total):
    h = bytearray(head)
    h[TOTAL_POS:TOTAL_POS + 4] = enc_total(total)
    return bytes(h)


# ------------------------------------------------------------- blocksInfo
def bi_parse(body):
    p = 0
    bc = body[p]; p += 1
    blocks = []
    for _ in range(bc):
        usize, csize, flags = struct.unpack_from(">IIH", body, p)
        blocks.append([usize, csize, flags])
        p += 10
    nc = struct.unpack_from(">I", body, p)[0]; p += 4
    nodes = []
    for _ in range(nc):
        off, size, fl = struct.unpack_from(">QQI", body, p)
        p += 20
        e = body.index(b"\0", p)
        nodes.append([off, size, fl, body[p:e].decode("ascii")])
        p = e + 1
    return blocks, nodes, p


def bi_build(blocks, nodes):
    out = bytearray([len(blocks)])
    for usize, csize, flags in blocks:
        out += struct.pack(">IIH", usize, csize, flags)
    out += struct.pack(">I", len(nodes))
    for off, size, fl, path in nodes:
        out += struct.pack(">QQI", off, size, fl)
        out += path.encode("ascii") + b"\0"
    return bytes(out)


def bi_body(data, b):
    st = data[b["start"] + K.HEADER_LEN:b["start"] + K.HEADER_LEN + b["bi_len"]]
    out, _, _, _, _ = K.lz4_decode(st, PRE)
    return out[len(PRE):]


# ------------------------------------------------------------- 压缩到指定长度
def compress_hc(payload, level=12):
    return LB.compress(payload, store_size=False, mode="high_compression",
                       compression=level)


def compress_exact(payload, target):
    """把 payload 压成恰好 target 字节（优先自然命中，其次用 inflate 补齐）"""
    if not payload:
        return (b"" if target == 0 else None), "empty"
    for lev in HC_LEVELS:
        st = compress_hc(payload, lev)
        if len(st) > target:
            continue
        if len(st) == target:
            return st, "exact(lev%d)" % lev
        seqs, _ = L.parse(st)
        s2, rem = L.inflate(seqs, payload, target - len(st))
        if rem:
            continue
        out = L.build(s2)
        if len(out) == target and L.decode(out) == payload:
            return out, "inflate(lev%d,+%d)" % (lev, target - len(st))
    return None, "无法命中 %d" % target


# ------------------------------------------------------------- 重打包
def split_payload(b, pl):
    out, off = [], 0
    for usize, csize, flags in b["blocks"]:
        out.append(pl[off:off + usize])
        off += usize
    return out


def repack(data, b, new_payload, keep_size=True, verbose=False,
           blocks_override=None, nodes_override=None):
    """用 new_payload（长度须等于 sum(usize)）重建 bundle 字节串。

    keep_size=True 时尽量保持每个 block 的 csize 不变（文件长度不变）；
    做不到就允许变化，并同步修正 blocksInfo 与头部 total。
    blocks_override / nodes_override 允许改 payload 长度（新建 block / 改 node 长度）。

    返回 (bundle_bytes | None, info)
    """
    body_old = bi_body(data, b)
    blocks0, nodes0, bi_end = bi_parse(body_old)
    if bi_end != len(body_old):
        return None, {"err": "blocksInfo 解析不完整 %d/%d" % (bi_end, len(body_old))}
    blocks = ([list(x) for x in blocks0] if blocks_override is None
              else [list(x) for x in blocks_override])
    nodes = nodes0 if nodes_override is None else [list(x) for x in nodes_override]
    if sum(x[0] for x in blocks) != len(new_payload):
        return None, {"err": "payload 长度不匹配"}

    old_parts = split_payload({"blocks": blocks0}, K.bundle_payload(data, b))
    new_parts = split_payload({"blocks": blocks}, new_payload)

    pos = b["data_start"]
    chunks = []
    new_blocks = []
    stats = []
    for i, (usize, csize, flags) in enumerate(blocks):
        old_chunk = data[pos:pos + csize]
        pos += csize
        if new_parts[i] == old_parts[i]:
            chunks.append(old_chunk)
            new_blocks.append([usize, csize, flags])
            stats.append(("keep", csize, csize))
            continue
        if flags not in (2, 3):
            chunks.append(new_parts[i])
            new_blocks.append([usize, len(new_parts[i]), flags])
            stats.append(("raw", csize, len(new_parts[i])))
            continue
        st, mode = (None, "")
        if keep_size:
            st, mode = compress_exact(new_parts[i], csize)
        if st is None:
            st = compress_hc(new_parts[i], 12)
            mode = "hc12"
        if K.lz4_decode(st, b"")[0] != new_parts[i]:
            return None, {"err": "block%d 压缩校验失败" % i}
        chunks.append(st)
        new_blocks.append([usize, len(st), flags])
        stats.append((mode, csize, len(st)))
        if verbose:
            print("    block%d %9d -> %9d (%+d) %s" %
                  (i, csize, len(st), len(st) - csize, mode))

    new_body = bi_build(new_blocks, nodes)
    full_new = PRE + new_body
    # blocksInfo：内容没变就**原样复用原始压缩字节**（连压缩器差异都省掉）
    full_old = PRE + body_old
    bi_out = None
    if new_body == body_old:
        bi_out = data[b["start"] + K.HEADER_LEN:
                      b["start"] + K.HEADER_LEN + b["bi_len"]]
    elif len(full_new) == len(full_old):
        bi_out, _m = compress_exact(new_body, b["bi_len"])
        if bi_out is not None and K.lz4_decode(bi_out, PRE)[0] != full_new:
            bi_out = None
    if bi_out is None:
        for lev in HC_LEVELS:
            cand = compress_hc(new_body, lev)
            if K.lz4_decode(cand, PRE)[0] == full_new:
                bi_out = cand
                break
    if bi_out is None:
        return None, {"err": "blocksInfo 重压缩失败"}
    if K.lz4_decode(bi_out, PRE)[0] != full_new:
        return None, {"err": "blocksInfo 校验失败"}

    total = K.HEADER_LEN + len(bi_out) + sum(x[1] for x in new_blocks)
    head = set_total(data[b["start"]:b["start"] + K.HEADER_LEN], total)
    out = head + bi_out + b"".join(chunks)
    if len(out) != total:
        return None, {"err": "长度自校验失败 %d != %d" % (len(out), total)}
    return out, {"blocks": stats, "bi_len": b["bi_len"], "new_bi_len": len(bi_out),
                 "total": b["total"], "new_total": total}


def repack_keep_total(data, b, new_payload, blocks_override, nodes_override,
                      verbose=False):
    """重打包，但强制 **bundle 总长度与原来完全一致**（文件字节数不变）。

    做法：payload 变长/变短后，把差量摊到最大的那个被改动 block 的 csize 上
    （用 compress_exact 的 inflate 旋钮精确命中），blocksInfo 也压回原 bi_len。
    这样整份 .wmv 的字节数不变 —— 客户端按 size 做的本地校验就不会报警。
    """
    body_old = bi_body(data, b)
    blocks0, nodes0, bi_end = bi_parse(body_old)
    if bi_end != len(body_old):
        return None, {"err": "blocksInfo 解析不完整"}
    blocks = [list(x) for x in blocks_override]
    nodes = [list(x) for x in nodes_override]
    if sum(x[0] for x in blocks) != len(new_payload):
        return None, {"err": "payload 长度不匹配"}

    old_parts = split_payload({"blocks": blocks0}, K.bundle_payload(data, b))
    new_parts = split_payload({"blocks": blocks}, new_payload)

    # 1) 原样保留的 block 直接复用；改动的先用 HC12 压出自然长度
    pos = b["data_start"]
    chunks, new_blocks, stats = [], [], []
    natural = []
    for i, (usize, csize, flags) in enumerate(blocks):
        old_chunk = data[pos:pos + csize]
        pos += csize
        if new_parts[i] == old_parts[i]:
            chunks.append(old_chunk)
            new_blocks.append([usize, csize, flags])
            stats.append(("keep", csize, csize))
            natural.append((i, csize, True))
            continue
        st = compress_hc(new_parts[i], 12)
        if K.lz4_decode(st, b"")[0] != new_parts[i]:
            return None, {"err": "block%d 压缩校验失败" % i}
        chunks.append(st)
        new_blocks.append([usize, len(st), flags])
        stats.append(("hc12", csize, len(st)))
        natural.append((i, len(st), False))

    # 2) 迭代收敛：padding 会改变 blocksInfo 的压缩长度，故来回校 3~4 轮
    changed = [i for i, sz, kept in natural if not kept]
    if not changed and sum(x[1] for x in new_blocks) != b["total"] - K.HEADER_LEN - b["bi_len"]:
        return None, {"err": "无改动块可调，长度无法对齐"}
    changed.sort(key=lambda i: -len(new_parts[i]))

    bi_out = None
    bi_mode = ""
    for it in range(6):
        new_body = bi_build(new_blocks, nodes)
        full_new = PRE + new_body
        bi_out, bi_mode = compress_exact(new_body, b["bi_len"])
        if bi_out is None:
            for lev in HC_LEVELS:
                cand = compress_hc(new_body, lev)
                if K.lz4_decode(cand, PRE)[0] == full_new:
                    bi_out = cand
                    break
            if bi_out is None:
                return None, {"err": "blocksInfo 重压缩失败"}
            bi_mode = "hc len=%d" % len(bi_out)
        budget = b["total"] - K.HEADER_LEN - len(bi_out)
        cur = sum(x[1] for x in new_blocks)
        deficit = budget - cur
        if verbose:
            print("   [轮%d] bi_len=%d(%s) csize=%d 预算=%d 差=%+d" %
                  (it, len(bi_out), bi_mode, cur, budget, deficit))
        if deficit == 0:
            break
        if deficit < 0:
            return None, {"err": "压缩后已超出原总长 %d，无法等长" % (-deficit)}
        done = False
        for i in changed:
            st, mode = compress_exact(new_parts[i], new_blocks[i][1] + deficit)
            if st is None:
                continue
            chunks[i] = st
            stats[i] = (mode, stats[i][1], len(st))
            new_blocks[i][1] = len(st)
            if verbose:
                print("   block%d 补齐 -> %d" % (i, len(st)))
            done = True
            break
        if not done:
            return None, {"err": "无法精确补齐 %d 字节" % deficit}
    else:
        return None, {"err": "等长收敛失败"}

    total = K.HEADER_LEN + len(bi_out) + sum(x[1] for x in new_blocks)
    if total != b["total"]:
        return None, {"err": "总长未对齐 %d != %d" % (total, b["total"])}
    head = set_total(data[b["start"]:b["start"] + K.HEADER_LEN], total)
    out = head + bi_out + b"".join(chunks)
    if K.lz4_decode(bi_out, PRE)[0] != PRE + bi_build(new_blocks, nodes):
        return None, {"err": "blocksInfo 校验失败"}
    return out, {"bi_len": b["bi_len"], "new_bi_len": len(bi_out),
                 "total": b["total"], "new_total": total, "blocks": stats,
                 "same_size": True}


# ------------------------------------------------------------- 文件级
def read_file(path):
    data = open(path, 'rb').read()
    _, bs = K.walk(data=data)
    return data, bs


def replace_bundle(path, bidx, new_payload, out_path=None, verbose=True):
    data, bs = read_file(path)
    b = bs[bidx]
    if not b["ok"]:
        raise RuntimeError("bundle#%d 未解析成功" % bidx)
    nb, info = repack(data, b, new_payload, verbose=verbose)
    if nb is None:
        raise RuntimeError("重打包失败: %s" % info)
    out = data[:b["start"]] + nb + data[b["start"] + b["total"]:]
    _, bs2 = K.walk(data=out)
    ok = all(x["ok"] for x in bs2)
    out_path = out_path or (path + ".new")
    open(out_path, 'wb').write(out)
    return out, info, ok, bs2, out_path
