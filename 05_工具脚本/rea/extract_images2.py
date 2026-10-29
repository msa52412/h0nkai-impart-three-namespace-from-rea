# -*- coding: utf-8 -*-
"""images 表（T5）全解 v2：pid → 解密名；验证 key 公式正确性"""
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
    v = (v + 0x48C65E21) & M32
    v = (v * 0x22343DDF) & M64
    v >>= 0x15
    return v & M32

# T5 记录 0x28=40 字节 10 列。已确认 f5=nameOff(pid 解)。
# il2cpp Image 标准: {nameIdx, assemblyIdx, typeStart, typeCount,
#   exportedTypeStart, exportedTypeCount, entryPointIndex, token,
#   customAttributeStart, customAttributeCount}
rows = []
for i in range(N_IMG):
    r = struct.unpack_from("<10I", BUF, T5 + i * 0x28)
    k = ikey(i)
    img = {
        "namePid": (r[5] - 0x3D7DC690 - k) & M32,
        "c0": (r[0] - 0x36D7455A - k) & M32,
        "c1": (r[1] - k + 0x1298B083) & M32,
        "c2": (r[2] - 0x3B4B92FD - k) & M32,
        "c3": (r[3] - k - 0x3640F13B) & M32,
        "c4": (r[4] - 0x7C293E16 - k) & M32,
        "c6": (r[6] - 0x12813D35 - k) & M32,
        "c7": (((r[7] ^ 0x16A0E2A5) - k) + 0x3A0AAEFE) & M32,
        "c8": (r[8] - 0x3D2E6FE3 - k) & M32,
        "c9": (((r[9] ^ 0x0CA5B561) - k) + 0x27FD9462) & M32,
    }
    img["name"] = decrypt_str(img["namePid"])
    rows.append(img)

ok = sum(1 for x in rows if x["name"] and x["name"].endswith(".dll"))
print("名字以 .dll 结尾: %d / 192" % ok)
for i in list(range(8)) + [180, 191]:
    x = rows[i]
    print("  [%3d] %-42s c0=%-8d c3=%-7d c4=%-6d c6=%-9d c8=%d" %
          (i, (x["name"] or "?")[:42], x["c0"], x["c3"], x["c4"], x["c6"], x["c8"]))

# 语义猜测验证：c3=typeStart c4=typeCount?（c3+c4 应单调覆盖 57487）
t3 = [x["c3"] for x in rows]
t4 = [x["c4"] for x in rows]
print("c3 单调递增:", all(t3[i] <= t3[i+1] for i in range(191)), " c3 末值:", t3[-1], "+c4末:", t3[-1]+t4[-1])
print("sum(c4) =", sum(t4))
# c6 分布（entryPoint?）
print("c6 样例:", [rows[i]["c6"] for i in range(6)])
# c8/c9（customAttributeStart/Count?）
print("c8 样例:", [rows[i]["c8"] for i in range(8)], " c9 样例:", [rows[i]["c9"] for i in range(8)])
