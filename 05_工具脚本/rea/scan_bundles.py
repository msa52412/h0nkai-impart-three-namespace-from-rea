# -*- coding: utf-8 -*-
"""流式扫描 Asb 包，定位指定字节串出现在哪个包、什么偏移
   用法: python scan_bundles.py <目录> 关键词1 [关键词2 ...]
"""
import mmap
import os
import sys


def scan(path, needles):
    hits = []
    try:
        with open(path, "rb") as f:
            size = os.fstat(f.fileno()).st_size
            if size == 0:
                return hits
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                for nd in needles:
                    pos = 0
                    cnt = 0
                    first = -1
                    while True:
                        i = mm.find(nd, pos)
                        if i < 0:
                            break
                        if cnt == 0:
                            first = i
                        cnt += 1
                        pos = i + 1
                        if cnt >= 9999:
                            break
                    if cnt:
                        hits.append((nd, cnt, first))
    except (OSError, ValueError):
        pass
    return hits


def main():
    root = sys.argv[1]
    needles = [a.encode("utf-8") for a in sys.argv[2:]]
    if not needles:
        sys.exit("需要关键词")

    files = []
    for dp, _, fs in os.walk(root):
        for fn in fs:
            files.append(os.path.join(dp, fn))
    files.sort()
    print("扫描 %d 个文件，%d 个关键词" % (len(files), len(needles)))

    total = 0
    for p in files:
        h = scan(p, needles)
        if h:
            total += 1
            desc = ", ".join("%s×%d@%d" % (nd.decode("utf-8", "replace"), c, f)
                             for nd, c, f in h)
            print("  %s  [%s]" % (os.path.basename(p), desc))
            sys.stdout.flush()
    print("命中文件: %d" % total)


if __name__ == "__main__":
    main()
