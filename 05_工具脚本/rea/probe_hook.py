# -*- coding: utf-8 -*-
"""在游戏主线程里执行我们自己的代码 —— 热函数 hook 探针

为什么不用远程线程
------------------
实测：CreateRemoteThread 在 BH3 进程里被拦截（线程退出码 0xFFFFFFFF，
但 VirtualAllocEx / WriteProcessMemory 全部成功）。
所以改成「挂到游戏现有线程上」：把每帧必调的 Unity Update 入口改成绝对跳转，
让游戏自己每帧跳到我们的 stub。好处：
  * 不创建线程 → 绕开拦截
  * 跑在游戏主线程 → 调用托管方法时 il2cpp 线程已 attach，GC 安全

本脚本只做最小验证：stub 里先写一个标记值再执行原始指令跳回。
如果能在内存里读到标记，说明「在游戏线程里跑自己的代码」这条链路通了。

宿主函数
--------
MoleMole.MonoClientPacketConsumer.Update   RVA 0x21D2550
前 14 字节（恰好落在指令边界）：
    40 53                push rbx
    48 83 EC 20          sub rsp, 0x20
    48 8B D9             mov rbx, rcx
    B9 82 22 01 00       mov ecx, 0x12282

用法
----
    python probe_hook.py run [秒数]    打钩子、等标记、回读
    python probe_hook.py revert        还原宿主函数
    python probe_hook.py status        查看当前状态
"""
import sys, os, struct, time
import ctypes
import ctypes.wintypes as wt
import pefile

DLL_PATH = r"D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll"
PROC_NAME = "BH3.exe"
FUNC_RVA = 0x21D2550
PATCH_LEN = 14
MARKER = 0xCAFEBABE

k32 = ctypes.WinDLL("kernel32", use_last_error=True)


def _init():
    k32.OpenProcess.restype = wt.HANDLE
    k32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
    k32.CloseHandle.argtypes = [wt.HANDLE]
    k32.VirtualAllocEx.restype = wt.LPVOID
    k32.VirtualAllocEx.argtypes = [wt.HANDLE, wt.LPVOID, ctypes.c_size_t, wt.DWORD, wt.DWORD]
    k32.VirtualProtectEx.restype = wt.BOOL
    k32.VirtualProtectEx.argtypes = [wt.HANDLE, wt.LPVOID, ctypes.c_size_t, wt.DWORD,
                                     ctypes.POINTER(wt.DWORD)]
    for f in ("ReadProcessMemory",):
        getattr(k32, f).restype = wt.BOOL
    k32.ReadProcessMemory.argtypes = [wt.HANDLE, wt.LPCVOID, wt.LPVOID, ctypes.c_size_t,
                                      ctypes.POINTER(ctypes.c_size_t)]
    k32.WriteProcessMemory.restype = wt.BOOL
    k32.WriteProcessMemory.argtypes = [wt.HANDLE, wt.LPVOID, wt.LPCVOID, ctypes.c_size_t,
                                       ctypes.POINTER(ctypes.c_size_t)]
    k32.FlushInstructionCache.restype = wt.BOOL
    k32.FlushInstructionCache.argtypes = [wt.HANDLE, wt.LPCVOID, ctypes.c_size_t]


_init()


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


def rva2off(rva):
    pe = pefile.PE(DLL_PATH, fast_load=True)
    for s in pe.sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData):
            return s.PointerToRawData + (rva - s.VirtualAddress)
    return None


def orig_bytes():
    off = rva2off(FUNC_RVA)
    with open(DLL_PATH, "rb") as f:
        f.seek(off)
        return f.read(PATCH_LEN)


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


def build_stub(func_va, stub_va, flag_va, out_va, orig):
    """stub 用 r11（调用者保存、非参数寄存器），不会破坏 this/参数。"""
    b = b""
    b += b"\x49\xBB" + struct.pack("<Q", flag_va)          # mov r11, flag
    b += b"\x41\x80\x3B\x00"                                # cmp byte [r11], 0
    b += b"\x75\x15"                                        # jne original (offset 37)
    b += b"\x41\xC6\x03\x01"                                # mov byte [r11], 1
    b += b"\x49\xBB" + struct.pack("<Q", out_va)            # mov r11, out
    b += b"\x41\xC7\x03" + struct.pack("<I", MARKER)        # mov dword [r11], MARKER
    assert len(b) == 37, len(b)
    b += orig                                               # 原始 14 字节
    b += b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", func_va + PATCH_LEN)
    return b


