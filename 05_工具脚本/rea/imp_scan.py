# -*- coding: utf-8 -*-
"""列出 PE 文件导入 API 中与「文件完整性/哈希/签名」相关的项"""
import sys
import pefile

P = sys.argv[1]
pe = pefile.PE(P, fast_load=False)

GROUPS = {
    "签名": ["WinVerifyTrust", "WinVerifyTrustEx", "CryptQueryObject", "CertGetCertificateChain",
             "CertVerifyCertificateChainPolicy", "CryptCATAdminCalcHashFromFileHandle",
             "CertFindCertificateInStore", "CryptCATAdminEnumCatalogFromHash"],
    "哈希": ["CryptCreateHash", "CryptHashData", "CryptGetHashParam", "CryptAcquireContextW",
             "BCryptCreateHash", "BCryptHashData", "BCryptFinishHash", "BCryptOpenAlgorithmProvider",
             "MD5Init", "MD5Update", "MD5Final", "SHA1", "SHA256"],
    "文件": ["CreateFileW", "CreateFileA", "ReadFile", "GetFileSize", "GetFileSizeEx",
             "FindFirstFileW", "GetFileAttributesW", "SetFileAttributesW", "MoveFileExW",
             "CopyFileW", "DeleteFileW", "MapViewOfFile", "CreateFileMappingW"],
    "加载": ["LoadLibraryW", "LoadLibraryExW", "GetProcAddress", "LdrLoadDll"],
    "反调试": ["IsDebuggerPresent", "CheckRemoteDebuggerPresent", "NtQueryInformationProcess",
               "OutputDebugStringW", "VirtualProtect", "VirtualProtectEx"],
}

found = {k: [] for k in GROUPS}
allimps = []
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    dll = entry.dll.decode("ascii", "replace")
    for imp in entry.imports:
        n = imp.name.decode("ascii", "replace") if imp.name else "ord#%d" % imp.ordinal
        allimps.append((dll, n, imp.address))
        for g, names in GROUPS.items():
            for t in names:
                if n == t or (len(t) > 4 and n.startswith(t)):
                    found[g].append("%s!%s" % (dll, n))

print("文件: %s" % P)
print("导入模块: %s" % ", ".join(sorted({e.dll.decode('ascii','replace') for e in pe.DIRECTORY_ENTRY_IMPORT})))
print("导入总数: %d" % len(allimps))
for g, v in found.items():
    print("\n[%s] %d 项" % (g, len(v)))
    for x in sorted(set(v)):
        print("   ", x)
