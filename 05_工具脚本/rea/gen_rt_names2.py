#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_rt_names2.py — 生成 ApplyRt.java 用的 TSV（va / noreturn / ns / cls / method）

和第一版 gen_rt_names.py 的差别：
  * 命名空间只到 `il2cpp`，类名单独一层 `codegen`，避免出现 `codegen::codegen`
  * 增加 noreturn 列：抛异常的 4 个函数标 1，反编译就不再吐 `swi(3)` 尾巴
  * 新增 0x1804FE3C0 = initialize_class（依据见下）

证据等级：
  S  字符串常量坐实（0x1881A1DE8="System"、0x1881A1F18="IndexOutOfRangeException"、
     0x1881A1F38="NullReferenceException"）
  A  汇编形态（noreturn 桩 = SUB RSP,0x28; CALL X; INT3；thunk = 5 字节 JMP）
  C  调用点上下文（空指针比较 / 数组越界比较 / klass+0xE8 初始化标志 /
     返回值被当作 this 继续调用）
用法: python gen_rt_names2.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "bh3_rt_names2.tsv")

# (VA, noreturn, ns, cls, method, 证据, 说明)
ROWS = [
    (0x18042D650, 0, "il2cpp.vm", "Class", "FromName", "S",
     "MOV RCX,[corlib]; LEA RDX,\"System\"; LEA R8,\"<异常类名>\"; CALL → Il2CppClass*"),
    (0x18042D860, 0, "il2cpp.vm", "Class", "Init", "C",
     "以 klass 为参；调用点均先判 [klass+0xE8]==0；内部取全局锁 0x1899DB878 后把 +0xE8 置 1"),

    (0x180448320, 1, "il2cpp.vm", "Exception", "Raise", "A/C",
     "37 字节，尾随 INT3；入参是已构造好的异常对象；被 codegen::raise_exception 调用"),
    (0x180436120, 0, "il2cpp.vm", "Exception", "CreateIndexOutOfRangeException", "S",
     "Class::FromName(corlib,\"System\",\"IndexOutOfRangeException\") 后实例化"),
    (0x180431FB0, 0, "il2cpp.vm", "Exception", "CreateArrayTypeMismatchException", "S",
     "同形态；名字常量 0x1881A2080 = \"ArrayTypeMismatchException\""),
    (0x1804FE1D0, 0, "il2cpp", "codegen", "get_array_type_mismatch_exception", "A/S",
     "5 字节 JMP 0x180431FB0；22,453 个调用点"),
    (0x180448970, 1, "il2cpp.vm", "Exception", "RaiseNullReferenceException", "S",
     "Class::FromName(corlib,\"System\",\"NullReferenceException\") 后 Raise"),

    (0x1804FE400, 1, "il2cpp", "codegen", "raise_null_reference_exception", "A/C",
     "10 字节 = CALL 0x180448970 + INT3；调用点紧跟对象空判断；946,440 个调用点"),
    (0x1804FE210, 0, "il2cpp", "codegen", "get_index_out_of_range_exception", "A/S",
     "5 字节 JMP 0x180436120；调用点位于数组越界分支；99,310 个调用点"),
    (0x1804FE3D0, 1, "il2cpp", "codegen", "raise_exception", "A/C",
     "10 字节 = CALL 0x180448320 + INT3；参数为异常对象；186,425 个调用点"),
    (0x1804FE480, 0, "il2cpp", "codegen", "runtime_class_init", "A/C",
     "5 字节 JMP 0x18042D860；调用点均先判 klass+0xE8，且丢弃返回值；393,235 个调用点"),
    (0x1804457F0, 0, "il2cpp.vm", "Object", "New", "C",
     "先按 [klass+0xC0] 把泛型/变体解析成真实 klass；再用 [klass+0x114] 的 instance_size "
     "调分配器；末尾调 Class::Init 跑 cctor；返回新实例"),
    (0x1804FE3C0, 0, "il2cpp", "codegen", "object_new", "A/C",
     "5 字节 JMP 0x180445760→0x1804457F0；入参是 klass 全局，返回值被当作 this 传给构造函数"
     "并存进字段（见 BulletinActivityConfig::_ctor）；194,209 个调用点"),
]

HEADER = "#va\tnoreturn\tns\tcls\tmethod\n"


def main():
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(HEADER)
        for va, nr, ns, cls, method, ev, note in ROWS:
            f.write("%X\t%d\t%s\t%s\t%s\n" % (va, nr, ns, cls, method))
    print("写出 %d 条 -> %s" % (len(ROWS), OUT))
    print()
    print("%-12s %-3s %-24s %-42s %-3s %s"
          % ("VA", "NR", "命名空间", "名字", "证据", "说明"))
    for va, nr, ns, cls, method, ev, note in ROWS:
        print("%-12X %-3s %-24s %-42s %-3s %s"
              % (va, "Y" if nr else "", ns, cls + "::" + method, ev, note))


if __name__ == "__main__":
    main()
