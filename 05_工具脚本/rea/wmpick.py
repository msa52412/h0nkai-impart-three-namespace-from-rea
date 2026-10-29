# -*- coding: utf-8 -*-
"""wmpick —— 世界地图卡片「点击时」捕获 + 重定向到迪拉克之海

目标
----
把迪拉克之海（FeatureType 108）挂到悬赏委托卡片（FeatureType 109）上。
服务端改不了（GetWorldMapDataRsp 不含入口列表），ctable 是加密的，
所以走运行时：在 DoClickAction 入口装 stub，命中目标卡片就直接往信箱
塞一条 GoToOWEndless 命令，下一帧由 Update 取走执行。

⚠ 2026-10-25 17:27 崩溃事故（务必先读）
----------------------------------------
旧版曾尝试「把 ExcelMeta 的 FeatureType 从 109 改成 108」，写 `[meta+0x18]+0x20`。
反汇编证明那里是一个 **64 位指针**，不是 int 字段：

    0x1843b2d25  mov  r10, [rcx+0x20]      ; rcx = [meta+0x18]
    0x1843b2d5e  cmp  edx, [r10+0x18]      ; ★ 崩溃点，解引用 r10

把低 32 位改成 108 后指针变成 0x70040000006C，再读就 c0000005。
事件查看器实证：17:27:28 BH3.exe / UserAssembly.dll / c0000005 / 偏移 0x43B2D5E。

更关键：AAGPFOHOKJL(0x43B2280) 里全是 bts / test byte [..+0x20] 位操作，
说明 FeatureType 在内存里存的是**位图**，RVA_GET_FT 返回的 int[] 只是转换产物。

结论：**永远不要写 ExcelMeta 内存**。点击接线靠 ExcelMeta 指针身份匹配，
卡片是不是 108 完全不影响。`ftpatch` 已封存为只打印警告。

为什么挂 DoClickAction 而不是 OnClick
-------------------------------------
OnClick 的函数头是 push rbx / sub rsp,0x20 / mov rbx,rcx / mov ecx,0xcdc / call IsPatched，
覆盖 14 字节必然包含那个 call rel32（目标在块外），icall 的 unsafe_replay 会拒绝。
DoClickAction 的头部是 7 个 push + sub rsp,0x70（共 15 字节），全位置无关，可安全挂钩。

内存布局依据（bh3_layout6.tsv 实证）
------------------------------------
MonoWorldMapEntryContainerBase   +0xC8  ContainerData (MoleMole.OODENFBANCC)
OODENFBANCC   +0x18  LMAMHLCNBDL  -> ExcelMeta.FIGGCBHEGMC   (getter IEIBKDKPKPE)
              +0x20  List<FNPIAMHFCKC>  (getter ACEGIOFPCNN，+0x10 长度)
ExcelMeta.FIGGCBHEGMC  +0x10 int(PFCFININFLF)  +0x18 ptr(EOCAKFNLANC)  +0x20 int(FBOLCFNDCBB)
FNPIAMHFCKC  +0x10 AMICHAGCAMD (GeneralActivityType)   +0x14 FBOLCFNDCBB (int)  +0x18 (锁判定用)
List<T>  +0x10 _items  +0x18 _size(int32)  +0x20 元素起，每元素 8 字节

用法
----
    python wmpick.py arm          装信箱（如需）+ 挂钩 + 清槽
    python wmpick.py setup --yes  重启后一键重做：解锁补丁 + 点击接线
    python wmpick.py status       看挂钩状态
    python wmpick.py clickoff     撤掉点击接线
    python wmpick.py unlockoff    撤掉解锁补丁

安全：arm / grab / status / tabs 只读；setup --yes 只写两处
      （解锁补丁 5 字节 + 自建 stub 区），不碰任何 il2cpp 托管对象。
"""
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, ".wmpick.json")

# ---- RVA ----
RVA_DOCLICK      = 0x2CFB880   # MonoWorldMapEntryContainerBase.DoClickAction(IList<int>)
RVA_SETCONTAINER = 0xBFD610    # .set_ContainerData —— 只有 mov [rcx+0xc8],rdx; ret，最好挂
RVA_SETUPCONTAIN = 0x2CFE4C0   # .SetupContainerData   （头部有 call IsPatched，挂不了）
RVA_SETUPALLENTRY = 0x2D08310  # MonoWorldMapUIManager.SetupAllEntryButton —— rcx = 管理器实例
RVA_CURTABLIST   = 0x2D047C0   # MonoWorldMapUIManager.GetCurrentTabEntryList
RVA_COLLECTALL   = 0x2D03FB0   # MonoWorldMapUIManager.CollectAllEntryData
RVA_GETALLBTN    = 0x2D03840   # MonoWorldMapUIManager.CheckAllMissionData（备选，随便一个非内联点）
RVA_GET_META     = 0xA51C00    # OODENFBANCC.IEIBKDKPKPE -> FIGGCBHEGMC
RVA_GET_ENTRIES  = 0xA51730    # OODENFBANCC.ACEGIOFPCNN -> List<FNPIAMHFCKC>
RVA_GET_SHOWTYPE = 0xA518E0    # OODENFBANCC.EMELLCFHFMB -> WorldMapShowContentListType
RVA_GET_FEATURE  = 0xA51E70    # OODENFBANCC.JONKHNOFPPH -> proto.GeneralActivityType
RVA_GET_CONTENT  = 0xA52190    # OODENFBANCC.LFNDLLMAILF -> IList<int>
RVA_GET_FT       = 0x44FBF90   # ExcelMeta.FIGGCBHEGMC.HHCFLLHHHKB -> List<int> (FeatureType)

OFF_CONTAINER = 0xC8
SLOT = 0x40                    # 捕获槽（信箱占 0x00~0x37）

# ---- 目标 ----
# 2026-10-25 实测修正：悬赏委托卡片的 FeatureType 是 109，不是 114。
# 证据：点击 Challenge/Task_6/Cover -> Enter NewWantedMainPageContext，
#       而该卡片的 ContainerData 里 feature=109、entry[+0x10]=109。
# 旧文档写「114 = Wanted」是假设，已被推翻（114 是 EntryID 1006 的 newbie37 引导入口）。
OLD_FEATURE = 109              # 悬赏委托（实测）
NEW_FEATURE = 108              # 迪拉克之海 / OWEndless（EntryID 1012 图标在 SpriteOutput/WorldMap/OWEndless/ 下）


def q(h, va):
    b = icall.read_mem(h, va, 8)
    return struct.unpack("<Q", b)[0] if b and len(b) == 8 else None


def u32(h, va):
    b = icall.read_mem(h, va, 4)
    return struct.unpack("<I", b)[0] if b and len(b) == 4 else None


def i32(h, va):
    b = icall.read_mem(h, va, 4)
    return struct.unpack("<i", b)[0] if b and len(b) == 4 else None


def load():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except Exception:
            return None
    return None


def save(d):
    json.dump(d, open(STATE, "w"), indent=2)


def call(h, base, mb, rva, arg0, wait=5.0):
    """投递一次调用，返回 rax。失败返回 None。"""
    if icall.cmd_call(base + rva, [arg0], wait) != 0:
        return None
    return q(h, mb + 0x30)


def list_items(h, lst):
    """List<T> -> (items_ptr, size)"""
    return q(h, lst + 0x10), (u32(h, lst + 0x18) or 0)


