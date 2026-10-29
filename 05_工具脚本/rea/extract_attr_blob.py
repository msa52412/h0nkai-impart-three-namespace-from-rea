# -*- coding: utf-8 -*-
"""CustomAttribute 完整链条定位（全部坐标已贯通）：
   ① 方法表+0x14 → attrIdx（1 基，1..76737，76,737 owner 记录）
   ② generator 数组 @0x7C4F64..0xAC104C（780,234 条 ctor token 记录）
   ③ E8C（=值池 0x1D79938）起始处 = attr 参数数据（96,0,1,2,3,4,... 枚举参数流）
   落盘: attrIdx→generator 序列切分表（方法 0 的 range [1,?) 长度=方法 1 attrIdx 差）
   注: attrIdx 是【generator 数组的 1 基 start】—— 方法 i 的 range =
       [attrIdx[i], attrIdx[i+1])（相邻共享 start 的按 0 长处理）"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
TBL_M = 0x118 + 0xFA8318
N_METH = 251708
GEN_S = 0x7C4F64

def prf(i):
    x = ((i * 0xB069) ^ 0x3E382F2D) & M64
    x = (x * 0x24147491) & M64
    x = (x ^ 0xF997B4A800) >> 10
    x = (x * 0x3857AACA) & M64
    return x >> 0xE

# 1) 全部方法的 attrIdx
attr = []
for i in range(N_METH):
    raw = struct.unpack_from("<I", BUF, TBL_M + i * 0x20 + 0x14)[0]
    attr.append((((raw + 0xBD6FC398) & M32) ^ prf(i)) & 0xFFFFFF)

# 2) generator 数组（含 00 跳过？—— 不跳过，00 也是记录位）
#    方法 i 的 range = [attr[i], attr[i+1])
names = {}
for ln in open(r"D:\Carol-start\_rea\bh3_methods.txt", encoding="utf-8"):
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 4:
        names[int(p[0])] = p[3]

n_out = 0
with open(r"D:\Carol-start\_rea\bh3_method_attrs.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("methodIdx\tmethodName\tattrStart\tattrCount\tctors\n")
    for i in range(N_METH):
        s = attr[i]
        e = attr[i + 1] if i + 1 < N_METH else 780235
        if s == 0 or s > 76737 or e < s:
            continue
        cnt = e - s
        if cnt <= 0 or cnt > 500:
            continue
        # ctor tokens: generator 数组 [s-1, e-1) (1基→0基)
        ctors = []
        for j in range(s - 1, e - 1):
            b = BUF[GEN_S + j * 4: GEN_S + j * 4 + 4]
            if b[3] == 0x60:
                ctors.append(str(b[0] | b[1] << 8 | b[2] << 16))
            elif b[3] == 0xC0:
                ctors.append("T" + str(b[0] | b[1] << 8 | b[2] << 16))
        f.write("%d\t%s\t%d\t%d\t%s\n" % (i, names.get(i, "?"), s, cnt, ",".join(ctors)))
        n_out += 1
print("方法 attribute 展开表: %d 行" % n_out)

# 3) 验证: 方法0 range=[1,2) → ctor=3904(GetHashCode? 不对,应是 attr ctor)
print("\n方法 0..3 展开样例:")
for ln in list(open(r"D:\Carol-start\_rea\bh3_method_attrs.tsv", encoding="utf-8"))[1:5]:
    p = ln.rstrip("\n").split("\t")
    ct = p[4].split(",")
    print("  方法%-6s %-20s ctors=%s" % (p[0], p[1][:20], [names.get(int(c), "?") if c.isdigit() else c for c in ct][:4]))
