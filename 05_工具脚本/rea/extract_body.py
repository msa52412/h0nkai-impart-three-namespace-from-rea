# -*- coding: utf-8 -*-
"""extract_body —— 从 bodies_merged.tsv 里取某个 VA 的反编译体

bodies_merged.tsv 是「VA\\t代码」的 948MB 大表，Grep 工具会省略超长行，
所以单独写一个流式提取器。

用法:
    python extract_body.py 1819C5E00            # 打印
    python extract_body.py 1819C5E00 out.c      # 存文件
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, "bodies_merged.tsv")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    key = sys.argv[1].lower().lstrip("0x").upper()   # 首列是大写、不带 0x
    out = sys.argv[2] if len(sys.argv) > 2 else None
    if not os.path.exists(TSV):
        print("找不到 %s" % TSV)
        return 1

    hit = None
    with open(TSV, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith(key + "\t"):
                hit = line
                break
    if hit is None:
        print("没有 VA %s 的反编译体" % key)
        return 1

    body = hit.split("\t", 1)[1]
    if out:
        with open(out, "w", encoding="utf-8") as g:
            g.write(body)
        print("已写出 %s（%d 字符）" % (out, len(body)))
    else:
        print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
