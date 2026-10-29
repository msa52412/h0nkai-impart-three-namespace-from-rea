#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bh3_layout5.py —— 在 v4 的「声明顺序 + 对齐打包」基础上，修掉值类型的静态常量污染

v4 的问题（实测）：
  System.DateTime 被算出 **280 字节**，因为它元数据里有 45 个字段，其中 44 个是
  static readonly 常量（TicksPerMillisecond / MaxTicks / KindUtc / TicksMask …），
  只有最后那个 `dateData : ulong` 才是真正的实例字段。真实 DateTime 是 8 字节。
  这一个错误会级联污染所有含 DateTime 的类型（DateTimeOffset / DateMapping /
  TransitionTime / X509Certificate …），进而让几千个 class 的偏移整体错位。

v5 的改动，只碰值类型（class 的打包逻辑一字未改）：
  1) 新增 is_const_like()：按 .NET / Mono 的常量命名惯例识别 static readonly，
     比 v4 的「自引用类型 + kXxx」两条判据强得多
  2) 值类型里，名字像常量的基元字段直接排除出实例布局
  3) 值类型尺寸做「观测校准」：若打包尺寸远超观测跨度，说明仍有常量残留，
     从尾部回退到观测能证实的边界
  4) class 若引用了尺寸被修正的值类型，自动跟着修正（因为 pack 是递归 + memo 的）

conf 语义沿用 v4：
  P   打包覆盖全部观测偏移
  P!  有观测偏移落空
  P?  该类型无观测

输出：bh3_layout5.tsv（不覆盖 v4，便于对比与回退）

v4 已验证有效的部分（保留）：
  proto.BulletinActivityConfig（构造函数 0x186637860）逐条核对，22 个字段
  全部是实例字段、零 static，纯声明顺序对齐打包完全吻合：
    0x10 → activity_id + activity_type      0x40 → min_player_level + max_player_level
    0x18 → begin_time + end_time            0x48 → item_list
    0x20 → bulletin_id                      0x50..0x70 → title_name/title_image/image_path/...
    0x28 → mission_ids                      0x78 → weight
    0x30 → type_param_list                  0x80,0x88 → background_path / text_image_path
    0x38 → type_param_str                   0x90 → currency_list
                                            0x98 → unlock_param_str
    （extensionObject 构造函数没写 → 在 0xA0，实例尺寸 0xA8=168）
