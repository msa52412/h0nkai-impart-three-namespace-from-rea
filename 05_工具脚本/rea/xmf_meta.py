# -*- coding: utf-8 -*-
import os, struct
ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
p = os.path.join(ASB, "BlockMeta.xmf")
d = open(p, "rb").read()
print("size =", len(d), " 440*32 =", 440*32, " 差值 =", len(d) - 440*32)
print("头 48 字节:", d[:48].hex())
print()
TGT = bytes.fromhex("f65865df27ea6a9e58bf8f1f3b01bdcd")
i = d.find(TGT)
print("目标 16 字节 md5 出现位置:", i)
if i >= 0:
    print("上下文:", d[max(0,i-16):i+32].hex())
    # 假设记录按 32 字节对齐
    for base in range(0, 64):
        if (i - base) % 32 == 0:
            print("若记录起点偏移=%d，则记录号 = %d" % (base, (i - base)//32))
    print("按 i-16 对齐尝试: 记录号 =", (i-16)/32)
