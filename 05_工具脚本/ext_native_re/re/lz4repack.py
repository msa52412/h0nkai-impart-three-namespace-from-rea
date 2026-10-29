"""LZ4 block 解析 / 重建 / 等长重编码

核心用途：在不改变压缩流长度（csize）的前提下，修改 LZ4 压缩块里的任意字节。

== 为什么能等长 ==
LZ4 block 是「token 序列」：
    seq = [literals, match_len, offset]
    编码 = token(1) [lit_ext] literals [ml_ext] offset(2)
其中 match 的源与 payload 中的字节完全相同（match 就是从前面复制）。
因此把 match 的前 k 字节"并入 literals"，输出 payload 一字不差，
而压缩流长度恰好增加 k 字节（不含 nibble 溢出）。这就是 1 字节粒度的调节旋钮。

反方向（缩短）也存在：把 literals 尾部并入 match，或在 seq 边界搬移，
当 match_len-4 跨过 15 边界时会省下 1 字节 ext。本模块主要用加长旋钮。
"""


# ------------------------------------------------------------ 长度计算
def _extlen(v):
    """LZ4 扩展长度字节数（v = 超出 15 的部分，v >= 0）"""
    return v // 255 + 1


def seqlen(lit, ml):
    """单个 seq 编码后的字节数。ml=None 表示结尾纯字面量段。"""
    n = 1
    if lit >= 15:
        n += _extlen(lit - 15)
    n += lit
    if ml is not None:
        if ml - 4 >= 15:
            n += _extlen(ml - 4 - 15)
        n += 2
    return n


# ------------------------------------------------------------ 解析
def parse(src, track=False):
    """压缩流 -> seq 列表 [[literals(bytes), match_len|None, offset|None], ...]

    track=True 时额外返回 srcmap：输出 payload 下标 -> 压缩流下标（-1 = 来自 match）
    """
    seqs = []
    srcmap = [] if track else None
    i, n = 0, len(src)
    while i < n:
        tok = src[i]
        i += 1
        lit = tok >> 4
        if lit == 15:
            while True:
                if i >= n:
                    return seqs, srcmap
                b = src[i]
                i += 1
                lit += b
                if b != 255:
                    break
        if i + lit > n:
            return seqs, srcmap
        lits = src[i:i + lit]
        i += lit
        if track:
            srcmap.extend(range(i - lit, i))
        if i >= n:
            seqs.append([lits, None, None])
            break
        if i + 2 > n:
            return seqs, srcmap
        off = src[i] | (src[i + 1] << 8)
        i += 2
        ml = (tok & 0x0F) + 4
        if (tok & 0x0F) == 15:
            while True:
                if i >= n:
                    return seqs, srcmap
                b = src[i]
                i += 1
                ml += b
                if b != 255:
                    break
        seqs.append([lits, ml, off])
        if track:
            srcmap.extend([-1] * ml)
    return seqs, srcmap


# ------------------------------------------------------------ 重建
def build(seqs):
    out = bytearray()
    for lits, ml, off in seqs:
        lit = len(lits)
        tok = min(lit, 15) << 4
        if ml is not None:
            tok |= min(ml - 4, 15)
        out.append(tok)
        if lit >= 15:
            x = lit - 15
            while True:
                b = 255 if x >= 255 else x
                out.append(b)
                x -= 255
                if b != 255:
                    break
        out += lits
        if ml is not None:
            # 注意顺序：offset 在 match 长度扩展之前（LZ4 标准）
            out += bytes((off & 255, (off >> 8) & 255))
            if ml - 4 >= 15:
                x = ml - 4 - 15
                while True:
                    b = 255 if x >= 255 else x
                    out.append(b)
                    x -= 255
                    if b != 255:
                        break
    return bytes(out)


def decode(src):
    """纯解码（走 seq 路径，便于验证 build/parse 一致性）"""
    out = bytearray()
    seqs, _ = parse(src)
    for lits, ml, off in seqs:
        out += lits
        if ml is not None:
            st = len(out) - off
            if st < 0:
                raise ValueError("bad offset")
            for k in range(ml):
                out.append(out[st + k])
    return bytes(out)


# ------------------------------------------------------------ 编码
def encode(data, min_match=4, chain=1):
    """贪心 LZ4 编码 -> seqs

    chain=1 等价于标准 LZ4 level1（hash table 单候选），速度最快；
    增大 chain 可获得更高压缩率（更短的 csize）。
    """
    n = len(data)
    if n == 0:
        return [[b"", None, None]]
    MFLIMIT = 12
    limit = n - MFLIMIT
    seqs = []
    tbl = {}
    anchor = 0
    i = 0
    while i < limit:
        key = data[i:i + 4]
        cands = tbl.get(key)
        best_len, best_off = 0, 0
        if cands:
            for c in (cands if chain > 1 else cands[-1:]):
                off = i - c
                if off <= 0 or off > 65535:
                    continue
                ml = 4
                mx = n - i
                while ml < mx and data[c + ml] == data[i + ml]:
                    ml += 1
                if ml > best_len:
                    best_len, best_off = ml, off
                    if chain <= 1:
                        break
        if best_len >= min_match and best_off:
            seqs.append([data[anchor:i], best_len, best_off])
            end = i + best_len
            # 把 match 内部位置也进表，改善后续压缩
            j = i + 1
            while j < end:
                tbl[data[j:j + 4]] = [j]
                j += 1
            i = end
            anchor = i
        else:
            if cands is None:
                tbl[key] = [i]
            else:
                tbl[key] = cands[-3:] + [i] if chain > 1 else [i]
            i += 1
    seqs.append([data[anchor:], None, None])
    # 合并尾部空 literals 段
    if len(seqs) > 1 and not seqs[-1][0]:
        seqs.pop()
    return seqs


