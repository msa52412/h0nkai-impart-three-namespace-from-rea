#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
路线 B 第一刀：从字符串锚点定位 metadata 解密例程。

已知（实测）：
  - UserAssembly.dll 只导入 8 个 DLL，ADVAPI32 里只有 CryptGenRandom，
    没有任何 CryptDecrypt / BCryptDecrypt -> 解密是纯软件自实现。
  - "global-metadata.dat" 全文件只出现 1 次，VA = 0x1881A2478（.rdata）
  - "MHY" 出现 2 次，VA = 0x187AF09F8（.rdata）-> 文件魔数校验很可能就在这附近

做法：
  1. 在 .text + il2cpp 两个可执行节里扫 RIP 相对引用（lea / mov / cmp）
  2. 命中后，用 .pdata 的 RUNTIME_FUNCTION 表反查该地址属于哪个函数（给函数起止）
  3. 打印命中点前后 64 字节机器码 + capstone 反汇编，人工判断语义

用法：
    python find_meta_decrypt.py                  # 扫两个锚点
    python find_meta_decrypt.py 0x1881A2478      # 扫指定 VA
"""
import os
import struct
import sys

import pefile

HERE = os.path.dirname(os.path.abspath(__file__))
DLL = r"Z:\AI\7.0\BH3_Data\Native\UserAssembly.dll"

# 已实测的锚点
ANCHORS = {
    0x1881A2478: "global-metadata.dat",
    0x187AF09F8: "MHY (魔数)",
}

EXEC_SECS = (b".text", b"il2cpp")


def va2off(pe, va):
    ib = pe.OPTIONAL_HEADER.ImageBase
    rva = va - ib
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData):
            return s.PointerToRawData + (rva - s.VirtualAddress)
    return None


def off2va(pe, off):
    for s in pe.sections:
        if s.PointerToRawData <= off < s.PointerToRawData + s.SizeOfRawData:
            return pe.OPTIONAL_HEADER.ImageBase + s.VirtualAddress + (off - s.PointerToRawData)
    return None


def load_pdata(pe, data):
    """解析 .pdata -> [(begin_rva, end_rva)]，按 begin 排序"""
    seg = [s for s in pe.sections if s.Name.rstrip(b"\0") == b".pdata"]
    if not seg:
        return []
    s = seg[0]
    raw = data[s.PointerToRawData:s.PointerToRawData + s.SizeOfRawData]
    out = []
    for i in range(0, len(raw) - 12 + 1, 12):
        begin, end, unwind = struct.unpack_from("<III", raw, i)
        if begin == 0 or end == 0 or end <= begin:
            continue
        if end > 0x0C000000:
            continue
        out.append((begin, end))
    out.sort()
    return out


def find_func(pdata, rva):
    """二分找包含 rva 的函数"""
    lo, hi = 0, len(pdata) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        b, e = pdata[mid]
        if rva < b:
            hi = mid - 1
        elif rva >= e:
            lo = mid + 1
        else:
            return b, e
    return None


def scan_ripref(data, pe, target_va):
    """扫 RIP 相对引用：REX? opcode modrm(mod=00,rm=101) disp32"""
    hits = []
    ib = pe.OPTIONAL_HEADER.ImageBase
    for s in pe.sections:
        if s.Name.rstrip(b"\0") not in EXEC_SECS:
            continue
        start = s.PointerToRawData
        end = start + s.SizeOfRawData
        buf = data[start:end]
        sec_va = ib + s.VirtualAddress
        n = len(buf)
        for p in range(n - 8):
            b = buf[p]
            # 只关心 lea(8D) / mov(8B) / cmp(3B/39) / movzx(0F B6)
            if b not in (0x8D, 0x8B, 0x3B, 0x39):
                continue
            modrm = buf[p + 1]
            if (modrm & 0xC7) != 0x05:
                continue
            rex = buf[p - 1] if p >= 1 else 0
            has_rex = 0x40 <= rex <= 0x4F
            insn_start = p - 1 if has_rex else p
            insn_len = (3 if has_rex else 2) + 4
            disp = struct.unpack_from("<i", buf, p + 2)[0]
            va = sec_va + p
            tgt = va + (insn_len - (p - insn_start)) + disp
            if tgt == target_va:
                hits.append((va - (1 if has_rex else 0), s.Name.rstrip(b"\0").decode()))
    return hits


def scan_absqword(data, pe, target_va):
    """扫 .data/.rdata 里是否存了该 VA 的绝对 qword（后续可能被间接引用）"""
    pat = struct.pack("<Q", target_va)
    hits = []
    pos = data.find(pat)
    while pos != -1:
        va = off2va(pe, pos)
        if va:
            hits.append((va, "abs-qword"))
        pos = data.find(pat, pos + 1)
    return hits


def disasm(data, pe, va, n=80, before=0):
    try:
        from capstone import Cs, CS_ARCH_X86, CS_MODE_64
    except ImportError:
        return "(capstone 未安装)"
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    off = va2off(pe, va - before)
    if off is None:
        return "(VA 无法映射)"
    code = data[off:off + n]
    out = []
    for ins in md.disasm(code, va - before):
        out.append("  0x%X: %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
    return "\n".join(out[:26])


def main():
    targets = {}
    if len(sys.argv) > 1:
        targets[int(sys.argv[1], 16)] = "手动指定"
    else:
        targets = dict(ANCHORS)

    print("加载 %s ..." % DLL)
    data = open(DLL, "rb").read()
    pe = pefile.PE(data=data, fast_load=True)
    print("文件 %.1f MB  ImageBase=0x%X" % (len(data) / 1048576, pe.OPTIONAL_HEADER.ImageBase))

    pdata = load_pdata(pe, data)
    print(".pdata 函数条目: %d" % len(pdata))
    print()

    for tva, label in targets.items():
        print("=" * 78)
        print("锚点 0x%X  (%s)" % (tva, label))
        print("=" * 78)

        hits = scan_ripref(data, pe, tva)
        print("  代码节 RIP 相对引用: %d 处" % len(hits))
        for va, sec in hits:
            rva = va - pe.OPTIONAL_HEADER.ImageBase
            f = find_func(pdata, rva)
            fs = ("函数 0x%X ~ 0x%X (len 0x%X, 命中点 +0x%X)"
                  % (f[0] + pe.OPTIONAL_HEADER.ImageBase, f[1] + pe.OPTIONAL_HEADER.ImageBase,
                     f[1] - f[0], rva - f[0])) if f else "(不在任何函数内)"
            print()
            print("  --- 命中 0x%X  [%s]  %s" % (va, sec, fs))
            print(disasm(data, pe, va, 96, before=24))

        qs = scan_absqword(data, pe, tva)
        if qs:
            print()
            print("  绝对 qword 引用: %d 处" % len(qs))
            for va, _ in qs[:10]:
                print("    0x%X" % va)
        print()


if __name__ == "__main__":
    main()
