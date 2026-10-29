# -*- coding: utf-8 -*-
"""在游戏主线程里调用任意函数，并取回返回值。

原理
----
远程线程被拦截（CreateRemoteThread 退出码 0xFFFFFFFF），但内存读写正常。
所以不建线程，改成「热函数 hook」：把每帧必调的
`MoleMole.MonoClientPacketConsumer.Update` 入口换成绝对跳转，
游戏自己每帧跳到我们的 stub。stub 只执行一次，做完就把入口还原。

为什么必须在游戏线程里跑
------------------------
调托管方法（il2cpp）要求当前线程已 attach 到 il2cpp 运行时、且处于 GC 安全点。
游戏主线程天然满足，新建线程则必须手动 attach —— 而 attach 函数本身没导出。

stub 结构
---------
    mov r11, flag          49 BB <flag>
    cmp byte [r11], 0      41 80 3B 00
    jne orig               75 <rel>
    mov byte [r11], 1      41 C6 03 01
    push rcx/rdx/r8/r9     保存参数寄存器（原函数入口要用 rcx=this）
    sub rsp, 0x28          影子空间 + 16 字节对齐
    mov rax, target        48 B8 <target>
    call rax               FF D0
    add rsp, 0x28
    pop r9/r8/rdx/rcx
    mov r11, out           49 BB <out>
    mov [r11], rax         49 89 03
    <原始 14 字节>
    jmp [rip+0] -> orig+14 FF 25 00 00 00 00 <addr>

用法
----
    python thread_call.py export il2cpp_get_api_table
    python thread_call.py rva 0x21D2550
    python thread_call.py rva 0x1821D2550 --arg0 0x1234 --wait 5
    python thread_call.py status
    python thread_call.py revert
"""
import sys, os, struct, time
import ctypes
import ctypes.wintypes as wt
import pefile

DLL_PATH = r"D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll"
PROC_NAME = "BH3.exe"
HOST_RVA = 0x21D2550          # MonoClientPacketConsumer.Update
PATCH_LEN = 14

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
    k32.ReadProcessMemory.restype = wt.BOOL
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
    k32.CreateToolhelp32Snapshot.restype = wt.HANDLE
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


def rva2off(rva):
    for s in pe().sections:
        if s.VirtualAddress <= rva < s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData):
            return s.PointerToRawData + (rva - s.VirtualAddress)
    return None


def export_rva(name):
    ex = getattr(pe(), "DIRECTORY_ENTRY_EXPORT", None)
    if not ex:
        return None
    for s in ex.symbols:
        if s.name and s.name.decode() == name:
            return s.address
    return None


def orig_bytes():
    off = rva2off(HOST_RVA)
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


def build_stub(target_va, resume_va, flag_va, out_va, orig, args):
    """args = [rcx, rdx, r8, r9]（可少于 4 个）"""
    b = b""
    b += b"\x49\xBB" + struct.pack("<Q", flag_va)      # mov r11, flag
    b += b"\x41\x80\x3B\x00"                            # cmp byte [r11], 0
    jne_pos = len(b)
    b += b"\x75\x00"                                    # jne orig（占位，稍后回填）
    b += b"\x41\xC6\x03\x01"                            # mov byte [r11], 1
    b += b"\x51\x52\x41\x50\x41\x51"                    # push rcx, rdx, r8, r9
    b += b"\x48\x83\xEC\x28"                            # sub rsp, 0x28
    for reg, val in zip((b"\xB9", b"\xBA", b"\x41\xB8", b"\x41\xB9"), args):
        b += reg + struct.pack("<I", val & 0xFFFFFFFF)  # mov ecx/edx/r8d/r9d, imm32
    b += b"\x48\xB8" + struct.pack("<Q", target_va)     # mov rax, target
    b += b"\xFF\xD0"                                    # call rax
    b += b"\x48\x83\xC4\x28"                            # add rsp, 0x28
    b += b"\x41\x59\x41\x58\x5A\x59"                    # pop r9, r8, rdx, rcx
    b += b"\x49\xBB" + struct.pack("<Q", out_va)        # mov r11, out
    b += b"\x49\x89\x03"                                # mov [r11], rax
    orig_pos = len(b)
    b += orig
    b += b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", resume_va)
    # 回填 jne 目标 = orig_pos
    rel = orig_pos - (jne_pos + 2)
    assert -128 <= rel <= 127, rel
    b = b[:jne_pos + 1] + bytes([rel]) + b[jne_pos + 2:]
    return b


