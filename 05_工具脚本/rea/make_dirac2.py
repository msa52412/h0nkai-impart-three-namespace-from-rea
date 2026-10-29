# -*- coding: utf-8 -*-
"""把挑战面板 Task_6 的入口从「悬赏委托」改指向「迪拉克之海」。

改动内容
--------
预制体里每个卡片节点的 MonoWorldMapEntryContainerBase 都有一个序列化 int `entryID`
（+0x18），运行时 SetupContainerData() 用它去查 WorldMap 配置表：
    ContainerData = worldMap.HCIBJEOCENM(entryID, index)

解包后的 SerializedFile 里实测有 12 个 (entryID, index=0) 槽位：
    1010, 1000, 1005, 1002, 1004, 1001, 1006, 1007, 1008, 1003, 1013, 1009
其中 1006 对应「悬赏委托」（日志实证：Task_6 -> NewWantedMainPageContext），
1011/1012 根本不在预制体里 —— 所以迪拉克之海没有卡位。

本脚本把 entryID=1006 的那一处改成 1012：
    1006 = 0x03EE  ->  1012 = 0x03F4     只有低字节变，改 1 个字节
LZ4 字面量级原地补丁，文件总长度不变（.wmv 文件名是 md5，长度不能变）。

用法
----
    python make_dirac2.py            # 生成补丁文件到 _ext/out/
    python make_dirac2.py --check    # 只检查不写
"""
import sys, os, struct, shutil

RE = r"D:\BH3\7.0\_ext\re"
sys.path.insert(0, RE)
import wmvkit

WMV = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc\0a95a3510bffb1a31fdef2cae36e8783.wmv"
OUTDIR = r"D:\BH3\7.0\_ext\out"

SF_SIZE = 412587          # 解包出的 SerializedFile 大小，用来认出目标 bundle
SF_OFF = 0x04EA20         # entryID=1006 在 SF 内的偏移
OLD = b"\xEE"             # 0x03EE = 1006 的低字节
NEW = b"\xF4"             # 0x03F4 = 1012 的低字节


def main():
    check_only = "--check" in sys.argv
    data = bytearray(open(WMV, "rb").read())
    print("wmv %s  %d 字节" % (os.path.basename(WMV), len(data)))

    _, bundles = wmvkit.walk(data=bytes(data))
    print("bundle 数 %d" % len(bundles))

    target = None
    for i, b in enumerate(bundles):
        pl = wmvkit.bundle_payload(bytes(data), b)
        if len(pl) < SF_SIZE + 16:
            continue
        ms, fs, ver, doff = struct.unpack_from(">IIII", pl, 0)
        if ver != 17:
            continue
        if not (0 < ms < (1 << 20)) or doff < ms or doff > fs:
            continue
        if pl[SF_OFF:SF_OFF + 4] == b"\xEE\x03\x00\x00":
            print("命中 bundle #%d: payload %d B, SF fileSize=%d dataOffset=%d"
                  % (i, len(pl), fs, doff))
            target = (i, b)
            break

    if target is None:
        print("!! 没找到含 entryID=1006 的 bundle")
        return 1

    i, b = target
    pl = wmvkit.bundle_payload(bytes(data), b)
    eid, idx = struct.unpack_from("<ii", pl, SF_OFF)
    print("当前 SF[0x%X] : entryID=%d index=%d" % (SF_OFF, eid, idx))
    if eid != 1006:
        print("!! entryID 不是 1006，放弃")
        return 1

    print("把 entryID 1006 -> 1012 （0x03EE -> 0x03F4）")
    ok, msg = wmvkit.patch_same_length(data, b, SF_OFF, OLD, NEW)
    print("patch_same_length:", ok, msg)
    if not ok:
        return 1

    # 复核：重新解包看结果
    _, bs2 = wmvkit.walk(data=bytes(data))
    pl2 = wmvkit.bundle_payload(bytes(data), bs2[i])
    eid2, idx2 = struct.unpack_from("<ii", pl2, SF_OFF)
    print("复核 SF[0x%X] : entryID=%d index=%d" % (SF_OFF, eid2, idx2))
    if eid2 != 1012:
        print("!! 复核失败")
        return 1
    if len(data) != os.path.getsize(WMV):
        print("!! 文件长度变了：%d -> %d" % (os.path.getsize(WMV), len(data)))
        return 1
    print("长度未变 %d 字节 ✓" % len(data))

    if check_only:
        print("(--check 模式，未写文件)")
        return 0

    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, os.path.basename(WMV))
    open(out, "wb").write(bytes(data))
    print("[+] 写出 %s (%d 字节)" % (out, len(data)))
    print()
    print("安装方式：")
    print("  1) 备份原文件：")
    print("     copy \"%s\" \"%s.bak\"" % (WMV, WMV))
    print("  2) 覆盖：")
    print("     copy /Y \"%s\" \"%s\"" % (out, WMV))
    print("  3) 重启游戏，进世界地图 -> 挑战页签，看第 6 张卡是否变成迪拉克之海")
    return 0


if __name__ == "__main__":
    sys.exit(main())
