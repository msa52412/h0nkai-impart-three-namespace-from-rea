# -*- coding: utf-8 -*-
"""挑战面板 Task_6 -> 迪拉克之海 的补丁安装器。

两个补丁
--------
wmv  （必需，零风险）
    预制体 0a95a351....wmv 里 Task_6 的 entryID 由 1006(悬赏委托) 改成 1012(迪拉克之海)。
    只改 1 个字节的 LZ4 字面量，文件长度不变。

dll  （可选，仅在装完 wmv 后卡片直接消失时才需要）
    UserAssembly.dll 的 OODENFBANCC.NOIBCEBOLDE() 要求「WorldMap 行存在 且 内容列表非空」。
    迪拉克的 ContentIDList 是空数组，所以会被判为无效而隐藏。
    把 0x180A5253B 处的 `7E 08`(jle) 改成 `90 90`(nop)，
    即可让「有行但内容为空」的入口也算有效。
    副作用：其它同样「有行但内容为空」的入口（1001/1002/1007/1008/1011）也会变成可见。

用法
----
    python apply_dirac.py status     # 看当前装了哪个
    python apply_dirac.py wmv        # 只装预制体补丁（先试这个）
    python apply_dirac.py dll        # 再加装 DLL 补丁
    python apply_dirac.py revert     # 全部还原

注意：安装前请先退出游戏，否则文件被占用。
"""
import sys, os, shutil, struct

WMV = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc\0a95a3510bffb1a31fdef2cae36e8783.wmv"
WMV_PATCHED = r"D:\BH3\7.0\_ext\out\0a95a3510bffb1a31fdef2cae36e8783.wmv"
WMV_BAK = WMV + ".bak"

DLL = r"D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll"
DLL_BAK = DLL + ".bak"
DLL_OFF = 0xA5113B
DLL_OLD = b"\x7E\x08"
DLL_NEW = b"\x90\x90"

SF_OFF = 0x04EA20
SF_SIZE = 412587


def wmv_entry_id(path):
    """读出 wmv 里那个 entryID，用来判断是否已打补丁。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("wmvkit", r"D:\BH3\7.0\_ext\re\wmvkit.py")
    wk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wk)
    data = open(path, "rb").read()
    _, bs = wk.walk(data=data)
    for b in bs:
        pl = wk.bundle_payload(data, b)
        if len(pl) < SF_SIZE + 16:
            continue
        try:
            ms, fs, ver, doff = struct.unpack_from(">IIII", pl, 0)
        except struct.error:
            continue
        if ver != 17 or not (0 < ms < (1 << 20)) or doff < ms or doff > fs:
            continue
        if pl[SF_OFF:SF_OFF + 4] in (b"\xEE\x03\x00\x00", b"\xF4\x03\x00\x00"):
            return struct.unpack_from("<i", pl, SF_OFF)[0]
    return None


def dll_patched():
    d = open(DLL, "rb").read(DLL_OFF + 2)[DLL_OFF:DLL_OFF + 2]
    return d == DLL_NEW


def status():
    eid = wmv_entry_id(WMV)
    print("预制体 entryID = %s  (%s)" % (eid, "已打补丁 -> 迪拉克" if eid == 1012
                                          else "原样 -> 悬赏委托" if eid == 1006 else "未知"))
    print("DLL 补丁      = %s" % ("已装" if dll_patched() else "未装"))
    print("备份: wmv %s / dll %s"
          % ("有" if os.path.exists(WMV_BAK) else "无",
             "有" if os.path.exists(DLL_BAK) else "无"))


def install_wmv():
    if not os.path.exists(WMV_PATCHED):
        print("!! 找不到补丁文件 %s，先运行 make_dirac2.py" % WMV_PATCHED)
        return False
    if wmv_entry_id(WMV) == 1012:
        print("已经打过补丁了，跳过。")
        return True
    if not os.path.exists(WMV_BAK):
        shutil.copy2(WMV, WMV_BAK)
        print("[+] 备份 -> %s" % WMV_BAK)
    shutil.copy2(WMV_PATCHED, WMV)
    print("[+] 已覆盖 %s" % WMV)
    print("    entryID 现在 =", wmv_entry_id(WMV))
    return True


def install_dll():
    if dll_patched():
        print("DLL 已经打过补丁了，跳过。")
        return True
    if not os.path.exists(DLL_BAK):
        print("正在备份 190MB 的 DLL ...")
        shutil.copy2(DLL, DLL_BAK)
        print("[+] 备份 -> %s" % DLL_BAK)
    with open(DLL, "r+b") as f:
        f.seek(DLL_OFF)
        cur = f.read(2)
        if cur != DLL_OLD:
            print("!! 该位置字节是 %s，不是预期的 %s，放弃" % (cur.hex(), DLL_OLD.hex()))
            return False
        f.seek(DLL_OFF)
        f.write(DLL_NEW)
    print("[+] DLL 已打补丁：0x%X  %s -> %s" % (DLL_OFF, DLL_OLD.hex(), DLL_NEW.hex()))
    return True


def revert():
    if os.path.exists(WMV_BAK):
        shutil.copy2(WMV_BAK, WMV)
        os.remove(WMV_BAK)
        print("[+] 已还原 wmv")
    else:
        print("wmv 无备份，跳过")
    if os.path.exists(DLL_BAK):
        shutil.copy2(DLL_BAK, DLL)
        os.remove(DLL_BAK)
        print("[+] 已还原 DLL")
    else:
        print("DLL 无备份，跳过")


def main():
    a = sys.argv[1:] or ["status"]
    cmd = a[0]
    if cmd == "status":
        status()
    elif cmd == "wmv":
        install_wmv()
    elif cmd == "dll":
        install_dll()
    elif cmd == "revert":
        revert()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