def entry_jump(stub_va):
    return b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", stub_va)


def run(wait=5.0):
    pid = find_pid()
    if not pid:
        print("游戏未运行"); return 1
    h = k32.OpenProcess(0x0410 | 0x0020 | 0x0008, False, pid)
    if not h:
        print("OpenProcess 失败"); return 1
    base = find_module_base(pid)
    func_va = base + FUNC_RVA
    orig = orig_bytes()
    cur = read_mem(h, func_va, PATCH_LEN)
    print("PID=%d  基址=%#x  Update @ %#x" % (pid, base, func_va))
    print("原始字节: %s" % orig.hex(" "))
    if cur and cur[:2] == b"\xFF\x25":
        print("已经打过钩子，先 revert"); k32.CloseHandle(h); return 1
    if cur != orig:
        print("入口字节与文件不一致（%s），跳过" % (cur.hex(" ") if cur else "读取失败"))
        k32.CloseHandle(h); return 1

    page = k32.VirtualAllocEx(h, None, 0x1000, 0x3000, 0x40)
    if not page:
        print("VirtualAllocEx 失败"); k32.CloseHandle(h); return 1
    flag_va, out_va = page + 0xF00, page + 0xF08
    stub = build_stub(func_va, page, flag_va, out_va, orig)
    write_mem(h, page, stub)
    write_mem(h, flag_va, b"\x00")
    write_mem(h, out_va, b"\x00" * 4)
    print("stub @ %#x (%d 字节)  flag=%#x  out=%#x" % (page, len(stub), flag_va, out_va))

    if not write_mem(h, func_va, entry_jump(page)):
        print("入口跳转写入失败"); k32.CloseHandle(h); return 1
    print("钩子已挂上，等待游戏线程执行（最多 %.1fs）..." % wait)

    got = None
    t0 = time.time()
    while time.time() - t0 < wait:
        d = read_mem(h, out_va, 4)
        if d and struct.unpack("<I", d)[0] == MARKER:
            got = time.time() - t0
            break
        time.sleep(0.2)
    if got is not None:
        print("✓ 成功：%.2fs 后读到标记 %#x —— 我们的代码确实在游戏线程里跑了" % (got, MARKER))
        rc = 0
    else:
        print("✗ 未读到标记（可能宿主函数未被调用，或 hook 未生效）")
        rc = 1
    # 还原，避免长期占着入口
    write_mem(h, func_va, orig)
    print("已还原宿主函数入口")
    k32.CloseHandle(h)
    return rc


def revert():
    pid = find_pid()
    if not pid:
        print("游戏未运行"); return 1
    h = k32.OpenProcess(0x0410 | 0x0020 | 0x0008, False, pid)
    base = find_module_base(pid)
    func_va = base + FUNC_RVA
    orig = orig_bytes()
    if write_mem(h, func_va, orig):
        print("✓ 已还原为 %s" % orig.hex(" "))
    k32.CloseHandle(h)
    return 0


def status():
    pid = find_pid()
    if not pid:
        print("游戏未运行"); return 1
    h = k32.OpenProcess(0x0410, False, pid)
    base = find_module_base(pid)
    func_va = base + FUNC_RVA
    cur = read_mem(h, func_va, PATCH_LEN)
    orig = orig_bytes()
    st = "已挂钩子(跳转)" if cur and cur[:2] == b"\xFF\x25" else (
        "原始" if cur == orig else "未知")
    print("PID=%d  Update @ %#x  当前 %s  [%s]" % (pid, func_va, cur.hex(" "), st))
    k32.CloseHandle(h)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "run":
        sys.exit(run(float(sys.argv[2]) if len(sys.argv) > 2 else 5.0))
    elif cmd == "revert":
        sys.exit(revert())
    else:
        sys.exit(status())
