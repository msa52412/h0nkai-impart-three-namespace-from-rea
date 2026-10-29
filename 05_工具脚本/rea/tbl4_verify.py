#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tbl4_verify.py —— 检验「表4 = 泛型方法实例化规格 (Il2CppMethodSpec)」假设。

判据：
  f2 = 方法定义索引（< 408,461）
  f1 >= 0  -> 方法自身是泛型方法（methods.tsv 的 genericContainer 非空）
  f0 >= 0  -> 方法所在类型是泛型类型（类型名含 ` 或 该类型出现在泛型容器里）
"""
import csv
import struct
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")
from rd import d, va2off  # noqa: E402

T4 = 0x187127630
N = 213854


def load_methods():
    m = {}
    with open("bh3_methods_v2.tsv", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            m[int(r["idx"])] = r
    return m


def load_types():
    t = {}
    for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
        p = line.split("\t")
        t[int(p[0])] = (p[1], p[2])
    return t


def main():
    meth = load_methods()
    types = load_types()
    o = va2off(T4)

    # 交叉表
    stat = {}
    bad_idx = 0
    bad_gm = 0
    bad_tp = 0
    n_f1 = 0
    n_f0 = 0
    both = 0
    for i in range(N):
        a, b, c = struct.unpack_from("<iii", d, o + i * 12)
        key = (a >= 0, b >= 0)
        stat[key] = stat.get(key, 0) + 1
        r = meth.get(c)
        if r is None:
            bad_idx += 1
            continue
        if a >= 0 and b >= 0:
            both += 1
        # f1 >= 0  => 方法自身泛型
        if b >= 0:
            n_f1 += 1
            if not r["genericContainer"]:
                bad_gm += 1
        # f0 >= 0 => 声明类型是泛型类型
        if a >= 0:
            n_f0 += 1
            nm = types.get(int(r["declTypeIdx"]), ("", ""))[1]
            if "`" not in nm:
                bad_tp += 1

    print("总条数 %d" % N)
    print("\n(f0>=0, f1>=0) 分布：")
    for k in sorted(stat):
        print("   f0>=0:%-5s f1>=0:%-5s  %7d  (%.2f%%)"
              % (k[0], k[1], stat[k], 100.0 * stat[k] / N))
    print("\n f2 越界（>408458）: %d" % bad_idx)
    print(" f1>=0 共 %d 条，其中方法非泛型: %d (%.2f%%)"
          % (n_f1, bad_gm, 100.0 * bad_gm / max(n_f1, 1)))
    print(" f0>=0 共 %d 条，其中声明类型非泛型: %d (%.2f%%)"
          % (n_f0, bad_tp, 100.0 * bad_tp / max(n_f0, 1)))
    print(" f0>=0 且 f1>=0（双层泛型）: %d" % both)

    # 抽样展示
    print("\n抽样（f1>=0，方法应为泛型方法）:")
    n = 0
    for i in range(N):
        a, b, c = struct.unpack_from("<iii", d, o + i * 12)
        if b >= 0 and a < 0:
            r = meth.get(c)
            if r:
                nm = types.get(int(r["declTypeIdx"]), ("", ""))[1]
                print("   [%6d] f1=%6d  %s::%s  <gc=%s>" % (i, b, nm, r["name"], r["genericContainer"]))
                n += 1
                if n >= 8:
                    break

    print("\n抽样（f0>=0，方法所在类型应为泛型类型）:")
    n = 0
    for i in range(N):
        a, b, c = struct.unpack_from("<iii", d, o + i * 12)
        if a >= 0 and b < 0:
            r = meth.get(c)
            if r:
                nm = types.get(int(r["declTypeIdx"]), ("", ""))[1]
                print("   [%6d] f0=%6d  %s::%s  <gc=%s>" % (i, a, nm, r["name"], r["genericContainer"]))
                n += 1
                if n >= 8:
                    break


if __name__ == "__main__":
    main()
