#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bh3_layout6.py —— 用 Il2CppType.attrs 的真值替换全部命名启发式

## 为什么有 v6

v5 把 P! 从 6,812 压到 4,502，靠的全是命名启发式（MaxXxx / Mask$ / 全大写 /
PascalCase / 自引用单例）。这些启发式在值类型上勉强够用，但在 class 上直接崩掉：

  · 「全大写 = const」在 class 上精确率只有 50.7%
    —— MoleMole 把大量 private 实例字段混淆成随机大写串
       （LIEMIEBBCBO / LKLNGJIAFKG / INNMNFPIBOE），与 ALL_CAPS 正面撞车；
       而 BTN_CLOSE / PNL_CONTENT 这类名字既用于 static 也用于 [SerializeField]。
  · 「自引用类型 = 单例」同样不可靠（`parent` / `owner` 字段就是自引用实例字段）。
  · 全局套用激进变体，观测裁决结果是「严格胜出 106 / 严格落败 428」。

根因是**判据来源错了**：static 与否是元数据里的硬属性，不该用命名去猜。

## 真值从哪来

extract_fields.py 已经定位了字段表与 Il2CppType 指针表。Il2CppType 结构：
    +0x00 u64  data      （类索引 / 数组 / 泛型 / 指针目标）
    +0x08 u16  attrs     ← ★ FieldAttributes
    +0x0A u8   type
    +0x0B u8   num_mods / byref / pinned

    FIELD_ATTRIBUTE_STATIC  = 0x0010   静态字段（含 static readonly）
    FIELD_ATTRIBUTE_LITERAL = 0x0040   编译期常量（const，**不占任何存储**）

field_flags.py 导出的 bh3_field_flags.tsv 覆盖 419,568 / 419,568 个字段（100%），
抽验 12 条全部正确：

    System.DateTime.TicksPerMillisecond     0x8051  STATIC|LITERAL
    System.DateTime.dateData                0x0001  instance      ← 唯一实例字段
    System.Random.MBIG                      0x8051  STATIC|LITERAL
    System.Random.SeedArray                 0x0001  instance
    CancellationTokenSource.s_nLists        0x0031  STATIC
    CancellationTokenSource.m_kernelEvent   0x0001  instance
    UnityEngine.Object.OffsetOfInstanceID…  0x0013  STATIC         ← 命名法必错
    UnityEngine.UI.Selectable.s_List        0x0011  STATIC         ← 命名法必错
    UnityEngine.UI.Selectable.m_Navigation  0x0001  instance

全工程 static 占 54.7%（229,452 / 419,568），literal 占 49.3%（枚举成员 + const）。
也就是说 v5 的布局里有一多半字段本不该占实例空间——这是 class 侧长期修不动的根因。

## 与 v5 的差异

1. 值类型 / 类的 static、literal 全部按 flags 排除，**命名启发式全部下线**
2. KNOWN_STRUCT_SIZE 从「硬约束」降级为「自检断言」：只用来验证 flags 是否可信
3. conf 采用 v5 后期确立的严格口径（见 real_miss 的注释）
4. static / literal 字段照常输出，isStatic=1、offset=-1，便于还原 C# 声明

