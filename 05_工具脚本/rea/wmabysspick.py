# -*- coding: utf-8 -*-
"""wmabysspick —— 世界地图卡片点击重定向到「无限深渊」（Infinity Abyss / EndlessTypeNormal）

和原版的关系
------------
原版链路（本文件**不修改**它们，只 import 复用）：
    rehook.bat → wmpick.py status/arm/mgrarm → wmready.py → wmpick.py setup
    cmd_setup 做两处运行时改动：解锁补丁（LJMINEONAFF 里 2 当 3）
    和点击接线（DoClickAction 入口 stub → 信箱 → 下一帧 GoToOWEndless）。

为什么原版落到迪拉克
--------------------
GoToOWEndless（RVA 0x19C5E00）不带模式参数，它走：

    this_00 = module->_TwoEndless            ; [module+0x58]
    mode    = TwoEndless::GetActiveMode(this_00)   ; RVA 0x3758440
    type    = ModeToType(module, mode)             ; RVA 0x19C6410
    Send(GetOpenworldEndlessDataReq)               ; type 字段 = ModeToType 结果

ModeToType 的跳表（实测 0x1819C6410，7 个分支）：
    mode 0 -> 0      mode 1 -> 0      mode 2 -> 2
    mode 3 -> 3      mode 4 -> 0      mode 5 -> 5      mode 6 -> 6

**注意 mode 1 = EndlessMode.Normal 也映射成 0** —— 也就是说在 7.0 的
协议上，「无限深渊」在 wire 上就是 **type 0**（不是 1）。这一点被三处代码
反复证实，是这套接线能成立的全部依据：

  1) ModeToType(Normal) = 0
  2) EndlessBaseData.Refresh(RVA 0x1607E70) 先做
         TypeToMode(rsp.type)  (RVA 0x19C6C90：2->2 3->3 4->4 5->5 6->6，其余->0)
     再和 this.Mode 比；所以只有 rsp.type=0 才能刷新 Mode=None(0) 那条 base data
  3) OnGetOWEndlessRspForGotoEndless（RVA 0x19C64E0）读当前模式对象的
     endless_type（EndlessStatus+0x10），分支只有 0 / 5 / 6：
         case 0:  PreActivity.get_Status() == 2 ? 显示 OWEndlessStubPageContext
                                                : 显示 EndlessPreActivityPageContext
         case 5:  → GoToUltraEndless（贪婪那条）
         case 6:  → 0x1819C6B20（前哨那条）

     case 0 的 EndlessPreActivityPageContext 就是无限深渊页面本体
     （0x180877130 构造；字段：_floorText/_scoreText/_groupLevelNameText/
      _groupLevelRangeText/_monsterScroller/_goEndlessBtn/_resetFloorBtn/
      _shopBtn/_scheduleBtn/_endlessRewardBtn ...），不是超弦、也不是迪拉克。

所以这个文件做的事只有两件：
  * stub 里把 _currentMode.endless_type 摆成 0（而不是 3）
  * 照旧投递 GoToOWEndless（用它而不是 UIUtil.GoToEndless，是为了让
    rcx=module 这个参数语义和其它版本完全一致 —— 后者是无参静态方法，
    RVA 0x3029200，内部只是判 InUltraEndlessMode 再尾跳 GoToOWEndless）

服务端配合（必须）
------------------
服务端 GetOpenworldEndlessDataReqHandler 原来把 req.Type==None 当成
Openworld 处理，并且把 **响应里的 type 也改写成 2**，于是：
    客户端发 0 → 服务端回 2 → TypeToMode(2)=2 → 刷新的是 Mode=2 的 base data
    → case 0 拿到的无限深渊页没有任何数据（甚至走不到 case 0，取决于当前模式）
本仓库已同步改过（见 docs/无限深渊_接入说明.md）：请求 0 时查表仍走迪拉克
（Type=2，复用 OWEndless 系列表），但响应 type 原样回 0。

⚠ 两个版本共用 DoClickAction 一个入口，谁后装谁生效，不能同时挂两张卡。
⚠ stub 把 _currentMode 留在 0，不还原的话 rehook.bat / rehook_qt.bat 的点击
   也会带着 0 出去（服务端若没改就是迪拉克数据 + 无限深渊页的错配）。
   回迪拉克版：python wmabysspick.py off     （撤接线 + 写回 2）

用法
----
    python wmabysspick.py arm            装信箱 + 挂钩（等同 wmpick.py arm）
    python wmabysspick.py ready [sec]    等挑战面板装配，然后 setup --yes
    python wmabysspick.py setup --yes    面板已开：立刻装（解锁补丁 + 无限深渊接线）
    python wmabysspick.py status         接线/模式/卡 一眼看全
    python wmabysspick.py mode           读当前 _currentMode.endless_type
    python wmabysspick.py mode 0         只改模式，不碰接线（做对照实验用）
    python wmabysspick.py restore-mode   写回 2（迪拉克）
    python wmabysspick.py patchmode      装 TypeToMode 补丁（type 0 -> mode 2）
    python wmabysspick.py unpatchmode    还原 TypeToMode
    python wmabysspick.py off            撤点击接线 + 还原模式 + 还原 TypeToMode

安全：arm / status / mode(读) 只读；setup 写四处 ——
      解锁补丁 5 字节、TypeToMode 18 字节、自建 stub 区、
      EndlessStatus.endless_type 4 字节。
      都不碰 ExcelMeta，也不改任何配置行。
      TypeToMode 改动前会挂起其它线程（livepatch.py），避免半截指令。
"""
import os
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall       # noqa: E402
import livepatch   # noqa: E402
import wmpick as W  # noqa: E402  只读复用：常量/搜索/补丁/撤钩

