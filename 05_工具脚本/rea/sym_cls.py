# -*- coding: utf-8 -*-
"""按类名子串列出符号表里的类与代表方法

用法:
    python sym_cls.py WorldMap            # 类名含 WorldMap 的所有类 + 方法数
    python sym_cls.py WorldMap --full     # 连方法名一起列
    python sym_cls.py WorldMap --max 60   # 最多列 60 个类
"""
import sys, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
SYM = os.path.join(HERE, "bh3_symtab.tsv")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    needle = sys.argv[1]
    full = "--full" in sys.argv
    mx = 40
    if "--max" in sys.argv:
        mx = int(sys.argv[sys.argv.index("--max") + 1])

    meth = collections.defaultdict(list)
    with open(SYM, "r", encoding="utf-8", errors="replace") as f:
        next(f, None)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            cls = p[2]
            if needle.lower() not in cls.lower():
                continue
            meth[cls].append((p[0], p[3], p[5] if len(p) > 5 else ""))

    print("类名含 %r 的类: %d 个" % (needle, len(meth)))
    for cls, lst in sorted(meth.items(), key=lambda kv: -len(kv[1]))[:mx]:
        print("\n%-52s  %d 个方法" % (cls, len(lst)))
        if full:
            for rva, name, params in lst[:40]:
                print("    %-9s %-34s %s" % (rva, name, params[:60]))
        else:
            names = [x[1] for x in lst[:14]]
            print("    " + ", ".join(names) + (" ..." if len(lst) > 14 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
