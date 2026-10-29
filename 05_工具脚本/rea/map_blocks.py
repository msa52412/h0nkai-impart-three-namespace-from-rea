# -*- coding: utf-8 -*-
import ctypes, os, struct, hashlib
DLL = r"D:/BH3/7.0/BH3_Data/Plugins/AssetNativePlugin.dll"
ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
lib = ctypes.CDLL(DLL)
lib.CreateFileMapSystemDataFromBytes.restype = ctypes.c_void_p
lib.CreateFileMapSystemDataFromBytes.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.GetFileMapSystemBlockMapCount.restype = ctypes.c_int
lib.GetFileMapSystemBlockMapCount.argtypes = [ctypes.c_void_p]
lib.GetBlockFileInfoInSystemBlockMapByIndex.restype = ctypes.c_void_p
lib.GetBlockFileInfoInSystemBlockMapByIndex.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]

def readmem(a, n):
    return bytes((ctypes.c_char * n).from_address(a))

def cstr(a):
    if not a: return None
    out = bytearray()
    while True:
        c = readmem(a, 1)
        if c == b"\x00": break
        out += c; a += 1
        if len(out) > 300: break
    return out.decode("utf-8", "replace")

p = os.path.join(ASB, "Blocks.xmf")
data = open(p, "rb").read()
ptr = lib.CreateFileMapSystemDataFromBytes(data, len(data))
n = lib.GetFileMapSystemBlockMapCount(ptr)

rows = []
for i in range(n):
    a = lib.GetBlockFileInfoInSystemBlockMapByIndex(ptr, i, None)
    raw = readmem(a, 64)
    nameptr = struct.unpack_from("<Q", raw, 0)[0]
    md5 = raw[8:24]
    rows.append((i, cstr(nameptr), md5.hex()))

print("前 5 行:")
for r in rows[:5]: print("  ", r)
print("\nMD5 与磁盘文件对应情况（抽查 10 个）:")
ok = 0
for i, nm, h in rows[:10]:
    f = os.path.join(ASB, h + ".wmv")
    e = os.path.exists(f)
    ok += e
    print("   idx=%-4d md5=%-34s 文件存在=%s  name=%s" % (i, h, e, nm))
print("\n前10中命中:", ok)

# 全量统计
exist = sum(1 for _, _, h in rows if os.path.exists(os.path.join(ASB, h + ".wmv")))
print("全量 %d 块，md5 命名文件存在 %d 个" % (n, exist))

# 找目标
TARGET_MD5 = "f65865df27ea6a9e58bf8f1f3b01bdcd"
for i, nm, h in rows:
    if h == TARGET_MD5:
        print("\n>>> 目标块 idx =", i, "name =", nm)
        break
else:
    print("\n>>> 未在块表中找到目标 md5")
