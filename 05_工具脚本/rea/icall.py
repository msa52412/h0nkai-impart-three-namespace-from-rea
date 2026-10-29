# -*- coding: utf-8 -*-
"""icall —— 在游戏主线程里调用任意函数（常驻指令槽）

为什么是这个架构
----------------
远程线程被拦截（CreateRemoteThread 退出码 0xFFFFFFFF），只能挂到游戏现有线程上。
但每调一个函数就「打钩子→还原」一次，等于反复改 14 字节代码入口，
既有碰撞风险，又要重复做同一件事。

所以改成常驻信箱（mailbox）：钩子只打一次，stub 常驻。
之后每次调用只是往信箱里写 target/args/pending，游戏线程下一帧自己取走执行。

    0x00  u8   pending      0xA5 = 有新命令待执行（其它任何值一律当「没命令」）
    0x01  u8   done         1 = 执行完毕 / 2 = stub 拒绝执行（target 为 0）
    0x08  u64  target       要调用的函数绝对地址
    0x10  u64  arg0         → rcx
    0x18  u64  arg1         → rdx
    0x20  u64  arg2         → r8
    0x28  u64  arg3         → r9
    0x30  u64  ret          ← rax

内存布局（一次分配 0x8000，整局复用）
    0x0000  信箱（0x40 字节）
    0x1000  stub
    0x2000  scratch（0x2000 字节，0x2000~0x3FFF）
    0x4000  每个被 hook 的函数占一页（0x4000、0x5000、0x6000、0x7000）

注意：scratch 只能到 0x3FFF。0x4000 起是钩子槽，scratch 越界写会把捕获 stub 打烂。
（旧版文档写「scratch 0x6000 字节」，与 HOOK_BASE_OFF=0x4000 冲突，已修正。）

stub（加固版，随后是原始 14 字节 + 跳回）
    49 BB <M>          mov  r11, M
    41 80 3B A5        cmp  byte [r11], 0xA5    ; 魔数校验
    75 xx              jne  orig                ; 不是魔数 → 直接跑原函数（done 不动）
    41 C6 03 00        mov  byte [r11], 0
    53                 push rbx
    51 52 41 50 41 51  push rcx, rdx, r8, r9     ; 保住原函数的 this/参数
    48 83 EC 20        sub  rsp, 0x20             ; 影子空间 + 对齐到 16
    4C 89 DB           mov  rbx, r11
    4C 8B 5B 08        mov  r11, [rbx+8]          ; target
    4D 85 DB           test r11, r11
    74 xx              jz   bail                  ; target 为 0 → 不调用，记 done=2
    48 8B 4B 10        mov  rcx, [rbx+0x10]
    48 8B 53 18        mov  rdx, [rbx+0x18]
    4C 8B 43 20        mov  r8,  [rbx+0x20]
    4C 8B 4B 28        mov  r9,  [rbx+0x28]
    41 FF D3           call r11
    48 89 43 30        mov  [rbx+0x30], rax
    C6 43 01 01        mov  byte [rbx+1], 1       ; done=1（调用之后才置位）
    EB xx              jmp  restore
 bail: C6 43 01 02     mov  byte [rbx+1], 2       ; done=2：看见了魔数但 target 是 0
 restore: 48 83 C4 20  add  rsp, 0x20
    41 59 41 58 5A 59  pop  r9, r8, rdx, rcx
    5B                 pop  rbx
    <原始 14 字节>
    FF 25 00 00 00 00 <host+14>                  ; 跳回原函数

三道闸的意义：
  1) pending 必须等于 0xA5 —— 内存被写脏时最坏结果是「这次命令没执行」
  2) target 为 0 不调用 —— 即使 pending 被伪造成魔数，也不会 call 0
  3) bail 时 done=2 —— 「拒绝执行」是可观测事件，不再是静默失败

关键点：done 在 call **之后**才置位。所以「done 没到」＝调用崩了/卡住了，
不会被误读成「返回 0」。（上一版就是栽在这里。）

用法
----
    python icall.py install              打钩子（每个游戏进程只需一次）
    python icall.py status
    python icall.py call 0x19C64E0 --arg0 scratch
    python icall.py call 0x18 --arg0 0x1234 --wait 3
    python icall.py read 0x2000 64       读 scratch 前 64 字节
    python icall.py uninstall            还原入口
"""
import sys, os, json, struct, time
import ctypes
import ctypes.wintypes as wt
import pefile

