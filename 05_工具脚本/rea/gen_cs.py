#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_cs.py — 由还原出的元数据 + 字段布局，生成 C# 源码骨架

输入（全部是本项目已还原的产物）：
  bh3_types_v5.txt        类型表   index ns type token methodStart methodCount nestedCount parentIdx parent fieldCount
  bh3_fields.tsv          字段表   typeIdx typeName fieldIdx fieldName fieldType
  bh3_layout4.tsv         字段布局 typeIdx typeName fieldIdx fieldName fieldType size isStatic offset conf nProbe
  bh3_structs2.tsv        类型尺寸 typeIdx catPath name size conf nInst fields
  bh3_methods_v2.tsv      方法表   idx token declTypeIdx declType name returnType flags slot iflags paramCount genericContainer params
  bh3_method_addr.tsv     方法地址 idx token module rva declType name params
  bh3_generic_params.tsv  泛型形参 idx name container kind ownerIdx owner
  bh3_properties_v2.tsv   属性     typeIdx typeName propIdx propName propType token getter setter
  bh3_events.tsv          事件     typeIdx typeName eventIdx eventName eventType addIdx removeIdx raiseIdx token

输出：
  src/<命名空间>.cs        一个命名空间一个文件（全局命名空间 → _global.cs）
  src/_index.md            索引

用法：
  python gen_cs.py [--out src] [--ns proto] [--bodies bodies.tsv]

说明：
  * 方法体默认留空并标注原生地址；给了 --bodies 就把反编译体填进去
  * 类型种类由父类推断：System.Enum→enum / System.ValueType→struct /
    System.MulticastDelegate→delegate / 全抽象方法→interface / 其余→class
  * 元数据里没有「嵌套类型归属」字段（nestedTypes 数组未解出），
    所以嵌套类型与顶层类型混在同一个命名空间里，名字保持原样
"""
import os
import sys
import re
import io
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
# 布局来源：v6 用元数据 attrs 真值判定 static/literal，并修了泛型结构体实例化
LAYOUT_FILE = os.environ.get("BH3_LAYOUT", "bh3_layout6.tsv")

# ---- C# 别名 ----
ALIAS = {
    "System.Object": "object", "System.String": "string", "System.Boolean": "bool",
    "System.Char": "char", "System.SByte": "sbyte", "System.Byte": "byte",
    "System.Int16": "short", "System.UInt16": "ushort",
    "System.Int32": "int", "System.UInt32": "uint",
    "System.Int64": "long", "System.UInt64": "ulong",
    "System.Single": "float", "System.Double": "double",
    "System.Decimal": "decimal", "System.Void": "void",
    "System.IntPtr": "IntPtr", "System.UIntPtr": "UIntPtr",
    "System.TypedReference": "TypedReference",
}

# 指针类原生类型 → 统一落成 IntPtr
NATIVE_PTR = re.compile(r"^[A-Za-z_][\w.]*\*+$")

BAD = re.compile(r"[<>`\$\-]")

# 方法 flags（本二进制的位布局与 ECMA 标准不同，实测标定见 §9O 注）
F_STATIC = 0x0010
F_VIRTUAL = 0x0040
F_FINAL = 0x0020
F_NEWSLOT = 0x0100
F_ABSTRACT = 0x0400          # 标准是 0x0200，本二进制右移了一位
F_SPECIAL = 0x0800           # 标准是 0x0400
ACCESS = {0: "", 1: "private ", 2: "protected internal ", 3: "internal ",
          4: "protected ", 5: "protected internal ", 6: "public "}


def ident(s):
    """把 il2cpp 里的非法标识符改成可编译的形式"""
    if not s:
        return "_"
    t = BAD.sub("_", s)
    t = t.replace(".", "_").replace("/", "_").replace(" ", "_")
    if t and t[0].isdigit():
        t = "_" + t
    return t


def const_literal(ct, v, kind="u32"):
    """按 C# 声明类型与值宽度把原始值渲染成常量字面量；kind 来自 fdv 表"""
    t = ct.strip()
    if kind == "string":
        return '"%s"' % v.replace("\\", "\\\\").replace('"', '\\"') if isinstance(v, str) else "null"
    if t == "string":
        return "null /* string const，值缺 */"
    if t in ("bool",):
        return "true" if (v & 1) else "false"
    if t in ("byte", "sbyte", "ushort", "short", "uint", "int", "ulong", "long"):
        # 有符号类型按宽度符号扩展后输出十进制
        w = {"byte": 8, "sbyte": 8, "ushort": 16, "short": 16,
             "uint": 32, "int": 32, "ulong": 64, "long": 64}[t]
        sv = v & ((1 << w) - 1)
        if t in ("sbyte", "short", "int", "long") and sv >> (w - 1):
            sv -= 1 << w
        return str(sv)
    if t in ("float",):
        import struct as _st
        return "%rF" % _st.unpack("<f", _st.pack("<I", v & 0xFFFFFFFF))[0]
    if t in ("double",):
        import struct as _st
        return "%rD" % _st.unpack("<d", _st.pack("<Q", v))[0]
    if t in ("char",):
        return "'\\u%04X'" % (v & 0xFFFF)
    if kind in ("u8", "u16"):
        return str(v)
    return "0x%X" % v      # 枚举等其他：十六进制