# ---- RVA / 偏移 ----
RVA_GOTO_OW = W.RVA_GOTO_OW   # 0x19C5E00  OWEndlessModule.GoToOWEndless
RVA_GOTO_ENDLESS = 0x3029200  # UIUtil.GoToEndless  —— 仅用于日志对照，不投递
RVA_GET_MODULE = W.RVA_GET_MODULE  # 0x1A92080  get_module（rcx 传 0 即可）

OFF_TWO      = 0x58   # OWEndlessModule._TwoEndless  (layout6.tsv: 37632 @ 88)
OFF_CURRENT  = 0x10   # TwoEndless._currentMode     (layout6.tsv: 37678 @ 16)
OFF_STATUS_TYPE = 0x10  # proto.EndlessStatus.endless_type (layout6.tsv: 9927 @ 16)

TYPE_DIRAC = 2
TYPE_QT = 3
# 无限深渊在 7.0 wire 上就是 0（= EndlessType.None 这个枚举值，
# 但语义是「普通/无限深渊」，不是「没有」）。见文件头 2) 3) 两条证据。
TYPE_ABYSS = 0

# --------------------------------------------------------------------------
# TypeToMode 补丁：让 type 0 走 mode 2 的 base data
#
# 为什么必须补这一刀
# ------------------
# _currentMode.endless_type = 0 时：
#     GetActiveMode() = TypeToMode(0) = 0 (EndlessMode.None)
#     GetCurrentEndlessData() = _baseDataList.Find(Mode == 0) = null
# 而 OWEndlessModule 构造函数（RVA 0x189D370）只硬编码了两条 base data：
#     baseDataList.Add(new EndlessBaseData(2));   // OWE 迪拉克
#     baseDataList.Add(new EndlessBaseData(3));   // QTE 量子
# 于是 MonoOWEndlessUIManager.SetupView（RVA 0x185AF00）第一句
# GetCurrentEndlessData() 就拿到 null，直接 NullReferenceException ——
# 表现就是点完卡以后黑屏转圈，output_log.txt 每帧刷一条
# "MonoOWEndlessUIManager.SetupView" 的 NRE。
#
# 补丁把 TypeToMode(0) 从 0 改成 2：
#     * type 0 的 rsp 会命中 Mode=2 那条 base data（EndlessBaseData.Refresh
#       RVA 0x1607E70 就是拿 TypeToMode(rsp.type) 和 this.Mode 比的），
#       于是 Schedule / Group / BattleLevelInfo 都会被填上；
#     * 服务端 OwGroupLevel=21 在 OWEndlessGroup 表里正好属于 mode 2，
#       RefreshPlayerGroup 的 (level, mode) 查表也能命中；
#     * 出站请求仍然带 type 0（那是 ModeToType 的事，没动）。
#
# 语义边界：只改 0，不动 1。type 1（EndlessTypeNormal 这个枚举里的 Normal）
# 从来没在 wire 上出现过，保持它原来的 0，避免别的入口（世界地图条目）误判。
#
# 入口前 15 字节是固定前导，补丁占 18 字节，可以整段盖掉（后面全是死代码）。
# --------------------------------------------------------------------------
RVA_TYPETOMODE = 0x19C6C90
TYPETOMODE_LEN = 18
# 48 89 5c 24 08 57 48 83 ec 20 48 8b f9 8b da  前导
TYPETOMODE_PROLOGUE = bytes.fromhex("48895c2408574883ec20488bf98bda")
# 8b c2             mov eax, edx
# 83 f8 02          cmp eax, 2
# 73 0a             jae  ret        ; 2..6 原样返回
# 83 f8 01          cmp eax, 1
# 74 05             je   ret        ; 1 保持 0（不参与映射）
# b8 02 00 00 00    mov eax, 2     ; 0 -> 2
# c3                ret
TYPETOMODE_NEW = bytes.fromhex("8bc283f802730a83f8017405b802000000c3")


