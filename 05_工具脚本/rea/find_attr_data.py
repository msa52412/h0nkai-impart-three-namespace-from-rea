# -*- coding: utf-8 -*-
"""找 customAttributeData / ranges 表本体：
   已知: attr 总数 76,737；T5 c1 = 每镜像 attrStart（262402869+ 域, 差分=c2）
   c1 值很大（2.6 亿）——不是 attr 行号，是别的坐标。重新审视：
   c1[i] = 262402869..  单调、差分=c2。也许 c1 = attrDataOffset（字节）！
   262402869 ≈ 0xFA6F0C5 —— 不是文件偏移。也许加密坐标。
   换路：attr tuple 表按惯例 {start(24b),count(8b)} 或 {ownerToken, offset}。
   用「token 域」扫：owner token = 0x06xxxxxx(方法)/0x02xxxxxx(类型)/0x04字段/0x01..."""
import struct
from collections import Counter

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
N = len(BUF)

# 扫 8B 对 {token, x}: token 高字节 ∈ {0x01,0x02,0x04,0x06,0x0A?} 且低位合理
# 方法 token = 0x06000000 | (methodIdx+1)，方法 idx < 251708 → token ∈ [0x06000001, 0x063D6B0C]
print("扫 {0x06xxxxxx token, 任意} 8B run...")
best = []
i = 0x118
run0 = runlen = 0
while i + 8 <= N:
    t = struct.unpack_from("<I", BUF, i)[0]
    if 0x06000001 <= t <= 0x063D6B0C:
        if runlen == 0:
            run0 = i
        runlen += 1
        if runlen > best[1] if best else True:
            best = [run0, runlen]
        i += 8
    else:
        if runlen >= 30:
            if not best or runlen > best[1]:
                best = [run0, runlen]
        runlen = 0
        i += 8
if runlen >= 30 and (not best or runlen > best[1]):
    best = [run0, runlen]
if best:
    print("最长 run: 0x%X 长 %d" % (best[0], best[1]))
    for j in range(6):
        t, x = struct.unpack_from("<2I", BUF, best[0] + j * 8)
        print("   (%08X, %d)" % (t, x))
PYEOF = None
