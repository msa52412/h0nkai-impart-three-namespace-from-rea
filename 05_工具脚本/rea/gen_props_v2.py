#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
属性表补全：从 getter 的返回类型（或 setter 的唯一参数类型）得到属性类型。

属性表本身不含类型（Il2CppPropertyDefinition 结构所限），
因此 propType = methods[getter].returnType
无 getter 时退化为 methods[setter].params[0]
"""
import csv
import collections

PROPS = r"D:\Carol-start\_rea\bh3_properties.tsv"
METHODS = r"D:\Carol-start\_rea\bh3_methods_v2.tsv"
OUT = r"D:\Carol-start\_rea\bh3_properties_v2.tsv"

M = {}
for line in open(METHODS, encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    if not f[0].isdigit():
        continue
    idx = int(f[0])
    M[idx] = (f[4], f[5], f[11])     # name, returnType, params

rows = list(csv.DictReader(open(PROPS, encoding="utf-8"), delimiter="\t"))
out = []
stat = collections.Counter()
for r in rows:
    gidx = int(r["getter"].split(":", 1)[0]) if r["getter"] else None
    sidx = int(r["setter"].split(":", 1)[0]) if r["setter"] else None
    pt = ""
    if gidx is not None and gidx in M:
        pt = M[gidx][1]
        stat["由 getter 返回类型"] += 1
    elif sidx is not None and sidx in M:
        ps = M[sidx][2]
        if ps:
            pt = ps.split(" ", 1)[0]
            stat["由 setter 参数类型"] += 1
        else:
            stat["setter 无参数"] += 1
    else:
        stat["无 getter/setter"] += 1
    out.append((r["typeIdx"], r["typeName"], r["propIdx"], r["propName"],
                pt or "?", r["token"], r["getter"], r["setter"]))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("typeIdx\ttypeName\tpropIdx\tpropName\tpropType\ttoken\tgetter\tsetter\n")
    for r in out:
        f.write("\t".join(r) + "\n")

print("[+] %s  (%d 条)" % (OUT, len(out)))
print("  类型来源: %s" % dict(stat))

print("\n[校验] 已知类型属性")
for t in ("System.String", "System.Exception", "UnityEngine.Transform",
          "System.Collections.Generic.List`1", "System.Array"):
    sub = [r for r in out if r[1] == t]
    print("  %-42s %2d 属性" % (t, len(sub)))
    for r in sub[:6]:
        print("      %-24s : %s" % (r[3], r[4]))
