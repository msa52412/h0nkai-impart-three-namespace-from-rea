## §9O 热点未命名函数命名（第 8 步）：13 个符号吃掉 4 成调用边

### 9O.1 一句话结果

给 **13 个 il2cpp codegen 桩 / 运行时函数**命名后，反编译里「调用未命名函数」的占比从 **59.6% 降到 17.4%**：

| 指标 | 命名前 | 命名后 |
|---|---|---|
| 指向**已具名**函数的调用边 | 1,768,357（40.4%） | **3,610,737（82.6%）** |
| 指向**仍是 `FUN_`** 函数的调用边 | 2,605,085（59.6%） | **762,705（17.4%）** |
| 已具名函数数 | 151,220 | 151,235（+15） |
| 未命名函数数 | 29,001 | 28,986（−15） |

即**未命名函数只占函数总数 6.5%，却承担 59.6% 的调用边**——典型的「少数热点 + 长尾」，
啃掉头部十几个就把大头吃掉了。

### 9O.2 先纠正上一轮的一个统计错误

上一轮我报过「未命名被调函数 180,221 个，占被调总数 180,221」。**这个数字是假的**：
占比 100% 在逻辑上不可能，库里明明有 151,220 个具名函数。

根因是判定口径。当时用 `bh3_method_addr.tsv` 查地址「有没有名字」，而该表只含
**元数据里有 C# 方法**的函数；il2cpp 运行时本体、桥接桩、泛型共享体本来就不在方法表里，
于是被一律判成「未命名」。

改成以 **Ghidra 里函数当前的真实名字**为准（新写 `DumpNames.java` 导出
`names_all.tsv`，443,069 行，`entry / name / size / thunk` 四列），基线才是 9O.1 表里的
40.4% / 59.6%。新写的 `cg_unnamed.py` 就是按这个口径统计的。

> 教训：**判断「有没有名字」必须问符号表本身**，不能拿另一张「应该有名字」的表去反推——
> 那张表的覆盖范围就是它的盲区。

### 9O.3 定位方法：拿 .rdata 里的字符串常量做地面真值

热点地址 `0x1804FE040–0x1804FE4A0` 这一片是 **MSVC 增量链接的 jump thunk 表**：
每个桩 5 字节 `E9 xx xx xx xx`，同一张表里还混着 `CoTaskMemAlloc`、
`K32GetProcessImageFileNameW`、`SHGetKnownFolderPath`、`inet_ntop`、`_guard_check_icall`
这些导入桩。所以语义都在**跳转目标**里，光看桩本身看不出东西。

突破口是这几个目标函数的固定形态：

```asm
180448976  MOV RCX,[0x1899db1c0]      ; corlib（Il2CppImage* 全局变量）
18044897d  LEA R8,[0x1881a1f38]       ; name
180448984  LEA RDX,[0x1881a1de8]      ; namespaze
18044898b  CALL 0x18042d650           ; Class::FromName(image, ns, name) -> Il2CppClass*
180448993  CALL 0x1804457f0           ; Object::New(klass) -> 异常对象
1804489aa  CALL 0x180447cf0           ; Raise
1804489c5  INT3
```

两个 `LEA` 指向 .rdata 的 C 字符串。**直接把字节读出来**（`Peek.java`）：

| 地址 | 内容 | 用在哪 |
|---|---|---|
| `0x1881A1DE8` | `"System"` | namespaze |
| `0x1881A1F18` | `"IndexOutOfRangeException"` | `0x180436120` |
| `0x1881A1F38` | `"NullReferenceException"` | `0x180448970` |
| `0x1881A2080` | `"ArrayTypeMismatchException"` | `0x180431FB0` |

于是「哪个函数抛哪个异常」不再靠推断，是**读出来的**。

再配合调用点上下文闭环：

```c
/* IsPatched 里，空判断 → 抛 */
if (**(longlong **)(klass + 0x28) == 0) {
    FUN_1804fe400();                     /* ← 空引用 */
}
/* IsPatched 里，越界判断失败 → 抛 */
if ((uint)id < *(uint *)(arr + 0x18)) { return ...; }
uVar4 = thunk_FUN_180436120();           /* ← 造 IndexOutOfRangeException */
FUN_1804fe3d0(uVar4, 0);                 /* ← 抛 */
```

