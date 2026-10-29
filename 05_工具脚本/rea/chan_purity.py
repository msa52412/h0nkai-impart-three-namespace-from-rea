# -*- coding: utf-8 -*-
import sys
from collections import defaultdict
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4src import lz4_srcmap

raw = open(r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc/f65865df27ea6a9e58bf8f1f3b01bdcd.wmv.orig","rb").read()

for off, sfsz, pxsz, nm in ((137,5088,4096,"Add"), (1301,5044,16896,"BackIcon")):
    out, src_of, origin, used = lz4_srcmap(raw[off:])
    lo, hi = sfsz, sfsz+pxsz
    use = defaultdict(list)
    for i, o in enumerate(origin):
        use[o].append(i)
    pure = 0; mixed = 0; mixed_samples = []
    chans = defaultdict(set)
    for s, idxs in use.items():
        if not all(lo <= i < hi for i in idxs):
            continue
        cs = {(i - lo) % 4 for i in idxs}
        if len(cs) == 1:
            pure += 1; chans[list(cs)[0]].add(s)
        else:
            mixed += 1
            if len(mixed_samples) < 5: mixed_samples.append((s, sorted(cs), len(idxs)))
    print("=== %s 像素独占字面量 %d 个 ===" % (nm, pure + mixed))
    print("  通道纯净: %d, 跨通道: %d" % (pure, mixed))
    if mixed_samples: print("  跨通道样例:", mixed_samples)
    print("  各通道字面量数: R=%d G=%d B=%d A=%d" % tuple(len(chans[c]) for c in range(4)))
