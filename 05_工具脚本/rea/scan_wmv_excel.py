# -*- coding: utf-8 -*-
"""在全部 wmv 中裸字节搜索 Excel 配置表特征串"""
import os, sys, glob, time

D = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc"
KW = [b"ContentIDList", b"forceShowContent", b"EntryDetailImagePath", b"BookTestCover"]
CHUNK = 8 * 1024 * 1024
OV = 64

def main():
    fs = sorted(glob.glob(os.path.join(D, "*.wmv")))
    print("wmv 文件数:", len(fs), flush=True)
    total = sum(os.path.getsize(p) for p in fs)
    print("总大小: %.2f GB" % (total / 2**30), flush=True)
    t0 = time.time()
    hits = []
    done = 0
    for p in fs:
        sz = os.path.getsize(p)
        with open(p, "rb") as f:
            prev = b""
            off = 0
            while True:
                buf = f.read(CHUNK)
                if not buf:
                    break
                data = prev + buf
                for k in KW:
                    i = data.find(k)
                    while i >= 0:
                        hits.append((os.path.basename(p), off - len(prev) + i, k.decode()))
                        i = data.find(k, i + 1)
                prev = data[-OV:]
                off += len(buf)
        done += sz
        print("  %-46s %6.2f%%  hits=%d" % (os.path.basename(p), done * 100.0 / total, len(hits)), flush=True)
    print("\n耗时 %.1fs" % (time.time() - t0))
    print("命中:", len(hits))
    for h in hits[:50]:
        print("  %s @%d  %s" % h)
    with open(r"D:\Carol-start\_rea\_wmv_excel_hits.txt", "w", encoding="utf-8") as fo:
        for h in hits:
            fo.write("%s\t%d\t%s\n" % h)

if __name__ == "__main__":
    main()
