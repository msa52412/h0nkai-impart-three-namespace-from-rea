# -*- coding: utf-8 -*-
"""探针2：调用 GetAsbSegmentInfo 等函数，打通 资源名 -> (块文件, 偏移, 长度)
"""
import ctypes
import os

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
    print("systemData:", ptr)

    # 1) GetAsbSegmentInfo：猜签名 (systemData, asbName) -> segment*
    seg = lib.GetAsbSegmentInfo
    seg.restype = ctypes.c_void_p
    seg.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    # 2) ContainAsbHashInFileMapSystem：猜 (systemData, uint64 hash) -> bool
    if hasattr(lib, "ContainAsbHashInFileMapSystem"):
        ch = lib.ContainAsbHashInFileMapSystem
        ch.restype = ctypes.c_bool
        ch.argtypes = [ctypes.c_void_p, ctypes.c_uint64]

    cands = [
        "_ExcelOutputAsset/OWEndlessGroup",
        "OWEndlessGroup",
        "_ExcelOutputAsset/OWEndlessGroup.asset",
        "Assets/AsbRes/SpriteOutput/OWEndless/ChangeMap/OWDirac",
        "OWEndlessUIManager",
    ]
    for name in cands:
        s = seg(ptr, name.encode())
        print("GetAsbSegmentInfo(%-52s) -> %s" % (name[:52], s))
        if s:
            fn = lib.GetAsbSegmentInfoBlockFileName
            fn.restype = ctypes.c_char_p
            fn.argtypes = [ctypes.c_void_p]
            off = lib.GetAsbSegmentInfoOffset
            off.restype = ctypes.c_longlong
            off.argtypes = [ctypes.c_void_p]
            blk = lib.GetAsbSegmentInfoOwnerBlockIndexInSystemBlockMap
            blk.restype = ctypes.c_int
            blk.argtypes = [ctypes.c_void_p]
            print("    block=%s offset=%s idx=%s" % (fn(s), off(s), blk(s)))

    # 3) 按索引看 blockFileInfo 的更多字段（md5 等）
    cnt = lib.GetFileMapSystemBlockMapCount
    cnt.restype = ctypes.c_int
    cnt.argtypes = [ctypes.c_void_p]
    n = cnt(ptr)
    print("\n块数:", n)
    h = lib.GetBlockFileInfoInSystemBlockMapByIndex
    h.restype = ctypes.c_void_p
    h.argtypes = [ctypes.c_void_p, ctypes.c_int]
    info = h(ptr, 0)
    if info:
        for nm, rt in (("GetBlockFileInfoMD51", ctypes.c_uint64),
                       ("GetBlockFileInfoMD52", ctypes.c_uint64),
                       ("GetFileTagByBlockFileInfo", ctypes.c_int),
                       ("GetDownloadTagByBlockFileInfo", ctypes.c_int)):
            fn = getattr(lib, nm, None)
            if fn:
                fn.restype = rt
                fn.argtypes = [ctypes.c_void_p]
                print("  %s = %s" % (nm, fn(info)))


if __name__ == "__main__":
    main()
