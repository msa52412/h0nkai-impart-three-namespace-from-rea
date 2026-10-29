# -*- coding: utf-8 -*-
"""在资源文件中搜索指定文本（UTF-8 / UTF-16LE 两种编码）
   用法: python find_text.py <目录或文件> 文本1 [文本2 ...]
"""
import os
import sys


def patterns(text):
    out = []
    out.append(("utf8", text.encode("utf-8")))
    out.append(("utf16le", text.encode("utf-16-le")))
    return out


def scan_file(path, pats):
    hits = []
    try:
        size = os.path.getsize(path)
        if size == 0:
            return hits
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return hits
    for enc, p in pats:
        start = 0
        cnt = 0
        while True:
            i = data.find(p, start)
            if i < 0:
                break
            cnt += 1
            start = i + 1
            if cnt >= 3:
                break
        if cnt:
            hits.append((enc, cnt, i if cnt else -1))
    return hits


def main():
    root = sys.argv[1]
    texts = sys.argv[2:]
    if not texts:
        sys.exit("需要至少一个文本参数")
    pats = []
    for t in texts:
        pats += patterns(t)

    targets = []
    if os.path.isfile(root):
        targets = [root]
    else:
        for dp, _, fs in os.walk(root):
            for fn in fs:
                targets.append(os.path.join(dp, fn))

    print("扫描 %d 个文件，模式 %d 个" % (len(targets), len(pats)))
    found = 0
    for p in targets:
        h = scan_file(p, pats)
        if h:
            found += 1
            desc = ", ".join("%s×%d" % (e, c) for e, c, _ in h)
            print("  %s  [%s]" % (p, desc))
    print("命中文件数: %d" % found)


if __name__ == "__main__":
    main()