def q(h, va):
    return W.q(h, va)


def i32(h, va):
    return W.i32(h, va)


def _chain(h, base):
    """module → TwoEndless → _currentMode(EndlessStatus)。任一环缺失返回 None。"""
    mod = W._resolve_module(h, base)
    if not mod:
        return mod, None, None
    two = q(h, mod + OFF_TWO)
    if not two:
        return mod, None, None
    return mod, two, q(h, two + OFF_CURRENT)


# --------------------------------------------------------------------------
# 点击接线 stub
#
# 和 wmqtpick.build_qt_stub 只差一个立即数（3 → 0）：
#   wmqtpick：命中卡 → 写 endless_type=3 → 投递 GoToOWEndless
#   这个版：  命中卡 → 写 endless_type=0 → 投递 GoToOWEndless
#
# 手写机器码的约束（wmpick 里踩过的坑，照抄结论）：
#   * 只用 r10/r11/rax —— 全是调用者保存，函数入口处不承载有效值；
#     rcx 必须原样保留（原始前导 `mov rdi,rdx` / `mov rbx,rcx` 还要用）。
#   * 捕获槽 page+0x40 与信箱头 page+0x00 是两个地址，不能混用；
#     信箱头保持 pending 最后写，避免半截命令被执行。
#   * jz/jne 全是 rel8，整段必须压在 127 字节内（build 里有 assert）。
# --------------------------------------------------------------------------
def build_abyss_stub(slot_va, mb_va, meta_va, module_va, goto_va, orig, resume_va,
                     force_type=TYPE_ABYSS):
    b = bytearray()
    b += b"\x49\xBB" + struct.pack("<Q", slot_va)        # mov r11, slot（捕获槽）
    b += b"\x49\x89\x0B"                                 # mov [r11], rcx
    b += b"\x4C\x8B\x91\xC8\x00\x00\x00"                 # mov r10, [rcx+0xC8]
    jmps = []
    b += b"\x4D\x85\xD2"                                 # test r10, r10
    jmps.append(len(b)); b += b"\x74\x00"                # jz replay
    b += b"\x4D\x8B\x52\x18"                             # mov r10, [r10+0x18]  meta
    b += b"\x48\xB8" + struct.pack("<Q", meta_va)        # mov rax, meta_va
    b += b"\x49\x39\xC2"                                 # cmp r10, rax
    jmps.append(len(b)); b += b"\x75\x00"                # jne replay

    # --- 无限深渊：把 _currentMode.endless_type 摆成 0 ---
    # 指针现取：TwoEndless 与 EndlessStatus 都可能被 Refresh 换掉，
    # 用 setup 时的快照写会打到已回收的堆上。
    b += b"\x48\xB8" + struct.pack("<Q", module_va)      # mov rax, module
    b += b"\x48\x8B\x40" + bytes([OFF_TWO])              # mov rax, [rax+0x58]
    skips = []
    b += b"\x48\x85\xC0"                                 # test rax, rax
    skips.append(len(b)); b += b"\x74\x00"               # jz skipw
    b += b"\x48\x8B\x40" + bytes([OFF_CURRENT])          # mov rax, [rax+0x10]
    b += b"\x48\x85\xC0"                                 # test rax, rax
    skips.append(len(b)); b += b"\x74\x00"               # jz skipw
    b += b"\xC7\x40" + bytes([OFF_STATUS_TYPE]) + struct.pack("<I", force_type)

    skipw = len(b)
    for p in skips:
        rel = skipw - (p + 2)
        assert 0 <= rel <= 127, (p, rel)
        b[p + 1] = rel

    # --- 投递信箱命令（和 wmpick 完全一致，别动顺序） ---
    b += b"\x49\xBB" + struct.pack("<Q", mb_va)          # mov r11, mb
    b += b"\x45\x31\xD2"                                 # xor r10d, r10d
    for off in (0x10, 0x18, 0x20, 0x28, 0x30):
        b += b"\x4D\x89\x53" + bytes([off])              # mov [r11+off], r10
    b += b"\x48\xB8" + struct.pack("<Q", module_va)      # mov rax, module
    b += b"\x49\x89\x43\x10"                             # mov [r11+0x10], rax  arg0
    b += b"\x48\xB8" + struct.pack("<Q", goto_va)        # mov rax, GoToOWEndless
    b += b"\x49\x89\x43\x08"                             # mov [r11+8], rax     target
    b += b"\x41\xC6\x43\x01\x00"                         # mov byte [r11+1], 0  done=0
    b += b"\x41\xC6\x03" + bytes([icall.MAGIC])          # mov byte [r11], 0xA5 pending

    replay = len(b)
    for p in jmps:
        rel = replay - (p + 2)
        assert 0 <= rel <= 127, (p, rel)
        b[p + 1] = rel
    b += orig
    b += b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", resume_va)
    return bytes(b)


