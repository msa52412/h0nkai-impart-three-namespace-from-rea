# -*- coding: utf-8 -*-
"""定位 CustomAttribute 表：
   层1 customAttributeGenerators（方法表）：4B/条，408,458 条，值为方法 RVA 或 -1
   层2 customAttributeStarter tuples：每个包含 attribute 的 token 一条 {start,count}
   先用「40 万条连续 RVA 域 int 数组」找层1（最硬指纹）"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
N = len(BUF)
N_METH = 408458

# 方法 RVA 域: 0x1000..0x52D7E6 (.text)
# 找长 run: 值域在 [0x1000, 0x52D7E6] 或 == 0xFFFFFFFF
best = (0, 0)
i = 0x118
run0 = 0
runlen = 0
while i + 4 <= N:
    v = struct.unpack_from("<I", BUF, i)[0]
    if (0x1000 <= v <= 0x52D7E6) or v == 0xFFFFFFFF:
        if runlen == 0:
            run0 = i
        runlen += 1
        if runlen > best[1]:
            best = (run0, runlen)
        i += 4
    else:
        runlen = 0
        i += 4
print("最长 RVA 域 run: 起点 0x%X 长度 %d (%.1f%% 的方法数)" % (best[0], best[1], 100.0 * best[1] / N_METH))

# 展示头部
S = best[0]
print("头部 16 条:", struct.unpack_from("<16I", BUF, S))
# 对齐猜测：S 应恰在段边界(0x118+段偏移)。S-0x118 = 段偏移
print("段偏移 = 0x%X" % (S - 0x118))
# 尾部
E = S + best[1] * 4
print("尾部 8 条:", struct.unpack_from("<8I", BUF, E - 32))
print("表尾 0x%X, 表后 32B: %s" % (E, BUF[E:E + 32].hex()))