def split_params(s):
    """按 ', ' 切参数，跳过 <> 与 [] 内部"""
    out = []
    if not s.strip():
        return out
    depth = 0
    cur = []
    i = 0
    while i < len(s):
        c = s[i]
        if c in "<[(":
            depth += 1
        elif c in ">])":
            depth -= 1
        if c == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
            i += 1
            if i < len(s) and s[i] == " ":
                i += 1
            continue
        cur.append(c)
        i += 1
    if cur:
        out.append("".join(cur).strip())
    return out


def split_decl(s):
    """'Type name' → (Type, name)；按 depth 0 的最后一个空格切"""
    depth = 0
    last = -1
    for i, c in enumerate(s):
        if c in "<[(":
            depth += 1
        elif c in ">])":
            depth -= 1
        elif c == " " and depth == 0:
            last = i
    if last < 0:
        return s.strip(), ""
    return s[:last].strip(), s[last + 1:].strip()


class BodyStore(object):
    """bodies.tsv 的磁盘索引视图。

    只把 (rva → 行首字节偏移) 放进内存，函数体按需 seek 读取。
    全量导出后 bodies.tsv 有 905 MB / 311,317 条，如果做成 `{rva: text}` 字典，
    光字符串就要 1 GB —— 本机可用内存只有 1 GB 上下（kryptex 常驻吃 8 GB），
    会直接换页到磁盘。索引本身约 30 MB。

    对调用方完全透明：支持 `rva in store` / `store.get(rva)` / `store[rva]`。
    """

    def __init__(self, path):
        self.path = path
        self.base = 0x180000000
        self.idx = {}
        off = 0
        with io.open(path, "rb") as f:
            for ln in f:
                t = ln.find(b"\t")
                if t > 0:
                    try:
                        self.idx[int(ln[:t], 16) - self.base] = off
                    except ValueError:
                        pass
                off += len(ln)
        self.n = len(self.idx)
        self._f = None

    def __contains__(self, rva):
        return rva in self.idx

    def __len__(self):
        return self.n

    def __getitem__(self, rva):
        v = self.get(rva)
        if v is None:
            raise KeyError(rva)
        return v

    def get(self, rva, default=None):
        off = self.idx.get(rva)
        if off is None:
            return default
        if self._f is None:
            # 必须用带缓冲的 reader：RawIOBase 的 readline 是逐字节读，
            # 311k 条 3 KB 的行会退化成十亿次单字节系统调用。
            self._f = io.open(self.path, "rb")
        self._f.seek(off)
        ln = self._f.readline()
        t = ln.find(b"\t")
        if t < 0:
            return default
        b = ln[t + 1:].decode("utf-8", "replace")
        return b.replace("\\n", "\n").rstrip("\\").rstrip()


