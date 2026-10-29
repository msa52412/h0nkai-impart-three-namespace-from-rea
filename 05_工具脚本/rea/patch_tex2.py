# -*- coding: utf-8 -*-
"""把指定贴图改成纯色（按通道分配字面量值），长度不变、元数据零污染"""
import sys, os
from collections import defaultdict
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4src import lz4_srcmap
from pngtool import write_png

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
NAME = "f65865df27ea6a9e58bf8f1f3b01bdcd.wmv"
OUTDIR = r"D:/Carol-start/_rea/patch_asb"
TEXDIR = r"D:/Carol-start/_rea/tex"

SPECS = [(137, 5088, 4096, 32, 32, "Add", (255, 0, 255, 255)),
         (1301, 5044, 16896, 88, 48, "BackIcon", (255, 0, 255, 255))]


def build(raw, off, sfsz, pxsz, color):
    out, src_of, origin, used = lz4_srcmap(raw[off:])
    assert len(out) >= sfsz + pxsz
    lo, hi = sfsz, sfsz + pxsz
    use = defaultdict(list)
    for i, o in enumerate(origin):
        use[o].append(i)

    patch = {}
    covered = 0
    mixed = 0
    for s, idxs in use.items():
        if not all(lo <= i < hi for i in idxs):
            continue
        cs = {(i - lo) % 4 for i in idxs}
        if len(cs) == 1:
            patch[s] = color[list(cs)[0]]
        else:
            patch[s] = 0xFF
            mixed += 1
        covered += len(idxs)
    return dict(out=out, lo=lo, hi=hi, patch=patch, covered=covered,
                mixed=mixed, total=pxsz, exclusive=len(patch))


def main():
    raw = open(os.path.join(ASB, NAME + ".orig"), "rb").read()
    buf = bytearray(raw)
    os.makedirs(OUTDIR, exist_ok=True); os.makedirs(TEXDIR, exist_ok=True)

    for off, sfsz, pxsz, w, h, nm, color in SPECS:
        b = build(raw, off, sfsz, pxsz, color)
        print("=== %s 目标色 %s ===" % (nm, color))
        print("  独占字面量 %d (其中跨通道 %d)" % (b["exclusive"], b["mixed"]))
        print("  覆盖像素区 %d/%d = %.1f%%" % (b["covered"], b["total"], 100.0*b["covered"]/b["total"]))
        for s, v in b["patch"].items():
            buf[off + s] = v
        out2, _, _, _ = lz4_srcmap(bytes(buf)[off:])
        write_png(os.path.join(TEXDIR, nm + "_color.png"), w, h, out2[b["lo"]:b["hi"]])
        print("  元数据区未变:", out2[:b["lo"]] == b["out"][:b["lo"]])
        print("  预览:", os.path.join(TEXDIR, nm + "_color.png"))

    diffs = [i for i in range(len(raw)) if raw[i] != buf[i]]
    print("\n差异字节 %d 个, 范围 %s..%s" % (len(diffs), diffs[0], diffs[-1]))
    print("长度 %d -> %d" % (len(raw), len(buf)))
    dst = os.path.join(OUTDIR, NAME)
    open(dst, "wb").write(bytes(buf))
    print("已生成:", dst)


if __name__ == "__main__":
    main()
