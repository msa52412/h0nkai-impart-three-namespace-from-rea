# -*- coding: utf-8 -*-
"""BH3 内存补丁工具（Python + ctypes，无需编译器）

原理
----
磁盘上的 UserAssembly.dll 保持原版 → pkg_version 签名/完整性校验天然通过；
游戏跑起来之后，直接改进程内存里的机器码。

前提（已实测成立）
- ACE 保护驱动 ACE-BASE / ACE-GAME / ACE-ADVT 均为 STOPPED
- OpenProcess(PROCESS_VM_WRITE|VM_OPERATION) 成功
- EnumProcessModules / ReadProcessMemory / WriteProcessMemory 均可用

用法
----
    python mem_patch.py status            查看进程、模块基址、各补丁位当前字节
    python mem_patch.py apply             应用全部补丁
    python mem_patch.py apply noib        只应用指定补丁
    python mem_patch.py revert            还原全部补丁（写回原始字节）
    python mem_patch.py wait [秒数]       轮询等游戏起来后自动打补丁（默认 120 秒）

补丁清单
--------
noib   OODENFBANCC.NOIBCEBOLDE  (RVA 0xA52510) -> mov al,1; ret
       作用：世界地图卡片「容器数据有效性」判定恒真
             → CheckEntryValid 走 AddRealEntry() 分支 → 卡片显示

cvalid MonoWorldMapEntryContainerBase.CheckEntryValid (RVA 0x2CFB4C0) -> mov al,1; ret
       备用目标。注意：直接返回 true 不会执行 AddRealEntry()，
             单独用它卡片仍可能不出现，优先用 noib。
"""
import sys, os, time, struct
import ctypes
import ctypes.wintypes as wt
import pefile

DLL_PATH = r"D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll"
PROC_NAME = "BH3.exe"
IMAGE_BASE = 0x180000000

PATCHES = {
    "noib": {
        "rva": 0xA52510,
        "patch": bytes.fromhex("B001C3"),
        "desc": "OODENFBANCC.NOIBCEBOLDE -> mov al,1; ret",
    },
    "cvalid": {
        "rva": 0x2CFB4C0,
        "patch": bytes.fromhex("B001C3"),
        "desc": "CheckEntryValid -> mov al,1; ret",
    },
    "owopen": {
        "rva": 0x189D710,
        "patch": bytes.fromhex("31C0C3"),
        "desc": "OWEndlessModule.get_IsOWFeatureClosed -> 返回 false（迪拉克功能未关闭）",
    },
    # 把「超弦空间 goto」的页面构造重定向到迪拉克页面。
    # 调用点：UltraEndlessModule::OnGetUltraEndlessRspForGotoEndless + 0x1DD
    #   原始 E8 FE B2 B8 FE  -> call 0x1823F28A0 (UltraEndlessMainPageContextV2..ctor)
    #   改为 E8 FE 4B BA FD  -> call 0x18140C1A0 (OWEndlessStubPageContext..ctor)
    # 两个构造函数的序言完全一致（IL2CPP 样板，rcx=this），参数结构兼容。
    # rel32 与模块基址无关（两端同模块），所以固定字节即可。
    "owgoto": {
        "rva": 0x386759D,
        "patch": bytes.fromhex("E8FE4BBAFD"),
        "desc": "goto 重定向：超弦空间页面 -> 迪拉克页面 OWEndlessStubPageContext",
    },
}

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = wt.HANDLE
k32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
k32.CloseHandle.argtypes = [wt.HANDLE]
k32.ReadProcessMemory.restype = wt.BOOL
k32.ReadProcessMemory.argtypes = [wt.HANDLE, wt.LPCVOID, wt.LPVOID, ctypes.c_size_t,
                                 ctypes.POINTER(ctypes.c_size_t)]
k32.WriteProcessMemory.restype = wt.BOOL
k32.WriteProcessMemory.argtypes = [wt.HANDLE, wt.LPVOID, wt.LPCVOID, ctypes.c_size_t,
                                  ctypes.POINTER(ctypes.c_size_t)]
k32.VirtualProtectEx.restype = wt.BOOL
k32.VirtualProtectEx.argtypes = [wt.HANDLE, wt.LPVOID, ctypes.c_size_t, wt.DWORD,
                                 ctypes.POINTER(wt.DWORD)]
k32.FlushInstructionCache.restype = wt.BOOL
k32.FlushInstructionCache.argtypes = [wt.HANDLE, wt.LPCVOID, ctypes.c_size_t]
k32.CreateToolhelp32Snapshot.restype = wt.HANDLE
k32.CreateToolhelp32Snapshot.argtypes = [wt.DWORD, wt.DWORD]
k32.VirtualAllocEx.restype = wt.LPVOID
k32.VirtualAllocEx.argtypes = [wt.HANDLE, wt.LPVOID, ctypes.c_size_t, wt.DWORD, wt.DWORD]

MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000

TH32CS_SNAPPROCESS = 0x00000002
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010
PAGE_EXECUTE_READWRITE = 0x40
PROCESS_ALL = 0x0010 | 0x0020 | 0x0008 | 0x0400


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD),
                ("th32ProcessID", wt.DWORD), ("th32DefaultHeapID", ctypes.c_void_p),
                ("th32ModuleID", wt.DWORD), ("cntThreads", wt.DWORD),
                ("th32ParentProcessID", wt.DWORD), ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", wt.DWORD), ("szExeFile", wt.WCHAR * 260)]


class MODULEENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("th32ModuleID", wt.DWORD),
                ("th32ProcessID", wt.DWORD), ("GlblcntUsage", wt.DWORD),
                ("ProccntUsage", wt.DWORD), ("modBaseAddr", ctypes.c_void_p),
                ("modBaseSize", wt.DWORD), ("hModule", wt.HMODULE),
                ("szModule", wt.WCHAR * 256), ("szExePath", wt.WCHAR * 260)]


# 「只对指定 entry 生效」的补丁：用代码洞实现条件判断
# 目标函数 OODENFBANCC.NOIBCEBOLDE 的对象布局（已由构造函数反汇编确认）：
#   +0x10 int  entryID      <- 第二个参数，后续用于 GGMFAGLNJMM(entryID, index) 查表
#   +0x14 int  index
#   +0x18 行对象，查表结果；NOIBCEBOLDE 检查的就是它非空
#   +0x20 List<FNPIAMHMCKC> 内容列表
SCOPED = {
    "dirac": {
        "func_rva": 0xA52510,
        "entry_id": 1007,
        "patch_len": 14,
        "desc": "仅 entryID==1007 绕过 NOIBCEBOLDE，其它容器行为不变",
    },
}


def build_stub(func_va, stub_va, entry_id, orig, patch_len):
    """生成代码洞（全部用绝对跳转，避免 VirtualAllocEx 距离超出 ±2GB）：

         mov  eax,[rcx+0x10]     ; entryID
         cmp  eax,<id>
         jne  original
         mov  al,1 ; ret
    original:
         <原始 patch_len 字节>
         jmp  qword ptr [rip+0] ; 绝对跳到 func+patch_len
         <8 字节目标地址>
    """
    head = b"\x8B\x41\x10"                                   # mov eax,[rcx+0x10]
    head += b"\x3D" + struct.pack("<I", entry_id)             # cmp eax,imm32
    head += b"\x75\x06"                                      # jne -> original (offset 16)
    head += b"\xB0\x01\xC3"                                  # mov al,1 ; ret
    head += b"\x90\x90\x90"                                  # 补齐到 16
    assert len(head) == 16, len(head)
    tail = b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", func_va + patch_len)
    return head + orig + tail


def build_entry_jump(stub_va, patch_len):
    """入口处写入绝对跳转：jmp qword ptr [rip+0] + 8 字节目标。"""
    assert patch_len >= 14, patch_len
    jmp = b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", stub_va)
    return jmp + b"\x90" * (patch_len - len(jmp))


# ---------------------------------------------------------------- 原始字节
def build_rva_map():
    pe = pefile.PE(DLL_PATH, fast_load=True)
    data = open(DLL_PATH, "rb").read()

    def rva2off(rva):
        for s in pe.sections:
            if s.VirtualAddress <= rva < s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData):
                return s.PointerToRawData + (rva - s.VirtualAddress)
        return None
    return data, rva2off


ORIG = {}


def load_orig():
    data, rva2off = build_rva_map()
    for name, p in PATCHES.items():
        off = rva2off(p["rva"])
        p["orig"] = data[off:off + len(p["patch"])]
        ORIG[name] = p["orig"]


# ---------------------------------------------------------------- 进程/模块
def find_pid(name=PROC_NAME):
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == wt.HANDLE(-1).value or not snap:
        return None
    e = PROCESSENTRY32W(); e.dwSize = ctypes.sizeof(e)
    ok = k32.Process32FirstW(snap, ctypes.byref(e))
    pid = None
    while ok:
        if e.szExeFile.lower() == name.lower():
            pid = e.th32ProcessID
            break
        ok = k32.Process32NextW(snap, ctypes.byref(e))
    k32.CloseHandle(snap)
    return pid


