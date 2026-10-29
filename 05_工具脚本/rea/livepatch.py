# -*- coding: utf-8 -*-
"""livepatch —— 在运行中的 BH3 里安全改写代码字节（先挂起其它线程，再写）

为什么不能直接 WriteProcessMemory
----------------------------------
WriteProcessMemory 不是原子的：18 字节会分几次写进目标进程。如果游戏主线程
此刻正执行这个函数的开头，就可能取到「一半新、一半旧」的指令流，直接崩客户端。

这里在写之前把目标进程里除自己以外的线程全部 SuspendThread，写完立刻
ResumeThread。窗口只有一次 WriteProcessMemory 的时间，且这期间没有线程能在
被改写的区间里取指。

用法
----
    import livepatch
    livepatch.write_code(h, pid, va, data, icall.write_mem)

只做「挂起 -> 调 write_fn -> 恢复」，不关心 write_fn 怎么实现，
所以和 icall.write_mem（带 VirtualProtectEx + FlushInstructionCache）天然兼容。
"""
import ctypes
import ctypes.wintypes as wt

k32 = ctypes.WinDLL("kernel32", use_last_error=True)

TH32CS_SNAPTHREAD = 0x00000004
THREAD_SUSPEND_RESUME = 0x0002
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


class THREADENTRY32(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD),
                ("cntUsage", wt.DWORD),
                ("th32ThreadID", wt.DWORD),
                ("th32OwnerProcessID", wt.DWORD),
                ("tpBasePri", ctypes.c_long),
                ("tpDeltaPri", ctypes.c_long),
                ("dwFlags", wt.DWORD)]


def _init():
    k32.CreateToolhelp32Snapshot.restype = wt.HANDLE
    k32.CreateToolhelp32Snapshot.argtypes = [wt.DWORD, wt.DWORD]
    k32.Thread32First.restype = wt.BOOL
    k32.Thread32First.argtypes = [wt.HANDLE, ctypes.POINTER(THREADENTRY32)]
    k32.Thread32Next.restype = wt.BOOL
    k32.Thread32Next.argtypes = [wt.HANDLE, ctypes.POINTER(THREADENTRY32)]
    k32.OpenThread.restype = wt.HANDLE
    k32.OpenThread.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
    k32.SuspendThread.restype = wt.DWORD
    k32.SuspendThread.argtypes = [wt.HANDLE]
    k32.ResumeThread.restype = wt.DWORD
    k32.ResumeThread.argtypes = [wt.HANDLE]


_init()


def thread_ids(pid):
    """返回 pid 的所有线程 id（不含 0）。快照失败返回空列表。"""
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if not snap or snap == INVALID_HANDLE_VALUE:
        return []
    out = []
    try:
        e = THREADENTRY32()
        e.dwSize = ctypes.sizeof(e)
        ok = k32.Thread32First(snap, ctypes.byref(e))
        while ok:
            if e.th32OwnerProcessID == pid and e.th32ThreadID:
                out.append(e.th32ThreadID)
            ok = k32.Thread32Next(snap, ctypes.byref(e))
    finally:
        k32.CloseHandle(snap)
    return out


def _suspend_all(pid):
    handles = []
    for tid in thread_ids(pid):
        h = k32.OpenThread(THREAD_SUSPEND_RESUME, False, tid)
        if not h or h == INVALID_HANDLE_VALUE:
            continue
        if k32.SuspendThread(h) == 0xFFFFFFFF:
            k32.CloseHandle(h)
            continue
        handles.append(h)
    return handles


def _resume_all(handles):
    for h in handles:
        k32.ResumeThread(h)
        k32.CloseHandle(h)


def write_code(h, pid, va, data, write_fn):
    """挂起 pid 的所有线程 -> write_fn(h, va, data) -> 恢复。

    返回 (ok, suspended_count)。write_fn 抛异常时也会恢复线程。
    """
    handles = _suspend_all(pid)
    try:
        ok = write_fn(h, va, data)
    finally:
        _resume_all(handles)
    return ok, len(handles)


if __name__ == "__main__":
    import sys
    print("threads of pid %s: %s" % (sys.argv[1] if len(sys.argv) > 1 else "?",
                                     thread_ids(int(sys.argv[1])) if len(sys.argv) > 1 else []))
