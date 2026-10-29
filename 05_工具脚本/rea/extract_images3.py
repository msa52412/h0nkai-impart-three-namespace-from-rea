# -*- coding: utf-8 -*-
"""images 表（T5）全解 v3：64 位 ikey，输出全部 192 个镜像与语义列"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
BASE = 0x118
POOL_ABS = BASE + 0x24AAC18
T5 = BASE + 0x1C2A198
N_IMG = 192

K_MUL = (-0x394A88E12FFFF3A0) & M64
K_ADD = 0x53DB1FC7E9ECC644
K_STEP = 0x64C7CE0352814CF6

_cache = {}
def decrypt_str(pid):
    if pid in _cache:
        return _cache[pid]
    length = (pid >> 24) & 0xFF
    if length == 0:
        return ""
    if length > 0x100:
        return None
    index = pid & 0xFFFFFF
    src = POOL_ABS + index
    nb = (length + 7) >> 3
    if src + nb * 8 > len(BUF):
        return None
    key = (index * K_MUL + K_ADD) & M64
    out = bytearray()
    for b in range(nb):
        c = struct.unpack_from("<Q", BUF, src + b * 8)[0]
        out += (c ^ key).to_bytes(8, "little")
        key = (key + K_STEP) & M64
    s = bytes(out[:length]).decode("utf-8", "replace")
    _cache[pid] = s
    return s

def ikey(i):
    v = (i * 0x14C3BD9234D3) & M64
    v >>= 9
    v = (v + 0x48C65E21) & M64
    v = (v * 0x22343DDF) & M64
    v >>= 0x15
    return v & M32

rows = []
for i in range(N_IMG):
    r = struct.unpack_from("<10I", BUF, T5 + i * 0x28)
    k = ikey(i)
    rows.append({
        "idx": i,
        "name": decrypt_str((r[5] - 0x3D7DC690 - k) & M32),
        "c0": (r[0] - 0x36D7455A - k) & M32,
        "c1": (r[1] - k + 0x1298B083) & M32,
        "c2": (r[2] - 0x3B4B92FD - k) & M32,
        "c3": (r[3] - k - 0x3640F13B) & M32,
        "c4": (r[4] - 0x7C293E16 - k) & M32,
        "c6": (r[6] - 0x12813D35 - k) & M32,
        "c7": (((r[7] ^ 0x16A0E2A5) - k) + 0x3A0AAEFE) & M32,
        "c8": (r[8] - 0x3D2E6FE3 - k) & M32,
        "c9": (((r[9] ^ 0x0CA5B561) - k) + 0x27FD9462) & M32,
    })

with open(r"D:\Carol-start\_rea\bh3_images.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("imageIdx\tname\tc0\tc1\tc2\tc3\tc4\tc6\tc7\tc8\tc9\n")
    for x in rows:
        f.write("%d\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" %
                (x["idx"], x["name"] or "?", x["c0"], x["c1"], x["c2"], x["c3"],
                 x["c4"], x["c6"], x["c7"], x["c8"], x["c9"]))

ok = sum(1 for x in rows if x["name"] and x["name"].endswith(".dll"))
print("镜像名 .dll 结尾: %d / 192" % ok)
print("\n语义列检验:")
# c3=typeStart c4=typeCount → sum(c4) ≈ 57487? c3 单调?
t3 = [x["c3"] for x in rows]
t4 = [x["c4"] for x in rows]
print("  sum(c4)=%d (类型数 57487?)  c3 单调: %s  c3 范围 0..%d" %
      (sum(t4), all(t3[i] <= t3[i+1] for i in range(191)), max(t3)))
# c8/c9 = customAttributeStart/Count: sum(c9) = attr 总数
print("  sum(c9)=%d  c8 单调: %s  c8 范围 0..%d" %
      (sum(x["c9"] for x in rows),
       all(rows[i]["c8"] <= rows[i+1]["c8"] for i in range(191)),
       max(x["c8"] for x in rows)))
# c0/c1/c2/c6/c7 语义
print("  c0 样例:", [rows[i]["c0"] for i in (0,1,2,3)], "(token?)")
print("  c2 样例:", [rows[i]["c2"] for i in (0,1,2,3)])
print("  c6 样例:", [rows[i]["c6"] for i in (0,1,2,3)], "(assemblyIdx? 0..191)")
print("  c7 样例:", [rows[i]["c7"] for i in (0,1,2,3)])
for i in (0, 1, 2, 3, 180, 191):
    x = rows[i]
    print("  [%3d] %-44s c8=%-8d c9=%d" % (i, x["name"][:44], x["c8"], x["c9"]))