def find_module(pid, want="UserAssembly.dll"):
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)
    if not snap or snap == wt.HANDLE(-1).value:
        return None
    e = MODULEENTRY32W(); e.dwSize = ctypes.sizeof(e)
    ok = k32.Module32FirstW(snap, ctypes.byref(e))
    base = None
    while ok:
        if want.lower() in e.szModule.lower():
            base = e.modBaseAddr
            break
        ok = k32.Module32NextW(snap, ctypes.byref(e))
    k32.CloseHandle(snap)
    return base


def read_mem(h, va, n):
    buf = ctypes.create_string_buffer(n)
    rd = ctypes.c_size_t(0)
    if not k32.ReadProcessMemory(h, ctypes.c_void_p(va), buf, n, ctypes.byref(rd)):
        return None
    return buf.raw[:rd.value]


def write_mem(h, va, data):
    old = wt.DWORD(0)
    if not k32.VirtualProtectEx(h, ctypes.c_void_p(va), len(data),
                                PAGE_EXECUTE_READWRITE, ctypes.byref(old)):
        print("   VirtualProtectEx 失败 err=%d" % ctypes.get_last_error()); return False
    wrote = ctypes.c_size_t(0)
    ok = k32.WriteProcessMemory(h, ctypes.c_void_p(va), data, len(data), ctypes.byref(wrote))
    if not ok:
        print("   WriteProcessMemory 失败 err=%d" % ctypes.get_last_error())
    k32.FlushInstructionCache(h, ctypes.c_void_p(va), len(data))
    tmp = wt.DWORD(0)
    k32.VirtualProtectEx(h, ctypes.c_void_p(va), len(data), old.value, ctypes.byref(tmp))
    return bool(ok) and wrote.value == len(data)


# ---------------------------------------------------------------- 命令
def attach():
    pid = find_pid()
    if not pid:
        print("未找到 %s 进程，请先启动游戏" % PROC_NAME)
        return None, None, None
    h = k32.OpenProcess(PROCESS_ALL, False, pid)
    if not h:
        print("OpenProcess 失败 err=%d" % ctypes.get_last_error())
        return None, None, pid
    base = find_module(pid)
    if not base:
        print("进程里还没加载 UserAssembly.dll（游戏可能仍在早期初始化）")
        return h, None, pid
    return h, base, pid


def status():
    h, base, pid = attach()
    if not h:
        return 1
    print("PID = %d    UserAssembly.dll 基址 = %#x" % (pid, base or 0))
    if not base:
        return 1
    for name, p in PATCHES.items():
        va = base + p["rva"]
        cur = read_mem(h, va, len(p["patch"]))
        if cur is None:
            print("  %-7s 读取失败" % name); continue
        if cur == p["patch"]:
            st = "已打补丁"
        elif cur == p["orig"]:
            st = "原始"
        else:
            st = "未知"
        print("  %-7s RVA=%#-9x VA=%#-13x %s  [%s]  %s"
              % (name, p["rva"], va, cur.hex(" "), st, p["desc"]))
    for name, sp in SCOPED.items():
        va = base + sp["func_rva"]
        L = sp.get("patch_len", 14)
        cur = read_mem(h, va, L)
        if cur is None:
            print("  %-7s 读取失败" % name); continue
        st = "已跳转(scoped)" if (cur[0] == 0xFF and cur[1] == 0x25) else "原始"
        print("  %-7s RVA=%#-9x VA=%#-13x %s  [%s]  %s"
              % (name, sp["func_rva"], va, cur.hex(" "), st, sp["desc"]))
    k32.CloseHandle(h)
    return 0


def apply(names):
    h, base, pid = attach()
    if not h or not base:
        if h: k32.CloseHandle(h)
        return 1
    print("PID = %d   基址 = %#x" % (pid, base))
    rc = 0
    for name in names:
        p = PATCHES[name]
        va = base + p["rva"]
        cur = read_mem(h, va, len(p["patch"]))
        if cur is None:
            print("  %-7s 读取失败，跳过" % name); rc = 1; continue
        if cur == p["patch"]:
            print("  %-7s 已是补丁状态，跳过" % name); continue
        if cur != p["orig"]:
            print("  %-7s 原始字节不匹配（%s），为安全起见跳过" % (name, cur.hex(" "))); rc = 1; continue
        if write_mem(h, va, p["patch"]):
            back = read_mem(h, va, len(p["patch"]))
            print("  %-7s ✓ %s -> %s  %s" % (name, cur.hex(" "), back.hex(" "), p["desc"]))
        else:
            print("  %-7s 写入失败" % name); rc = 1
    k32.CloseHandle(h)
    return rc


