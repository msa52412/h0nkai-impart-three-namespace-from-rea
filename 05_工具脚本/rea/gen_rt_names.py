#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_rt_names.py — 生成「il2cpp 运行时 / codegen helper」的符号表

只收录**有硬证据**的条目，判据分三类：

  [S] 字符串常量：函数体内 LEA 到 .rdata 的 C 字符串，内容直接读出
      （0x1881A1DE8="System"、0x1881A1F18="IndexOutOfRangeException"、
        0x1881A1F38="NullReferenceException"）
  [A] 汇编形态：noreturn 桩 = `SUB RSP,0x28; CALL X; INT3`；
      thunk = 5 字节 `JMP X`
  [C] 调用点上下文：调用者紧邻的判据（空指针比较 / 数组越界比较 /
      klass->initialized 标志比较）

输出：bh3_rt_names.tsv，列与 ApplySymbols.java 一致
      rva  ns  cls  method  ret  params  isStatic  token  module  aliasOf
用法: python gen_rt_names.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "bh3_rt_names.tsv")
BASE = 0x180000000

# (VA, ns, cls, method, 证据, 说明)
ROWS = [
    # ---- il2cpp::vm::Exception 家族：由 .rdata 字符串直接坐实 ----
    (0x18042D650, "il2cpp.vm", "Class", "FromName",
     "S",
     "参数为 (corlib, \"System\", 异常类型名)，返回 Il2CppClass*"),
    (0x18042D860, "il2cpp.vm", "Class", "Init",
     "C",
     "以 klass 为参数；调用点均先判 [klass+0xE8]==0；内部持全局锁 0x1899DB878 后置 1"),
    (0x180448320, "il2cpp.vm", "Exception", "Raise",
     "A/C",
     "37 字节；尾随 INT3；被 0x1804FE3D0 以「已构造好的异常对象」调用"),
    (0x180436120, "il2cpp.vm", "Exception", "CreateIndexOutOfRangeException",
     "S",
     "Class::FromName(corlib,\"System\",\"IndexOutOfRangeException\") 后实例化"),
    (0x180448970, "il2cpp.vm", "Exception", "RaiseNullReferenceException",
     "S",
     "Class::FromName(corlib,\"System\",\"NullReferenceException\") 后 Raise"),

    # ---- il2cpp_codegen_* 前端桩：由调用点上下文坐实 ----
    (0x1804FE400, "il2cpp.codegen", "codegen", "raise_null_reference_exception",
     "A/C",
     "10 字节 = CALL 0x180448970 + INT3；调用点紧跟对象空判断；946,440 个调用点"),
    (0x1804FE210, "il2cpp.codegen", "codegen", "get_index_out_of_range_exception",
     "A/S",
     "5 字节 JMP 0x180436120；调用点用于数组越界分支；99,310 个调用点"),
    (0x1804FE3D0, "il2cpp.codegen", "codegen", "raise_exception",
     "A/C",
     "10 字节 = CALL 0x180448320 + INT3；参数为异常对象；186,425 个调用点"),
    (0x1804FE480, "il2cpp.codegen", "codegen", "runtime_class_init",
     "A/C",
     "5 字节 JMP 0x18042D860；调用点均先判 klass+0xE8；393,235 个调用点"),
]

HEADER = "rva\tns\tcls\tmethod\tret\tparams\tisStatic\ttoken\tmodule\taliasOf\n"


def main():
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(HEADER)
        for va, ns, cls, method, ev, note in ROWS:
            rva = va - BASE
            f.write("%X\t%s\t%s\t%s\tvoid\t-\t0\t-\t-\t\n"
                    % (rva, ns, cls, method))
    print("写出 %d 条 -> %s" % (len(ROWS), OUT))
    print()
    print("%-12s %-16s %-40s %-4s %s" % ("VA", "命名空间", "名字", "证据", "说明"))
    for va, ns, cls, method, ev, note in ROWS:
        print("%-12X %-16s %-40s %-4s %s"
              % (va, ns, cls + "::" + method, ev, note))


if __name__ == "__main__":
    main()