DLL_PATH = r"D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll"
PROC_NAME = "BH3.exe"
HOST_RVA = 0x21D2550          # MoleMole.MonoClientPacketConsumer.Update
PATCH_LEN = 14

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".icall.json")

MAILBOX_OFF = 0x0000
CAPTURE_OFF = 0x38            # 捕获到的 this 存这里
STUB_OFF = 0x1000
SCRATCH_OFF = 0x2000
ALLOC_SIZE = 0x8000
MAGIC = 0xA5                  # pending 必须是这个值才执行命令（防脏字节误触发）

# 每个被 hook 的函数单独占一个 0x1000 页，从 0x4000 开始
HOOK_BASE_OFF = 0x4000
HOOK_SLOT_SIZE = 0x1000

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = wt.HANDLE
k32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
k32.CloseHandle.argtypes = [wt.HANDLE]
k32.VirtualAllocEx.restype = wt.LPVOID
k32.VirtualAllocEx.argtypes = [wt.HANDLE, wt.LPVOID, ctypes.c_size_t, wt.DWORD, wt.DWORD]
k32.VirtualProtectEx.restype = wt.BOOL
k32.VirtualProtectEx.argtypes = [wt.HANDLE, wt.LPVOID, ctypes.c_size_t, wt.DWORD,
                                 ctypes.POINTER(wt.DWORD)]
k32.ReadProcessMemory.restype = wt.BOOL
k32.ReadProcessMemory.argtypes = [wt.HANDLE, wt.LPCVOID, wt.LPVOID, ctypes.c_size_t,
                                  ctypes.POINTER(ctypes.c_size_t)]
k32.WriteProcessMemory.restype = wt.BOOL
k32.WriteProcessMemory.argtypes = [wt.HANDLE, wt.LPVOID, wt.LPCVOID, ctypes.c_size_t,
                                   ctypes.POINTER(ctypes.c_size_t)]
k32.FlushInstructionCache.restype = wt.BOOL
k32.FlushInstructionCache.argtypes = [wt.HANDLE, wt.LPCVOID, ctypes.c_size_t]


class MODULEENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("th32ModuleID", wt.DWORD),
                ("th32ProcessID", wt.DWORD), ("GlblcntUsage", wt.DWORD),
                ("ProccntUsage", wt.DWORD), ("modBaseAddr", ctypes.c_void_p),
                ("modBaseSize", wt.DWORD), ("hModule", wt.HMODULE),
                ("szModule", wt.WCHAR * 256), ("szExePath", wt.WCHAR * 260)]


def find_pid(name=PROC_NAME):
    import subprocess, re
    out = subprocess.check_output(["tasklist", "/FI", "IMAGENAME eq %s" % name],
                                  text=True, errors="replace")
    m = re.search(re.escape(name) + r"\s+(\d+)", out)
    return int(m.group(1)) if m else None


def find_module_base(pid, want="UserAssembly.dll"):
    k32.CreateToolhelp32Snapshot.restype = wt.HANDLE
    k32.CreateToolhelp32Snapshot.argtypes = [wt.DWORD, wt.DWORD]
    snap = k32.CreateToolhelp32Snapshot(0x18, pid)
    e = MODULEENTRY32W(); e.dwSize = ctypes.sizeof(e)
    ok = k32.Module32FirstW(snap, ctypes.byref(e))
    base = None
    while ok:
        if e.szModule.lower() == want.lower():
            base = e.modBaseAddr
            break
        ok = k32.Module32NextW(snap, ctypes.byref(e))
    k32.CloseHandle(snap)
    return base


_pe = None


