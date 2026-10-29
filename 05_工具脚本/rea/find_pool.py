# -*- coding: utf-8 -*-
"""反推 fieldDefaultValues 值池基址 X：
   约束（c1=字节偏移）：
     AttributeTargets: [X+204..X+236) = 1,2,4,8,16,32,64,128 (Assembly..Property)
     DateTimeKind:     [X+1248]=1, [X+1252]=2
     DayOfWeek:        [X+1256..X+1284) = 0,1,2,3,4,5,6
     Int32:            [X+1972]=0x7FFFFFFF, [X+1976]=0x80000000
     Byte.MaxValue:    [X+293]=0xFF (1 字节)"""
import struct

BUF = open(r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat", "rb").read()
N = len(BUF)

# 最硬的锚: X+1972 处 int32=0x7FFFFFFF 且 X+1976 处 int32=0x80000000
pat = struct.pack("<Ii", 0x7FFFFFFF, -0x80000000)
i = BUF.find(pat)
cands = []
while i >= 0:
    X = i - 1972
    if X >= 0:
        cands.append(X)
    i = BUF.find(pat, i + 1)
print("MaxValue/MinValue 锚: %d 个候选 X" % len(cands))

for X in cands:
    ok = True
    # AttributeTargets powers of 2
    for k, v in enumerate([1, 2, 4, 8, 16, 32, 64, 128]):
        if struct.unpack_from("<I", BUF, X + 204 + k * 4)[0] != v:
            ok = False
            break
    if not ok:
        print("X=0x%X: AttributeTargets 不匹配" % X)
        continue
    # DayOfWeek 0..6
    dw = struct.unpack_from("<7I", BUF, X + 1256)
    if list(dw) != [0, 1, 2, 3, 4, 5, 6]:
        print("X=0x%X: DayOfWeek=%s 不匹配" % (X, list(dw)))
        continue
    # DateTimeKind
    dtk = struct.unpack_from("<2I", BUF, X + 1248)
    if list(dtk) != [1, 2]:
        print("X=0x%X: DateTimeKind=%s 不匹配" % (X, list(dtk)))
        continue
    b = BUF[X + 293]
    print("★ X=0x%X 全部匹配! Byte.MaxValue@293=0x%02X (期望 0xFF: %s)" %
          (X, b, "OK" if b == 0xFF else "FAIL"))
