#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探针 2：Il2CppGenericClass(+8) 的 GenericInst 结构
  推测 Il2CppGenericInst = {u32 type_argc; pad4; Il2CppType** type_argv}
  验证 type_argv 每项指向 12 字节 Il2CTYPE，其 +10 是 type enum
"""
import struct
from collections import Counter

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
BASE = 0x118
TBL_VA = 0x186D41F80
NT = 57487

d = open(DLL, "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
coff = e + 4
nsec = struct.unpack_from("<H", d, coff + 2)[0]
optsz = struct.unpack_from("<H", d, coff + 16)[0]
opt = coff + 20
IB = struct.unpack_from("<Q", d, opt + 24)[0]
SECS = []
sh = opt + optsz
for i in range(nsec):
    o = sh + i * 40
    name = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((name, va, vs, rs, rp))


def va2off(va):
    rva = va - IB
    for name, vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


tbl_off = va2off(TBL_VA)

# 取一批 GenericClass 指针，统计 +8 指向的目标结构
seen = Counter()
samples = []
for idx in range(NT):
    p = struct.unpack_from("<Q", d, tbl_off + idx * 8)[0]
    po = va2off(p)
    if po is None or d[po + 10] != 0x15:
        continue
    gc = struct.unpack_from("<Q", d, po)[0]
    go = va2off(gc)
    if go is None:
        continue
    ci = struct.unpack_from("<Q", d, go + 8)[0]
    seen[ci] += 1
    if len(samples) < 12 and ci not in [s[0] for s in samples]:
        samples.append((ci, gc, idx))

print("GenericClass 总数 = %d" % sum(seen.values()))
print("distinct class_inst(+8) = %d" % len(seen))
print("top +8 值:", ["0x%X:%d" % (k, v) for k, v in seen.most_common(6)])

for ci, gc, idx in samples:
    co = va2off(ci)
    print("\n--- typedef[%d] GC=0x%X  classInst=0x%X off=0x%X" % (idx, gc, ci, co or 0))
    if co is None:
        print("    <not in image>")
        continue
    raw = d[co:co + 32]
    print("    raw: %s" % raw.hex(" "))
    argc = struct.unpack_from("<I", raw, 0)[0]
    argv = struct.unpack_from("<Q", raw, 8)[0]
    print("    argc=%d  argv=0x%X inImage=%s" % (argc, argv, va2off(argv) is not None))
    ao = va2off(argv)
    if ao is not None and argc <= 8:
        for k in range(argc):
            tp = struct.unpack_from("<Q", d, ao + k * 8)[0]
            to = va2off(tp)
            if to is None:
                print("      arg[%d] 0x%X <out>" % (k, tp))
                continue
            print("      arg[%d] typeVA=0x%X  data=0x%X ty=0x%02X bits=0x%02X"
                  % (k, tp, struct.unpack_from("<Q", d, to)[0],
                     d[to + 10], d[to + 11]))