def pe():
    global _pe
    if _pe is None:
        _pe = pefile.PE(DLL_PATH, fast_load=True)
        _pe.parse_data_directories(
            directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
    return _pe


def module_span():
    """UserAssembly.dll 的内存映像大小（SizeOfImage），用于校验调用地址。

    2026-10-25 21:1x 事故后加：groupprobe.py 把反汇编里的 VA
    (0x183758440，已含 0x180000000) 当 RVA 又加了一次 base，
    实际 target 变成 0x7fffe3d758440 —— 未映射内存，客户端访问违例崩溃。
    cmd_call 之前只拦 target==0，拦不住这种越界。
    """
    try:
        return int(pe().OPTIONAL_HEADER.SizeOfImage)
    except Exception:
        return None


def rva2off(rva):
    for s in pe().sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData):
            return s.PointerToRawData + (rva - s.VirtualAddress)
    return None


def orig_bytes():
    off = rva2off(HOST_RVA)
    with open(DLL_PATH, "rb") as f:
        f.seek(off)
        return f.read(PATCH_LEN)


def file_bytes(rva, n):
    off = rva2off(rva)
    with open(DLL_PATH, "rb") as f:
        f.seek(off)
        return f.read(n)


def insn_len_at(rva, minimum=14):
    """从 rva 起按指令边界累加，返回 >= minimum 的最小边界长度。"""
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    data = file_bytes(rva, 64)
    total = 0
    for ins in md.disasm(data, 0x180000000 + rva):
        total += ins.size
        if total >= minimum:
            return total
    raise RuntimeError("无法在 64 字节内找到指令边界")


_REL_BRANCH = {
    "call", "jmp", "je", "jne", "jz", "jnz", "ja", "jae", "jb", "jbe", "jc", "jnc",
    "jg", "jge", "jl", "jle", "jo", "jno", "js", "jns", "jp", "jnp", "jpe", "jpo",
    "loop", "loope", "loopne", "jrcxz", "jecxz",
}


def unsafe_replay(orig, orig_va, new_va):
    """检查 orig 这段字节能否**原样**搬到 new_va 处执行。

    为什么需要这个
    --------------
    2026-10-25 16:01 实测事故：挂 `raise_null_reference_exception`(RVA 0x4FE400)，
    覆盖的 14 字节里有 `e8 67 a5 f4 ff`（call rel32 → 0x180449770）。
    这段字节原样搬到 stub(0xE51000) 后，rel32 位移不变，目标变成 0xD9B573，
    是个未映射地址，一跳就 Access Violation，游戏直接崩。

    规则：相对跳转 / RIP 相对寻址，只有在**目标落在本块内部**时才安全
    （整块一起平移，位移不变）。目标在块外就必须重定位，而 stub 与模块相距
    通常远超 ±2GB，rel32 装不下 —— 所以这里直接判定为不可挂钩。

    返回：问题描述列表，空列表表示安全。
    """
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    md.detail = True
    end = orig_va + len(orig)
    bad = []
    for ins in md.disasm(orig, orig_va):
        rel = ins.address - orig_va
        if ins.mnemonic in _REL_BRANCH:
            for op in ins.operands:
                if op.type == capstone.x86.X86_OP_IMM:
                    t = op.imm
                    if not (orig_va <= t < end):
                        bad.append("%s @+%#x → %#x（块外目标，需重定位）"
                                   % (ins.mnemonic, rel, t))
        for op in ins.operands:
            if (op.type == capstone.x86.X86_OP_MEM
                    and op.mem.base == capstone.x86.X86_REG_RIP):
                t = ins.address + ins.size + op.mem.disp
                if not (orig_va <= t < end):
                    bad.append("rip 相对寻址 @+%#x → %#x（块外目标，需重定位）"
                               % (rel, t))
    return bad


def build_capture_stub(slot_va, resume_va, orig):
    """只把 rcx 存下来，然后原样执行被覆盖的指令。r11 是调用者保存寄存器，可随意用。"""
    b = b""
    b += b"\x49\xBB" + struct.pack("<Q", slot_va)      # mov r11, slot
    b += b"\x49\x89\x0B"                                # mov [r11], rcx
    b += orig
    b += b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", resume_va)
    return b