# --------------------------------------------------------------------------
# 环形缓冲钩子
#
# 为什么不用 icall.cmd_hook
# ------------------------
# cmd_hook 的捕获 stub 只把 rcx 写到一个固定槽，后一次覆盖前一次。
# 面板里十几张卡片是在几帧内连续装配的，单槽只能留下最后一张。
# 所以这里自己生成一个「追加式」stub：把每次的 rcx 依次写进环形缓冲。
#
#     mov r11, ring          ; 49 BB <ring>
#     mov rax, [r11]         ; 49 8B 03        rax = 已记录条数
#     cmp rax, CAP           ; 48 3D <cap>
#     jae skip               ; 73 0B
#     mov [r11+rax*8+8], rcx ; 49 89 4C C3 08
#     inc rax                ; 48 FF C0
#     mov [r11], rax         ; 49 89 03
#  skip:
#     <被覆盖的原始指令>
#     jmp resume             ; FF 25 00000000 <resume>
#
# 只动 rax / r11，两个都是调用者保存寄存器，函数入口处不承载有效值。
# --------------------------------------------------------------------------
RING_OFF = 0x7000
RING_CAP = 500


def build_ring_stub(ring_va, resume_va, orig):
    b = b""
    b += b"\x49\xBB" + struct.pack("<Q", ring_va)   # mov r11, ring
    b += b"\x49\x8B\x03"                            # mov rax, [r11]
    b += b"\x48\x3D" + struct.pack("<I", RING_CAP)  # cmp rax, CAP
    b += b"\x73\x0B"                                # jae skip
    b += b"\x49\x89\x4C\xC3\x08"                    # mov [r11+rax*8+8], rcx
    b += b"\x48\xFF\xC0"                            # inc rax
    b += b"\x49\x89\x03"                            # mov [r11], rax
    b += orig
    b += b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", resume_va)
    return b


def cmd_ring():
    """把 set_ContainerData 换成环形缓冲钩子，记录所有卡片实例。"""
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("信箱未装，先跑 python wmpick.py arm")
            return 1
        page = st["page"]
        hooks = st.setdefault("hooks", {})
        key = str(RVA_SETCONTAINER)
        fn_va = base + RVA_SETCONTAINER

        if key in hooks:
            print("set_ContainerData 已挂环形钩子（stub %#x）" % hooks[key]["stub"])
            icall.write_mem(h, page + RING_OFF, b"\x00" * 0x1000)
            print("已清空环形缓冲。去游戏里重新打开一次「挑战」面板。")
            return 0

        L = icall.insn_len_at(RVA_SETCONTAINER)
        orig = icall.file_bytes(RVA_SETCONTAINER, L)
        cur = icall.read_mem(h, fn_va, L)
        if cur != orig:
            print("✗ 入口字节与文件不一致（%s vs %s），跳过"
                  % (cur.hex(" ") if cur else "读取失败", orig.hex(" ")))
            return 1

        n = len(hooks)
        stub_va = page + icall.HOOK_BASE_OFF + n * icall.HOOK_SLOT_SIZE
        if icall.HOOK_BASE_OFF + (n + 1) * icall.HOOK_SLOT_SIZE > icall.ALLOC_SIZE:
            print("✗ 挂钩槽位用尽")
            return 1
        ring_va = page + RING_OFF

        bad = icall.unsafe_replay(orig, fn_va, stub_va)
        if bad:
            print("✗ 这段函数头不能安全挂钩：")
            for x in bad:
                print("    " + x)
            return 1

        icall.write_mem(h, ring_va, b"\x00" * 0x1000)
        stub = build_ring_stub(ring_va, fn_va + L, orig)
        if not icall.write_mem(h, stub_va, stub):
            print("✗ stub 写入失败")
            return 1
        back = icall.read_mem(h, stub_va, len(stub))
        if back != stub:
            print("✗ stub 落地校验失败，入口未改动")
            return 1
        jmp = b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", stub_va)
        if not icall.write_mem(h, fn_va, jmp):
            print("✗ 入口写入失败")
            return 1
        cur2 = icall.read_mem(h, fn_va, L)
        if not cur2 or cur2[:len(jmp)] != jmp:
            print("✗ 入口回读不符，回滚")
            icall.write_mem(h, fn_va, orig)
            return 1

        hooks[key] = {"slot": ring_va, "stub": stub_va, "len": L,
                      "orig": orig.hex(), "ring": True}
        icall.save_state(st)
        print("✓ 已挂环形钩子 RVA %#x（覆盖 %d 字节，原始 %s）" % (RVA_SETCONTAINER, L, orig.hex(" ")))
        print("  入口 %#x → stub %#x，记录写到环形缓冲 %#x（容量 %d）"
              % (fn_va, stub_va, ring_va, RING_CAP))
        print("\n现在去游戏里：")
        print("   1) 关掉挑战面板再重新打开（或退出世界地图再进）")
        print("   2) 回来跑： python wmpick.py dump")
        return 0
    finally:
        icall.k32.CloseHandle(h)


def cmd_dump():
    """读出环形缓冲里所有卡片，逐个解析 ContainerData。"""
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("状态失效，先跑 python wmpick.py arm")
            return 1
        page, mb = st["page"], st["mailbox"]
        ring = page + RING_OFF

        raw = icall.read_mem(h, ring, 8)
        n = struct.unpack("<Q", raw)[0] if raw else 0
        print("环形缓冲记录 %d 条" % n)
        if not n:
            print("  空的 —— 面板还没重新装配。去游戏里关掉挑战面板再打开一次。")
            return 1
        n = min(n, RING_CAP)

        blob = icall.read_mem(h, ring + 8, n * 8)
        vals = [struct.unpack("<Q", blob[i:i + 8])[0] for i in range(0, n * 8, 8)]

        seen = []
        for v in vals:
            if v and v not in seen:
                seen.append(v)
        print("去重后 %d 个不同卡片实例\n" % len(seen))

        rows = []
        for this in seen:
            cd = q(h, this + OFF_CONTAINER)
            if not cd:
                print("  this=%#x  ContainerData=null（装配中/已回收）" % this)
                continue
            feat = call(h, base, mb, RVA_GET_FEATURE, cd)
            meta = call(h, base, mb, RVA_GET_META, cd)
            showtype = call(h, base, mb, RVA_GET_SHOWTYPE, cd)
            lst = call(h, base, mb, RVA_GET_ENTRIES, cd)
            mid = i32(h, meta + 0x20) if meta else None
            ent = []
            if lst:
                items, cnt = list_items(h, lst)
                for i in range(min(cnt, 8)):
                    e = q(h, items + 0x20 + i * 8)
                    if e:
                        ent.append((i32(h, e + 0x10), i32(h, e + 0x14)))
            rows.append({"this": this, "cd": cd, "feat": feat, "meta": meta,
                         "id": mid, "showtype": showtype, "entries": ent})
            print("  this=%#x cd=%#x feature=%-4s meta.ID=%-4s showType=%s entries=%s"
                  % (this, cd, feat, mid, showtype, ent))

        save({"pid": pid, "cards": rows})
        print("\n已记录到 %s" % STATE)
        print("\n对照表：FeatureType 114 = 悬赏委托(EntryID 1006, ID 6)；108 = 迪拉克之海(EntryID 1012, ID 15)")
        return 0
    finally:
        icall.k32.CloseHandle(h)


def cmd_ringoff():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        return icall.cmd_unhook(RVA_SETCONTAINER)
    finally:
        icall.k32.CloseHandle(h)


# --------------------------------------------------------------------------
# 管理器捕获：一次拿到 MonoWorldMapUIManager 实例，然后从它枚举全部卡片
# --------------------------------------------------------------------------
MGR_SLOT = 0x48