# --------------------------------------------------------------------------
# TypeToMode 补丁的安装 / 还原
# --------------------------------------------------------------------------
def _ttm_orig_bytes():
    """DLL 文件里的原始 18 字节 —— 还原的唯一权威来源。"""
    b = icall.file_bytes(RVA_TYPETOMODE, TYPETOMODE_LEN)
    if not b or len(b) != TYPETOMODE_LEN:
        return None
    return b


def cmd_patchmode(on=True):
    """on=True 装补丁（type 0 → mode 2），on=False 还原。

    写之前先挂起进程里其它线程 —— TypeToMode 每帧都在被调用，
    裸写 18 字节有取到半截指令的风险（见 livepatch.py 的文件头）。
    """
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        va = base + RVA_TYPETOMODE
        orig = _ttm_orig_bytes()
        if not orig or orig[:len(TYPETOMODE_PROLOGUE)] != TYPETOMODE_PROLOGUE:
            print("✗ DLL 文件里 RVA %#x 的字节不是预期前导：%s"
                  % (RVA_TYPETOMODE, orig.hex(" ") if orig else "读取失败"))
            print("  DLL 版本对不上就别改，先确认这是 7.0 的 UserAssembly.dll")
            return 1

        cur = icall.read_mem(h, va, TYPETOMODE_LEN)
        if cur is None:
            print("✗ 读取 %#x 失败" % va)
            return 1
        patched = cur == TYPETOMODE_NEW

        if not on:
            if not patched:
                if cur == orig:
                    print("· TypeToMode 本来就没打补丁，无需还原")
                    return 0
                print("✗ %#x 当前字节既不是补丁也不是原值：%s" % (va, cur.hex(" ")))
                print("  拒绝改写（可能是别的工具改过，先重启客户端）")
                return 1
            ok, n = livepatch.write_code(h, pid, va, orig, icall.write_mem)
            back = icall.read_mem(h, va, TYPETOMODE_LEN)
            if not ok or back != orig:
                print("✗ 还原失败 [%s]" % (back.hex(" ") if back else "读取失败"))
                return 1
            print("✓ TypeToMode 已还原成原始字节（挂起 %d 个线程后写入）" % n)
            return 0

        if patched:
            print("✓ TypeToMode 补丁已经就位（type 0 → mode 2）")
            return 0
        if cur != orig:
            print("✗ %#x 当前字节既不是原始值也不是本补丁：%s" % (va, cur.hex(" ")))
            print("  拒绝改写（可能是别的工具改过，先重启客户端）")
            return 1

        ok, n = livepatch.write_code(h, pid, va, TYPETOMODE_NEW, icall.write_mem)
        back = icall.read_mem(h, va, TYPETOMODE_LEN)
        if not ok or back != TYPETOMODE_NEW:
            print("✗ 写入失败 [%s]" % (back.hex(" ") if back else "读取失败"))
            return 1
        print("✓ TypeToMode 补丁已写入 %#x（挂起 %d 个线程后写入）" % (va, n))
        print("  type 0（无限深渊）→ mode 2：SetupView 能拿到 Mode=2 的 base data")
        print("  type 1 与 2..6 语义不变；还原：python wmabysspick.py unpatchmode")
        return 0
    finally:
        icall.k32.CloseHandle(h)


