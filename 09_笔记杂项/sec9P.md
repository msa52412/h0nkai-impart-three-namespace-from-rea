## §9P 源码树生成（第 9 步）：57,487 个类型 / 408,458 个方法落成 C#

### 9P.1 一句话结果

把「解密出的元数据 + 求解出的字段布局 + Ghidra 的反编译体」三份成果合成为
**468 个 `.cs` 文件（69 MB）**，覆盖 **57,487 个类型 / 408,458 个方法 / 419,568 个字段 /
56,137 个属性 / 415 个事件**，并附一个本地源码浏览器。

| 产物 | 规模 |
|---|---|
| `src/*.cs` | 468 个文件，一个命名空间一个 |
| `src/_index.json` | 57,487 条类型级索引（文件 / 起始行 / 行数 / 方法数 / token / 尺寸 / 置信度），6.2 MB |
| 生成耗时 | 全量 **6 秒** |

最大的三个文件：`MoleMole.cs` 21.1 MB（12,172 类型 / 141,514 方法）、
`_global.cs` 10.6 MB（21,994 类型）、`IFix.cs` 9.7 MB。

### 9P.2 三份数据各管一段

```
global-metadata.dat（已解密）
  ├─ bh3_types_v5.txt       namespace / 类型名 / token / 父类 / 方法区间
  ├─ bh3_fields.tsv         字段声明顺序 + 字段类型
  ├─ bh3_methods_v2.tsv     方法名 / 返回类型 / 参数名 + 参数类型 / flags
  ├─ bh3_generic_params.tsv 泛型形参真实名（T / TKey / TSource …）
  ├─ bh3_properties_v2.tsv  属性（含 getter/setter 有无）
  └─ bh3_events.tsv         事件
字段布局（bh3_layout4.tsv / bh3_structs2.tsv）
  └─ 每个字段的 +0xNN 偏移、字节数、类型总尺寸、置信度
Ghidra（已贴符号 + 46,147 个结构体 + 303,151 个签名 + 13 个运行时符号）
  └─ 每个方法的反编译体（按 RVA 索引）
```

三者互不重叠：**结构来自元数据、偏移来自布局、代码来自反编译**。缺任何一份都生成不出可读的类。

### 9P.3 类型种类只能推断

元数据里**没有** `TypeAttributes` 表（§9L.3 已确认字段记录无标志位，类型记录同样没有）。
所以种类靠父类 + 方法修饰符推断：

| 判据 | 结论 |
|---|---|
| 父类 = `System.Enum` | `enum` |
| 父类 = `System.ValueType` | `struct` |
| 父类 = `System.MulticastDelegate` | `delegate` |
| 父类 = `System.Object` **且所有方法都抽象** | `interface` |
| 其余 | `class` |

分布：`System.Object` 26,276 / `System.Enum` 8,547 / `System.ValueType` 2,668 /
`System.MulticastDelegate` 1,479 / 无父类 914。

### 9P.4 方法 flags 的位布局和 ECMA 标准不一样（实测标定）

直接按 ECMA-335 的 `MethodAttributes` 解码会全错。实测标定结果：

| 语义 | ECMA 标准 | 本二进制 |
|---|---|---|
| `Private` | 0x0001 | 0x0001 ✔ |
| `Static` | 0x0010 | 0x0010 ✔ |
| `Final` | 0x0020 | 0x0020 ✔ |
| `Virtual` | 0x0040 | 0x0040 ✔ |
| `HideBySig` | 0x0080 | 0x0080 ✔ |
| `NewSlot` | 0x0100 | 0x0100 ✔ |
| **`Abstract`** | 0x0200 | **0x0400** |
| **`SpecialName`** | 0x0400 | **0x0800** |
| **`RTSpecialName`** | 0x0800 | **0x1000** |

标定依据是三条已知答案的方法：

- `System.IDisposable.Dispose` = `0x05C6` = Public + Virtual + HideBySig + NewSlot + **0x0400**
  → 接口方法必然是 `abstract`，所以 0x0400 = Abstract
- `System.Object..ctor` = `0x1886` = Public + HideBySig + **0x0800** + **0x1000**
  → 构造函数必然是 `SpecialName | RTSpecialName`
- `MonoBehaviour.Internal_CancelInvokeAll` = `0x0081` = Private + HideBySig ✔（标准位）
- `String.Concat` = `0x0096` = Public + Static + HideBySig ✔（标准位）

即只有 0x0200 / 0x0400 / 0x0800 三位整体左移了一位，低 9 位与标准一致。

