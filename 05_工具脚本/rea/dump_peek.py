# -*- coding: utf-8 -*-
"""dump 定点查看：hexdump + 附近可读字符串

用法:
    python dump_peek.py hit_00_206FE000_53MB.bin 0x1ddd444 --before 96 --after 512
    python dump_peek.py hit_00_206FE000_53MB.bin 0x1dbabae --strings 2048
"""
import sys, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DUMP = os.path.join(HERE, "dump")

PRINTABLE = re.compile(rb"[\x20-\x7e]{4,}")


def hexdump(data, base, width=16):
    for i in range(0, len(data), width):
        row = data[i:i + width]
        hx = " ".join("%02x" % b for b in row)
        tx = "".join(chr(b) if 0x20 <= b < 0x7f else "." for b in row)
        print("  %08X  %-*s  %s" % (base + i, width * 3 - 1, hx, tx))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    name = sys.argv[1]
    off = int(sys.argv[2], 0)
    args = sys.argv[3:]

    path = name if os.path.isabs(name) else os.path.join(DUMP, name)
    if not os.path.exists(path):
        print("找不到 %s" % path)
        return 2

    before, after, strs = 64, 256, 0
    if "--before" in args:
        before = int(args[args.index("--before") + 1], 0)
    if "--after" in args:
        after = int(args[args.index("--after") + 1], 0)
    if "--strings" in args:
        strs = int(args[args.index("--strings") + 1], 0)

    size = os.path.getsize(path)
    print("%s  %.1f MB" % (os.path.basename(path), size / 1048576))

    with open(path, "rb") as f:
        if strs:
            lo = max(0, off - strs)
            f.seek(lo)
            data = f.read(min(strs * 2, size - lo))
            print("\n--- 可读字符串 (0x%X ~ 0x%X) ---" % (lo, lo + len(data)))
            for m in PRINTABLE.finditer(data):
                s = m.group().decode("ascii")
                if len(s) >= 6:
                    print("  %08X  %s" % (lo + m.start(), s))
            return 0

        lo = max(0, off - before)
        f.seek(lo)
        data = f.read(before + after)
        print("\n--- hexdump 0x%X (目标 0x%X) ---" % (lo, off))
        hexdump(data, lo)

        print("\n--- 该段里的可读字符串 ---")
        for m in PRINTABLE.finditer(data):
            print("  %08X  %s" % (lo + m.start(), m.group().decode("ascii")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
