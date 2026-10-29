import os
import sys

import UnityPy

OUT = r"D:/BH3/7.0/_ext/unpack"
fn = sys.argv[1]
path = os.path.join(OUT, fn)

env = UnityPy.load(path)
print("objects:")
for o in env.objects:
    print("  %-28s pathid=%s" % (o.type.name, o.path_id))

print()
print("--- 含 Task_3 的对象 ---")
for o in env.objects:
    try:
        raw = o.get_raw_data()
    except Exception as e:
        continue
    if b"Task_3" in raw:
        print("  命中 %s pathid=%s size=%d" % (o.type.name, o.path_id, len(raw)))
        i = raw.find(b"Task_3")
        print("   raw[%d:%d] = %r" % (max(0, i - 60), i + 80, raw[max(0, i - 60):i + 80]))