def cmd_mgrarm():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("信箱未装，先跑 python wmpick.py arm")
            return 1
        icall.write_mem(h, st["page"] + MGR_SLOT, b"\x00" * 8)
        hooks = st.get("hooks", {})
        if str(RVA_SETUPALLENTRY) in hooks:
            print("SetupAllEntryButton 已挂钩，槽已清空。")
        else:
            print("挂钩 SetupAllEntryButton (RVA %#x)…" % RVA_SETUPALLENTRY)
            if icall.cmd_hook(RVA_SETUPALLENTRY, MGR_SLOT) != 0:
                return 1
        print("\n现在去游戏里：关掉挑战面板再打开（或退出世界地图再进）。")
        print("然后跑： python wmpick.py mgrdump")
        return 0
    finally:
        icall.k32.CloseHandle(h)


def _dump_card(h, base, mb, this, tag=""):
    cd = q(h, this + OFF_CONTAINER)
    if not cd:
        print("  %sthis=%#x  ContainerData=null" % (tag, this))
        return None
    feat = call(h, base, mb, RVA_GET_FEATURE, cd)
    meta = call(h, base, mb, RVA_GET_META, cd)
    showtype = call(h, base, mb, RVA_GET_SHOWTYPE, cd)
    mid = i32(h, meta + 0x20) if meta else None
    lst = call(h, base, mb, RVA_GET_ENTRIES, cd)
    ent = []
    if lst:
        items, cnt = list_items(h, lst)
        for i in range(min(cnt, 8)):
            e = q(h, items + 0x20 + i * 8)
            if e:
                ent.append((i32(h, e + 0x10), i32(h, e + 0x14)))
    print("  %sthis=%#x cd=%#x feature=%-4s meta.ID=%-4s showType=%s entries=%s"
          % (tag, this, cd, feat, mid, showtype, ent))
    return {"this": this, "cd": cd, "feat": feat, "meta": meta,
            "id": mid, "showtype": showtype, "entries": ent}


def cmd_mgrdump():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("状态失效，先跑 python wmpick.py arm")
            return 1
        page, mb = st["page"], st["mailbox"]

        raw = icall.read_mem(h, page + MGR_SLOT, 8)
        mgr = struct.unpack("<Q", raw)[0] if raw else 0
        if not mgr:
            print("管理器槽是空的 —— SetupAllEntryButton 还没被调用过。")
            print("  去游戏里关掉挑战面板再打开一次，然后重跑。")
            return 1
        print("MonoWorldMapUIManager 实例 = %#x" % mgr)

        # 1) 当前标签页的卡片列表
        lst = call(h, base, mb, RVA_CURTABLIST, mgr)
        print("GetCurrentTabEntryList() = %#x" % (lst or 0))
        cards = []
        if lst:
            items, cnt = list_items(h, lst)
            print("  size=%d  items=%#x" % (cnt, items or 0))
            for i in range(min(cnt, 24)):
                c = q(h, items + 0x20 + i * 8)
                if not c:
                    print("  [%d] null" % i)
                    continue
                r = _dump_card(h, base, mb, c, tag="[%d] " % i)
                if r:
                    r["idx"] = i
                    cards.append(r)

        # 2) 如果空，退一步把管理器原始对象打出来，方便我按实际布局再改
        if not cards:
            print("\n当前标签页没拿到卡片。管理器原始 0x100 字节：")
            blob = icall.read_mem(h, mgr, 0x100)
            for i in range(0, len(blob), 16):
                seg = blob[i:i + 16]
                print("  %#012x  %-47s  %s" % (
                    mgr + i, seg.hex(" "),
                    "".join(chr(c) if 32 <= c < 127 else "." for c in seg)))

        save({"pid": pid, "mgr": mgr, "cards": cards})
        print("\n已记录到 %s（%d 张卡片）" % (STATE, len(cards)))
        print("对照：FeatureType 114 = 悬赏委托(EntryID 1006, ID 6)；108 = 迪拉克之海(EntryID 1012, ID 15)")
        return 0
    finally:
        icall.k32.CloseHandle(h)


def cmd_mgroff():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        return icall.cmd_unhook(RVA_SETUPALLENTRY)
    finally:
        icall.k32.CloseHandle(h)


# 三个标签页的卡片列表字段（由 GetCurrentTabEntryList 反汇编实证）
TAB_FIELDS = [(0xB0, "tab1/进攻"), (0xB8, "tab2/挑战"), (0xC0, "tab3/活动")]


def cmd_retarget():
    """把捕获到的那张卡片的 FeatureType 改成 108（迪拉克之海）。

    只改运行时 entry 对象的 [+0x10]，不动配置行：
      - 配置行的 FeatureType 数组一旦改掉，管理器会按新 feature 去找卡片容器，
        找不到就整张卡消失；
      - 运行时 entry 是点击时真正被读的那份数据，改它影响面最小。
    """
    go = "--yes" in sys.argv
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("信箱未装，先跑 python wmpick.py arm")
            return 1
        mb = st["mailbox"]
        d = load()
        if not d or d.get("pid") != pid or not d.get("cd"):
            print("还没有 grab 结果，先跑 python wmpick.py grab")
            return 1
        cd = d["cd"]
        # 注意：ContainerData 对象是稳定的（同一个入口在不同标签页共用同一个对象），
        # 但里面的 entryList 每次打开面板都会重建，所以不能用 grab 时存下的指针，
        # 必须现场重新调 ACEGIOFPCNN 取当前列表。
        lst = call(h, base, mb, RVA_GET_ENTRIES, cd)
        if not lst:
            print("ACEGIOFPCNN(cd) 返回 null，ContainerData 可能已失效")
            return 1

        items, n = list_items(h, lst)
        if not items or not n:
            print("entryList 读不出来（%#x / size=%s），卡片可能已销毁，重跑 grab"
                  % (items or 0, n))
            return 1

        print("ContainerData = %#x   entryList size=%d" % (cd, n))
        targets = []
        for i in range(min(n, 16)):
            e = q(h, items + 0x20 + i * 8)
            if not e:
                continue
            f = i32(h, e + 0x10)
            c = i32(h, e + 0x14)
            print("  [%d] entry=%#x  FeatureType=%s  contentID=%s" % (i, e, f, c))
            if f == OLD_FEATURE:
                targets.append((i, e, f))

        if not targets:
            print("\n没有 FeatureType=%d 的 entry。" % OLD_FEATURE)
            print("把上面这行发我，我按实际值改 OLD_FEATURE。")
            return 1

        print("\n计划：把 %d 个 entry 的 [+0x10] 从 %d 写成 %d"
              % (len(targets), OLD_FEATURE, NEW_FEATURE))
        if not go:
            print("（演练。确认后加 --yes 真正写入）")
            return 0

        for i, e, f in targets:
            ok = icall.write_mem(h, e + 0x10, struct.pack("<i", NEW_FEATURE))
            now = i32(h, e + 0x10)
            print("  [%d] %#x  %d -> %s  %s"
                  % (i, e, f, now, "✓" if ok and now == NEW_FEATURE else "✗"))
        print("\n现在回游戏点一下 Task_6（悬赏委托那张卡）。")
        print("预期：进 OWEndlessStubPageContext / 迪拉克界面，而不是 NewWantedMainPageContext。")
        return 0
    finally:
        icall.k32.CloseHandle(h)


