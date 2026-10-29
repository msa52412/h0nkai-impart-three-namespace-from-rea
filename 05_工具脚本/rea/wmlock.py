# -*- coding: utf-8 -*-
"""wmlock —— 查「世界地图卡片为什么显示未解锁」

只读。不发任何调用、不写内存（除 --patch 明确要求时）。

要弄清的两件事
--------------
1) LJMINEONAFF(cd) 到底从哪条指令产出 2
   —— 反汇编 0xA521F0 起整段，逐条打印机器码，标出所有 immediate 常量。
2) entry 的 GetWorldMapEntryStatus() 为什么返回 2
   —— 从 entry 对象取 vtable，读 [+0x1a8] 得到方法地址，换算 RVA 后反汇编。

用法
----
    python wmlock.py asm           反汇编 LJMINEONAFF
    python wmlock.py entry         看 entry 虚方法 GetWorldMapEntryStatus
    python wmlock.py live          现场重取 entry 列表并逐条报状态
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import wmpick  # noqa: E402

RVA_LJMIN = 0xA521F0     # OODENFBANCC.LJMINEONAFF -> WorldMapEntryStatus
RVA_VSLOT = 0x1A8        # GetWorldMapEntryStatus 在 vtable 里的槽位


def disas(base, rva, n, label=""):
    from capstone import Cs, CS_ARCH_X86, CS_MODE_64
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = False
    h, pid, b = icall.open_game()
    if not h:
        return
    try:
        data = icall.read_mem(h, b + rva, n)
    finally:
        icall.k32.CloseHandle(h)
    if not data:
        print("读取失败 %#x" % (b + rva))
        return
    print("=== %s  @ RVA %#x ===" % (label or "disasm", rva))
    for ins in md.disasm(data, b + rva):
        print("  %#012x  %-20s %s %s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str))


def cmd_asm():
    disas(None, RVA_LJMIN, 0x180, "OODENFBANCC.LJMINEONAFF")


def pick_cd(h, base, d, want=108):
    """从 grab 记录里挑出 feature==want 那张卡的 ContainerData，并现场校验 meta。"""
    mb = icall.load_state()["mailbox"]
    cands = [c for c in d.get("cards", []) if c.get("feat") == want]
    for c in cands:
        cd = c.get("cd")
        if not cd:
            continue
        meta = wmpick.call(h, base, mb, wmpick.RVA_GET_META, cd)
        mid = wmpick.i32(h, meta + 0x20) if meta else None
        if meta and mid == c.get("id"):
            print("选中卡片 %s  cd=%#x  meta=%#x  ID=%s ✓（现场校验一致）"
                  % (c.get("tab"), cd, meta, mid))
            return cd
        print("候选 cd=%#x 现场校验不符（meta=%s id=%s vs 记录 %s），跳过"
              % (cd, meta or 0, mid, c.get("id")))
    return None


def cmd_entry():
    """取当前 entry 的 vtable，找到 GetWorldMapEntryStatus 的实现地址。"""
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        d = wmpick.load()
        if not st or not d:
            print("先跑 wmpick.py arm / grab")
            return 1
        cd = pick_cd(h, base, d)
        if not cd:
            print("找不到 feature=108 的卡片容器 —— 面板是否已关闭？重开面板后跑 wmpick.py grab")
            return 1
        mb = st["mailbox"]
        lst = wmpick.call(h, base, mb, wmpick.RVA_GET_ENTRIES, cd)
        if not lst:
            print("entryList 取不到（面板是否已关闭？）")
            return 1
        items, n = wmpick.list_items(h, lst)
        print("entryList=%#x items=%#x size=%d" % (lst, items or 0, n))
        seen = {}
        for i in range(min(n, 8)):
            e = wmpick.q(h, items + 0x20 + i * 8)
            if not e:
                continue
            vt = wmpick.q(h, e)
            fn = wmpick.q(h, vt + RVA_VSLOT) if vt else None
            print("  [%d] entry=%#x vt=%#x  +0x10=%s  +0x14=%s  status_fn=%#x (RVA %#x)"
                  % (i, e, vt or 0, wmpick.i32(h, e + 0x10), wmpick.i32(h, e + 0x14),
                     fn or 0, (fn - base) if fn else 0))
            if fn and fn not in seen:
                seen[fn] = i
        for fn, i in seen.items():
            print()
            disas(base, fn - base, 0x100, "GetWorldMapEntryStatus  (entry[%d])" % i)
        return 0
    finally:
        icall.k32.CloseHandle(h)


def cmd_live():
    """现场重取 entry 列表，逐条打印字段。"""
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        d = wmpick.load()
        if not st or not d:
            print("先跑 wmpick.py arm / grab")
            return 1
        cd = pick_cd(h, base, d)
        if not cd:
            print("找不到 feature=108 的卡片容器")
            return 1
        mb = st["mailbox"]
        print("cd=%#x" % cd)
        meta = wmpick.call(h, base, mb, wmpick.RVA_GET_META, cd)
        print("meta=%#x" % (meta or 0))
        if meta:
            print("  meta +0x10=%s +0x18=%#x +0x20=%s"
                  % (wmpick.i32(h, meta + 0x10), wmpick.q(h, meta + 0x18) or 0,
                     wmpick.i32(h, meta + 0x20)))
        print("  feature=%s" % wmpick.call(h, base, mb, wmpick.RVA_GET_FEATURE, cd))
        print("  showType=%s" % wmpick.call(h, base, mb, wmpick.RVA_GET_SHOWTYPE, cd))
        print("  LJMINEONAFF=%s" % wmpick.call(h, base, mb, RVA_LJMIN, cd))
        lst = wmpick.call(h, base, mb, wmpick.RVA_GET_ENTRIES, cd)
        items, n = wmpick.list_items(h, lst) if lst else (None, 0)
        print("  entryList=%#x items=%#x size=%d" % (lst or 0, items or 0, n))
        for i in range(min(n, 8)):
            e = wmpick.q(h, items + 0x20 + i * 8)
            if not e:
                continue
            print("    [%d] %#x  +0x10=%s  +0x14=%s"
                  % (i, e, wmpick.i32(h, e + 0x10), wmpick.i32(h, e + 0x14)))
        return 0
    finally:
        icall.k32.CloseHandle(h)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "asm"
    if cmd == "asm":
        return cmd_asm()
    if cmd == "entry":
        return cmd_entry()
    if cmd == "live":
        return cmd_live()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