class Gen(object):
    def __init__(self):
        self.types = {}       # idx -> dict
        self.by_name = {}     # full name -> idx
        self.fdecl = {}       # typeIdx -> [(fi, name, type)]
        self.layout = {}      # (typeIdx, fi) -> (offset, size, isStatic, conf)
        self.fliteral = set() # fieldIdx：元数据 literal（const），不占存储
        self.tsize = {}       # typeIdx -> size
        self.methods = {}     # declTypeIdx -> [method dict]
        self.maddr = {}       # method idx -> rva
        self.gp_type = {}     # typeIdx -> [names]
        self.gp_meth = {}     # method idx -> [names]
        self.props = {}       # typeIdx -> [dict]
        self.events = {}      # typeIdx -> [dict]
        self.bodies = {}      # rva -> code text
        self.gname = {}       # va -> Ghidra 里的函数名
        self.share = {}       # rva -> 共用该地址的 C# 方法数
        self.nest_parent = {} # childIdx -> parentIdx
        self.nest_kids = {}   # parentIdx -> [childIdx]（保持元数据顺序）
        self.fdefault = {}    # fieldIdx -> U32 值（fieldDefaultValues 表，含 const/枚举）

    # ---------- 载入 ----------
    def _open(self, name):
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            return None
        return open(p, encoding="utf-8", errors="replace")

    def load_types(self):
        f = self._open("bh3_types_v5.txt")
        f.readline()
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 10:
                continue
            i = int(p[0])
            self.types[i] = dict(i=i, ns=p[1], name=p[2], token=p[3],
                                 ms=int(p[4]), mc=int(p[5]), ncc=int(p[6]),
                                 parent=p[8], fc=int(p[9]))
            full = (p[1] + "." if p[1] else "") + p[2]
            self.by_name.setdefault(full, i)
        f.close()

    def load_fields(self):
        f = self._open("bh3_fields.tsv")
        f.readline()
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 5:
                continue
            ti = int(p[0])
            self.fdecl.setdefault(ti, []).append((int(p[2]), p[3], p[4]))
        f.close()
        for v in self.fdecl.values():
            v.sort()

    def load_field_defaults(self):
        """fieldDefaultValues 表（0x564210，值池 0x1D79938 明文）：
           fieldIdx -> (kind, value)；kind in u8/u16/u32/u64/f32/str/sentinel"""
        f = self._open("bh3_field_defaults.tsv")
        if not f:
            return
        f.readline()
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) >= 5 and p[0] != "fieldIdx":
                # value 列：数值类是十进制文本，string 类是文本本身
                try:
                    self.fdefault[int(p[0])] = (p[3], int(p[4]))
                except ValueError:
                    self.fdefault[int(p[0])] = (p[3], p[4])
        f.close()

    def load_layout(self):
        f = self._open(LAYOUT_FILE)
        f.readline()
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 10:
                continue
            ti = int(p[0])
            fi = int(p[2])
            self.layout[(ti, fi)] = (int(p[7]), int(p[5]), p[6] == "1", p[8])
        f.close()
        f = self._open("bh3_field_flags.tsv")
        if f:
            f.readline()
            for ln in f:
                p = ln.rstrip("\n").split("\t")
                if len(p) >= 5 and p[4] == "1":
                    try:
                        self.fliteral.add(int(p[0]))
                    except ValueError:
                        pass
            f.close()
        f = self._open("bh3_structs2.tsv")
        if f:
            f.readline()
            for ln in f:
                p = ln.rstrip("\n").split("\t")
                if len(p) >= 4:
                    try:
                        self.tsize[int(p[0])] = int(p[3])
                    except ValueError:
                        pass
            f.close()
        # 类型置信度（取该类型任一字段的 conf，同类型内一致）
        self.tconf = {}
        for (ti, fi), v in self.layout.items():
            self.tconf.setdefault(ti, v[3])

    def load_methods(self):
        f = self._open("bh3_methods_v2.tsv")
        f.readline()
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 12:
                continue
            try:
                mi = int(p[0])
                ti = int(p[2])
                fl = int(p[6], 16)
            except ValueError:
                continue
            self.methods.setdefault(ti, []).append(dict(
                idx=mi, token=p[1], name=p[4], ret=p[5], flags=fl,
                params=p[11], pc=int(p[9]) if p[9].isdigit() else 0))
        f.close()
        for v in self.methods.values():
            v.sort(key=lambda m: m["idx"])

        f = self._open("bh3_method_addr.tsv")
        f.readline()
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 4 or not p[3].strip():
                continue
            try:
                self.maddr[int(p[0])] = int(p[3], 16)
            except ValueError:
                pass
        f.close()

        for r in self.maddr.values():
            self.share[r] = self.share.get(r, 0) + 1

    def load_generic(self):
        f = self._open("bh3_generic_params.tsv")
        if not f:
            return
        f.readline()
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 5:
                continue
            try:
                ci = int(p[2])
                oi = int(p[4])
            except ValueError:
                continue
            if p[3] == "VAR":
                self.gp_type.setdefault(oi, []).append((ci, p[1]))
            elif p[3] == "MVAR":
                self.gp_meth.setdefault(oi, []).append((ci, p[1]))
        f.close()
        for d in (self.gp_type, self.gp_meth):
            for k in d:
                d[k].sort()

    def load_props_events(self):
        f = self._open("bh3_properties_v2.tsv")
        if f:
            f.readline()
            for ln in f:
                p = ln.rstrip("\n").split("\t")
                if len(p) < 8:
                    continue
                self.props.setdefault(int(p[0]), []).append(
                    dict(name=p[3], type=p[4], token=p[5],
                         getter=p[6], setter=p[7]))
            f.close()
        f = self._open("bh3_events.tsv")
        if f:
            f.readline()
            for ln in f:
                p = ln.rstrip("\n").split("\t")
                if len(p) < 9:
                    continue
                self.events.setdefault(int(p[0]), []).append(
                    dict(name=p[3], type=p[4]))
            f.close()

    def load_gnames(self, path=None):
        """Ghidra 里每个函数的真实名字，用来标注共享体的代表函数"""
        p = os.path.join(HERE, path or "names_all3.tsv")
        if not os.path.exists(p):
            return
        with open(p, encoding="utf-8", errors="replace") as f:
            f.readline()
            for ln in f:
                q = ln.rstrip("\n").split("\t")
                if len(q) < 2:
                    continue
                try:
                    self.gname[int(q[0], 16)] = q[1]
                except ValueError:
                    pass
        print("  载入 Ghidra 函数名 %d 条" % len(self.gname))

    def load_nested(self, path=None):
        """嵌套类型父子关系。
        来源：metadata +0x1C41FB0 处的 TypeDefinitionIndex 数组（长度 21429），
        配合 TypeDefinition +0x20 nestedTypesStart / +0x46 nestedCount 切段。
        验证：数组元素 namespace 全为空、零重复、父段零空洞零重叠。"""
        p = os.path.join(HERE, path or "bh3_nested.tsv")
        if not os.path.exists(p):
            print("  [warn] 没有 %s，跳过嵌套类型归属" % (path or "bh3_nested.tsv"))
            return
        with open(p, encoding="utf-8", errors="replace") as f:
            f.readline()
            for ln in f:
                q = ln.rstrip("\n").split("\t")
                if len(q) < 2:
                    continue
                c, pa = int(q[0]), int(q[1])
                self.nest_parent[c] = pa
                self.nest_kids.setdefault(pa, []).append(c)
        print("  载入嵌套类型 %d 个（%d 个父类型）"
              % (len(self.nest_parent), len(self.nest_kids)))

    def load_bodies(self, path):
        """bodies.tsv: VA<TAB>一行代码（\\n 转义）。内部统一按 RVA 存，和方法表对齐。

        用 BodyStore 而不是 dict：全量导出后这个文件有 905 MB / 311,317 条，
        `{rva: text}` 要吃掉 1 GB 以上内存。改成只把 (rva → 字节偏移) 放内存
        （约 30 MB），函数体在真正写的时候才 seek 读。
        """
        self.bodies = BodyStore(path)
        print("  载入方法体索引 %d 条（%.0f MB，磁盘按需读取）"
              % (self.bodies.n, os.path.getsize(path) / 1048576.0))

    # ---------- 渲染 ----------
    def cs_type(self, t, tidx=None, midx=None):
        t = (t or "").strip()
        if not t:
            return "object"
        if t.startswith("!"):
            # !0 → 类型泛型形参
            try:
                k = int(t[1:])
            except ValueError:
                return "object"
            names = self.gp_type.get(tidx or -1, [])
            return names[k][1] if k < len(names) else "T%d" % k
        if t.startswith("!!"):
            try:
                k = int(t[2:])
            except ValueError:
                return "object"
            names = self.gp_meth.get(midx or -1, [])
            return names[k][1] if k < len(names) else "T%d" % k
        if NATIVE_PTR.match(t):
            return "IntPtr"
        if t in ALIAS:
            return ALIAS[t]
        # 泛型：Ns.List`1<...> → List<...>
        m = re.match(r"^(.*?)`(\d+)(<(.*)>)?$", t)
        if m:
            base = m.group(1)
            args = split_params(m.group(4) or "")
            short = base.rsplit(".", 1)[-1]
            if args:
                return "%s<%s>" % (short, ", ".join(
                    self.cs_type(a, tidx, midx) for a in args))
            # 没有实参：用声明处的形参名补上
            k = int(m.group(2))
            nm = self.gp_type.get(self.by_name.get(base, -1), [])
            if len(nm) >= k:
                return "%s<%s>" % (short, ", ".join(x[1] for x in nm[:k]))
            return "%s<%s>" % (short, ", ".join("T%d" % i for i in range(k)))
        if t.endswith("[]"):
            return self.cs_type(t[:-2], tidx, midx) + "[]"
        if "." in t:
            return t.rsplit(".", 1)[-1]
        return t

    def kind_of(self, ti):
        t = self.types[ti]
        p = t["parent"]
        if p == "System.Enum":
            return "enum"
        if p == "System.ValueType":
            return "struct"
        if p == "System.MulticastDelegate":
            return "delegate"
        ms = self.methods.get(ti, [])
        if ms and p == "System.Object" and all(m["flags"] & F_ABSTRACT for m in ms):
            return "interface"
        return "class"

    def type_decl(self, ti):
        t = self.types[ti]
        k = self.kind_of(ti)
        name = ident(t["name"])
        gp = self.gp_type.get(ti, [])
        if gp:
            name += "<%s>" % ", ".join(x[1] for x in gp)
        base = ""
        if k == "class" and t["parent"] and t["parent"] != "System.Object":
            base = " : " + self.cs_type(t["parent"])
        if k == "interface":
            base = ""
        return k, name, base

    def emit_type(self, ti, out, depth=0, spans=None):
        """spans: ti -> (起始下标, 结束下标)，用于给浏览器做行号切片"""
        st = len(out)
        try:
            self._emit_type(ti, out, depth, spans)
        finally:
            if spans is not None:
                spans[ti] = (st, len(out))

    def _emit_type(self, ti, out, depth=0, spans=None):
        t = self.types[ti]
        k, name, base = self.type_decl(ti)
        size = self.tsize.get(ti, 0)
        conf = self.tconf.get(ti, "")
        ind = "  " * (depth + 1)       # 类型声明缩进
        mem = "  " * (depth + 2)       # 成员缩进
        hdr = ind + "// token %s" % t["token"]
        if size:
            hdr += " · 0x%X 字节" % size
        if conf:
            hdr += " · 布局置信度 %s" % conf
        if t["mc"]:
            hdr += " · %d 个方法" % t["mc"]
        kids = self.nest_kids.get(ti, [])
        if kids:
            hdr += " · %d 个嵌套类型" % len(kids)
        out.append(hdr)

        if k == "delegate":
            ms = self.methods.get(ti, [])
            if ms:
                m = ms[0]
                ps = [self.render_param(x, ti, m["idx"]) for x in split_params(m["params"])]
                out.append("%spublic delegate %s %s(%s);"
                           % (ind, self.cs_type(m["ret"], ti, m["idx"]), name, ", ".join(ps)))
            else:
                out.append("%spublic delegate void %s();" % (ind, name))
            out.append("")
            return

        if k == "enum":
            out.append("%spublic enum %s : int" % (ind, name))
            out.append("%s{" % ind)
            for fi, fn, ft in self.fdecl.get(ti, []):
                if fn == "value__":      # 枚举的内部 backing field，不是成员
                    continue
                dv = self.fdefault.get(fi)
                if dv is not None and dv[0] in ("u8", "u16", "u32", "u64"):
                    out.append("%s%s = %d," % (mem, ident(fn), dv[1]))
                else:
                    out.append("%s%s," % (mem, ident(fn)))
            out.append("%s}" % ind)
            out.append("")
            return

        out.append("%spublic %s %s%s" % (ind, k, name, base))
        out.append("%s{" % ind)

        # 字段
        lay = [(fi, fn, ft) for fi, fn, ft in self.fdecl.get(ti, [])]
        for fi, fn, ft in lay:
            info = self.layout.get((ti, fi))
            ct = self.cs_type(ft, ti)
            if info:
                off, sz, is_static, cf = info
                if is_static:
                    # literal（const）编译期内联，不占实例区也不占 static 区，
                    # 与普通 static 分开标注，便于还原 C# 声明
                    if fi in self.fliteral:
                        dv = self.fdefault.get(fi)
                        if dv is not None and dv[0] != "sentinel":
                            out.append("%spublic const %s %s = %s;"
                                       % (mem, ct, ident(fn), const_literal(ct, dv[1], dv[0])))
                        else:
                            out.append("%s// const（literal，值未解）" % mem)
                            out.append("%spublic const %s %s = default;"
                                       % (mem, ct, ident(fn)))
                    else:
                        out.append("%s// static" % mem)
                        out.append("%spublic static %s %s;" % (mem, ct, ident(fn)))
                else:
                    out.append("%s// +0x%X  (%d 字节)" % (mem, off, sz))
                    out.append("%spublic %s %s;" % (mem, ct, ident(fn)))
            else:
                out.append("%s// 布局未知" % mem)
                out.append("%spublic %s %s;" % (mem, ct, ident(fn)))

        # 属性
        for p in self.props.get(ti, []):
            acc = ""
            if p["getter"]:
                acc += "get; "
            if p["setter"]:
                acc += "set; "
            out.append("%s// %s" % (mem, p["token"]))
            out.append("%spublic %s %s { %s}"
                       % (mem, self.cs_type(p["type"], ti), ident(p["name"]), acc.strip()))

        # 事件
        for e in self.events.get(ti, []):
            out.append("%spublic event %s %s;"
                       % (mem, self.cs_type(e["type"], ti), ident(e["name"])))

        # 方法
        for m in self.methods.get(ti, []):
            self.emit_method(ti, m, k, out, depth)

        # 嵌套类型：递归，缩进 +1
        for c in kids:
            if c in self.types:
                self.emit_type(c, out, depth + 1, spans)

        out.append("%s}" % ind)
        out.append("")

    def render_param(self, decl, tidx, midx):
        ty, nm = split_decl(decl)
        return "%s %s" % (self.cs_type(ty, tidx, midx), ident(nm) or "arg")

    def emit_method(self, ti, m, kind, out, depth=0):
        mem = "  " * (depth + 2)
        f = m["flags"]
        acc = ACCESS.get(f & 7, "")
        mods = []
        if f & F_STATIC:
            mods.append("static")
        if f & F_ABSTRACT:
            mods.append("abstract")
        elif f & F_VIRTUAL and not (f & F_FINAL):
            mods.append("virtual")
        nm = m["name"]
        tname = ident(self.types[ti]["name"])
        gp = self.gp_meth.get(m["idx"], [])
        gps = ""
        if gp:
            gps = "<%s>" % ", ".join(x[1] for x in gp)

        # 显式接口实现：名字里带点（如 System.IDisposable.Dispose）是合法 C#，
        # 保留点号、去掉 global:: 前缀，并且不能带访问修饰符
        explicit = ("." in nm and not nm.startswith(".")
                    and not nm.startswith("<"))
        if explicit:
            nm_cs = nm.replace("global::", "")
        else:
            nm_cs = ident(nm)

        if nm == ".ctor":
            sig = "%s(%s)" % (tname, ", ".join(
                self.render_param(x, ti, m["idx"]) for x in split_params(m["params"])))
        elif nm == ".cctor":
            sig = "static %s()" % tname
        else:
            ps = ", ".join(self.render_param(x, ti, m["idx"])
                           for x in split_params(m["params"]))
            sig = "%s %s%s(%s)" % (self.cs_type(m["ret"], ti, m["idx"]),
                                   nm_cs, gps, ps)

        if explicit:
            decl = sig
        elif nm in (".ctor", ".cctor"):
            decl = ("%s%s %s" % (acc, " ".join(x for x in mods if x != "static"), sig))
        else:
            decl = "%s%s %s" % (acc, " ".join(mods), sig)
        decl = re.sub(r" +", " ", decl).strip()

        rva = self.maddr.get(m["idx"])
        lines = out
        lines.append("%s// %s%s" % (mem, m["token"],
                                    (" @ 0x%X" % (0x180000000 + rva)) if rva else " (无地址)"))
        body = self.bodies.get(rva) if rva else None
        if body is not None and rva is not None:
            share = self.share.get(rva, 1)
            gname = self.gname.get(0x180000000 + rva, "")
            note = "%s// 共享体：%d 个 C# 方法共用此地址" % (mem, share)
            if gname:
                note += "，Ghidra 代表函数 %s" % gname
            lines.append(note)
        if kind == "interface" or (f & F_ABSTRACT):
            lines.append("%s%s;" % (mem, decl))
        elif body:
            lines.append("%s%s" % (mem, decl))
            lines.append("%s{" % mem)
            for bl in body.split("\n"):
                lines.append(mem + "  " + bl if bl.strip() else "")
            lines.append("%s}" % mem)
        else:
            lines.append("%s%s" % (mem, decl))
            lines.append("%s{" % mem)
            lines.append("%s}" % mem)