def cmd_ftpatch():
    """【已禁用】改配置行里的 FeatureType。

    2026-10-25 17:27 崩溃事故后封存
    ------------------------------
    这个命令原本写 `HHCFLLHHHKB(meta)+0x20`。反汇编证明那不是一个 int 字段，
    而是 AAGPFOHOKJL 从**位图**转换出来的临时 int[]：

        0x1843b2d25  mov  r10, [rcx+0x20]      ; rcx = [meta+0x18]
        0x1843b2d5e  cmp  edx, [r10+0x18]      ; 越界检查后 test byte [r10+rdx+0x20]

    所以写进去既不会改变 getter 的返回值（它每次都重新转换），
    又因为 `[meta+0x18]+0x20` 本身是个指针，写错位置会直接打坏堆指针。
    实测后果：c0000005 @ 0x43B2D5E，游戏崩溃。

    结论：FeatureType 这条路彻底封掉。点击接线靠 ExcelMeta 指针身份匹配，
    不需要 FeatureType 变成 108。保留函数只是为了留个说明。
    """
    print("【已禁用】ftpatch 会写坏 ExcelMeta 的位图指针，导致 c0000005 崩溃。")
    print("  实证：2026-10-25 17:27:28 BH3.exe / UserAssembly.dll / 偏移 0x43B2D5E")
    print("  FeatureType 在内存里是位图，不是 int 数组；点击接线也不需要改它。")
    print("  需要重做改动请用：python wmpick.py setup --yes")
    return 1


# --------------------------------------------------------------------------
# 解锁补丁：LJMINEONAFF 循环里「status==2 就记 2」改成「直接判 3」
#
# 2026-10-25 反汇编实证（0xA521F0 起）：
#     22a2  call ...            ; ebx = 等级
#     22b3  jl  -> 返回 1       ; 等级 < UnlockLevel
#     22c3  jl  -> 返回 2       ; 等级 < UnlockHintLevel   （旧补丁改的是这里，走不到）
#     22c9  mov ebx, 1          ; ★ 默认值 1
#     2327  call [rax+0x1a8]    ; entry.GetWorldMapEntryStatus()
#     232d  cmp eax, 3
#     2330  je  233e            ; ==3 -> ebx=3 并跳出
#     2332  cmp eax, 2
#     2335  jne 2300            ; !=2 -> 继续循环
#     2337  mov ebx, eax        ; ==2 -> ebx=2  ★ 真正产出 2 的地方
#     233e  mov ebx, 3
#
# 而 entry.GetWorldMapEntryStatus（RVA 0x682FC0）只有两个出口：
#     rcx = [entry+0x18]
#     if (!rcx) return 2                       ; ← 我们这张卡的 +0x18 就是 NULL
#     if (!f(rcx)) return 2
#     return 3
# 那个 +0x18 是构造 entry 时解析出来的引用，改 +0x10/+0x14 不会让它重新解析，
# 所以数据层没法救，只能在 LJMINEONAFF 里把 2 当 3。
#
# 补丁：0x2332 起 5 字节  83 f8 02 75 c9  ->  eb 0a 90 90 90
# 效果：循环里只要碰到 entry 就 ebx=3 并跳出（等价于「忽略 entry 级锁」）。
# 只影响 LJMINEONAFF 一个函数，随时可还原。
# --------------------------------------------------------------------------
PATCH_OLD = bytes.fromhex("83f80275c9")      # cmp eax,2 / jne 0x2300
PATCH_NEW = bytes.fromhex("eb0a909090")      # jmp 0x233e / nop nop nop
RVA_UNLOCK = 0xA52332                        # 上面那 5 字节的起始 RVA
RVA_STATUS2 = 0xA52398                       # 旧补丁位置（仅用于还原）


def _revert_old_status2(h, base):
    va = base + RVA_STATUS2
    cur = icall.read_mem(h, va, 5)
    if cur and cur[:5] == b"\xb8\x03\x00\x00\x00":
        icall.write_mem(h, va + 1, b"\x02")
        print("  已还原旧补丁 %#x 的立即数 03 -> 02" % (va + 1))


def cmd_unlock():
    go = "--yes" in sys.argv
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        va = base + RVA_UNLOCK
        cur = icall.read_mem(h, va, 5)
        print("LJMINEONAFF 循环分支 @ %#x : %s" % (va, cur.hex(" ") if cur else "读取失败"))
        if not cur or len(cur) < 5:
            return 1
        if cur[:5] == PATCH_NEW:
            print("补丁已在位（eb 0a 90 90 90）")
            return 0
        if cur[:5] != PATCH_OLD:
            print("✗ 不是预期的 %s，拒绝改写" % PATCH_OLD.hex(" "))
            return 1
        if not go:
            print("计划：%#x 处 %s -> %s（5 字节）"
                  % (va, PATCH_OLD.hex(" "), PATCH_NEW.hex(" ")))
            print("      cmp eax,2 / jne 循环  →  jmp 0x233e（ebx=3 并跳出）")
            print("（演练。确认后加 --yes）")
            return 0
        _revert_old_status2(h, base)
        ok = icall.write_mem(h, va, PATCH_NEW)
        back = icall.read_mem(h, va, 5)
        print("写入 %s，当前 %s" % ("成功" if ok else "失败", back.hex(" ") if back else "?"))
        if not back or back[:5] != PATCH_NEW:
            print("✗ 回读不符")
            return 1
        return _verify(h, base)
    finally:
        icall.k32.CloseHandle(h)


def _verify(h, base):
    st = icall.load_state()
    d = load()
    if not st or not d:
        print("（没有 arm/grab 记录，跳过验证）")
        return 0
    mb = st["mailbox"]
    cd, card = None, None
    for c in d.get("cards", []):
        if c.get("feat") == NEW_FEATURE:
            cd, card = c.get("cd"), c.get("this")
    if not cd:
        print("（没有 feature=%d 的卡片记录，跳过验证）" % NEW_FEATURE)
        return 0
    print("\n--- 验证 ---")
    for name, rva, arg, want in (
            ("LJMINEONAFF(cd)", 0xA521F0, cd, 3),
            ("GetFeatureStatus(card)", 0x2CFC9A0, card, 3),
            ("IsFeatureUnlock(card)", 0x2CFCD50, card, 1)):
        if not arg:
            continue
        r = call(h, base, mb, rva, arg)
        mark = "✓" if r == want else "✗"
        print("  %s %-24s 期望 %d  实际 %s" % (mark, name, want, r if r is None else int(r)))
    return 0


def cmd_unlockoff():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        va = base + RVA_UNLOCK
        ok = icall.write_mem(h, va, PATCH_OLD)
        back = icall.read_mem(h, va, 5)
        print("还原 %s，当前 %s" % ("成功" if ok else "失败", back.hex(" ") if back else "?"))
        _revert_old_status2(h, base)
        return 0
    finally:
        icall.k32.CloseHandle(h)


def cmd_restore():
    """把 FeatureType 改回 109。"""
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("信箱未装，先跑 python wmpick.py arm")
            return 1
        mb = st["mailbox"]
        d = load()
        if not d or not d.get("cd"):
            print("没有 grab 记录")
            return 1
        lst = call(h, base, mb, RVA_GET_ENTRIES, d["cd"])
        if not lst:
            print("entryList 取不到")
            return 1
        items, n = list_items(h, lst)
        cnt = 0
        for i in range(min(n, 16)):
            e = q(h, items + 0x20 + i * 8) if items else None
            if not e:
                continue
            if i32(h, e + 0x10) == NEW_FEATURE:
                icall.write_mem(h, e + 0x10, struct.pack("<i", OLD_FEATURE))
                print("  [%d] %#x  %d -> %d" % (i, e, NEW_FEATURE, i32(h, e + 0x10)))
                cnt += 1
        print("已还原 %d 个 entry" % cnt)
        return 0
    finally:
        icall.k32.CloseHandle(h)