def call_in_thread(target_va, args=(), wait=5.0, label=""):
    pid = find_pid()
    if not pid:
        print("游戏未运行"); return None
    h = k32.OpenProcess(0x0410 | 0x0020 | 0x0008, False, pid)
    if not h:
        print("OpenProcess 失败"); return None
    base = find_module_base(pid)
    host_va = base + HOST_RVA
    orig = orig_bytes()
    cur = read_mem(h, host_va, PATCH_LEN)
    if cur != orig:
        print("宿主入口不是原始字节（%s），可能残留钩子；先 revert" % (
            cur.hex(" ") if cur else "读取失败"))
        k32.CloseHandle(h); return None

    page = k32.VirtualAllocEx(h, None, 0x1000, 0x3000, 0x40)
    if not page:
        print("VirtualAllocEx 失败"); k32.CloseHandle(h); return None
    flag_va, out_va = page + 0xF00, page + 0xF08
    stub = build_stub(target_va, host_va + PATCH_LEN, flag_va, out_va, orig, list(args))
    write_mem(h, page, stub)
    write_mem(h, flag_va, b"\x00")
    write_mem(h, out_va, b"\x00" * 8)

    print("PID=%d 基址=%#x" % (pid, base))
    print("目标 %s = %#x" % (label or "func", target_va))
    print("stub @ %#x (%d 字节)  flag=%#x  out=%#x" % (page, len(stub), flag_va, out_va))
    if not write_mem(h, host_va, b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", page)):
        print("入口跳转写入失败"); k32.CloseHandle(h); return None
    print("钩子已挂上，等待游戏线程…")

    res, flag = None, 0
    t0 = time.time()
    while time.time() - t0 < wait:
        f = read_mem(h, flag_va, 1)
        if f and f[0] == 1:
            flag = 1
            d = read_mem(h, out_va, 8)
            if d and len(d) == 8:
                res = struct.unpack("<Q", d)[0]
            break
        time.sleep(0.1)

    # 立即还原入口，避免游戏在 stub 生命周期外继续跳进来
    write_mem(h, host_va, orig)
    if flag:
        print("✓ 已执行，返回值 rax = %#x (%d)" % (res, res))
    else:
        print("✗ 超时：宿主函数没被调用，或 stub 崩溃导致 flag 未置位")
    k32.CloseHandle(h)
    return res if flag else None


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    cmd = sys.argv[1]
    if cmd == "status":
        pid = find_pid()
        if not pid:
            print("游戏未运行"); return 1
        h = k32.OpenProcess(0x0410, False, pid)
        base = find_module_base(pid)
        cur = read_mem(h, base + HOST_RVA, PATCH_LEN)
        print("PID=%d  Update @ %#x  [%s] %s" % (
            pid, base + HOST_RVA, cur.hex(" ") if cur else "?",
            "原始" if cur == orig_bytes() else "非原始(有残留钩子)"))
        k32.CloseHandle(h); return 0
    if cmd == "revert":
        pid = find_pid()
        if not pid:
            print("游戏未运行"); return 1
        h = k32.OpenProcess(0x0410 | 0x0020 | 0x0008, False, pid)
        base = find_module_base(pid)
        ok = write_mem(h, base + HOST_RVA, orig_bytes())
        print("✓ 已还原" if ok else "✗ 还原失败")
        k32.CloseHandle(h); return 0

    # call 模式
    if cmd == "export":
        name = sys.argv[2]
        rva = export_rva(name)
        if rva is None:
            print("导出不存在:", name); return 1
        label = "export %s (RVA %#x)" % (name, rva)
    elif cmd == "rva":
        rva = int(sys.argv[2], 0) & 0x0FFFFFFF
        label = "RVA %#x" % rva
    else:
        print(__doc__); return 1

    args, wait = [], 5.0
    i = 3
    while i < len(sys.argv):
        a = sys.argv[i]
        if a == "--wait":
            wait = float(sys.argv[i + 1]); i += 2; continue
        if a.startswith("--arg"):
            args.append(int(sys.argv[i + 1], 0)); i += 2; continue
        i += 1
    args = (args + [0, 0, 0, 0])[:4]

    pid = find_pid()
    if not pid:
        print("游戏未运行"); return 1
    base = find_module_base(pid)
    call_in_thread(base + rva, args, wait, label)
    return 0


if __name__ == "__main__":
    sys.exit(main())
