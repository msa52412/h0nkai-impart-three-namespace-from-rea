"""
BH3 客户端进程内存扫描器 —— 验证「运行时 metadata 解密」假说的工具。

原理
----
global-metadata.dat 的 identifier 表在磁盘上被加密（MHY0，非 XOR），
但 IL2CPP 运行时启动时必须把它解密到内存里才能工作。
只要客户端跑起来，明文的类名（UltraEndlessPreparePageContext 等）
必然出现在进程内存中 —— 那一刻就是我们的窗口。

用法（都是我先跑，不用用户操作）：
    python mem_scan.py                     # 自动找 BH3.exe 进程并扫描
    python mem_scan.py --pid 12345         # 指定 PID
    python mem_scan.py --name Server        # 扫别的进程（测试用）
    python mem_scan.py --pattern foo       # 追加自定义 pattern（测试用）
    python mem_scan.py dump                 # 扫描 + 把命中区域 dump 到 memdump/

只读操作：OpenProcess(PROCESS_VM_READ) + ReadProcessMemory，不写入、不注入。
"""
import ctypes
import ctypes.wintypes as wt
import os
import sys
import time

# ---------------------------------------------------------------- Win32 样板
k32 = ctypes.WinDLL('kernel32', use_last_error=True)

TH32CS_SNAPPROCESS = 0x2
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

MEM_COMMIT = 0x1000
PAGE_NOACCESS = 0x01
PAGE_GUARD = 0x100
MEM_PRIVATE = 0x20000
MEM_MAPPED = 0x40000
MEM_IMAGE = 0x1000000
READABLE = {0x02, 0x04, 0x08, 0x20, 0x40, 0x80}  # RO/RW/WC/XR/XRW/XWC


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ('dwSize', wt.DWORD), ('cntUsage', wt.DWORD),
        ('th32ProcessID', wt.DWORD), ('th32DefaultHeapID', ctypes.POINTER(wt.ULONG)),
        ('th32ModuleID', wt.DWORD), ('cntThreads', wt.DWORD),
        ('th32ParentProcessID', wt.DWORD), ('pcPriClassBase', wt.LONG),
        ('dwFlags', wt.DWORD), ('szExeFile', wt.WCHAR * 260),
    ]


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('BaseAddress', ctypes.c_void_p), ('AllocationBase', ctypes.c_void_p),
        ('AllocationProtect', wt.DWORD), ('RegionSize', ctypes.c_size_t),
        ('State', wt.DWORD), ('Protect', wt.DWORD), ('Type', wt.DWORD),
    ]


def list_pids(name_substr):
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    pe = PROCESSENTRY32W()
    pe.dwSize = ctypes.sizeof(pe)
    out = []
    if k32.Process32FirstW(snap, ctypes.byref(pe)):
        while True:
            nm = pe.szExeFile
            if name_substr.lower() in nm.lower():
                out.append((pe.th32ProcessID, nm))
            if not k32.Process32NextW(snap, ctypes.byref(pe)):
                break
    k32.CloseHandle(snap)
    return out


# ---------------------------------------------------------------- 扫描主体
PATTERNS = {
    # IL2CPP 标准 metadata 魔数（0xFAB11BAF 的小端字节序）
    'std_magic': b'\xaf\x1b\xb1\xfa',
    # miHoYo 加密魔数（磁盘形态，未解密副本长这样）
    'mhy_magic': b'MHY\x00',
    # ===== 类名探针：磁盘上全是 0 命中，内存里若出现 = 解密实锤 =====
    'UltraEndlessPreparePageContext': b'UltraEndlessPreparePageContext',
    'OpenworldPreparePageContext': b'OpenworldPreparePageContext',
    'GetMainDataRsp': b'GetMainDataRsp',
    'LevelLockConfig/UI侧': b'PlayerLevelLock',
    # ===== 任何 IL2CPP 程序必有的高频标识符 =====
    'MonoBehaviour': b'MonoBehaviour',
    'MoveNext': b'MoveNext',
    # ===== 运行时痕迹 =====
    'il2cpp': b'il2cpp',
    'global-metadata': b'global-metadata',
}

DUMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'memdump')
MAX_DUMP_REGION = 256 * 1024 * 1024  # 单区域最大 dump 256MB