def cmd_tabs():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        d = load()
        if not st or not d:
            print("先跑 python wmpick.py arm / mgrarm")
            return 1
        page, mb = st["page"], st["mailbox"]

        mgr = d.get("mgr")
        if not mgr or d.get("pid") != pid:
            raw = icall.read_mem(h, page + MGR_SLOT, 8)
            mgr = struct.unpack("<Q", raw)[0] if raw else 0
        if not mgr:
            print("管理器实例未知 —— 去游戏里开关一次挑战面板，再跑 mgrdump")
            return 1
        print("MonoWorldMapUIManager = %#x  当前 tab=[+0xEC]=%s\n"
              % (mgr, i32(h, mgr + 0xEC)))

        all_cards = []
        for off, name in TAB_FIELDS:
            lst = q(h, mgr + off)
            print("=== %s  [mgr+%#x] = %#x ===" % (name, off, lst or 0))
            if not lst:
                print("  (空)\n")
                continue
            items, cnt = list_items(h, lst)
            print("  size=%d  items=%#x" % (cnt, items or 0))
            for i in range(min(cnt, 24)):
                c = q(h, items + 0x20 + i * 8)
                if not c:
                    print("  [%d] null" % i)
                    continue
                r = _dump_card(h, base, mb, c, tag="[%d] " % i)
                if r:
                    r["idx"] = i
                    r["tab"] = name
                    all_cards.append(r)
            print()

        save({"pid": pid, "mgr": mgr, "cards": all_cards})
        print("共 %d 张卡片，已记录到 %s" % (len(all_cards), STATE))

        hit = [c for c in all_cards if c["feat"] == OLD_FEATURE]
        print("\nFeatureType=%d 的卡片：%d 张" % (OLD_FEATURE, len(hit)))
        for c in hit:
            print("  %s [%d] this=%#x cd=%#x meta.ID=%s"
                  % (c["tab"], c["idx"], c["this"], c["cd"], c["id"]))
        if not hit:
            print("  没有 114 —— 挑战页可能还没装配，或该入口不在这三个列表里。")
        return 0
    finally:
        icall.k32.CloseHandle(h)





# --------------------------------------------------------------------------
def cmd_arm():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("装信箱…")
            if icall.cmd_install() != 0:
                return 1
            st = icall.load_state()
        else:
            cur = icall.read_mem(h, base + icall.HOST_RVA, 14)
            if not cur or cur[:2] != b"\xFF\x25":
                print("信箱状态文件在但入口不是钩子 → 重装")
                if icall.cmd_install() != 0:
                    return 1
                st = icall.load_state()
        mb = st["mailbox"]
        # 清捕获槽
        icall.write_mem(h, st["page"] + SLOT, b"\x00" * 8)
        icall.write_mem(h, st["page"] + MGR_SLOT, b"\x00" * 8)

        hooks = st.get("hooks", {})
        if str(RVA_DOCLICK) not in hooks:
            print("挂钩 DoClickAction (RVA %#x)…" % RVA_DOCLICK)
            if icall.cmd_hook(RVA_DOCLICK, SLOT) != 0:
                return 1
            st = icall.load_state()
            hooks = st.get("hooks", {})
        else:
            print("DoClickAction 已挂钩")

        # 管理器实例：setup 要靠它现场找卡片，所以 arm 顺手一起挂
        if str(RVA_SETUPALLENTRY) not in hooks:
            print("挂钩 SetupAllEntryButton (RVA %#x)…" % RVA_SETUPALLENTRY)
            if icall.cmd_hook(RVA_SETUPALLENTRY, MGR_SLOT) != 0:
                return 1
            st = icall.load_state()
        else:
            print("SetupAllEntryButton 已挂钩")

        save({"pid": pid, "base": base, "page": st["page"], "mailbox": mb})
        print("\n✓ 已就绪。现在去游戏里：")
        print("   1) 打开世界地图 -> 挑战面板（关掉再打开一次，让管理器钩子抓到实例）")
        print("   2) 回来跑： python wmpick.py setup --yes")
        print("      （会自动做：解锁补丁 + 点击接线；不动 FeatureType）")
        print("   3) 再点那张卡")
        return 0
    finally:
        icall.k32.CloseHandle(h)


def cmd_grab():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        d = load()
        if not st or not d or d.get("pid") != pid:
            print("状态失效，先跑 python wmpick.py arm")
            return 1
        page, mb = st["page"], st["mailbox"]

        raw = icall.read_mem(h, page + SLOT, 8)
        this = struct.unpack("<Q", raw)[0] if raw else 0
        if not this:
            print("捕获槽是空的 —— 还没有卡片被点击过。")
            print("  去游戏里点一下「悬赏委托」卡片，再跑一次 grab。")
            print("  若点了仍为空，说明这条链没走 DoClickAction，改挂 SetupContainerData（见文件头注释）。")
            return 1

        print("卡片实例 this = %#x" % this)
        klass = q(h, this)
        print("  klass = %#x" % (klass or 0))

        cd = q(h, this + OFF_CONTAINER)
        print("  ContainerData [this+%#x] = %#x" % (OFF_CONTAINER, cd or 0))
        if not cd:
            print("  ✗ ContainerData 为空，可能 this 抓错了（或者卡片还没装配完）")
            return 1

        print("\n--- ContainerData 原始 0x60 字节 ---")
        blob = icall.read_mem(h, cd, 0x60)
        for i in range(0, len(blob), 16):
            seg = blob[i:i + 16]
            print("  %#012x  %-47s  %s" % (
                cd + i, seg.hex(" "),
                "".join(chr(c) if 32 <= c < 127 else "." for c in seg)))

        meta = call(h, base, mb, RVA_GET_META, cd)
        showtype = call(h, base, mb, RVA_GET_SHOWTYPE, cd)
        feat = call(h, base, mb, RVA_GET_FEATURE, cd)
        print("\n  meta(FIGGCBHEGMC) = %#x" % (meta or 0))
        print("  ShowContentListType = %s" % showtype)
        print("  JONKHNOFPPH() feature = %s" % feat)

        if meta:
            print("  meta: EntryID?[+0x10]=%s  ptr[+0x18]=%#x  int[+0x20]=%s"
                  % (i32(h, meta + 0x10), q(h, meta + 0x18) or 0, i32(h, meta + 0x20)))

        lst = call(h, base, mb, RVA_GET_ENTRIES, cd)
        print("\n  entryList = %#x" % (lst or 0))
        if lst:
            items, n = list_items(h, lst)
            print("  items=%#x  size=%d" % (items or 0, n))
            for i in range(min(n, 16)):
                e = q(h, items + 0x20 + i * 8)
                if not e:
                    print("    [%d] null" % i)
                    continue
                print("    [%d] entry=%#x  +0x10=%s  +0x14=%s  +0x18=%s  +0x1C=%s"
                      % (i, e, i32(h, e + 0x10), i32(h, e + 0x14),
                         i32(h, e + 0x18), i32(h, e + 0x1C)))

        cids = call(h, base, mb, RVA_GET_CONTENT, cd)
        if cids:
            items, n = list_items(h, cids)
            vals = []
            for i in range(min(n, 12)):
                v = q(h, items + 0x20 + i * 8)
                vals.append(v if v is not None else 0)
            print("  contentIDList(size=%d) = %s" % (n, vals))

        d.update({"this": this, "cd": cd, "meta": meta, "lst": lst,
                  "showtype": showtype, "feature": feat})
        save(d)
        print("\n已记录到 %s" % STATE)
        return 0
    finally:
        icall.k32.CloseHandle(h)


