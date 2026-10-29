# -*- coding: utf-8 -*-
"""用 AssetNativePlugin 正确签名建立 块索引 -> .wmv 文件名/长度/MD5 映射"""
import ctypes, os, hashlib

DLL_DIR = r"D:/BH3/7.0/BH3_Data/Plugins"
ASB = r"D:/BH3/7.0/BH3_Data/StreamingAssets/Asb/pc"
XMF = os.path.join(ASB, "Blocks.xmf")

if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(DLL_DIR)
lib = ctypes.CDLL(os.path.join(DLL_DIR, "AssetNativePlugin.dll"))

def sig(name, restype, argtypes):
    f = getattr(lib, name)
    f.restype = restype
    f.argtypes = argtypes
    return f

create   = sig("CreateFileMapSystemDataFromBytes", ctypes.c_void_p, [ctypes.c_char_p, ctypes.c_int])
count    = sig("GetFileMapSystemBlockMapCount", ctypes.c_int, [ctypes.c_void_p])
by_index = sig("GetBlockFileInfoInSystemBlockMapByIndex", ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_int])
by_name  = sig("GetBlockFileInfoIndexInSystemBlockMap", ctypes.c_int, [ctypes.c_void_p, ctypes.c_char_p])
fname    = sig("GetFileNameByBlockFileInfo", ctypes.c_char_p, [ctypes.c_void_p])
flen     = sig("GetFileLenByBlockFileInfo", ctypes.c_longlong, [ctypes.c_void_p])

md51 = md52 = None
try:
    md51 = sig("GetBlockFileInfoMD51", ctypes.c_ulonglong, [ctypes.c_void_p])
    md52 = sig("GetBlockFileInfoMD52", ctypes.c_ulonglong, [ctypes.c_void_p])
except AttributeError:
    pass

def load():
    data = open(XMF, "rb").read()
    p = create(data, len(data))
    assert p, "解析失败"
    return p, count(p)

def entry(p, i):
    info = by_index(p, i)
    n = fname(info)
    name = n.decode("utf-8", "replace") if n else None
    return dict(idx=i, name=name, len=flen(info),
                md51=md51(info) if md51 else None,
                md52=md52(info) if md52 else None,
                info=info)

if __name__ == "__main__":
    p, n = load()
    print("块数 =", n)
    print("\n前 6 条:")
    for i in range(6):
        e = entry(p, i)
        print("  idx=%-4d len=%-10d md51=%016x md52=%016x name=%s" % (
            e["idx"], e["len"], e["md51"] or 0, e["md52"] or 0, e["name"]))

    TARGET = "f65865df27ea6a9e58bf8f1f3b01bdcd.wmv"
    found = [entry(p, i) for i in range(n) if (entry(p, i)["name"] or "") == TARGET]
    print("\n目标条目:", found[0] if found else "未找到")

    # 校验 md51/md52 是否等于 md5 前后半
    ok = 0; bad = 0
    for i in range(n):
        e = entry(p, i)
        f = os.path.join(ASB, e["name"] or "")
        if not os.path.exists(f): continue
        d = hashlib.md5(open(f, "rb").read()).digest()
        w1 = int.from_bytes(d[0:8], "big"); w2 = int.from_bytes(d[8:16], "big")
        if e["md51"] == w1 and e["md52"] == w2: ok += 1
        else: bad += 1
    print("\nMD51/MD52 == md5 前后半: 匹配 %d, 不匹配 %d" % (ok, bad))
