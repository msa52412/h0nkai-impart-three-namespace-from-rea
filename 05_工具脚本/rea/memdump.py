# -*- coding: utf-8 -*-
"""从运行中的游戏进程内存里抓取 ctable 解密后的明文。

用途：ctable.dat 的加载器在 UnityPlayer.dll 内（自定义密码 + 控制流平坦化），
静态逆向成本高；但进程启动后明文必然短暂存在于堆上，直接读内存更快。

用法:
    python memdump.py scan  [--exe BH3.exe] [--pat EntryImagePath]
    python memdump.py dump  <base_hex> <size_hex> -o out.bin
    python memdump.py heaps [--min 1048576]
"""
import sys, ctypes, ctypes.wintypes as wt, re, os

k32 = ctypes.WinDLL("kernel32", use_last_error=True)

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

MEM_COMMIT = 0x1000
PAGE_READABLE = (0x02, 0x04, 0x20, 0x40)  # READONLY, READWRITE, EXECUTE_READ, EXECUTE_READWRITE


class MEMORY_BASIC_INFORMATION64(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_ulonglong),
        ("AllocationBase", ctypes.c_ulonglong),
        ("AllocationProtect", wt.DWORD),
        ("__alignment1", wt.DWORD),
        ("RegionSize", ctypes.c_ulonglong),
        ("State", wt.DWORD),
        ("Protect", wt.DWORD),
        ("Type", wt.DWORD),
        ("__alignment2", wt.DWORD),
    ]


def find_pid(exe="BH3.exe"):
    import subprocess
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq " + exe, "/FO", "CSV", "/NH"],
                         capture_output=True, text=True, encoding="gbk", errors="replace").stdout
    for line in out.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) >= 2 and parts[0].lower() == exe.lower():
            return int(parts[1])
    return None


def open_proc(pid):
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h:
        raise OSError("OpenProcess 失败 %d" % ctypes.get_last_error())
    return h


def regions(h):
    addr = 0
    mbi = MEMORY_BASIC_INFORMATION64()
    while addr < 0x7FFFFFFFFFFF:
        got = k32.VirtualQueryEx(ctypes.c_void_p(h), ctypes.c_void_p(addr),
                                 ctypes.byref(mbi), ctypes.sizeof(mbi))
        if not got:
            break
        yield mbi.BaseAddress, mbi.RegionSize, mbi.State, mbi.Protect
        addr = mbi.BaseAddress + mbi.RegionSize


def read_mem(h, base, size):
    buf = ctypes.create_string_buffer(size)
    read = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(ctypes.c_void_p(h), ctypes.c_void_p(base),
                               buf, size, ctypes.byref(read))
    return buf.raw[:read.value] if ok else None


def scan(pid, pats, min_size=1 << 16, max_region=256 << 20):
    h = open_proc(pid)
    found = []
    for base, size, state, prot in regions(h):
        if state != MEM_COMMIT or prot not in PAGE_READABLE:
            continue
        if size < min_size or size > max_region:
            continue
        data = read_mem(h, base, size)
        if not data:
            continue
        for p in pats:
            i = data.find(p)
            if i >= 0:
                found.append((base, size, p, base + i))
    return found


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    exe = "BH3.exe"
    if "--exe" in sys.argv:
        exe = sys.argv[sys.argv.index("--exe") + 1]
    pid = find_pid(exe)
    print("进程 %s pid=%s" % (exe, pid))
    if pid is None:
        sys.exit("游戏没在运行")

    if cmd == "scan":
        pats = [b"EntryImagePath", b"ChallengeMissionPanel", b"WorldMapCoverInfo"]
        if "--pat" in sys.argv:
            pats = [sys.argv[sys.argv.index("--pat") + 1].encode()]
        res = scan(pid, pats)
        print("命中 %d 处" % len(res))
        for base, size, p, at in res[:40]:
            print("  区域 base=0x%X size=0x%X  %s @0x%X" % (base, size, p.decode(), at))
    elif cmd == "heaps":
        mn = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else (1 << 20)
        h = open_proc(pid)
        tot = 0
        for base, size, state, prot in regions(h):
            if state == MEM_COMMIT and prot in PAGE_READABLE and size >= mn:
                print("  0x%012X size=0x%-9X prot=0x%X" % (base, size, prot))
                tot += size
        print("合计 %.1f MB" % (tot / 1048576))
    elif cmd == "dump":
        base = int(sys.argv[2], 16)
        size = int(sys.argv[3], 16)
        out = sys.argv[sys.argv.index("-o") + 1] if "-o" in sys.argv else "mem.bin"
        h = open_proc(pid)
        data = read_mem(h, base, size)
        if data is None:
            sys.exit("读取失败")
        open(out, "wb").write(data)
        print("[+] 写出 %s %d B" % (out, len(data)))