### 9O.4 命名表（13 条）

证据等级：**S** = 字符串常量坐实；**A** = 汇编形态（`SUB RSP,0x28; CALL X; INT3` 或 5 字节 `JMP`）；
**C** = 调用点上下文。

| VA | 名字 | 调用点数 | 证据 | 依据 |
|---|---|---:|---|---|
| `0x18042D650` | `il2cpp::vm::Class::FromName` | — | S | 三参 `(corlib, "System", <类型名>)`，返回 klass |
| `0x18042D860` | `il2cpp::vm::Class::Init` | — | C | 以 klass 为参；调用点均先判 `[klass+0xE8]==0`；内部取全局锁 `0x1899DB878` 后置 1 |
| `0x1804457F0` | `il2cpp::vm::Object::New` | — | C | 先按 `[klass+0xC0]` 解析泛型/变体，再用 `[klass+0x114]` 的 instance_size 调分配器，末尾调 `Class::Init` 跑 cctor，返回新实例 |
| `0x180448320` | `il2cpp::vm::Exception::Raise` | — | A/C | 37 字节，尾随 `INT3`；入参是已构造好的异常对象 |
| `0x180436120` | `il2cpp::vm::Exception::CreateIndexOutOfRangeException` | — | S | `FromName(...,"IndexOutOfRangeException")` + `Object::New` |
| `0x180448970` | `il2cpp::vm::Exception::RaiseNullReferenceException` | — | S | `FromName(...,"NullReferenceException")` + `Raise` |
| `0x180431FB0` | `il2cpp::vm::Exception::CreateArrayTypeMismatchException` | — | S | 同形态，名字常量 `0x1881A2080` |
| `0x1804FE400` | `il2cpp::codegen::raise_null_reference_exception` | **946,440** | A/C | 10 字节 = `CALL 0x180448970` + `INT3`；调用点紧跟对象空判断 |
| `0x1804FE480` | `il2cpp::codegen::runtime_class_init` | **393,235** | A/C | 5 字节 `JMP 0x18042D860`；调用点先判 `klass+0xE8` 且丢弃返回值 |
| `0x1804FE3C0` | `il2cpp::codegen::object_new` | **194,209** | A/C | 5 字节 `JMP 0x180445760→0x1804457F0`；入参是 klass 全局，返回值被当作 `this` 传给构造函数并存进字段 |
| `0x1804FE3D0` | `il2cpp::codegen::raise_exception` | **186,425** | A/C | 10 字节 = `CALL 0x180448320` + `INT3` |
| `0x1804FE210` | `il2cpp::codegen::get_index_out_of_range_exception` | **99,310** | A/S | 5 字节 `JMP 0x180436120` |
| `0x1804FE1D0` | `il2cpp::codegen::get_array_type_mismatch_exception` | **22,453** | A/S | 5 字节 `JMP 0x180431FB0` |

`object_new` 的语义一开始我看错了。看到 `Class::FromName` 后紧跟一次调用，先写成了
`initialize_class`；直到看 `BulletinActivityConfig::_ctor` 的实际用法才纠正过来：

```c
puVar1 = il2cpp::codegen::initialize_class(_DAT_1899e69f0);  /* ← 同一个 klass 全局 */
FUN_1849b2bc0(puVar1, 0);                                   /* ← 紧接着调 ctor */
this->mission_ids = puVar1;                                 /* ← 结果存进字段 */
```

返回的是**新分配的对象实例**（还被当作 `this` 传给构造函数），不是 klass。
四个 `List<T>` 字段共用同一个 `_DAT_1899e69f0` 也说明了这一点：那只是 `List<T>`
泛型定义的 klass，具体实例化由 `Object::New` 内部按 `[klass+0xC0]` 解析。

### 9O.5 顺手把 `swi(3)` 尾巴删掉：noreturn 标记

