# -*- coding: utf-8 -*-
"""
ctable 采集器 v3 —— 两阶段设计（手动运行）

为什么改设计
------------
v2 一次性落盘整段内存，有两个盲区：
  1) 「体量接近 ctable」的区只取前 6 个，真正目标可能排在第 7 位之后；
  2) 跳过 >1GB 的区，而解密缓冲可能就在大堆里。

v3 改成两阶段：
  阶段一  --index     只读每个内存区的前 512 字节 + 统计量，写一个小 jsonl。
                      全部区扫完通常只有几 MB，跑完把这个文件发我。
  阶段二  --dump-base 我根据索引挑出候选，给你一个地址，你只抓那一段。

这样既不盲扫几个 GB，也不会漏。

重要
----
**请先在游戏里打开「挑战」面板（世界地图 → 挑战）**，让 WorldMap 配置真正被读进内存，
然后再运行本脚本。配置是按需加载的，停在主界面时它可能根本不在内存里。

用法
----
    # 阶段一：抓索引（推荐，先跑这个）
    python ctable_hunt2.py --index

    # 阶段二：定点抓取（地址由索引分析得出）
    python ctable_hunt2.py --dump-base 0x206FE000
    python ctable_hunt2.py --dump-base 0x206FE000 --dump-size 30000000

    # 辅助：直接把体量接近 ctable 的区全抓下来（不设 6 个上限）
    python ctable_hunt2.py --near-size

    # 只想看统计不落盘
    python ctable_hunt2.py --index --dry

注意：只读内存，不写、不注入、不改游戏文件。
"""
import sys, os, json, time, math, ctypes, collections
import ctypes.wintypes as wt

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dump2")

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = wt.HANDLE
k32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
k32.VirtualQueryEx.restype = ctypes.c_size_t
k32.VirtualQueryEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
k32.ReadProcessMemory.restype = wt.BOOL
k32.ReadProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                                  ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
MEM_MAPPED = 0x40000
MEM_IMAGE = 0x1000000
PAGE_GUARD = 0x100
READABLE = (0x02, 0x04, 0x20, 0x40)
HEAD = 512

CTABLE = r"D:\BH3\7.0\BH3_Data\StreamingAssets\ctable.dat"
CTABLE_SIZE = os.path.getsize(CTABLE) if os.path.exists(CTABLE) else 28160000

# 在头部里找的特征串
MARKERS = [
    b"UnityFS", b"CAB-", b"ExcelOutputAsset", b"_ExcelOutputAsset",
    b"CombinedBytes", b"WorldMap", b"SpriteOutput", b"DataImpl",
    b"MHY", b"2017.4.18f1", b"PK\x03\x04",
]


class MBI64(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_ulonglong),
        ("AllocationBase", ctypes.c_ulonglong),
        ("AllocationProtect", wt.DWORD),
        ("__a1", wt.DWORD),
        ("RegionSize", ctypes.c_ulonglong),
        ("State", wt.DWORD),
        ("Protect", wt.DWORD),
        ("Type", wt.DWORD),
        ("__a2", wt.DWORD),
    ]


def find_pid(exe="BH3.exe"):
    import subprocess
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq " + exe, "/FO", "CSV", "/NH"],
                             capture_output=True, text=True, encoding="gbk",
                             errors="replace").stdout
    except Exception as e:
        print("tasklist 失败:", e)
        return None
    for line in out.splitlines():
        parts = [p.strip().strip('"') for p in line.split(",")]
        if len(parts) >= 2 and parts[0].lower() == exe.lower():
            try:
                return int(parts[1])
            except ValueError:
                pass
    return None


def open_proc(pid):
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h:
        err = ctypes.get_last_error()
        print("!! OpenProcess 失败 GetLastError=%d" % err)
        if err == 5:
            print("   权限不足，请用管理员身份打开命令行再运行。")
        else:
            print("   可能是反作弊拦截。")
        return None
    return h


def iter_regions(h):
    addr = 0
    mbi = MBI64()
    while addr < 0x7FFFFFFFFFFF:
        got = k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi),
                                 ctypes.sizeof(mbi))
        if not got:
            break
        yield (mbi.BaseAddress, mbi.RegionSize, mbi.State, mbi.Protect, mbi.Type)
        nxt = mbi.BaseAddress + mbi.RegionSize
        if nxt <= addr:
            break
        addr = nxt


def read_mem(h, base, size):
    buf = ctypes.create_string_buffer(size)
    got = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(h, ctypes.c_void_p(base), buf, size, ctypes.byref(got))
    if not ok or got.value == 0:
        return None
    return buf.raw[:got.value]