def read_mem(h, va, n):
    buf = ctypes.create_string_buffer(n); rd = ctypes.c_size_t(0)
    if not k32.ReadProcessMemory(h, ctypes.c_void_p(va), buf, n, ctypes.byref(rd)):
        return None
    return buf.raw[:rd.value]


def write_mem(h, va, data):
    old = wt.DWORD(0)
    if not k32.VirtualProtectEx(h, ctypes.c_void_p(va), len(data), 0x40, ctypes.byref(old)):
        return False
    w = ctypes.c_size_t(0)
    ok = k32.WriteProcessMemory(h, ctypes.c_void_p(va), data, len(data), ctypes.byref(w))
    k32.FlushInstructionCache(h, ctypes.c_void_p(va), len(data))
    tmp = wt.DWORD(0)
    k32.VirtualProtectEx(h, ctypes.c_void_p(va), len(data), old.value, ctypes.byref(tmp))
    return bool(ok) and w.value == len(data)


def build_stub(mb_va, resume_va, orig):
    """信箱 stub。

    2026-10-25 加固：原版用「pending != 0」判有命令，实测 pending 被写成非 0、
    target 为 0，于是 call r11 跳到地址 0 直接崩游戏
    （crash.dmp: RIP=0, RBX=信箱, 栈顶=stub 内 call 的下一条）。
    现在改成三道闸：
      1) pending 必须等于魔数 0xA5，其它任何值一律当「没命令」
      2) target 为 0 时不调用，直接走恢复路径
      3) 走到 (2) 时把 done 置 2，让「拒绝执行」在外部可观测
    这样内存被写脏最多是「本次命令没执行」，不会带走进程，也不会静默失败。
    """
    b = b""
    b += b"\x49\xBB" + struct.pack("<Q", mb_va)      # mov r11, M
    b += b"\x41\x80\x3B" + bytes([MAGIC])            # cmp byte [r11], 0xA5
    jne_pos = len(b)
    b += b"\x75\x00"                                  # jne orig（不碰 done）
    b += b"\x41\xC6\x03\x00"                          # mov byte [r11], 0
    b += b"\x53"                                      # push rbx
    b += b"\x51\x52\x41\x50\x41\x51"                  # push rcx,rdx,r8,r9
    b += b"\x48\x83\xEC\x20"                          # sub rsp,0x20
    b += b"\x4C\x89\xDB"                              # mov rbx,r11
    b += b"\x4C\x8B\x5B\x08"                          # mov r11,[rbx+8]  (target)
    b += b"\x4D\x85\xDB"                              # test r11,r11
    jz_pos = len(b)
    b += b"\x74\x00"                                  # jz bail
    b += b"\x48\x8B\x4B\x10"                          # mov rcx,[rbx+0x10]
    b += b"\x48\x8B\x53\x18"                          # mov rdx,[rbx+0x18]
    b += b"\x4C\x8B\x43\x20"                          # mov r8,[rbx+0x20]
    b += b"\x4C\x8B\x4B\x28"                          # mov r9,[rbx+0x28]
    b += b"\x41\xFF\xD3"                              # call r11
    b += b"\x48\x89\x43\x30"                          # mov [rbx+0x30],rax
    b += b"\xC6\x43\x01\x01"                          # mov byte [rbx+1],1   done=1
    b += b"\xEB\x04"                                  # jmp restore（跳过 bail 那 4 字节）
    bail_pos = len(b)                                 # bail:
    b += b"\xC6\x43\x01\x02"                          # mov byte [rbx+1],2   done=2
    b += b"\x48\x83\xC4\x20"                          # restore: add rsp,0x20
    b += b"\x41\x59\x41\x58\x5A\x59"                  # pop r9,r8,rdx,rcx
    b += b"\x5B"                                      # pop rbx
    orig_pos = len(b)
    b += orig
    b += b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", resume_va)
    rel = orig_pos - (jne_pos + 2)
    assert 0 <= rel <= 127, (rel, orig_pos)
    b = b[:jne_pos + 1] + bytes([rel]) + b[jne_pos + 2:]
    rel2 = bail_pos - (jz_pos + 2)
    assert 0 <= rel2 <= 127, (rel2, bail_pos)
    b = b[:jz_pos + 1] + bytes([rel2]) + b[jz_pos + 2:]
    return b


