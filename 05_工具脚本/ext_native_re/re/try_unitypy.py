import os, glob, sys, traceback
import UnityPy

base = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
files = sorted(glob.glob(os.path.join(base, "*.wmv")), key=os.path.getsize)
print("total", len(files))
# 取最小的 3 个
for f in files[:3]:
    print("="*70)
    print(os.path.basename(f), os.path.getsize(f))
    with open(f,'rb') as fh:
        head = fh.read(0x60)
    print("head:", head[:0x40].hex(' '))
    try:
        env = UnityPy.load(f)
        objs = list(env.objects)
        print("  OK objects:", len(objs))
        from collections import Counter
        print("  types:", Counter(o.type.name for o in objs).most_common(8))
    except Exception as e:
        print("  FAIL:", type(e).__name__, e)
