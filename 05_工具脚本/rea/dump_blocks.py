# -*- coding: utf-8 -*-
import ctypes, os
DLL = r"D:/BH3/7.0/BH3_Data/Plugins/AssetNativePlugin.dll"
ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
lib = ctypes.CDLL(DLL)
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

p = os.path.join(ASB, "Blocks.xmf")
data = open(p, "rb").read()
ptr = lib.CreateFileMapSystemDataFromBytes(data, len(data))
n = lib.GetFileMapSystemBlockMapCount(ptr)
print("blocks =", n)
for i in range(0, 8):
    ln = ctypes.c_ulonglong(0)
    nm = lib.GetBlockFileInfoInSystemBlockMapByIndex(ptr, i, ctypes.byref(ln))
    print(i, repr(nm)[:90], "len=", ln.value, "MD51=%016x" % lib.GetBlockFileInfoMD51(ptr, i), "MD52=%016x" % lib.GetBlockFileInfoMD52(ptr, i))