def load_state():
    if not os.path.exists(STATE):
        return None
    try:
        return json.load(open(STATE))
    except Exception:
        return None


def save_state(d):
    json.dump(d, open(STATE, "w"), indent=2)


def open_game():
    pid = find_pid()
    if not pid:
        print("游戏未运行"); return None, None, None
    h = k32.OpenProcess(0x0410 | 0x0020 | 0x0008, False, pid)
    if not h:
        print("OpenProcess 失败"); return None, None, None
    return h, pid, find_module_base(pid)


def cmd_install():
    h, pid, base = open_game()
    if not h:
        return 1
    host_va = base + HOST_RVA
    orig = orig_bytes()
    cur = read_mem(h, host_va, PATCH_LEN)
    if cur != orig:
        print("宿主入口非原始字节 [%s]，先 uninstall 或重启游戏" % (cur.hex(" ") if cur else "读取失败"))
        k32.CloseHandle(h); return 1

    page = k32.VirtualAllocEx(h, None, ALLOC_SIZE, 0x3000, 0x40)
    if not page:
        print("VirtualAllocEx 失败"); k32.CloseHandle(h); return 1
    mb_va = page + MAILBOX_OFF
    stub_va = page + STUB_OFF
    scratch_va = page + SCRATCH_OFF

    write_mem(h, mb_va, b"\x00" * 0x40)
    # 自检：信箱必须读回全 0。读不回来说明这块地址根本没归我们（或被别的东西占着），
    # 继续挂钩就是在赌命 —— 2026-10-25 那次崩溃就是 pending 被写成非 0 导致的。
    chk = read_mem(h, mb_va, 0x40)
    if chk != b"\x00" * 0x40:
        print("✗ 信箱自检失败：写入全 0 后读回 %s" % (chk.hex(" ") if chk else "读取失败"))
        print("  这块地址可能被进程占用，放弃安装（入口未改动）")
        k32.CloseHandle(h); return 1
    stub = build_stub(mb_va, host_va + PATCH_LEN, orig)
    if not write_mem(h, stub_va, stub):
        print("stub 写入失败"); k32.CloseHandle(h); return 1
    # 自检 2：stub 必须原样落地。写进去和读回来不一致，说明这块地址不可写/被共享，
    # 那就绝不能把入口指过去 —— 否则游戏一跳就是执行随机字节。
    back = read_mem(h, stub_va, len(stub))
    if back != stub:
        print("✗ stub 落地自检失败：写入 %d 字节，读回 %s" % (
            len(stub), ("%d 字节" % len(back)) if back else "读取失败"))
        print("  入口未改动，安全退出")
        k32.CloseHandle(h); return 1
    entry = b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", stub_va)
    if not write_mem(h, host_va, entry):
        print("入口跳转写入失败"); k32.CloseHandle(h); return 1
    # 自检 3：入口必须指到 stub_va
    cur2 = read_mem(h, host_va, PATCH_LEN)
    if cur2 != entry:
        print("✗ 入口自检失败：读回 %s，预期 %s" % (
            cur2.hex(" ") if cur2 else "?", entry.hex(" ")))
        print("  正在尝试回滚入口…")
        write_mem(h, host_va, orig)
        k32.CloseHandle(h); return 1

    save_state({"pid": pid, "base": base, "page": page, "mailbox": mb_va,
                "stub": stub_va, "scratch": scratch_va})
    print("✓ 已安装（三道自检通过：信箱全 0 / stub 落地一致 / 入口指向正确）")
    print("  PID=%d  模块基址=%#x" % (pid, base))
    print("  信箱=%#x  stub=%#x (%d 字节)  scratch=%#x" % (mb_va, stub_va, len(stub), scratch_va))
    print("  scratch 可用 %d 字节（%#x~%#x，别越过 %#x）" % (
        HOOK_BASE_OFF - SCRATCH_OFF, scratch_va, page + HOOK_BASE_OFF - 1, page + HOOK_BASE_OFF))
    k32.CloseHandle(h)
    return 0


