# -*- coding: utf-8 -*-
"""生成"看得见"的验证补丁：三处 UI 文案等长替换
   8067 进入游戏 / 8139 返回游戏 / 8052 登录成功  ->  「补丁生效」
   全部 12 字节，等长替换，零长度变化
"""
import sys

sys.path.insert(0, r"D:\Carol-start\_rea")
from meta_writer import MetaWriter

SRC = r"D:\Carol-start\_rea\work_metadata.dat"
DST = r"D:\Carol-start\_rea\patch_visible.dat"
NEW = "补丁生效"

TARGETS = [8067, 8139, 8052]


def main():
    w = MetaWriter(SRC)
    print("原始文案:")
    for idx in TARGETS:
        old = w.get_blob_text(idx)
        print("  %d: %r (%d 字节)" % (idx, old, len(old.encode("utf-8"))))
        assert len(old.encode("utf-8")) == len(NEW.encode("utf-8")), \
            "长度不匹配: %d 原文 %d 字节" % (idx, len(old.encode("utf-8")))

    # 邻行快照（用于验证零污染）
    neigh = {}
    for idx in TARGETS:
        for j in (idx - 1, idx + 1):
            neigh[j] = w.get_blob_text(j)

    for idx in TARGETS:
        w.set_blob_text(idx, NEW)

    w.save(DST)

    # 回读验证
    w2 = MetaWriter(DST)
    print("\n改后回读:")
    ok = True
    for idx in TARGETS:
        got = w2.get_blob_text(idx)
        print("  %d: %r  %s" % (idx, got, "OK" if got == NEW else "失败"))
        ok = ok and got == NEW
    print("邻行零污染:", all(w2.get_blob_text(j) == v for j, v in neigh.items()))

    orig = open(SRC, "rb").read()
    pat = open(DST, "rb").read()
    diff = sum(1 for a, b in zip(orig, pat) if a != b)
    print("与原件差异字节: %d (期望 36 = 3 处 × 12 字节)" % diff)
    print("结果:", "通过" if ok and diff == 36 else "需检查")


if __name__ == "__main__":
    main()
