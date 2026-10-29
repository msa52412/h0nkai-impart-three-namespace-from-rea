# -*- coding: utf-8 -*-
"""探针3：asbName(.unity3d) -> 块文件(.wmv) 的映射，验证索引可用
"""
import ctypes
import os
import re

DLL_DIR = r"D:\BH3\7.0\BH3_Data\Plugins"
XMF = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc\Blocks.xmf"


def main():
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(DLL_DIR)
    lib = ctypes.CDLL(os.path.join(DLL_DIR, "AssetNativePlugin.dll"))

    data = open(XMF, "rb").read()
    f = lib.CreateFileMapSystemDataFromBytes
    f.restype = ctypes.c_void_p
    f.argtypes = [ctypes.c_char_p, ctypes.c_int]
    ptr = f(data, len(data))

    # 抽出所有 .unity3d 名字
    names = sorted({m.group().decode() for m in
                    re.finditer(rb"[0-9]{5,}_[0-9]{3,}\.unity3d", data)})
    print("索引中的 asbName 数量:", len(names))
    for n in names[:5]:
        print("  ", n)

    idx = lib.GetBlockFileInfoIndexInSystemBlockMap
    idx.restype = ctypes.c_int
    idx.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    h = lib.GetBlockFileInfoInSystemBlockMapByIndex
    h.restype = ctypes.c_void_p
    h.argtypes = [ctypes.c_void_p, ctypes.c_int]
    gn = lib.GetFileNameByBlockFileInfo
    gn.restype = ctypes.c_char_p
    gn.argtypes = [ctypes.c_void_p]
    gl = lib.GetFileLenByBlockFileInfo
    gl.restype = ctypes.c_longlong
    gl.argtypes = [ctypes.c_void_p]

    print("\n=== asbName -> 块文件 ===")
    hit = 0
    for n in names[:8]:
        i = idx(ptr, n.encode())
        if i < 0:
            print("  %-34s -> 未命中(%d)" % (n, i))
            continue
        hit += 1
        info = h(ptr, i)
        print("  %-34s -> idx=%-4d %s len=%s" % (n, i, gn(info), gl(info)))
    print("命中 %d/%d" % (hit, min(8, len(names))))


if __name__ == "__main__":
    main()