# ------------------------------------------------------------ 等长调节
def _seq_starts(seqs):
    st, p = [], 0
    for lits, ml, off in seqs:
        st.append(p)
        p += len(lits)
        if ml is not None:
            p += ml
    return st


def inflate(seqs, payload, delta):
    """把 match 前 k 字节并入 literals，使总编码长度增加 delta 字节。

    返回 (新 seqs, 未补齐的剩余量)。
    """
    seqs = [[s[0], s[1], s[2]] for s in seqs]
    if delta <= 0:
        return seqs, 0
    starts = _seq_starts(seqs)
    remaining = delta
    for i, s in enumerate(seqs):
        if remaining <= 0:
            break
        if s[1] is None or s[1] <= 4:
            continue
        L0, ML0 = len(s[0]), s[1]
        base = seqlen(L0, ML0)
        best_k, best_d = 0, 0
        for k in range(1, ML0 - 3):
            d = seqlen(L0 + k, ML0 - k) - base
            if d == remaining:
                best_k, best_d = k, d
                break
            if d < remaining:
                best_k, best_d = k, d
            else:
                break
        if best_k:
            m = starts[i] + L0
            s[0] = s[0] + payload[m:m + best_k]
            s[1] = ML0 - best_k
            remaining -= best_d
    return seqs, remaining


def deflate(seqs, payload, delta):
    """反向旋钮：把 literals 尾部并入 match，缩短 delta 字节（要求真能匹配）。"""
    seqs = [[s[0], s[1], s[2]] for s in seqs]
    if delta <= 0:
        return seqs, 0
    starts = _seq_starts(seqs)
    remaining = delta
    for i, s in enumerate(seqs):
        if remaining <= 0:
            break
        if s[1] is None or len(s[0]) == 0:
            continue
        L0, ML0, off = len(s[0]), s[1], s[2]
        base = seqlen(L0, ML0)
        # 只能吞 down = L0 （最多把整个 literals 吃掉）
        for k in range(1, L0 + 1):
            # 校验 payload[p-k .. p) == payload[p-k-off .. p-off)
            p = starts[i] + L0
            ok = True
            for j in range(k):
                if payload[p - k + j] != payload[p - k + j - off]:
                    ok = False
                    break
            if not ok:
                break
            d = base - seqlen(L0 - k, ML0 + k)
            if d == remaining:
                s[0] = s[0][:L0 - k]
                s[1] = ML0 + k
                remaining = 0
                break
            if 0 < d < remaining:
                remaining -= d
                s[0] = s[0][:L0 - k]
                s[1] = ML0 + k
                base = seqlen(len(s[0]), s[1])
                L0 = len(s[0])
                break
    return seqs, remaining


# ------------------------------------------------------------ 顶层 API
def reencode(src, payload_new, target_len):
    """把 payload_new 重新写成 LZ4 流，长度精确等于 target_len。

    返回 (流 bytes, 信息 dict) 或 (None, 原因)。
    """
    for min_match, chain in ((4, 1), (5, 1), (4, 3), (6, 1), (4, 8), (8, 1), (4, 16)):
        seqs = encode(payload_new, min_match=min_match, chain=chain)
        cur = len(build(seqs))
        if cur > target_len:
            continue
        need = target_len - cur
        if need == 0:
            return build(seqs), {"path": "exact", "min_match": min_match,
                                 "chain": chain}
        s2, rem = inflate(seqs, payload_new, need)
        if rem == 0:
            out = build(s2)
            if len(out) == target_len:
                return out, {"path": "inflate", "min_match": min_match,
                             "chain": chain, "delta": need}
        # 若仍有剩余，尝试 deflate 池化后再补（少见）
    return None, "无法命中目标长度"


def verify_stream(stream, expect_payload):
    """解码流并比对，确认重建正确。"""
    try:
        d = decode(stream)
    except Exception as e:
        return False, "decode 失败: %s" % e
    if d != expect_payload:
        return False, "payload 不一致（%d vs %d）" % (len(d), len(expect_payload))
    return True, "ok"


if __name__ == "__main__":
    import random
    import time
    random.seed(7)
    # 自测：随机 + 重复混合数据
    data = (b"HelloWorld_" * 400 + bytes(range(256)) * 8 +
            b"Task_3CoverLine" * 200 +
            bytes(random.randrange(256) for _ in range(20000)))
    t = time.time()
    seqs = encode(data, 4, 1)
    st = build(seqs)
    ok, msg = verify_stream(st, data)
    print("encode -> %d bytes (raw %d, ratio %.3f) verify=%s %s  用时 %.2fs" %
          (len(st), len(data), len(st) / len(data), ok, msg, time.time() - t))

    # 改一个字节（在随意位置），做等长重编码
    target = len(st)
    for pos in (0, 5000, 12345, len(data) - 1):
        pn = bytearray(data)
        pn[pos] ^= 0xFF
        out, info = reencode(st, bytes(pn), target)
        if out is None:
            print("  pos=%-6d 失败: %s" % (pos, info))
            continue
        vok, vmsg = verify_stream(out, bytes(pn))
        print("  pos=%-6d 等长重编码 %d -> %d  %s verify=%s" %
              (pos, target, len(out), info, vok))

    # 解析原流再重建，验证 parse/build 往返
    back = build(parse(st)[0])
    print("parse/build 往返一致:", back == st)