def entropy(b):
    if not b:
        return 0.0
    c = collections.Counter(b)
    n = len(b)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def do_index(h, dry=False):
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "index.jsonl")
    f = None if dry else open(path, "w", encoding="utf-8")
    t0 = time.time()
    n = 0
    rows = []
    for base, size, state, prot, typ in iter_regions(h):
        if state != MEM_COMMIT or prot not in READABLE or (prot & PAGE_GUARD):
            continue
        if size < 4096:
            continue
        head = read_mem(h, base, min(HEAD, size))
        if not head:
            continue
        n += 1
        ent = entropy(head)
        txt = "".join(chr(c) if 32 <= c < 127 else "." for c in head[:48])
        hits = [m.decode("latin1") for m in MARKERS if m in head]
        rec = {"base": base, "size": size, "prot": prot, "type": typ,
               "ent": round(ent, 3), "hits": hits,
               "hex": head[:64].hex(), "txt": txt}
        rows.append(rec)
        if f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if n % 500 == 0:
            print("  ...已索引 %d 区, 用时 %.0fs" % (n, time.time() - t0), flush=True)
    if f:
        f.close()

    print("\n共索引 %d 个可读区, 用时 %.1fs" % (n, time.time() - t0))
    if dry:
        print("(--dry，未落盘)")
        return

    # 摘要：按大小排序的前 30 个，以及头部是 ASCII 的（容器头候选）
    print("\n--- 体量最大的 20 个区 ---")
    print("%-18s %-12s %-8s %-6s %s" % ("基址", "大小", "类型", "熵", "头部/命中"))
    for r in sorted(rows, key=lambda x: -x["size"])[:20]:
        print("0x%-16X %-12s %-8d %-6.2f %s %s"
              % (r["base"], "%.1fMB" % (r["size"] / 1048576), r["type"], r["ent"],
                 ",".join(r["hits"]) or "", r["txt"][:32]))

    print("\n--- 体量接近 ctable(%d) 的区 ---" % CTABLE_SIZE)
    near = [r for r in rows if CTABLE_SIZE * 0.5 <= r["size"] <= CTABLE_SIZE * 1.6]
    for r in sorted(near, key=lambda x: -x["size"]):
        print("0x%-16X %-12s %-6.2f %s %s"
              % (r["base"], "%.2fMB" % (r["size"] / 1048576), r["ent"],
                 ",".join(r["hits"]) or "", r["txt"][:32]))
    print("  共 %d 个" % len(near))

    print("\n--- 头部像文本的区（容器头候选，熵 < 6.5 且前 16 字节可打印）---")
    cand = [r for r in rows
            if r["ent"] < 6.5 and sum(1 for c in bytes.fromhex(r["hex"])[:16] if 32 <= c < 127) >= 12]
    for r in sorted(cand, key=lambda x: -x["size"])[:20]:
        print("0x%-16X %-12s %-6.2f %s" % (r["base"], "%.1fMB" % (r["size"] / 1048576),
                                           r["ent"], r["txt"][:40]))
    print("  共 %d 个" % len(cand))

    print("\n[+] 索引已写入 %s" % path)
    print("    把这个文件发我，我筛出候选地址后给你 --dump-base 的命令。")


def do_dump(h, base, size=None, limit=200 << 20):
    os.makedirs(OUTDIR, exist_ok=True)
    if size is None:
        size = None
        for b, s, st, pr, ty in iter_regions(h):
            if b == base:
                size = s
                break
        if size is None:
            print("!! 找不到基址 0x%X 的区" % base)
            return
    if size > limit:
        print("[!] 区大小 %.0fMB 超过上限，只抓前 %.0fMB"
              % (size / 1048576, limit / 1048576))
        size = limit
    data = read_mem(h, base, size)
    if not data:
        print("!! 读取失败")
        return
    p = os.path.join(OUTDIR, "reg_%X_%dMB.bin" % (base, len(data) >> 20))
    open(p, "wb").write(data)
    print("[+] %s (%d B, %.1f MB)" % (p, len(data), len(data) / 1048576))


def do_near(h):
    os.makedirs(OUTDIR, exist_ok=True)
    lo, hi = CTABLE_SIZE * 0.5, CTABLE_SIZE * 1.6
    got = 0
    for base, size, state, prot, typ in iter_regions(h):
        if state != MEM_COMMIT or prot not in READABLE or (prot & PAGE_GUARD):
            continue
        if not (lo <= size <= hi):
            continue
        if size > (256 << 20):
            continue
        data = read_mem(h, base, size)
        if not data:
            continue
        p = os.path.join(OUTDIR, "near_%X_%dMB.bin" % (base, len(data) >> 20))
        open(p, "wb").write(data)
        got += 1
        print("[+] %s (%.1f MB)" % (p, len(data) / 1048576))
    print("共抓 %d 个" % got)


def main():
    a = sys.argv[1:]
    pid = int(a[a.index("--pid") + 1]) if "--pid" in a else None
    exe = a[a.index("--exe") + 1] if "--exe" in a else "BH3.exe"
    if pid is None:
        pid = find_pid(exe)
    if pid is None:
        print("没找到进程 %s。请先启动游戏，并打开「挑战」面板。" % exe)
        return
    print("目标 pid=%d  ctable=%d B" % (pid, CTABLE_SIZE))
    h = open_proc(pid)
    if not h:
        return

    if "--index" in a:
        do_index(h, dry="--dry" in a)
    elif "--dump-base" in a:
        base = int(a[a.index("--dump-base") + 1], 0)
        size = int(a[a.index("--dump-size") + 1], 0) if "--dump-size" in a else None
        do_dump(h, base, size)
    elif "--near-size" in a:
        do_near(h)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