def _patchmode_state(h, base):
    """给 status / state 用：返回 'on' / 'off' / '??'。"""
    cur = icall.read_mem(h, base + RVA_TYPETOMODE, TYPETOMODE_LEN)
    if cur is None:
        return "??"
    if cur == TYPETOMODE_NEW:
        return "on"
    if cur == _ttm_orig_bytes():
        return "off"
    return "??"


# --------------------------------------------------------------------------
# 模式读写（不进 stub，手动对照用）
# --------------------------------------------------------------------------
def cmd_mode(arg=None):
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        mod, two, status = _chain(h, base)
        if not mod:
            print("✗ 取不到 OWEndlessModule 实例（游戏还没进过主界面？）")
            return 1
        if not two:
            print("✗ module+0x58 是空的：TwoEndless 还没建")
            print("  → 先在游戏里打开一次「世界地图 → 挑战」，让 3433 回来")
            return 1
        if not status:
            print("✗ TwoEndless+0x10 是空的：_currentMode 还没被 Refresh 填过")
            print("  → 同上，先开一次挑战面板")
            return 1

        cur = i32(h, status + OFF_STATUS_TYPE)
        print("module=%#x  TwoEndless=%#x  _currentMode=%#x  endless_type=%s"
              % (mod, two, status, cur))
        if arg is None:
            print("  生效类型 = %s（GoToOWEndless 会按它发 3419）" % _type_name(cur))
            return 0

        try:
            want = int(arg, 0)
        except ValueError:
            print("✗ 模式必须是数字：0 无限深渊 / 2 迪拉克 / 3 量子")
            return 1
        if want not in (TYPE_ABYSS, TYPE_DIRAC, TYPE_QT):
            print("⚠ %d 不在已知可用集合 {0,2,3} 里，仍按你要求写入" % want)
        if not icall.write_mem(h, status + OFF_STATUS_TYPE, struct.pack("<I", want)):
            print("✗ 写入失败")
            return 1
        now = i32(h, status + OFF_STATUS_TYPE)
        print("  写入 %d → 当前 %s  %s" % (want, now, "✓" if now == want else "✗"))
        print("  GoToOWEndless 下次点击就会按这个类型发 3419")
        return 0 if now == want else 1
    finally:
        icall.k32.CloseHandle(h)


def _type_name(t):
    if t is None:
        return "?"
    return {
        0: "0 无限深渊（wire 值 0）",
        1: "1 Normal（未在 wire 上出现）",
        2: "2 迪拉克之海",
        3: "3 量子奇点",
        4: "4 超弦空间",
        5: "5 贪婪深渊",
        6: "6 前哨无尽",
    }.get(t, "%d 未知" % t)


