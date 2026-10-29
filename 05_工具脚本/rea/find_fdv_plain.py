# -*- coding: utf-8 -*-
"""在 metadata 文件的未归属区间里扫 fieldDefaultValues：
   明文 12B 行 {fieldIndex, typeIndex, dataIndex}，fieldIndex 严格递增且落在 literal 集合"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
N = len(BUF)
N_FIELDS = 419568
N_TYPES = 41014  # 类型数

# literal 集合
lit = set()
with open(r"D:\Carol-start\_rea\bh3_field_flags.tsv", encoding="utf-8") as f:
    next(f)
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) >= 5 and p[4] == "1":
            lit.add(int(p[0]))
print("literal 字段 %d 个" % len(lit))

# 已知段（绝对地址, 结束或 None=只标起点）
segs = [
    (0x118, 0x118, "header-salt区"),
    (0x512B8, None, "TYPE"),
    (0x55C71C, 0x55C71C + 1967 * 12, "GENCONT"),
    (0xAC1050, None, "PARAM"),
    (0xEC7724, 0xEC7724 + 66261 * 0xC, "interfaceOffsets明文"),
    (0xFA8430, None, "METHOD"),
    (0x1C1F570, None, "GENPAR"),
    (0x1C2A1B0, None, "T5"),
    (0x1EC6738, 0x1EC6738 + 77396 * 8, "blob描述表"),
    (0x1F5D9D8, None, "FIELD"),
    (0x242AD18, None, "ASM"),
    (0x242D400, None, "T7"),
    (0x24AAC30, None, "STRPOOL"),
    (0x3185AB4, 0x3185AB4 + 0x213C15, "blob数据区"),
    (0x33996B4, 0x33996B4 + 263700 * 8, "pairs"),
]

# 简易区间图：按起点排序，找 >=0x2000 的空隙
segs.sort()
gaps = []
prev_end = 0x118
for s, e, name in segs:
    if s > prev_end + 0x2000:
        gaps.append((prev_end, s))
    if e:
        prev_end = max(prev_end, e)
    else:
        prev_end = max(prev_end, s + 0x1000)  # 未知长度，保守占位
if N - prev_end > 0x2000:
    gaps.append((prev_end, N))
print("大空隙 %d 个:" % len(gaps))
for a, b in gaps:
    print("  0x%X..0x%X (%.1f MB)" % (a, b, (b - a) / 1048576))


def scan_plain(lo, hi, rowsize=12):
    """扫明文 {fi,ti,di}，fi 严格递增 ∈ literal，ti<N_TYPES，找最长 run"""
    best = (0, 0)  # (start, len)
    cur_start = None
    cur_len = 0
    prev = -1
    off = lo
    while off + rowsize <= hi:
        fi = struct.unpack_from("<I", BUF, off)[0]
        ti = struct.unpack_from("<I", BUF, off + 4)[0]
        ok = fi > prev and fi in lit and ti < N_TYPES
        if ok:
            if cur_len == 0:
                cur_start = off
            cur_len += 1
            prev = fi
            if cur_len > best[1]:
                best = (cur_start, cur_len)
        else:
            cur_len = 0
            prev = -1
        off += rowsize
    return best


print("\n空隙内明文扫描（12B 行）：")
for lo, hi in gaps:
    st, ln = scan_plain(lo & ~3, hi)
    if ln > 8:
        print("  0x%X..0x%X: 最长 run %d 行 @0x%X" % (lo, hi, ln, st))
