# -*- coding: utf-8 -*-
"""fill_ow —— 主动触发一次 RequestOWEndlessData，把 GroupInfo 填起来

为什么需要它
------------
MonoOWEndlessUIManager.SetupView 的执行顺序是：

    +0x95  NetworkManager.RequestOWEndlessData()   → 发 3419
    ...    继续往下装配，调到 RefreshPlayerGroup
           → GroupInfo._GroupLevel 还是 0（rsp 没回来）
           → GetOWEndlessGroupMetaByKey(0, mode) = null → NRE
           → 装配失败 → 每帧重试 → 每帧重发 3419（3419 风暴 + 黑屏）

GroupInfo 只能由 `OnGetOpenworldEndlessDataRsp` → `EndlessBaseData.Refresh(rsp)` 填充。
正常流程里，数据是在**开放世界准备页**就拉好的：

    OWEndlessPreparePageContext.SetupView (+0x11C)  →  RequestOWEndlessData

我们直接调 GoToOWEndless 跳过了准备页，所以 GroupInfo 是空壳。

这个脚本补上那一步：先发一次请求，等 rsp 回来把 GroupInfo 填好，
再让上层去调 GoToOWEndless。

NetworkManager 实例怎么拿
------------------------
SetupView 里是一段 il2cpp 静态单例追逐：

    0x18185AF4F  rax = [rip + 0x823D252]   ; → 0x189A981A8（Il2CppClass* 槽）
    0x18185AF56  rdi = [rax]               ; Il2CppClass*
    0x18185AF6A  rax = [rdi + 0x90]        ; ->static_fields
    0x18185AF71  rdi = [rax]               ; 下一层
    0x18185AF85  rax = [rdi + 0x28]        ; ->字段槽
    0x18185AF89  rcx = [rax]               ; ← NetworkManager 实例

本脚本逐层读内存复现这段追逐，并在调用前做三道校验（klass 落在模块内、
初始化标志是 0/1、实例指针合法），任一不过就放弃调用。

用法:
    python fill_ow.py          # 触发 + 校验填充结果
    python fill_ow.py --dry    # 只做指针追逐和校验，不调用
"""
import struct
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import icall   # noqa: E402
import owgo    # noqa: E402

RVA_STATIC_SLOT = 0x9A981A8    # [rip+0x823D252] 静态槽
RVA_REQUEST     = 0x1AC59D0    # NetworkManager.RequestOWEndlessData(this)
RVA_CURRENT     = 0x18981B0    # OWEndlessModule.GetCurrentEndlessData
RVA_GROUP_BY_KEY = 0x35062C0   # GetOWEndlessGroupMetaByKey(level, mode)

OFF_DATA_GROUP  = 0x20
OFF_GROUP_RSP   = 0x18
OFF_GROUP_ID    = 0x20
OFF_GROUP_LEVEL = 0x24
OFF_GROUP_TOP   = 0x28

# 模块内 klass / 静态数据都落在 .rdata/.data/.tvm0，rva 大致 0x400000..0xC000000
MOD_RVA_LO = 0x00400000
MOD_RVA_HI = 0x0C000000


def q(h, va):
    b = icall.read_mem(h, va, 8)
    return struct.unpack("<Q", b)[0] if b and len(b) == 8 else None


def u32(h, va):
    b = icall.read_mem(h, va, 4)
    return struct.unpack("<I", b)[0] if b and len(b) == 4 else None


def i32(h, va):
    b = icall.read_mem(h, va, 4)
    return struct.unpack("<i", b)[0] if b and len(b) == 4 else None


def u8(h, va):
    b = icall.read_mem(h, va, 1)
    return b[0] if b else None


def in_module(base, va):
    if not va:
        return False
    rva = va - base
    return MOD_RVA_LO <= rva <= MOD_RVA_HI


