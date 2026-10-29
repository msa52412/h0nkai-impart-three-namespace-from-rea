# -*- coding: utf-8 -*-
"""check_stub —— 离线校验信箱 stub 的结构与跳转落点（不需要游戏在跑）

验四件事：
  1. 反汇编出来正好是指定序列，没有踩到非法指令
  2. jne 落在「原始 14 字节副本」的第一个字节
  3. jz  落在「bail: done=2」那一句
  4. jmp [rip] 的 8 字节目标 == resume_va

跑法： python check_stub.py
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402
import capstone  # noqa: E402

MB = 0x006A0000
HOST = 0x18021D2550
RESUME = HOST + 14
ORIG = bytes.fromhex("40534883ec20488bd9b9822201 00".replace(" ", ""))

stub = icall.build_stub(MB, RESUME, ORIG)
base = 0x7FF600000000          # 任意可执行映射基址，只为算绝对地址

md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True

print("stub 长度 = %d 字节（旧版 75，两道闸版 109）" % len(stub))
print("hex: %s" % stub.hex(" "))
print()

insns = list(md.disasm(stub, base))
pos = 0
for ins in insns:
    off = ins.address - base
    mark = ""
    if ins.mnemonic.startswith("j"):
        tgt = ins.operands[0].imm if ins.operands and ins.operands[0].type == capstone.x86.X86_OP_IMM else None
        if tgt is not None:
            mark = "   → +%#x" % (tgt - base)
    print("  +%#04x  %-24s %-8s %s%s" % (
        off, ins.bytes.hex(" "), ins.mnemonic, ins.op_str, mark))
    pos = off + ins.size

print()
ok = True


def check(name, cond, extra=""):
    global ok
    print(("  ✓ " if cond else "  ✗ ") + name + (("  " + extra) if extra else ""))
    ok = ok and cond


# 定位关键偏移
orig_pos = None
bail_pos = None
restore_pos = None
jne_t = jz_t = jmp_t = None
for ins in insns:
    off = ins.address - base
    if ins.mnemonic == "jne" and jne_t is None:
        jne_t = ins.operands[0].imm - base
    if ins.mnemonic in ("je", "jz") and jz_t is None:
        jz_t = ins.operands[0].imm - base
    if ins.mnemonic == "jmp" and off < len(stub) - 20:
        jmp_t = ins.operands[0].imm - base
    if ins.mnemonic == "mov" and ins.op_str == "byte ptr [rbx + 1], 2":
        bail_pos = off
    if ins.mnemonic == "mov" and ins.op_str == "byte ptr [rbx + 1], 1":
        normal_done = off

# 原始字节副本位置：stub 里找 ORIG
orig_pos = stub.find(ORIG)
print("关键位置：")
print("  orig 副本 +%#x   bail +%#x   jne→+%#x   jz→+%#x   jmp→+%#x" % (
    orig_pos, bail_pos or 0, jne_t or 0, jz_t or 0, jmp_t or 0))
print()

check("orig 副本位置有效", orig_pos > 0, "+%#x" % orig_pos)
check("jne 落在 orig 副本首字节", jne_t == orig_pos, "%#x vs %#x" % (jne_t, orig_pos))
check("jz 落在 bail(done=2)", jz_t == bail_pos, "%#x vs %#x" % (jz_t, bail_pos))
check("jmp 跳过 bail 落到 add rsp,0x20", jmp_t is not None and jmp_t > (bail_pos or 0),
      "+%#x" % (jmp_t or 0))
# add rsp,0x20 的位置
add_pos = None
for ins in insns:
    if ins.mnemonic == "add" and ins.op_str == "rsp, 0x20":
        add_pos = ins.address - base
check("jmp 精确落在 restore(add rsp,0x20)", jmp_t == add_pos, "%#x vs %#x" % (jmp_t, add_pos))

# 尾部跳回
tail = stub[-14:]
check("尾部是 FF 25 00 00 00 00", tail[:6] == bytes.fromhex("ff2500000000"))
check("跳回地址 == resume_va", struct.unpack("<Q", tail[6:])[0] == RESUME,
      "%#x" % struct.unpack("<Q", tail[6:])[0])

# 魔数 / rel8 的位置从反汇编里动态取，不要硬编码偏移（stub 一改就错位）
cmp_off = jne_off = je_off = None
for ins in insns:
    off = ins.address - base
    if ins.mnemonic == "cmp" and "0xa5" in ins.op_str and cmp_off is None:
        cmp_off = off
    if ins.mnemonic == "jne" and jne_off is None:
        jne_off = off
    if ins.mnemonic in ("je", "jz") and je_off is None:
        je_off = off

check("魔数 0xA5 已写入 cmp 立即数", cmp_off is not None and stub[cmp_off + 3] == 0xA5,
      "%02x @+%#x" % (stub[cmp_off + 3], cmp_off + 3) if cmp_off is not None else "找不到 cmp")
check("jne rel8 为正（只能向前跳）", jne_off is not None and 0 < stub[jne_off + 1] <= 127,
      "%d" % stub[jne_off + 1] if jne_off is not None else "找不到 jne")
check("je  rel8 为正（只能向前跳）", je_off is not None and 0 < stub[je_off + 1] <= 127,
      "%d" % stub[je_off + 1] if je_off is not None else "找不到 je")
# 反汇编必须恰好消费完（不允许有残字节被当数据）
check("反汇编覆盖完整 stub", pos == len(stub), "%d/%d" % (pos, len(stub)))

print()
print("结论：%s" % ("结构正确，可以安装" if ok else "有问题，不要安装"))
sys.exit(0 if ok else 1)
