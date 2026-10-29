#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""field_flags.py —— 从 Il2CppType.attrs 解出字段级 static 标志（真值，不是启发式）

背景：extract_fields.py 已经定位了
  · 字段表      F0 + fi*12，记录 {u32 A; u32 enc_typeIdx; u32 enc_nameId}
  · Il2CppType  由 tbl_off + tidx*8 取指针 → va2off → 结构体
结构体布局（与 extract_fields.py 的 ctype() 一致）：
  +0x00 u64  data（类索引 / 数组 / 泛型 / 指针目标）
  +0x08 u16  attrs          ← ★ FIELD_ATTRIBUTE_STATIC = 0x0010
  +0x0A u8   type
  +0x0B u8   num_mods / byref / pinned

输出 bh3_field_flags.tsv：typeIdx \t fieldIdx \t fieldName \t flags(hex) \t isStatic
"""
import struct

DLL = r"D:\Carol-start\_rea\UserAssembly_slim.dll"
META = r"Z:\AI\7.0\BH3_Data\Managed\Metadata\global-metadata.dat"
OUT = r"D:\Carol-start\_rea\bh3_field_flags.tsv"

M64 = (1 << 64) - 1
M32 = 0xFFFFFFFF
TBL_CTYPE = 0x186D41F80

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


def va2off(va):
    rva = va - IB
    for nm, vaddr, vsize, rsize, rptr in SECS:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return None if rsize == 0 else rptr + (rva - vaddr)
    return None


K1 = 0x7740EEFF55F40540
K2 = 0x49ED7F5AFCC4AF8


def prf(i):
    return (((i * K1 + K2) & M64) >> 0x11) & M32


tbl_off = va2off(TBL_CTYPE)
BUF = open(META, "rb").read()
FSIZE = len(BUF)

# 字段表偏移：与 extract_fields.py 相同
u32va = lambda va: struct.unpack_from("<I", d, va2off(va))[0]
FLD_OFF = (u32va(0x188198E84) - 0x2F59FE76) & M32
F0 = 0x118 + FLD_OFF

N_FIELDS = 419568


def field_attrs(fi):
    """返回 (attrs_u16, ty_u8) 或 None"""
    b = struct.unpack_from("<I", BUF, F0 + fi * 12 + 4)[0]
    tidx = ((b - prf(fi)) - 0xF2A3D7F) & M32
    if tidx == M32 or tidx >= 354184:
        return None
    p = struct.unpack_from("<Q", d, tbl_off + tidx * 8)[0]
    po = va2off(p)
    if po is None:
        return None
    attrs = struct.unpack_from("<H", d, po + 8)[0]
    ty = d[po + 10]
    return attrs, ty


FA_STATIC = 0x0010
FA_INITONLY = 0x0020
FA_LITERAL = 0x0040

if __name__ == "__main__":
    import sys
    # 抽样验证：按字段名找
    want = {}
    for line in open("bh3_fields.tsv", encoding="utf-8", errors="replace").read().splitlines()[1:]:
        p = line.split("\t")
        if len(p) < 5:
            continue
        key = (p[1], p[3])
        want[key] = int(p[2])

    checks = [
        ("System.DateTime", "TicksPerMillisecond"),
        ("System.DateTime", "MaxTicks"),
        ("System.DateTime", "dateData"),
        ("System.Threading.CancellationTokenSource", "s_nLists"),
        ("System.Threading.CancellationTokenSource", "CANNOT_BE_CANCELED"),
        ("System.Threading.CancellationTokenSource", "m_kernelEvent"),
        ("UnityEngine.Object", "OffsetOfInstanceIDInCPlusPlusObject"),
        ("UnityEngine.Object", "m_CachedPtr"),
        ("UnityEngine.UI.Selectable", "m_Navigation"),
        ("UnityEngine.UI.Selectable", "s_List"),
        ("System.Random", "MBIG"),
        ("System.Random", "SeedArray"),
    ]
    print("%-52s %-28s %-8s %-6s %s" % ("类型", "字段", "attrs", "type", "判定"))
    for t, f in checks:
        fi = want.get((t, f))
        if fi is None:
            print("%-52s %-28s 未找到" % (t, f))
            continue
        r = field_attrs(fi)
        if r is None:
            print("%-52s %-28s 取 attrs 失败" % (t, f))
            continue
        a, ty = r
        tag = []
        if a & FA_STATIC:
            tag.append("STATIC")
        if a & FA_LITERAL:
            tag.append("LITERAL")
        if a & FA_INITONLY:
            tag.append("INITONLY")
        print("%-52s %-28s 0x%-6x 0x%-4x %s" % (t, f, a, ty, "/".join(tag) or "instance"))

    if len(sys.argv) > 1 and sys.argv[1] == "--dump":
        with open(OUT, "w", encoding="utf-8") as fo:
            fo.write("fieldIdx\tattrs\ttypeIdx(y)\tisStatic\tisLiteral\n")
            n = 0
            for fi in range(N_FIELDS):
                r = field_attrs(fi)
                if r is None:
                    continue
                a, ty = r
                fo.write("%d\t0x%04x\t0x%02x\t%d\t%d\n"
                         % (fi, a, ty, 1 if a & FA_STATIC else 0,
                            1 if a & FA_LITERAL else 0))
                n += 1
        print("[+] %s  %d 字段" % (OUT, n))
