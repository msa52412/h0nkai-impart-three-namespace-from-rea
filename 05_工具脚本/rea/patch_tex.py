# -*- coding: utf-8 -*-
"""定向修改 .wmv 内的贴图像素（LZ4 字面量级，长度不变）
   只改“独占于像素区”的字面量，保证元数据/对象表零污染
"""
import sys, os
from collections import defaultdict
sys.path.insert(0, r"D:/Carol-start/_rea")
from lz4src import lz4_srcmap
from pngtool import write_png

ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
NAME = "f65865df27ea6a9e58bf8f1f3b01bdcd.wmv"
OUTDIR = r"D:/Carol-start/_rea/patch_asb"
TEXDIR = r"D:/Carol-start/_rea/tex"

# (流起点, SF大小, 像素字节数, 宽, 高, 名字)
SPECS = [(137, 5088, 4096, 32, 32, "Add"),
         (1301, 5044, 16896, 88, 48, "BackIcon")]


def plan(raw, off, sfsz, pxsz):
    out, src_of, origin, used = lz4_srcmap(raw[off:])
    assert len(out) >= sfsz + pxsz, "解压不足 %d" % len(out)
    lo, hi = sfsz, sfsz + pxsz
    use = defaultdict(list)
    for i, o in enumerate(origin):
        use[o].append(i)
    exclusive = set()
    for s, idxs in use.items():
        if all(lo <= i < hi for i in idxs):
            exclusive.add(s)
    covered = sum(1 for i in range(lo, hi) if origin[i] in exclusive)
    return dict(out=out, src_of=src_of, origin=origin, used=used, lo=lo, hi=hi,
                use=use, exclusive=exclusive, covered=covered)


def apply(raw, off, plan_, newval=0xFF):
    buf = bytearray(raw)
    for s in plan_["exclusive"]:
        buf[off + s] = newval
    return bytes(buf)


def main():
    raw = open(os.path.join(ASB, NAME + ".orig"), "rb").read()
    buf = bytearray(raw)
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(TEXDIR, exist_ok=True)

    for off, sfsz, pxsz, w, h, nm in SPECS:
        p = plan(raw, off, sfsz, pxsz)
        print("=== %s ===" % nm)
        print("  字面量源总数 %d, 独占于像素区 %d" % (len(p["use"]), len(p["exclusive"])))
        print("  像素区被独占字面量覆盖: %d / %d (%.1f%%)" % (
            p["covered"], pxsz, 100.0 * p["covered"] / pxsz))
        for s in p["exclusive"]:
            buf[off + s] = 0xFF
        # 预览
        out2, _, _, _ = lz4_srcmap(bytes(buf)[off:])
        px = out2[p["lo"]:p["hi"]]
        write_png(os.path.join(TEXDIR, nm + "_patched.png"), w, h, px)
        # 元数据区一致性
        same = out2[:p["lo"]] == p["out"][:p["lo"]]
        print("  元数据/对象表区是否完全未变: %s" % same)
        print("  预览: %s" % os.path.join(TEXDIR, nm + "_patched.png"))

    # 差异统计
    diffs = [i for i in range(len(raw)) if raw[i] != buf[i]]
    print("\n全文件差异字节: %d, 范围 %s..%s, 长度 %d -> %d" % (
        len(diffs), diffs[0] if diffs else "-", diffs[-1] if diffs else "-", len(raw), len(buf)))
    dst = os.path.join(OUTDIR, NAME)
    open(dst, "wb").write(bytes(buf))
    print("已生成:", dst)


if __name__ == "__main__":
    main()
