# -*- coding: utf-8 -*-
"""
离线复查：在已有 dump 里按 UTF-16LE 搜配置表指纹

动机
----
ctable_hunt.py 的 STRONG 指纹全是 ASCII 字节，扫完零命中，
于是当时判定「明文配置不在常驻内存」。

但 il2cpp 的 System.String 在内存里是 UTF-16LE：
    "Cover_11"  ->  43 00 6F 00 76 00 65 00 72 00 5F 00 31 00 31 00
用 data.find(b"Cover_11") 永远找不到。

本脚本对 dump/ 下已有文件做离线复查，两种编码都试，不碰活进程。

用法
----
    python dump_utf16_scan.py                # 扫 dump/ 全部 .bin
    python dump_utf16_scan.py --dir dump2    # 换目录
    python dump_utf16_scan.py --ctx 64       # 命中处打印前后 64 字节 hex
"""
import sys, os, struct, glob

HERE = os.path.dirname(os.path.abspath(__file__))

STRONG = [
    "SpriteOutput/WorldMap/OWEndless/Cover_11",
    "SpriteOutput/WorldMap/Entry/MutilTask_1",
    "SpriteOutput/WorldMap/Entry/Extra_1",
    "SpriteOutput/WorldMap/Entry/OWTask_1",
    "event/Immediately/newbie37/entrance_truecolor",
    "SpriteOutput/WorldMap/Entry/Avatar_Tutorial_Image",
    "SpriteOutput/WorldMap/Entry/Cover_4",
    "SpriteOutput/WorldMap/Entry/Regular_1_100",
]
WEAK = [
    "EntryImagePath", "EntryTitleImgPath", "ContentIDList", "FeatureType",
    "ExcelOutputAsset", "WorldMapCoverInfo",
]


def pats_for(s):
    return [
        ("ascii", s.encode("ascii", "ignore")),
        ("u16", s.encode("utf-16-le")),
        ("u16+len", struct.pack("<i", len(s)) + s.encode("utf-16-le")),
    ]


def scan_file(path, ctx):
    size = os.path.getsize(path)
    print("\n=== %s  (%.1f MB) ===" % (os.path.basename(path), size / 1048576))
    data = open(path, "rb").read()

    found_any = False
    for kind, group in (("STRONG", STRONG), ("weak", WEAK)):
        for s in group:
            for enc, pat in pats_for(s):
                p = data.find(pat)
                n = 0
                first = -1
                while p >= 0:
                    if n == 0:
                        first = p
                    n += 1
                    p = data.find(pat, p + 1)
                if n:
                    found_any = True
                    print("  [%s] %-52s enc=%-8s x%-3d @%#x"
                          % (kind, s[:52], enc, n, first))
                    if ctx and enc == "u16":
                        lo = max(0, first - ctx)
                        seg = data[lo:first + len(pat) + ctx]
                        print("        ctx: %s" % seg.hex(" "))
    if not found_any:
        print("  （无命中）")
    return found_any


def main():
    args = sys.argv[1:]
    d = os.path.join(HERE, "dump")
    if "--dir" in args:
        d = os.path.join(HERE, args[args.index("--dir") + 1])
    ctx = 0
    if "--ctx" in args:
        ctx = int(args[args.index("--ctx") + 1])

    files = sorted(glob.glob(os.path.join(d, "*.bin")),
                   key=os.path.getsize, reverse=True)
    if not files:
        print("目录里没有 .bin：%s" % d)
        return 2
    print("待查 %d 个文件，共 %.0f MB"
          % (len(files), sum(os.path.getsize(f) for f in files) / 1048576))

    any_hit = False
    for f in files:
        if scan_file(f, ctx):
            any_hit = True

    print("\n" + "=" * 60)
    if any_hit:
        print("[结论] 命中。配置表的字符串确实在内存里，之前是编码问题。")
    else:
        print("[结论] ASCII + UTF-16LE 双编码在这批 dump 里都零命中。")
        print("       注意：这批 dump 是 10-24 抓的，且当时不一定打开了挑战面板。")
        print("       要下结论必须对着「已打开挑战面板」的现场重新抓。")
    return 0 if any_hit else 1


if __name__ == "__main__":
    sys.exit(main())
