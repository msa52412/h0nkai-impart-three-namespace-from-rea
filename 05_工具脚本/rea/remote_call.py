# -*- coding: utf-8 -*-
"""在目标进程里执行任意函数（远程线程方案，无需编译器）

这是「进程内调用」能力的地基：
  1. VirtualAllocEx 分配一块 RWX 内存，写入机器码 stub
  2. CreateRemoteThread 让目标进程执行 stub
  3. stub 里调用目标函数，把返回值写回一块可读内存
  4. 我们从外部读回结果

stub 机器码（x86-64）：
    48 B8 <imm64 func>     mov rax, func
    48 83 EC 28            sub rsp, 0x28
    FF D0                  call rax
    48 83 C4 28            add rsp, 0x28
    48 A3 <imm64 out>      mov [out], rax      ; 返回值落到 out
    C3                     ret

注意：这条路调的是「原生函数」。托管方法需要线程已 attach 到 il2cpp 域，
直接用远程线程调托管方法有风险 —— 后续要用「在游戏线程里跑」的方式（hook 热函数）。

用法
----
    python remote_call.py <pid> <模块名> <导出函数名>
例：
    python remote_call.py 15436 UserAssembly.dll il2cpp_get_api_table
"""
import sys, struct, time
import ctypes
import ctypes.wintypes as wt
import pefile

k32 = ctypes.WinDLL("kernel32", use_last_error=True)


def _setup():
    k32.OpenProcess.restype = wt.HANDLE
    k32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
    k32.VirtualAllocEx.restype = wt.LPVOID
    k32.VirtualAllocEx.argtypes = [wt.HANDLE, wt.LPVOID, ctypes.c_size_t, wt.DWORD, wt.DWORD]
    k32.WriteProcessMemory.restype = wt.BOOL
    k32.WriteProcessMemory.argtypes = [wt.HANDLE, wt.LPVOID, wt.LPCVOID, ctypes.c_size_t,
                                       ctypes.POINTER(ctypes.c_size_t)]
    k32.ReadProcessMemory.restype = wt.BOOL
    k32.ReadProcessMemory.argtypes = [wt.HANDLE, wt.LPCVOID, wt.LPVOID, ctypes.c_size_t,
                                      ctypes.POINTER(ctypes.c_size_t)]
    k32.CreateRemoteThread.restype = wt.HANDLE
    k32.CreateRemoteThread.argtypes = [wt.HANDLE, wt.LPVOID, ctypes.c_size_t, wt.LPVOID,
                                       wt.LPVOID, wt.DWORD, ctypes.POINTER(wt.DWORD)]
    k32.WaitForSingleObject.restype = wt.DWORD
    k32.WaitForSingleObject.argtypes = [wt.HANDLE, wt.DWORD]
    k32.CloseHandle.argtypes = [wt.HANDLE]
    k32.VirtualFreeEx.restype = wt.BOOL
    k32.VirtualFreeEx.argtypes = [wt.HANDLE, wt.LPVOID, ctypes.c_size_t, wt.DWORD]


_setup()

MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
MEM_RELEASE = 0x8000
PAGE_EXECUTE_READWRITE = 0x40
PROCESS_ALL = 0x0010 | 0x0020 | 0x0008 | 0x0400


class MODULEENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("th32ModuleID", wt.DWORD),
                ("th32ProcessID", wt.DWORD), ("GlblcntUsage", wt.DWORD),
                ("ProccntUsage", wt.DWORD), ("modBaseAddr", ctypes.c_void_p),
                ("modBaseSize", wt.DWORD), ("hModule", wt.HMODULE),
                ("szModule", wt.WCHAR * 256), ("szExePath", wt.WCHAR * 260)]


def find_module_base(pid, want):
    TH32CS_SNAPMODULE = 0x8
    TH32CS_SNAPMODULE32 = 0x10
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)
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


def export_rva(dll_path, name):
    pe = pefile.PE(dll_path, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
    for s in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        if s.name and s.name.decode() == name:
            return s.address
    return None


def build_stub(func_va, out_va):
    b = b"\x48\xB8" + struct.pack("<Q", func_va)
    b += b"\x48\x83\xEC\x28"
    b += b"\xFF\xD0"
    b += b"\x48\x83\xC4\x28"
    b += b"\x48\xA3" + struct.pack("<Q", out_va)
    b += b"\xC3"
    return b


def call_remote(pid, func_va, timeout_ms=5000):
    h = k32.OpenProcess(PROCESS_ALL, False, pid)
    if not h:
        raise SystemExit("OpenProcess 失败 err=%d" % ctypes.get_last_error())
    mem = k32.VirtualAllocEx(h, None, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    if not mem:
        raise SystemExit("VirtualAllocEx 失败 err=%d" % ctypes.get_last_error())
    out_va = mem + 0x800
    stub = build_stub(func_va, out_va)
    w = ctypes.c_size_t(0)
    k32.WriteProcessMemory(h, ctypes.c_void_p(mem), stub, len(stub), ctypes.byref(w))
    tid = wt.DWORD(0)
    th = k32.CreateRemoteThread(h, None, 0, ctypes.c_void_p(mem), None, 0, ctypes.byref(tid))
    if not th:
        raise SystemExit("CreateRemoteThread 失败 err=%d" % ctypes.get_last_error())
    rc = k32.WaitForSingleObject(th, timeout_ms)
    buf = ctypes.create_string_buffer(8); rd = ctypes.c_size_t(0)
    k32.ReadProcessMemory(h, ctypes.c_void_p(out_va), buf, 8, ctypes.byref(rd))
    ret = struct.unpack("<Q", buf.raw)[0] if rd.value == 8 else None
    k32.CloseHandle(th)
    k32.VirtualFreeEx(h, ctypes.c_void_p(mem), 0, MEM_RELEASE)
    k32.CloseHandle(h)
    return ret, rc


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__); raise SystemExit(1)
    pid = int(sys.argv[1]); mod = sys.argv[2]; fn = sys.argv[3]
    dll = None
    cands = [r"D:\BH3\7.0\BH3_Data\Native\UserAssembly.dll",
             r"D:\BH3\7.0\UnityPlayer.dll",
             r"C:\Windows\System32" + "\\" + mod,
             r"C:\Windows\SysWOW64" + "\\" + mod]
    for cand in cands:
        if cand.lower().endswith("\\" + mod.lower()) or cand.lower().endswith(mod.lower()):
            if __import__("os").path.exists(cand):
                dll = cand
                break
    if not dll:
        raise SystemExit("只内置了 UserAssembly.dll / UnityPlayer.dll 的导出解析")
    rva = export_rva(dll, fn)
    if rva is None:
        raise SystemExit("模块里没有这个导出: " + fn)
    base = find_module_base(pid, mod)
    if not base:
        raise SystemExit("进程里没找到模块 " + mod)
    func_va = base + rva
    print("PID=%d  %s 基址=%#x  导出 %s RVA=%#x  VA=%#x" % (pid, mod, base, fn, rva, func_va))
    ret, rc = call_remote(pid, func_va)
    print("远程调用完成 wait=%#x  返回值 = %s" % (rc, hex(ret) if ret is not None else "读取失败"))
