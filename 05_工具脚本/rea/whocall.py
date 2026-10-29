# -*- coding: utf-8 -*-
"""whocall —— 抓「谁在调这个函数」

在函数入口放一个只读型 stub：把 `[rsp]`（返回地址）抄到一个槽里，
然后原样执行被覆盖的指令、跳回原处。不碰信箱、不挂 Update，风险面最小。

适合场景：某个函数被高频调用（比如卡在每帧重发的死循环里），
想知道是哪段代码在调它。

用法:
    python whocall.py 0x1AC59D0              # 盯 3 秒
    python whocall.py 0x1AC59D0 --seconds 6
    python whocall.py 0x1AC59D0 --keep       # 抓完不还原（一般不需要）
    python whocall.py --restore              # 手动还原入口
"""
import json
import os
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".whocall.json")
SYM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "addr2name.json")

_k32 = icall.k32


def build_ret_stub(slot_va, resume_va, orig):
    """mov r11,slot / mov rax,[rsp] / mov [r11],rax / <orig> / jmp resume

    只读写一个 8 字节槽，不压栈、不改 rsp，所以 rsp 相对寻址的原始指令照常生效。
    rax 是易失寄存器，函数入口处可随意用。
    """
    b = b""
    b += b"\x49\xBB" + struct.pack("<Q", slot_va)   # mov r11, slot
    b += b"\x48\x8B\x04\x24"                        # mov rax, [rsp]     返回地址
    b += b"\x49\x89\x03"                            # mov [r11], rax
    b += orig
    b += b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", resume_va)
    return b


def build_this_stub(slot_va, resume_va, orig):
    """mov r11,slot / mov [r11],rcx / <orig> / jmp resume

    抓 this（实例方法的 rcx）。不压栈、不改 rsp，原始指令照常生效。
    """
    b = b""
    b += b"\x49\xBB" + struct.pack("<Q", slot_va)   # mov r11, slot
    b += b"\x49\x89\x0B"                            # mov [r11], rcx
    b += orig
    b += b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", resume_va)
    return b


_names = None


def names():
    global _names
    if _names is None:
        raw = json.load(open(SYM, encoding="utf-8"))
        _names = sorted((int(k), v) for k, v in raw.items())
    return _names


def resolve(rva):
    """找 <= rva 的最近符号。"""
    n = names()
    lo, hi = 0, len(n) - 1
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        if n[mid][0] <= rva:
            best = n[mid]
            lo = mid + 1
        else:
            hi = mid - 1
    if not best:
        return "?", 0
    return best[1], rva - best[0]


def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except Exception:
            return None
    return None


def do_restore():
    st = load_state()
    if not st:
        print("没有 .whocall.json，无需还原")
        return 0
    h, pid, base = icall.open_game()
    if not h:
        return 1
    ok = icall.write_mem(h, base + st["rva"], bytes.fromhex(st["orig"]))
    _k32.CloseHandle(h)
    print(("✓ 已还原 RVA %#x" if ok else "✗ 还原失败 RVA %#x") % st["rva"])
    if ok:
        os.remove(STATE)
    return 0 if ok else 1


def main():
    args = sys.argv[1:]
    if "--restore" in args:
        return do_restore()
    if not args:
        print(__doc__)
        return 1
    rva = int(args[0], 0) & 0x0FFFFFFF
    seconds = 3.0
    if "--seconds" in args:
        seconds = float(args[args.index("--seconds") + 1])
    keep = "--keep" in args
    want_this = "--rcx" in args

    h, pid, base = icall.open_game()
    if not h:
        print("游戏未运行 / OpenProcess 失败（需要管理员）")
        return 1

    L = icall.insn_len_at(rva)
    orig = icall.file_bytes(rva, L)
    fn_va = base + rva
    cur = icall.read_mem(h, fn_va, L)
    if cur != orig:
        print("入口字节与文件不一致（%s vs %s），可能已被别的钩子占用，退出" % (
            cur.hex(" ") if cur else "读取失败", orig.hex(" ")))
        _k32.CloseHandle(h)
        return 1

    page = _k32.VirtualAllocEx(h, None, 0x2000, 0x3000, 0x40)
    if not page:
        print("VirtualAllocEx 失败")
        _k32.CloseHandle(h)
        return 1
    slot = page
    stub_va = page + 0x1000

    # 安全闸：原字节要原样搬到 stub 执行，块外的相对跳转/rip 寻址搬过去会跳错地址。
    # 2026-10-25 16:01 就是漏了这道检查，挂 raise_null_reference_exception 时崩了游戏。
    bad = icall.unsafe_replay(orig, fn_va, stub_va)
    if bad:
        print("✗ 该函数头不能安全挂钩（覆盖 %d 字节）：" % L)
        for b in bad:
            print("    " + b)
        print("  stub 与原函数相距太远，相对跳转无法原样搬运。入口未改动。")
        _k32.CloseHandle(h)
        return 1

    icall.write_mem(h, slot, b"\x00" * 8)
    stub = (build_this_stub if want_this else build_ret_stub)(slot, fn_va + L, orig)
    if not icall.write_mem(h, stub_va, stub):
        print("stub 写入失败")
        _k32.CloseHandle(h)
        return 1
    back = icall.read_mem(h, stub_va, len(stub))
    if back != stub:
        print("stub 落地校验失败，入口未改动")
        _k32.CloseHandle(h)
        return 1
    jmp = b"\xFF\x25\x00\x00\x00\x00" + struct.pack("<Q", stub_va)
    if not icall.write_mem(h, fn_va, jmp):
        print("入口写入失败")
        _k32.CloseHandle(h)
        return 1
    if icall.read_mem(h, fn_va, 6)[:6] != jmp[:6]:
        print("入口回读不符，回滚")
        icall.write_mem(h, fn_va, orig)
        _k32.CloseHandle(h)
        return 1

    print("已挂钩 RVA %#x（覆盖 %d 字节，原始 %s）" % (rva, L, orig.hex(" ")))
    print("  槽 %#x   stub %#x   捕获=%s" % (slot, stub_va, "rcx(this)" if want_this else "[rsp]返回地址"))
    print("  盯 %.0f 秒，收集不同的值…" % seconds)

    seen = {}
    t0 = time.time()
    try:
        while time.time() - t0 < seconds:
            raw = icall.read_mem(h, slot, 8)
            if raw and len(raw) == 8:
                v = struct.unpack("<Q", raw)[0]
                if v:
                    seen[v] = seen.get(v, 0) + 1
            time.sleep(0.05)
    finally:
        if not keep:
            icall.write_mem(h, fn_va, orig)
            print("已还原入口")
        else:
            json.dump({"rva": rva, "orig": orig.hex()}, open(STATE, "w"))
            print("保留了钩子，用完记得 python whocall.py --restore")
        _k32.CloseHandle(h)

    if not seen:
        print("没抓到任何调用（这段时间函数没被调用）")
        return 0

    print()
    if want_this:
        print("抓到 %d 个不同的 this：" % len(seen))
        for va, _ in sorted(seen.items(), key=lambda kv: -kv[1]):
            print("  this = %#x" % va)
        return 0

    print("抓到 %d 个不同的返回地址：" % len(seen))
    rows = sorted(seen.items(), key=lambda kv: -kv[1])
    for va, _ in rows:
        r = va - base
        name, off = resolve(r)
        print("  返回地址 %#x  (RVA %#x)  → %s + %#x" % (va, r, name, off))
    print()
    print("说明：上面第一行就是「直接调用者」所在的函数（+偏移是该调用点）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