def revert(names):
    h, base, pid = attach()
    if not h or not base:
        if h: k32.CloseHandle(h)
        return 1
    print("PID = %d   基址 = %#x" % (pid, base))
    for name in names:
        p = PATCHES[name]
        va = base + p["rva"]
        cur = read_mem(h, va, len(p["patch"]))
        if cur is None:
            print("  %-7s 读取失败" % name); continue
        if cur == p["orig"]:
            print("  %-7s 已是原始字节" % name); continue
        if write_mem(h, va, p["orig"]):
            print("  %-7s ✓ 已还原为 %s" % (name, p["orig"].hex(" ")))
        else:
            print("  %-7s 还原失败" % name)
    k32.CloseHandle(h)
    return 0


def apply_scoped(name):
    """应用「只对指定 entry 生效」的代码洞补丁。"""
    sp = SCOPED[name]
    L = sp.get("patch_len", 14)
    h, base, pid = attach()
    if not h or not base:
        if h: k32.CloseHandle(h)
        return 1
    func_va = base + sp["func_rva"]
    cur = read_mem(h, func_va, L)
    if cur is None:
        print("  %-7s 读取失败" % name); k32.CloseHandle(h); return 1
    if cur[:2] == b"\xFF\x25":
        print("  %-7s 已是跳转状态（可能已打过），跳过" % name); k32.CloseHandle(h); return 0
    data, rva2off = build_rva_map()
    off = rva2off(sp["func_rva"])
    orig = data[off:off + L]
    if cur != orig:
        print("  %-7s 原始字节不匹配（%s vs %s），跳过" % (name, cur.hex(" "), orig.hex(" ")))
        k32.CloseHandle(h); return 1

    stub_va = k32.VirtualAllocEx(h, None, 128, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    if not stub_va:
        print("  VirtualAllocEx 失败 err=%d" % ctypes.get_last_error()); k32.CloseHandle(h); return 1
    stub = build_stub(func_va, stub_va, sp["entry_id"], orig, L)
    if not write_mem(h, stub_va, stub):
        print("  写代码洞失败"); k32.CloseHandle(h); return 1

    patch = build_entry_jump(stub_va, L)
    if not write_mem(h, func_va, patch):
        print("  入口跳转写入失败"); k32.CloseHandle(h); return 1
    back = read_mem(h, func_va, L)
    print("  %-7s ✓ 入口 %s" % (name, back.hex(" ")))
    print("           代码洞 @ %#x  %s" % (stub_va, sp["desc"]))
    k32.CloseHandle(h)
    return 0


def revert_scoped(name):
    sp = SCOPED[name]
    L = sp.get("patch_len", 14)
    h, base, pid = attach()
    if not h or not base:
        if h: k32.CloseHandle(h)
        return 1
    func_va = base + sp["func_rva"]
    cur = read_mem(h, func_va, L)
    if cur is None:
        print("  %-7s 读取失败" % name); k32.CloseHandle(h); return 1
    data, rva2off = build_rva_map()
    off = rva2off(sp["func_rva"])
    orig = data[off:off + L]
    if cur == orig:
        print("  %-7s 已是原始字节" % name); k32.CloseHandle(h); return 0
    if write_mem(h, func_va, orig):
        print("  %-7s ✓ 已还原为 %s" % (name, orig.hex(" ")))
    else:
        print("  %-7s 还原失败" % name)
    k32.CloseHandle(h)
    return 0


def wait_and_apply(timeout=120, names=None):
    names = names or list(SCOPED)
    print("等待 %s 启动（最多 %d 秒）；将应用: %s" % (PROC_NAME, timeout, ", ".join(names)))
    t0 = time.time()
    while time.time() - t0 < timeout:
        pid = find_pid()
        if pid:
            base = find_module(pid)
            if base:
                print("进程就绪 PID=%d 基址=%#x（等待 %.1fs）" % (pid, base, time.time() - t0))
                time.sleep(1.0)
                rc = 0
                for n in names:
                    if n in SCOPED:
                        rc |= apply_scoped(n)
                    elif n in PATCHES:
                        rc |= apply([n])
                    else:
                        print("未知补丁:", n); rc = 1
                return rc
        time.sleep(0.4)
    print("超时未就绪")
    return 1


if __name__ == "__main__":
    load_orig()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    args = sys.argv[2:]
    if cmd == "status":
        sys.exit(status())
    elif cmd in ("apply", "revert"):
        fn_simple = apply if cmd == "apply" else revert
        fn_scoped = apply_scoped if cmd == "apply" else revert_scoped
        names = args or (list(PATCHES) + list(SCOPED))
        rc = 0
        for n in names:
            if n in SCOPED:
                rc |= fn_scoped(n)
            elif n in PATCHES:
                rc |= fn_simple([n])
            else:
                print("未知补丁:", n); rc = 1
        sys.exit(rc)
    elif cmd == "wait":
        to = int(args[0]) if args else 120
        names = args[1:] if len(args) > 1 else None
        sys.exit(wait_and_apply(to, names))
    else:
        print(__doc__)