def cmd_uninstall():
    h, pid, base = open_game()
    if not h:
        return 1
    ok = write_mem(h, base + HOST_RVA, orig_bytes())
    print("✓ 已还原入口" if ok else "✗ 还原失败")
    k32.CloseHandle(h)
    return 0 if ok else 1


def cmd_status():
    h, pid, base = open_game()
    if not h:
        return 1
    host_va = base + HOST_RVA
    cur = read_mem(h, host_va, PATCH_LEN)
    st = load_state()
    hooked = cur and cur[:2] == b"\xFF\x25"
    print("PID=%d  基址=%#x  Update @ %#x" % (pid, base, host_va))
    print("入口 [%s]  %s" % (cur.hex(" ") if cur else "?",
                            "已挂钩子" if hooked else ("原始" if cur == orig_bytes() else "未知")))
    if st:
        alive = st.get("pid") == pid
        print("信箱 %#x  %s" % (st.get("mailbox", 0), "有效" if alive else "失效（进程已重启）"))
    else:
        print("未安装")
    k32.CloseHandle(h)
    return 0


def cmd_call(target, args, wait=5.0):
    st = load_state()
    if not st:
        print("未安装，先 install"); return 1
    if not target:
        # 这一条能挡住 2026-10-25 那次崩溃的直接成因：target=0 投进信箱
        print("✗ target 为 0，拒绝投递"); return 1
    h, pid, base = open_game()
    if not h:
        return 1
    if st["pid"] != pid:
        print("信箱已失效（游戏重启过），重新 install"); k32.CloseHandle(h); return 1

    # ★ 调用地址必须落在 UserAssembly.dll 映像内。
    # 不做这个检查的后果见 module_span() 的注释：0x7fffe3d758440 直接崩客户端。
    span = module_span()
    if span:
        off = target - base
        if not (0 <= off < span):
            print("✗ target %#x 不在 UserAssembly.dll 里" % target)
            print("  base=%#x  SizeOfImage=%#x  换算 rva=%#x"
                  % (base, span, target - base & 0xFFFFFFFFFFFFFFFF))
            print("  常见原因：把反汇编打印的 VA（0x18xxxxxxx）当 RVA 又加了一次 base。")
            k32.CloseHandle(h); return 1

    mb = st["mailbox"]
    scratch = st["scratch"]

    # 参数里的 scratch 关键字换成实际地址
    args = [scratch if a == "scratch" else a for a in args]
    args = (list(args) + [0, 0, 0, 0])[:4]

    pkt = b"\x00\x00" + b"\x00" * 6                        # pending=0, done=0
    pkt += struct.pack("<Q", target)
    pkt += b"".join(struct.pack("<Q", a & 0xFFFFFFFFFFFFFFFF) for a in args)
    pkt += struct.pack("<Q", 0)                            # ret
    if not write_mem(h, mb, pkt):
        print("信箱写入失败"); k32.CloseHandle(h); return 1

    # 投递前核对：target 必须真的落在信箱里。写失败但 pending 写成功，
    # 就是「stub 看见魔数却读到 target=0」的经典成因。
    back = read_mem(h, mb, len(pkt))
    if back != pkt:
        print("✗ 信箱回读不一致，放弃投递（pending 未置位）")
        print("  写入 %s" % pkt.hex(" "))
        print("  读回 %s" % (back.hex(" ") if back else "读取失败"))
        write_mem(h, mb, b"\x00" * len(pkt))
        k32.CloseHandle(h); return 1

    if not write_mem(h, mb, bytes([MAGIC])):               # pending = 0xA5
        print("✗ 魔数写入失败"); k32.CloseHandle(h); return 1
    chk = read_mem(h, mb, 1)
    if not chk or chk[0] != MAGIC:
        print("✗ 魔数回读失败（读回 %s）" % (chk.hex(" ") if chk else "?"))
        write_mem(h, mb, b"\x00")
        k32.CloseHandle(h); return 1

    print("命令已投递：target=%#x  args=[%s]" % (target, ", ".join(hex(a) for a in args)))

    t0 = time.time()
    ret = None
    bailed = False
    while time.time() - t0 < wait:
        d = read_mem(h, mb, 2)
        if d:
            if d[0] == 0 and d[1] == 1:
                raw = read_mem(h, mb + 0x30, 8)
                if raw and len(raw) == 8:
                    ret = struct.unpack("<Q", raw)[0]
                break
            if d[0] == 0 and d[1] == 2:
                bailed = True
                break
        time.sleep(0.05)
    if bailed:
        print("✗ stub 拒绝执行：看见了魔数，但 target 读出来是 0")
        print("  说明「target 写入」和「pending 置位」之间被别的东西插了一脚，")
        print("  或者信箱地址被进程内其它组件占用。跑 probe 盯 15 秒看看。")
        write_mem(h, mb, b"\x00\x00")
        k32.CloseHandle(h); return 1
    if ret is None:
        print("✗ 超时：游戏线程没取走命令（可能卡住/已崩溃）")
        write_mem(h, mb, b"\x00")
        k32.CloseHandle(h); return 1
    print("✓ 已执行  ret(rax) = %#x  (%d)  [%.2fs]" % (ret, ret, time.time() - t0))
    k32.CloseHandle(h)
    return 0


