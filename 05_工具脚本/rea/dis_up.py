# -*- coding: utf-8 -*-
"""反汇编 UnityPlayer.dll 中 IL2CPP 加载区域"""
import sys
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

P = r"D:\BH3\7.0\UnityPlayer.dll"
pe = pefile.PE(P, fast_load=False)
ib = pe.OPTIONAL_HEADER.ImageBase
d = open(P, "rb").read()
secs = [(s.Name.rstrip(b"\0").decode(), ib + s.VirtualAddress, s.Misc_VirtualSize,
         s.PointerToRawData, s.SizeOfRawData) for s in pe.sections]

def va2off(va):
    for n, base, vsz, praw, rsz in secs:
        if base <= va < base + max(vsz, rsz):
            return praw + (va - base)
    return None

# 已知符号提示
KNOWN = {
    0x18133fbda: "WinVerifyTrust(导入跳板)",
    0x180e2d8f5: "CertOpenStore",
    0x180e2dbcc: "CertGetCertificateChain",
    0x180e2dd77: "CertVerifyCertificateChainPolicy#1",
    0x180e2ddbd: "CertVerifyCertificateChainPolicy#2",
    0x180e2ddee: "CertVerifyCertificateChainPolicy#3",
    0x180e2dfa7: "CertCloseStore",
    0x181326697: "CryptQueryObject",
    0x181326765: "CertFindCertificateInStore",
    0x18016cab0: "CryptQueryObject(2)",
    0x18016cc30: "CertFindCertificateInStore(2)",
}

md = Cs(CS_ARCH_X86, CS_MODE_64)

def dump(start, length):
    o = va2off(start)
    if o is None:
        print("无法映射 %#x" % start); return
    blob = d[o:o+length]
    for insn in md.disasm(blob, start):
        note = KNOWN.get(insn.address, "")
        extra = ""
        if insn.mnemonic in ("call", "jmp"):
            extra = "   ; " + KNOWN.get(int(insn.op_str, 16), "") if insn.op_str.startswith("0x") else ""
        print("  %#010x  %-8s %-42s%s%s" % (insn.address, insn.mnemonic, insn.op_str,
                                            ("  <-- " + note) if note else "", extra))

if __name__ == "__main__":
    start = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x180e9ff60
    length = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x160
    print("反汇编 %#x (+%#x)" % (start, length))
    dump(start, length)
