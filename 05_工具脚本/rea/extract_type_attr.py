# -*- coding: utf-8 -*-
"""类型表 attribute 列提取：每类型 {attrStart, attrCount}
   +0x14 (d[5]) attrStart: ((d[5] - 0x2822B502) - salt) & M32, 0xFFFFFFFF=-1
   +0x48 short attrCount: (s16 ^ C 或 s16 - C) - S16[i] —— 常数待定，用总数 76,737 校准
   初始化代码: uVar23 = (attrStart) + counter; 行号 → 0x5C 表 + counter 循环 count 次
   short 常数从反编译: (short)(*(short+0x48) + 0x1950) —— 即 count = raw16 - (-0x1950)?
   试多组常数，用 sum == 76737 且哨兵一致性筛"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
M32 = 0xFFFFFFFF
M64 = (1 << 64) - 1
T0 = 0x513B8
NT = 57487
STEP = 0x5C

SALT = []
for i in range(NT):
    x = (i * 0x1F17946EF935) & M64
    x = (x + 0xAFD81BAECAFDAC6) & M64
    x >>= 0x15
    x = (x + 0x54760499) & M64
    SALT.append(((x * 0x1125F1B6) & M64) & M32)
S16 = [(SALT[i] & 0xFFFF) - 0x10000 if SALT[i] & 0x8000 else (SALT[i] & 0xFFFF) for i in range(NT)]

TARGET = 76737

def s16(i, reloff):
    r = struct.unpack_from("<H", BUF, T0 + i * STEP + reloff)[0]
    return r - 0x10000 if r & 0x8000 else r

# attrStart
starts = []
for i in range(NT):
    d5 = struct.unpack_from("<I", BUF, T0 + i * STEP + 0x14)[0]
    starts.append(((d5 - 0x2822B502) - SALT[i]) & M32)

n_valid = sum(1 for v in starts if v != M32)
print("attrStart != -1 的类型: %d / %d" % (n_valid, NT))
vs = sorted(v for v in starts if v != M32)
print("attrStart 值域: %d..%d" % (vs[0], vs[-1]))

# attrCount @ +0x48: 反编译 sVar27=(short)(*(short+0x48)+0x1950) —— count= s16 + 0x1950 - S16?
# 但同列已用于 methodCount (u16c(i,0x48,-0x1950,False) = s - (-0x1950) - S16 = s + 0x1950 - S16)
# 冲突! methodCount 用了 +0x48。attr 的 short 是别的偏移 —— 反编译是 (short*)(lVar26+0x48)
# lVar26 = uVar23*0x5C + lVar7 —— 同一张类型表! +0x48 只有一个 short 槽。
# 再想: 反编译 sVar27 循环上限 (count_at_0x48 - sVar27) —— 但 methodCount 也在此。
# → (short)(*(short+0x48)+0x1950) 的解是【行内另一个 16 位】: +0x4A!
# il2cpp TypeDefinition: ... bitfield 区 (method_count:16, property_count:16, field_count:16,
#   event_count:16, nested_type_count:16, vtable_count:16, interfaces_count:16,
#   attribute_count:16 ...) —— attrCount 在 bitfield 群里
# 暴力: 试 +0x40..+0x56 所有 16 位槽 × {xor C, sub C} 用 sum==76737 筛
print("\n扫 16 位槽与常数 (目标 sum=%d):" % TARGET)
for reloff in range(0x40, 0x58, 2):
    for C in range(-0x10000, 0x10000, 1):
        pass  # 太慢，先只试 reloff 的裸值分布
    # 快速预筛：sum(s16 - S16) 各槽
    tot = 0
    ok = True
    for i in range(NT):
        if starts[i] == M32:
            continue
        v = (s16(i, reloff) - S16[i]) & 0xFFFF
        if v > 0x8000:
            ok = False
            break
        tot += v
    if ok:
        print("  +0x%02X: 裸 sum(s16-S16)=%d (差 %d)" % (reloff, tot, TARGET - tot))