def cmd_read(off_or_va, n, absolute=False):
    st = load_state()
    if not st:
        print("未安装"); return 1
    h, pid, base = open_game()
    if not h:
        return 1
    va = off_or_va if absolute else st["page"] + off_or_va
    d = read_mem(h, va, n)
    k32.CloseHandle(h)
    if d is None:
        print("读取失败"); return 1
    for i in range(0, len(d), 16):
        chunk = d[i:i + 16]
        print("%#012x  %-47s  %s" % (va + i, chunk.hex(" "),
                                     "".join(chr(c) if 32 <= c < 127 else "." for c in chunk)))
    return 0


def cmd_hook(rva, slot_off=CAPTURE_OFF):
    st = load_state()
    if not st:
        print("未安装，先 install"); return 1
    h, pid, base = open_game()
    if not h:
        return 1
    if st["pid"] != pid:
        print("信箱已失效（游戏重启过），重新 install"); k32.CloseHandle(h); return 1
    page = st["page"]
    hooks = st.setdefault("hooks", {})
    key = str(rva)
    if key in hooks:
        print("该函数已挂钩（%#x）" % hooks[key]["slot"]); k32.CloseHandle(h); return 1

    L = insn_len_at(rva)
    orig = file_bytes(rva, L)
    fn_va = base + rva
    cur = read_mem(h, fn_va, L)
    if cur != orig:
        print("入口字节与文件不一致（%s vs %s），跳过" % (
            cur.hex(" ") if cur else "读取失败", orig.hex(" ")))
        k32.CloseHandle(h); return 1

    n = len(hooks)
    if HOOK_BASE_OFF + (n + 1) * HOOK_SLOT_SIZE > ALLOC_SIZE:
        print("挂钩槽位用尽"); k32.CloseHandle(h); return 1
    stub_va = page + HOOK_BASE_OFF + n * HOOK_SLOT_SIZE
    slot_va = page + slot_off

    # 安全闸：被覆盖的字节要原样搬到 stub 执行。若里面有块外的相对跳转/rip 寻址，
    # 搬过去就会跳错地址 → 崩游戏（2026-10-25 16:01 真实事故）。直接拒绝。
    bad = unsafe_replay(orig, fn_va, stub_va)
    if bad:
        print("✗ 这段函数头不能安全挂钩（覆盖 %d 字节）：" % L)
        for b in bad:
            print("    " + b)
        print("  原因：stub 与原函数相距太远，相对跳转无法原样搬运。入口未改动。")
        k32.CloseHandle(h); return 1

    stub = build_capture_stub(slot_va, fn_va + L, orig)
    if not write_mem(h, stub_va, stub):
        print("stub 写入失败"); k32.CloseHandle(h); return 1
    back = read_mem(h, stub_va, len(stub))
    if back != stub:
        print("✗ 捕获 stub 落地校验失败（写入 %d，读回 %s），入口未改动" % (
            len(stub), len(back) if back else "失败"))
        k32.CloseHandle(h); return 1
    jmp = b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", stub_va)
    if not write_mem(h, fn_va, jmp):
        print("入口跳转写入失败"); k32.CloseHandle(h); return 1
    cur2 = read_mem(h, fn_va, L)
    if cur2[:len(jmp)] != jmp:
        print("✗ 入口回读不符（%s），回滚" % (cur2.hex(" ") if cur2 else "?"))
        write_mem(h, fn_va, orig)
        k32.CloseHandle(h); return 1

    hooks[key] = {"slot": slot_va, "stub": stub_va, "len": L, "orig": orig.hex()}
    save_state(st)
    print("✓ 已挂钩 RVA %#x（覆盖 %d 字节，原始 %s）" % (rva, L, orig.hex(" ")))
    print("  入口 %#x → stub %#x，捕获结果写到 %#x" % (fn_va, stub_va, slot_va))
    print("  现在去游戏里触发一次，然后 python icall.py read %#x 8" % slot_off)
    k32.CloseHandle(h)
    return 0


