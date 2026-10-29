# -*- coding: utf-8 -*-
import ctypes, os, struct, hashlib

DLL_DIR = r"D:\BH3\7.0\BH3_Data\Plugins"
ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
TARGET = "f65865df27ea6a9e58bf8f1f3b01bdcd.wmv"

lib = ctypes.CDLL(os.path.join(DLL_DIR, "AssetNativePlugin.dll"))
lib.CreateFileMapSystemDataFromBytes.restype = ctypes.c_void_p
lib.CreateFileMapSystemDataFromBytes.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.GetFileMapSystemBlockMapCount.restype = ctypes.c_int
lib.GetFileMapSystemBlockMapCount.argtypes = [ctypes.c_void_p]
lib.GetBlockFileInfoInSystemBlockMapByIndex.restype = ctypes.c_char_p
lib.GetBlockFileInfoInSystemBlockMapByIndex.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]
lib.GetBlockFileInfoMD51.restype = ctypes.c_ulonglong
lib.GetBlockFileInfoMD51.argtypes = [ctypes.c_void_p, ctypes.c_int]
lib.GetBlockFileInfoMD52.restype = ctypes.c_ulonglong
lib.GetBlockFileInfoMD52.argtypes = [ctypes.c_void_p, ctypes.c_int]

target_md5 = hashlib.md5(open(os.path.join(ASB, TARGET), "rb").read()).digest()
want1 = struct.unpack(">Q", target_md5[0:8])[0]
want2 = struct.unpack(">Q", target_md5[8:16])[0]
print("原始包 md5 =", target_md5.hex())
print("期望 MD51 = %016x  MD52 = %016x" % (want1, want2))
print()

for xmf in ("Blocks.xmf", "Blocks_7_0.xmf", "BlockMeta.xmf"):
    p = os.path.join(ASB, xmf)
    if not os.path.exists(p):
        print(xmf, "不存在"); continue
    data = open(p, "rb").read()
    ptr = lib.CreateFileMapSystemDataFromBytes(data, len(data))
    if not ptr:
        print("%-16s 解析失败 size=%d" % (xmf, len(data))); continue
    n = lib.GetFileMapSystemBlockMapCount(ptr)
    hit = None
    for i in range(n):
        ln = ctypes.c_ulonglong(0)
        nm = lib.GetBlockFileInfoInSystemBlockMapByIndex(ptr, i, ctypes.byref(ln))
        if nm and nm.decode("utf-8", "replace") == TARGET:
            hit = (i, ln.value, lib.GetBlockFileInfoMD51(ptr, i), lib.GetBlockFileInfoMD52(ptr, i))
            break
    print("%-16s size=%-10d blocks=%-8d" % (xmf, len(data), n), end="")
    if hit:
        i, ln, m1, m2 = hit
        print(" 命中 idx=%d len=%d MD51=%016x MD52=%016x  匹配=%s" % (i, ln, m1, m2, (m1 == want1 and m2 == want2)))
    else:
        print(" 无该条目")
