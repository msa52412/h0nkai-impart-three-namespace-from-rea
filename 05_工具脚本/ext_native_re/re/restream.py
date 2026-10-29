"""结构保持重放（restream）：原 LZ4 流的 token 结构不变，只修补被改字节波及的 match。

原理：
  match 就是从前面复制，源字节与 payload 完全相同。改动 payload 后，
  逐 seq 重放：literals 直接取新 payload；match 校验「按原 offset 复制」是否仍等于
  新 payload 对应区间 —— 一致则原样保留，不一致则把能保留的最长前缀留作 match，
  剩余字节下沉到下一个 seq 的 literals（carry）。

因为绝大多数 match 不受影响，长度变化通常为 0；只有真被波及的 seq 会变化，
且变化量等于「match 缩短的字节数」。随后可用 inflate/deflate 旋钮把总长度掰回目标值。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lz4repack as L


def restream(src, payload_new):
    """原压缩流 + 新 payload -> 新 seqs（尽量保持结构）

    返回 (seqs, stats)；seqs 为 [(literals, match_len|None, offset|None), ...]
    """
    seqs, _ = L.parse(src)
    out = []
    pos = 0
    carry = b""
    n_match = n_keep = n_shrink = n_drop = 0
    moved = 0

    for (lits0, ml0, off0) in seqs:
        L0 = len(lits0)
        cur = carry + payload_new[pos:pos + L0]
        pos += L0
        carry = b""

        if ml0 is None:
            out.append((cur, None, None))
            continue

        start = pos
        end = start + ml0
        good = 0
        if end <= len(payload_new):
            for k in range(ml0):
                sp = start + k - off0
                if sp < 0:
                    break
                if payload_new[start + k] == payload_new[sp]:
                    good += 1
                else:
                    break
        n_match += 1
        if good >= ml0:
            n_keep += 1
            out.append((cur, ml0, off0))
            pos += ml0
        elif good >= 4:
            n_shrink += 1
            out.append((cur, good, off0))
            pos += ml0
            carry = payload_new[start + good:start + ml0]
            moved += ml0 - good
        else:
            n_drop += 1
            pos += ml0
            carry = cur + payload_new[start:start + ml0]
            moved += ml0

    if carry:
        out.append((carry, None, None))

    # 规范化：末尾必须是纯 literals 段；中间不能出现连续两段纯 literals
    norm = []
    for s in out:
        if s[1] is None:
            if norm and norm[-1][1] is None:
                norm[-1] = (norm[-1][0] + s[0], None, None)
            else:
                norm.append(s)
        else:
            norm.append(s)
    if not norm or norm[-1][1] is not None:
        norm.append((b"", None, None))

    stats = dict(seqs=len(seqs), match=n_match, keep=n_keep,
                 shrink=n_shrink, drop=n_drop, moved=moved)
    return norm, stats


def rebuild(src, payload_new):
    """返回 (新流, 是否等长, 差值, stats)"""
    seqs, stats = restream(src, payload_new)
    stream = L.build([list(s) for s in seqs])
    return stream, len(stream) == len(src), len(stream) - len(src), stats


def rebuild_exact(src, payload_new):
    """尽量做到等长：先结构保持，再用 inflate/deflate 旋钮补齐。

    返回 (流|None, 信息 dict)
    """
    seqs, stats = restream(src, payload_new)
    cur = len(L.build([list(s) for s in seqs]))
    target = len(src)
    if cur == target:
        return L.build([list(s) for s in seqs]), dict(path="exact", **stats)
    if cur < target:
        s2, rem = L.inflate([list(s) for s in seqs], payload_new, target - cur)
        if rem == 0:
            b = L.build(s2)
            if len(b) == target:
                return b, dict(path="inflate", delta=target - cur, **stats)
    # 结构保持后变长：尝试"更紧凑的重编码"不行，改用 deflate 旋钮在其他 seq 上省
    if cur > target:
        s2, rem = L.deflate([list(s) for s in seqs], payload_new, cur - target)
        if rem == 0:
            b = L.build(s2)
            if len(b) == target:
                return b, dict(path="deflate", delta=cur - target, **stats)
    return None, dict(path="fail", cur=cur, target=target, **stats)


if __name__ == "__main__":
    import random
    random.seed(11)
    data = (b"HelloWorld_" * 400 + bytes(range(256)) * 8 +
            b"Task_3CoverLine" * 200 + b"\x00" * 4000 +
            bytes(random.randrange(256) for _ in range(20000)))
    seqs = L.encode(data, 4, 8)
    st = L.build(seqs)
    print("原流 %d bytes, payload %d, seqs %d" % (len(st), len(data), len(seqs)))
    for p0 in (0, 3, 5000, 12345, 20000, len(data) - 1):
        pn = bytearray(data)
        pn[p0] ^= 0xFF
        pn = bytes(pn)
        out, same, diff, stats = rebuild(st, pn)
        okdec = L.decode(out) == pn
        ex, info = rebuild_exact(st, pn)
        exok = (ex is not None) and L.decode(ex) == pn
        print("  改 pos=%-6d 长度 %+d 解码=%s | 精确等长=%s %s" %
              (p0, diff, okdec, exok, info["path"] if ex is None else info))