def scan(pid, extra_patterns=(), do_dump=False, only_private_image=True):
    hits = {k: [] for k in PATTERNS}
    counts = {k: 0 for k in PATTERNS}
    for p in extra_patterns:
        hits[p] = []
        counts[p] = 0

    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h:
        raise OSError('OpenProcess 失败 err=%d（权限不够？用管理员跑）' % ctypes.get_last_error())

    mbi = MEMORY_BASIC_INFORMATION()
    addr = 0
    scanned_bytes = 0
    last_progress = 0
    dumped_regions = 0
    t0 = time.time()
    CHUNK = 32 * 1024 * 1024

    while addr < 0x7FFFFFFFFFFF:
        if k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi),
                               ctypes.sizeof(mbi)) == 0:
            break
        size = mbi.RegionSize
        base = mbi.BaseAddress or addr
        nxt = base + size

        ok_state = (mbi.State == MEM_COMMIT)
        ok_prot = (mbi.Protect & 0xFF) in READABLE and not (mbi.Protect & PAGE_GUARD)
        ok_type = (not only_private_image) or (mbi.Type in (MEM_PRIVATE, MEM_IMAGE))

        if ok_state and ok_prot and ok_type and size > 0:
            buf = ctypes.create_string_buffer(min(size, CHUNK))
            read_total = 0
            region_hit = False
            while read_total < size:
                want = min(size - read_total, CHUNK)
                nread = ctypes.c_size_t(0)
                if k32.ReadProcessMemory(h, ctypes.c_void_p(base + read_total),
                                         buf, want, ctypes.byref(nread)) and nread.value:
                    data = buf.raw[:nread.value]
                    scanned_bytes += nread.value
                    for name, pat in PATTERNS.items():
                        i = data.find(pat)
                        while i >= 0:
                            counts[name] += 1
                            if len(hits[name]) < 24:
                                hits[name].append(base + read_total + i)
                            region_hit = True
                            if counts[name] > 20000:
                                break
                            i = data.find(pat, i + 1)
                    for p in extra_patterns:
                        i = data.find(p)
                        while i >= 0:
                            counts[p] += 1
                            if len(hits[p]) < 24:
                                hits[p].append(base + read_total + i)
                            region_hit = True
                            i = data.find(p, i + 1)
                    read_total += nread.value
                    if read_total >= size:
                        break
                else:
                    break

            if do_dump and region_hit and size <= MAX_DUMP_REGION:
                os.makedirs(DUMP_DIR, exist_ok=True)
                fn = os.path.join(DUMP_DIR, '%016x_%x.bin' % (base, size))
                if not os.path.exists(fn):
                    with open(fn, 'wb') as f:
                        off = 0
                        while off < size:
                            want = min(size - off, CHUNK)
                            nb = ctypes.create_string_buffer(want)
                            n2 = ctypes.c_size_t(0)
                            if k32.ReadProcessMemory(h, ctypes.c_void_p(base + off),
                                                     nb, want, ctypes.byref(n2)) and n2.value:
                                f.write(nb.raw[:n2.value])
                                off += n2.value
                            else:
                                # 读不动就填零保持偏移
                                f.write(b'\x00' * want)
                                off += want
                    dumped_regions += 1

        if scanned_bytes - last_progress >= 256 * 1024 * 1024:
            last_progress = scanned_bytes
            print('  ... 已扫 %.2f GB（%.0fs）' %
                  (scanned_bytes / 1e9, time.time() - t0), flush=True)
        addr = nxt

    k32.CloseHandle(h)
    return hits, counts, scanned_bytes, dumped_regions, time.time() - t0


def main():
    args = sys.argv[1:]
    do_dump = 'dump' in args
    pid = None
    name = 'BH3'
    extra = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--pid':
            pid = int(args[i + 1]); i += 2
        elif a == '--name':
            name = args[i + 1]; i += 2
        elif a == '--pattern':
            extra.append(args[i + 1].encode()); i += 2
        else:
            i += 1

    if pid is None:
        cands = list_pids(name)
        if not cands:
            print('没找到名字含 "%s" 的进程。当前相关进程：' % name)
            for p, n in list_pids(''):
                if any(k in n.lower() for k in ('bh3', 'server', 'unity', 'game')):
                    print('   pid=%-7d %s' % (p, n))
            sys.exit(1)
        if len(cands) > 1:
            print('多个候选进程，请用 --pid 指定：')
            for p, n in cands:
                print('   pid=%-7d %s' % (p, n))
            sys.exit(1)
        pid, pname = cands[0]
    else:
        pname = '?'

    print('目标进程 pid=%d (%s)  dump=%s' % (pid, pname, '开' if do_dump else '关'))
    print('patterns=%d 个探针，只读扫描，开始...\n' % len(PATTERNS))

    hits, counts, total, dumped, secs = scan(pid, extra, do_dump)

    print('\n================ 扫描结果（%.2f GB / %.0f 秒）================' % (total / 1e9, secs))
    print('%-38s %8s  %s' % ('探针', '命中数', '前几个地址'))
    for name_, cnt in sorted(counts.items(), key=lambda x: -x[1]):
        addrs = ', '.join('0x%X' % a for a in hits[name_][:4])
        print('%-38s %8d  %s' % (name_, cnt, addrs))

    print('\n判定：')
    key = 'UltraEndlessPreparePageContext'
    if counts.get(key, 0) > 0:
        print('  [实锤] 类名在内存中是明文 —— identifier 表运行时解密，'
              '「内存 dump metadata」路线成立！')
    elif counts.get('std_magic', 0) > 0:
        print('  [强信号] 标准 IL2CPP 魔数出现在内存 —— 找到解密后的 metadata 块。')
    else:
        print('  [未证实] 没扫到类名明文 —— 可能客户端没进到加载 metadata 的阶段，'
              '或运行时只解密了部分。让客户端跑到主界面再扫一次。')
    if dumped:
        print('  已 dump %d 个命中区域 -> %s' % (dumped, DUMP_DIR))


if __name__ == '__main__':
    main()
