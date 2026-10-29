# -*- coding: utf-8 -*-
"""
ctable 明文猎手 v2 —— 手动运行版

背景
----
崩坏3 的配置表打包在 BH3_Data/StreamingAssets/ctable.dat（28,160,000 字节，全密文）。
加载器在 UnityPlayer.dll 里（函数 0x180D558E0，解密调用 0x180D559D0 -> 0x1800E0070），
代码被控制流平坦化，静态逆向代价高。

但游戏启动后，解密后的配置必然出现在进程内存里。本脚本只做三件事：
  1) 打开 BH3.exe 进程，枚举可读内存区
  2) 用「只有配置表里才有的字符串」当指纹，给每个内存区打分
  3) 把命中区整段落盘到 dump/ 目录，并记下每个指纹的偏移

指纹分两档：
  STRONG —— 贴图资源路径，只可能出现在 WorldMap.json 里，命中即铁证
  WEAK   —— 表名，代码里也可能出现，仅作辅助打分

拿到 dump 后配合 ctable_crack.py 就能反推密钥流，
之后改配置、重新加密、写回 ctable.dat，全程不需要密钥。

本次目标
--------
WorldMap.json 里 EntryID 1006（挑战面板 Task_6，当前指向"悬赏委托"）
    FeatureType      [114]  ->  [108]      (108 = 迪拉克之海 / OWEndless)
    EntryImagePath   event/Immediately/newbie37/entrance_truecolor
                     ->  SpriteOutput/WorldMap/OWEndless/Cover_11
    ContentIDList    [30130..30136]  ->  []
即把 EntryID 1006 整行改造成 EntryID 1012 的样子。

用法
----
    python ctable_hunt.py                 # 扫描并落盘（推荐）
    python ctable_hunt.py --scan-only     # 只打印候选，不落盘
    python ctable_hunt.py --pid 1234      # 指定 pid
    python ctable_hunt.py --all-big       # 额外落盘所有 >=8MB 的内存区

注意：脚本只读内存，不写、不注入、不改游戏文件。
"""
import sys, os, json, time, ctypes
import ctypes.wintypes as wt

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dump")

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = wt.HANDLE
k32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
k32.VirtualQueryEx.restype = ctypes.c_size_t
k32.VirtualQueryEx.argtypes = [wt.HANDLE, ctypes.c_void_p,
                               ctypes.c_void_p, ctypes.c_size_t]
k32.ReadProcessMemory.restype = wt.BOOL
k32.ReadProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                                  ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_GUARD = 0x100
READABLE = (0x02, 0x04, 0x20, 0x40)
MAX_DUMP = 192 << 20          # 单区落盘上限 192MB

# ---- 铁证级指纹：WorldMap.json 独有的贴图路径 ----
STRONG = [
    b"SpriteOutput/WorldMap/OWEndless/Cover_11",   # 迪拉克之海 入口图标
    b"SpriteOutput/WorldMap/Entry/MutilTask_1",    # 记忆战场 (EntryID 1004)
    b"SpriteOutput/WorldMap/Entry/MutilTask_2",    # EntryID 1011
    b"SpriteOutput/WorldMap/Entry/Extra_1",        # EntryID 1003
    b"SpriteOutput/WorldMap/Entry/OWTask_1",       # EntryID 1001
    b"SpriteOutput/WorldMap/Entry/Cover_4",        # EntryID 1008
    b"SpriteOutput/WorldMap/Entry/Regular_1_100",  # EntryID 1009
    b"event/Immediately/newbie37/entrance_truecolor",  # EntryID 1006 当前图标
    b"SpriteOutput/WorldMap/Entry/Avatar_Tutorial_Image",  # EntryID 1013
]

# ---- 辅助指纹：表名 ----
WEAK = [
    b"ExcelOutputAsset", b"WorldMapCoverInfo", b"ChallengeMissionLink",
    b"ChallengeMissionPanel", b"OWEndlessSchedule", b"UltraEndlessSite",
    b"MissionData", b"AvatarData", b"StageData", b"OpenWorldMap",
    b"GachaData", b"StigmataData", b"WeaponData", b"WorldMap",
]

CTABLE = r"D:\BH3\7.0\BH3_Data\StreamingAssets\ctable.dat"
CTABLE_SIZE = os.path.getsize(CTABLE) if os.path.exists(CTABLE) else 28160000


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
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq " + exe,
                              "/FO", "CSV", "/NH"],
                             capture_output=True, text=True,
                             encoding="gbk", errors="replace").stdout
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
        print("!! OpenProcess 失败, GetLastError = %d" % err)
        if err == 5:
            print("   权限不足。请用管理员身份打开命令行再运行本脚本。")
        elif err == 87:
            print("   pid 无效。")
        else:
            print("   可能是反作弊拦截。可尝试管理员运行，或先退出杀软再试。")
        return None
    return h


def iter_regions(h):
    addr = 0
    mbi = MBI64()
    while addr < 0x7FFFFFFFFFFF:
        got = k32.VirtualQueryEx(h, ctypes.c_void_p(addr),
                                 ctypes.byref(mbi), ctypes.sizeof(mbi))
        if not got:
            break
        yield (mbi.BaseAddress, mbi.RegionSize, mbi.State, mbi.Protect)
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