def cmd_patch():
    go = "--yes" in sys.argv
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        d = load()
        if not d or d.get("pid") != pid or not d.get("this"):
            print("还没有 grab 结果，先跑 python wmpick.py grab")
            return 1
        cd = d.get("cd")
        lst = d.get("lst")
        if not cd or not lst:
            print("grab 记录里没有 ContainerData / entryList，重跑 grab")
            return 1

        items, n = list_items(h, lst)
        if not items:
            print("entryList 读不出来")
            return 1

        # 找出所有 featureType == 114 的 entry
        hits = []
        for i in range(n):
            e = q(h, items + 0x20 + i * 8)
            if not e:
                continue
            f = i32(h, e + 0x10)
            if f == OLD_FEATURE:
                hits.append((i, e, f))
        print("entryList 共 %d 条，其中 FeatureType=%d 的有 %d 条"
              % (n, OLD_FEATURE, len(hits)))
        for i, e, f in hits:
            print("  [%d] entry=%#x  FeatureType=%d" % (i, e, f))
        if not hits:
            print("没有找到 FeatureType=%d 的 entry。" % OLD_FEATURE)
            print("可能 grab 抓到的是别的卡片，或者 FeatureType 不在 entry+0x10。")
            print("把 grab 的完整输出发我，我按实际布局改。")
            return 1

        print("\n计划：把上面每个 entry 的 [+0x10] 从 %d 写成 %d"
              % (OLD_FEATURE, NEW_FEATURE))
        if not go:
            print("\n（这是演练。确认无误后加 --yes 真正写入）")
            return 0

        for i, e, f in hits:
            ok = icall.write_mem(h, e + 0x10, struct.pack("<i", NEW_FEATURE))
            now = i32(h, e + 0x10)
            print("  [%d] %#x  %d -> %s  %s"
                  % (i, e, f, now, "✓" if ok and now == NEW_FEATURE else "✗"))
        print("\n现在回游戏，再点一次那张卡片。")
        return 0
    finally:
        icall.k32.CloseHandle(h)


def cmd_off():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        return icall.cmd_unhook(RVA_DOCLICK)
    finally:
        icall.k32.CloseHandle(h)


# --------------------------------------------------------------------------
# 点击接线：把这张卡的点击接到 OWEndlessModule.GoToOWEndless
#
# 为什么必须走代码而不是改数据
# ----------------------------
# 卡片实例的 C# 类型是 MonoWorldMapWantedEntry，ContainerData 里的 entry 是
# 「章节入口」那一支，它的虚方法 GoToAction（0x683030 -> HIIJLPBCCPK）打开的是
# ChapterSelectPageContext。改 entry 的 +0x10/+0x14 换不掉 vtable，所以点击永远
# 到不了迪拉克。而 entry 的 +0x18（活动数据对象）是 NULL，连 GoToAction 都跑不动。
#
# 做法
# ----
# 在 DoClickAction 入口挂一个 stub：
#   1) 照旧把 rcx 写进捕获槽（grab 还能用）
#   2) 顺 this+0xC8 -> +0x18 取 ExcelMeta（WorldMap 配置行指针，进程内唯一且稳定），
#      不等于目标卡的 meta 就原样执行被覆盖的 16 字节，什么都不变
#   3) 是这张卡就往信箱里塞一条 GoToOWEndless 命令（pending=0xA5），
#      由下一帧 Update 的常驻 stub 取走执行
#
# 踩过的坑（2026-10-25 17:2x）
# --------------------------
# 第一版把「捕获槽」和「信箱头」当成同一个地址（都用 page+0），stub 一进去就用
# mov [r11], rcx 把信箱头写成了卡片指针，pending 从 0xA5 变成 0xC0，Update 直接跳过。
# 捕获槽是 page+0x40，信箱头是 page+0x00，必须分开传。
# 另外 FeatureType 数组不能按 int[] 直接读：HHCFLLHHHKB(0x44FBF90) 里是
# [meta+0x18] 再走 AAGPFOHOKJL(x,0,4) 转换，+0x18 处是指针不是长度。所以改用 meta 指针判身份。
#
# 为什么不当场调用：点击回调里直接切页面，等于在 UI 事件处理中销毁面板，
# 有 use-after-free 风险。投递到信箱后延后一帧，调用点回到 Update 里，
# 和之前验证成功的 gotoow.py 第 ④ 步完全同一条路径。
#
# 模块实例不需要挂钩等包：MonoWorldMapEndlessEntry.get_module(0x1A92080) 是标准
# il2cpp 静态字段链，rcx 进来就被覆盖，传 0 即可调用。
# 实证：get_Group() 返回 GroupId=1 GroupLevel=21 CurTopGroupLevel=22，与服务端日志一致。
# --------------------------------------------------------------------------
RVA_GET_MODULE = 0x1A92080     # MonoWorldMapEndlessEntry.get_module -> OWEndlessModule
RVA_GOTO_OW    = 0x19C5E00     # OWEndlessModule.GoToOWEndless
RVA_GET_GROUP  = 0x189DC90     # OWEndlessModule.get_Group（只用于校验模块实例）
CLICK_STUB_OFF = 0x6000        # icall 页内空槽（0x4000/0x5000 已被占用）
CAPTURE_STUB   = 0x4000        # icall 原来的 DoClickAction 捕获 stub


def _resolve_module(h, base):
    st = icall.load_state()
    mb = st["mailbox"]
    if icall.cmd_call(base + RVA_GET_MODULE, [0], 5.0) != 0:
        return None
    raw = icall.read_mem(h, mb + 0x30, 8)
    return struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else None


def build_click_stub(slot_va, mb_va, meta_va, module_va, goto_va, orig, resume_va):
    """见上面注释。

    寄存器只用 r10/r11/rax（全调用者保存），rcx/rdx 原样保留 —— DoClickAction 的
    原始前导里 `mov rdi,rdx` / `mov rbx,rcx` 都要用到它们。

    身份判定用「卡片元数据行指针」而不是 FeatureType 数组：
      [rcx+0xC8] = ContainerData ; [cd+0x18] = ExcelMeta（WorldMap 配置行，进程内唯一且稳定）
    比特征值可靠 —— 那张卡的 FeatureType 本来就是被我们改出来的，直接比配置行指针最干净。
    """
    b = bytearray()
    b += b"\x49\xBB" + struct.pack("<Q", slot_va)        # mov r11, slot（捕获槽，不是信箱头！）
    b += b"\x49\x89\x0B"                                 # mov [r11], rcx
    b += b"\x4C\x8B\x91\xC8\x00\x00\x00"                 # mov r10, [rcx+0xC8]
    jmps = []
    b += b"\x4D\x85\xD2"                                 # test r10, r10
    jmps.append(len(b)); b += b"\x74\x00"                # jz replay
    b += b"\x4D\x8B\x52\x18"                             # mov r10, [r10+0x18]   meta
    b += b"\x48\xB8" + struct.pack("<Q", meta_va)        # mov rax, meta_va
    b += b"\x49\x39\xC2"                                 # cmp r10, rax
    jmps.append(len(b)); b += b"\x75\x00"                # jne replay
    # --- 投递信箱命令（现在才把 r11 换成信箱头） ---
    b += b"\x49\xBB" + struct.pack("<Q", mb_va)          # mov r11, mb
    b += b"\x45\x31\xD2"                                 # xor r10d, r10d
    for off in (0x10, 0x18, 0x20, 0x28, 0x30):
        b += b"\x4D\x89\x53" + bytes([off])              # mov [r11+off], r10
    b += b"\x48\xB8" + struct.pack("<Q", module_va)      # mov rax, module
    b += b"\x49\x89\x43\x10"                             # mov [r11+0x10], rax   arg0
    b += b"\x48\xB8" + struct.pack("<Q", goto_va)        # mov rax, GoToOWEndless
    b += b"\x49\x89\x43\x08"                             # mov [r11+8], rax      target
    b += b"\x41\xC6\x43\x01\x00"                         # mov byte [r11+1], 0   done=0
    b += b"\x41\xC6\x03" + bytes([icall.MAGIC])          # mov byte [r11], 0xA5  pending（最后写）
    replay = len(b)
    for p in jmps:
        rel = replay - (p + 2)
        assert 0 <= rel <= 127, (p, rel)
        b[p + 1] = rel
    b += orig
    b += b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", resume_va)
    return bytes(b)