命名之后暴露出第二个问题。Ghidra 不知道这些抛异常的函数**不返回**，于是每个调用点后面
都跟着一段不可达代码：

```c
uVar2 = il2cpp::vm::Exception::CreateIndexOutOfRangeException();
il2cpp::codegen::raise_exception(uVar2,0);
pcVar2 = (code *)swi(3);
bVar3 = (*pcVar2)();
return bVar3;
```

`swi(3)` 就是 `INT3`（MSVC 给 noreturn 调用后面填的 `int3` 对齐）。给这 4 个函数
（`Exception::Raise`、`Exception::RaiseNullReferenceException`、
`codegen::raise_null_reference_exception`、`codegen::raise_exception`）
调 `Function.setNoReturn(true)` 之后，反编译变成：

```c
uVar2 = il2cpp::codegen::get_index_out_of_range_exception();
                    /* WARNING: Subroutine does not return */
il2cpp::codegen::raise_exception(uVar2,0);
```

`IsPatched` 从 54 行降到 39 行，而且**死代码和假返回值全消失了**。

### 9O.6 前后对比

`IFix::WrappersManagerImpl::IsPatched`（146 字节）：

```c
/* 命名 + noreturn 之前 */
if (*(int *)(_DAT_189a34088 + 0xe8) == 0) { thunk_FUN_18042d860(); }
if (**(longlong **)(_DAT_189a34088 + 0x28) == 0) {
    FUN_1804fe400();
    pcVar2 = (code *)swi(3); bVar3 = (*pcVar2)(); return bVar3;
}
...
    uVar4 = thunk_FUN_180436120();
    FUN_1804fe3d0(uVar4,0);
    pcVar2 = (code *)swi(3); bVar3 = (*pcVar2)(); return bVar3;
```

```c
/* 命名 + noreturn 之后 */
if (*(int *)(_DAT_189a34088 + 0xe8) == 0) { il2cpp::codegen::runtime_class_init(); }
if (**(longlong **)(_DAT_189a34088 + 0x28) == 0) {
    /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
}
...
    uVar2 = il2cpp::codegen::get_index_out_of_range_exception();
    /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_exception(uVar2,0);
```

`proto::BulletinActivityConfig::_ctor` 现在读起来已经接近 C# 源码：

```c
this->activity_id = 0;
this->activity_type = 0;
this->begin_time = 0;
this->end_time = 0;
this->bulletin_id = 0;
puVar1 = (undefined *)il2cpp::codegen::object_new(_DAT_1899e69f0);
FUN_1849b2bc0(puVar1,0);
this->mission_ids = puVar1;
...
this->type_param_str = _DAT_189b4a238;   /* string.Empty */
this->min_player_level = 0;
this->max_player_level = 0;
```

### 9O.6b 三个坑（都实测）

**① 本地的 `UserAssembly_slim.dll` 不是 Ghidra 里那份 `UserAssembly_fixed.dll`。**
想省一次 SSH 往返、直接在本地文件上做 xref，结果读 `0x1881A1DE8` 得到的是 Boehm GC 的
`"performance\n"`，完全对不上。原因是 slim 版是被 TenProtect 处理过的落盘文件
（节表里有两个 `.reloc`、还有 `.tvm0` / `edata2` 这种壳节），`.text` 只有 5.4 MB，
而 `UserAssembly_fixed.dll` 是内存 dump，`.text` 覆盖到 0x52D7E6 之外。
**结论：任何「按 VA 读字节」的操作都必须在 Ghidra 里做**（`Peek.java`）。

**② 手工解析 PE 节表时漏读 `SizeOfOptionalHeader`。**
`IMAGE_SECTION_HEADER` 起点是 `e_lfanew + 4 + 20 + SizeOfOptionalHeader`，
PE32+ 的 `SizeOfOptionalHeader = 0xF0`。我硬编码成 `e_lfanew + 24`，节表整体错位 240 字节，
读出来 11 个节名全是乱码，`.text` 的 RVA 变成 `0x1000`（真实是 `0x1000`，碰巧对）而
`.rdata` 变成 `0x6C56000`（真实 `0x6C56000`，也碰巧对）——**错得很像对的**，最难发现。