# --------------------------------------------------------------------------
# 装接线
# --------------------------------------------------------------------------
def _install_abyss_click(h, base, mb, page, hit):
    """把 DoClickAction 接到「无限深渊 stub」。hit=(this, cd, meta) 由 setup 现场解析。"""
    go = "--yes" in sys.argv
    st = icall.load_state()
    rec = W._hook_rec()

    if rec:
        orig = bytes.fromhex(rec["orig"])
        print("被覆盖的原始字节取自钩子记录（%d 字节）" % len(orig))
    else:
        orig = icall.file_bytes(W.RVA_DOCLICK, 16)
        print("被覆盖的原始字节取自 DLL 文件（%d 字节）" % len(orig))
    if not orig or len(orig) < 16:
        print("✗ 原始字节取不到，放弃")
        return 1

    mod, two, status = _chain(h, base)
    if not mod:
        print("✗ 取不到 OWEndlessModule 实例")
        return 1
    if not status:
        print("⚠ TwoEndless/_currentMode 还取不到 —— 接线照装，但点击时")
        print("  stub 会跳过写入，GoToOWEndless 只能按当时的类型走（多半仍是迪拉克）。")
        print("  正确顺序：arm → 开挑战面板 → 再 setup。")
    else:
        print("module=%#x  TwoEndless=%#x  _currentMode=%#x  当前 endless_type=%s"
              % (mod, two, status, _type_name(i32(h, status + OFF_STATUS_TYPE))))

    this, cd, meta = hit
    print("目标卡片 this=%#x cd=%#x meta=%#x meta.ID=%s"
          % (this, cd, meta, i32(h, meta + 0x20)))

    slot_va = rec["slot"] if rec else page + W.SLOT
    stub_va = page + W.CLICK_STUB_OFF
    blob = build_abyss_stub(slot_va, mb, meta, mod, base + RVA_GOTO_OW,
                            orig, base + W.RVA_DOCLICK + 16, TYPE_ABYSS)
    print("\n捕获槽 %#x   信箱头 %#x（两者不能相同）" % (slot_va, mb))
    print("stub  %d 字节 → %#x（里面带 endless_type=0）" % (len(blob), stub_va))
    print("入口 %#x 将指向该 stub" % (base + W.RVA_DOCLICK))
    print("触发条件：卡片 ContainerData 的 ExcelMeta == %#x" % meta)
    if not go:
        print("\n（演练。确认后加 --yes）")
        return 0

    cur = icall.read_mem(h, stub_va, 32)
    if cur is None:
        print("✗ stub 槽不可读")
        return 1
    site = icall.read_mem(h, base + W.RVA_DOCLICK, 14)
    mine = bool(site and site[:2] == b"\xFF\x25"
                and struct.unpack("<Q", site[6:])[0] == stub_va)
    if cur.strip(b"\x00") and not mine:
        print("✗ stub 槽被别的代码占着 [%s]，不敢覆盖" % cur.hex(" "))
        return 1
    if mine:
        print("（槽里是上一版接线，允许覆盖）")
    if not icall.write_mem(h, stub_va, blob):
        print("✗ stub 写入失败")
        return 1
    if icall.read_mem(h, stub_va, len(blob)) != blob:
        print("✗ stub 落地自检失败")
        return 1
    icall.write_mem(h, mb, b"\x00" * 0x38)
    ent = b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", stub_va)
    if not icall.write_mem(h, base + W.RVA_DOCLICK, ent):
        print("✗ 入口写入失败")
        return 1
    if icall.read_mem(h, base + W.RVA_DOCLICK, 14) != ent:
        print("✗ 入口自检失败")
        return 1

    st.setdefault("hooks", {})[str(W.RVA_DOCLICK)] = {
        "slot": rec["slot"] if rec else page + W.CAPTURE_STUB,
        "stub": stub_va, "len": 16, "orig": orig.hex(),
    }
    icall.save_state(st)
    print("\n✓ 无限深渊点击接线已装。回游戏点那张卡，应当进入无限深渊（无线上的 type=0）。")
    print("  回迪拉克版：python wmabysspick.py off  然后 rehook.bat force")
    return 0


def _ensure_mailbox(pid):
    """确保信箱属于当前进程；缺失/属于旧进程时自动重装。

    为什么需要：wmpick.py status 即使信箱没装也会打印 `pid=<当前pid>`，
    批处理拿它做 findstr 判断会永远“已装”，于是跳过 arm，后面 setup 才报
    “信箱未装/失效”。这里把判断收回到 python 里，直接比状态文件里的 pid。
    """
    st = icall.load_state()
    if st and st.get("pid") == pid:
        return st
    old = st.get("pid") if st else None
    print("信箱未安装或属于旧进程（state pid=%s，当前 pid=%d），自动装信箱…"
          % (old if old is not None else "无", pid))
    W.cmd_arm()
    st = icall.load_state()
    if not st or st.get("pid") != pid:
        print("✗ 自动装信箱失败，先手动跑：python wmpick.py arm")
        return None
    print("（信箱已重装：如果挑战面板已经开着，请关掉再打开一次）")
    return st


