# -*- coding: utf-8 -*-
import sys
from collections import defaultdict, Counter
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4src import lz4_srcmap

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()

for OFF, SFSZ, PXSZ, NAME in ((137, 5088, 4096, "Add"), (1301, 5044, 16896, "BackIcon")):
    out, src_of, origin, used = lz4_srcmap(raw[OFF:])
    print("=== %s body@%d ===" % (NAME, OFF))
    print("  解压 %d B, 消耗 %d B" % (len(out), used))
    px_lo, px_hi = SFSZ, SFSZ + PXSZ
    if len(out) < px_hi:
        print("  !! 解压不足，实际 %d < 期望 %d" % (len(out), px_hi)); continue

    lit = sum(1 for i in range(px_lo, px_hi) if src_of[i] >= 0)
    cpy = PXSZ - lit
    print("  像素区 %d B: 字面量 %d, 拷贝派生 %d" % (PXSZ, lit, cpy))

    # 每个字面量源被哪些输出使用
    use = defaultdict(list)
    for i, o in enumerate(origin):
        use[o].append(i)
    px_src = {origin[i] for i in range(px_lo, px_hi)}
    print("  像素区涉及的字面量源: %d 个" % len(px_src))

    cross = [s for s in px_src if any(i < px_lo or i >= px_hi for i in use[s])]
    print("  其中被“非像素区”共用的: %d 个" % len(cross))
    if cross:
        print("   前5个:", [(s, len(use[s])) for s in cross[:5]])

    # 若全部改成 0xFF，是否有冲突（某源还被要求保持别的值）
    print("  目标=全 0xFF 时，非像素区受影响的输出字节数: %d" % sum(
        1 for s in px_src for i in use[s] if i < px_lo or i >= px_hi))
    print()
