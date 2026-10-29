# -*- coding: utf-8 -*-
"""images 表（T5，0x28 字节/条）全解：192 个程序集的属性/字段范围
   表 @ 0x118+0x1C2A198（T5 段偏移 0x1C2A080），key 按 imageIdx"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1

# E1C ^ 0x72267500 = T5 段偏移 0x1C2A080 → 绝对 = 0x118 + 0x1C2A080 = 0x1C2A198
T5 = 0x118 + 0x1C2A198 - 0x118  # 直接用段偏移+0x118
T5 = 0x1C2A198
N_IMG = 192


def ikey(i):
    # iVar6 = ((i*0x14C3BD9234D3 >> 9) + 0x48C65E21) * 0x22343ddf >> 0x15
    v = (i * 0x14C3BD9234D3) & M64
    v >>= 9
    v = (v + 0x48C65E21) & M32
    v = (v * 0x22343DDF) & M64
    v >>= 0x15
    return v & M32


def dec_off(raw, sub, k):
    return ((raw - sub) - k) & M32


rows = []
for i in range(N_IMG):
    o = T5 + i * 0x28
    r = struct.unpack_from("<10I", BUF, o)
    k = ikey(i)
    img = {
        # piVar16[6] = r[0] - 0x36d7455a - k (xor 存进缓存，这里解真值)
        "f0_tokenRangeStart": dec_off(r[0], 0x36D7455A, k),
        "f1_?": (r[1] - k + 0x1298B083) & M32,
        "f2_?": ((r[2] - 0x3B4B92FD) - k) & M32,
        "f3_?": ((r[3]) - k - 0x3640F13B) & M32,
        "f4_?": ((r[4] - 0x7C293E16) - k) & M32,
        "f5_nameOff": dec_off(r[5], 0x3D7DC690, k),
        "f6_attrIdx?": dec_off(r[6], 0x12813D35, k),
        "f7_?": ((r[7] ^ 0x16A0E2A5) - k + 0x3A0AAEFE) & M32,
        "f8_?": ((r[8] - 0x3D2E6FE3) - k) & M32,
        "f9_?": ((r[9] ^ 0x0CA5B561) - k + 0x27FD9462) & M32,
    }
    rows.append(img)

# 名称在字符串池: STRPOOL @ 0x24AAC18 段内 f5_nameOff
STRPOOL = 0x118 + 0x24AAC18
def pool_str(off):
    # il2cpp 字符串池: '\0' 结尾字节流
    e = BUF.find(b"\0", STRPOOL + off)
    return BUF[STRPOOL + off:e].decode("utf-8", "replace")

print("192 个镜像（T5 表解出）:")
for i, img in enumerate(rows[:12]):
    print("  [%3d] %-46s f1=%-8d f2=%-8d f3=%-8d f6=%d" %
          (i, pool_str(img["f5_nameOff"])[:46], img["f1_?"], img["f2_?"], img["f3_?"], img["f6_attrIdx?"]))
print("  ...")
for i in (180, 181, 190, 191):
    img = rows[i]
    print("  [%3d] %-46s f1=%-8d f2=%-8d f3=%-8d f6=%d" %
          (i, pool_str(img["f5_nameOff"])[:46], img["f1_?"], img["f2_?"], img["f3_?"], img["f6_attrIdx?"]))

# f6 == -1 的数量（无 attribute 的镜像）
n_noattr = sum(1 for img in rows if img["f6_attrIdx?"] == 0xFFFFFFFF)
print("\nf6=-1 (无 attr 索引): %d / 192" % n_noattr)
# f6 值域
f6s = sorted(img["f6_attrIdx?"] for img in rows if img["f6_attrIdx?"] != 0xFFFFFFFF)
print("f6 值域: %d..%d" % (f6s[0], f6s[-1]) if f6s else "全 -1")
