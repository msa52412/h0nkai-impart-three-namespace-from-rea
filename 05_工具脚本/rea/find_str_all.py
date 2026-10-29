# -*- coding: utf-8 -*-
import os, sys
ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
PATS = [b"MapPanel0", b"WorldMapUIManager", b"Task_3", b"Challenge/Task"]
LIMIT = 6 * 1024 * 1024
hits = {}
for f in sorted(os.listdir(ASB)):
    if not f.endswith(".wmv"): continue
    p = os.path.join(ASB, f)
    try:
        with open(p, "rb") as fh:
            buf = fh.read(LIMIT)
    except Exception:
        continue
    got = [pat.decode() for pat in PATS if pat in buf]
    if got:
        hits[f] = got
        print("%-40s %10d  %s" % (f, os.path.getsize(p), got))
print("\n命中 %d 个包" % len(hits))
