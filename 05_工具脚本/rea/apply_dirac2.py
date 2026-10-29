# -*- coding: utf-8 -*-
"""迪拉克入口补丁 · 第二步：加诊断标记 + 门禁补丁。

背景
----
预制体补丁已装（entryID 1006 -> 1012），但游戏里 Task_6 仍打开悬赏委托。
静态检查已排除：文件未改动 / 被其它 bundle 覆盖 / IFix 热补丁 / Lua 覆盖 /
运行时改写 entryID。剩下唯一无法静态确认的是「游戏加载的到底是不是这份 prefab」。

因此加一个**零风险**的诊断标记：
    把 GameObject 名 "Task_6" 改成等长的 "TaskX6"
    - DLL 里搜 "Task_" 命中 0 次，代码完全不引用这些名字，改名不影响逻辑
    - 名字只用于日志/层级显示
装完后点第 6 张卡，服务端 PlayerLog 会显示点击路径：
    出现 .../Challenge/TaskX6/Cover  -> prefab 是这份，问题在别处
    仍是 .../Challenge/Task_6/Cover  -> 游戏用的是另一份 prefab

同时装 DLL 门禁补丁：
    迪拉克 1012 的 ContentIDList 是空数组，OODENFBANCC.NOIBCEBOLDE() 会判它无效。
    把 0x180A5253B 的 `7E 08`(jle) 改成 `90 90`，让「有 WorldMap 行但内容为空」也算有效。
    副作用：1001/1002/1007/1008/1011 这几个同样空内容的入口也会变可见。

用法
----
    python apply_dirac2.py status
    python apply_dirac2.py mark      # 只加诊断标记
    python apply_dirac2.py dll       # 只打门禁补丁
    python apply_dirac2.py all       # 两个都装（推荐）
    python apply_dirac2.py revert    # 还原标记 + DLL

注意：先退出游戏。
"""
import sys, os, struct, shutil

sys.path.insert(0, r"D:\BH3\7.0\_ext\re")
import wmvkit

WMV = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc\0a95a3510bffb1a31fdef2cae36e8783.wmv"
SF_SIZE = 412587
EID_OFF = 0x04EA20          # entryID
NAME_OFF = 0x040BF4         # "Task_6" 里的 '_' -> 'X'

DLL = r"D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll"
DLL_OFF = 0xA5113B
DLL_OLD = b"\x7E\x08"
DLL_NEW = b"\x90\x90"


def load_wmv():
    data = bytearray(open(WMV, "rb").read())
    _, bs = wmvkit.walk(data=bytes(data))
    for i, b in enumerate(bs):
        pl = wmvkit.bundle_payload(bytes(data), b)
        if len(pl) < SF_SIZE + 16:
            continue
        try:
            ms, fs, ver, doff = struct.unpack_from(">IIII", pl, 0)
        except struct.error:
            continue
        if ver != 17 or not (0 < ms < (1 << 20)) or doff < ms or doff > fs:
            continue
        if pl[EID_OFF:EID_OFF + 4] in (b"\xF4\x03\x00\x00", b"\xEE\x03\x00\x00"):
            return data, i, b, pl
    return None, None, None, None


def status():
    data, i, b, pl = load_wmv()
    if data is None:
        print("!! 找不到目标 bundle")
        return
    eid = struct.unpack_from("<i", pl, EID_OFF)[0]
    name = pl[NAME_OFF - 4:NAME_OFF + 6]
    print("目标 bundle #%d  payload=%d" % (i, len(pl)))
    print("  entryID @0x%X = %d  %s" % (EID_OFF, eid, "-> 迪拉克" if eid == 1012 else "-> 悬赏委托" if eid == 1006 else ""))
    print("  m_Name  @0x%X = %r  %s" % (NAME_OFF - 4, name, "(已加标记)" if b"TaskX6" in pl else "(未加标记)"))
    d = open(DLL, "rb").read(DLL_OFF + 2)[DLL_OFF:DLL_OFF + 2]
    print("DLL 0x%X = %s  %s" % (DLL_OFF, d.hex(), "(已打补丁)" if d == DLL_NEW else "(未打补丁)"))


def install_mark():
    data, i, b, pl = load_wmv()
    if data is None:
        print("!! 找不到目标 bundle")
        return False
    if b"TaskX6" in pl:
        print("标记已存在，跳过。")
        return True
    if pl[NAME_OFF:NAME_OFF + 1] != b"_":
        print("!! 0x%X 处不是 '_'，实际 %s，放弃" % (NAME_OFF, pl[NAME_OFF:NAME_OFF + 1].hex()))
        return False
    ok, msg = wmvkit.patch_same_length(data, b, NAME_OFF, b"_", b"X")
    print("patch:", ok, msg)
    if not ok:
        return False
    # 复核
    _, bs2 = wmvkit.walk(data=bytes(data))
    pl2 = wmvkit.bundle_payload(bytes(data), bs2[i])
    print("复核 m_Name =", pl2[NAME_OFF - 4:NAME_OFF + 6])
    if b"TaskX6" not in pl2:
        print("!! 复核失败")
        return False
    if len(data) != os.path.getsize(WMV):
        print("!! 长度变了")
        return False
    open(WMV, "wb").write(bytes(data))
    print("[+] 已写入，长度 %d 不变" % len(data))
    return True


def install_dll():
    cur = open(DLL, "rb").read(DLL_OFF + 2)[DLL_OFF:DLL_OFF + 2]
    if cur == DLL_NEW:
        print("DLL 已打补丁，跳过。")
        return True
    if cur != DLL_OLD:
        print("!! 0x%X 处是 %s，不是预期 %s，放弃" % (DLL_OFF, cur.hex(), DLL_OLD.hex()))
        return False
    bak = DLL + ".bak"
    if not os.path.exists(bak):
        print("备份 190MB DLL ...")
        shutil.copy2(DLL, bak)
        print("[+] 备份 ->", bak)
    with open(DLL, "r+b") as f:
        f.seek(DLL_OFF)
        f.write(DLL_NEW)
    print("[+] DLL 0x%X: %s -> %s" % (DLL_OFF, DLL_OLD.hex(), DLL_NEW.hex()))
    return True


def revert():
    data, i, b, pl = load_wmv()
    if data is not None and b"TaskX6" in pl:
        ok, msg = wmvkit.patch_same_length(data, b, NAME_OFF, b"X", b"_")
        print("还原标记:", ok, msg)
        if ok:
            open(WMV, "wb").write(bytes(data))
    else:
        print("标记不存在，跳过")
    bak = DLL + ".bak"
    if os.path.exists(bak):
        shutil.copy2(bak, DLL)
        os.remove(bak)
        print("[+] DLL 已还原")
    else:
        print("DLL 无备份，跳过")


def main():
    cmd = (sys.argv[1:] or ["status"])[0]
    if cmd == "status":
        status()
    elif cmd == "mark":
        install_mark()
    elif cmd == "dll":
        install_dll()
    elif cmd == "all":
        install_mark()
        print()
        install_dll()
        print()
        status()
    elif cmd == "revert":
        revert()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