def _hook_rec():
    st = icall.load_state()
    return (st.get("hooks") or {}).get(str(RVA_DOCLICK))


def _find_target_card(h, base, mb, feat=NEW_FEATURE):
    """现场从 MonoWorldMapUIManager 的三个页签列表里找 feature==feat 的卡片。

    为什么不用 grab 记录：游戏重启后堆地址全变，grab 的 cd/meta 都失效。
    现场走一遍 tab 列表最可靠 —— 前提是挑战面板开着。
    返回 (this, cd, meta) 或 None。
    """
    st = icall.load_state()
    d = load() or {}
    mgr = d.get("mgr") if d.get("pid") == icall.find_pid() else None
    if not mgr:
        raw = icall.read_mem(h, st["page"] + MGR_SLOT, 8)
        mgr = struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else 0
    if not mgr:
        return None
    for off, _name in TAB_FIELDS:
        lst = q(h, mgr + off)
        if not lst:
            continue
        items, n = list_items(h, lst)
        if not items:
            continue
        for i in range(min(n, 24)):
            c = q(h, items + 0x20 + i * 8)
            if not c:
                continue
            cd = q(h, c + OFF_CONTAINER)
            if not cd:
                continue
            f = call(h, base, mb, RVA_GET_FEATURE, cd)
            if f != feat:
                continue
            meta = call(h, base, mb, RVA_GET_META, cd)
            if meta:
                return c, cd, meta
    return None


def cmd_setup():
    """重启游戏后的一键重做：解锁补丁 + 点击接线（**不再动 FeatureType**）。

    为什么需要它：这两处改动全在运行时内存里，游戏一重启就全没了。
    前置条件只有两个：跑过 arm，且挑战面板开着（关掉再打开一次让管理器钩子抓到实例）。

    2026-10-25 17:27 崩溃事故后的修订
    ---------------------------------
    旧版这里还会顺手把 ExcelMeta 的 FeatureType 从 109 改成 108，写的是
    `[meta+0x18]+0x20`。反汇编证明该处是一个 **64 位指针**（指向位图对象），
    不是 int 字段：

        0x1843b2d25  mov  r10, [rcx+0x20]      ; rcx = [meta+0x18]
        0x1843b2d5e  cmp  edx, [r10+0x18]      ; ★ 崩溃点

    把低 32 位改成 108 之后指针变成 0x70040000006C，再解引用就 0xc0000005。
    事件查看器实证：17:27:28 BH3.exe / UserAssembly.dll / c0000005 / 偏移 0x43B2D5E。

    更进一步：AAGPFOHOKJL(0x43B2280) 里全是 bts / test byte [..+0x20] 位操作，
    说明 FeatureType 在内存里存的是**位图**，RVA_GET_FT 返回的 int[] 只是转换产物。
    改它要动位图长度，越界风险极高。

    而点击接线是用 **ExcelMeta 指针身份**匹配的，卡片是不是 108 完全不影响。
    所以这一步永久移除，不再写任何 ExcelMeta 内存。
    """
    go = "--yes" in sys.argv
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("信箱未装/失效，先跑 python wmpick.py arm")
            return 1
        mb = st["mailbox"]

        # 找卡：正常就是 109（悬赏委托）
        hit = _find_target_card(h, base, mb, OLD_FEATURE)
        if not hit:
            hit = _find_target_card(h, base, mb, NEW_FEATURE)
        if not hit:
            print("✗ 三个页签里都没找到目标卡片 —— 挑战面板开着吗？管理器实例抓到了吗？")
            print("  先在游戏里关掉挑战面板再打开，然后重跑本命令。")
            return 1
        this, cd, meta = hit
        print("目标卡片 this=%#x cd=%#x meta=%#x meta.ID=%s feature=%s"
              % (this, cd, meta, i32(h, meta + 0x20),
                 call(h, base, mb, RVA_GET_FEATURE, cd)))

        # 解锁补丁
        uva = base + RVA_UNLOCK
        ucur = icall.read_mem(h, uva, 5)
        need_unlock = ucur != PATCH_NEW
        print("\n计划：")
        print("  %s 解锁补丁    %s -> %s   @ %#x"
              % ("·" if need_unlock else "✓已就位",
                 ucur.hex(" ") if ucur else "?", PATCH_NEW.hex(" "), uva))
        print("  · 点击接线（下面 cmd_click 的输出）")
        print("  （不碰 FeatureType —— 那处是位图指针，写它会崩）")
        if not go:
            print("\n（演练。确认后加 --yes）")
            return 0

        if need_unlock:
            if not ucur or ucur[:5] != PATCH_OLD:
                print("✗ 解锁补丁位置字节不是预期值 %s，拒绝改写" % PATCH_OLD.hex(" "))
                return 1
            _revert_old_status2(h, base)
            icall.write_mem(h, uva, PATCH_NEW)
            back = icall.read_mem(h, uva, 5)
            print("解锁补丁写入 %s" % ("成功" if back == PATCH_NEW else "失败"))
            if back != PATCH_NEW:
                return 1

        print("\n--- 安装点击接线 ---")
        # 直接把现场解析出来的 (this, cd, meta) 传下去，避免二次搜索 ——
        # 之前二次搜索用 feature==108 匹配，而 FeatureType 根本不是 int 字段，
        # 所以必然找不到。
        return cmd_click(hit=hit)
    finally:
        icall.k32.CloseHandle(h)