def chase_network_manager(h, base):
    """复现 SetupView 里的静态单例追逐，带逐层校验。"""
    steps = []

    slot = q(h, base + RVA_STATIC_SLOT)
    steps.append(("静态槽 [%#x]" % (base + RVA_STATIC_SLOT), slot))
    if not slot:
        return None, steps, "静态槽读出 0"

    cls1 = q(h, slot)
    steps.append(("[槽] → cls1", cls1))
    if not in_module(base, cls1):
        return None, steps, "cls1 不在模块内"

    f1 = u8(h, cls1 + 0x136)
    steps.append(("cls1+0x136 初始化标志", f1))
    if f1 not in (0, 1):
        return None, steps, "cls1 不像 Il2CppClass（+0x136 不是 0/1）"

    sf1 = q(h, cls1 + 0x90)
    steps.append(("cls1+0x90 static_fields", sf1))
    if not in_module(base, sf1):
        return None, steps, "static_fields 不在模块内"

    cls2 = q(h, sf1)
    steps.append(("[static_fields] → cls2", cls2))
    if not in_module(base, cls2):
        return None, steps, "cls2 不在模块内"

    f2 = u8(h, cls2 + 0x136)
    steps.append(("cls2+0x136 初始化标志", f2))
    if f2 not in (0, 1):
        return None, steps, "cls2 不像 Il2CppClass（+0x136 不是 0/1）"

    fld = q(h, cls2 + 0x28)
    steps.append(("cls2+0x28 字段槽", fld))
    if not fld:
        return None, steps, "字段槽为 0"

    nm = q(h, fld)
    steps.append(("[字段槽] → NetworkManager", nm))
    if not nm or nm < 0x10000:
        return None, steps, "NetworkManager 指针不合法"

    # 实例的 klass 指针（对象头 +0x00）必须在模块内
    klass = q(h, nm)
    steps.append(("nm+0x00 klass", klass))
    if not in_module(base, klass):
        return None, steps, "nm 的 klass 不在模块内 —— 追错了"

    return nm, steps, None


def read_group(h, mb, base, this):
    buf = None
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        rc = icall.cmd_call(base + RVA_CURRENT, [this])
    if rc != 0:
        return None
    data = q(h, mb + 0x30)
    if not data:
        return None
    g = q(h, data + OFF_DATA_GROUP)
    if not g:
        return {"data": data, "group": 0}
    return {
        "data": data,
        "group": g,
        "rsp": q(h, g + OFF_GROUP_RSP),
        "id": u32(h, g + OFF_GROUP_ID),
        "level": i32(h, g + OFF_GROUP_LEVEL),
        "top": u32(h, g + OFF_GROUP_TOP),
    }


def show(tag, g):
    if not g:
        print("  [%s] GetCurrentEndlessData = null" % tag)
        return
    if not g.get("group"):
        print("  [%s] Group = 0" % tag)
        return
    print("  [%s] _rsp=%#x  _GroupID=%s  _GroupLevel=%s  _CurTopGroupLevel=%s"
          % (tag, g["rsp"] or 0, g["id"], g["level"], g["top"]))


def main():
    dry = "--dry" in sys.argv

    h, pid, base = icall.open_game()
    if not h:
        print("游戏未运行 / 需要管理员权限")
        return 1
    try:
        st = owgo.ensure_mailbox(h, pid, base)
        if not st:
            return 1
        mb = st["mailbox"]

        d = owgo.load() or {}
        this = d.get("this") if d.get("pid") == pid else None
        if not this:
            print("还没有 this，先跑 python owgo.py check")
            return 1

        print("指针追逐 NetworkManager：")
        nm, steps, err = chase_network_manager(h, base)
        for k, v in steps:
            print("  %-32s %s" % (k, ("%#x" % v) if isinstance(v, int) else v))
        if err:
            print("✗ 校验失败：%s —— 放弃调用，什么都没改" % err)
            return 2
        print("✓ NetworkManager = %#x（三道校验通过）" % nm)

        print("\n调用前：")
        show("before", read_group(h, mb, base, this))

        if dry:
            print("\n--dry：到此为止，未调用")
            return 0

        print("\n调用 RequestOWEndlessData(%#x) …" % nm)
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            rc = icall.cmd_call(base + RVA_REQUEST, [nm])
        if rc != 0:
            print("✗ 调用失败 rc=%d" % rc)
            return 1
        print("  已发出，等 rsp 回来…")
        time.sleep(2.0)

        print("\n调用后：")
        g = read_group(h, mb, base, this)
        show("after", g)

        if not g or not g.get("group"):
            return 1
        if not g.get("rsp"):
            print("✗ _rsp 仍为 0 —— 3420 没被处理（看服务端日志有没有 GetOpenworldEndlessDataRsp）")
            return 2

        lv = g.get("level")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = icall.cmd_call(base + RVA_GROUP_BY_KEY, [lv, 2])
        meta = q(h, mb + 0x30) if rc == 0 else None
        print("\n  GetOWEndlessGroupMetaByKey(%s, 2) = %s" % (lv, ("%#x" % meta) if meta else "null"))
        if meta:
            print("✓ 查表通过 —— 现在可以 python owgo.py call")
            return 0
        print("✗ 查表仍为 null。mode=2 的有效 GroupLevel 是 21~24，")
        print("  服务端 GetOpenworldEndlessDataRsp.GroupLevel 要改成其中之一。")
        return 2
    finally:
        icall.k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main())
