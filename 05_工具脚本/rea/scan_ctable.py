# -*- coding: utf-8 -*-
import re
P = r"D:/BH3/7.0/BH3_Data/StreamingAssets/ctable.dat"
d = open(P, "rb").read()
print("ctable.dat %d 字节" % len(d))
print("前64B:", d[:64].hex())
print("可读前64:", "".join(chr(c) if 32 <= c < 127 else "." for c in d[:64]))
for kw in (b"ChapterChallengeData", b"ChallengeMissionLink", b"OWEndless", b"WorldMap"):
    print("%-24s %s" % (kw.decode(), d.find(kw)))
names = sorted(set(m.group().decode() for m in re.finditer(rb"[A-Za-z_][A-Za-z0-9_]{5,60}", d)))
print("\n可读标识符 %d 个，前 40:" % len(names))
for n in names[:40]: print("   ", n)