def fn_of(ns):
    return (ns or "_global") + ".cs"


def main():
    out_dir = "src"
    only_ns = None
    bodies = None
    a = sys.argv[1:]
    i = 0
    while i < len(a):
        if a[i] == "--out":
            out_dir = a[i + 1]; i += 2
        elif a[i] == "--ns":
            only_ns = a[i + 1]; i += 2
        elif a[i] == "--bodies":
            bodies = a[i + 1]; i += 2
        else:
            i += 1
    out_dir = os.path.join(HERE, out_dir)

    g = Gen()
    print("载入元数据 …")
    g.load_types()
    g.load_fields()
    g.load_field_defaults()
    g.load_layout()
    g.load_methods()
    g.load_generic()
    g.load_props_events()
    g.load_gnames()
    g.load_nested()
    print("  类型 %d / 有布局字段 %d / 方法组 %d / 方法地址 %d / 泛型形参 %d"
          % (len(g.types), len(g.layout), len(g.methods), len(g.maddr),
             len(g.gp_type) + len(g.gp_meth)))
    if bodies:
        g.load_bodies(bodies)

    groups = collections.defaultdict(list)
    for ti in sorted(g.types):
        groups[g.types[ti]["ns"]].append(ti)

    os.makedirs(out_dir, exist_ok=True)
    idx_lines = ["# 源码索引", "",
                 "由 `gen_cs.py` 从还原后的元数据生成。共 **%d** 个类型 / **%d** 个命名空间。"
                 % (len(g.types), len(groups)), "",
                 "| 命名空间 | 类型数 | 方法数 | 文件 |", "|---|---:|---:|---|"]

    total_types = 0
    total_methods = 0
    hit_body = 0
    entries = []          # 类型级索引：供源码浏览器按行号切片
    g_spans = {}          # ti -> (文件名, 起始行 1-based, 行数)；嵌套类型也在此
    emitted = set()       # 已输出的类型（含递归带出的嵌套类型）
    for ns in sorted(groups):
        if only_ns and ns != only_ns:
            continue
        tis = groups[ns]
        out = []
        n_meth = sum(len(g.methods.get(ti, [])) for ti in tis)
        out.append("// <auto-generated>")
        out.append("// 由 global-metadata.dat 解密还原 + 原生代码布局求解生成，非原始源码。")
        out.append("// 命名空间: %s   类型: %d   方法: %d" % (ns or "<全局>", len(tis), n_meth))
        out.append("// </auto-generated>")
        out.append("")
        if ns:
            out.append("namespace %s" % ns)
            out.append("{")
        spans = {}
        for ti in tis:
            if ti in g.nest_parent:
                continue          # 嵌套类型由父类型递归输出，不单独占位
            g.emit_type(ti, out, 0, spans)
        if ns:
            out.append("}")
        fn = fn_of(ns)
        with open(os.path.join(out_dir, fn), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(out) + "\n")
        for ti, (st, en) in spans.items():
            g_spans[ti] = (fn, st + 1, en - st)
            emitted.add(ti)
        for ti in tis:
            for m in g.methods.get(ti, []):
                r = g.maddr.get(m["idx"])
                if r is not None and r in g.bodies:
                    hit_body += 1
        total_types += len(tis)
        total_methods += n_meth
        idx_lines.append("| `%s` | %d | %d | [%s](%s) |"
                         % (ns or "<全局>", len(tis), n_meth, fn, fn))

    # 类型级索引（全局收集，因为嵌套类型落在父类型所在文件里）
    for ti in sorted(g_spans):
        fn, start, n = g_spans[ti]
        t = g.types[ti]
        k, nm, _b = g.type_decl(ti)
        entries.append([t["ns"], t["name"], nm, k, fn, start, n,
                        len(g.methods.get(ti, [])), t["token"],
                        g.tsize.get(ti, 0), g.tconf.get(ti, ""),
                        g.nest_parent.get(ti, -1)])

    with open(os.path.join(out_dir, "_index.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(idx_lines) + "\n")

    import json
    with open(os.path.join(out_dir, "_index.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"types": entries,
                   "nested": len(g.nest_parent),
                   "namespaces": {ns: [len(v), sum(len(g.methods.get(t, [])) for t in v)]
                                  for ns, v in groups.items()}},
                  f, ensure_ascii=False, separators=(",", ":"))

    print("生成完成：%d 个类型 / %d 个方法 / %d 个文件 -> %s"
          % (total_types, total_methods, len(groups), out_dir))
    print("  嵌套类型已归位 %d 个（%d 个父类型），索引覆盖 %d 个类型"
          % (len(g.nest_parent), len(g.nest_kids), len(entries)))
    if len(emitted) < total_types:
        print("  [warn] 有 %d 个类型未落盘（父类型被 --ns 过滤掉）"
              % (total_types - len(emitted)))
    if bodies:
        print("  其中 %d 个方法填入了反编译体（%.1f%%）"
              % (hit_body, 100.0 * hit_body / max(1, total_methods)))


if __name__ == "__main__":
    main()