**③ Ghidra 会自动把 thunk 改名成 `thunk_<目标新名>`。**
第一次 `ApplySymbols` 之后，`0x1804FE210` 从 `thunk_FUN_180436120` 变成
`CreateIndexOutOfRangeException`，`0x1804FE480` 变成 `Init`——因为目标函数先被改名了，
Ghidra 顺手同步了 thunk 名。而 `ApplySymbols.java` 只改 `FUN_` / `thunk_FUN_` / `SUB_`
开头的名字，改完就变成 `KEPT` 跳过。所以新写了 `ApplyRt.java`：**强制改名**（不看当前名），
并且顺便支持 `setNoReturn`。

### 9O.7 已知局限 / 下一梯队

剩下 762,705 条未命名调用边里，头部 10 个就占 39 万条：

| VA | 入度 | 形态 | 现状 |
|---|---:|---|---|
| `0x18043E4C0` | 103,744 | 134 字节，锁 `0x1899DB6B0` → 调 `0x18043E550` → 失败则带类名抛异常 → 返回 1 | 疑似 `Class::Init` 的另一条入口（用 `+0x13F`/`+0x13D` 标志），**未定名** |
| `0x1803EE250` | 66,537 | thunk → `0x18042CF20`，含 `memcpy(..., slot-0x10)` | 疑似泛型虚方法/值类型 this 适配器，**未定名** |
| `0x1804FE260` | 51,733 | thunk → `0x180436090` = `idx==-1 ? 0 : table[idx]` | 疑似元数据 usage 表查询，**未定名** |
| `0x1804FE040` | 44,931 | thunk → `0x180442320`（接口/类型匹配判断） | **未定名** |
| `0x1804FE070` | 36,024 | 用 `*(*(klass)+0x30)`（类名）拼消息后抛 | 疑似 `RaiseTypeInitializationException`，**未定名** |
| `0x1804FE0E0` | 22,559 | 5 字节 `JMP 0x180445770` | 曾疑为 `unbox`（`obj+0x10`）；dump 汇编后确认 `0x180445770` 是 `strlen` + 构造 std::string 的**字符串哈希**，**否定** |

再往下是 `0x1846F7D30`(20,456)、`0x180257840`(13,650)、`0x180261460`(13,318)、
`0x184C69C50`(11,614) 等，已离开 thunk 表，分散在各处，需要逐个看反编译。

**判据纪律**：只收「字符串常量 + 汇编形态 + 调用点上下文」三类硬证据能闭环的。
`0x1804FE0E0` 就是反例——形态上很像 `il2cpp_codegen_unbox`（返回 `obj+0x10`），
真去 dump 目标函数才发现是字符串哈希。**宁可不命名，也不贴错名**：
错名比 `FUN_` 更有害，因为它会让后续所有推理建立在错误前提上。

### 9O.8 复现

```bash
# 1) 导出 Ghidra 里全部函数的真实名字（443,069 行）
-postScript DumpNames.java ~/re/sym/names_all.tsv

# 2) 本地按入度统计「仍未命名」的（务必用 names_all，别用 bh3_method_addr）
python cg_unnamed.py names_all.tsv 40

# 3) 读字符串常量 + 查交叉引用
-postScript Peek.java ~/re/sym/peek1.txt 0x1881a1de8 0x1881a1f18 0x1881a1f38

# 4) 生成命名表并写回（强制改名 + noreturn）
python gen_rt_names2.py          # → bh3_rt_names2.tsv（va/noreturn/ns/cls/method）
-postScript ApplyRt.java ~/re/sym/bh3_rt_names2.tsv ~/re/sym/apply_rt4.txt

# 5) 验证
-postScript DumpDecomp.java ~/re/sym/rt5.c 0x1835D7F80 0x186637860
```

工具链：`DumpNames.java`（导出真实名）/ `cg_unnamed.py`（入度统计）/
`Peek.java`（读字节 + 查引用）/ `gen_rt_names2.py`（命名表）/ `ApplyRt.java`（写回 + noreturn）。

---

