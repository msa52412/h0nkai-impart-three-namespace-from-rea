#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描 Il2CppCodeGenModule 数组

结构（il2cpp 24.x）:
  Il2CppCodeGenModule {
    const char* moduleName;        // +0x00
    const uint32_t methodPointerCount;  // +0x08 (64位下可能是 u64)
    const Il2CppMethodPointer* methodPointers; // +0x10
    const InvokerMethod* invokerIndices;       // +0x18
    ...
  }
特征：数组元素 p -> [p+0]=指向只读字符串(模块名)  [p+8]=count  [p+0x10]=指向 count 个 .text 指针
目标：所有模块 count 之和 ≈ 408,461
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
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
    nm = d[o:o + 8].rstrip(b"\0").decode("latin1")
    vs, va, rs, rp = struct.unpack_from("<IIII", d, o + 8)
    SECS.append((nm, va, vs, rs, rp))
    print("%-8s VA=0x%X vsize=0x%-8X rsize=0x%-8X rptr=0x%X"
          % (nm, IB + va, vs, rs, rp))
print()


def va2off(va):
    rva = va - IB
    for nm, vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


def q(off):
    return struct.unpack_from("<Q", d, off)[0]


# .text 范围（含 il2cpp 段：0x18052E000 起，也放代码）
TLO = IB + [s for s in SECS if s[0] == ".text"][0][1]
il2 = [s for s in SECS if s[0] == "il2cpp"]
THI = (IB + il2[0][1] + il2[0][2]) if il2 else TLO + 0x600000
print(".text 代码区间 [0x%X, 0x%X)" % (TLO, THI))


def is_code(va):
    return TLO <= va < THI


# 候选：任意位置开始的指针数组，元素指向「模块结构体」
best = []
for nm, vaddr, vsize, rsize, rptr in SECS:
    if rsize < 0x20:
        continue
    n = rsize // 8
    runs = []
    st = None
    for i in range(n):
        v = q(rptr + i * 8)
        o = va2off(v) if v else None
        ok = False
        if o is not None and o + 0x18 <= len(d):
            cnt = q(o + 8)
            mpp = q(o + 0x10)
            if 0 < cnt < 60000 and mpp:
                mo = va2off(mpp)
                if mo is not None and mo + cnt * 8 <= len(d):
                    # 抽查前 8 个是否为代码指针
                    good = 0
                    chk = min(cnt, 8)
                    for k in range(chk):
                        if is_code(q(mo + k * 8)):
                            good += 1
                    ok = good >= max(chk - 1, 1)
        if ok:
            if st is None:
                st = i
        else:
            if st is not None and i - st >= 20:
                runs.append((nm, rptr + st * 8, i - st))
            st = None
    if st is not None and n - st >= 20:
        runs.append((nm, rptr + st * 8, n - st))
    best.extend(runs)

best.sort(key=lambda x: -x[2])
print("\n候选模块数组段（长度>=20）:")
for nm, off, c in best[:12]:
    # 汇总 count
    tot = sum(q(va2off(q(off + k * 8)) + 8) for k in range(c)
              if va2off(q(off + k * 8)) is not None)
    print("  %-8s off=0x%08X 元素=%d  count合计=%d" % (nm, off, c, tot))
if not best:
    print("  无")