### 9P.5 泛型用真实形参名还原

`bh3_generic_params.tsv` 里有 2,772 个泛型形参（721 个类型容器 + 1,246 个方法容器），
名字是原样的（`T` 1,290 / `TKey` 124 / `TValue` 118 / `TSource` 117 …）。所以：

- 类型 `List\`1` + 形参 `T` → `List<T>`
- 字段类型 `!0` → `T`（第 0 个类型形参）
- 方法内 `!!0` → 该方法第 0 个方法形参
- `Dictionary\`2<System.Int32,System.String>` → `Dictionary<int, string>`

没有实参的泛型定义会用声明处的形参名补齐，不会退化成 `T0, T1` 占位。

### 9P.6 函数体：按 RVA 索引，共享体单独标注

反编译体由 `DumpBodies.java` 在 Ghidra 里批量导出，格式 `VA<TAB>转义后的函数体`。
生成器按方法表里的 RVA 取体。

**关键点：泛型共享**。311,382 个唯一原生地址服务 398,316 个 C# 方法
（平均 1.28 个方法/地址，最高一个地址被 **1,302** 个方法共用）。
所以同一段代码在不同类型下显示时，`this` 的具体类型只能取 Ghidra 的代表符号。
生成器为此专门标一行：

```csharp
// 0600000A @ 0x186AD0AF0
// 共享体：1302 个 C# 方法共用此地址，Ghidra 代表函数 probe_186ad0af0
IExtension ProtoBuf.IExtensible.GetExtensionObject(bool createIfMissing)
{
  SecurityParser *this_00;      // ← 代表类型是 Mono.Xml.SecurityParser
  ...
}
```

覆盖率不是线性的：前 400 个体覆盖 38,774 个方法（9.5%），前 4,400 个覆盖 42,996 个（10.5%）。
因为 `body_list.txt` 已按「共用度降序」排序，头部地址被最多方法共用。

### 9P.7 三个坑

**① `bodies.tsv` 的键是 VA，方法表的 `rva` 是 RVA。**
第一版直接 `bodies.get(rva)`，全部落空，而且**静默失败**——生成出来的树看起来完全正常，
只是方法体全是空的。后来给生成器加了命中计数才暴露：
`载入方法体 400 条` 之后应当有 `其中 38774 个方法填入了反编译体（9.5%）`。
**凡是「查表合并」，都必须把命中率打出来**，否则错在静默处。

**② `DumpBodies` 的转义收尾少算一位。**
拼接时末尾的空行也追加了一个 `\n` 字面量，收尾只 `substring(len-3)` 就留下一个孤立反斜杠：

```
return *ppuVar1;\        ← 行尾多了个 \
```

没有丢内容，但会让 C# 里出现非法字符。生成器侧统一 `rstrip("\\")` 兜住了。

**③ 单文件 21 MB，浏览器直接卡死。**
所以不能做成「一个 HTML 塞全部源码」。改成服务端按**类型行号切片**：
`_index.json` 记录每个类型的 `(文件, 起始行, 行数)`，
`/api/type?i=N` 只返回那几十行。前端一次只渲染一个类型，滚动流畅。

### 9P.8 已知局限

| 局限 | 原因 | 规模 |
|---|---|---|
| 嵌套类型不归属父类 | 元数据的 `nestedTypes` 数组未解出，只有 `nestedCount` 计数 | 10,390 个类型 |
| static 字段混进实例布局 | 字段记录无 static 位（§9L.3） | `P!` 类型 6,812 个需注意 |
| 枚举没有数值 | 常量表未解 | 8,547 个枚举 |
| 没有 attribute | 未解 | 全部类型 |
| 无 C# 名的函数体缺失 | 110,089 个 `FUN_` 函数不在方法表里 | 不进源码树 |

### 9P.9 复现

```bash
# 1) 声明骨架（不需要 Ghidra）
python gen_cs.py --out src

# 2) 反编译体（远端后台，可续跑）
-postScript DumpBodies.java ~/re/sym/body_list.txt ~/re/sym/bodies.tsv

# 3) 合并 + 生成索引
scp nas@192.168.0.104:~/re/sym/bodies.tsv .
python gen_cs.py --out src --bodies bodies.tsv

# 4) 浏览
python serve_src.py --port 8765     # → http://127.0.0.1:8765/
```

工具链：`gen_cs.py`（生成器）/ `DumpBodies.java`（批量反编译，断点续跑）/
`serve_src.py`（浏览器）/ `body_list.txt`（按共用度排序的地址表）。

---