"""
import csv
import os
import re
import sys
from collections import defaultdict

# 实验开关：不设默认值，默认行为与 v5 完全一致，便于 A/B 与回退
#   BH3_OUT=xxx.tsv        输出文件名（默认 bh3_layout5.tsv）
#   BH3_CLASS_STATIC=1     class 也应用常量/static 命名判据（v6 手术刀）
OUT_PATH = os.environ.get("BH3_OUT", "bh3_layout5.tsv")
CLASS_STATIC = os.environ.get("BH3_CLASS_STATIC") == "1"
# 位掩码：1=自引用单例 2=kXxx 4=全大写+下划线 8=s_ 前缀
CS_MASK = int(os.environ.get("BH3_CS_MASK", "15"))
# 变体择优：对每个「有观测的 class」分别用这些变体打包，取落空最少的那个。
# 空串表示关闭择优、全部使用 CS_MASK。
CS_VARIANTS = [int(x) for x in os.environ.get("BH3_CS_VARIANTS", "0,15").split(",") if x != ""]
CS_DEFAULT_VARIANT = CS_MASK

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
for line in open("bh3_types_v5.txt", encoding="utf-8", errors="replace").read().splitlines()[1:]:
    p = line.split("\t")
    if len(p) < 9:
        continue
    i = int(p[0])
    ns, nm, parent = p[1], p[2], p[8]
    types[i] = {"i": i, "ns": ns, "name": nm,
                "full": (ns + "." if ns else "") + nm,
                "parent": parent,
                "parentIdx": int(p[7]) if p[7] not in ("", "-1") else -1}
by_name = {}
for t in types.values():
    by_name.setdefault(t["full"], t["i"])

# ★ 注意：bh3_types_v5.txt 第 8 列（下标 7）不是父类型索引 ——
#   实测 t6158 的父类名是 System.Object，而该列值为 1（指向 <>f__AnonymousType0`1），
#   按它走继承链会把无关字段继承进来，把整张表的偏移推后 8 字节。
#   父类只能按名字反查。
for t in types.values():
    pn = (t["parent"] or "").strip()
    pi = by_name.get(pn, -1) if pn else -1
    if pi == t["i"]:
        pi = -1
    t["parentIdx"] = pi

# ---------------- 字段 ----------------
fields = defaultdict(list)
with open("bh3_fields.tsv", encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        fields[int(r["typeIdx"])].append(
            (int(r["fieldIdx"]), r["fieldName"], r["fieldType"]))
for ti in fields:
    fields[ti].sort()

# ---------------- kind ----------------
_kind_memo = {}


_ENUM_UNDERLYING = {"int", "uint", "long", "ulong", "short", "ushort",
                    "byte", "sbyte", "System.Int32", "System.UInt32"}


def is_enum_like(idx):
    """识别「父类被标成 System.ValueType、但实际是 enum」的类型。

    实测 PacketCommand（ti=27732）的 parent 是 System.ValueType，照理会当 struct 处理；
    但它的 13 个字段里 12 个的类型就是 PacketCommand 自身（Null / Heartbeat / Login …
    这些枚举成员），只剩一个 CommandCode : uint 是真正的底层值。这是 enum 的典型
    形态（il2cpp 里枚举成员表现为同类型 static literal）。

    不识别出来的后果：v5 会把 12 个「自引用」字段按 struct 展开成 12 个 8 字节槽，
    PacketCommand 从 4 字节膨胀到 100，凡是含该枚举字段的类型（如游戏协议头 ID）
    后面全部错位。

    ★ 判据必须同时满足三条，否则会误伤：
      · 非自引用字段**恰好 1 个**，且是整型（enum 的底层值）
      · 该字段占多数以外，自引用占比 >= 70%
      · 总字段数 >= 4
      反例：UnityEngine.Vector3 有 3 个 float（x/y/z）+ 若干自引用单例
      （zeroVector / oneVector / upVector），非自引用字段不是 1 个，必须排除；
      System.DateTimeOffset 有 m_dateTime / m_offsetMinutes 两个，同样排除。
    """
    fl = fields.get(idx, [])
    if len(fl) < 4:
        return False
    full = types.get(idx, {}).get("full")
    if not full:
        return False
    self_ref = 0
    others = []
    for _fi, _fn, ft in fl:
        t = (ft or "").strip()
        if t == full:
            self_ref += 1
        else:
            others.append(t)
    if len(others) != 1 or others[0] not in _ENUM_UNDERLYING:
        return False
    return self_ref >= len(fl) * 0.7


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
            r = "enum"                 # 父类标错的值类型，实际是 enum
    else:
        pi = t["parentIdx"]
        if pi >= 0 and pi in types and pi != idx:
            pk = kind_of(pi, depth + 1)
            r = "class" if pk == "class" else pk
    _kind_memo[idx] = r
    return r


_align_memo = {}
_size_memo = {}


def align_of_name(nm):
    if not nm:
        return 8
    nm = nm.strip()
    if nm in PRIM:
        return max(1, min(PRIM[nm], 8))
    if nm.endswith("*") or nm.endswith("&") or nm.startswith("!") or nm.startswith("!!"):
        return 8
    if "[" in nm or "<" in nm:
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
    for _fi, _fn, ft in fields.get(idx, []):
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
    if "[" in nm or "<" in nm:
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
def chain(idx, depth=0):
    """返回 [最基类, ..., idx]（去掉接口/System.Object 之前的）"""
    out = []
    cur = idx
    seen = set()
    while cur >= 0 and cur in types and cur not in seen and depth < 32:
        seen.add(cur)
        out.append(cur)
        pi = types[cur]["parentIdx"]
        if pi == cur:
            break
        cur = pi
        depth += 1
    out.reverse()
    return out


def all_fields(idx):
    """展平后的 (ownerTypeIdx, fieldIdx, name, typeName) 列表，基类在前

    ★ 值类型（struct）不展平：它的 parent 是 System.ValueType，那只是个语义基类，
      本身没有任何数据成员。若把它当基类继承，会把 System.ValueType 的字段排在
      偏移 0 之前，把 Vector3 撑成 96 字节（实测踩过）。
    ★ 类也要在 System.Object / System.ValueType / System.Enum 处截断。
    """
    if kind_of(idx) != "class":
        return [(idx, fi, fn, ft) for fi, fn, ft in fields.get(idx, [])]
    STOP = ("System.Object", "System.ValueType", "System.Enum")
    out = []
    for t in chain(idx):
        if types.get(t, {}).get("full") in STOP:
            continue
        if kind_of(t) != "class":
            continue
        for fi, fn, ft in fields.get(t, []):
            out.append((t, fi, fn, ft))
    return out


def base_start(idx):
    k = kind_of(idx)
    if k == "enum":
        return 0
    if k == "struct":
        return 0
    return 16


# ---------------- 观测 ----------------
# ★ 必须在 pack() 之前加载：pack 要据此决定「值类型的常量剔除可以多激进」。
#   有观测的值类型，观测能证实哪些字段真的占位，禁用命名启发式以免误伤
#   （实测 Option.Code / Value.SortKey 这类 PascalCase 实例字段会被误剔）；
#   没有观测的值类型才允许激进剔除（DateTime 那 44 个常量就属于这种情况）。
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
    o = obs_all.get(ti)
    if not o:
        o = obs_3.get(ti, set())
    return o


def clean_obs(ti, o):
    """过滤掉不可能落在实例区里的观测偏移。

    DumpCtorAccess 的正则会把几种非字段访问也当成 this+off 收进来：
      · class 的 0x0 / 0x1  —— 反编译里 param_1 被当成数组基址、或空指针兜底
      · 奇数偏移            —— 位域 / 临时指针运算
    实测 P! 类型的 15,981 个落空偏移里，0x0/0x1 占 20.0%、其他奇数占 8.8%，
    合计 28.8% 是纯噪声。class 的对象头占 0x00~0x0F，实例字段从 0x10 起，
    所以 <16 一律排除；值类型（struct）从 0 起，连续 byte 合法，不做过滤。
    """
    if kind_of(ti) == "struct":
        return o
    return {x for x in o if x >= 16}


# ---------------- 纯打包 ----------------
_pack_memo = {}


_SELF_STATIC = {}


_ALIAS = {
    "string": "System.String", "object": "System.Object",
    "bool": "System.Boolean", "byte": "System.Byte", "sbyte": "System.SByte",
    "char": "System.Char", "short": "System.Int16", "ushort": "System.UInt16",
    "int": "System.Int32", "uint": "System.UInt32", "long": "System.Int64",
    "ulong": "System.UInt64", "float": "System.Single", "double": "System.Double",
}

# 值类型里的 static readonly / const 命名族（.NET BCL 与 Mono 的通行惯例）
_CONST_PAT = [re.compile(p) for p in (
    r"^(Max|Min)[A-Z]",            # MaxTicks / MinTicks / MaxMillis / MaxValue
    r"^Ticks",                     # TicksPerMillisecond / TicksMask / TicksCeiling / TicksField
    r"^(Millis|Days|Hours|Minutes|Seconds)(Per|To)",   # MillisPerSecond / DaysTo1601
    r"^Kind[A-Z]",                 # KindUtc / KindLocal / KindShift
    r"Mask$",                      # TicksMask / FlagsMask / LocalMask
    r"^(Zero|One|Empty|Identity|Default|Null|None|True|False)$",
    r"Field$",                     # DateDataField（只对 string 生效）
    r"^Epsilon",
)]

# 已知尺寸的 BCL / Unity 基础值类型。
# 这些尺寸由 C# 语言规范和 Unity 的公开布局决定，不需要逆向，可以直接钉死。
# 用途：当算法给出更大尺寸时，说明把 static 缓存也算进去了（实测 System.Guid
# 多出 _rngAccess/_rng/_fastRng 三个 RandomNumberGenerator 缓存 → 40 字节；
# System.TimeSpan 多出 _legacyConfigChecked/_legacyMode 两个 static bool → 16 字节），
# 落在已知尺寸之外的字段一律剔除。
KNOWN_STRUCT_SIZE = {
    "System.DateTime": 8, "System.TimeSpan": 8, "System.DateTimeOffset": 16,
    "System.Guid": 16, "System.Decimal": 16,
    "UnityEngine.Vector2": 8, "UnityEngine.Vector3": 12, "UnityEngine.Vector4": 16,
    "UnityEngine.Vector2Int": 8, "UnityEngine.Vector3Int": 12,
    "UnityEngine.Quaternion": 16, "UnityEngine.Matrix4x4": 64,
    "UnityEngine.Color": 16, "UnityEngine.Color32": 4, "UnityEngine.Color24": 3,
    "UnityEngine.Bounds": 24, "UnityEngine.BoundsInt": 24,
    "UnityEngine.Rect": 16, "UnityEngine.RectInt": 16,
    "UnityEngine.Ray": 24, "UnityEngine.Plane": 16,
    "UnityEngine.LayerMask": 4, "UnityEngine.Keyframe": 20,
    "UnityEngine.GradientColorKey": 20, "UnityEngine.GradientAlphaKey": 8,
}


def skip_in_struct(idx, fn, ft, aggressive=True):
    """值类型里排除「不占实例空间」的字段。

    元数据里没有 static/literal 标志，只能靠结构性与命名惯例判据。v5 在原有两
    条基础上补上 .NET / Mono 的常量命名族——这是 DateTime 类灾难的根因：

        System.DateTime 元数据里有 45 个字段，44 个是 static readonly：
          TicksPerMillisecond / TicksPerSecond / … / MillisPerSecond / DaysPerYear /
          DaysTo1601 / MinTicks / MaxTicks / TicksMask / FlagsMask / LocalMask /
          KindUnspecified / KindUtc / KindShift / TicksField / DateDataField
        唯一真正的实例字段是最后一个 `dateData : ulong`（8 字节）。

    ★ aggressive 参数是关键：PascalCase 判据在 DateTime 上是对的，但在
      Option.Code / Value.SortKey / Value.Index 这类「实例字段也按 PascalCase
      命名」的值类型上会误伤。所以调用方要传入「该类型有没有观测」——
      有观测说明字段能被代码证实，禁用 PascalCase 这一条；没观测才激进剔除。

    判据清单（全部只在值类型上生效，class 完全不受影响）：
      1) 字段类型 == 声明类型自身 → 必然是 static readonly 单例
         （Vector3.zeroVector / Quaternion.identity / String.Empty …）
      2) 名字形如 kXxx → Unity 惯例的 public const（literal，无存储）
      3) .NET 常量命名族：MaxXxx / MinXxx / TicksXxx / XxxMask / KindXxx /
         MillisPerXxx / DaysToXxx / Zero / One / Empty / Identity / Default
      4) 全大写常量名（BASE_PROPERTY_ENHANCE_RATIO / EQUIP_SLOTS 这种）
      5) 以 Field 结尾的 string 字段 → 反射用的名字常量（DateDataField）
      6) [仅 aggressive] PascalCase：.NET 实例字段惯例是 camelCase 或 m_/_ 前缀
    ★ 3)~6) 只对基元 / string / 数组生效，避免误伤 m_xxx 之类的实例字段。
    ★ 比较前要展开 C# 别名：元数据里 String.Empty 的类型写作 "string"，
      而声明类型全名是 "System.String"，不展开就漏判。
    """
    full = types.get(idx, {}).get("full")
    if ft and full:
        f2 = ft.strip()
        if _ALIAS.get(f2, f2) == full:
            return True
    if not fn:
        return False
    ft2 = (ft or "").strip()
    is_prim = ft2 in PRIM
    is_str = _ALIAS.get(ft2, ft2) == "System.String"
    is_arr = ft2.endswith("[]")
    if len(fn) > 1 and fn[0] == "k" and fn[1].isupper() and is_prim:
        return True
    if not (is_prim or is_str or is_arr):
        return False
    if not aggressive:
        # 有观测可证实字段：只信任结构性判据，所有命名启发式全部禁用。
        # 反例（实测）：SignMask / ScaleMask 会被 Mask$ 误伤，
        # DECIMAL_NEG 会被「全大写」误伤，而它们正是观测 0x0/0x4/0x8/0xc
        # 对应的真实实例字段。
        return False
    for pat in _CONST_PAT:
        if pat.search(fn):
            return True
    # 全大写常量名（至少 4 字符，避免误伤 X / Y / ID 这类单字母实例字段）
    if len(fn) >= 4 and fn.upper() == fn and any(c.isalpha() for c in fn):
        return True
    # ★ PascalCase 判据：.NET 实例字段惯例是 camelCase（dateData）或 m_xxx / _xxx
    #   （m_Center / _ticks），而 static readonly 常量惯例是 PascalCase（MaxTicks /
    #   OADateMinAsTicks / DaysToMonth365 / DatePartYear）。
    #   只在没有观测可证实字段时启用，否则会误剔 Option.Code / Value.SortKey。
    if fn[0].isupper():
        return True
    return False


def skip_in_class(idx, fn, ft, mask=None):
    """class 里排除「不占实例空间」的 static / const 字段。

    ★ 这是 v6 的主手术刀。元数据里没有字段级 static 标志（Il2CppType.attrs 未解），
      但 .NET / Mono 的常量命名惯例极其稳定，实测量级很大：全工程 class 字段
      210,943 个，其中全大写命名的有 50,415 个（23.9%），几乎全是 static：

        System.Random            MBIG / MSEED          = private const int
        System.Text.Encoding     ISO2022JP / EUCJP …   = internal const int
        System.Text.Encoding     MIMECONTF_MAILNEWS …  = private const int
        System.GC                EPHEMERON_TOMBSTONE   = private static object
        Mono.Security.MD2Managed PI_SUBST              = private static readonly byte[]
        CharUnicodeInfo          HIGH_SURROGATE_START  = const char
        MoleMole.MonoDragonAvatar  MOVE_SPEED_LIMIT / RANDOM_PARAM

      把这些塞进实例布局会让整条偏移链后移，是 P! 的主要来源之一。

    判据（只在 class 上生效）：
      1) 字段类型 == 声明类型自身 → static readonly 单例
      2) 名字形如 kXxx            → Unity 惯例 public const
      3) 全大写（含下划线或 len>=4）且是基元 / string / 数组 → const 或 static 缓存

    ★ 已知反例：Mono.Globalization.Unicode.TailoringInfo.LCID 是真实的实例字段
      （public readonly int LCID）。所以这条判据在「有观测」的类型上要能被观测否决，
      调用方（pack）会用覆盖率把被误剔的字段找回来。
    """
    if mask is None:
        mask = CS_MASK
    full = types.get(idx, {}).get("full")
    if ft and full and (mask & 1):
        f2 = ft.strip()
        if _ALIAS.get(f2, f2) == full:
            return True
    if not fn:
        return False
    ft2 = (ft or "").strip()
    is_prim = ft2 in PRIM
    is_str = _ALIAS.get(ft2, ft2) == "System.String"
    is_arr = ft2.endswith("[]")
    # `s_` 前缀是 Mono / .NET 的静态字段惯例（s_nLists / s_timerCallback /
    # s_LinkedTokenCancelDelegate），且从不用在实例字段上，精确率远高于全大写。
    if (mask & 8) and fn.startswith("s_") and len(fn) > 2:
        return True
    if (mask & 2) and len(fn) > 1 and fn[0] == "k" and fn[1].isupper() and is_prim:
        return True
    if not (mask & 4):
        return False
    if not (is_prim or is_str or is_arr):
        return False
    if not any(c.isalpha() for c in fn):
        return False
    if fn.upper() != fn:
        return False
    # ★ 必须含下划线。Mihoyo 把大量 private 实例字段混淆成了纯大写随机串
    #   （LIEMIEBBCBO / LKLNGJIAFKG / INNMNFPIBOE / PFCFININFLF …），它们和
    #   ALL_CAPS 常量判据正面撞车。实测被剔字段里命中观测的 17,924 个中绝大多数
    #   是这类混淆名，而真正的常量几乎都能写成 ALL_CAPS_WITH_UNDERSCORE。
    return "_" in fn


def covered_set(fl):
    """字段起点 ∪ 内联结构体的合法内部偏移（递归由 pack 展平，故一层即可）。

    ★ 为什么要并上内部偏移：Ghidra 会把 `this->pos.z` 常量折叠成 `param_1 + 0x28`，
      而 pos 是 0x20 处的 Vector3。这类偏移不是字段起点，但**是真实的**，不能算错。
      实测这一项吸收掉 4,578 个伪落空（Vector3 2,216 / Color 348 / Quaternion 167 …）。
    """
    s = set()
    for owner, fi, fn, ft, off, sz in fl:
        s.add(off)
        fti = by_name.get((ft or "").strip())
        if fti is None or kind_of(fti) != "struct":
            continue
        sub, _ = pack(fti)
        for _o, _f, _n, _t, soff, _sz in sub:
            if soff < sz:
                s.add(off + soff)
    return s


def real_miss(fl, end, o):
    """真正的落空 = 落在字段之间的空隙里，或超出类型总尺寸。

    ★ 「严格落在某个字段所占字节之内、又不是合法内部偏移」的观测一律当噪声：
        · `proto.ClientMail` 每个 8 字节引用字段后面都有一个 +4 的观测
          （0x14/0x1c/0x24/0x2c …）。0x14 不是 8 字节对齐，物理上不可能是引用
          字段的起点，而该类型的 fieldCount=15 与元数据完全一致，不存在漏字段。
        · `MoleMole.BaseMonoAvatar` 的 TRIGGER_*_PARAM 是 8 字节 string 字段，
          观测落在 +1/+2/+4，同样是字节级指针运算折叠出来的。
      这类伪落空占全部落空的 78.4%，把它们算成布局错误会把准确率严重低估。
    """
    cov = covered_set(fl)
    bad = []
    for m in o:
        if m in cov:
            continue
        if m >= end:
            bad.append(m)                       # 尾部漏字段
            continue
        inside = False
        for owner, fi, fn, ft, off, sz in fl:
            if off < m < off + sz:
                inside = True
                break
        if not inside:
            bad.append(m)                       # 空隙：真的少了一个字段
    return bad


def pack(idx, depth=0, variant=None):
    """返回 [(owner, fieldIdx, name, typeName, offset, size)]，以及总尺寸

    variant 只影响 class 的「常量字段剔除策略」（位掩码，见 skip_in_class）。
    值类型只用变体 0 的规则（struct 常量判据另有一套，见 skip_in_struct）。
    """
    if variant is None:
        variant = CS_DEFAULT_VARIANT
    key = (variant, idx)
    if key in _pack_memo:
        return _pack_memo[key]
    if depth > 12:
        return [], 8
    _pack_memo[key] = ([], 8)          # 防环
    k = kind_of(idx)
    if k == "enum":
        _pack_memo[key] = ([], 4)
        return [], 4
    cur = base_start(idx)
    maxa = 1
    out = []
    cand = all_fields(idx)
    if k != "class":
        # 值类型：按常量判据剔除 static readonly。启用激进剔除要同时满足：
        #   · 没有观测（有观测说明字段能被代码证实，命名启发式一律禁用）
        #   · 字段数 >= 8 且 PascalCase 占比 >= 80%（「常量块」的形态特征）
        # 这条门槛是必须的：System.IO.MonoIOStat 只有 5 个字段（fileAttributes /
        # Length / CreationTime / LastAccessTime / LastWriteTime），其中 4 个是
        # PascalCase 的真实实例字段，无门槛时会被削成 4 字节，进而让
        # FileSystemInfo._data 从 0x28 缩到 4，把后面所有字段整体前移。
        # 而 System.DateTime 是 45 个字段里 44 个 PascalCase 常量，占比 98%，
        # 属于典型的常量块，必须剔。
        # 「剔完不能一个不剩」是硬兜底。
        n_pass = sum(1 for x in cand if x[2] and x[2][0].isupper())
        aggr = (len(obs_of(idx)) < 2 and len(cand) >= 8
                and n_pass >= 0.8 * len(cand))
        kept = [x for x in cand if not skip_in_struct(idx, x[2], x[3], aggressive=aggr)]
        if kept:
            cand = kept
    elif variant:
        # class：剔除常量 / static 命名族（v6 主手术刀）
        kept = [x for x in cand if not skip_in_class(idx, x[2], x[3], variant)]
        if kept:
            cand = kept

    # 已知尺寸的基础值类型：落在尺寸之外的字段必然是 static 缓存
    known = KNOWN_STRUCT_SIZE.get(types[idx]["full"]) if k != "class" else None
    for owner, fi, fn, ft in cand:
        s = size_of_type_name(ft)
        if s <= 0:
            continue
        a = align_of_name(ft)
        maxa = max(maxa, a)
        nxt = align(cur, a)
        if known is not None and nxt + s > known:
            continue
        cur = nxt
        out.append((owner, fi, fn, ft, cur, s))
        cur += s
    end = known if known is not None else align(cur, maxa)
    _pack_memo[key] = (out, end)
    return out, end


def packed_size(idx, depth=0):
    return pack(idx, depth)[1]


# ---------------- 主循环 ----------------
out = open(OUT_PATH, "w", encoding="utf-8", newline="")
w = csv.writer(out, delimiter="\t", lineterminator="\n")
w.writerow(["typeIdx", "typeName", "fieldIdx", "fieldName", "fieldType",
            "size", "isStatic", "offset", "conf", "nProbe"])

nP = nPb = nPq = 0
nRawPb = 0
n_field = 0
bad_samples = []
struct_size = {}
n_switch = 0
n_tried = 0
n_win = n_tie = n_lose = 0
for ti in sorted(types):
    t = types[ti]
    k = kind_of(ti)
    if k == "enum":
        continue
    o = obs_all.get(ti, set())
    if not o:
        o = obs_3.get(ti, set())
    o = clean_obs(ti, o)

    # ★ 变体择优：有观测的 class 才有资格被裁决。
    #   命名启发式（尤其「全大写 = const」）在 class 上精确率只有约 50%
    #   （BTN_CLOSE / PNL_CONTENT 这类名字既是 static 也是 [SerializeField] 实例字段），
    #   全局套用会净亏。改成「每个类型拿观测投票」：底层计算量翻倍，但保证不回归。
    pick = CS_DEFAULT_VARIANT
    if k == "class" and o and len(CS_VARIANTS) > 1:
        best = None
        for v in CS_VARIANTS:
            f2_, e2_ = pack(ti, 0, v)
            nm_ = len(real_miss(f2_, e2_, o))
            # 落空少者胜；打平取更靠后的变体（列表按「保守 → 激进」排列）
            if best is None or nm_ <= best[0]:
                best = (nm_, v, f2_, e2_)
        n_tried += 1
        if best[1] != CS_VARIANTS[0]:
            n_switch += 1
        # 严格胜出 / 打平 / 严格落败：用来判断命名启发式到底值不值得用
        base = len(real_miss(*pack(ti, 0, CS_VARIANTS[0]), o)) if False else None
        m_first = len(real_miss(*pack(ti, 0, CS_VARIANTS[0]), o))
        m_last = len(real_miss(*pack(ti, 0, CS_VARIANTS[-1]), o))
        if m_last < m_first:
            n_win += 1
        elif m_last > m_first:
            n_lose += 1
        else:
            n_tie += 1
        pick = best[1]
    fl, end = pack(ti, 0, pick)
    if k == "struct":
        struct_size[t["full"]] = end
    if not fl:
        continue
    offs = set(x[4] for x in fl)
    raw_miss = o - offs
    miss = real_miss(fl, end, o)
    if not o:
        conf = "P?"
        nPq += 1
    elif miss:
        conf = "P!"
        nPb += 1
        if len(bad_samples) < 15:
            bad_samples.append((t["full"], end, sorted(o)[:12],
                                sorted(offs)[:12], miss[:8]))
    else:
        conf = "P"
        nP += 1
    if raw_miss:
        nRawPb += 1
    for owner, fi, fn, ft, off, s in fl:
        w.writerow([ti, t["full"], fi, fn, ft, s, 0, off, conf, len(o)])
        n_field += 1
out.close()

print("v5  类型: P=%d  P!=%d  P?=%d  字段=%d" % (nP, nPb, nPq, n_field))
print("    （严格口径：只把落在空隙 / 超出末尾的观测算错；原始口径 P!=%d）" % nRawPb)
print("    变体择优: 参与裁决 %d 个 class；激进变体严格胜出 %d、打平 %d、严格落败 %d" % (
    n_tried, n_win, n_tie, n_lose))
for nm in ("System.DateTime", "System.DateTimeOffset", "System.Guid", "System.TimeSpan",
           "TransitionTime", "DateMapping", "UnityEngine.Vector3", "UnityEngine.Matrix4x4"):
    if nm in struct_size:
        print("   %-26s %5d 字节" % (nm, struct_size[nm]))
print("\n存在观测冲突的样例（前 15）：")
for full, end, o, offs, miss in bad_samples:
    print("  %-44s end=%-5d" % (full, end))
    print("     观测: %s" % ",".join("0x%x" % x for x in o))
    print("     打包: %s" % ",".join("0x%x" % x for x in offs))
    print("     未命中: %s" % ",".join("0x%x" % x for x in miss))