def cmd_state():
    """给批处理用的 ASCII 探针：STATE ok / STATE stale。"""
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        if st and st.get("pid") == pid:
            raw = icall.read_mem(h, st["page"] + W.MGR_SLOT, 8)
            mgr = struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else 0
            print("STATE ok pid=%d page=%#x mailbox=%#x mgr=%#x ttm=%s"
                  % (pid, st.get("page", 0), st.get("mailbox", 0), mgr,
                     _patchmode_state(h, base)))
            return 0
        print("STATE stale state_pid=%s cur_pid=%d"
              % (st.get("pid") if st else "none", pid))
        return 2
    finally:
        icall.k32.CloseHandle(h)


def cmd_setup():
    """解锁补丁 + 无限深渊点击接线（顺序与 wmpick.cmd_setup 一致）。"""
    go = "--yes" in sys.argv
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = _ensure_mailbox(pid)
        if not st:
            return 1
        mb = st["mailbox"]

        hit = W._find_target_card(h, base, mb, W.OLD_FEATURE)
        if not hit:
            hit = W._find_target_card(h, base, mb, W.NEW_FEATURE)
        if not hit:
            print("✗ 三个页签里都没找到目标卡片 —— 挑战面板开着吗？管理器实例抓到了吗？")
            print("  先在游戏里关掉挑战面板再打开，然后重跑本命令。")
            return 1

        uva = base + W.RVA_UNLOCK
        ucur = icall.read_mem(h, uva, 5)
        need_unlock = ucur != W.PATCH_NEW
        print("目标卡片 this=%#x cd=%#x meta=%#x meta.ID=%s"
              % (hit[0], hit[1], hit[2], i32(h, hit[2] + 0x20)))
        print("\n计划：")
        print("  %s 解锁补丁    %s -> %s   @ %#x"
              % ("·" if need_unlock else "✓已就位",
                 ucur.hex(" ") if ucur else "?", W.PATCH_NEW.hex(" "), uva))
        print("  %s TypeToMode 补丁 %s   @ %#x"
              % ("✓已就位" if _patchmode_state(h, base) == "on" else "·",
                 "type 0 -> mode 2", base + RVA_TYPETOMODE))
        print("  · 无限深渊点击接线（stub 里带 endless_type=0）")
        if not go:
            print("\n（演练。确认后加 --yes）")
            return 0

        print("\n--- TypeToMode 补丁（type 0 -> mode 2）---")
        if cmd_patchmode(True) != 0:
            return 1

        if need_unlock:
            if not ucur or ucur[:5] != W.PATCH_OLD:
                print("✗ 解锁补丁位置字节不是预期值 %s，拒绝改写" % W.PATCH_OLD.hex(" "))
                return 1
            W._revert_old_status2(h, base)
            icall.write_mem(h, uva, W.PATCH_NEW)
            back = icall.read_mem(h, uva, 5)
            print("解锁补丁写入 %s" % ("成功" if back == W.PATCH_NEW else "失败"))
            if back != W.PATCH_NEW:
                return 1

        print("\n--- 安装无限深渊点击接线 ---")
        return _install_abyss_click(h, base, mb, st["page"], hit)
    finally:
        icall.k32.CloseHandle(h)


def wait_panel(timeout=120.0):
    """硬门禁只有一条：挑战面板装配完成（MGR_SLOT 非 0）。"""
    deadline = time.time() + timeout
    note = ""
    ensured = False
    while time.time() < deadline:
        h, pid, base = icall.open_game()
        if not h:
            print("\n✗ 找不到游戏进程")
            return None
        try:
            st = icall.load_state()
            if not st or st.get("pid") != pid:
                icall.k32.CloseHandle(h)
                if not ensured:
                    ensured = True
                    st = _ensure_mailbox(pid)
                    if not st:
                        return None
                    continue
                print("\n✗ 信箱与当前进程不匹配，先跑 python wmpick.py arm")
                return None
            raw = icall.read_mem(h, st["page"] + W.MGR_SLOT, 8)
            mgr = struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else 0
        finally:
            try:
                icall.k32.CloseHandle(h)
            except Exception:
                pass
        if mgr:
            print("\n✓ 挑战面板已装配（管理器 %#x）" % mgr)
            return mgr
        if note != "wait":
            sys.stdout.write("\n  … 等待挑战面板装配（游戏里打开「世界地图 → 挑战」）")
            sys.stdout.flush()
            note = "wait"
        else:
            sys.stdout.write(".")
            sys.stdout.flush()
        time.sleep(1.0)
    print("\n✗ 超时（%.0fs）：挑战面板一直没装配" % timeout)
    return None


