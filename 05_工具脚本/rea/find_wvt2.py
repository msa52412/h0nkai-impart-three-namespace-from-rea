# -*- coding: utf-8 -*-
"""纯字节模式定位 UnityPlayer.dll 中对 wintrust/crypt32 导入的引用"""
import struct
import pefile

P = r"D:\BH3\7.0\UnityPlayer.dll"
pe = pefile.PE(P, fast_load=False)
ib = pe.OPTIONAL_HEADER.ImageBase

targets = {}
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    dll = entry.dll.decode("ascii", "replace").lower()
    for imp in entry.imports:
        if imp.name:
            n = imp.name.decode("ascii", "replace")
            if n in ("WinVerifyTrust", "WinVerifyTrustEx", "CryptQueryObject",
                     "CertGetCertificateChain", "CertVerifyCertificateChainPolicy",
                     "CryptCATAdminCalcHashFromFileHandle", "CertFindCertificateInStore",
                     "CertOpenStore", "CertCloseStore", "CryptCATAdminEnumCatalogFromHash"):
                targets[imp.address] = "%s!%s" % (dll, n)

print("目标导入:")
for va, n in sorted(targets.items()):
    print("  %#x  %s" % (va, n))

for s in pe.sections:
    if b".text" not in s.Name:
        continue
    va = ib + s.VirtualAddress
    data = s.get_data()
    print("\n.text VA=%#x size=%#x" % (va, len(data)))
    found = []
    for i in range(len(data) - 6):
        # FF 15 disp32  = call qword [rip+disp]
        if data[i] == 0xFF and data[i+1] == 0x15:
            disp = struct.unpack_from("<i", data, i+2)[0]
            t = va + i + 6 + disp
            if t in targets:
                found.append((va+i, "call", targets[t]))
        # FF 25 disp32 = jmp qword [rip+disp]
        elif data[i] == 0xFF and data[i+1] == 0x25:
            disp = struct.unpack_from("<i", data, i+2)[0]
            t = va + i + 6 + disp
            if t in targets:
                found.append((va+i, "jmp", targets[t]))
        # 48/4C 8B xx disp32 = mov r64, [rip+disp]
        elif data[i] in (0x48, 0x4C) and data[i+1] == 0x8B and (data[i+2] & 0xC7) == 0x05:
            disp = struct.unpack_from("<i", data, i+3)[0]
            t = va + i + 7 + disp
            if t in targets:
                found.append((va+i, "mov", targets[t]))
    print("rip 相对引用:", len(found))
    for a, k, n in found:
        print("  %#x  %-5s %s" % (a, k, n))

    # 绝对 8 字节立即数
    print("\n绝对地址立即数:")
    for tva, tn in targets.items():
        pat = struct.pack("<Q", tva)
        idx = data.find(pat)
        cnt = 0
        while idx >= 0 and cnt < 5:
            print("  %#x  %#x  %s" % (va+idx, tva, tn))
            idx = data.find(pat, idx+1); cnt += 1
        if cnt == 0:
            print("  %#x  %s : 无" % (tva, tn))
