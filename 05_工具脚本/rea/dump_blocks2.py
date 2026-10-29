# -*- coding: utf-8 -*-
import ctypes, os, struct
DLL = r"D:/BH3/7.0/BH3_Data/Plugins/AssetNativePlugin.dll"
ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
lib = ctypes.CDLL(DLL)
lib.CreateFileMapSystemDataFromBytes.restype = ctypes.c_void_p
lib.CreateFileMapSystemDataFromBytes.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.GetFileMapSystemBlockMapCount.restype = ctypes.c_int
lib.GetFileMapSystemBlockMapCount.argtypes = [ctypes.c_void_p]
lib.GetBlockFileInfoInSystemBlockMapByIndex.restype = ctypes.c_void_p
lib.GetBlockFileInfoInSystemBlockMapByIndex.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]

def readmem(addr, n):
    buf = (ctypes.c_char * n).from_address(addr)
    return bytes(buf)

p = os.path.join(ASB, "Blocks.xmf")
data = open(p, "rb").read()
ptr = lib.CreateFileMapSystemDataFromBytes(data, len(data))
print("system ptr = 0x%x" % ptr)
n = lib.GetFileMapSystemBlockMapCount(ptr)
print("blocks =", n)

for i in (0, 1, 2):
    ln = ctypes.c_ulonglong(0)
    a = lib.GetBlockFileInfoInSystemBlockMapByIndex(ptr, i, ctypes.byref(ln))
    print("\nidx=%d info ptr=0x%x  lenarg=%d" % (i, a, ln.value))
    raw = readmem(a, 160)
    print("hex:", raw[:96].hex())
    print("u64:", [hex(x) for x in struct.unpack_from("<8Q", raw, 0)])