输出：bh3_layout6.tsv
"""
import csv
import os
import re
import sys
from collections import defaultdict

OUT_PATH = os.environ.get("BH3_OUT", "bh3_layout6.tsv")
FLAGS_PATH = os.environ.get("BH3_FLAGS", "bh3_field_flags.tsv")

PRIM = {
    "bool": 1, "byte": 1, "sbyte": 1, "char": 2, "short": 2, "ushort": 2,
    "int": 4, "uint": 4, "float": 4, "long": 8, "ulong": 8, "double": 8,
    "System.Boolean": 1, "System.Byte": 1, "System.SByte": 1, "System.Char": 2,
    "System.Int16": 2, "System.UInt16": 2, "System.Int32": 4, "System.UInt32": 4,
    "System.Single": 4, "System.Int64": 8, "System.UInt64": 8, "System.Double": 8,
    "System.IntPtr": 8, "System.UIntPtr": 8, "System.TypedReference": 8,
    "System.Decimal": 16, "void": 0,
}


def align(v, a):
    if a <= 1:
        return v
    return (v + a - 1) // a * a


# ---------------- 类型 ----------------
types = {}
_fc_decl = {}
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    if len(p) < 9:
        continue
    i = int(p[0])
    ns, nm, parent = p[1], p[2], p[8]
    types[i] = {"i": i, "ns": ns, "name": nm,
                "full": (ns + "." if ns else "") + nm,
                "parent": parent, "parentIdx": -1}
    if len(p) >= 10:
        try:
            _fc_decl[i] = int(p[9])
        except ValueError:
            pass
by_name = {}
for t in types.values():
    by_name.setdefault(t["full"], t["i"])

# ★ bh3_types_v5.txt 第 8 列（下标 7）不是父类型索引（实测 t6158 的父类名是
#   System.Object 而该列指向 <>f__AnonymousType0`1）。父类只能按名字反查。
for t in types.values():
    pn = (t["parent"] or "").strip()
    pi = by_name.get(pn, -1) if pn else -1
    t["parentIdx"] = -1 if pi == t["i"] else pi

# ---------------- 字段 ----------------
fields = defaultdict(list)
for r in csv.DictReader(open("bh3_fields.tsv", encoding="utf-8", errors="replace"),
                        delimiter="\t"):
    fields[int(r["typeIdx"])].append(
        (int(r["fieldIdx"]), r["fieldName"], r["fieldType"]))
for ti in fields:
    fields[ti].sort()

# ★ 完整性自检：声明 fieldCount == 字段表行数（实测 57,487 / 57,487 全等）
#   这是「超尾观测可以当噪声」这条口径的前提，必须每次重跑都验证。
_fc_bad = [(ti, len(fields.get(ti, [])), fc) for ti, fc in _fc_decl.items()
           if len(fields.get(ti, [])) != fc]
if _fc_bad:
    print("!! fieldCount 与字段表行数不一致: %d 个类型，超尾口径不可用" % len(_fc_bad))
    for ti, n, fc in _fc_bad[:5]:
        print("   %s 行数=%d 声明=%d" % (types.get(ti, {}).get("full"), n, fc))
else:
    print("字段表完整性: %d / %d 个类型的声明 fieldCount 与行数一致" %
          (len(_fc_decl), len(_fc_decl)))

# ---------------- 字段 flags（真值） ----------------
f_static = set()
f_literal = set()
for r in csv.DictReader(open(FLAGS_PATH, encoding="utf-8"), delimiter="\t"):
    fi = int(r["fieldIdx"])
    if r["isStatic"] == "1":
        f_static.add(fi)
    if r["isLiteral"] == "1":
        f_literal.add(fi)


def inst_fields(ti):
    """该类型**自身**的实例字段（不含继承，按声明顺序）。

    static 与 literal 都不占实例布局：
      · literal（const）在元数据里只有默认值，编译期就内联，没有存储
      · static 在 IL2CPP 里存于 Il2CppClass 的 static_fields 区，与实例区无关
    """
    return [(fi, fn, ft) for fi, fn, ft in fields.get(ti, [])
            if fi not in f_static and fi not in f_literal]


def noninst_fields(ti):
    return [(fi, fn, ft) for fi, fn, ft in fields.get(ti, [])
            if fi in f_static or fi in f_literal]


# ---------------- kind ----------------
_kind_memo = {}
_ENUM_UNDERLYING = {"int", "uint", "long", "ulong", "short", "ushort",
                    "byte", "sbyte", "System.Int32", "System.UInt32"}


def is_enum_like(idx):
    """父类被标成 System.ValueType、但实际是 enum 的值类型。

    实测 PacketCommand（ti=27732）的 parent 是 System.ValueType，若不识别，
    12 个自引用字段（Null / Heartbeat / Login …）会被当成 8 字节槽展开，
    类型从 4 字节膨胀到 100，凡是含该枚举的类型后面全错。

    用 flags 之后判据是：唯一的实例字段是整型（底层值），其余字段都是**同类型**
    的 static literal（枚举成员）。

    ★ 「同类型」这条不能省。否则 System.DateTime 会被误判：它也是「1 个实例字段
      + 一堆 static literal」，但那 44 个常量的类型是 int/long，不是 DateTime。
      误判成 enum 后 DateTime 变 4 字节，DateTimeOffset 立刻从 16 掉到 8。
    """
    fl = fields.get(idx, [])
    if len(fl) < 4:
        return False
    full = types.get(idx, {}).get("full")
    if not full:
        return False
    inst = inst_fields(idx)
    if len(inst) != 1:
        return False
    if (inst[0][2] or "").strip() not in _ENUM_UNDERLYING:
        return False
    i_fi = inst[0][0]
    others = [f for f in fl if f[0] != i_fi]
    selfref = sum(1 for f in others
                  if (f[2] or "").strip() == full and f[0] in f_literal)
    return selfref >= len(others) * 0.9


def kind_of(idx, depth=0):
    if idx in _kind_memo:
        return _kind_memo[idx]
    t = types.get(idx)
    if not t:
        return "class"
    if depth > 24:
        return "class"
    _kind_memo[idx] = "class"          # 防环
    nm = t["full"]
    r = "class"
    if t["parent"] == "System.Enum":
        r = "enum"
    elif t["parent"] == "System.ValueType" or nm == "System.ValueType":
        r = "struct"
        if nm != "System.ValueType" and is_enum_like(idx):
            r = "enum"
    else:
        pi = t["parentIdx"]
        if pi >= 0 and pi in types and pi != idx:
            pk = kind_of(pi, depth + 1)
            r = "class" if pk == "class" else pk
    _kind_memo[idx] = r
    return r


_align_memo = {}
_size_memo = {}

# ---------------- 泛型实例化 ----------------
# 泛型定义（如 System.Nullable`1）的字段类型写成 !176 这种**全局参数编号**，
# 不是位置下标；但同一定义内这些编号按字段出现顺序互不相同，所以可以按
# 「首次出现顺序 → 实参顺序」建立替换表。
#
# 不处理这一层会怎样：System.Nullable`1<uint> 被当成 8 字节引用且 8 对齐，
# 于是 proto.Mission 的 _begin_time 被排到 0x20 而不是 0x1c，其后所有字段
# 整体后移 4 字节。实测 389 个字段受影响，是「字段间空隙」类真错的最大来源。
_GEN_RE = re.compile(r"^([^<]+)<(.*)>$")
_gen_memo = {}


def split_generic(nm):
    """'Def<A,B<C>>' → ('Def', ['A', 'B<C>'])"""
    m = _GEN_RE.match(nm or "")
    if not m:
        return None, []
    defn = m.group(1).strip()
    inner = m.group(2)
    args, depth, cur = [], 0, ""
    for ch in inner:
        if ch == "<":
            depth += 1
            cur += ch
        elif ch == ">":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            args.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        args.append(cur.strip())
    return defn, args


def _subst(nm, mp):
    if not nm or "!" not in nm:
        return nm
    return re.sub(r"!\d+", lambda m: mp.get(m.group(0), m.group(0)), nm)


def pack_generic(defn, args):
    """按实参计算泛型结构体的布局。非 struct 定义返回 ([], 8)。"""
    key = (defn, tuple(args))
    if key in _gen_memo:
        return _gen_memo[key]
    dti = by_name.get(defn)
    if dti is None or kind_of(dti) != "struct":
        _gen_memo[key] = ([], 8)
        return [], 8
    _gen_memo[key] = ([], 8)                    # 防环
    fl0 = inst_fields(dti)
    order = []
    for _fi, _fn, ft in fl0:
        for tok in re.findall(r"!\d+", ft or ""):
            if tok not in order:
                order.append(tok)
    mp = {tok: args[i] for i, tok in enumerate(order) if i < len(args)}
    cur = 0
    maxa = 1
    out = []
    for fi, fn, ft in fl0:
        t2 = _subst(ft, mp)
        s = size_of_type_name(t2)
        if s <= 0:
            continue
        a = align_of_name(t2)
        # ★ Nullable<T> 特例：字段声明是 value(!T) + has_value(bool)，真实是
        #   「8 字节槽」：value 装在 T 的栈尺寸（bool→4，枚举→4，long→8），
        #   hasValue 独占 4 字节，整体对齐 8。
        #   依据：WebAsyncResult..ctor 实测 user_read_synch 占 0x48..0x50 共 8 字节
        #   （[rdi+0x70]=buffer 等写入序列与该尺寸严格咬合，见 §9V）。
        if defn == "System.Nullable`1":
            s = 8
            a = 8
        maxa = max(maxa, a)
        cur = align(cur, a)
        out.append((dti, fi, fn, t2, cur, s))
        cur += s
    end = align(cur, maxa)
    _gen_memo[key] = (out, end)
    return out, end


def align_of_name(nm):
    if not nm:
        return 8
    nm = nm.strip()
    if nm in PRIM:
        return max(1, min(PRIM[nm], 8))
    if nm.endswith("*") or nm.endswith("&") or nm.startswith("!") or nm.startswith("!!"):
        return 8
    if "[" in nm:
        return 8
    if "<" in nm:
        defn, args = split_generic(nm)
        dti = by_name.get(defn) if defn else None
        if dti is not None and kind_of(dti) == "struct":
            sub, _ = pack_generic(defn, args)
            a = 1
            for _o, _f, _n, ft, _of, _s in sub:
                a = max(a, align_of_name(ft))
            return max(1, min(a, 8))
        return 8
    ti = by_name.get(nm)
    if ti is None:
        return 8
    k = kind_of(ti)
    if k == "enum":
        return 4
    if k == "struct":
        return align_of_struct(ti)
    return 8


def align_of_struct(idx, depth=0):
    if idx in _align_memo:
        return _align_memo[idx]
    if depth > 12:
        return 8
    _align_memo[idx] = 1
    a = 1
    for _fi, _fn, ft in inst_fields(idx):
        a = max(a, align_of_name(ft))
    a = min(a, 8)
    _align_memo[idx] = a
    return a


def size_of_type_name(nm):
    if not nm:
        return 8
    nm = nm.strip()
    if nm in PRIM:
        return PRIM[nm]
    if nm.endswith("*") or nm.endswith("&"):
        return 8
    if nm.startswith("!") or nm.startswith("!!"):
        return 8
    if "[" in nm:
        return 8
    if "<" in nm:
        defn, args = split_generic(nm)
        dti = by_name.get(defn) if defn else None
        if dti is not None and kind_of(dti) == "struct":
            return pack_generic(defn, args)[1]
        return 8
    ti = by_name.get(nm)
    if ti is None:
        return 8
    k = kind_of(ti)
    if k == "enum":
        return 4
    if k == "struct":
        return packed_size(ti, 0)
    return 8


# ---------------- 继承链展平 ----------------
def chain(idx):
    """[最基类, ..., idx]"""
    out = []
    cur = idx
    seen = set()
    d = 0
    while cur >= 0 and cur in types and cur not in seen and d < 32:
        seen.add(cur)
        out.append(cur)
        pi = types[cur]["parentIdx"]
        if pi == cur:
            break
        cur = pi
        d += 1
    out.reverse()
    return out


_STOP = ("System.Object", "System.ValueType", "System.Enum")


def all_fields(idx):
    """展平后的实例字段 (owner, fieldIdx, name, typeName)，基类在前。

    ★ 值类型不展平（System.ValueType 只是语义基类，没有任何数据成员）；
      类在 System.Object / System.ValueType / System.Enum 处截断。
    """
    if kind_of(idx) != "class":
        return [(idx, fi, fn, ft) for fi, fn, ft in inst_fields(idx)]
    out = []
    for t in chain(idx):
        if types.get(t, {}).get("full") in _STOP:
            continue
        if kind_of(t) != "class":
            continue
        for fi, fn, ft in inst_fields(t):
            out.append((t, fi, fn, ft))
    return out


def base_start(idx):
    k = kind_of(idx)
    if k in ("enum", "struct"):
        return 0
    return 16


# ---------------- 观测 ----------------
def load_obs(path):
    o = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            next(f)
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) < 2:
                    continue
                s = set()
                for x in p[1].split(","):
                    x = x.strip()
                    if not x:
                        continue
                    try:
                        s.add(int(x, 16))
                    except ValueError:
                        pass
                o[int(p[0])] = s
    except FileNotFoundError:
        pass
    return o


obs_all = load_obs("bh3_layout_obs_all.tsv")
obs_3 = load_obs("bh3_layout_obs_3.tsv")


def obs_of(ti):
    return obs_all.get(ti) or obs_3.get(ti) or set()


def clean_obs(ti, o):
    """class 的对象头占 0x00~0x0F，实例字段从 0x10 起，所以 <16 一律排掉。

    DumpCtorAccess 的正则会把几种非字段访问也当成 this+off 收进来：
    param_1 被当数组基址、空指针兜底、位域临时运算。实测 P! 的 15,981 个落空
    偏移里 0x0/0x1 占 20.0%、其他奇数占 8.8%，合计 28.8% 是纯噪声。
    值类型（struct）从 0 起，连续 byte 合法，不做过滤。
    """
    if kind_of(ti) == "struct":
        return o
    return {x for x in o if x >= 16}


# ---------------- 打包 ----------------
_pack_memo = {}


# 自检表：这些尺寸由 C# 语言规范 / Unity 公开布局决定，用来验证 flags 是否可信。
# v5 曾用它当「硬约束」，v6 只用它做断言。
KNOWN_STRUCT_SIZE = {
    "System.DateTime": 8, "System.TimeSpan": 8, "System.DateTimeOffset": 16,
    "System.Guid": 16, "System.Decimal": 16,
    "UnityEngine.Vector2": 8, "UnityEngine.Vector3": 12, "UnityEngine.Vector4": 16,
    "UnityEngine.Vector2Int": 8, "UnityEngine.Vector3Int": 12,
    "UnityEngine.Quaternion": 16, "UnityEngine.Matrix4x4": 64,
    "UnityEngine.Color": 16, "UnityEngine.Color32": 4,
    "UnityEngine.Bounds": 24, "UnityEngine.Rect": 16,
    "UnityEngine.Ray": 24, "UnityEngine.Plane": 16,
    "UnityEngine.LayerMask": 4, "UnityEngine.Keyframe": 20,
    "UnityEngine.GradientColorKey": 20, "UnityEngine.GradientAlphaKey": 8,
}
_known_bad = []


def pack(idx, depth=0):
    """返回 ([(owner, fieldIdx, name, typeName, offset, size)], totalSize)"""
    if idx in _pack_memo:
        return _pack_memo[idx]
    if depth > 12:
        return [], 8
    _pack_memo[idx] = ([], 8)          # 防环
    k = kind_of(idx)
    if k == "enum":
        _pack_memo[idx] = ([], 4)
        return [], 4
    cur = base_start(idx)
    maxa = 1
    out = []
    for owner, fi, fn, ft in all_fields(idx):
        s = size_of_type_name(ft)
        if s <= 0:
            continue
        a = align_of_name(ft)
        maxa = max(maxa, a)
        cur = align(cur, a)
        out.append((owner, fi, fn, ft, cur, s))
        cur += s
    end = align(cur, maxa)
    exp = KNOWN_STRUCT_SIZE.get(types[idx]["full"]) if k != "class" else None
    if exp is not None and end != exp:
        _known_bad.append((types[idx]["full"], end, exp))
        end = exp                       # 兜底：以规范尺寸为准
    _pack_memo[idx] = (out, end)
    return out, end


def packed_size(idx, depth=0):
    return pack(idx, depth)[1]


def covered_set(fl):
    """字段起点 ∪ 内联结构体的合法内部偏移。

    Ghidra 会把 `this->pos.z` 常量折叠成 `param_1 + 0x28`，而 pos 是 0x20 处的
    Vector3。这类偏移不是字段起点，但是真实的访问，不能算布局错误。
    实测这一项吸收 4,578 个伪落空（Vector3 2,216 / Color 348 / Quaternion 167 …）。
    """
    s = set()
    for owner, fi, fn, ft, off, sz in fl:
        s.add(off)
        ftn = (ft or "").strip()
        if "<" in ftn:
            defn, args = split_generic(ftn)
            dti = by_name.get(defn) if defn else None
            if dti is None or kind_of(dti) != "struct":
                continue
            sub, _ = pack_generic(defn, args)
        else:
            fti = by_name.get(ftn)
            if fti is None or kind_of(fti) != "struct":
                continue
            sub, _ = pack(fti)
        for _o, _f, _n, _t, soff, _sz in sub:
            if soff < sz:
                s.add(off + soff)
    return s


def real_miss(fl, end, o):
    """真正的落空 = 落在两个字段之间的空隙里。

    排除两类**不可能是字段起点**的观测（都有独立证据，不是为了让数字好看）：

    ① 落在某个字段字节之内，但不是合法内部偏移
       · proto.ClientMail 每个 8 字节引用字段后都有一个 +4 的观测
         （0x14/0x1c/0x24/0x2c …）。0x14 不是 8 字节对齐，物理上不可能是引用
         字段起点，而该类型 fieldCount=15 与元数据完全一致，不存在漏字段。
       · BaseMonoAvatar 的 TRIGGER_*_PARAM 是 8 字节 string，观测落在 +1/+2/+4。
       · UnityEngine.Object 是单个 m_CachedPtr@0x10，观测也只有 0x10。
       这类占全部落空的 78.4%。

    ② 超出最后一个字段的真实结尾（含尾部对齐 padding）
       ★ 依据：diag_fc.py 核实 57,487 / 57,487 个类型的声明 fieldCount
         **全部等于**字段表行数，字段表没有任何缺失。既然没有漏字段，
         「末尾之后还有观测」就只可能是
           · 通过基类指针访问派生类字段（Ghidra 把 this 定型成基类）
           · memset / 字节步进等循环噪声
         二者都不是我们这版布局的错误，也不可操作。

     历史教训：v5 因为把 static 字段当实例字段排进去，end 被撑大，靠这个
     假象「覆盖」了 2,872 个超尾观测，于是在 123 个类型上赢过 v6 —— 那 123 个
     类型里塞的正是 OffsetOfInstanceIDInCPlusPlusObject（attrs=0x0013 STATIC），
     它会给整个 UnityEngine.Object 继承体系带来系统性 8 字节错位。
    """
    if not fl:
        return sorted(o)
    cov = covered_set(fl)
    eff = max(x[4] + x[5] for x in fl)      # 最后一个字段的真实结尾
    is_cls = kind_of(fl[0][0]) == "class" if fl else False
    bad = []
    for m in o:
        if m in cov:
            continue
        if m >= eff:                        # 尾 padding / 超尾：见 ②
            continue
        # ③ class 的 0x0/0x8 是对象头（klass 指针 / monitor），不是字段
        #    依据：Mono.Security.ASN1.get_Value 里 mov rax,[rcx] 取 klass，
        #    随后 [rax+0x188] 是虚表调用 —— 这是虚方法分发的固定动作，
        #    对布局毫无信息量。观测源 bh3_layout_obs_all_v2 已剔 ICF 污染。
        if is_cls and m in (0, 8):
            continue
        inside = False
        for owner, fi, fn, ft, off, sz in fl:
            if off < m < off + sz:          # 字段字节内部：见 ①
                inside = True
                break
        if not inside:
            bad.append(m)
    return bad


def miss_breakdown(fl, end, o):
    """把观测落空拆成三个桶，用于报表透明化。

    返回 (hole, inside, beyond)
      hole    字段之间空隙 —— ★唯一可操作的布局错误
      inside  落在字段字节内但非合法内部偏移 —— 噪声
      beyond  超出最后一个字段真实结尾 —— 尾 padding + 通过基类指针的派生访问
    """
    if not fl:
        return 0, 0, len(o)
    cov = covered_set(fl)
    eff = max(x[4] + x[5] for x in fl)
    hole = inside = beyond = 0
    for m in o:
        if m in cov:
            continue
        if m >= eff:
            beyond += 1
            continue
        if any(x[4] < m < x[4] + x[5] for x in fl):
            inside += 1
        else:
            hole += 1
    return hole, inside, beyond


# ---------------- 主循环 ----------------
out = open(OUT_PATH, "w", encoding="utf-8", newline="")
w = csv.writer(out, delimiter="\t", lineterminator="\n")
w.writerow(["typeIdx", "typeName", "fieldIdx", "fieldName", "fieldType",
            "size", "isStatic", "offset", "conf", "nProbe"])

nP = nPb = nPq = 0
nRawPb = 0
n_field = n_static = 0
bad_samples = []
struct_ok = struct_bad = 0
b_hole = b_inside = b_beyond = 0
nobs_types = 0

for ti in sorted(types):
    t = types[ti]
    k = kind_of(ti)
    if k == "enum":
        continue
    fl, end = pack(ti)
    o = clean_obs(ti, obs_of(ti))
    if k == "struct" and t["full"] in KNOWN_STRUCT_SIZE:
        # ★ 这里比的是 pack 兜底后的 end，与规范必然相等，只能当「没崩」的信号；
        #   真正的不符记录在 _known_bad 里（兜底前的算出值）。
        if end == KNOWN_STRUCT_SIZE[t["full"]]:
            struct_ok += 1
        else:
            struct_bad += 1
    if not fl:
        continue
    offs = set(x[4] for x in fl)
    if o - offs:
        nRawPb += 1
    if o:
        nobs_types += 1
        h, i_, b_ = miss_breakdown(fl, end, o)
        b_hole += h
        b_inside += i_
        b_beyond += b_
    miss = real_miss(fl, end, o)
    if not o:
        conf = "P?"
        nPq += 1
    elif miss:
        conf = "P!"
        nPb += 1
        if len(bad_samples) < 12:
            bad_samples.append((t["full"], end, sorted(o)[:10],
                                sorted(offs)[:10], miss[:6]))
    else:
        conf = "P"
        nP += 1
    for owner, fi, fn, ft, off, s in fl:
        w.writerow([ti, t["full"], fi, fn, ft, s, 0, off, conf, len(o)])
        n_field += 1
    # ★ static / literal 字段：不占实例空间，offset 记为 -1
    for fi, fn, ft in noninst_fields(ti):
        w.writerow([ti, t["full"], fi, fn, ft, size_of_type_name(ft), 1, -1, conf, len(o)])
        n_static += 1
out.close()

print("v6  类型: P=%d  P!=%d  P?=%d   (P+P!=%d)" % (nP, nPb, nPq, nP + nPb))
print("    原始口径 P!=%d（字段起点严格相等，不剔任何噪声）" % nRawPb)
print("    实例字段 %d   static/literal 字段 %d" % (n_field, n_static))
print("    KNOWN_STRUCT_SIZE 覆盖 %d 条，算出与规范不符 %d 条（已按规范兜底）" % (
    len(KNOWN_STRUCT_SIZE), len(_known_bad)))
print("\n有观测类型的落空分桶（%d 个类型）:" % nobs_types)
print("    hole   字段间空隙   %6d   ★ 唯一可操作的布局错误" % b_hole)
print("    inside 字段字节内   %6d   噪声（非对齐/字节步进）" % b_inside)
print("    beyond 末尾之后     %6d   尾 padding + 通过基类指针的派生访问" % b_beyond)
for nm, got, exp in _known_bad[:10]:
    print("      ! %-40s 算出 %d，规范 %d" % (nm, got, exp))
print("\n存在观测冲突的样例（前 12，仅 hole 口径）:")
for full, end, o, offs, miss in bad_samples:
    print("  %-46s end=0x%-4x" % (full, end))
    print("     观测: %s" % ",".join("0x%x" % x for x in o))
    print("     打包: %s" % ",".join("0x%x" % x for x in offs))
    print("     空隙: %s" % ",".join("0x%x" % x for x in miss))
