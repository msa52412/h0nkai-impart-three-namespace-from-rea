# -*- coding: utf-8 -*-
"""owmod —— 不挂钩、直接从静态单例取 OWEndlessModule 实例

依据：MonoWorldMapEndlessEntry.get_module (RVA 0x1A92080) 是标准 il2cpp 静态字段链，
      且 rcx 进来就被覆盖，可以传 0 调用。

只读（getter，无副作用）。
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall  # noqa: E402

RVA_GET_MODULE = 0x1A92080
RVA_GOTO = 0x19C5E00          # OWEndlessModule.GoToOWEndless


def get_module(h, base):
    st = icall.load_state()
    mb = st["mailbox"]
    if icall.cmd_call(base + RVA_GET_MODULE, [0], 5.0) != 0:
        return None
    raw = icall.read_mem(h, mb + 0x30, 8)
    return struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else None


def class_name(h, klass_va):
    """Il2CppClass: +0x10 = name (const char*)"""
    p = icall.read_mem(h, klass_va + 0x10, 8)
    if not p:
        return None
    s = icall.read_mem(h, struct.unpack("<Q", p)[0], 96)
    if not s:
        return None
    e = s.find(b"\x00")
    try:
        return s[:e if e > 0 else 96].decode("utf-8", "replace")
    except Exception:
        return None


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "show"
    h, pid, base = icall.open_game()
    if not h:
        return 1
    try:
        print("pid=%d  base=%#x" % (pid, base))
        v = get_module(h, base)
        if not v:
            print("✗ get_module 返回 0")
            return 1
        print("OWEndlessModule = %#x" % v)
        k = struct.unpack("<Q", icall.read_mem(h, v, 8))[0]
        print("  [this] klass = %#x" % k)
        st = icall.load_state()
        if icall.cmd_call(base + 0x189DC90, [v], 5.0) == 0:
            g = struct.unpack("<Q", icall.read_mem(h, st["mailbox"] + 0x30, 8))[0]
            if g:
                print("  get_Group: GroupId=%s GroupLevel=%s CurTop=%s"
                      % (struct.unpack("<i", icall.read_mem(h, g + 0x20, 4))[0],
                         struct.unpack("<i", icall.read_mem(h, g + 0x24, 4))[0],
                         struct.unpack("<i", icall.read_mem(h, g + 0x28, 4))[0]))
        if mode != "goto":
            return 0
        print("\n④ call GoToOWEndless(%#x) ..." % (base + RVA_GOTO))
        print("   预期：出现加载轮，随后进入迪拉克之海界面")
        return icall.cmd_call(base + RVA_GOTO, [v], 15.0)
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main() or 0)
