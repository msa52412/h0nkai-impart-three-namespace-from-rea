# -*- coding: utf-8 -*-
"""wmqtpick —— 世界地图卡片点击重定向到「量子奇点」（EndlessType=3）

和原版的关系
------------
原版链路（本文件**不修改**它们，只 import 复用）：
    rehook.bat → wmpick.py status/arm/mgrarm → wmready.py → wmpick.py setup
    cmd_setup 做两处运行时改动：解锁补丁（LJMINEONAFF 里 2 当 3）
    和点击接线（DoClickAction 入口 stub → 信箱 → 下一帧 GoToOWEndless）。

为什么原版落到迪拉克
--------------------
GoToOWEndless（RVA 0x19C5E00，反汇编 0x183720xxx 段）本身**不带模式参数**：

    this_00 = module->_TwoEndless            ; [module+0x58]
    mode    = TwoEndless::GetActiveMode(this_00)
    type    = ModeToType(module, mode)
    req.<type 字段> = type
    Send(GetOpenworldEndlessDataReq)          ; 0xD5B = 3419

而 GetActiveMode（RVA 0x3758440）尾巴上是：

    mov rax, [rdi + 0x10]      ; TwoEndless._currentMode (proto.EndlessStatus)
    mov edx, [rax + 0x10]      ; EndlessStatus.endless_type
    jmp ModeToType             ; 2→2 3→3 5→5 6→6 其余→0

_currentMode 由 TwoEndless.Refresh（RVA 0x3758710）直接取
GetEndlessStatusRsp.cur_status。服务端 AbyssConfig 默认 SelectedEndlessType=2，
CurStatus.EndlessType=Openworld，所以这张卡永远走迪拉克那条路。

量子版做的唯一一件事
--------------------
在点击接线的 stub 里、dispatch GoToOWEndless **之前**插一段：

    rax = [module + 0x58]      ; TwoEndless
    rax = [rax + 0x10]         ; _currentMode
    if (rax) [rax + 0x10] = 3  ; endless_type = Quantum

指针是**每次点击时现取**的，不存快照 —— 面板重开、3433 刷新换掉
EndlessStatus 对象之后也不会往已回收的堆地址写。
之后 GoToOWEndless 发出的就是 type=3 的 3419，客户端走 QTInLevelData 那条路
（它只认 rsp.type==3，且要求 rsp.quantum_endless 非空，服务端两条都已满足）。

⚠ 两个版本共用 DoClickAction 一个入口，谁后装谁生效，不能同时挂两张卡。
⚠ stub 把 _currentMode 留在 3，不还原的话原版 rehook.bat 也会跳到量子。
   回迪拉克版：python wmqtpick.py off     （撤接线 + 写回 2）
   只还原模式：python wmqtpick.py restore-mode

用法
----
    python wmqtpick.py arm              装信箱 + 挂钩（等同 wmpick.py arm）
    python wmqtpick.py ready [sec]      等挑战面板装配，然后 setup --yes
    python wmqtpick.py setup --yes      面板已开：立刻装（解锁补丁 + 量子点击接线）
    python wmqtpick.py status           接线/模式/卡 一眼看全
    python wmqtpick.py mode             读当前 _currentMode.endless_type
    python wmqtpick.py mode 3           只改模式，不碰接线（做对照实验用）
    python wmqtpick.py restore-mode     写回 2（迪拉克）
    python wmqtpick.py off              撤点击接线 + 还原模式

安全：arm / status / mode(读) 只读；setup 写三处 ——
      解锁补丁 5 字节、自建 stub 区、EndlessStatus.endless_type 4 字节。
      都不碰 ExcelMeta，也不改任何配置行。
"""
import os
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall       # noqa: E402
import wmpick as W  # noqa: E402  只读复用：常量/搜索/补丁/撤钩

# ---- RVA / 偏移 ----
RVA_GOTO_OW = W.RVA_GOTO_OW   # 0x19C5E00  OWEndlessModule.GoToOWEndless
RVA_GET_MODULE = W.RVA_GET_MODULE  # 0x1A92080  get_module（rcx 传 0 即可）

OFF_TWO      = 0x58   # OWEndlessModule._TwoEndless  (layout6.tsv: 37632 @ 88)
OFF_CURRENT  = 0x10   # TwoEndless._currentMode     (layout6.tsv: 37678 @ 16)
OFF_STATUS_TYPE = 0x10  # proto.EndlessStatus.endless_type (layout6.tsv: 9927 @ 16)

