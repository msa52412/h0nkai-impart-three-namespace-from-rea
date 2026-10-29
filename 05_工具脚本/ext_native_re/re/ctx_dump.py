import os
import re
import sys

BASE = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
PAT = re.compile(rb"[\x20-\x7e]{6,}")


def ctx(name, keys, maxrun=40):
    p = os.path.join(BASE, name)
    d = open(p, 'rb').read()
    print("=" * 92)
    print(name, len(d))
    seen = set()
    n = 0
    for m in PAT.finditer(d):
        s = m.group()
        if any(k in s for k in keys):
            if s in seen:
                continue
            seen.add(s)
            n += 1
            if n > maxrun:
                print("   ...")
                break
            print("   %s" % s.decode('ascii', 'replace')[:160])


ctx("0a95a3510bffb1a31fdef2cae36e8783.wmv",
    [b"WorldMap", b"worldmap", b"Abyss", b"abyss", b"Cover_", b"cover_", b"Task_", b"Quantum"])
print()
ctx("a760d70eb463ac3e290a733cfd35d18f.wmv",
    [b"worldmap", b"Cover_", b"cover_"])