def main():
    args = sys.argv[1:]
    scan_only = "--scan-only" in args
    all_big = "--all-big" in args
    pid = None
    if "--pid" in args:
        pid = int(args[args.index("--pid") + 1])
    exe = "BH3.exe"
    if "--exe" in args:
        exe = args[args.index("--exe") + 1]

    if pid is None:
        pid = find_pid(exe)
    if pid is None:
        print("没找到进程 %s。请先把游戏启动到主界面（进到世界地图更好），再运行。" % exe)
        return

    print("目标进程 %s  pid=%d" % (exe, pid))
    print("ctable.dat = %d 字节" % CTABLE_SIZE)
    h = open_proc(pid)
    if not h:
        return

    os.makedirs(OUTDIR, exist_ok=True)
    t0 = time.time()
    cands = []      # (score, strong_n, base, size, detail)
    big = []
    nreg = 0
    total = 0

    for base, size, state, prot in iter_regions(h):
        if state != MEM_COMMIT:
            continue
        if prot not in READABLE or (prot & PAGE_GUARD):
            continue
        if size < (64 << 10) or size > (1 << 30):
            continue
        nreg += 1
        data = read_mem(h, base, size)
        if not data:
            continue
        total += len(data)

        detail = []
        for m in STRONG:
            off = data.find(m)
            if off >= 0:
                detail.append((m.decode("utf-8", "replace"), off))
        weak_n = sum(1 for m in WEAK if m in data)

        if detail or weak_n:
            # 打分：强指纹权重 10，弱指纹权重 1
            score = len(detail) * 10 + weak_n
            cands.append((score, len(detail), base, size, detail, weak_n))
        if all_big and size >= (8 << 20):
            big.append((base, size))
        if nreg % 200 == 0:
            print("  ...已扫 %d 区, 读入 %.0f MB, 候选 %d, 用时 %.0fs"
                  % (nreg, total / 1048576, len(cands), time.time() - t0), flush=True)

    print("\n扫描完成: %d 个可读区, 读入 %.0f MB, 用时 %.1fs"
          % (nreg, total / 1048576, time.time() - t0))
    print("有指纹命中的区: %d 个" % len(cands))

    cands.sort(key=lambda x: (-x[0], -x[3]))
    print("\n%-5s %-6s %-18s %-10s %s" % ("分", "铁证", "基址", "大小", "命中"))
    for score, sn, base, size, detail, wn in cands[:25]:
        tag = ",".join(os.path.basename(d[0]) for d in detail[:4]) or ("弱命中x%d" % wn)
        print("%-5d %-6d 0x%-16X %-10s %s"
              % (score, sn, base, "%.1fMB" % (size / 1048576), tag))

    if not any(c[1] for c in cands):
        print("\n[!] 没有任何铁证级命中 —— 说明明文配置不在常驻内存里（可能是流式解密）。")
        print("    这种情况下 --all-big 也意义不大，请把上面的弱命中列表发我，我们换思路。")

    if scan_only:
        print("\n(--scan-only 模式，未落盘)")
        return

    manifest = {"pid": pid, "ctable_size": CTABLE_SIZE,
                "time": time.strftime("%Y-%m-%d %H:%M:%S"), "dumps": []}

    # 1) 落盘有命中的区（按分数取前 10 个）
    for i, (score, sn, base, size, detail, wn) in enumerate(cands[:10]):
        if size > MAX_DUMP:
            print("[!] 跳过 0x%X (%.0fMB 超过落盘上限)" % (base, size / 1048576))
            continue
        data = read_mem(h, base, size)
        if not data:
            continue
        p = os.path.join(OUTDIR, "hit_%02d_%X_%dMB.bin" % (i, base, size >> 20))
        open(p, "wb").write(data)
        manifest["dumps"].append({
            "kind": "hit", "path": p, "base": base, "size": len(data),
            "score": score, "strong_hits": [{"s": d[0], "off": d[1]} for d in detail],
            "weak_hits": wn,
        })
        print("[+] %s  (%.1f MB, 铁证 %d)" % (p, len(data) / 1048576, sn))

    # 2) 落盘「配置体量级」的大区
    lo, hi = int(CTABLE_SIZE * 0.3), int(CTABLE_SIZE * 2.5)
    sized = list(big)
    if not sized:
        for base, size, state, prot in iter_regions(h):
            if state != MEM_COMMIT or prot not in READABLE or (prot & PAGE_GUARD):
                continue
            if lo <= size <= hi:
                sized.append((base, size))
    for i, (base, size) in enumerate(sized[:6]):
        if size > MAX_DUMP:
            continue
        data = read_mem(h, base, size)
        if not data:
            continue
        p = os.path.join(OUTDIR, "size_%02d_%X_%dMB.bin" % (i, base, size >> 20))
        open(p, "wb").write(data)
        manifest["dumps"].append({"kind": "size", "path": p, "base": base,
                                  "size": len(data)})
        print("[+] %s  (%.1f MB)" % (p, len(data) / 1048576))

    mp = os.path.join(OUTDIR, "manifest.json")
    json.dump(manifest, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n[+] %s" % mp)
    print("\n把整个 dump/ 目录发我即可。共 %d 个文件。" % len(manifest["dumps"]))


if __name__ == "__main__":
    main()
