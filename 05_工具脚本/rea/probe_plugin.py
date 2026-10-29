# -*- coding: utf-8 -*-
"""直接用 ctypes 调用 AssetNativePlugin.dll，让它自己解析 Blocks.xmf
   目标：拿到 资源路径 -> (块文件名, 偏移, 长度) 的映射，避免手工破包头
"""
import ctypes
import os
import sys

DLL_DIR = r"D:\BH3\7.0\BH3_Data\Plugins"
DLL = os.path.join(DLL_DIR, "AssetNativePlugin.dll")
XMF = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc\Blocks.xmf"
META = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc\BlockMeta.xmf"


def main():
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(DLL_DIR)
    lib = ctypes.CDLL(DLL)
    print("DLL 已加载")

    names = ["CreateFileMapSystemDataFromBytes",
             "CreateFileMapSystemDataFromStreamAssetFile",
             "GetFileMapSystemBlockMapCount",
             "GetBlockFileInfoInSystemBlockMapByIndex",
             "GetFileNameByBlockFileInfo",
             "GetFileNameSizeByBlockFileInfo",
             "GetFileLenByBlockFileInfo",
             "GetAsbSegmentInfo"]
    for n in names:
        ok = hasattr(lib, n)
        print("  %-46s %s" % (n, "存在" if ok else "缺失"))
        if not ok:
            continue

    # 尝试用 Bytes 版本解析 Blocks.xmf
    data = open(XMF, "rb").read()
    print("\nBlocks.xmf 大小:", len(data))
    f = lib.CreateFileMapSystemDataFromBytes
    f.restype = ctypes.c_void_p
    f.argtypes = [ctypes.c_char_p, ctypes.c_int]
    ptr = f(data, len(data))
    print("FileMapSystemData ptr:", ptr)
    if not ptr:
        print("解析失败（返回空指针）")
        return

    g = lib.GetFileMapSystemBlockMapCount
    g.restype = ctypes.c_int
    g.argtypes = [ctypes.c_void_p]
    cnt = g(ptr)
    print("块数量:", cnt)

    if cnt and 0 < cnt < 100000:
        h = lib.GetBlockFileInfoInSystemBlockMapByIndex
        h.restype = ctypes.c_void_p
        h.argtypes = [ctypes.c_void_p, ctypes.c_int]
        gn = lib.GetFileNameByBlockFileInfo
        gn.restype = ctypes.c_char_p
        gn.argtypes = [ctypes.c_void_p]
        gl = lib.GetFileLenByBlockFileInfo
        gl.restype = ctypes.c_longlong
        gl.argtypes = [ctypes.c_void_p]
        for i in range(min(cnt, 5)):
            info = h(ptr, i)
            if not info:
                print("  [%d] info=null" % i)
                continue
            try:
                nm = gn(info)
                ln = gl(info)
                print("  [%d] %s  len=%s" % (i, nm, ln))
            except Exception as e:
                print("  [%d] 读取异常: %s" % (i, e))


if __name__ == "__main__":
    main()