TYPE_DIRAC = 2
TYPE_QT = 3


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
# 和 wmpick.build_click_stub 的差别只有中间那段「量子」写：
#   wmpick 版：命中卡 → 直接投递 GoToOWEndless
#   这个版：  命中卡 → 先把 _currentMode.endless_type 摆成 3 → 再投递
#
# 手写机器码的约束（wmpick 里踩过的坑，照抄结论）：
#   * 只用 r10/r11/rax —— 全是调用者保存，函数入口处不承载有效值；
#     rcx 必须原样保留（原始前导 `mov rdi,rdx` / `mov rbx,rcx` 还要用）。
#   * 捕获槽 page+0x40 与信箱头 page+0x00 是两个地址，不能混用；
#     信箱头保持 pending 最后写，避免半截命令被执行。
#   * jz/jne 全是 rel8，最长一条要跨到 replay，所以整段必须压在 127 字节内
#     （build 里有 assert；实测 124，再塞东西就会溢出）。
# --------------------------------------------------------------------------
def build_qt_stub(slot_va, mb_va, meta_va, module_va, goto_va, orig, resume_va,
                  force_type=TYPE_QT):
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

    # --- 量子：把 _currentMode.endless_type 摆成 3 ---
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
            print("✗ 模式必须是数字：2 迪拉克 / 3 量子")
            return 1
        if want not in (TYPE_DIRAC, TYPE_QT):
            print("⚠ %d 不在已知可用集合 {2,3} 里，仍按你要求写入" % want)
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
        0: "0 None",
        1: "1 Normal",
        2: "2 迪拉克之海",
        3: "3 量子奇点",
        4: "4 超弦空间",
        5: "5 贪婪深渊",
        6: "6 前哨无尽",
    }.get(t, "%d 未知" % t)


# --------------------------------------------------------------------------
# 装接线
# --------------------------------------------------------------------------
def _install_qt_click(h, base, mb, page, hit):
    """把 DoClickAction 接到「量子 stub」。hit=(this, cd, meta) 由 setup 现场解析。"""
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
    blob = build_qt_stub(slot_va, mb, meta, mod, base + RVA_GOTO_OW,
                         orig, base + W.RVA_DOCLICK + 16, TYPE_QT)
    print("\n捕获槽 %#x   信箱头 %#x（两者不能相同）" % (slot_va, mb))
    print("stub  %d 字节 → %#x（里面带 endless_type=3）" % (len(blob), stub_va))
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
    print("\n✓ 量子点击接线已装。回游戏点那张卡（挑战页第 3 张），应当进入量子奇点。")
    print("  回迪拉克版：python wmqtpick.py off  然后 rehook.bat force")
    return 0


def cmd_setup():
    """解锁补丁 + 量子点击接线（顺序与 wmpick.cmd_setup 一致）。"""
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
        print("  · 量子点击接线（stub 里带 endless_type=3）")
        if not go:
            print("\n（演练。确认后加 --yes）")
            return 0

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

        print("\n--- 安装量子点击接线 ---")
        return _install_qt_click(h, base, mb, st["page"], hit)
    finally:
        icall.k32.CloseHandle(h)


def wait_panel(timeout=120.0):
    """硬门禁只有一条：挑战面板装配完成（MGR_SLOT 非 0）。"""
    deadline = time.time() + timeout
    note = ""
    while time.time() < deadline:
        h, pid, base = icall.open_game()
        if not h:
            print("\n✗ 找不到游戏进程")
            return None
        try:
            st = icall.load_state()
            if not st or st.get("pid") != pid:
                print("\n✗ 信箱与当前进程不匹配，先跑 python wmpick.py arm")
                return None
            raw = icall.read_mem(h, st["page"] + W.MGR_SLOT, 8)
            mgr = struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else 0
        finally:
            icall.k32.CloseHandle(h)
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
    rc = W.cmd_clickoff()
    print()
    print("--- 还原 _currentMode.endless_type ---")
    rc2 = cmd_mode(str(TYPE_DIRAC))
    return rc or rc2


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
            if b"\xC7\x40\x10\x03\x00\x00\x00" in stub:
                kind = "量子版（stub 内写 endless_type=3）"
            elif tgt == (st.get("page", 0) + W.CLICK_STUB_OFF if st else 0):
                kind = "迪拉克版（原 wmpick 接线）"
            elif tgt == (st.get("page", 0) + W.CAPTURE_STUB if st else 0):
                kind = "仅捕获（arm 状态，还没 setup）"
        print("接线版本: %s" % kind)

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
    if cmd == "status":
        return cmd_status()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
