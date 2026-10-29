# -*- coding: utf-8 -*-
"""世界地图卡片槽位编辑器（wmv bundle #848 / CAB-97db9bad...）。

背景
----
`MonoWorldMapEntryContainerBase` 序列化布局（对象起始 + 偏移）：
    +0x00 m_GameObject (PPtr, 12B)
    +0x0C m_Enabled    (1B) + 3B pad
    +0x10 m_Script     (PPtr, 12B)
    +0x1C m_Name       (4B)
    +0x20 entryID      (int32)   <- 卡片绑定的 WorldMap EntryID
    +0x24 index        (int32)
    +0x28 isFixedEntry (bool)    <- 关键！

`isFixedEntry` 语义
-------------------
- 1 = 固定槽位：卡片内容由序列化的 entryID 决定（改 entryID 有效）
- 0 = 动态槽位：运行时由活动列表填充，**序列化的 entryID 被完全忽略**

预制体里 12 个槽位实测：
    1010@0x01CB70 fixed=1     1000@0x021DB4 fixed=0
    1005@0x02FDB0 fixed=0     1002@0x02FFF8 fixed=1
    1004@0x040818 fixed=1     1001@0x044670 fixed=1
    1005@0x04EA20 fixed=0     1007@0x04F530 fixed=1
    1008@0x0527D0 fixed=1     1003@0x057178 fixed=1
    1013@0x059F70 fixed=1     1009@0x0605E8 fixed=1

> 之前把 0x04EA20（isFixed=0 的动态槽）的 entryID 1006 改成 1012/1005
> 全部无效，原因就是这个槽位根本不读 entryID。

LZ4 约束
--------
`wmvkit.patch_same_length` 只能改 LZ4 **字面量**里的字节：
- entryID 的低 1~2 字节通常是字面量 → 可改（1000~1013 只有低字节不同）
- 高 2 字节（恒为 0x00）与 `isFixedEntry` 常落在 match 区 → 改不了
- 因此 isFixed 无法从 0 改成 1；只能选本来 fixed=1 的槽位

用法
----
    python patch_slot.py status
    python patch_slot.py set 0x059F70 1012
    python patch_slot.py set 0x059F70 1013
    python patch_slot.py restore
"""
import sys, os, struct, shutil

RE = r"D:\BH3\7.0\_ext\re"
sys.path.insert(0, RE)
import wmvkit

WMV = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc\0a95a3510bffb1a31fdef2cae36e8783.wmv"
CAB = "CAB-97db9bad99c9e85516ab4c692725db04"
BAK = WMV + ".slot.bak"

SLOTS = [0x01CB70, 0x021DB4, 0x02FDB0, 0x02FFF8, 0x040818, 0x044670,
         0x04EA20, 0x04F530, 0x0527D0, 0x057178, 0x059F70, 0x0605E8]

# 已知语义（来自 PlayerLog 实证 + WorldMap.json）
KNOWN = {1013: "角色教学", 1006: "悬赏委托", 1012: "迪拉克之海"}


def load():
    data = bytearray(open(WMV, "rb").read())
    _, bundles = wmvkit.walk(data=bytes(data))
    b = [x for x in bundles if any(CAB in n.get("path", "") for n in x["nodes"])][0]
    pl = wmvkit.bundle_payload(bytes(data), b)
    return data, bundles, b, pl


def cmd_status():
    data, bundles, b, pl = load()
    print("wmv %d B · bundle %d 个 · payload %d B" % (len(data), len(bundles), len(pl)))
    print("%-10s %-8s %-9s %s" % ("offset", "entryID", "isFixed", "说明"))
    for off in sorted(SLOTS):
        eid = struct.unpack_from("<i", pl, off)[0]
        fx = pl[off + 8]
        tag = KNOWN.get(eid, "")
        note = "" if fx else "  <- 动态槽，entryID 被忽略"
        print("%-10s %-8d %-9d %s%s" % (hex(off), eid, fx, tag, note))


def cmd_set(off_s, want_s):
    off = int(off_s, 0)
    want = int(want_s)
    if off not in SLOTS:
        print("!! 未知槽位 %s，可用：%s" % (off_s, [hex(x) for x in SLOTS]))
        return 1
    if not (0 <= want < 65536):
        print("!! entryID 必须在 0..65535")
        return 1
    data, bundles, b, pl = load()
    cur = struct.unpack_from("<i", pl, off)[0]
    fx = pl[off + 8]
    print("槽位 %s : entryID=%d isFixed=%d" % (hex(off), cur, fx))
    if not fx:
        print("!! 该槽位 isFixed=0（动态），改 entryID 不会有任何效果")
    if cur == want:
        print("已是目标值")
        return 0
    if not os.path.exists(BAK):
        open(BAK, "wb").write(bytes(data))
        print("[+] 已备份 -> %s" % BAK)

    # 优先只改低 1 字节（1000~1013 高字节相同，几乎总能成功）
    ok = False
    for n in (1, 2, 4):
        old = struct.pack("<i", cur)[:n]
        new = struct.pack("<i", want)[:n]
        if old == new:
            continue
        ok, msg = wmvkit.patch_same_length(data, b, off, old, new)
        print("  改 %d 字节: %s %s" % (n, ok, msg))
        if ok:
            break
    if not ok:
        print("!! 目标字节全部落在 LZ4 match 区，无法原地修改")
        return 1

    if len(data) != os.path.getsize(WMV):
        print("!! 文件长度变了")
        return 1
    open(WMV, "wb").write(bytes(data))

    data2, bs2, b2, pl2 = load()
    got = struct.unpack_from("<i", pl2, off)[0]
    bad = [i for i, x in enumerate(bs2) if not x.get("ok")]
    print("复核: entryID=%d  文件 %d B  bundle %d 个 解析失败 %d 个"
          % (got, len(data2), len(bs2), len(bad)))
    return 0 if got == want and not bad else 1


def cmd_restore():
    if not os.path.exists(BAK):
        print("没有备份")
        return 1
    shutil.copy2(BAK, WMV)
    print("[+] 已从备份还原")
    return 0


def main():
    args = sys.argv[1:]
    cmd = (args or ["status"])[0]
    if cmd == "status":
        cmd_status()
    elif cmd == "set" and len(args) >= 3:
        return cmd_set(args[1], args[2])
    elif cmd == "restore":
        return cmd_restore()
    else:
        print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
