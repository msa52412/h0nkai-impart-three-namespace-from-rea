# -*- coding: utf-8 -*-
"""wmv bundle payload 通用改写器（整块重压缩，保持文件总长度不变）。

背景
----
`wmvkit.patch_same_length` 只能改 LZ4 **字面量**里的字节；一旦目标字节落在
match 区就改不动（entryID 1006->1012 改完后，再想改回去就失败了）。

本脚本改用「解压整块 -> 改 -> 用 LZ4 HC 重压缩 -> 补零到原压缩长度」的办法，
因此任何偏移都能改，且 .wmv 文件长度不变（BlockMeta 的块偏移全部保持有效）。

前提：重压缩后的长度必须 <= 原压缩长度。LZ4 HC 通常优于 Unity 用的
LZ4_compress_default，实测 block#2 可从 31381 压到更小。

用法
----
    python patch_wmv.py status
    python patch_wmv.py set 1006          # 把 Task_6 槽位的 entryID 设成 1006
    python patch_wmv.py set 1012
    python patch_wmv.py raw 0x4EA20 04    # 查看 payload 某处原始字节
"""
import sys, os, struct

RE = r"D:\BH3\7.0\_ext\re"
sys.path.insert(0, RE)
import wmvkit
import lz4.block

WMV = r"D:\BH3\7.0\BH3_Data\StreamingAssets\Asb\pc\0a95a3510bffb1a31fdef2cae36e8783.wmv"
CAB = "CAB-97db9bad99c9e85516ab4c692725db04"
EID_OFF = 0x04EA20          # Task_6 槽位 entryID 在 SerializedFile 内的偏移
INDEX_OFF = 0x04EA24        # index（应为 0）
BAK = WMV + ".dirac.bak"


def find_bundle(data):
    _, bundles = wmvkit.walk(data=bytes(data))
    for i, b in enumerate(bundles):
        if any(CAB in n.get("path", "") for n in b["nodes"]):
            return i, b
    raise SystemExit("!! 没找到目标 bundle " + CAB)


def block_range(b, bi):
    cstart = b["data_start"]
    for j in range(bi):
        cstart += b["blocks"][j][1]
    return cstart, b["blocks"][bi][1]


def patch_payload(data, b, payload_off, new_bytes):
    """把 bundle payload 中 payload_off 起的 len(new_bytes) 字节改成 new_bytes。"""
    bi, boff = wmvkit.locate_payload_byte(b, payload_off)
    if bi is None:
        return False, "偏移超出 payload"
    usize, csize, flags = b["blocks"][bi]
    cstart, clen = block_range(b, bi)
    assert clen == csize

    chunk = bytes(data[cstart:cstart + csize])
    out, used, clean, _, _ = wmvkit.lz4_decode(chunk, b"", track=True)
    if len(out) != usize:
        return False, "解压长度不符 %d != %d" % (len(out), usize)

    mod = bytearray(out)
    mod[boff:boff + len(new_bytes)] = new_bytes

    # 优先用 HC 压，失败再退回默认档
    best = None
    for mode, lvl in (("high_compression", 12), ("high_compression", 9), ("default", 0)):
        try:
            if mode == "default":
                c = lz4.block.compress(bytes(mod), store_size=False, mode="default")
            else:
                c = lz4.block.compress(bytes(mod), store_size=False, mode=mode, compression=lvl)
        except Exception:
            continue
        if len(c) <= csize and (best is None or len(c) < len(best)):
            best = c
        if best is not None and len(best) < csize - 64:
            break
    if best is None:
        return False, "重压缩后 %d > 原 %d，无法等长替换" % (len(c), csize)

    # 补零到原压缩长度（解码器产出满 usize 字节后即停止，尾部多余字节被忽略）
    padded = best + b"\x00" * (csize - len(best))
    data[cstart:cstart + csize] = padded

    # 复核
    out2, _, _, _, _ = wmvkit.lz4_decode(bytes(padded), b"", track=True)
    if out2 != bytes(mod):
        return False, "复核失败：重压缩块解压结果不一致"
    return True, "block#%d 原 %d -> 新 %d (补零 %d)" % (bi, csize, len(best), csize - len(best))


def load():
    data = bytearray(open(WMV, "rb").read())
    i, b = find_bundle(data)
    pl = wmvkit.bundle_payload(bytes(data), b)
    return data, i, b, pl


def cmd_status():
    data, i, b, pl = load()
    eid, idx = struct.unpack_from("<ii", pl, EID_OFF)
    print("wmv %d 字节, bundle #%d payload %d" % (len(data), i, len(pl)))
    print("  entryID = %d  (0x%X)" % (eid, eid))
    print("  index   = %d" % idx)
    print("  备份存在: %s" % os.path.exists(BAK))
    return eid


def cmd_set(want):
    want = int(want)
    if not (0 <= want < 65536):
        print("!! entryID 必须在 0..65535（高 2 字节在 LZ4 match 区，改不了）")
        return 1
    data, i, b, pl = load()
    eid, idx = struct.unpack_from("<ii", pl, EID_OFF)
    print("当前 entryID=%d -> 目标 %d" % (eid, want))
    if eid == want:
        print("已是目标值，无需改动")
        return 0
    if not os.path.exists(BAK):
        open(BAK, "wb").write(bytes(data))
        print("[+] 已备份原文件 -> %s" % BAK)

    # 优先原地改低 2 字节（实测可行：高 2 字节恒为 0，且落在 LZ4 match 区）
    old2 = struct.pack("<H", eid & 0xFFFF)
    new2 = struct.pack("<H", want & 0xFFFF)
    ok, msg = wmvkit.patch_same_length(data, b, EID_OFF, old2, new2)
    print("原地改低 2 字节:", ok, msg)
    if not ok:
        print("回退到整块重压缩…")
        data, i, b, pl = load()
        ok, msg = patch_payload(data, b, EID_OFF, struct.pack("<i", want))
        print("patch:", ok, msg)
        if not ok:
            return 1
    if len(data) != os.path.getsize(WMV):
        print("!! 长度变了")
        return 1
    open(WMV, "wb").write(bytes(data))
    # 复核
    data2, i2, b2, pl2 = load()
    eid2, idx2 = struct.unpack_from("<ii", pl2, EID_OFF)
    print("复核: entryID=%d index=%d  文件 %d 字节" % (eid2, idx2, len(data2)))
    if eid2 != want:
        print("!! 复核失败")
        return 1
    return 0


def cmd_restore():
    if not os.path.exists(BAK):
        print("没有备份")
        return 1
    import shutil
    shutil.copy2(BAK, WMV)
    print("[+] 已从备份还原 %s" % BAK)
    return 0


def main():
    cmd = (sys.argv[1:] or ["status"])[0]
    if cmd == "status":
        cmd_status()
    elif cmd == "set":
        return cmd_set(sys.argv[2])
    elif cmd == "restore":
        return cmd_restore()
    else:
        print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