def cmd_ready(timeout=120.0):
    if not wait_panel(timeout):
        return 1
    if "--yes" not in sys.argv:
        sys.argv.append("--yes")
    time.sleep(0.3)
    return cmd_setup()


def cmd_off():
    print("--- 还原 TypeToMode ---")
    rc0 = cmd_patchmode(False)
    print()
    rc = W.cmd_clickoff()
    print()
    print("--- 还原 _currentMode.endless_type ---")
    rc2 = cmd_mode(str(TYPE_DIRAC))
    return rc0 or rc or rc2


def cmd_status():
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        st = icall.load_state()
        print("pid=%d base=%#x" % (pid, base))
        cur = icall.read_mem(h, base + W.RVA_DOCLICK, 15)
        hooked = bool(cur and cur[:2] == b"\xFF\x25")
        tgt = struct.unpack("<Q", cur[6:14])[0] if hooked else 0
        print("DoClickAction 入口: %s"
              % ("已挂钩 → %#x" % tgt if hooked else "原始"))

        kind = "?"
        if hooked:
            stub = icall.read_mem(h, tgt, 160) or b""
            if b"\xC7\x40\x10\x00\x00\x00\x00" in stub:
                kind = "无限深渊版（stub 内写 endless_type=0）"
            elif b"\xC7\x40\x10\x03\x00\x00\x00" in stub:
                kind = "量子版（stub 内写 endless_type=3）"
            elif tgt == (st.get("page", 0) + W.CLICK_STUB_OFF if st else 0):
                kind = "迪拉克版（原 wmpick 接线）"
            elif tgt == (st.get("page", 0) + W.CAPTURE_STUB if st else 0):
                kind = "仅捕获（arm 状态，还没 setup）"
        print("接线版本: %s" % kind)
        print("TypeToMode 补丁: %s"
              % {"on": "已装（type 0 -> mode 2）",
                 "off": "原始（type 0 -> 0，SetupView 会 NRE）",
                 "??": "未知 / 被别的工具改过"}[_patchmode_state(h, base)])

        mod, two, status = _chain(h, base)
        if status:
            print("module=%#x  TwoEndless=%#x  _currentMode=%#x" % (mod, two, status))
            print("当前 endless_type = %s → GoToOWEndless 会发这一套"
                  % _type_name(i32(h, status + OFF_STATUS_TYPE)))
        elif two:
            print("module=%#x  TwoEndless=%#x  _currentMode=<空>" % (mod, two))
        elif mod:
            print("module=%#x  TwoEndless=<空>" % mod)
        else:
            print("OWEndlessModule = 取不到")
        return 0
    finally:
        icall.k32.CloseHandle(h)


def main():
    a = sys.argv[1:] or ["status"]
    cmd = a[0].lower()
    if cmd == "arm":
        return W.cmd_arm()
    if cmd == "setup":
        return cmd_setup()
    if cmd == "ready":
        timeout = 120.0
        for x in a[1:]:
            try:
                timeout = float(x)
            except ValueError:
                pass
        return cmd_ready(timeout)
    if cmd == "mode":
        return cmd_mode(a[1] if len(a) > 1 else None)
    if cmd == "restore-mode":
        return cmd_mode(str(TYPE_DIRAC))
    if cmd == "off":
        return cmd_off()
    if cmd == "patchmode":
        return cmd_patchmode(True)
    if cmd == "unpatchmode":
        return cmd_patchmode(False)
    if cmd == "status":
        return cmd_status()
    if cmd == "state":
        return cmd_state()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