def cmd_unhook(rva=None):
    st = load_state()
    if not st:
        print("未安装"); return 1
    h, pid, base = open_game()
    if not h:
        return 1
    hooks = st.get("hooks", {})
    if not hooks:
        print("没有挂钩"); k32.CloseHandle(h); return 1
    keys = [str(rva)] if rva is not None else list(hooks)
    for k in keys:
        if k not in hooks:
            print("未挂钩 RVA %s" % k); continue
        info = hooks[k]
        ok = write_mem(h, base + int(k), bytes.fromhex(info["orig"]))
        print(("✓ 已还原 RVA %s" if ok else "✗ 还原失败 RVA %s") % k)
        if ok:
            hooks.pop(k, None)
    save_state(st)
    k32.CloseHandle(h)
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    cmd = sys.argv[1]
    if cmd == "install":
        return cmd_install()
    if cmd == "uninstall":
        return cmd_uninstall()
    if cmd == "status":
        return cmd_status()
    if cmd == "hook":
        slot = int(sys.argv[3], 0) if len(sys.argv) > 3 else CAPTURE_OFF
        return cmd_hook(int(sys.argv[2], 0) & 0x0FFFFFFF, slot)
    if cmd == "unhook":
        return cmd_unhook(int(sys.argv[2], 0) & 0x0FFFFFFF if len(sys.argv) > 2 else None)
    if cmd == "read":
        off = int(sys.argv[2], 0)
        n = int(sys.argv[3], 0) if len(sys.argv) > 3 else 64
        return cmd_read(off, n, "--va" in sys.argv)
    if cmd == "call":
        raw = int(sys.argv[2], 0)
        target = raw if "--abs" in sys.argv else (find_module_base(find_pid() or 0) or 0) + (raw & 0x0FFFFFFF)
        if not target:
            print("游戏未运行"); return 1
        args, wait = [], 5.0
        i = 3
        while i < len(sys.argv):
            a = sys.argv[i]
            if a == "--wait":
                wait = float(sys.argv[i + 1]); i += 2; continue
            if a.startswith("--arg"):
                v = sys.argv[i + 1]
                args.append(v if v == "scratch" else int(v, 0)); i += 2; continue
            i += 1
        return cmd_call(target, args, wait)
    print(__doc__); return 1


if __name__ == "__main__":
    sys.exit(main())