def cmd_click(hit=None):
    """装点击接线。hit=(this, cd, meta) 可由 cmd_setup 直接传入，省掉二次搜索。"""
    go = "--yes" in sys.argv
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("信箱未装或已失效，先跑 python wmpick.py arm")
            return 1
        page, mb = st["page"], st["mailbox"]

        rec = _hook_rec()
        if rec:
            orig = bytes.fromhex(rec["orig"])
            print("被覆盖的原始字节取自钩子记录（%d 字节）" % len(orig))
        else:
            orig = icall.file_bytes(RVA_DOCLICK, 16)
            print("被覆盖的原始字节取自 DLL 文件（%d 字节）" % len(orig))
        if not orig or len(orig) < 16:
            print("✗ 原始字节取不到，放弃")
            return 1

        mod = _resolve_module(h, base)
        if not mod:
            print("✗ 取不到 OWEndlessModule 实例")
            return 1
        # 交叉校验：get_Group 里应当有 GroupLevel=21 / CurTop=22
        g = None
        if icall.cmd_call(base + RVA_GET_GROUP, [mod], 5.0) == 0:
            raw = icall.read_mem(h, mb + 0x30, 8)
            g = struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else None
        if g:
            print("OWEndlessModule = %#x   GroupId=%s GroupLevel=%s CurTop=%s"
                  % (mod, i32(h, g + 0x20), i32(h, g + 0x24), i32(h, g + 0x28)))
        else:
            print("OWEndlessModule = %#x   （get_Group 取不到，跳过校验）" % mod)

        # 目标卡片：优先用调用方传入的现场解析结果，其次 grab 记录，最后现场搜索
        cd = None
        meta = None
        if hit:
            _t, cd, meta = hit
            print("目标卡片由 setup 直接传入：cd=%#x meta=%#x ID=%s"
                  % (cd, meta, i32(h, meta + 0x20)))
        else:
            d = load()
            if d and d.get("pid") == pid:
                for c in d.get("cards", []):
                    if c.get("feat") in (OLD_FEATURE, NEW_FEATURE):
                        cd = c.get("cd")
                        break
            if cd:
                meta = call(h, base, mb, RVA_GET_META, cd)
                if meta:
                    print("目标卡片来自 grab 记录：cd=%#x meta=%#x ID=%s"
                          % (cd, meta, i32(h, meta + 0x20)))
                else:
                    cd = None
            if not cd:
                # 卡片一直是 109，别再按 108 找（FeatureType 是位图，不会变成 108）
                hit2 = _find_target_card(h, base, mb, OLD_FEATURE) \
                    or _find_target_card(h, base, mb, NEW_FEATURE)
                if not hit2:
                    print("✗ 找不到目标卡片（feature 109/108 都没匹配）—— 挑战面板开着吗？")
                    return 1
                _c, cd, meta = hit2
                print("目标卡片现场解析：this=%#x cd=%#x meta=%#x ID=%s"
                      % (_c, cd, meta, i32(h, meta + 0x20)))

        slot_va = rec["slot"] if rec else page + SLOT
        stub_va = page + CLICK_STUB_OFF
        blob = build_click_stub(slot_va, mb, meta, mod, base + RVA_GOTO_OW,
                                orig, base + RVA_DOCLICK + 16)
        print("\n捕获槽 %#x   信箱头 %#x（两者不能相同）" % (slot_va, mb))
        print("stub  %d 字节 → %#x" % (len(blob), stub_va))
        print("入口 %#x 将指向该 stub" % (base + RVA_DOCLICK))
        print("触发条件：卡片 ContainerData 的 ExcelMeta == %#x" % meta)
        if not go:
            print("\n（演练。确认后加 --yes）")
            return 0

        cur = icall.read_mem(h, stub_va, 32)
        if cur is None:
            print("✗ stub 槽不可读")
            return 1
        site = icall.read_mem(h, base + RVA_DOCLICK, 14)
        mine = bool(site and site[:2] == b"\xFF\x25"
                    and struct.unpack("<Q", site[6:])[0] == stub_va)
        if cur.strip(b"\x00") and not mine:
            print("✗ stub 槽被别的代码占着 [%s]，不敢覆盖" % cur.hex(" "))
            return 1
        if mine:
            print("（槽里是上一版自己的 stub，允许覆盖）")
        if not icall.write_mem(h, stub_va, blob):
            print("✗ stub 写入失败")
            return 1
        back = icall.read_mem(h, stub_va, len(blob))
        if back != blob:
            print("✗ stub 落地自检失败")
            return 1
        # 清掉信箱头（上一版 stub 可能把捕获指针写到这里过）
        icall.write_mem(h, mb, b"\x00" * 0x38)
        ent = b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", stub_va)
        if not icall.write_mem(h, base + RVA_DOCLICK, ent):
            print("✗ 入口写入失败")
            return 1
        if icall.read_mem(h, base + RVA_DOCLICK, 14) != ent:
            print("✗ 入口自检失败")
            return 1

        # 让 icall 的钩子记录指向新 stub，这样 unhook 仍能正确还原
        st["hooks"][str(RVA_DOCLICK)] = {"slot": rec["slot"] if rec else page + CAPTURE_STUB,
                                         "stub": stub_va, "len": 16,
                                         "orig": orig.hex()}
        icall.save_state(st)
        print("\n✓ 点击接线已装。回游戏点那张卡（挑战页第 3 张），应当进入迪拉克之海。")
        print("  撤销：python wmpick.py clickoff")
        return 0
    finally:
        icall.k32.CloseHandle(h)


def cmd_clickoff():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if not st or st.get("pid") != pid:
            print("信箱未装")
            return 1
        rec = _hook_rec()
        orig = bytes.fromhex(rec["orig"]) if rec else icall.file_bytes(RVA_DOCLICK, 16)
        ok = icall.write_mem(h, base + RVA_DOCLICK, orig)
        print("入口还原 %s" % ("成功" if ok else "失败"))
        if rec:
            st["hooks"][str(RVA_DOCLICK)] = {"slot": rec["slot"],
                                             "stub": st["page"] + CAPTURE_STUB,
                                             "len": 16, "orig": rec["orig"]}
            icall.save_state(st)
            print("（捕获钩子记录已指回 %#x，需要的话再跑 arm 重挂）" % (st["page"] + CAPTURE_STUB))
        return 0
    finally:
        icall.k32.CloseHandle(h)


def cmd_status():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        d = load()
        print("pid=%d base=%#x" % (pid, base))
        cur = icall.read_mem(h, base + RVA_DOCLICK, 15)
        print("DoClickAction 入口: %s"
              % ("已挂钩" if cur and cur[:2] == b"\xFF\x25" else "原始"))
        if st and st.get("pid") == pid:
            raw = icall.read_mem(h, st["page"] + SLOT, 8)
            v = struct.unpack("<Q", raw)[0] if raw else 0
            print("捕获槽: %s" % (("%#x" % v) if v else "空"))
        if d and d.get("pid") == pid:
            print("上次 grab: this=%#x cd=%#x feature=%s"
                  % (d.get("this", 0), d.get("cd", 0), d.get("feature")))
        return 0
    finally:
        icall.k32.CloseHandle(h)


def main():
    a = sys.argv[1:] or ["status"]
    cmd = a[0].lower()
    if cmd == "arm":
        return cmd_arm()
    if cmd == "grab":
        return cmd_grab()
    if cmd == "ring":
        return cmd_ring()
    if cmd == "dump":
        return cmd_dump()
    if cmd == "ringoff":
        return cmd_ringoff()
    if cmd == "mgrarm":
        return cmd_mgrarm()
    if cmd == "mgrdump":
        return cmd_mgrdump()
    if cmd == "mgroff":
        return cmd_mgroff()
    if cmd == "tabs":
        return cmd_tabs()
    if cmd == "retarget":
        return cmd_retarget()
    if cmd == "ftpatch":
        return cmd_ftpatch()
    if cmd == "unlock":
        return cmd_unlock()
    if cmd == "unlockoff":
        return cmd_unlockoff()
    if cmd == "restore":
        return cmd_restore()
    if cmd == "patch":
        return cmd_patch()
    if cmd == "click":
        return cmd_click()
    if cmd == "clickoff":
        return cmd_clickoff()
    if cmd == "setup":
        return cmd_setup()
    if cmd == "off":
        return cmd_off()
    if cmd == "status":
        return cmd_status()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
