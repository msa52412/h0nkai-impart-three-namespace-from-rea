"""BH3 .wmv 解析器 v2 —— 关键结论修正：

  .wmv 文件 = 多个 UnityFS bundle 首尾拼接（每个 bundle 自成一体）
  每个 bundle：
    0x00..0x07  "UnityFS\\0"
    0x08..0x35  46 字节被变换的包头（重打包时若长度不变可原字节照抄）
    0x36..      blocksInfo（LZ4 流，需 16 字节零前缀）：
                  hash16 | u8 blockCount | blockCount*(u32BE usize,u32BE csize,u16BE flags)
                        | u32BE nodeCount | nodeCount*(u64BE off,u64BE size,u32BE flags,path\\0)
    之后        sum(csize) 字节的数据块（每块独立 LZ4 / 原样）
  bundle 总长 = 0x36 + bi_len + sum(csize)
  下一个 bundle 起点必须落在 "UnityFS\\0" 上（或 EOF）—— 这是唯一可靠的自校验。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wmv import lz4_decode

HEADER_LEN = 0x36
MAGIC = b"UnityFS\0"


def _u(buf, off, n):
    return int.from_bytes(buf[off:off + n], 'big')


def parse_blocks_info(buf, s=16):
    n = len(buf)
    if s + 1 > n:
        return None
    bc = buf[s]
    if not (0 < bc <= 4096):
        return None
    p = s + 1
    blocks = []
    for _ in range(bc):
        if p + 10 > n:
            return None
        usize = _u(buf, p, 4)
        csize = _u(buf, p + 4, 4)
        flags = _u(buf, p + 8, 2)
        if usize == 0 or csize == 0:
            return None
        if usize > (1 << 31) or csize > (1 << 31):
            return None
        if flags not in (0, 1, 2, 3, 4, 5):
            return None
        blocks.append((usize, csize, flags))
        p += 10
    if p + 4 > n:
        return None
    nc = _u(buf, p, 4)
    if not (0 < nc <= 40000):
        return None
    p += 4
    nodes = []
    for _ in range(nc):
        if p + 20 > n:
            return None
        off = _u(buf, p, 8)
        size = _u(buf, p + 8, 8)
        fl = _u(buf, p + 16, 4)
        p += 20
        e = buf.find(b"\0", p)
        if e < 0:
            return None
        path = buf[p:e]
        if not path or len(path) > 512:
            return None
        if not all(32 <= c < 127 for c in path):
            return None
        nodes.append({"offset": off, "size": size, "flags": fl,
                      "path": path.decode("ascii")})
        p = e + 1
    return {"block_count": bc, "blocks": blocks,
            "node_count": nc, "nodes": nodes, "end": p}


def try_bundle(data, p, max_bi=1 << 17):
    """尝试把 data[p:] 解释成一个 bundle。返回 dict 或 None。"""
    if data[p:p + 8] != MAGIC:
        return None
    out, used, clean, bounds = lz4_decode(data[p + HEADER_LEN:], bytes(16),
                                          max_out=1 << 20)
    fsize = len(data)
    for bi_len, out_len in bounds:
        if bi_len > max_bi:
            break
        r = parse_blocks_info(out[:out_len], 16)
        if not r:
            continue
        if r["end"] != out_len:
            continue
        total = HEADER_LEN + bi_len + sum(b[1] for b in r["blocks"])
        if p + total > fsize:
            continue
        nxt = p + total
        if nxt != fsize and data[nxt:nxt + 8] != MAGIC:
            continue
        r["start"] = p
        r["bi_len"] = bi_len
        r["total"] = total
        r["data_start"] = p + HEADER_LEN + bi_len
        r["head_raw"] = data[p:p + HEADER_LEN]
        return r
    return None


def walk(path):
    """解析整个 .wmv，返回 bundle 列表。"""
    data = open(path, "rb").read()
    p = 0
    out = []
    while p < len(data):
        b = try_bundle(data, p)
        if not b:
            out.append({"ok": False, "start": p, "rest": len(data) - p})
            break
        b["ok"] = True
        out.append(b)
        p = b["total"] + b["start"]
    return data, out


def extract_payload(data, b):
    """按 block 表解压，返回拼接后的 payload。"""
    p = b["data_start"]
    buf = bytearray()
    for usize, csize, flags in b["blocks"]:
        chunk = data[p:p + csize]
        if len(chunk) != csize:
            return None
        if flags in (2, 3):          # LZ4 / LZ4HC
            d, u, c, _ = lz4_decode(chunk, b"")
            if not c or u != csize:
                return None
            buf += d
        elif flags == 5:             # 原样存储
            buf += chunk
        else:
            buf += chunk
        p += csize
    return bytes(buf)


if __name__ == "__main__":
    import glob
    base = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
    files = sorted(glob.glob(os.path.join(base, "*.wmv")), key=os.path.getsize)
    arg = sys.argv[1:] or files
    if len(sys.argv) > 1:
        arg = sys.argv[1:]
        if os.path.isdir(arg[0]):
            arg = sorted(glob.glob(os.path.join(arg[0], "*.wmv")))
    ok = 0
    part = 0
    bad = []
    for f in arg:
        data, bundles = walk(f)
        n_ok = sum(1 for b in bundles if b["ok"])
        if not bundles:
            bad.append((os.path.basename(f), len(data), 0))
            continue
        if all(b["ok"] for b in bundles):
            ok += 1
        else:
            part += 1
            bad.append((os.path.basename(f), len(data), len(bundles)))
        if len(arg) <= 20:
            print("%-42s %9d bundles=%d %s" %
                  (os.path.basename(f), len(data), len(bundles),
                   "OK" if all(b["ok"] for b in bundles) else "PARTIAL"))
            for b in bundles:
                if not b["ok"]:
                    print("     FAIL at %d rest=%d" % (b["start"], b["rest"]))
                    continue
                print("     @%-9d total=%-8d bi=%-4d blocks=%-3d nodes=%-3d %s" %
                      (b["start"], b["total"], b["bi_len"], b["block_count"],
                       b["node_count"], b["nodes"][0]["path"][:52]))
    print()
    print("全部成功 %d / %d ；部分失败 %d" % (ok, len(arg), part))
    for r in bad[:15]:
        print("   FAIL", r)
