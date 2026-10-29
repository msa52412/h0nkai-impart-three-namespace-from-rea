# 崩坏3 global-metadata.dat 解密算法还原（路线 B 完成报告）

> 目标文件：`BH3_Data/Managed/Metadata/global-metadata.dat`（56,440,956 字节）
> 目标二进制：`BH3_Data/Native/UserAssembly.dll`（190,867,608 字节，ImageBase `0x180000000`）
> 状态：**算法 100% 还原并通过实测验证（192/192 表名精确解出）**

---

## 0. 结论速览

| 项 | 结论 |
|---|---|
| 文件头是否加密 | **否**。`+4` 处 `0x652F4D71` 就是版本标识，直接与二进制常量比对通过 |
| 加密粒度 | **字段级 / 字符串级按需解密**，不是整文件流加密 |
| 解密位置 | `FUN_18043ab50`（字符串按需解密 + 缓存），**不在** LoadMetadataFile 里 |
| 表数量 | **192**（自定义格式，不是标准 il2cpp） |
| 是否可离线解密 | **是**，纯整数运算，无外部密钥、无硬件绑定 |
| 是否依赖运行时内存 | **否**，只需磁盘文件 + 二进制里的常量 |

**已提取规模**

| 内容 | 数量 | 准确率 |
|---|---|---|
| 程序集 | 192 | 192/192 |
| 字符串（池内） | 34,949 | ~90%（ID 数组本身加密，见 §8.4） |
| 方法名 | 408,458 | 100%（长度精确，见 §8.5） |
| **方法记录全字段** | **408,458** | **100%**（declType / returnType / paramStart / paramCount / token / flags / slot，见 §9D） |
| **方法签名（返回类型 + 参数名 + 参数类型）** | **408,458** | **100%**，签名内**未解类型 = 0**（含真实泛型形参名，见 §9D / §9E） |
| **参数** | **351,719** | **100%**（区间 `0xAC0F38..0xEC760C`，差分 408,456/408,457 一致；46,908 条名字被整段抹为空串，属原样） |
| **泛型形参（名字 + 宿主）** | **2,772 / 2,772** | **100%**（1,967 个容器 = 721 类型 + 1,246 方法，见 §9E） |
| 类型（含命名空间） | **57,487** | **100%**（见 §9） |
| 类型→方法归属 | 47,374 个类型 / 408,458 个方法 | **双验证**（独立 count 字段 + 差分 57,486/57,487 一致） |
| 类型继承（parent） | **57,487 / 57,487** | **100%**（29,777 直接类 + 26,276 Object + 520 泛型基类 + 914 nil + 0 坏索引，见 §9.7–9.8） |
| 泛型基类（type 0x15） | 520 | **520/520**，368 种形态，实参递归渲染到 `Base<Foo,Bar>`（见 §9.8） |
| **字段** | **419,568** | **100%**（计数与差分双向 50,182/50,182 互证，零空名零残标，见 §9A） |
| 有字段的类型 | 50,183 / 57,487 | 100% |
| **事件** | **415** | **100%**（131 类型，差分 130/130，表尾精确闭合，见 §9B） |
| **属性** | **56,137** | **100%**（15,443 类型，差分 15,442/15,442，区间精确闭合，见 §9C） |
| **属性类型** | **56,137 / 56,137** | **100%**（55,046 由 getter 返回类型 + 1,091 由 setter 参数类型，见 §9C.6） |
| 属性 → getter/setter 方法 | 55,046 getter / 14,605 setter | 结构闭合（方法索引 = `methodStart + 槽位`，Transform 20/20 全中） |
| **CodeGenModule（模块名 + 方法指针数组）** | **188 / 188** | **100%**，条数合计恰为 408,458（见 §9F） |
| **泛型方法实例化规格（表4）** | **213,854** | **100%**，**明文在 `.rdata`（零解密）**，`+0x08` 方法索引越界 0、边界精确（见 §9I.3） |
| **程序集 → 类型区间（表5）** | **192 / 192** | **100%**，192 个区间**零空隙零重叠铺满 `0..57,486`**，`sum(count)=57,487` 精确闭合（见 §9I.4） |
| **实例字段布局（偏移 + static + 尺寸）** | **419,568** | **偏移全覆盖**（393,394 个实例字段，偏移均对应一次真实 `[this+disp]` 访问）；50,183 个类型中 **23,821（47.5%）精确命中**、1,554 松弛命中；**9/9 已知真值全对**（Vector3=12 / Vector2=8 / Vector4=16 / Quaternion=16 / Color=16 / Rect=16 / Matrix4x4=64 / Bounds=24 / String=22）。元数据侧**没有** static 标志与字段偏移，全部从代码反推（见 §9K） |
| **符号落地（C# 方法名 → 原生函数）** | **311,382 / 311,382** | **100%**。全库 443,069 个函数中 **332,980（75.15%）有 C# 真名**，按代码字节 **80.01%**；建出 **30,041** 个命名空间（见 §9J） |
| **方法 → 原生地址（RVA）** | **398,316 / 408,458** | **97.52%**，零越界；地址 **100% 16 字节对齐**；其中 82.32% 落在 `.pdata` 的**真函数起点**（424,760 个，已剔除 54.3% 的 CHAININFO 分片），**0%** 落在已登记函数体内；其余 17.68% 是**无栈帧叶子桩**（`jmp` 转发 / `ret`），x64 ABI 不要求 unwind 记录故不在 `.pdata`，已由 Ghidra 复核（见 §9F.8） |
| **二进制反分析伪装** | **2 处** | `il2cpp` 节头被清零（隐藏 108 MB 生成代码）+ `Exception` 数据目录被指向空洞（隐藏 938,197 条 `.pdata`）。已给出修复脚本与 VA→raw 校准（`0x1400`），修复后 Ghidra 可正常装载（见 §9F.10） |
| **Ghidra 函数建成率** | **424,760 / 424,760 = 100.00%** | 工程 `proj4` 建出 429,850 个函数（多出 5,090 全部有归属），CHAININFO 分片 **0 污染**；函数体合计 101.9 MB / 108.2 MB 代码区。路线 B 后半段入口已打通（见 §9G） |

---

## 1. 加载链

```
FUN_18043EC20  (metadata 初始化, 3437 字节)
 ├─ FUN_180443FC0()            读整个文件
 │   ├─ "Metadata" + "global-metadata.dat"   路径拼接
 │   ├─ FUN_1803F4CC0(path, 3, 1, 1, 0, &err)   File::Open
 │   ├─ FUN_1804F1B20(handle)   MemoryMappedFile::ReadToMemoryDirect
 │   │   ├─ FUN_1803F3790        GetFileSizeEx
 │   │   ├─ malloc(len)
 │   │   └─ FUN_1803F53C0        ReadFile  ← 纯 ReadFile，无解密
 │   └─ FUN_1803F0DD0            CloseHandle
 ├─ s_GlobalMetadata = buf + 0x118
 ├─ 校验 buf[+4] == 0x652F4D71   否则 MessageBoxA + 终止
 └─ 构造 192 张表
```

**关键点**：`ReadFile` 是原样读取，磁盘字节 == 内存 buffer 字节。解密发生在**用到某个字段/字符串时**。

---

## 2. 字符串按需解密：`FUN_18043ab50`

```c
ulonglong * FUN_18043ab50(uint packed_id)
{
    if (packed_id == 0xffffffff) return &DAT_187aebda5;   // 空串

    // 1) 查缓存 std::unordered_map<uint, X>
    FUN_18041c210(&DAT_1899db5f0, &entry, &packed_id, packed_id);
    if (命中 && entry.second == 0) { ... 直接返回缓存 ... }

    // 2) 未命中 → 解密
    len   = (packed_id >> 24) & 0xFF;          // 高 8 位 = 长度
    index = packed_id & 0xFFFFFF;              // 低 24 位 = 池内偏移

    dst = arena_alloc(len + 1);
    key = index * 0xC6B5771ED0000C60 + 0x53DB1FC7E9ECC644;   // 64 位
    src = s_GlobalMetadata + (DAT_188198E50 ^ 0x7483FF7A) + index;

    nblocks = (len + 7) >> 3;
    do {
        *(u64*)dst = *(u64*)src ^ key;         // 8 字节一组
        key += 0x64C7CE0352814CF6;             // 密钥递推
        src += 8; dst += 8;
    } while (--nblocks);

    dst[len] = 0;
    return dst;
}
```

**常量（实测值）**

| 名称 | 值 | 含义 |
|---|---|---|
| `DAT_188198E50 ^ 0x7483FF7A` | `0x024AAC18` | 字符串池相对偏移（相对 `buf+0x118`） |
| 字符串池绝对偏移 | `0x24AAD30` | |
| `K_MUL` | `0xC6B5771ED0000C60` | 即 `-0x394A88E12FFFF3A0` |
| `K_ADD` | `0x53DB1FC7E9ECC644` | |
| `K_STEP` | `0x64C7CE0352814CF6` | 每块递增量 |

**打包 ID 结构**

```
 31        24 23                    0
+------------+----------------------+
|  length(8) |      index(24)       |
+------------+----------------------+
```

---

## 3. 索引扰动函数 `prf(i)`

每条表描述符记录在解密时都要减去一个按索引变化的扰动值：

```c
iVar5 = (int)(( ((i * 0x14C3BD9234D3) >> 9) + 0x48C65E21 ) * 0x22343DDF >> 21);
```

**必须全 64 位运算，最后才截断成 int32。**

这一点是整条链上最容易踩的坑：如果按 32 位中途截断，`piVar17[5]` 解出来的字符串 ID 会全部错位，192 条一条都对不上；而按 64 位运算则 192/192 全部命中。

实测对比（用"解密后可打印 ASCII 占比"作判据）：

| PRF 语义 | 平均可打印率 | 示例 |
|---|---|---|
| **全 64 位** | **100.0%** | `mscorlib.dll` |
| 乘后截 32 | 37.9% | — |
| 加后截 32 | 37.9% | — |
| 全 32 位 | 38.9% | — |
| 无 PRF | 39.3% | — |

---

## 4. 表布局

### 4.1 全局计数

| 表 | 常量来源 | 条数 | 元素大小 |
|---|---|---|---|
| 表1 | `DAT_1881A3640 ^ 0x7CD3B5B8` | 354,184 | 8 |
| 表2 | `(DAT_188198E78 + 0xF5B00267) ÷ 0x5C` | **57,487**（原写 132,220，**勘误**） | **0x5C**（原写 0x28，**勘误**） |
| 表3 | `(DAT_188198E14 ^ 0x5F613838) >> 5` | 408,458 | 8 |
| 表4 | `DAT_1881A35EC ^ 0x7CC59670` | 213,854 | 12（描述符）/ 8（缓存槽） |

> **表2 勘误（见 §9I.2）**：`DAT_188198E78 + 0xF5B00267 = 5,288,804` 是**字节长度**，
> 不是条数。除以 `0x5C` 得 **57,487**，且 `57,487 × 0x5C = 5,288,804` 精确相等。
> 旧写法用除数 `0x28` 得到 132,220.1（非整数，本身就是危险信号）。
> 除数 `0x5C` 在汇编里是 MSVC 魔数序列 `0x642C8590B21642C9` + `sub/shr 1/add/shr 6`，
> 与 §9 类型表的步长（`imul rdi, rdx, 0x5C`）互为独立证据。

> **"条数 = 记录表"这个假设是错的（见 §9I.5）**：表1–表4 这四个计数只用来 `malloc`
> **8 字节指针槽**，是**运行时惰性缓存**的槽位数，文件里并不存在对应的"表本体"。
> 真正数据分四类来源：加密段数据表 / `.rdata` 明文静态表 / 运行时缓存 / 加载期常量。
| 表5 | `(DAT_188198E4C ^ 0x6F3F9184) / 0x28` | **192** | 0x50 |
| 表6 | `(DAT_188198E20 ^ 0x20910E12) >> 4` | **192** | 0x60 |

### 4.2 文件内段偏移（相对 `buf + 0x118`）

| 区 | 常量来源 | 偏移 | 步长 | 条数 |
|---|---|---|---|---|
| **类型表（表2）** | `DAT_188198E08 ^ 0x2B849DB3` | `0x0512A0` | 0x5C | **57,487** |
| 表5 描述符 | `DAT_188198E1C ^ 0x72267500` | `0x01C2A198` | 0x28 | 192 |
| 表7 | `DAT_188198E60 ^ 0x371B8070` | `0x0242D2E8` | 0x10 | 192 |
| 表8 | `DAT_188198E70 ^ 0x0561C6FD` | `0x01C6556C` | 0x2C | 192 |
| 表9（方法定义） | `DAT_188198E58 - 0x017A3B99` | `0x00FA8318` | 0x20 | 408,461 |
| **字段表** | `DAT_188198E84 - 0x2F59FE76` | `0x01F5D8C0` | 12 | **419,568** |
| **事件表** | `DAT_188198E24 ^ 0x3A73133E` | `0x0242AC00` | 0x18 | **415**（131 类型） |
| **属性表** | `DAT_188198E28 ^ 0x3CB812E1` | `0x01C6766C` | 0x14 | **56,137**（15,443 类型） |
| **参数表** | `DAT_188198E30 ^ 0x7EA603B1` | `0x00AC0F38` | 0xC | **351,719** |
| **泛型容器表** | `DAT_188198E00 ^ 0x7497C9EE` | `0x0055C604` | 0x10 | **1,967**（721 类型 + 1,246 方法） |
| **泛型形参表** | `DAT_188198E40 - 0x77870E75` | `0x01C1F458` | 0x10 | **2,772** |
| 程序集描述符 | `DAT_188198E04 - 0x1FE83754` | `0x024A1138` | 0x38 | — |
| 字符串池 | `DAT_188198E50 ^ 0x7483FF7A` | `0x024AAC18` | — | — |
| **表4（泛型方法实例化）** | **不在加密段内** | **`.rdata` RVA `0x7127630`** | 12 | **213,854** |

> 表4 是**静态明文表**，直接从 DLL 读即可，零解密。见 §9I.3。
> 段偏移 `332448`（= `0x512A0`）= 类型表，表2 与 §9 的类型表**是同一张表**。

> 早期从 `.text` 扫出的 10 个 `mov eax,[global]; xor imm32` 常量，
> 当时误判为"表长度"，实际是**计数和偏移**：
> `7680 = 192×0x28`、`3072 = 192×0x10`、
> `29532568 / 37933800 / 29775212 / 332448` 全是段偏移（其中 `332448 = 0x512A0` = 类型表）。

### 4.3 表5 记录结构（0x28 = 10 个 int32）

解密公式（`p = prf(i)`，全部 32 位运算）：

| 字段 | 公式 | 写入运行时偏移 |
|---|---|---|
| `rec[0]` | `((rec[0] - 0x36D7455A) - p) ^ 0x61A2155E` | +0x18 |
| `rec[1]` | `(rec[1] - p) + 0x1298B083` | +0x10 |
| `rec[2]` | `((rec[2] - 0x3B4B92FD) - p) ^ 0x5887C8C6` | +0x04 |
| `rec[3]` | `(rec[3] - p) - 0x3640F13B` | +0x00 |
| `rec[4]` | `(rec[4] - 0x7C293E16) - p` → **typeCount** | +0x1C |
| `rec[5]` | `(rec[5] - 0x3D7DC690) - p` → **表名 ID** | +0x48（指针） |
| `rec[6]` | `(rec[6] - 0x12813D35) - p` → 表6 索引（-1 = 无） | — |
| `rec[7]` | `((rec[7] ^ 0x16A0E2A5) - p) + 0x3A0AAEFE` | +0x20 |
| `rec[8]` | `(rec[8] - 0x3D2E6FE3) - p` → **typeStart** | +0x14 |
| `rec[9]` | `((rec[9] ^ 0x0CA5B561) - p) + 0x27FD9462` | +0x40 |

> **`rec[4]` / `rec[8]` 勘误（见 §9I.4）**：这两行**没有 XOR**。
> 旧写法末尾的 `^ 0x53C69178` / `^ 0x1D3B2899` 混淆了**文件侧解密**与**运行时内存掩码**两件事：
> 文件侧只有 `减常量、减 prf`；运行时把解出的值**写入描述符时再 XOR 一次**当掩码，
> 读的时候（`0x180430980`：`mov edx,[rcx]; xor edx,0x1d3b2899`）再 XOR 回来。
>
> 判据：按「带 XOR」解，192 条里 start ∈ [0,57487) 的一条都没有，
> `sum(count)` 是 2.7×10¹¹；按「不带 XOR」解，**192/192 全部合法，`sum(count) = 57,487`**，
> 且 192 个区间首尾相接、**零空隙零重叠**铺满 `0..57,486`。
>
> ⇒ **待办**：本表其余带 `^` 的行（`rec[0]` / `rec[2]` / `rec[7]` / `rec[9]`）
> 很可能也是同一类混淆，建议按下节同一判据逐行做一次「带/不带 XOR」对照再定稿。

### 4.4 每张表的五层结构

```
文件内 0x28 记录 (表5)
      ↓ 解字段
运行时 0x50 描述符 (DAT_1899dbc10)   ← 192 个，arena 分配
运行时 0x60 类型信息 (DAT_1899dbc20)  ← 192 个，arena 分配
      ↑ 由表7 (0x10) + 表8 (0x2C) 填充
```

### 4.5 指针混淆

运行时描述符里的字符串指针以「地址 + 密钥」形式存储：

```c
store: *(char**)(desc + 0x48) = ptr + 0x459DCF922742193B;
load:  ptr = *(longlong*)(desc + 0x48) - 0x459DCF922742193B;
```

同类密钥常量：`0x3F10E1615E5443F4`、`0x15EFE0164A2EC19B`、
`0x563412751289B3D9`、`0x6A690E5722724657`。

---

## 5. 解出的 192 张表（前 30）

```
  0  mscorlib.dll
  1  System.Configuration.dll
  2  Mono.Security.dll
  3  System.Xml.dll
  4  System.dll
  5  System.Core.dll
  6  UnityEngine.SharedInternalsModule.dll
  7  UnityEngine.CoreModule.dll
  8  UnityEngine.TextRenderingModule.dll
  9  UnityEngine.AudioModule.dll
 10  UnityEngine.GridModule.dll
 11  UnityEngine.IMGUIModule.dll
 12  UnityEngine.ImageConversionModule.dll
 13  UnityEngine.Physics2DModule.dll
 14  UnityEngine.PhysicsModule.dll
 15  UnityEngine.StyleSheetsModule.dll
 16  UnityEngine.UnityWebRequestModule.dll
 17  UnityEngine.WebModule.dll
 18  UnityEngine.AIModule.dll
 19  UnityEngine.AnimationModule.dll
 20  UnityEngine.DirectorModule.dll
 21  UnityEngine.InputModule.dll
 22  UnityEngine.JSONSerializeModule.dll
 23  UnityEngine.MihoyoExtensionModule.dll      ← 米哈游自定义
 24  UnityEngine.ParticleSystemModule.dll
 25  UnityEngine.ParticlesLegacyModule.dll
 26  UnityEngine.ScreenCaptureModule.dll
 27  UnityEngine.TerrainModule.dll
 28  UnityEngine.TilemapModule.dll
 29  UnityEngine.UIElementsModule.dll
```

完整 192 条见 `bh3_metadata_tables.json`。

---

## 6. 辅助函数身份（已确认）

| 地址 | 身份 |
|---|---|
| `FUN_18041C210` | `std::unordered_map<int,X>::find`（bucket 步长 0x20、64 位 bitmap） |
| `FUN_1804F09A0` | bump allocator：`(count*elemsize+7)&~7`，不足则扩容，然后 `memset 0` |
| `FUN_1804F1B20` | `MemoryMappedFile::ReadToMemoryDirect` |
| `FUN_1803F53C0` | `ReadFile` 包装（56 字节） |
| `FUN_1803F3790` | `GetFileSizeEx` 包装 |
| `FUN_1803F0DD0` | `CloseHandle` 包装 |
| `FUN_1803F4CC0` | `File::Open` jumptable 分发器 |
| `FUN_1804ED510` | 7 字节 setter，写 `DAT_1899DE1C8` |
| `FUN_1804491A0` | `std::vector<T>::push_back` |
| `FUN_180440660` | 构建程序集 map |

---

## 7. 复现方式

```bash
# 1) 反编译（rea 主机 / Ghidra 12.1.4）
GHIDRA_HEADLESS_MAXMEM=4G analyzeHeadless proj bh3 \
  -import UserAssembly_slim.dll \
  -scriptPath scripts \
  -postScript DumpDecomp.java out.c <addr...> \
  -deleteProject -analysisTimeoutPerFile 2400 -max-cpu 3

# 2) 解表布局
python resolve_layout.py

# 3) 验证 PRF 语义
python verify_prf.py

# 4) 验证字符串解密
python verify_decrypt.py

# 5) 完整解密
python bh3_meta_decrypt.py
```

**产物**
- `dec_targets.c` — 10 个核心函数伪代码
- `dec_core.c` — 15 个解密链函数伪代码
- `bh3_metadata_tables.json` — 192 张表结构
- `bh3_metadata_strings.txt` — 192 条表名

---

## 8. 字符串批量提取（新增）

### 8.1 表8 的字符串字段

`dec_targets.c:478-481` 暴露了两个字符串字段：

```c
uVar23 = (i * 0x447FCE41 ^ 0x120DD35F) * 0x3E8906DA;      // 表8 PRF
lVar8  = FUN_18043ab50(puVar16[1] + 0x84B0104A ^ uVar23);   // [1] → 程序集短名
uVar19 = FUN_18043ab50(puVar16[5] + 0xF54D97A6 ^ uVar23);   // [5] → ?
```

实测：字段 `[1]` 解出 **192/192**，内容是程序集短名（`mscorlib`、`System.Configuration`…），
与表5 的 `.dll` 全名一一对应。字段 `[5]` 全部失败（0/192），语义待定。

另外 `puVar16[9]`/`puVar16[10]` 是**明文直拷**：
```c
*(undefined8 *)(piVar15 + 0x13) = *(undefined8 *)(puVar16 + 9);
```
这解释了表8 的 `+0x24`/`+0x28` 为什么只有 8 个唯一值 —— 它们是明文枚举值，不是加密数据。

### 8.2 全文件 ID 扫描

既然解密函数已知，可以反推：**凡是能解出可打印字符串的 int32 就是打包 ID**。
不假设任何步长，对 56 MB 文件逐 4 字节扫描：

| 阶段 | 数量 |
|---|---|
| 扫描的 int32 | 14,110,000 |
| 初步命中 | 67,253 |
| 字符集清洗后 | 28,375 |
| 长度修正后还原 | **37,724**（其中 5,810 条用频次众数修掉了尾部垃圾） |
| 最终过滤有效 | **34,949** |
| 其中米哈游三段式完整签名 | **18,046** |

产物：`bh3_strings_final.txt`（index + 完整字符串）

**长度修正策略**：对每个 index 同时取「最长全合法长度」和「频次众数长度」，
若众数版是最长版的前缀且差距 ≤ 2 字节，判定最长版尾部粘了垃圾，取众数版。
实测修正了 5,810 条（如 `mscorlib.dll9V` → `mscorlib.dll`、`EqualsS` → `Equals`）。

### 8.3 字符串格式

```
程序集-命名空间-类-完整签名
```

实例：
```
MoleMole-PlatformShooter-PlatformShooterNavigationUIData-MoleMole.PlatformShooter.IPlatformShooterNavigationUI.get_Daily
MoleMole-TiledGame-TiledGameFarm-TiledGameFarmMatrixUseToolSeedBtnCmpt-OnTiledGameFarmToolHoldingPreInputExec
UnityEngine-Experimental-Rendering-LightweightPipeline-LightweightPipelineAsset-set_EnablePassOutlineAvatarSecondPass
System.Collections.Generic.IEnumerable<System.Linq.Expressions.Interpreter.InterpretedFrameInfo>.GetEnumerator
```

类名分布（Top 10）：
`TiledGame` 588 / `Config` 360 / `MahouCard` 229 / `LevelDesignManager` 214 /
`ChapterARK` 210 / `PlatformShooter` 185 / `MatchThree` 183 / `Experimental` 161 /
`WaveRush` 139 / `MonsterCard` 124

### 8.4 已知精度限制

1. **ID 数组本身是加密的**。扫描结果里**没有任何连续 ID 数组段**
   （相邻命中间隔全 > 8 字节），说明存 ID 的表同样经过 PRF 反扰动。
   扫描只能捞到未加密位置的 ID。
2. **长度字段不精确**。真实 length 在打包 ID 的高 8 位，而 ID 加密后只能靠
   "最长全可打印前缀 + 频次众数"逼近。后果：
   - 部分短字符串仍会被截短（`GetTex` 实为 `GetText`）
   - 部分长字符串末尾仍残留 1~2 个垃圾字符（`<Module>B`、`valueJ`）
   - 实测准确率约 90%，长签名（米哈游三段式）准确率更高
3. 表9（`0x00FA8318`，步长 `0x5C`）才是类型记录区，
   字段级结构尚未展开 —— 那是彻底解决长度问题的正路。

### 8.5 建议的下一步

从 `FUN_18043EC20:499-514` 这条链往下：

```c
lVar6 = (DAT_188198e08 ^ 0x2B849DB3) + s_GlobalMetadata;   // 0x00FA8318 类型表
uVar19 = *(u64*)(desc + 8) ^ 0x56EAD61B43CC4F04;           // 程序集描述符 +0x08 → 指针
local_258 = *(uint*)(uVar19 + 0x1c) ^ 0x53C69178;          // 类型数量
uVar21 = (*(uint*)(uVar19 + 0x14) ^ 0x1D3B2899) + j;       // 全局类型索引
lVar24 = uVar21 * 0x5C + lVar6;                            // 类型记录
```

先反编译 `FUN_180440660` 依赖的 `DAT_188198E04 - 0x1FE83754`（每条 8 字节的
`{base, count}` 数组）和 `DAT_188198E6C - 0x3670DF73`（int32 索引数组），
就能拿到类型/方法索引表的入口，之后按 ID 精确解密，不必再暴力扫。

### 8.5 方法名表（完整解出 408,461 条）

从 `FUN_18044b7f0`（`dec_str.c:1149-1156`）拿到完整算法：

```c
uVar10 = 方法全局索引;
uVar7  = ((((uVar10 * 0xB069) ^ 0x3E382F2D) * 0x24147491 ^ 0xF997B4A800) >> 10)
          * 0x3857AACA >> 0xE;                       // 全 64 位，mod 2^64
lVar3  = (DAT_188198e58 - 0x17A3B99) + s_GlobalMetadata;   // = 0xFA8318
lVar5  = uVar10 * 0x20;                                    // 步长 0x20

method_name_id = *(uint*)(lVar5 + 0x0C + lVar3) ^ uVar7 ^ 0x1D64B276;
flag           = (*(u8*)(lVar5 + 0x1C + lVar3) - 0x10 ^ uVar7) & 0x10;
```

| 项 | 值 |
|---|---|
| 表偏移 | `0xFA8318`（绝对 `0xFA8430`） |
| 步长 | `0x20` |
| 条数 | **408,461**（自动判定表尾在 i=409,336，连续 300 条失败） |
| 唯一方法名 | **149,507** |
| 解密成功率 | **100%**（长度完全精确，无垃圾字符） |

**自洽性验证**：这个条数与 §4.1 里表3 的 `(DAT_188198E14 ^ 0x5F613838) >> 5 = 408,458` 只差 3 —— **表3 就是方法名表**。

**方法名统计**

| 项 | 数量 |
|---|---|
| 混淆名（纯大写 9~12 位，如 `DBNIDKMKDAB`） | 34,591 |
| 含泛型 `<>` | 8,787 |
| `get_` / `set_` 前缀 | 22,901 |

高频方法名：
```
.ctor                       46,694     SetupView          5,146
Read                         9,522     CacheUIReference   4,341
Write                        9,404     BindViewCallbacks  3,421
.cctor                       5,665     MoveNext           2,995
```

业务关键字命中：`Avatar` 2,926 / `UI` 2,793 / `Quest` 2,248 / `Skill` 1,321 /
`Activity` 1,162 / `Mission` 1,122 / `Monster` 935 / `World` 868 / `Battle` 699。

最长的方法名（泛型嵌套）：
```
System.Collections.Generic.IEnumerable<System.Collections.Generic.KeyValuePair<System.Type,System.Object[]>>.GetEnumerator
System.Collections.Generic.IEnumerator<System.Collections.Generic.KeyValuePair<System.String,System.Object>>.get_Current
```

产物：`bh3_methods.txt`（`索引\tID\tflag\t方法名`）

### 8.6 对比：为什么方法表比暴力扫描可靠

| | 暴力扫描 | 方法表 |
|---|---|---|
| 条数 | 34,949（含误报） | 408,461（全部有效） |
| 长度精度 | ~90%，末尾常粘垃圾 | 100% 精确 |
| 依据 | 猜测"能解出可打印就是 ID" | 反编译得到的确定公式 |

**结论**：暴力扫描只能当探索手段，真正的结构化提取必须走反编译。

---

## 9. 类型表（完整解出）

### 9.1 定位与规模

| 项 | 值 |
|---|---|
| 段偏移（相对 `buf + 0x118`） | `0x0512A0` |
| 绝对文件位置 | `0x0513B8` |
| 记录步长 | `0x5C` = **92 字节 = 23 个 int32** |
| 记录条数 | **57,487** |

`0x5C` 正好等于标准 `Il2CppTypeDefinition` 的尺寸，但**字段顺序被重排**且每字段独立加密。

**条数判定依据**：`FUN_18043E870` 里校验失败直接 `return`（不是 `continue`），所以表必须从索引 0 连续通过；实测 `0..57486` 全部通过，`57487` 起全为垃圾。

```c
/* FUN_18043e870 */
if (param_1[7] != 0x53c69178) {
  do {
    uVar1 = (param_1[5] ^ 0x1d3b2899U) + uVar4;      // 索引 = base + i
    local_28  = (((uVar1 * 0x1f17946ef935 + 0xafd81baecafdac6) >> 0x15) + 0x54760499) * 0x1125f1b6;
    uStack_20 = uVar1 * 0x5c + (DAT_188198e08 ^ 0x2b849db3) + DAT_1899dbaf8;
    if (*(int *)(uStack_20 + 4) - (int)local_28 != 0xfbe4139) return;   // ← 失败即整体退出
    FUN_18042b910(param_1, &local_18);
    uVar4++;
  } while (uVar4 < (param_1[7] ^ 0x53c69178U));
}
```

### 9.2 每条记录的 salt

```c
salt(i) = (uint32)( (((uint64)i * 0x1F17946EF935 + 0xAFD81BAECAFDAC6) >> 21)
                    + 0x54760499 ) * 0x1125F1B6
```

**必须全 64 位运算，最后才截 int32** —— 和方法表 `prf(i)` 同一个坑。

有效性校验（`FUN_18042BD50`）：

```c
if (((*(uint32*)(rec + 4) - salt) & 0xFFFFFFFF) != 0xFBE4139) return;   // 不是 0xFBE4139 即无效
```

### 9.3 字段反混淆：两种变换并存

米哈游对同一张表的不同字段用了**不同的混淆式**，必须分别处理：

| 型 | 形式 | 典型字段 |
|---|---|---|
| **SUB 型** | `value = (raw - C - salt) mod 2^32` | namespace、methodStart |
| **XOR 型** | `value = ((raw ^ C) - salt) mod 2^32` | name、nestedTypesStart |

**判定方法**：对位置 `p`，若 `value ∈ {-1} ∪ [0,T]` 对所有记录成立，则 `C` 唯一。
- SUB 型：`C = (raw₀ - salt₀ - v₀)`，枚举 `v₀ ∈ {-1} ∪ [0,T]`
- XOR 型：`C = raw₀ ^ ((salt₀ + v₀) mod 2^32)`

再用 21 条探针记录验证。实现见 `solve_consts3.py`。

### 9.4 字段映射（终版，来自 `FUN_180430980` + 求解器交叉验证）

`FUN_180430980`（"按索引构建运行时 TypeInfo"）成批读取类型记录，把全部常量一次暴露：

| 记录偏移 | 语义 | 变换 | 常量 | 空值 |
|---|---|---|---|---|
| `+0x00` | **parentIndex**（Il2CTYPE 表） | SUB | `0x15F045CB` | `-1` |
| `+0x04` | elementIndex | SUB | `0xFBE413A` | `0xFBE4139`（即校验值本身） |
| `+0x14` | **methodStart** | SUB | `0x2822B502` | `-1` |
| `+0x18` | 小索引表起点（范围 [0,414]，仅 131 类非空，语义待定） | XOR | `0x689A417F` | `-1` |
| `+0x1C` | **fieldStart** | SUB | `0xAA6F650E` | `-1` |
| `+0x20` | nestedTypesStart | XOR | `0x21FE571D` | `-1` |
| `+0x28` | byvalTypeIndex（Il2CTYPE 表） | SUB | `0x67AD6F69` | — |
| `+0x2C` | byrefTypeIndex | XOR | `0x1F5A4501` | — |
| `+0x30` | namespace | SUB | `0x4B6ACCC7` | — |
| `+0x34` | name | XOR | `0x3399EFB` | — |
| `+0x38` | interfacesStart | XOR | `0x58833D25` | `-1` |
| `+0x40` | declaringTypeIndex | XOR | `0x5AEB04` | 条件启用 |
| `+0x58` | **token** | XOR | `0x78647F39` | — |

8 个 u16 count（`+0x44..0x52`，全部减 `salt` 低 16 位符号扩展）：

| 偏移 | 变换 | 常量 | sum | 语义 |
|---|---|---|---|---|
| `+0x44` | XOR | `0x910A` | 22,464 | interfaces_count |
| `+0x46` | XOR | `0x7883` | 21,429 | nested_type_count |
| `+0x48` | SUB | `-0x1950` | **408,458** | **method_count**（=表3 描述符值，精确一致） |
| `+0x4A` | SUB | `-0x17A3` | 56,137 | property_count |
| `+0x4C` | XOR | `0x5BE4` | 58,954 | event_count |
| `+0x4E` | SUB | `-2` | **419,568** | **field_count**（与字段表精确闭合 50,182/50,182） |
| `+0x50` | SUB | `0x27E6` | 782,396 | vtable_count |
| `+0x54` | flags/bitfield | SUB（位测试） | `0xE65638B4` 补 | — |

**token 验证**：全部 57,487 条高字节 `0x02`（TypeDef），mscorlib 前几条 = `0x02000001..` 严格递增；uniq=29,417 < NT 是因为 192 个程序集各自独立 rid 空间。

### 9.5 methodCount：独立字段 + 差分双验证

- methodStart（C=`0x2822B502`，-1 哨兵）非空 47,374 条**严格递增**，差分总和 = **408,461**（与方法表总数精确闭合，修正 C 后差 1 问题消失）
- 独立字段 `+0x48` 的 method_count 与差分法 **57,486/57,487 一致**
- `FUN_180437120` 行 255 直接确认 `methodStart + 0x2822B502` 写法

### 9.6 验证证据

| 验证 | 结果 |
|---|---|
| name 解出率 | **57,487 / 57,487 = 100%** |
| `<Module>` 数量 | **192**，正好等于程序集数 |
| 非空 methodStart 单调性 | 47,374 条**零递减** |
| `sum(methodCount)` | 408,460 vs 408,461（差 1） |
| 方法名缺失 | 仅 **3** 条 |

**语义抽查**：

| 类型 | start | count | 方法（前 6） |
|---|---|---|---|
| `System.String` | 2853 | 190 | `.ctor` ×6（构造函数重载）|
| `UnityEngine.GameObject` | 21192 | 70 | `.ctor`, `CreatePrimitive`, `GetComponent`, `GetComponentFastPath`, `GetComponent` |
| `MoleMole.BaseActor` | 187365 | 10 | `Init`, `IsGameObjectActive`, `IsGameObjectExists`, `OnEvent`, `ListenEvent`, `Core` |

`GameObject` 的 70 个方法全部是真实 Unity API，`BaseActor` 是崩坏3 业务类且方法名符合游戏逻辑 —— 这是最硬的自洽证据。

### 9.7 parentIndex：已完全闭合（含泛型基类）

**最终答案**：Il2CTYPE 表**不在 metadata 文件里，而在 UserAssembly.dll 的 .rdata 静态区**。

```
PTR_PTR_1881a3628 (.data 初值) = 0x186D41F80
  ├─ 指针数组 354,184 条 (PE 重定位加载)
  └─ 每条指向 12 字节 Il2CTYPE: {u64 data; u16 unused@+8; u8 type@+10; u8 bits@+11}
     type: 0x11 VALUETYPE / 0x12 CLASS / 0x1C OBJECT / 0x15 GENERICINST / 0x13 VAR ...
```

定位方法：17 个引用函数全是 `mov reg,[rip]` **读**，无写入 → 该全局是静态初值 → 直接读 .data 初值即得。

> **注：`0x11`/`0x12` 语义已实测纠正**。取 byval 条目实测：`Nullable\`1 → 0x11`、`List\`1 / Dictionary\`2 / Enum / ValueType → 0x12`、`Object → 0x1C`、`Int32 → 0x08(I4)`、`IntPtr → 0x18(I)`。即 **0x11 = VALUETYPE，0x12 = CLASS**（此前文档写反）。

**验证**：
- byval 自检：`data == 自身 typedef 索引` **57,487/57,487 全过**
- parent 锚点：String→Object、Exception→Object、Int32/Enum→ValueType、GameObject→UnityEngine.Object、Object→nil **全部 OK**
- parent 解析（终版）：**29,777 直接类 + 26,276 System.Object + 520 泛型基类 + 914 nil + 0 坏索引 = 57,487**

### 9.8 泛型基类（Il2CTYPE `0x15`）解析

`FUN_180430150` 的 `case 0x15` 直接给出入口：

```c
case 0x15:
  uVar2 = FUN_180432a60(*(undefined8 *)param_1);   // data 字段 = Il2CppGenericClass*
```

`FUN_180432a60` 第一行即 `lVar2 = FUN_18043b320(*param_1)` —— **泛型类结构首字段就是泛型定义的 typeDefinitionIndex**。实测布局：

```
Il2CppGenericClass (0x20 字节)
  +0x00  u32   typeDefinitionIndex   <-- 泛型定义（如 List`1），FUN_18043b320 消费
  +0x04  u32   pad
  +0x08  ptr   class_inst: Il2CppGenericInst
  +0x10  ptr   method_inst
  +0x18  ptr   cached_class（运行时缓存，静态文件里为 0）
         ↑ FUN_180432a60 中 param_1+6 即 +0x18，用作 "已构建则直接返回" 的缓存判定

Il2CppGenericInst (0x10 字节)
  +0x00  u32   type_argc
  +0x04  u32   pad
  +0x08  ptr   type_argv: Il2CppType**   <-- 每项指向 12 字节 Il2CTYPE
```

递归渲染规则（实测 type 分布：`0x15` 53,526 / `0x12` 3,283 / `0x11` 589 / `0x1d` 70）：

| type | 语义 | 渲染 |
|---|---|---|
| `0x11` / `0x12` | VALUETYPE / CLASS | `data` 即 typedef 索引 → 类型全名 |
| `0x1C` | OBJECT | `System.Object` |
| `0x15` | GENERICINST | 递归：`定义名<实参…>` |
| `0x1D` | SZARRAY | `元素[]` |
| `0x14` | ARRAY | `元素[,,]`（rank 来自 `Il2CppArrayType.rank`） |
| `0x0F` / `0x10` | PTR / BYREF | `元素*` / `元素&` |
| `0x13` / `0x1E` | VAR / MVAR | `data` = 全局 genericParameterIndex → 按声明序还原 `T0/T1` |
| `0x01..0x0E` | 基元 | void/bool/char/sbyte/byte/short/ushort/int/uint/long/ulong/float/double/string |
| `0x18` / `0x19` | I / U | `System.IntPtr` / `System.UIntPtr` |

**结果：520 / 520 全部解出，368 种泛型基类形态，零残留标记。**

典型样本（均与 .NET / FullInspector 源码一致）：

```
System.IO.FileSystemEnumerableIterator`1  -> System.IO.Iterator`1<T0>
System.Threading.Tasks.FromAsyncTrimPromise`1 -> System.Threading.Tasks.Task`1<T0>
System.Collections.Generic.NullableComparer`1 -> Comparer`1<System.Nullable`1<T0>>
System.Diagnostics.Tracing.NameInfo -> ConcurrentSetItem`2<
        KeyValuePair`2<string,System.Diagnostics.Tracing.EventTags>, NameInfo>
System.Diagnostics.Tracing.TraceLoggingTypeInfo`1<bool>   (10 个基元特化)
MoleMole.TiledGame.BaseTiledState`1<MoleMole.TiledGame.Actor>   (20 个子类)
```

**`!n` 归一化说明**：VAR 的 `data` 是**全局** genericParameterIndex（如 `!1245`），不是类型内序号。GenericParam 表按声明序分配，故升序即 `T0,T1,...`。38 条「基类只引用子类部分形参」的情形（如 `` EnumerableTypeInfo`2 `` → `TraceLoggingTypeInfo`1<T0>`、`` WhereSelectEnumerableIterator`2 `` → `Iterator`1<T0>`）逐条对照源码全部吻合。

另有一批 FullInspector 演示类型（`Box`/`Button`/`Color`/`ColorIf`，全局命名空间、`declaringType == 自身`）名字无 `` `n `` 后缀却引用两个形参 —— 这是原程序集 metadata 的既有形态，基类记录为**开放泛型实例**，按 `T0,T1` 渲染语义正确。

**继承树样本**（12 层，含 UnityEngine 段）：
```
MoleMole.MonoBronya_C7 → MonoBronyaEvade_BattleY → MonoBronya_BattleY
  → MonoBattleYAvatarV2 → BaseMonoAvatar → BaseMonoAnimatorEntity
  → BaseMonoAbilityEntity → BaseMonoEntity → UnityEngine.MonoBehaviour
  → UnityEngine.Behaviour → UnityEngine.Component → UnityEngine.Object
```
父类频次：System.Object 26,276 / System.Enum 8,547 / ValueType 2,668 / MoleMole.MonoBaseUIComponent 1,826 / UnityEngine.MonoBehaviour 1,704 / MulticastDelegate 1,479 —— 与真实 .NET + Unity 生态完全吻合。

### 9.9 产物（v4）

| 文件 | 大小 | 内容 |
|---|---|---|
| `bh3_types_v4.txt` | 4.3 MB | 57,487 行 9 列：索引/命名空间/类型名/token/methodStart/methodCount/nestedCount/parentIdx/**父类名（含泛型实参）**，parent 列 **0 残留** |
| `bh3_inheritance_v4.txt` | 700 KB | 按父类名聚合的子类清单（含泛型基类分组） |
| `bh3_generic_parents.txt` | 100 KB | 520 条泛型基类明细：按基类聚合 + 按子类索引双视图 |
| `bh3_types_full.txt` | 4.3 MB | v3（泛型基类显示为 `<type 0x15 idx N>`），保留作对照 |
| `bh3_types_methods.txt` | 9.9 MB | 类型全名 + 全部方法名（独立 count 展开法） |
| `bh3_types.json` | 8 MB | 结构化 |

---

## 9A. 字段表（新增，完整解出）

### 9A.1 定位

`FUN_18044b7f0`（`il2cpp_class_get_*` 的成员数组构建器）里出现一张未被映射的表：

```c
lVar7 = (DAT_188198e84 + -0x2f59fe76) + DAT_1899dbaf8;      // 表基址
piVar1 = (int *)(lVar7 + uVar6 * 0xc);                       // 12 字节记录
iVar8 = (int)(uVar6 * 0x7740eeff55f40540 + 0x49ed7f5afcc4af8 >> 0x11);   // prf(i)
typeIdx = (*(int *)(lVar7 + 4 + uVar6 * 0xc) - iVar8) + -0xf2a3d7f;
nameId  = (piVar1[2] ^ 0x5daab140) - iVar8;
```

```
F0 = buf + (u32(DAT_188198E84) - 0x2F59FE76) = buf + 0x1F5D9D8
记录 = 12 字节 {u32 rawA; u32 typeIdx; u32 nameId}，全部以 prf(全局字段索引) 混淆
prf(i) = ((i * 0x7740EEFF55F40540 + 0x49ED7F5AFCC4AF8) >> 0x11) & 0xFFFFFFFF
  nameId  = (rec[2] ^ 0x5DAAB140) - prf
  typeIdx = (rec[1] - prf) - 0xF2A3D7F   -> Il2CTYPE 表索引
```

### 9A.2 计数：`+0x4E` 就是 field_count

| 方法 | 结果 |
|---|---|
| `+0x4E`（SUB `-2`）求和 | **419,568** |
| fieldStart 差分（max start + 末类型 count） | **419,568** |
| 逐类型比对 | **50,182 / 50,182 一致（100%）** |
| 运行时侧交叉 | `klass+0x128` 被当作成员数循环使用（`FUN_18044b230`），与 metadata `+0x4E` 语义一致 |

> 早前一度判定「`+0x4E` 不是 field_count」，是比对脚本自身写错（用 `order[:-1]` 且加了错误的 `n>0` 过滤）。修正后 100% 命中。

### 9A.3 结果

| 项 | 数值 |
|---|---|
| 字段总数 | **419,568** |
| 有字段的类型 | 50,183 / 57,487 |
| 空字段名 / 未解析类型标记 | **0 / 0** |
| 泛型字段 | 24,610（5.9%） |
| 数组字段 | 9,254（2.2%） |

**语义锚点校验**（与 Mono 源码逐字吻合）：

```
System.String    8 字段: m_stringLength, m_firstChar, TrimHead, TrimTail,
                          TrimBoth, Empty, charPtrAlignConst, alignConst
System.Int32     3 字段: m_value, MaxValue, MinValue
System.Exception 17 字段: s_EDILock, _className, _message, _data, _innerException,
                          _helpURL, _stackTrace, _stackTraceString, ...
System.Object    0 字段
```

### 9A.4 一个解码坑

`dec()` 里曾有 `L > 0x80 → 失败` 的经验性上限（长度字节是完整 8 位，最大 255）。IFix 注入的 8 个超长字段名（132~138 字节）因此被误判为空名。放宽为 `L == 0` 后归零，且类型名最长仅 79 字符，说明该上限从未影响类型表。

### 9A.5 产物

| 文件 | 大小 | 内容 |
|---|---|---|
| `bh3_fields.txt` | 10 MB | 按类型分组，`## [idx] 类型 (N 字段)` + `字段类型 字段名` |
| `bh3_fields.tsv` | 12 MB | 扁平 5 列：typeIdx / typeName / fieldIdx / fieldName / fieldType |
| `bh3_classes.txt` | **68 MB** | **类定义视图**：`类型 : 父类 [方法/字段/属性/事件]` + 缩进字段 + 完整方法签名（一文件读完整个 metadata） |
| `bh3_types_v5.txt` | 4.3 MB | v4 基础上追加 `fieldCount` 列（合计 419,568） |
| `bh3_events.tsv` | 38 KB | 415 条事件（§9B.5） |
| `bh3_properties.tsv` | 5.8 MB | 56,137 条属性（§9C.5） |
| `bh3_properties_v2.tsv` | 6.2 MB | 同上 + **propType**（§9C.6） |

---

## 9B. 事件表（新增，完整解出）

### 9B.1 定位

| 项 | 值 |
|---|---|
| 基址 | `buf + (u32(DAT_188198E24) ^ 0x3A73133E)` = `buf + 0x242AC00` |
| 记录 | `0x18` = 6 个 int32 |
| 条数 | **415**（131 个类型） |
| 区间 | `0x242AC00 .. 0x242D2E8 = 0x26E8 = 415 × 0x18` |

每类型：

```
eventStart = (typedef[+0x18] ^ 0x689A417F) - salt        # 无效值为 0xFFFFFFFF
eventCount = (u16(typedef[+0x52]) 符号扩展 + 0x1197 - salt16) & 0xFFFF
```

### 9B.2 记录结构与解码

```c
prf18(i) = ( ( (((i*0x7A00) ^ 0x3B79566A) * 0x3EA7ABC3 ^ 0x52121A98000) >> 0xC ) * 0x20CF3F69 ) & M32

[0] add    = ((rec[0] + 0xC617C479) & M32) ^ prf18(i)      哨兵 0xFFFFFFFF
[1] remove =  (rec[1] ^ prf18(i)) ^ 0x5AF3CD0              哨兵 0xFA50C32F
[2] raise  =  (rec[2] ^ prf18(i)) ^ 0x5E4DD4F1             哨兵 0xA1B22B0E
[3] type   = ((rec[3] + 0xFCC28A65) & M32) ^ prf18(i)
[4] name   = dec( prf18(i) ^ ((rec[4] + 0xBFC65639) & M32) )
[5] token  = ((rec[5] + 0xCE2556FD) & M32) ^ prf18(i) ^ 0x3081751A
```

### 9B.3 结果与三重闭合

* 415 条事件，**名字连续 415 条全部有效**（零失败）
* 差分 vs `+0x52`：**130 / 130 一致**
* 表尾 `0x242D2E8` 精确等于表7 起点（`DAT_188198E60 ^ 0x371B8070`）

语义锚点（全部逐字命中）：

| 类型 | 事件 |
|---|---|
| `System.AppDomain` | `AssemblyLoad` / `DomainUnload` / `ProcessExit` / `UnhandledException` |
| `UnityEngine.SceneManagement.SceneManager` | `sceneLoaded` / `activeSceneChanged` |
| `UnityEngine.Application` | `logMessageReceived` |
| `System.AppDomain` | `KeyGenerated`（取首条，验证解码起点） |

### 9B.4 事件 vs 属性的判定特征

事件有 **3 个可选成员**（add/remove/raise），属性有 **2 个**（get/set）。`raise` 哨兵 `0xA1B22B0E` 在 C# 事件里几乎恒等于哨兵（编译器不生成 raise 访问器），这是区分两张 0x18/0x14 表的决定性特征。

### 9B.5 产物

`bh3_events.tsv`（415 行：typeIdx / typeName / eventIdx / name / token / add / remove / raise / type）

---

## 9C. 属性表（新增，完整解出）

### 9C.1 定位

| 项 | 值 |
|---|---|
| 基址 | `buf + (u32(DAT_188198E28) ^ 0x3CB812E1)` = `buf + 0x1C6766C` |
| 记录 | `0x14` = 5 个 int32 |
| 条数 | **56,137**（15,443 个类型有属性） |
| 区间 | `0x1C6766C .. 0x1D79820 = 0x1121B4 = 56,137 × 0x14`，**精确闭合**，且正好接上 `TBL_PTR`（`0x1D79820`） |

```
propertyStart = (typedef[+0x24] - salt) + 0x97E219E0
propertyCount = (u16(typedef[+0x4A]) 符号扩展 + 0x17A3 - salt16) & 0xFFFF
```

差分验证：**15,442 / 15,442 一致**（100%）。

### 9C.2 记录结构与解码（以汇编为准）

反编译 `FUN_18044ca90` 时 Ghidra 把 `SUB EAX,EBP` 打印成了 `+ iVar3 * -0x1534fcf9`，**括号与符号都有歧义**。`prop_loop.asm` 的原始指令才是权威：

```
18044cbc2  IMUL RAX,RDX,0x64d5          ; gi*0x64D5
18044cbcd  XOR  RAX,0x6d7b1f20
18044cbd3  ADD  RAX,0x10eca71e
18044cbd9  IMUL RCX,RAX,0x7737c996
18044cbe0  SHR  RCX,0x8                 ; 64 位逻辑右移，不截断
18044cbe4  ADD  RCX,0x5505ff6b          ; = prfP
18044cbeb  IMUL RBP,RCX,0x1534fcf9      ; = m
```
每个字段统一做 **`SUB EAX,EBP`**（减法，不是加法）：

| off | 字段 | 变换 | 哨兵 |
|---|---|---|---|
| `0x00` | name | `(rec ^ 0x5566C15D) - m` | — |
| `0x04` | getSlot | `rec - m`，槽位 = 值 `- 0x4CF0C16B` | `0x4CF0C16A` |
| `0x08` | **token** | `(rec - m) - 0x6F268466`（≡ `+0x90D97B9A`） | — |
| `0x0C` | setSlot | `(rec ^ 0x0128B6C5) - m` | `-1` |
| `0x10` | attrs | `(rec ^ 0x72D0B1BB) - m` | — |

### 9C.3 两个重要纠正

**(1) `-0x1534FCF9` 的补码**：`0xEACB0307`，不是 `0xEACB0367`。差一个字节就会让 5 万多条属性名全部解成 `?`。

**(2) 属性表里没有类型字段**。偏移 `0x08` 曾被我当成 `typeIdx`，但解出来恒为 `0x17000001 + 局部计数`。真相是：

- `0x17` = **ECMA-335 的 Property 表编号（23）**，所以这是 `0x17000000 | row` 形式的 metadata token
- 全部 56,137 条 token 的高字节 **都是 `0x17`**
- row 在 **142 个块**内从 1 连续递增（26665 为最长块），说明原始程序集有 142 个，各自维护 Property 表行号

这与官方布局一致：`Il2CppGlobalMetadataPropertyDefinition` 只有 `{nameIndex, get, set, attrs, token}`，**本来就没有类型**。运行时的 `Il2CppPropertyInfo`（`0x28` 字节）也没有类型域——属性类型必须由 getter 的**返回类型**给出。

右侧 `attrs` 全部为 `0`（`PropertyAttributes.None`），符合 Roslyn 对普通属性的输出。

### 9C.4 getSlot / setSlot = 类内方法槽（已闭合）

槽位不是全局方法索引（范围仅 `0..2704`），而是**类内方法槽**。全局方法索引 = `typedef.methodStart + slot`。

以 `UnityEngine.Transform`（`methodStart = 22599`，109 个方法）验证，20 条属性全中：

| 属性 | getSlot / setSlot | 命中方法 |
|---|---|---|
| `position` | 1 / 2 | `get_position` / `set_position` |
| `localPosition` | 5 / 6 | `get_localPosition` / `set_localPosition` |
| `eulerAngles` | 13 / 14 | `get_eulerAngles` / `set_eulerAngles` |
| `localEulerAngles` | 15 / 16 | `get_localEulerAngles` / `set_localEulerAngles` |
| `right` | 17 / 18 | `get_right` / `set_right` |

全表联名验证：55,046 条有 getter 的属性中，**29,010 条精确等于 `get_ + 属性名`**（mscorlib 等未混淆程序集 100%）；其余全部是**显式接口实现**（属性 `System.Collections.IList.IsFixedSize` → getter `System.Collections.IList.get_IsFixedSize`）或被 IFix 分别重命名的混淆类型，属正常。另 1,091 条属性只有 setter 或两者皆无（后者为 IFix 注入）。

### 9C.5 产物

`bh3_properties.tsv`，10 列：

```
typeIdx  typeName  propIdx  propName  token  attrs  getSlot  getter  setSlot  setter
3223  UnityEngine.Transform  4106  position  170001E1  0  1  22600:get_position  2  22601:set_position
```

### 9C.6 属性类型（已补全，56,137 / 56,137）

属性表的记录里**没有类型字段**——这是 `Il2CppPropertyDefinition` 的原生设计（类型由 getter/setter 的方法签名承载）。
所以属性类型必须**反查方法表**：

```
propType = methods[getter].returnType        # 首选：getter 返回类型
若 getter 缺失 → methods[setter].params[0]   # 退化：setter 第一个参数类型（索引 = parameterStart）
```

`getSlot/setSlot → 全局方法索引 = typedef.methodStart + slot`（§9C.4 已闭合），再查 §9D 解出的方法记录。

实测来源分布：

| 来源 | 条数 | 占比 |
|---|---|---|
| 由 getter 返回类型 | **55,046** | 98.06% |
| 由 setter 参数类型（无 getter） | **1,091** | 1.94% |
| 缺失 | **0** | — |
| **合计** | **56,137** | **100%** |

语义锚点（`System.Exception` 六条属性类型逐条命中）：

| 属性 | 解出类型 | 期望 |
|---|---|---|
| `Message` | `string` | ✅ |
| `Data` | `System.Collections.IDictionary` | ✅ |
| `InnerException` | `System.Exception` | ✅ |
| `StackTrace` | `string` | ✅ |
| `Source` | `string` | ✅ |
| `HResult` | `int` | ✅ |

其它抽查：`String.Chars: char`、`String.Length: int`；`List`1` 的 `Capacity: int` / `Count: int` / `IsFixedSize: bool`；
`UnityEngine.Transform` 20 条全为 `Vector3` / `Quaternion` / `float` / `Transform` 等（无一条落空）。

只有 1 处形态可辨识的例外：泛型属性会显示成 `System.Collections.Generic.IEnumerable`1<>*`——
因为属性签名里的泛型实参指向的是**类定义**而非特定实例化，`*` 标记「此处未实例化」。

产物：`bh3_properties_v2.tsv`，8 列：

```
typeIdx  typeName  propIdx  propName  propType  token  getter  setter
218  System.Exception  172  Message  string  170000AD  2094:get_Message
218  System.Exception  177  HResult  int     170000B2  2110:get_HResult  2111:set_HResult
```

---

## 9D. 方法表 + 参数表（新增，完整解出：含签名）

### 9D.1 定位

| 项 | 值 |
|---|---|
| 全局 | `DAT_188198E58` |
| 变换 | `SUB 0x17A3B99` |
| 段偏移 | `0x0FA8318` |
| 记录长 | `0x20` |
| 条数 | **408,458**（尾部 3 条为填充，名字与类型全为噪声） |
| 区间 | `0xFA8318 .. 0x1C1EE78` |

注意：本作把标准 `Il2CppMethodDefinition` 的字段顺序**整体重排**了，名字不在 `+0x00` 而在 `+0x0C`。
所以按「名字能解出」来遍历是正确的，按标准布局去读 `+0x04 = declaringType` 则会全错。

### 9D.2 逆混淆函数（64 位乘法链）

```python
def prf(i):
    x = ((i * 0xB069) ^ 0x3E382F2D) & M64
    x = (x * 0x24147491) & M64
    x = (x ^ 0xF997B4A800) >> 10
    return ((x * 0x3857AACA) & M64) >> 0xE
```
一条 `prf` 同时服务全部字段；`u16` 字段只取 `prf & 0xFFFF`，`u8` 取 `prf & 0xFF`。

### 9D.3 记录布局（终版）

| 偏移 | 字段 | 变换 | 语义 |
|---|---|---|---|
| `+0x00` | declaringType | `(v + 0xE5AF14B4) ^ prf` | 声明类型 Il2CType 索引 |
| `+0x04` | parameterStart | `(v + 0xEA530370) ^ prf` | 参数表起始（`-1` = 无参） |
| `+0x08` | returnType | `(v + 0xAEAE5FEE) ^ prf` | 返回类型 Il2CType 索引（`0xFFFFFFFF` = void） |
| `+0x0C` | name | `v ^ prf ^ 0x1D64B276` | StringIndex |
| `+0x10` | genericContainer | `v ^ prf ^ 0x1A57A870` | `-1` = 非泛型（仅 1,246 条非 -1） |
| `+0x14` | token | `(v + 0xBD6FC398) ^ prf` | `0x06xxxxxx`（MethodDef） |
| `+0x18` | slot | `(u16v + 0xAC47) ^ prf16` | vtable 槽；**`0xFFFF` = 非虚方法**（93,915 条有槽） |
| `+0x1A` | parameterCount | `(u16v + 0x2641) ^ prf16` | 合计 **351,719** |
| `+0x1C` | flags | `(u16v + 0xDAB0) ^ prf16` | MethodAttributes |
| `+0x1E` | iflags | `u16v ^ prf16 ^ 0x4D12` | MethodImplAttributes |

### 9D.4 参数表

| 项 | 值 |
|---|---|
| 全局 | `DAT_188198E30` |
| 变换 | `XOR 0x7EA603B1` |
| 段偏移 | `0x0AC0F38` |
| 记录长 | `0xC` |
| 条数 | **351,719** |
| 区间 | `0xAC0F38 .. 0xEC760C`（0x4066D4 字节） |

```
prf3(i) = (((i*0x90C17665DF3 + 0x125F81CCD2DF4209) ^ 0x390ACBF7) * 0x7BABB4A2 >> 0xF) + 0x476926E5
[0] typeIndex  (v + 0xC6F108A2) ^ prf3
[4] nameIndex  v ^ 0x4CC553B0 ^ prf3
[8] token      v ^ 0x6697D2D9 ^ prf3     0x08xxxxxx（Param）
```

### 9D.5 结果与闭合验证

- `parameterStart` 值域 `0 .. 351,715`，唯一 202,518
- 按 `parameterStart` 排序后**逐条差分**：一致 **408,456 / 408,457**（唯一不符是末尾填充记录，`ps = -1`）
- 末项 `ps + pc = 351,719`，与 Σ`paramCount` **精确相等**，也与参数表条数一致
- 名字：`message` / `value` / `msg` / `fmt` / `args` / `resourceFormat` / `start` / `length` … 全部可读
- token：`0x08000001` 起连续递增，正是 Param 表

### 9D.6 语义锚点（签名逐字对照）

```
int    System.String::IndexOf(char value)
string System.String::Substring(int startIndex)
string System.String::Join(string separator, string[] value, int startIndex, int count)
char[] System.String::ToCharArray()
string System.String::Format(string format, object[] args)
void   UnityEngine.Transform::SetPositionAndRotation(UnityEngine.Vector3 position, UnityEngine.Quaternion rotation)
void   System.Collections.Generic.List`1::Add(T item)
```

`MethodAttributes` 分布也是教科书形态：`0x0081` 私有|HideBySig、`0x0086` 公有|HideBySig、
`0x1886` 公有|HideBySig|SpecialName|RTSpecialName（构造器）、`0x0096` 公有|静态|HideBySig、
`0x00C6` 公有|虚|HideBySig。

### 9D.7 三个坑

1. **`+0x1A` 不是泛型形参数，是 parameterCount**。最初按「泛型元数」解释，分布 0:50%/1:28%/2:15% 看着也像，
   但只有按 `parameterCount` 解释时，差分与 Σ 才能和参数表条数**同时**闭合 —— 这是唯一能定性的证据。
2. **`+0x10` 才是泛型容器索引**，且它是唯一带 `-1` 哨兵的字段；反编译里它只被当成布尔用
   （`MethodInfo+0x2F = (v != -1)`），不是字段值本身有用。
3. **类型 `data` 域全是指针**，不是索引。`SZARRAY`(0x1D)/`PTR`(0x0F)/`BYREF`(0x10) 的 `data` 指向另一个
   `Il2CType`；`GENERICINST`(0x15) 的 `data` 指向 `Il2CppGenericClass{ i32 typeDefIndex; ptr class_inst; ... }`，
   实参个数在 `class_inst+0`、实参数组指针在 `class_inst+8`。早期当成索引读，结果全是 `?[]` 和 `List<>`。

### 9D.8 产物

| 文件 | 大小 | 内容 |
|---|---|---|
| `bh3_methods_v2.tsv` | 46 MB | 12 列：idx / token / declTypeIdx / declType / name / returnType / flags / slot / iflags / paramCount / genericContainer / params |
| `bh3_method_sigs.txt` | 48 MB | 纯签名视图：`ret Type::Name(args)  // tok=... flags=... slot=...` |
| `bh3_properties_v2.tsv` | 6.3 MB | 属性表 + **propType** |
| `bh3_classes.txt` | **68 MB** | 类定义视图（类型 / 方法签名 / 字段 / 属性 / 事件 一文件读完） |

---

## 9E. 泛型形参表 + 泛型容器表（新增，完整解出）

前一轮方法签名里冒出的 `T314`、`M57` 就是这里的全局形参索引——当时只有索引没有名字。本节把它补齐。

### 9E.1 定位

线索来自 `FUN_18042fe20`（802 字节）——`Il2CType` 类型码 `0x13`(VAR) / `0x1E`(MVAR) 的节点构建器。
`FUN_180430150` 在 `case 0x13 / case 0x1e` 处算出两个值再交给它：

```c
uVar1 = *param_1;                                    // data = 全局形参索引
local_18  = ((uVar1 * 0x34D04BA0E4DB + 0xA13EE8C44CC682A) ^ 0x43427E7D) + 0x10776301;  // 盐
lStack_10 = uVar1 * 0x10 + (DAT_188198e40 + -0x77870e75) + DAT_1899dbaf8;               // 记录指针
uVar2 = FUN_18042fe20(&local_18);
```

| 区 | 常量来源 | 偏移 | 步长 | 条数 |
|---|---|---|---|---|
| **泛型形参表** | `DAT_188198E40 - 0x77870E75` | `0x01C1F458` | `0x10` | **2,772** |
| **泛型容器表** | `DAT_188198E00 ^ 0x7497C9EE` | `0x0055C604` | `0x10` | **1,967** |

形参表区间 `0x1C1F458 .. 0x1C2A198` 恰好等于「方法表末尾 → 表5 描述符起点」，
也就是说：**方法表 0xFA8318 + 408,461 × 0x20 = 0x1C1F458**，之后紧接形参表，再紧接表5。

> 这同时解释了 §10.1 里挂着的一条「未定段」：`0xC77140` 不是段偏移，而是**方法表的字节长度**（408,461 × 0x20）。

### 9E.2 形参记录（0x10 = 4 个 int32）

```python
salt(i)   = ((i * 0x34D04BA0E4DB + 0xA13EE8C44CC682A) ^ 0x43427E7D) + 0x10776301   # 64 位
nameId    = ((i32)rec[+0x04] + 0xEE50A144) ^ (uint32)salt(i)      → FUN_18043ab50
container = (uint32)salt(i) ^ rec[+0x00] ^ 0x6FE8EE1B             # 0xFFFFFFFF = 无宿主
```

`+0x08 / +0x0C` 尚未定名（在 `FUN_18042fe20` 里未被直接读取，可能是约束区）。

### 9E.3 容器记录（0x10）与 VAR/MVAR 的判据

`FUN_18042fe20` 核心：

```c
uVar14 = (uint32)salt ^ rec[0] ^ 0x6fe8ee1b;
if (uVar14 != 0xffffffff) {
    iVar15  = prfC(uVar14);
    puVar13 = uVar14 * 0x10 + (DAT_188198e00 ^ 0x7497c9ee) + buf;
}
if (*(int *)(puVar13 + 0xC) - 0x175A3FDF == iVar15)  iVar6 = 0x13;   // VAR
else                                                 iVar6 = 0x1e;   // MVAR
lVar12 = FUN_18043b320((*(int *)(puVar13 + 4) - 0x1DF344F8) - iVar15);   // 宿主
```

```python
def prfC(c):
    x = ((c * 0x6AE9) ^ 0x2E6F3E3D) & M64
    x = (x * 0x2AD3DD28) & M64
    x = (x >> 0x16) * 0x4C39B37D
    x = (x >> 10) & M32
    return ((x ^ 0x4DFAA6B0) * 0x22449C6E) & M32

flag  = ((crec[+0x0C] - 0x175A3FDF) - prfC(c)) & M32     # 实测只取 0 或 1
owner = (crec[+0x04] - 0x1DF344F8 - (prfC(c) + flag)) & M32
```

**这是本表唯一一处反编译不足以直译的地方**：直译只得到 `prfC(c)`，全表命中 721/1,967；
其余 1,246 条一律差 **+1**。差值 `flag ∈ {0,1}` 就是「是否方法泛型」这一位，
而块里没有显式指令——是混淆器把 `+flag` 折进了比较式。反过来看：

| flag | 容器数 | owner 语义 | owner 范围 | 越界 |
|---|---|---|---|---|
| 0 (VAR) | **721** | 类型索引 | 1 .. 57,388 | 0 |
| 1 (MVAR) | **1,246** | 方法索引 | 796 .. 392,204 | 0 |

**1,246 与方法表里 `genericContainer != -1` 的条数完全相等**——这是本节最硬的交叉验证。

### 9E.4 闭合验证

| 检查 | 结果 |
|---|---|
| 形参表条数 | 2,772 = 全表引用的最大索引 2,771 + 1 |
| 空名 | **0** |
| 容器数 | 1,967（721 类型 + 1,246 方法） |
| 每个容器的形参是否连续升序 | **1,967 / 1,967 全部连续** |
| 容器形参个数分布 | 1:1,565 / 2:288 / 3:51 / 4:18 / 5:7 / 6:6 / 7:6 / 8:6 / 9:4 / 10:3 / 11:2 / 12:2 … |
| 类型容器 owner 去重 | 721（一一对应，无重复宿主） |
| 方法容器 owner 去重 | 1,246（同上） |
| owner 越界 | **0** |

### 9E.5 语义锚点

| 索引 | 名字 | 类别 | 宿主 | 期望 |
|---|---|---|---|---|
| 0 | `<message>j__TPar` | VAR | `<>f__AnonymousType0`1` | ✅ Roslyn 匿名类型形参命名 `<属性名>j__TPar` |
| 2 / 3 | `T1` / `T2` | VAR | `System.ValueTuple`2` | ✅ |
| 26 / 27 | `TKey` / `TValue` | MVAR | method#898 | ✅ |
| 100 | `T3` | VAR | `System.Func`4` | ✅（`Func`4` = TResult,T,T2,T3） |
| 500 | `T7` | VAR | `System.Action`16` | ✅（`Action`16` 形参 T1..T16） |
| 1500 | `TKey` | VAR | `MoleMole.EmptyDictionary`2` | ✅ |
| 2771 | `T` | VAR | `MoleMole.FB.HashTable64`1` | ✅ |

名字分布 top10：`T` 1,290 / `TKey` 124 / `TValue` 118 / `TSource` 117 / `T1` 88 /
`TResult` 82 / `T2` 80 / `T3` 57 / `TContext` 55 / `T4` 43 —— 与 .NET 命名习惯完全一致。

生效后的签名（同一批方法，前后对比）：

```
- void System.Collections.Generic.List`1::Add(T314 item)
+ void System.Collections.Generic.List`1::Add(T item)

+ void System.Collections.Generic.Dictionary`2::Add(TKey key, TValue value)
+ TResult System.Func`4::Invoke(T1 arg1, T2 arg2, T3 arg3)
+ T System.Collections.Generic.IReadOnlyList`1::get_Item(int index)
+ void System.Action`16::Invoke(T1 arg1, ... , T16 arg16)
```

全表 `T<数字>` 形式的残留 = 0（`T10`..`T16` 是 `Action`10`..`Action`16` 的真实形参名，不是占位）。

### 9E.6 产物

| 文件 | 内容 |
|---|---|
| `bh3_generic_params.tsv` | 6 列：idx / name / container / kind(VAR\|MVAR) / ownerIdx / owner（类型名或 `method#N`） |
| `extract_generic_params.py` | 本节全部算法（含 prfC 与 flag 推导） |

---

## 9F. 方法 → 原生地址（新增，已闭合 97.52%）

### 9F.1 定位链路

静态文件里确实存在明文方法指针表，但**不在** `.text` 常规范围内、也**不通过** `Il2CppCodeRegistration.codeGenModules` 数组引用，所以早前用「数组引用 / 结构形状」搜索全部落空。正确链路是：

```
.reloc 的 DIR64 槽位
  → 等距 8 字节游程（1,873 个，>=16 槽）
  → 槽位值落在真实代码区（0x180001000..0x186C56000）的比例 > 50%
  → 「代码指针数组」（1,223 个）
  → 数组起点前 0x18 处是 "*.dll" 名字指针  ⇒ 该数组属于一个模块
```

关键前提是**真实代码区**：`.text` 节头被篡改为 5.4 MB，真实代码是 raw `0x400..0x6C54800`（108.3 MB，`VA = raw + 0xC00`）。用被篡改的节头做范围判定会漏掉 90% 的指针。

### 9F.2 CodeGenModule 记录布局（以数组起点 `A` 为锚）

```
A-0x70  u32  token（本模块最后一个方法 token，如 System = 0x06000DE7）
A-0x68  u64  代码指针（entry point 之类）
A-0x60  u32  哈希（0x3A121Dxx 家族，逐模块不同）
A-0x58  u64  0
A-0x50  u64  → 某个 .rdata 表
A-0x48  u64  → 某个 .rdata 表
A-0x40  u64  → 某个 .rdata 表
A-0x38  u64  → methodPointers   ★ 本节关键字段
A-0x30  u64  哈希常量（0x0962_49Cx_0708_3Dxx，随模块微变）
A-0x28  u32  0x6AAF6xxx（同族常量）
A-0x20  u64  → 去扩展名模块名
A-0x18  u64  → moduleName（"XXX.dll"）
A-0x10  u64  → moduleNameNoExt
A-0x08  u32  timestamp（0x63D5xxxx ≈ 2023-01-2x，IL2CPP 汇编元数据）
```

- 记录**连续排列**且彼此不重叠；`A_k - 0x38` 到 `A_k` 的 0x38 字节头紧贴前一个模块的数组尾部。
- 记录前（`A-0x80..A-0x70` 一带）常紧邻本模块的 **genericMethodTable**：`{u32 token, u32 0, u64 代码指针}` 16 字节元组，全文件 7,492 条 —— 这就是早前 `scan_tok_ptr.py` 找到的那 29 个游程的来源，它只是每模块的泛型方法表，不是全量映射。
- **混淆点**：`A-0x38` 的值经常正好落在「另一条记录的 `A`」上（数组与记录在 `.data` 里交错排布），极易被误读成 `prev` 链表。现在已有硬证据排除该误读：全量反引用查询显示**每个数组在全文件只被引用一次，且引用槽 = 名字槽 − 0x20 = `A-0x38`，188/188 全中**（见 §9F.7）。

### 9F.3 精确条数（两条独立路径互证）

**路径一：RID 多重集还原**

metadata 的方法 token 形如 `0x06xxxxxx`，低 24 位是**模块内 RID（1..c 连续）**。因此全部 408,458 个 RID 的多重集 = ∪ₖ{1..cₖ}，可唯一反解出 188 个模块尺寸：

```python
cnt[rid] += 1
while True:
    r = max(i for i in 1.. if cnt[i] > 0)
    if any(cnt[i] == 0 for i in 1..r): break     # 无缺口才成立
    for i in 1..r: cnt[i] -= 1
    sizes.append(r)
```

结果：**188 个模块，合计 408,458，最大 233,487**，全程无 RID 缺口（自洽性极强）。

**路径二：数组游程长度**

数组区按「代码指针 | 0」连续延伸，长度 = 真实条数 + 0~3（末尾桥接了紧邻的一条邻接数据）。188 个模块的游程合计 408,528，与路径一逐位配对后差值全部落在 `[0,4]`，且**对齐后的总和恰为 408,458**。

| 模块 | 数组 RVA | 条数 | 游程 | 差 |
|---|---|---|---|---|
| `Assembly-CSharp.dll` | `0x08D0A000` | **233,487** | 233,488 | +1 |
| `MetaData.dll` | `0x08F28E90` | 65,639 | 65,640 | +1 |
| `Assembly-CSharp-firstpass.dll` | `0x0913A210` | 18,436 | 18,436 | 0 |
| `mscorlib.dll` | `0x0985CBC0` | 12,749 | 12,750 | +1 |
| `Standard.dll` | `0x09881A90` | 5,747 | 5,748 | +1 |
| `MiHoYoSDK.dll` | `0x0988DC40` | 4,545 | 4,546 | +1 |
| `System.dll` | `0x098AE7C0` | 4,198 | 4,198 | 0 |
| `UnityEngine.CoreModule.dll` | `0x098B8980` | 3,750 | 3,750 | 0 |
| `BehaviorDesigner.Runtime.dll` | `0x098BFF10` | 3,068 | 3,068 | 0 |
| `System.Core.dll` | `0x098C5F60` | 3,047 | 3,048 | +1 |

其余 178 个模块见 `bh3_modules_v2.tsv`（含 100+ 个 `ProtobufSerializer.Part*.dll` / `NetCommand.Part*.dll` 分包）。

### 9F.4 方法 → 模块的配对（平铺法）

仅有尺寸多重集还不够，需知道哪一段方法属于哪个模块。方法表按**声明类型**排序，而类型按**镜像**排序，所以方法表在模块边界处是分段的。用强制平铺求出分段：

```
在位置 p，取「RID 互异的最长前缀」ℓ；
块的条数 c 必须同时满足  c ≤ ℓ、c ∈ 剩余尺寸多重集、set(RID[p..p+c)) == {1..c}
```

结果：**188 块、恰好覆盖 408,458、尺寸多重集被精确耗尽、每块 RID 集合严格等于 `{1..c}`**。

块与模块按**条数**配对，188 个模块中 128 个尺寸唯一（直接确定），60 个处于同尺寸并列组内（按物理序 / 元数据序对齐）。块序示例：

```
块0   start      0  c=12749   → mscorlib.dll
块4   start  13226  c=4198    → System.dll
块5   start  17424  c=3047    → System.Core.dll
块7   start  20512  c=3750    → UnityEngine.CoreModule.dll
```

### 9F.5 取地址

```python
rid  = token & 0xFFFFFF
rva  = *(u64*)(module.methodPointers + (rid - 1) * 8) - 0x180000000
# rva == 0 表示该方法没有编译产物（抽象 / 接口 / 纯泛型定义）
```

### 9F.6 校验

| 校验 | 结果 |
|---|---|
| 解析出的地址越出代码区 | **0 个**（全部落在 `0x1330..0x6C55B00`） |
| 有代码地址 | **398,316 / 408,458 = 97.52%** |
| 地址的 16 字节对齐率 | **398,316 / 398,316 = 100.00%**（对照：`.pdata` 的 938,197 条里只有 454,443 条即 48.4% 是 16 字节对齐 —— 因为其中 54.3% 是 CHAININFO 分片，见 §9F.8） |
| 恰好等于 `.pdata` 的 `BeginAddress` | 327,884 = 82.32% |
| 落在 `.pdata` 已登记函数**体内**（非起点） | **0 个** |
| 落在 `.pdata` 未覆盖区 | 70,432 = 17.68%，**已完全解释**：全部是「无栈帧的叶子桩」，x64 ABI 不要求 unwind 记录，见 §9F.8 |
| 空指针 | 10,142 = 2.48% |

「所有地址要么正好是函数起点、要么落在完全没有 `.pdata` 登记的区域，绝无停在函数体内的」这一条是最硬的判据 —— 说明 `methodPointers` 数组下标与 RID 的对应关系正确（错一位就会大量落在函数体内）。

### 9F.7 独立复核：模块 ↔ 数组的绑定是**证明**出来的，不是假设的

前面 §9F.2 假定「`A-0x38` 就是本模块的 `methodPointers`」。这一条可以反过来验证：**在 `.data`/`.rdata` 全量建索引，查每个数组被谁引用**。

```
扫描 .data/.rdata 所有 8 字节对齐槽 → 建 {值: [槽 RVA]}
对 188 个数组 RVA 逐个查询
```

结果（`ref_check.py` / `refmap.py`）：

| 项 | 结果 |
|---|---|
| 被**恰好一次**引用的数组 | **188 / 188**（0 个多处引用，0 个无引用） |
| 「名字槽相对数组引用槽」的偏移 | **+0x20，188/188 全命中**（唯一变体：+0x80 处另有 1 次同名字串引用） |
| 引用槽 +0x20 处的名字 与 `bh3_modules_v2.tsv` 里该数组的模块名 | **188/188 完全一致，0 处错配** |

即：**每个方法指针数组在全文件里只有一个引用者，引用者的 +0x20 处正好写着同名模块** —— 模块与数组是一一对应且被数据自身证明的，不存在「同尺寸模块配错」的系统性风险。

**数组在内存中的排布**（`array_span.py`）：188 个数组起点按 RVA 排序后，相邻间距 **187/187 都是 8 的整数倍**，且「按记录名槽地址排序」与「按数组 RVA 排序」**完全同序（0 处逆序）**。所以 §9F.4 里「同尺寸并列的 60 个模块按物理序对齐」是有结构依据的，不是碰运气。

### 9F.8 命中率之谜**已完全闭合**：空档是「无栈帧的叶子桩」

#### 9F.8.1 先把 `.pdata` 本身拆对

此前把 `.pdata` 的 938,197 条一律当作「函数起点」，这是错的。按 `RUNTIME_FUNCTION.UnwindInfoAddress` 首字节的 Flags 位（`(b0 >> 3) & 0x1F`，`UNW_FLAG_CHAININFO = 0x4`）分类（`pdata_class.py`）：

| 类别 | 条数 | 占比 |
|---|---|---|
| `CHAININFO` 分片（**不是**函数起点） | **509,555** | 54.3% |
| 真函数起点（16 字节对齐 **且** 非 CHAININFO） | **424,760** | 45.3% |
| `BeginAddress = 0` | 17 | — |

交叉表给出了近乎完美的判据：

| | CHAININFO | 正常 |
|---|---|---|
| 16 字节对齐 | 29,683 | **424,760** |
| 非 16 字节对齐 | **479,872** | 3,865 |

即 **「非 16 字节对齐 ⟺ CHAININFO 分片」，命中率 99.2%**。此前那个「`.pdata` 起点只有 48.4% 对齐」的怪现象，就是这 48 万条分片条目造成的，不是二进制异常。

> **补充（§9G.4 追查后修正）**：剩下那 3,865 条非对齐条目**不是噪声，是 C++ 异常处理的 funclet**。反汇编验证 99.5% 可干净解码并终止于 `ret`/`jmp`，且 **88.8% 的 unwind flags = 3（`EHANDLER|UHANDLER`）**——MSVC 为 `try/__except`、`__finally` 生成的语法块会独立登记 `.pdata`、有完整 unwind 信息，但**不保证 16 字节对齐**。所以准确表述是：**非对齐 = 99.2% CHAININFO 分片 + 0.8% funclet**。funclet 不是 il2cpp 方法，排除在「真函数起点」外是正确的。

换成 424,760 这个正确分母后：**真函数中 327,884 个（77.2%）恰好是某个方法的入口**，其余 96,876 个是运行时/辅助代码。

#### 9F.8.2 空档地址的真面目

70,432 个未命中方法对应 **13,766 个去重地址**。用正确映射（见 §9F.10，`raw = RVA - 0x1400`）逐个线性解码（`gap_final.py`）：

| 观测 | 结果 |
|---|---|
| 终止方式 | `jmp` 8,763（63.66%）／`ret` 4,996（36.29%）／解码中断 7 |
| 长度 ≤ 16 字节 | 10,363 个地址（75.3%） |
| 长度 17–32 字节 | 2,044（14.8%） |
| 长度 33–64 / 65–256 / >256 | 700 / 640 / 19 |
| **按方法条数加权，落在 ≤16 字节桩上的** | **64,797 / 70,432 = 92.0%** |
| 桩的 `jmp` 目标 | 3,428 个不同目标；3,996 次落到真函数起点，1,591 次落到另一个桩（二级转发），201 次其它 |

Ghidra 12.1.4 独立复核（远端 `192.168.0.104`，修正节头后 `ProbeStubs.java`）：

| VA | Ghidra 指令流 | `createFunction` 体大小 |
|---|---|---|
| `0x186AD0AF0` | `NOP` / `ADD RCX,0x18` / `JMP 0x186844210` / `INT3` | **11** 字节（止于 INT3 边界） |
| `0x1826B9250` | `JMP 0x181D1FF70` / `INT3` | **5** |
| `0x186B104B0` | `MOV dword [RCX+0x10],0` / `JMP 0x181D1FF70` / `INT3` | **12** |
| `0x186AEB8D0` | `XOR EAX,EAX` / `MOV [RCX+0x10],RAX` / `JMP …` / `INT3` | **11** |
| `0x186B07C40`（对照，真函数） | `MOV [RSP+8],RBX` / `PUSH RDI` / `SUB RSP,0x20` … 17 条 | 真函数体 |

而 `0x181D1FF70` 本身只有一条 **`RET 0x0`**（3 字节）—— 所以全部「`jmp 0x181D1FF70`」等价于 **`ret`**，这是 ICF 折叠出的共享返回桩。

#### 9F.8.3 结论（原两种解释都被推翻，正确解释是第三种）

IL2CPP 给每个方法都生成**独立入口**，但入口有两种形态：

| 形态 | 是否有 unwind 记录 | 原因 |
|---|---|---|
| **真实现**（有栈帧 / 保存了非易失寄存器） | **有**，在 `.pdata` 中 | x64 ABI 要求 |
| **叶子桩**（尾调用 `jmp` 转发；或 `ret`；或清零 1–2 个字段后 `ret`） | **没有** | 不改 RSP、不碰非易失寄存器 ⇒ 永远不会出现在栈回溯里 ⇒ MSVC 不生成 |

所以 17.68% 既不是解析错误，也不是「共享方法槽」，而是**目标代码本身没有 unwind 需求**。原先的「主解释（漏登记的小函数）」方向对但表述不准；「次解释（共享槽）」被否证——每个桩都独占自己的 16 字节槽位，共享发生在**跳转目标**一侧。

#### 9F.8.4 模块级命中率的机制

命中率 ≈ 「该模块方法被编译成叶子桩」的反面。用「去重地址率」可以直接量出来（`module_fold.py`）：

| 分组 | 模块数 | 方法数 | 去重地址 | 去重率 | 命中率 |
|---|---|---|---|---|---|
| `ProtobufSerializer.*` | 61 | 23,544 | 23,544 | **100.0%** | **100.00%** |
| `NetCommand.*` | 61 | 7,525 | 2,444 | **32.5%** | **15.19%** |
| `UnityEngine.*` | 35 | 10,989 | 9,272 | 84.4% | 45.35% |
| `mscorlib.dll` | 1 | 11,405 | 9,528 | 83.5% | 73.71% |
| `MetaData.dll` | 1 | 65,636 | 48,197 | 73.4% | 88.79% |
| `Assembly-CSharp.dll` | 1 | 229,018 | 192,604 | 84.1% | 86.91% |

机制很清楚：`ProtobufSerializer.*` 每个消息类型的 `.ctor` 都要逐字段反序列化，全是真实现 ⇒ 100% 去重、100% 命中；`NetCommand.*` 的方法大量退化成「空方法/清一个字段」，被 ICF 折叠 ⇒ 去重率仅 32.5%、命中率 15.19%。

极端样本 `NetCommand.Partswitch.dll`：**94 条方法只对应 11 个地址**（`pick_probe.py`）：

| RVA | 方法条数 | 命中 | 内容 |
|---|---|---|---|
| `6AD0AF0` | 30（全部 `GetExtensionObject`） | N | `NOP; ADD RCX,0x18; JMP 0x186844210` |
| `6B104B0` | 22（全部 `.ctor`） | N | `MOV [RCX+0x10],0; JMP ret` |
| `26B9250` | 15（全部 `.ctor`） | N | `JMP ret`（**完全空构造**） |
| `6B129B0` | 15（全部 `GetExtensionObject`） | N | 转发桩 |
| `6AEB8D0` | 6（全部 `.ctor`） | N | `XOR EAX,EAX; MOV [RCX+0x10],RAX; JMP ret` |
| `6B07C40` / `6B07BF0` | 各 1 | **Y** | 真实现（有 `SUB RSP,0x20` 栈帧） |

**工程建议**：批量标注 398,316 个地址时，必须「先 `disassemble` 再 `createFunction`」，不能只靠 `.pdata` 建函数；且 `createFunction` 的默认体长度要截到 INT3 边界，否则短桩会吞掉后面 16 字节对齐的真函数。


### 9F.9 产物

| 文件 | 内容 |
|---|---|
| `bh3_modules_v2.tsv` | 188 行：idx / module / arrayRVA / count / run / delta / timestamp |
| `bh3_method_blocks.tsv` | 188 行：idx / start / count / maxRID |
| `bh3_method_addr.tsv` | **408,458 行**：idx / token / module / rva / name / returnType / params |
| `bh3_module_diag.tsv` | 188 行：逐模块 count / live / exact / null / arrayRVA / recA / hit% |
| `bh3_module_fold.tsv` | 188 行：逐模块 methods / uniq_addr / uniq_pct / hit_pct（§9F.8.4） |
| `bh3_gap_stubs.tsv` | **13,766 行**：每个空档桩的 rva / methods / len / term / jmp_target（§9F.8.2） |
| `bh3_array_span.tsv` | 187 行：数组按地址序的相邻跨度（用于验证连续排布） |
| `close_modules.py` / `tile_blocks.py` / `gen_method_addr.py` | 本节全部算法 |
| `ref_check.py` / `refmap.py` | 反引用唯一性复核 |
| `stat_modules.py` / `module_diag.py` / `array_span.py` / `final_stat.py` | 校验统计 |
| `peek.py` / `annot.py` / `who_refs.py` | 结构观察工具（内存标注 / 反查引用） |
| `dis_gap.py` / `probe_addr.py` / `prev_byte.py` | 地址形态探测（依赖 `capstone`） |
| `pdata_class.py` | `.pdata` 条目分类：对齐 × CHAININFO |
| `calib_raw.py` | 用 `.pdata` 的 (Begin,End) 反解 il2cpp 区 raw 偏移常量 |
| `gap_final.py` / `thunk_census2.py` / `pick_probe.py` | 空档桩形态普查与模块抽样 |
| `module_fold.py` | 逐模块去重率 ↔ 命中率相关性 |
| `hexdump_at.py` | 任意 RVA 反汇编 + 标注 `.pdata` 起点 |
| `fix_sections.py` | 修复两处反分析伪装，生成 `UserAssembly_fixed.dll`（§9F.10） |
| `ProbeStubs.java` / `BlockList.java` | Ghidra 端定点探测脚本（远端 `~/re/ghidra/scripts/`） |

### 9F.10 二进制里有两处**反分析伪装**（本轮新发现，必修）

用 Ghidra 12.1.4（远端 `192.168.0.104`）装载原始 `UserAssembly_slim.dll` 时，`il2cpp` 区域**根本不可见**，`.pdata` 也读不出来。逐一查明是两处节表/数据目录被改：

**伪装一：`il2cpp` 节头被清零**

| 节 | VA | VSize | RawPtr | RawSize | 判定 |
|---|---|---|---|---|---|
| `.text` | `0x001000` | `0x52C7E6` | `0x000400` | `0x52C800` | 真实，未改 |
| `il2cpp` | `0x52E000` | `0x001000` | `0x000000` | `0x000000` | **伪装成空节** |
| `.rdata` | `0x6C56000` | `0x20B3E64` | `0x6C54800` | `0x20B4000` | 真实 |

但 IL2CPP 生成代码真实占据 VA `0x52E000..0x6C55B00`（约 108 MB，占全文件 57%），原始数据紧接 `.text` 之后自 raw `0x52CC00` 起。证据链：

- 全部 398,316 个方法地址落在 `0x52E000..0x6B13B40`，**最小值恰好等于 `il2cpp` 节的 VA**；
- `.pdata` 的 `EndAddress` 最大值 `0x6C55B2A`，正好卡在 `il2cpp` 应占的尾部。

**伪装二：`Exception` 数据目录被指向空洞**

| 项 | 值 |
|---|---|
| 数据目录里的 `Exception` | RVA `0x0ACF9000`，Size `0x00ABC1A4` ← **无任何节声明，Ghidra 报 `Invalid file index for acf9000`** |
| 节表里真实的 `.pdata` | VA `0x09E85000`，VSize `0x0ABC930` |

即：节表里有真 `.pdata`，但数据目录被指到别处，标准工具会认为「没有异常表」。这与伪装一配合，效果是**代码区不可见 + 函数边界不可见**，只能纯手工逆向。

**修复方式**（`fix_sections.py`，只改 6 个字段）：

```
il2cpp   : VA 0x52E000  VSize 0x6727C00  RawPtr 0x52CC00  RawSize 0x6727C00  Chars 0x60000020
           → VA 覆盖到 0x6C55C00（含 .pdata 最大 EndAddress 0x6C55B2A），
             raw 到 0x6C53800（不越过 .rdata 的 RawPtr 0x6C54800）
Exception: RVA 0x09E85000  Size 0x0ABC930
```

修复后 Ghidra 的内存块（`BlockList.java` 实测）：

```
.text   180001000..18052d7ff  size=5425152
il2cpp  18052e000..186c55bff  size=108166144   ← 108 MB 代码区可见
.rdata  186c56000..188d09fff  size=34291712
.data   188d0a000..189e84bb3  size=18328500
.pdata  189e85000..18a9419ff  size=11258368
```

**il2cpp 区的 VA→raw 常量是 `0x1400`，不是 `.text` 的 `0xC00`** —— 这个必须校准，否则字节全错。校准方法（`calib_raw.py`）：对 3,000 个已知 `(Begin, End)` 的真函数，在 `raw = Begin - delta` 处线性解码，看解码是否恰好铺满 `End - Begin`：

| delta | 精确铺满函数体的比例 |
|---|---|
| **`0x1400`** | **94.9%** |
| `0x0C00` | 33.8% |
| `0x1600` | 31.6% |
| `0x0A00` | 31.5% |
| 其余（`0x1000`/`0x2000`/`0x1800`…） | 28%–31% |

唯一胜出且断层明显。**此前用 `-0xC00` 得到的全部字节级统计（如「空档组能解到终止指令 93.0%」）都是错位 0x800 的结果，已作废。**

#### 9F.10.1 rea 连接器在本样本上的限制（实测）

rea 连接器（MCP）确实指向远端 `192.168.0.104`，`open_binary` 可正常绑定并返回 sha256/架构；但它内部走的是「**导入即全量自动分析**」+ 330 秒启动上限：

```
Ghidra did not finish importing and analyzing the target within its 330000 ms
startup deadline (REA_GHIDRA_STARTUP_TIMEOUT_MS)
```

190 MB / 424,760 个真函数的样本不可能在 330 秒内分析完，因此 `binary_overview`（枚举全部 procedure/string，响应 >10 MB）与 `analyze_function`（触发同一轮启动）一律失败。这不是配置错误。

可用方案，按成本排序：

1. **直接用 `analyzeHeadless`（本节采用）**：`-import ... -noanalysis` 只装载不分析，导入约 40 秒，再用脚本定点 `disassemble` / `createFunction`。可控、可复现。
2. 若坚持走 rea：调大 `REA_GHIDRA_STARTUP_TIMEOUT_MS`（如 `3600000`）并配 `REA_GHIDRA_DISABLED_ANALYZERS` 跳过重分析器，然后 `open_binary` 重开。
3. 一次性后台跑完整分析（数小时）落到固定工程，之后复用。

另注意：`analyzeHeadless` 的第一个参数是**工程目录，必须预先 `mkdir -p`**，否则报 `Directory not found`。

#### 9F.10.2 远端机器规格、资源需求与进度监控（实测）

**机器规格（实测）**

| 项 | 实测值 |
|---|---|
| CPU | Intel Xeon E-2124 @ 3.30GHz，**3 逻辑核**（1 socket / 3 core / 1 thread per core） |
| 内存 | **6.2 GiB total**（`free -m` = 6331 MB） |
| Swap | **3.8 GiB**（`/swap.img`，常态 0 B used） |
| 磁盘 | `/` 29G，已用 12–13G，**剩 15–16G** |
| load average | 0.0 / 0.2 / 0.4（空闲） |

**关键坑：`analyzeHeadless` 不读 `MAXMEM`**

`support/analyzeHeadless` 第 11–17 行写死：

```bash
MAXMEM_DEFAULT=2G
GHIDRA_MAXMEM=${GHIDRA_MAXMEM:=${MAXMEM_DEFAULT}}
GHIDRA_HEADLESS_MAXMEM=${GHIDRA_HEADLESS_MAXMEM:=${GHIDRA_MAXMEM}}
VMARG_LIST="-XX:ParallelGCThreads=2 -XX:CICompilerCount=2 -Djava.awt.headless=true"
```

所以：

- 设 `MAXMEM=4G` **完全无效**，JVM 仍拿 `-Xmx2G`（实测 `/proc/<pid>/cmdline` 确认）
- 正确开关是 **`GHIDRA_HEADLESS_MAXMEM=4G`**（或全局 `GHIDRA_MAXMEM`）
- `support/launch.properties` 里 `MAXMEM` 为空 ⇒ GUI 走 JVM 默认（物理内存/4 ≈ 1.5G），headless 走 2G
- headless 默认就把 GC/JIT 线程压到 2 个，3 核机器不必再调

**实测资源占用**

| 阶段 | 现象 |
|---|---|
| 导入 190 MB dll（`-noanalysis`） | 约 40 秒；工程目录 **802 MB** |
| 分析启动后 5.5 分钟 | java RSS **稳定 1.19 GiB**（2G 堆内），CPU **115%**（≈1.15 核），swap 0 |
| 系统可用内存 | 从 4.8 GiB 降到 **2.2–2.5 GiB** |

**结论：瓶颈不是 CPU，是分析器的单线程性。** 3 核里只有约 1.15 核在忙——Ghidra 的 analyzer 大多单线程，加核无用。真正受限的是堆大小和总时长。

**分级配置建议**

| 目标 | 命令要点 | 预期 |
|---|---|---|
| 定点反编译（当前做法） | `-noanalysis` + 脚本 `createFunction`/`decompile` | 导入 40 s，每个函数秒级 |
| 建出全部 424,760 个函数 | `GHIDRA_HEADLESS_MAXMEM=4G`，关掉 `Decompiler Parameter ID` / `FunctionID` / `BSim` | 数十分钟量级 |
| 完整自动分析（含反编译参数推断） | 同上，`-analysisTimeoutPerFile` 放开 | **10 小时以上**，不建议 |

磁盘上每个工程 0.8–2.5 GB，15 GB 只够 3–5 个；`proj`(553M) / `proj3`(315M) 是早期残留，可清。

**进度监控：`mon.py`（本地跑，SSH 拉快照）**

```bash
PYTHONPATH=D:/Carol-start/_rea/_pylibs \
  C:/Users/Administrator/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe \
  mon.py --proj proj4          # 单次快照
  mon.py --proj proj4 -w 30    # 每 30 秒刷新
```

实测输出：

```
┌─ 快照 2026-10-23 00:59:37
│ 进程  PID 16953   CPU   114%  RSS    1217 MB  已运行 05:28
│ 堆    上限 -Xmx2G
│ 内存   4032 /  6331 MB 已用   可用  2298 MB
│ Swap  已用     0 MB
│ 磁盘  13G 15G 46% /
│ 负载  1.12 0.82 0.62 2/307 20252
│ 工程  /home/nas/re/ghidra/proj4/bh3fix.rep  1.6G  (+0.0 MB, +0.0 MB/min)
│ 落盘  最新 db 802.4M   1546s 前（保存时才会写，分析中不写属正常）
│ 阶段  ... (PdbUniversalAnalyzer)
│ 日志  INFO  Packed database cache: /var/tmp/nas-ghidra/packed-db-cache
│ 日志增 +0.7 KB / 15 秒
│ 判定  正常
└────────────────────────────────────────────────────────────
```

三层信号，缺一不可：

1. **进程层**：`ps -eo rss,comm` 抓 `java`（**不能按 args grep `java`**，会把 SSH 的 `bash -c` 自己抓进来）；顺带读 `/proc/<pid>/cmdline` 里的 `-Xmx` 确认堆上限真的生效了
2. **内存层**：`free -m` 的 available + swap used。swap 一旦开始用，速度掉一个量级；available < 400 MB 就是 OOM 前兆
3. **活性层**：**日志文件大小增长**才是可靠信号，不是工程目录体积——Ghidra 只在保存时落盘，分析中 db 文件长时间不变是正常的

**Ghidra 自带日志不给逐 analyzer 进度**：`analyzeHeadless` 只在少数 analyzer（如 `PdbUniversalAnalyzer`）打 INFO，默认不打印「当前跑到第几个分析器」。要看细粒度进度必须在脚本里自己埋点（每 N 个函数打一行 `PROGRESS funcs=...`），或用 `GHIDRA_HEADLESS_JAVA_OPTIONS` 调日志级别。

**别误杀**：`ps` 里那个 `comm=MainThread` 的 node 进程（约 330 MB）是 **rea MCP 服务本身**（`node /home/nas/.local/bin/rea mcp`），不是僵尸 java，杀了连接器就断。

---

## 9G. Ghidra 全量建函数：召回率 100%（里程碑）

**结论：424,760 个真函数起点已全部在 Ghidra 工程 `proj4` 中建出，一个不漏。**

### 9G.1 做法

```bash
GHIDRA_HEADLESS_MAXMEM=2G ~/opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless \
  ~/re/ghidra/proj4 bh3fix \
  -process UserAssembly_fixed.dll \
  -analysisTimeoutPerFile 900 \
  -scriptPath ~/re/ghidra/scripts \
  -postScript FuncCount.java
```

即「导入（`-noanalysis`，约 40 s）→ 单独跑一次带超时的全量分析」。15 分钟超时到点时后续分析器被中断，但**建函数阶段早已完成**：

```
ERROR REPORT: Analysis timed out at 900 seconds. Processing not completed
INFO  FuncCount.java> FUNCCOUNT total=429850 bodyBytes=106894449 heapUsedMb=1241 heapMaxMb=2048
```

- `total=429850`：Ghidra 建出的函数数
- `bodyBytes=106894449`（**101.9 MB**）：函数体总字节，对应 il2cpp 代码区 108.2 MB 的 **94.2%**
- `heapMaxMb=2048`：确认实际生效的是 2G 堆（`MAXMEM=4G` 无效，见 §9F.10.2）

### 9G.2 三方对账（集合比对，不是数量比对）

把 Ghidra 的 429,850 个函数入口导出（`DumpFuncs.java`），与 `.pdata` 地面真值做集合运算：

| 集合 | 数量 |
|---|---|
| `.pdata` 真函数起点（16 对齐 且 非 CHAININFO） | **424,760** |
| Ghidra 建出的函数 | **429,850** |
| **交集** | **424,760** |
| 真值有、Ghidra 漏 | **0** |
| **召回率** | **100.00%** |
| Ghidra 多出 | 5,090 |

多出的 5,090 个**全部有归属**，没有一个是脏数据：

| 来源 | 数量 | 说明 |
|---|---|---|
| 「非对齐且非 CHAININFO」的 `.pdata` 条目 | **3,865** | 该集合共 3,865 个，Ghidra 收录率 **100%**；我们先前把它们排除在真值外，Ghidra 保守地建了函数 |
| 完全不在 `.pdata` 任何条目里 | **1,225** | Ghidra 从调用目标 / 跳转目标推断出来的函数（1,016 个 16 对齐，209 个非对齐——后者可能是中指令误判） |
| **CHAININFO 分片被误当函数起点** | **0** | ★ 关键：Ghidra 的 PE Exception 分析器**正确处理了 CHAININFO**，509,555 条分片一条都没污染 |

### 9G.3 这件事证明了什么

1. **`.pdata` 解析完全正确**：Ghidra 独立解析出的函数集与我们手写的 CHAININFO 拆分逻辑 100% 吻合，两条独立路径互证。
2. **§9F.8 的「17.68% 空档 = 叶子桩」得到第三方确认**：Ghidra 也没有在那些空档处建函数（除非被调用目标引用），说明它们确实不是 `.pdata` 登记的函数起点。
3. **路线 B 的入口打通了**：424,760 个函数已在工程里，可以直接按地址 `decompile`，不需要再逐个 `createFunction`。

### 9G.4 遗留项已全部闭环

**（1）1,225 个「`.pdata` 外」函数 → 零中指令误判**

把 5,090 个「Ghidra 有、真值没有」的地址逐个定性（`audit_extra.py`）：

| 分类 | 数量 | 判据 |
|---|---|---|
| A 落在某个真函数 `[Begin,End)` 内（＝中指令误判） | **0** | 区间二分查找 |
| B 属于「非 16 对齐 且 非 CHAININFO」的 `.pdata` 条目 | 3,865 | 见 (2) |
| C 命中已知叶子桩 | 547 | `bh3_gap_stubs.tsv` |
| D 其它 `.pdata` 条目 | 0 | — |
| E 完全无登记 | 678 | 见 (3) |

**没有任何一个额外函数落在别的函数体内部**，所以「Ghidra 把中指令误建成函数」这件事**一次都没发生**。

**（2）B 类 3,865 个 = C++ 异常处理 funclet（新发现）**

这批地址是 `.pdata` 里合法的 `BeginAddress`，但**不是 16 字节对齐**，且有真实函数体（17–256 字节占 96.7%）。反汇编验证（`audit_extra2.py`）：

- **3,845 / 3,865 = 99.5%** 可干净解码并终止于 `ret`(3,019) / `jmp`(826)
- 有正常序言：`push rbx` / `sub rsp,0x48` / `mov rax,rsp`
- **unwind flags 分布：`flags=3`（`EHANDLER|UHANDLER`）占 3,434 个 = 88.8%**，`flags=0` 399、`flags=2` 26、`flags=1` 6

⇒ 这是 MSVC 为 `try/__except` / `__finally` 生成的 **funclet（异常处理语法块）**。它们登记在 `.pdata` 里、有独立的 unwind 信息、**且不保证 16 字节对齐**。

这修正了 §9F.8 里「非对齐 ⟺ CHAININFO」的表述：**483,737 条非对齐条目中，479,872 条（99.2%）是 CHAININFO，剩下 3,865 条是 funclet**。funclet 不是 il2cpp 方法，排除在「真函数起点」之外是对的。

**（3）E 类 678 个 = Ghidra 额外发现的叶子桩**

677 / 678 可解码并终止于 `jmp`(652) / `ret`(25)，长度 3–5 字节，前面有 **4 字节填充**（`0xCC`）。典型的 `jmp <大函数>` / `ret 0` 转发桩。它们没被 `.pdata` 登记（因为是叶子、不需要 unwind），也没进我们的桩表（桩表来自方法地址推导，这里是 Ghidra 从跳转目标反向发现的）⇒ **桩表可以从 13,766 补到 14,444**。

**（4）body 边界差异 → 结构性原因，不是错误**

`audit_body.py` 比对 424,760 个函数的 `Ghidra body` 与 `.pdata (End-Begin)`：

| 关系 | 数量 | 占比 |
|---|---|---|
| 完全一致 | 271,718 | 63.97% |
| Ghidra 偏小 | 30,433 | 7.16% |
| Ghidra 偏大 | 122,609 | 28.87% |

对「偏大」的 122,609 个追因（`audit_body2.py`）：

| 原因 | 数量 | 结论 |
|---|---|---|
| **`.pdata` 的 End 恰好是某个 CHAININFO 分片的 Begin** | **119,491（97.5%）** | 函数被拆成多段，主条目 End 只覆盖第一段；**Ghidra 靠流分析把整段走完，是正确行为** |
| End 之后紧跟 `CC`/`90` 填充 | 2,325 | Ghidra 多吃了对齐填充 |
| 两者都不符合 | **793（0.19%）** | 真正待复查，含少量「Ghidra 把下一函数开头吃进来」 |

「偏小」的 30,433 个基本是 `.pdata` End 含尾部对齐填充、Ghidra 只到实际最后一条指令——同样合理。

**★ 自我更正**：先前 §9G.4 曾写「4 个函数 body 异常巨大（682,645 / 440,297 / 327,613×4）是 Ghidra 把大块未定义区并进来」——**这个判断是错的**。核对后 `.pdata` 里这些函数的主条目长度与 Ghidra body **完全相同**（682,645 对 682,645、327,613 对 327,613×4、440,297 对 440,299 差 2 字节），它们本来就是巨型函数（ICF 折叠后的超大 switch/状态机）。**不需要 `clearListing` 重划**。

全库仅 **1 个**真异常：`0x185886D50`，`.pdata` 长度 127 而 Ghidra body 76,316（把后面一大片未定义区吃进来了），需单独处理。

**（5）资源**：完整分析在 2G 堆下 15 分钟跑不完，可用内存一度掉到 **380 MB** 并开始用 swap（35 MB）⇒ 真要跑完整分析必须 `GHIDRA_HEADLESS_MAXMEM=4G`（见 §9F.10.2）。

---

## 9H. 全量调用图：桩污染、真实 hub、启动链（本轮新增）

函数边界建全之后，剩下的最大增量是**边**。`DumpCallGraph.java` 在 `proj4` 工程上遍历
27,234,875 条指令的 CALL/JUMP flow，导出全图：

```
CALLGRAPH-DONE funcs=429850 edges=4373442 indirectCalls=1199540 insn=27234875 errors=0 seconds=77
```

只用 **77 秒**（`-noanalysis` 直接复用已建好的工程）。产物：`bh3_cg_funcs.tsv` 12.8 MB
/ `bh3_cg_edges.tsv` 131 MB（**仅直接调用有边**，1,199,540 个间接调用在静态图里没有目标）。

### 9H.1 第一版分析是错的：入度榜首是「编译器桩」

第一版 `cg_analyze.py` 排出来的入度 Top1 是 `FUN_1804fe400`——**body 只有 10 字节**，
却「被调用 946,440 次、297,273 个不同调用者」。翻字节立刻明白：

```
1804FE3C0  e9 9b 73 f4 ff              jmp  rel32            <- 尾跳桩
1804FE3D0  48 83 ec 28  e8 47 9f f4 ff  sub rsp,0x28; call    <- 抛异常桩（无 ret）
1804FE400  48 83 ec 28  e8 67 a5 f4 ff  sub rsp,0x28; call
1804FE480  e9 db f3 f2 ff              jmp  rel32
```

这是 MSVC 的「**冷区跳板 + 共享抛异常桩**」：热路径里只留一条 5/10 字节的 `call`/`jmp`，
真正的 throw 逻辑集中在 `0x1804FE000` 这一页里的少数几条桩上。
`0x1804FE000` 一页就挤了 **53 个桩**，是全库最密的桩池。

对全部 `body ≤ 32` 的 6,938 个函数逐条解码分类（`thunk_scan.py`，必须读**原始**
`UserAssembly.dll`——`il2cpp` 节占 103 MB，slim 版把它的 raw 摘了）：

| 类别 | 数量 | 含义 |
|---|---|---|
| `short` | 5,347 | 真业务（短函数） |
| `throw` | **793** | `sub rsp,N; call X`，无 `ret` ⇒ **noreturn 抛异常桩** |
| `tailjmp` | **764** | 单条 `jmp rel32` ⇒ 尾跳桩（可穿透） |
| `iatjmp` | 28 | `jmp qword [rip+X]`，导入表跳板 |
| `retonly` | 5 | 只有 `ret`/`int3` |
| `regjmp` | 1 | `jmp reg` |

**桩吃掉 974,477 条边 = 全图的 22.3%**。不穿透桩，任何「核心函数排名」都是假的。

桩自身还有两层：

| 桩 | 指向 | 被多少个桩跳进来 |
|---|---|---|
| `0x1804FE3D0`（throw） | `0x180448320` | **409** |
| `0x1804FE410` | — | 190 |
| `0x1804FF8E0` | — | 73 |
| `0x180448320` | （真正的 noreturn 实现） | 21 |

### 9H.2 异常抛出点：115 万个，占全图 26.4%

穿透 `tailjmp`、把 `throw` 桩单独归档后（`cg_hub2.py`）：

| noreturn 目标 | 抛出点次数 | 来自多少个函数 | 占比 |
|---|---|---|---|
| `0x180448970` | **946,440** | **297,273** | 82.0% |
| `0x180448320` | **186,441** | **75,035** | 16.2% |
| `0x18619E1F0`（`System.ThrowHelper::ThrowArgumentOutOfRangeException`） | 18,794 | 13,981 | 1.6% |
| 其余 9 个 | < 2,200 | — | 0.2% |
| **合计** | **1,153,885** | — | **26.4%** |

⇒ 全库 **429,850 个函数里，297,273 个（69.2%）至少含一处异常抛出点**。
这就是 il2cpp 给每个解引用插 null-check 的代价，也是「为什么 4.37M 条边里四分之一是 throw」。

### 9H.3 穿透后的真实业务 hub

| VA | 调用次数 | 不同调用者 | body | 节 | 定性 |
|---|---|---|---|---|---|
| `0x18042D860` | **393,242** | **124,564** | 432 | .text | 一次性初始化守卫：`cmp [rcx+0xE8],0` → `lock cmpxchg [rbx+0xE8],1` → 前后各调一次导入函数（形态即 MSVC `__Init_thread_header/footer`） |
| `0x1804457F0` | 194,268 | 109,482 | 166 | .text | 运行时辅助（先 `call 0x18043D300` 再取 `[rbx+0xC0]` 链） |
| `0x1835D7F80` | 158,559 | **150,027** | 146 | il2cpp | **`IFix.WrappersManagerImpl::IsPatched`** |
| `0x1835D7ED0` | 158,047 | **149,522** | 90 | il2cpp | **`IFix.WrappersManagerImpl::GetPatch`** |
| `0x18043E4C0` | 103,744 | 39,125 | 134 | .text | 运行时辅助 |
| `0x180436120` | 99,317 | 34,344 | 62 | .text | 运行时辅助 |
| `0x18042CF20` | 66,546 | 50,794 | 231 | .text | 运行时辅助 |
| `0x183B83B70` | 58,289 | 57,641 | 179 | il2cpp | `IFix.ILFixDynamicMethodWrapper::__Gen_Wrap_13490` |
| `0x180436090` | 51,736 | 21,640 | 23 | .text | `cmp ecx,-1 / je → return 0` 索引检查桩 |
| `0x185F64590` | 49,533 | 19,019 | 76 | il2cpp | `System.Type::GetTypeFromHandle` |

**调用点偏移分布**（`insn - 函数入口`）能进一步定性：

| hub | 偏移 0 | ≤64 字节 | 结论 |
|---|---|---|---|
| `IsPatched` | 0.0% | **92.8%** | **序言检查**——补丁判断被插在每个方法体最前面 |
| `GetPatch` | 0.0% | 21.8% | 由包装函数在准备完参数后调用 |
| `0x18042D860` | 0.0% | 19.9% | 真·工具函数，任意深度都在调 |
| `0x180436120` | 0.0% | 0.6% | 同上 |

⇒ **IFix 的补丁检查覆盖约 15 万个方法（35% 的 Ghidra 函数、约一半的有名方法）**。
这条对路线 B 有实际意义：静态看到的 il2cpp 方法体，运行时可能被 IFix 重定向，
所以**任何以「静态方法体」为依据的结论都要先确认该方法没有 `[Patch]`**。

模块级热度（按被调用边计）：`Assembly-CSharp.dll` 978,031 → `mscorlib.dll` 240,226 →
`protobuf-net.dll` 138,695 → `MetaData.dll` 96,931 → `UnityEngine.CoreModule.dll` 69,012。
另有 2,605,922 条边（59.6%）指向**无法映射到 il2cpp 方法**的目标（运行时辅助 + 桩）。

出度 Top 是「巨型初始化/分发函数」，与 §9G.4 的结论一致：

| VA | 出度 | body | 方法 |
|---|---|---|---|
| `0x183144090` | 16,111 | 440,297 | `MoleMole.CommandMap::InitCommandTypes` |
| `0x182D4FD80` | 15,167 | 682,645 | `MoleMole.Bake.HEKCOOEBLFO::.cctor` |
| `0x184768570` | 3,715 | 62,602 | `proto.ProtobufSerializerPartthree::.cctor` |

### 9H.4 入度 0 的 25 万个函数**不是**死代码

| 项 | 数量 | 占 429,850 |
|---|---|---|
| 入度 0（无直接调用者） | **250,355** | 58.2% |
| ├ 能映射到 il2cpp 方法 | **147,589** | 34.3% |
| └ 无方法名 | 102,766 | 23.9% |

147,589 个有名方法没有静态调用者，只能说明它们**只经由虚调用 / 委托 / 反射**被调用——
这些在调用图里没有边（1,199,540 个间接调用全部丢失）。
按模块看，`Assembly-CSharp.dll` 86,079 个（游戏逻辑几乎全是虚方法/事件/协程），
`MetaData.dll` 26,725 个，`mscorlib.dll` 仅 3,498 个。

**结论：不能拿「入度 0」当死代码筛子。** 这个数字是 il2cpp 虚调用密集的直接后果。

### 9H.5 `.text` 前 1.43 MB 不是业务代码（★新发现，补 §9F.10 第三处伪装）

`.pdata` 条目按节统计：

| 节 | 条目数 | 覆盖字节 | 节大小 | 覆盖率 |
|---|---|---|---|---|
| `.text` | **27,619** | 4,691,836 | 5,425,152 | 86.5% |
| `il2cpp` | **397,141** | 58,941,632 | 108,166,144 | 54.5% |

`.text` 里有 6 条 `>20KB` 的条目，其中 **5 条首尾相接**，起点步长恒为 `0x4FFC0`：

```
0x180001330 .. 0x1800512ED   327,613
0x1800512F0 .. 0x1800A12AD   327,613
0x1800A12B0 .. 0x1800F126D   327,613
0x1800F1270 .. 0x18014122D   327,613
0x180141230 .. 0x18016E783   185,683
                              ───────
                       合计 1,496,135 字节 = .text 的 27.1%
```

三条硬证据说明这段是**人工切分**、不是编译器产物：

1. 5 条**共享同一条 UnwindInfo `0x8B8D604`**（`End - Begin` 四种长度完全相同，不可能自然出现）；
2. 内容 **99.99% 是同一种指令**——149,602 条 `mov dword ptr [rip+disp32], 0`（10 字节/条，
   共 1,496,020 字节），写入目标在 `.data` 里**连续递增**（`0x1899419D4`、`+4`、`+4`…），
   即**批量清零约 584 KB 全局区**；
3. 整个 1.43 MB 里只有 **602 个 `c3`（ret）**、1,777 个 `cc`，**没有任何函数间填充**。

也就是说：这是一段被「切成 5 块」的巨型清零例程，`.pdata` 的 Begin/End 在这段里**不可信**。
Ghidra 建出的 4 个 `327,613` 字节 + 1 个 `185,683` 字节巨型函数就是它。

真实 `.text` 代码从 **RVA `0x16E7D0`** 开始（`sub rsp,0x28; lea rcx,[rip+X]; call …`），
有效代码 ≈ 5.29 − 1.43 = **3.86 MB**。

**口径修正**：§9G 的「召回率 100.00%」是**相对于 `.pdata`** 成立的；
`.pdata` 本身这 5 条是伪条目，严格口径下真值应为 **424,755**。这不改变任何业务结论——
metadata 加载链（见 §9H.6）全部落在 RVA `0x16E7D0` 之后，未受影响。

### 9H.6 启动链：从 `DllGetActivationFactory` 到 metadata 读入内存（★直接可用）

把已验证的锚点（`MemoryMappedFile::ReadToMemoryDirect` @ `0x1804F1B20`，
其前 4 条指令后 `call 0x1803F3790`，并在失败分支引用字符串
`"########MemoryMappedFile::ReadToMemoryDirect File::GetLength Fai"` @ `0x1881A6090`）
放进调用图向上追 6 层（`cg_path.py up`），**整条链只有 5 个节点、无分叉**：

```
DllGetActivationFactory            0x180456370  body 554
  └─ 0x18043D350                   body 4,464
       └─ 0x18043EC20              body 3,446    ← metadata 初始化
            └─ 0x180443FC0         body   538    ← LoadMetadataFile（引用字符串 "Metadata" @ 0x1881A2490）
                 └─ 0x1804F1B20    body   171    ← MemoryMappedFile::ReadToMemoryDirect
```

另一条并行入口 `0x1803EDD00`（body 40）也直接进 `0x18043D350`。
`DllGetActivationFactory` 是 COM 导出，Unity 用它触发 il2cpp 运行时初始化。

`LoadMetadataFile`（`0x180443FC0`）的 8 个直接下游（深度 3 共 44 个节点）：

| 下游 | body | 说明 |
|---|---|---|
| `0x1804F1140` | 630 | 路径拼装 |
| `0x1803F4CC0` | 95 | 打开文件 |
| `0x1804F1B20` | 171 | **`MemoryMappedFile::ReadToMemoryDirect`**（映射 + 读入内存） |
| `0x1804F34F0` | 159 | 读后处理（调 `0x1804FE6A0` / `0x1803FAA60` / `0x18050F080`） |
| `0x180509DC8` | 47 | |
| `0x1803FD190` | 60 | |
| `0x1803F0DD0` | 49 | 关闭句柄 |
| `0x18050A3B8` | 17 | |

配合 §2 的结论（**解密不在 `LoadMetadataFile` 里**，而在 `FUN_18043ab50` 按需解密），
现在的完整时序是：**`DllGetActivationFactory` → metadata 初始化 → 映射读入原始字节
→ 需要时才由字符串解密函数按字段解**。这条链也解释了为什么 §9F 的方法地址、§9D 的签名
全都能离线复现：读入内存的就是磁盘上那份字节，没有第二层整文件解密。

### 9H.7 老锚点勘误（不影响的旧结论）

上一轮记录的 `CHECK_RVAS` 里有个别值漏了一位，实测正确值如下：

| 名称 | 本轮实测 | 旧记录 | 备注 |
|---|---|---|---|
| `LoadMetadataFile` | **`0x443FC0`** | `0x43FC0` | 退到 0x43FC0 会落进 §9H.5 的清零区 |
| metadata 初始化 | **`0x43EC20`** | `0x3EC20` | 同上 |
| 调用 `LoadMetadataFile` 处 | **`0x43EC45`** | `0x3EC45` | 同上 |
| `open` / `close` / `malloc` 包装 / 取文件大小 | `0x3F4CC0` / `0x3F0DD0` / `0x4F09A0` / `0x4F1B20` | 同 | **正确** |
| `"Metadata"` 字符串 | `0x81A2490` | 同 | **正确** |
| `"global-metadata.dat"` 字符串 | `0x81A2478` | 同 | **正确** |

> 这条勘误本身有价值：`0x43FC0` 落点看到的是一串 `mov dword [rip+X],0`，
> 如果没做 §9H.5 的审计，很容易误判成「加载器被抹掉了」。

### 9H.8 产物

| 文件 | 内容 |
|---|---|
| `bh3_cg_funcs.tsv` | 429,850 行（va / body / thunk / name），12.8 MB |
| `bh3_cg_edges.tsv` | 4,373,442 行（caller / callee / insn），131 MB |
| `bh3_thunks.tsv` | 6,938 个小函数分类（kind / target / nbytes / section） |
| `bh3_cg_hubs2.tsv` | 429,850 行，穿透后的入度/出度/调用者数/节/方法名/模块 |
| `bh3_cg_throw.tsv` | 12 个 noreturn 目标的抛出点统计 |
| `cg_hub2.out` | 完整分析输出 |

工具：`thunk_scan.py`（桩分类）/ `cg_hub2.py`（穿透 + 重排）/ `cg_path.py`（上下追溯）
/ `identify.py`（VA → 指令 + 调用 + 字符串）/ `stubpeek.py`（任意区间反汇编）。

---

## 9I. 表2 / 表4 收口：一张是类型表（勘误），一张是泛型实例表（明文）

§10.1 里挂着的最大遗留项——「表2（132,220 × 0x28）/ 表4（213,854 × 8）语义未展开」——本轮全部解掉。
结论先说：**这两行之所以长期空着，是因为它们本来就不是"文件里的表"**。

### 9I.1 先纠正一个方法论错误

`0x18043EC20`（metadata 初始化）对表1–表4 只做四件事：

```asm
18043ECE9  mov  eax, [0x188198E78]      ; 取加载期常量
18043ECEF  add  eax, 0xF5B00267         ; 解出"长度"
...                                     ; 魔数除法 → 条数 rbx
18043ED21  call 0x1804F09A0             ; malloc(条数 × 8)
18043ED30  mov  [rcx], r15              ; 逐 8 字节清零（r15 = 0）
18043ED42  mov  [0x1899DBBF0], rax      ; 存运行时全局
```

**整段没有任何 `memcpy`、没有一句从 `buf` 取数。** 所以这 4 个"条数"只是
`void* cache[count]` 的**槽位数**，是运行时惰性缓存的容量，文件里没有对应的表本体。

于是四类东西必须分开看：

| 类 | 特征 | 例子 |
|---|---|---|
| **A. 加密段数据表** | 段基址 + 偏移 + 步长，逐字段解密 | 类型 / 方法 / 字段 / 属性 / 事件 / 参数 / 泛型 |
| **B. `.rdata` 明文静态表** | 直接在 DLL 里，**零解密** | **表4（泛型实例规格）** |
| **C. 运行时惰性缓存** | 只在内存，`malloc` + 首次访问填充 | 表1–表4 的 8 字节指针数组 |
| **D. 加载期常量** | `xor` / `add` 的初值 | 条数、段偏移 |

### 9I.2 表2 = 类型表（§4.1 勘误）

条数推导的完整指令序列（`0x18043ECE9`–`0x18043ED0D`）：

```asm
mov  eax, dword [0x188198E78]        ; 0x0AA0B0FD
add  eax, 0xF5B00267                 ; → 0x0050B364 = 5,288,804
movsxd rbx, eax
movabs rax, 0x642C8590B21642C9       ; ← 魔数
mul  rbx                             ; rdx = high64(魔数 × rbx)
sub  rbx, rdx
shr  rbx, 1
add  rbx, rdx
shr  rbx, 6                          ; ← 这一串等价于「÷ 0x5C」
```

结果 **57,487**，而且 `57,487 × 0x5C = 5,288,804` **精确等于**原始值 ——
5,288,804 是**字节长度**，`0x5C` 是步长。

§4.1 旧写法 `(DAT_188198E78 - 0x0A4FFD99) / 0x28 = 132,220` 有两处错：

1. 除数错：`0x28` → 应为 `0x5C`
2. `5,288,804 / 0x28 = 132,220.1` **不是整数**，当时就该判为可疑

第二重独立证据来自类型构造器 `0x180430980`：

```asm
1804309B3  imul rdi, rdx, 0x5C                     ; 记录步长 0x5C
1804309CF  movsxd rcx, dword [0x188198E08]         ; 0x2B818F13
1804309DA  xor  rcx, 0x2B849DB3                    ; → 0x512A0  ★
1804309E1  add  rcx, [0x1899DBAF8]                 ; + 段基址
1804309FC  add  rdi, rcx                           ; 记录地址 = 段 + 0x512A0 + i*0x5C
```

`0x2B818F13 ^ 0x2B849DB3 = 0x512A0`，与 §9.1 的段偏移 `0x0512A0`（文件内 `0x0513B8`）完全一致。

⇒ **表2 就是 §9 已经完整解出的类型表**，57,487 条 × 0x5C。§4.1 / §4.2 已按此修正。

### 9I.3 表4 = 泛型方法实例化规格表（明文，Il2CppMethodSpec 形态）

**消费链**

```
0x180435E30(idx)                    ; 惰性 getter
  rax = [0x1899DBC00]               ; 213,854 个 8 字节槽
  if (rax[idx]) return rax[idx]     ; 命中直接返回
  r8  = [0x1881A3620] + idx*12      ; 12 字节描述符
  rdx = (i32[r8+4] != -1) ? r9[i32[r8+4]] : 0     ; r9 = [0x1881A35F8]
  r10 = (i32[r8+0] != -1) ? r9[i32[r8+0]] : 0
  call 0x180435C60(i32[r8+8], rdx, r10)           ; 构造并缓存
```

`[0x1881A3620]` 的初值 = VA `0x187127630` = **RVA `0x7127630`，在 `.rdata` 里**。
也就是说这张表 **根本不在加密的 metadata 段内**，是 DLL 自带的**静态明文数据** ——
这就是它"找不到段偏移"的真正原因。

**规模与边界**

| 项 | 值 |
|---|---|
| 基址 | VA `0x187127630` / RVA `0x7127630` / 文件偏移 `0x7125E30` |
| 步长 | 12（3 × int32） |
| 条数 | **213,854** |
| 字节数 | 2,566,248 |
| 结束 RVA | `0x7399E98` |
| 边界校验 | 第 213,853 条仍合法；**第 213,854 条起全为负数垃圾** ⇒ 条数精确 |

**字段（实测，非推断）**

| 偏移 | 语义 | 取值域 | `-1` 占比 |
|---|---|---|---|
| `+0x00` | 方法泛型实参组索引 | `{-1} ∪ [0, 33654]` | 78.75%（168,405） |
| `+0x04` | 类型泛型实参组索引 | `{-1} ∪ [0, 33653]` | 20.33%（43,472） |
| `+0x08` | **方法定义索引** | `[0, 394054]` | 0% |

三种组合恰好铺满，**不存在双 -1 的行**：

| 组合 | 条数 | 含义 |
|---|---|---|
| `+0x00 = -1`，`+0x04 ≥ 0` | 168,405 | 泛型类型的普通方法实例（class 侧有实参） |
| `+0x00 ≥ 0`，`+0x04 = -1` | 43,472 | 非泛型类型上的泛型方法实例（method 侧有实参） |
| 两者都 ≥ 0 | 1,977 | 双层泛型（泛型类型的泛型方法） |

**闭合验证**（`tbl4_verify.py`，拿已 100% 解出的方法表反查）

1. `+0x08` 全部 213,854 条落在方法表 `[0, 408,458)` 内，**越界 0**
2. `+0x00 ≥ 0` 的 45,449 条里，**95.66% 的声明类型不是泛型类型** —— 正好符合"泛型方法"；
   抽样：`Array::AsReadOnly<T>`、`Array::ConvertAll<T,U>`、`Array::Resize<T>`、`Array::BinarySearch<T>`
3. `+0x04 ≥ 0` 的 170,382 条里，**98.84% 的 `genericContainer` 为空** —— 正好符合"非泛型方法"；
   抽样：`ValueTuple`2::.ctor`、`<>f__AnonymousType0`1::Equals`、`SortedDictionary`2::get_Keys`

⇒ 语义确定为 il2cpp 的 **`Il2CppMethodSpec`**，但字段顺序被重排为
`(methodIndexIndex, classIndexIndex, methodDefinitionIndex)`。

```c
/* 等价结构 */
struct Il2CppMethodSpec {   /* 本作重排后 */
    int32 methodGenericArgGroup;   /* +0x00, -1 = 无 */
    int32 typeGenericArgGroup;     /* +0x04, -1 = 无 */
    int32 methodDefinitionIndex;   /* +0x08, 必有效 */
};
/* 213,854 条，明文，.rdata RVA 0x7127630 */
```

产物：`bh3_methodspecs.tsv`（213,854 行，含方法名 / 声明类型 / 泛型容器）。

### 9I.4 顺带收口的三行

| 表 | 结论 | 证据 |
|---|---|---|
| **表3**（408,458 × 8，`0x1899DBBF8`） | per-method `MethodInfo*` 惰性缓存；文件侧数据 = §9D 方法表（段偏移 `0xFA8318`） | 唯一读者 `0x180437120`（§9.5 里用 `methodStart + 0x2822B502` 的那个函数） |
| **表5**（192 × 0x28，段偏移 `0x1C2A198`） | **程序集映像表**：`+0x14` = typeStart，`+0x1C` = typeCount；192 个区间**首尾相接、零空隙零重叠铺满 `0..57,486`**（`sum(count)=57,487`），且记录顺序 = typeStart 升序 | `0x180430980` 内按类型索引扫描 192 个描述符，命中区间写入 `TypeInfo+0x58`；`tbl5_verify.py` 全量验证 |
| **表1**（354,184 × 8，`0x1899DBBE8`） | **死缓存**：`.text` 内只有 init 一处写、零处读；`il2cpp` 节 **0 处**；全文件也搜不到指向它的 `imm64` 绝对地址 ⇒ 分配后从未被消费。语义无法从静态侧确定（疑为裁剪残留 / 为 IFix 补丁预留），仅能确定"354,184 个 8 字节槽位、初值 0" | `xrefscan.py --sec text` + `rawxref.py --sec il2cpp`（字节级 rip 扫描）+ 全文件 `imm64` 搜索 |

> 表5 这个结论还有个额外价值：它证实 §4.3 的字段映射里
> `rec[8] → +0x14`（typeStart）与 `rec[4] → +0x1C`（typeCount）**是同一语义对**，
> 而不是两条独立的计数。

### 9I.5 复现方式

```bash
python xrefscan.py 0x1899DBBF0 0x1899DBC00 --sec text --ctx 12   # 找 getter
python disann.py 0x180430980 0x180430B40 --nohex                  # 类型构造器（带 rip 目标解析）
python rd.py 0x1881A3620 0x1881A35F8 0x1881A35EC                  # 读描述符指针
python tbl4_stat.py                                               # 表4 全量统计
python tbl4_verify.py                                             # 语义闭合验证
python gen_methodspec.py                                          # 导出 bh3_methodspecs.tsv
python tbl5_verify.py                                             # 表5 类型区间铺满验证
```

工具：`rd.py`（按 VA 读 dword/qword）/ `disann.py`（反汇编 + rip 目标自动解析 + 节名 + 解引用值）。

产物：

| 文件 | 内容 |
|---|---|
| `bh3_methodspecs.tsv` | 213,854 行（idx / 方法泛型组 / 类型泛型组 / 方法索引 / 声明类型 / 方法名 / 泛型容器） |
| `bh3_asm_typerange.tsv` | 192 行（asmIdx / typeStart / typeEnd / typeCount），按 typeStart 升序 |

---

## 9J. 符号落地：311,382 个 C# 方法名贴到原生函数上（里程碑）

§9A–§9I 把 metadata 解完了，但那是**磁盘上的数据**。真正能读代码，必须把这套符号
**贴到 443,069 个原生函数**上。本节就是这一刀，也是"路线 B 后半段"的正式开工。

### 9J.1 一句话结果

| 指标 | 结果 |
|---|---|
| 方法 → RVA 条目 | 398,316（97.52% 的方法有原生地址） |
| **去重后唯一函数体** | **311,382**（另 86,934 个是泛型共享别名） |
| **命中并命名** | **311,382 / 311,382 = 100.00%** |
| 其中直接改名 | 297,881 |
| 其中按 metadata 新建函数 | 13,218（12,488 + 730） |
| 保留原名（Ghidra 已识别） | 1,007 |
| 工程函数总数 | 429,990 → **443,209** |
| **全库命名覆盖** | 443,069 个函数中 **332,980（75.15%）** 有 C# 真名；按字节 **80.01%** |
| 命名空间 | **30,041** 个（`ns::Class::Method` 三层） |
| 耗时 | 单轮 5–37 秒（不含 Ghidra 装载） |

### 9J.2 符号表合成（`gen_symtab.py`）

三张已解出的表做 join，输出 `bh3_symtab.tsv`（398,316 行 / 49 MB）：

```
bh3_types_v5.txt      idx → (namespace, typeName)
bh3_methods_v2.tsv    idx → (declTypeIdx, name, returnType, flags, paramCount, params)
bh3_method_addr.tsv   idx → RVA
                        ↓ join
rva  ns  cls  method  ret  params  isStatic  token  module  aliasOf
```

几个必须处理的地方：

| 问题 | 处理 |
|---|---|
| 方法名里有 `.` / `` ` `` / `<>` | 清洗成 `_`：`.ctor → _ctor`、`List`1 → List_1`、`<>c → c` |
| 泛型方法 | 名字加 `_G` 后缀标记（形参真名见 §9E） |
| 泛型共享（同 RVA 多方法） | 第一个当主名，其余写进 `aliasOf` 列 |
| 静态判定 | `MethodAttributes & 0x10` |

### 9J.3 Ghidra 应用（`ApplySymbols.java`）

```java
Address a = space.getAddress(0x180000000L + rva);
Function f = fm.getFunctionAt(a);
if (f == null) f = createFunction(a, name);   // ← metadata 是地面真值，强制建
Namespace ns = resolveNamespace(p[1], p[2]);  // ns 分段 + 类名，建 3 层
f.setParentNamespace(ns);
f.setName(name, SourceType.USER_DEFINED);
f.setComment("C#: <签名> [static] token=...\nGENERIC-SHARED aliases (n): ...");
```

- 每 5,000 个提交一次事务（避免单个巨型事务吃内存）
- 只改 `FUN_` / `thunk_FUN_` / `SUB_` 开头的名字，已有的人工命名不覆盖
- 重名自动加 RVA 低 16 位后缀（实测 0 次触发）
- 同一 RVA 的泛型共享别名写进函数注释（最多列 12 个）

### 9J.4 关键修复：Ghidra 把函数边界算错了

第一轮只做 `getFunctionAt / getFunctionContaining`，结果 12,494 个地址**找不到函数**；
而反编译里出现大量 `func_0x186a650f0` 这类"未解析外部引用"。用 `CheckAddr.java` 一查：

```
186A650F0  fnAt=-  fnContaining=get_Position@1868A63F0  insn=NOP
```

`FlatBuffers.ByteBuffer::get_Position` 的 RVA 是 `0x6A650F0`，但 Ghidra 把它算进了
从 `0x1868A63F0` 开始的一个函数体内 —— **跨了 1.8 MB**。成因是这段区间里大量
**无栈帧叶子桩**（§9F.8 的 `jmp`/`ret` 桩）不被 `.pdata` 覆盖，Ghidra 顺着顺延吞并。

修法：**用 metadata 当地面真值，在地址处强制 `createFunction`**，Ghidra 会把原函数体截断。

修复后：

```
186A650F0  fnAt=get_Position/body=6   fnContaining=get_Position@186a650f0
186B0B910  fnAt=GetInt/body=13        fnContaining=GetInt@186b0b910
```

反编译里 `func_0x` 出现次数：**4 → 0**。这一轮额外拆出 730 个被吞并的函数。

### 9J.5 效果对比（同一个函数，前后）

**落地前**（`decomp_check2.c`）—— 调用链全是数字地址：

```c
longlong FUN_186afdd50(longlong param_1)
{
  lVar5 = thunk_FUN_1804457f0(_DAT_1899e49e0);
  Mono::Xml::SecurityParser::probe_1826b9250(lVar5);
  uVar2 = func_0x000186a650f0(param_1);
  iVar3 = func_0x000186b0b910(param_1,uVar2);
  ...
}
```

**落地后**（`decomp_check3.c`）—— 类、方法、调用链全部可读：

```c
longlong MoleMole::MPProtocol::ActionArg_ApplyLevelBuff::GetRootAsActionArg_ApplyLevelBuff
                   (longlong param_1)
{
  lVar5 = thunk_FUN_1804457f0(_DAT_1899e49e0);
  Mono::Xml::SecurityParser::probe_1826b9250(lVar5);
  if (param_1 == 0) { FUN_1804fe400(); ... }
  uVar2 = FlatBuffers::ByteBuffer::get_Position(param_1);
  iVar3 = FlatBuffers::ByteBuffer::GetInt(param_1, uVar2);
  iVar4 = FlatBuffers::ByteBuffer::get_Position(param_1);
  ...
}
```

函数头注释同时给出完整 C# 签名：

```
/* C#: MoleMole_MPProtocol_ActionArg_ApplyLevelBuff
   ActionArg_ApplyLevelBuff::GetRootAsActionArg_ApplyLevelBuff(FlatBuffers.ByteBuffer _bb)  [static]
   token=06000001 */
```

### 9J.6 命名分布（Top 命名空间）

| 命名空间 | 函数数 | 说明 |
|---|---|---|
| `Global` | 21,531 | 无 namespace 的类型（`Locale` / `SR` 等） |
| `IFix::ILFixDynamicMethodWrapper` | 8,854 | **热更新桥接层**（§9H.3 的 `IsPatched` 家族） |
| `c` | 3,974 | 编译器 lambda 缓存类 `<>c` |
| `ILPBGOFLNIP` | 3,516 | 混淆类名（MoleMole 内） |
| `MoleMole::LevelDesignManager` | 2,978 | 关卡设计器 |
| `MoleMole::Bake::HEKCOOEBLFO` | 2,557 | 烘焙（出度榜首，§9H） |
| `proto::ProtobufSerializerPartthree` | 2,231 | 协议序列化 |
| `AkSoundEnginePINVOKE` | 1,021 | Wwise 音频 |

### 9J.7 仍然没有名字的 110,089 个函数（24.85%）

| 类别 | 规模 | 说明 |
|---|---|---|
| `.text` C++ 运行时 | 27,613 | il2cpp 运行时本体（等价 libil2cpp），**不在方法表里**，要靠开源代码特征匹配 |
| il2cpp 桥接 / 桩 / 泛型适配 | ~80,000 | 方法表里没有对应项的编译器生成代码 |
| 早期 probe 命名残留 | 少量 | 如 `probe_1826b9250`，需清理 |

### 9J.8 复现

```bash
# 本地
python gen_symtab.py                                   # → bh3_symtab.tsv

# 远端
scp bh3_symtab.tsv ApplySymbols.java nas@host:~/re/sym/
GH=~/opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless
GHIDRA_HEADLESS_MAXMEM=4G $GH ~/re/ghidra/proj4 bh3fix \
  -process UserAssembly_fixed.dll -noanalysis \
  -scriptPath ~/re/ghidra/scripts \
  -postScript ApplySymbols.java ~/re/sym/bh3_symtab.tsv ~/re/sym/report.txt 0
```

> 工程改动前已备份到 `~/re/ghidra/proj4_pre_sym`（2.3 GB）。
> 工具：`gen_symtab.py` / `ApplySymbols.java` / `CheckAddr.java`（单点诊断）/ `StatNames.java`（覆盖率统计）。

---

## §9K 实例字段偏移还原（第 4 步）

### 9K.1 一句话结果

**419,568 个字段全部拿到 `{偏移, static/instance, 尺寸}` 三件套**，其中 **393,394 个是实例字段且偏移非空**；
**50,183 个有字段的类型**里 **23,821 个（47.5%）精确命中**、1,554 个松弛命中；
**9 个已知地面真值全部对上**（Vector3=12 / Vector2=8 / Vector4=16 / Quaternion=16 / Color=16 / Rect=16 / Matrix4x4=64 / Bounds=24 / String=22）。

产物：`bh3_layout.tsv`（38.7 MB，每字段一行）+ `bh3_instsize.tsv`（每类型实例大小）+ `bh3_layout_report.txt`。

### 9K.2 为什么不能从元数据直接算（关键否定结论）

字段记录是 **12 字节** `{u32 A; u32 typeIdx; u32 nameId}`，没有第四个 dword。逐字段验证 `A`：

| 类型 | 字段 | fieldIdx | A |
|---|---|---|---|
| `UnityEngine.Vector3` | `kEpsilon` | 12451 | `0x066CF188` |
| | `x` | 12452 | `0x066CF189` |
| | `y` | 12453 | `0x066CF18A` |
| | `z` | 12454 | `0x066CF18B` |
| `UnityEngine.Vector2` | `x` | 13444 | `0x066CF569` |
| `System.String` | `m_stringLength` | 1215 | `0x066CF5C4` |

`A` 逐字段 **+1**、且 `A − fieldIdx` 在同一类型内恒定（Vector3 与 Vector2 同为 `0x066CC0E5`，String 为 `0x066CD105`）
⇒ **`A = C(类型) + 字段下标`，是索引的线性函数，不含任何 per-field 信息**。

- 不像 token：`A >> 24 == 0x04` 占比 **0.00%**
- 不像偏移：`A < 0x2000` 占比 **0.00%**；全部 419,568 条 A 落在 `[0x066CF105, 0x0671AF2E]` 这条**宽 315,433 的窄带**里
- 不像 flags：bit25/bit26 **100% 恒置位**，其余高位 0.00%
- 当池索引解：可解率仅 **3.10%**，且解出来的多是 `'MoleMo'` 这类垃圾（索引落在池中段密文区）

> **结论：这份元数据里没有 static 标志，也没有字段偏移。** 只能从代码反推。

旧版 `bh3_layout.py` 直接按声明顺序求和，把 static 全算进实例，于是 `Vector3` 得 96 字节（应 12）、`Vector2` 得 80（应 8）——**该版本产物不可信，已废弃**。

### 9K.3 地面真值来自代码

`UnityEngine.Vector3::get_magnitude`（RVA `0x6A4ED30`）：

```asm
186A4ED30  movss xmm1, dword ptr [rcx + 4]
186A4ED35  movss xmm0, dword ptr [rcx]
186A4ED39  movss xmm2, dword ptr [rcx + 8]
```

⇒ 实例布局 12 字节，static 不在实例内。**这就是探针的立足点：非静态方法的第 1 个参数就是 `this`。**

### 9K.4 Ghidra 反编译器在此样本上不可用（重要经验）

原计划用 `DecompInterface` 反编译每个类型的代表方法，取 `param_1 + 0xNN`。实测失败：

```
ERRMSG Exception while decompiling 1857f0310: process: timeout
ERRMSG Exception while decompiling 185311020: process: timeout
```

- 3 个方法/类型时 30 types/s 正常，跑到第 13,000 个类型后**吞吐崩到 2.8/s**，随后**完全卡死**（连 30 秒超时都不再触发，进程 0% CPU）
- 加「函数体 > 20,000 地址直接跳过」+ 超时降到 10s 也救不回来
- 根因是 §9J.4 那类**巨型函数边界**（il2cpp 区大量无栈帧叶子桩不在 `.pdata`，Ghidra 顺延吞并）

**改路线：放弃反编译器，本地用 capstone 扫汇编 + 自己跟踪 `this` 寄存器。**

| 方案 | 37,752 类型 / 258,643 方法 | 结果 |
|---|---|---|
| Ghidra 反编译器 | 30 分钟只跑到 13,000，随后卡死 | ❌ |
| 本地 capstone 汇编扫描 | **218 秒**，命中 32,904 类型（87.2%） | ✅ |

**快 20 倍以上，且完全确定性、可断点重跑。**

### 9K.5 汇编扫描器（`scan_this.py`）

Win64 MS ABI，跟踪「持有 `this` 的寄存器集合」：

```
入口 this_regs = {rcx}
mov dst, src 且 src ∈ this_regs   → dst 入集合
其它任何写 dst                     → dst 出集合
call 之后 rcx/rdx/r8-r11 被破坏    → 移出集合
出现 [reg + disp] 且 reg ∈ this_regs、disp ∈ [0, 0x4000] → 记录 disp
```

停止条件：`ret` / `int3` / `ud2` / `hlt`，或 1,200 条指令 / 8,000 字节。

#### ★ 两个必须知道的坑

**坑 1：读或写都算访问。** 第一版只处理 `ops[0]` 是内存操作数的情况，于是 `movss xmm1, [rcx+4]` 这种**读**被漏掉，`get_magnitude` 返回空集。改成遍历**所有**操作数即可。

**坑 2（更致命）：sret 方法的 `rcx` 不是 `this`。** 返回「按值返回的大结构体」（>8 字节）时，MS x64 用 `rcx` 传**隐藏返回缓冲区指针**，`this` 在 `rdx`。搞错就会把「写返回值」的偏移当成字段访问：

```
Vector3.get_down  实测偏移 {0x0, 0x8}   ← 其实是往返回缓冲区写
```

判定：`returnType` 解析成 struct 且尺寸 > 8 ⇒ `sret=1` ⇒ `this_regs = {rdx}`。
探针表因此带标记：`rva:0` / `rva:1`。全量 258,643 个方法里 **4,135 个是 sret**。

> 尺寸判定不能简单求和：粗算会把 static 算进去，`Vector2`（真 8 字节，走寄存器返回）被误判成 sret。
> 解法：**用上一轮解出的布局回填尺寸**（`sizes.py` 读 `bh3_layout.tsv` 的 `offset+size` 最大值），迭代两轮后收敛。

### 9K.6 布局求解：子序列匹配 DP

模型：IL2CPP 按**声明顺序**给实例字段分配偏移，**static 不占实例空间**。
于是问题变成：在字段序列里挑一个**子序列**当实例字段，使算出的偏移集合 == 观测集合。

DP 状态 `(i, j, cur, ex)`：`i`=字段下标、`j`=已命中的观测偏移数、`cur`=当前偏移、`ex`=已放入的「未观测实例字段」数。

每个字段三个分支：
1. **命中**：`align(cur, align_i) == O[j]` → 实例字段，消费一个观测
2. **static**：不占空间，`cur` 不变
3. **未观测实例字段**（`align(cur, align_i) < O[j]` 且 `ex < 3`）：ctor 漏写 / 没人访问过

`align(cur, align_i) > O[j]` 直接剪掉——放下去就越过了待命中的观测偏移。

第一轮 `ex = 0`（精确），失败才放开到 `ex ≤ 3`（松弛）。

#### ★ 对齐规则：结构体取自身自然对齐，不是 `min(size, 8)`

`UnityEngine.Bounds` 暴露了这个 bug：`m_Center`(Vector3, 12 字节) 之后 `m_Extents` 被算到 `0x10`，整体尺寸 28（应 24）。
因为 Vector3 是 12 字节，但**对齐只有 4**（全是 float）。改成「结构体对齐 = 其字段对齐的最大值（上限 8）」后：

```
Bounds  conf=L size=24  m_Center@0x0  m_Extents@0xC   ✅
```

#### ★ 结构体套结构体的尺寸必须迭代

`size_of_type_name` 若递归求和会把 static 算进去（Vector3 → 96），导致含 Vector3 字段的类型全部错位。
解法：**先粗略解一遍 → 用解出的 `offset+size` 最大值回填 → 重解**，实测 3 轮收敛（尺寸更新 25,192 → 728 → 4 → 3）。

### 9K.7 属性访问器硬约束（消歧的唯一可靠手段）

`get_X` / `set_X` 的观测直接把「**字段名 → 偏移**」钉死。对 40,650 条属性访问器扫描后，
取出「**恰好 1 个偏移**」的 9,045 条作为 DP 的**硬约束**（该字段只能落在那个偏移）。

效果立竿见影：

| 类型 | 无约束 | 有约束 |
|---|---|---|
| `UnityEngine.Matrix4x4` | 224 字节 / 18 实例字段 | **64 字节 / 16 实例字段** ✅ |
| `UnityEngine.Rect` | 96 | **16**（`m_XMin/m_YMin/m_Width/m_Height`）✅ |

### 9K.8 结果与自检

```
迭代 1: H=23796  尺寸更新 25192
迭代 2: H=23821  尺寸更新 728
迭代 3: H=23821  尺寸更新 4
迭代 4: H=23821  尺寸更新 3        ← 收敛

[每类型置信度]   H 47.5% / R 3.1% / L 14.6% / X 34.9%
[字段行]        H 21.1% / R 3.9% / L 18.0% / X 56.9%
实例字段 393,394 行 / static 26,174 行
按种类：struct 2,475 / class 39,161 / enum 8,547
```

| 类型 | 解出实例大小 | 期望 | conf |
|---|---|---|---|
| `UnityEngine.Vector3` | 12 | 12 | H |
| `UnityEngine.Vector2` | 8 | 8 | H |
| `UnityEngine.Vector4` | 16 | 16 | H |
| `UnityEngine.Quaternion` | 16 | 16 | H |
| `UnityEngine.Color` | 16 | 16 | H |
| `UnityEngine.Rect` | 16 | 16 | H |
| `UnityEngine.Matrix4x4` | 64 | 64 | H |
| `UnityEngine.Bounds` | 24 | 24 | L |
| `System.String` | 22 | 22 | H |

`System.String` 解出 `m_stringLength@0x10` / `m_firstChar@0x14`，与 §9 早已独立解出的结论**完全一致**——这是一次跨章节的交叉验证。

### 9K.9 已知局限（必须读）

**(a) 偏移可信，名字可能错位。**
每个实例字段的偏移都对应一次真实的 `[this+disp]` 访问，所以**偏移本身是被钉住的**。
但「哪几个声明字段是实例字段」在观测不完整时无法唯一确定：

```
UnityEngine.Vector3   偏移 0x0 被标成 kEpsilon（实为 x）
```

原因：`kEpsilon` 是 `const`（不占实例空间），而 `kEpsilon/x/y/z` 四个 float **尺寸完全相同**，
观测集合 `{0,4,8}` 对 `{kEpsilon,x,y}` 和 `{x,y,z}` 都成立。Vector3 的 `x/y/z` 是**公有字段不是属性**，
拿不到 getter 约束，因此无解。

同尺寸相邻字段错位是**信息论层面的不可判定**，不是算法缺陷。要修只有两条路：
1. 找到 `const/literal` 表（field-default-value），把 const 字段直接排除出布局
2. 从 `.cctor` 的全局基址写入反推 static 布局

**(b) 观测不完整会把实例字段误判成 static。**
例如 `proto.QAvatarBattleMoveNotify` 只有 2 个实例方法有地址（`nProbe=2`），
只观测到 `{0x10, 0x18}`，于是中间 3 个 float 被标成 static。
这类类型在 `bh3_layout.tsv` 里带 `nProbe` 列，**`nProbe ≤ 2` 时字段名与 static 判定都应打问号**。

| 探针方法数 | 类型数 | 其中 H |
|---|---|---|
| 6+ | 12,835 | 53% |
| 3–5 | 10,058 | 69% |
| 1–2 | 14,859 | 68% |
| 0 | 12,431 | 0%（conf 必为 X） |

**(c) `X` 的 34.9%（17,494 类型 / 238,895 字段行）完全没有观测** —— 这些类型没有带地址的实例方法，静态侧无从下手。

### 9K.10 复现

```bash
# 1) 生成探针（每类型全部实例方法，带 sret 标记）
python gen_probe_all.py        # → bh3_layout_probe_all.tsv
python gen_probe3.py           # → bh3_prop_probe.tsv / bh3_prop_map.tsv

# 2) 本地汇编扫描（无需 Ghidra，218 秒 / 258,643 方法）
python scan_this.py bh3_layout_probe_all.tsv bh3_layout_obs_all.tsv
python scan_this.py bh3_prop_probe.tsv       bh3_prop_obs.tsv

# 3) 布局求解（含尺寸迭代，30 秒）
python bh3_layout3.py          # → bh3_layout.tsv

# 4) 汇总报告
python gen_layout_report.py    # → bh3_instsize.tsv / bh3_layout_report.txt
```

工具链：`scan_this.py`（汇编扫描）/ `sizes.py`（尺寸与 sret 判定）/ `bh3_layout3.py`（DP 求解）/ `gen_probe_all.py` / `gen_probe3.py` / `gen_layout_report.py`。

---

## §9L 字段布局写回 Ghidra（第 5 步）+ 布局算法重做

### 9L.1 一句话结果

反编译输出从 `*(undefined8 *)(param_1 + 0x28) = uVar1;` 变成 `this->mission_ids = puVar1;`，
并且**顺带查出上一轮布局表本身有系统性错误**（proto 类 44.5% 的字段被误判成 static，
导致后续字段名整体前移），改用「声明顺序对齐打包」后重建，`pad` 全部消失。

```
proto::BulletinActivityConfig::_ctor(BulletinActivityConfig *this)
{
  this->activity_id = 0;
  this->activity_type = 0;
  this->begin_time = 0;
  this->end_time = 0;
  this->bulletin_id = 0;
  this->mission_ids = puVar1;          /* new List<uint>() */
  this->type_param_list = puVar1;
  this->type_param_str = _DAT_189b4a238;   /* string.Empty */
  this->min_player_level = 0;
  this->max_player_level = 0;
  this->item_list = puVar1;
  ...
  this->weight = 0;
  ...
  this->unlock_param_str = _DAT_189b4a238;
  return;
}
```

对照改造前：

```c
void proto::BulletinActivityConfig::_ctor(longlong param_1)
{
  *(undefined8 *)(param_1 + 0x10) = 0;
  *(undefined8 *)(param_1 + 0x18) = 0;
  *(undefined4 *)(param_1 + 0x20) = 0;
  ...
  *(undefined8 *)(param_1 + 0x28) = uVar1;
  *(undefined8 *)(param_1 + 0x38) = _DAT_189b4a238;
```

### 9L.2 第一次写回为什么跑不起来（Ghidra 三个坑）

**(1) `StructureDataType.add()` 没有 3 参数重载**

```java
// ✗ 编译报 incompatible types: int cannot be converted to String
sdt.add(ft, flen, arg);
// ✓ 唯一可用签名（javap 确认）
DataTypeComponent add(DataType dt, int length, String name, String comment);
sdt.add(ft, flen, arg, null);
```

**(2) 44 万个函数建出来时参数表是空的**

`getParameterCount() == 0`，`getParameter(0)` 返回 null，所以 `p0.setDataType(...)` 直接 NPE。
必须**新增**参数而不是改已有参数：

```java
if (f.getParameterCount() > 0) {
    f.getParameter(0).setDataType(ptr, SourceType.USER_DEFINED);
} else {
    // 建函数时没做签名推断 → 参数表为空，直接追加 this，Ghidra 按 x64 约定放到 RCX
    f.addParameter(new ParameterImpl("this", ptr, currentProgram), SourceType.USER_DEFINED);
}
```

`addParameter` 还有重载二义性（`addParameter(Variable, SourceType)` 会编译失败），
必须显式 `new ParameterImpl(...)`。

**(3) `dtm.remove()` 是性能核弹（本轮最大的坑）**

二次运行时脚本卡住 4 分钟无任何输出，CPU 100%。抓 jstack 才看清：

```
"main" RUNNABLE
  at db.NodeMgr.addNode(NodeMgr.java:209)
  at db.Table$LongKeyRecordIterator.hasNext(Table.java:2211)
  at ghidra.program.database.code.CodeManager.clearData(CodeManager.java:2674)
  at ghidra.program.database.data.ProgramDataTypeManager.deleteDataTypesUsed(...)
  at ghidra.program.database.data.DataTypeManagerDB.remove(...)
  at ApplyTypes.run(ApplyTypes.java:141)
```

`remove` 会调 `deleteDataTypesUsed` → `clearData`，**遍历整个程序的地址空间**清引用。
在 443,209 个函数的库上单次就是几十秒级，2.4 万次根本跑不完。

结论：**绝不删已有类型**。要改布局就换一个新的分类根（`/bh3v2` → `/bh3v3` → `/bh3v4` → `/bh3v5`），
让新结构体与旧的并存，旧的自然失效但不影响任何东西。

顺带记一个运维坑：`pkill -f "analyzeHeadless"` 会匹配到 ssh 自己那条命令行（自杀，返回 255），
必须写成 `pkill -f "analyzeHead[less]"`；工程锁残留时删
`proj4/bh3fix.lock` 与 `bh3fix.lock~` 即可。

### 9L.3 关键发现：上一轮的布局表本身是错的

写回成功后发现字段名对不上类型宽度：

```c
this->type_param_list = puVar1;                            /* 0x28，8 字节指针，对 */
this->type_param_str = puVar1;                             /* 0x30，8 字节指针，对 */
*(undefined **)&this->min_player_level = _DAT_189b4a238;    /* 0x38，8 字节字符串 ← 但 min_player_level 是 uint */
```

`min_player_level` 是 `uint`（4 字节），却被写进了 8 字节的字符串指针 —— 说明名字整体错位了。

**地面真值：构造函数逐条比对。** `BulletinActivityConfig` 的 `_ctor`（RVA `0x6637860`）实际写的是：

| 偏移 | 宽度 | 值 | 对应字段（按声明顺序） |
|---|---|---|---|
| 0x10 | 8 | 0 | activity_id + activity_type |
| 0x18 | 8 | 0 | begin_time + **end_time** |
| 0x20 | 4 | 0 | **bulletin_id** |
| 0x28 | 8 | new List | mission_ids |
| 0x30 | 8 | new List | type_param_list |
| 0x38 | 8 | string.Empty | type_param_str |
| 0x40 | 8 | 0 | min_player_level + max_player_level |
| 0x48 | 8 | new List | item_list |
| 0x50–0x70 | 8×5 | string.Empty | title_name / title_image / image_path / link_button / description |
| 0x78 | 4 | 0 | weight |
| 0x80, 0x88 | 8×2 | string.Empty | background_path / text_image_path |
| 0x90 | 8 | new List | currency_list |
| 0x98 | 8 | string.Empty | unlock_param_str |
| 0xA0 | — | 未写 | extensionObject |

**22 个字段全部是实例字段，零 static，纯声明顺序对齐打包，一格不差。**

**根因：v3 的求解方式必然漏字段。**

v3 用「观测偏移集合 → 字段记录」做子序列匹配，没观测到的字段一律判成 static 并从偏移序列里剔除。
而观测**必然漏**相邻小字段，因为编译器会合并写：

```asm
mov qword ptr [rax+0x18], 0     ; 一条 8 字节存储，同时清零 begin_time 和 end_time
```

扫描器只记录**访问基址** `0x18`，于是 `end_time`（0x1C）永远不会出现在观测里 →
被判 static → `mission_ids` 从 0x28 前移到 0x20 → 其后所有字段名整体前移。

实测 `/bh3/proto` 下 **44.5%（5,834 / 13,103）的字段被误标 static**，真实情况接近 0。

### 9L.4 新算法：声明顺序对齐打包（`bh3_layout4.py`）

既然 C# 字段在 IL2CPP 里按声明顺序、按自然对齐顺序排列，偏移就是**可确定的**，
根本不需要观测来定位 —— 观测只用来**校验**。

规则：

1. **起点**：类从 `+16` 起（IL2CPP 对象头 `__klass` / `__monitor`），值类型从 `0` 起
2. **逐个打包**：`cur = align(cur, 自然对齐)`，`offset = cur`，`cur += 尺寸`
3. **自然对齐** = 字段自身对齐上限 8（**不是** `min(size,8)`：`Vector3` 12 字节但对齐只有 4）
4. **继承链展平**：基类字段排在前面（Ghidra 结构体没有继承概念，必须拍平）
   - 但**值类型不展平**：`System.ValueType` 只是语义基类，没有任何数据成员。
     踩过坑：把它的字段排到偏移 0 之前，`Vector3` 被撑成 96 字节
5. **值类型排除「不占实例空间」的字段**（元数据没有 static/literal 标志，用两条结构性判据）：
   - 字段类型 == 声明类型自身 → 必然是 `static readonly` 单例
     （`Vector3.zeroVector` / `Quaternion.identity` / `String.Empty`），实例字段不可能自包含
   - 名字形如 `kXxx` 的基元类型 → Unity 惯例的 `public const`（literal，无存储）
   - 比较前要展开 C# 别名：元数据里 `String.Empty` 的类型写作 `string`，声明类型全名是 `System.String`
6. **枚举字段按底层整型宽度落标量**，否则会掉进 pad 分支，反编译里变成
   `pad_60[0..3] = 0` 而不是 `device_type = 0`
7. **conf 分级**（只做校验，不参与定位）：
   - `P` —— 打包覆盖了全部观测偏移
   - `P!` —— 有观测偏移不落在打包边界上（多为观测侧失真，如 `UnityEngine.Bounds`）
   - `P?` —— 该类型没有观测
   conf 会写进 Ghidra 结构体的 description（`bh3 conf=P`），需要时可按它过滤。

另外一个必须记的坑：`bh3_types_v5.txt` **第 8 列不是父类型索引**。
实测 `t6158` 的父类名是 `System.Object`，而该列值是 `1`（指向 `<>f__AnonymousType0\`1`），
按它走继承链会把无关字段继承进来，把整张表偏移推后 8 字节。父类只能按名字反查。

### 9L.5 结果

| 项 | v3（上一轮） | v4（本轮） |
|---|---|---|
| 结构体规格 | 25,375 | **46,149** |
| Ghidra 实际建成 | 24,668 | **42,117** |
| 结构体字段数 | 120,879 | **470,843** |
| `this` 重定型函数 | 118,981（仅试跑 300） | **110,074（全量完成）** |
| proto 字段误标 static | 44.5% | **0（不再判 static）** |

地面真值 9 个类型尺寸：

| 类型 | 期望 | v3 | v4 |
|---|---|---|---|
| UnityEngine.Vector3 | 12 | 12 | **12** |
| UnityEngine.Vector2 | 8 | 8 | **8** |
| UnityEngine.Vector4 | 16 | 16 | **16** |
| UnityEngine.Quaternion | 16 | 16 | **16** |
| UnityEngine.Color | 16 | 16 | **16** |
| UnityEngine.Rect | 16 | 16 | **16** |
| UnityEngine.Matrix4x4 | 64 | 64 | **64** |
| UnityEngine.Bounds | 24 | 24 | **24** |
| System.String | 22 | 22 | 56 ✗ |

`System.String` 是唯一没对上的：`TrimHead` / `TrimTail` / `TrimBoth` /
`charPtrAlignConst` / `alignConst` 都是 `static readonly int`，没有结构性判据能识别，
被当成了实例字段。但 `m_stringLength@0x10`、`m_firstChar@0x14` 是对的，
不影响任何反编译结果（`String` 在代码里只以指针形式出现）。

### 9L.6 已知局限

- **`P!` 的 6,812 个类型**（占 14.8%）打包与观测冲突，真实 static 字段尚未剔除。
  它们仍被写入 Ghidra（因为 `Bounds` 这种「观测冲突但打包正确」的例子说明观测侧更不可靠），
  但名字可信度低于 `P`。
- **`noType=8,689`**：脚本里「依赖结构体没建出来 → 整个类型放弃」的策略会级联失败
  （4,032 个类型被跳过）。这 8,689 个函数仍是 `param_1`。
- **字段名错位问题只在 proto / MoleMole 这类「无 static」的类上被彻底解决**；
  含真实 static 字段的类（`Mono.*`、部分 `UnityEngine.*`）仍需按 `P!` 逐类处理。
- 参数类型（`string fmt, object[] args`）还没重定型，目前只有 `this`。

### 9L.7 复现

```bash
# 1) 纯打包布局（秒级）
python bh3_layout4.py          # → bh3_layout4.tsv

# 2) 生成结构体规格 + this 清单
python gen_structs2.py         # → bh3_structs2.tsv / bh3_this2.tsv

# 3) 传到远端，写回 Ghidra（全量约 15 秒脚本时间 + 程序打开/保存约 90 秒）
scp bh3_structs2.tsv bh3_this2.tsv ApplyTypes.java nas@192.168.0.104:~/re/sym/
~/opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless \
  ~/re/ghidra/proj4 bh3fix -process UserAssembly_fixed.dll -noanalysis \
  -scriptPath ~/re/ghidra/scripts \
  -postScript ApplyTypes.java ~/re/sym/bh3_structs2.tsv ~/re/sym/bh3_this2.tsv \
                ~/re/sym/apply_full4.txt 0 0

# 4) 导出反编译验证
... -postScript DumpDecomp.java ~/re/sym/decomp_final2.c 0x186637860 0x186B07D20
```

工具链：`bh3_layout4.py`（打包布局）/ `gen_structs2.py`（结构体规格）/
`ApplyTypes.java`（Ghidra 侧建结构体 + 重定型）/ `audit_pack.py`（打包 vs 观测偏差审计）。

---

## §9M 参数签名写回（第 6 步）：函数签名彻底对齐 C#

### 9M.1 一句话结果

303,143 个函数的签名从「只有 `this`」补成完整 C# 签名，**271,753 个参数**带上了真实类型与名字：

```c
AreaDataItem * AreaData::GetArea(AreaData *this,int areaId)
void AreaData::AddOnePoint(AreaData *this,PointData *pointData)
void CCAGLJPMIFF::_ctor(CCAGLJPMIFF *this,BaseActor *ONFGPPJOPHI,uint EDHEEBHCKMA,uint CCJMFKHNPGK)
```

对应 C# 声明（函数头注释里本来就有）：

```c
/* C#: AreaDataItem AreaData::GetArea(int areaId)  token=0600EA69 */
/* C#: void AreaData::AddOnePoint(PointData pointData)  token=0600EA67 */
```

### 9M.2 数据来源

| 信息 | 来源 |
|---|---|
| 返回类型 / 参数类型 / 参数名 / 是否 static | `bh3_methods_v2.tsv`（`returnType` / `params` / `flags`） |
| 方法 → RVA | `bh3_method_addr.tsv` 第 4 列 |
| 类型名 → typeIdx → 结构体 | `bh3_types_v5.txt` + `bh3_structs2.tsv` |

`flags` 是**十六进制**字符串，`& 0x10` 即 `MethodAttributes.Static`。
（实测 `ThrowHelper.IfNullAndNullsAreIllegalThenThrow` 的 flags=`0093` → static；
`BulletinActivityConfig::.ctor` 的 flags=`1886` → 非 static。）

### 9M.3 关键设计：值类型必须区分 s / p

MS x64 下：

- **≤8 字节的值类型**走寄存器（RCX/RDX/R8/R9 或 XMM），按值传
- **>8 字节的值类型**走隐藏指针（调用方分配缓冲区）

搞错这一点，整串参数会从出错位置起全部错位。所以 `gen_sigs.py` 把类型编码成：

| kind | 含义 |
|---|---|
| `v` | void |
| `i1 u1 i2 u2 i4 u4 i8 u8 f4 f8` | 定长标量，按真实宽度 |
| `p:<typeIdx>` | 指向该结构体的指针（引用类型 / 数组 / 泛型 / **>8 字节值类型**） |
| `p` | 无结构体的裸指针 |
| `s:<typeIdx>` | **≤8 字节**的小值类型，按值传 |

返回类型同理：`Vector3`（12 字节）编码成 `p:<idx>`，Ghidra 里显示 `Vector3 *` ——
这恰好就是 MS x64 隐藏返回缓冲区的语义，不会让 Ghidra 自己去摊平而错位 `this`。

枚举一律落成 `u4`（枚举字段之前掉进 pad 分支的坑，在 §9L.4 已记过）。

### 9M.4 幂等重建

脚本对每个函数先算期望参数个数 `want = (isStatic ? 0 : 1) + n`：

```java
while (f.getParameterCount() > want) f.removeParameter(f.getParameterCount() - 1);
// 再逐个「就地更新」或「追加」
```

这样重复运行不会叠加参数。注意 `f.removeParameter` 和 §9L.2 的 `dtm.remove`
完全不是一回事：前者只改函数签名，后者会遍历全程序地址。

### 9M.5 参数串解析的两个坑

**(1) 按 `", "` 切分会切坏泛型实参**

```
System.Converter`2<TInput,TOutput> converter
```

`<>` 里的逗号必须跳过。`gen_sigs.py` 用深度计数切分，只在 `depth == 0` 时才断。

**(2) kind 自身带冒号，必须按最后一个冒号切**

参数编码是 `p:6092:KOPNFGMFGBF`。按第一个冒号切会得到
`kind="p"`、`name="6092:KOPNFGMFGBF"`，Ghidra 里就显示成
`pointer 6092:KOPNFGMFGBF`。改成 `lastIndexOf(':')` 才对。
（参数名已被清洗成 `[0-9A-Za-z_]`，不会含冒号，所以这么做是安全的。）

### 9M.6 结果

| 项 | 数值 |
|---|---|
| 生成的签名行 | 303,722 |
| 成功应用 | **303,143** |
| 设置参数槽位 | **271,753** |
| 设置返回类型 | 303,164 |
| 找不到函数（noFn） | 558 |
| 出错 | 21（`Auto-parameter may not be modified` / `DuplicateNameException`，都是个别编译器生成方法） |
| 耗时 | 22 秒 |

参数 kind 分布：`p` 196,137 / `i4` 55,026 / `u4` 33,274 / `u1` 22,572 /
`f4` 12,846 / `s` 3,046 / `u2` 1,592 / `u8` 812 / `i8` 684 / `f8` 555 /
`i2` 443 / `i1` 74。

### 9M.7 顺带修掉的路径 bug

`gen_structs2.py` 的输出前缀从 `/bh3/` 改成 `/bh3v3/` 之后，
`ApplyTypes.java` 里的 `p[1].substring("/bh3".length())` 切出来是 `v3/UnityEngine`，
拼成 `/bh3v5v3/UnityEngine` —— 结构体全建到了错误路径下（脚本自身自洽所以没报错，
但外部脚本按 `/bh3v5/...` 查就一个都找不到，表现为「结构体索引 0 个」）。

修法：`gen_structs2.py` 前缀回到中性的 `/bh3/`，`ApplyTypes` 的 `ROOT2` 升到 `/bh3v6`，
两边都用 `substring("/bh3".length())` 切，路径就是 `/bh3v6/<namespace>`。

### 9M.8 已知局限

- 参数类型靠**名字**映射。泛型实参（`List`1<uint>`）、数组（`T[]`）、
  泛型形参（`T` / `TOutput`）一律降级成指针，没有还原成 `List<uint>*` 这种带实参的形式。
- 声明类型没建出结构体的方法（9,153 个）整行跳过，参数仍是 `param_N`。
- 少数编译器生成方法（闭包 `<>c__DisplayClass`、`b__26_0`）的 `this` 指向闭包类，
  结构体没建出来时显示 `pointer this`。
- **调用点没有跟着改**：Ghidra 不会因为我们改了被调函数的签名就回填所有 caller。
  需要在 Ghidra 里跑一次 "Re-analyze"（或重新反编译），caller 侧才会显示实参类型。

### 9M.9 复现

```bash
python gen_sigs.py                     # → bh3_sigs.tsv
scp bh3_sigs.tsv bh3_structs2.tsv ApplySig.java nas@192.168.0.104:~/re/sym/

~/opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless \
  ~/re/ghidra/proj4 bh3fix -process UserAssembly_fixed.dll -noanalysis \
  -scriptPath ~/re/ghidra/scripts \
  -postScript ApplySig.java ~/re/sym/bh3_sigs.tsv ~/re/sym/bh3_structs2.tsv \
                ~/re/sym/apply_sig_full.txt 0 0
```

工具：`gen_sigs.py`（签名编码）/ `ApplySig.java`（Ghidra 侧应用）。

---

## §9N 结构体覆盖率收口：`st:` 字段规格的分隔符 bug（+50% 字段）

### 9N.1 一句话结果

`ApplyTypes` 一直有 4,032 个类型（占 8.7%）建结构体失败，连带 8,689 个函数拿不到 `this`。
根因是一个**字段规格分隔符冲突**的 bug，不是数据问题。修掉之后：

| 项 | 修前 | 修后 |
|---|---|---|
| Ghidra 建成结构体 | 42,117 | **46,147** |
| 跳过类型 | 4,032 | **2** |
| 结构体字段总数 | 470,843 | **704,396**（+50%） |
| `this` 重定型函数 | 110,074 | **118,756** |
| `noType`（类型没结构体） | 8,689 | **0** |
| 签名应用 | 303,143 | 303,151 |

### 9N.2 根因：`kind` 里带了冒号，把 3 段规格切成 4 段

字段规格的格式是 `off:kind:name`，消费端按 3 段切：

```java
String[] q = spec.split(":", 3);
int off = Integer.parseInt(q[0]);
String kind = q[1];
String arg  = q[2];
```

而内联值类型的 kind 被编码成 `st:<typeIdx>`，于是规格变成 **4 段**：

```
40:st:6158:mission_ids
```

`split(":", 3)` 的结果是 `["40", "st", "6158:mission_ids"]` —— `kind` 只剩 `"st"`，
于是 `kind.startsWith("st:")` 判不中，掉进 `scalar("st")` 返回 `null`，
`bad = true`，**整个类型被丢弃**。

修法：把 kind 里的分隔符换成点号，规格恒定 3 段：

```
40:st.6158:mission_ids
```

消费端改成 `kind.startsWith("st.")`（同时保留 `st:` 分支做兼容）。

### 9N.3 为什么之前一直没发现

因为「丢整个类型」是**静默降级**：跳过的类型不在 `byTypeIdx` 里，
`this` 重定型时只表现为 `noType` 计数增加，反编译看起来仍然「正常」
（只是这些类显示成 `param_1`）。

诊断路径值得记下来：先给脚本加**原因计数**，而不是猜。

```
STRUCTS done: created=42117 skip=4032 ... | why: size=0 off=2 spec=0 len=0 dep=0 scalar=4030 exist=0
```

`scalar=4030` 一眼定位到「`scalar()` 返回了 null」——也就是 kind 没被识别。
用 Python 复现 `off < cur` 只找到 2 个，说明不是数据问题，才敢往分隔符上想。

### 9N.4 顺带修掉的两个降级策略

原来有两处「宁可丢掉整类」的保守写法，一并改成「保住偏移」：

**(1) 依赖结构体缺失时不再丢整类**

```java
// 修前：ft == null → bad = true → 整个类型跳过
// 修后：退化成同长度填充，后续字段偏移完全不受影响，只损失这一个字段的类型
if (ft == null || flen <= 0 || ft.getLength() != flen) {
    sdt.add(new ArrayDataType(new Undefined1DataType(), flen, 1, dtm),
            flen, String.format("pad_%X", off), null);
    cur += flen;
    nPadDep++;
    continue;
}
```

**(2) 布局长度与声明尺寸不一致时不再丢整类**

```java
// 修前：if (cur > size) { nSkip++; continue; }
// 修后：不足补尾填充；超出就按实际布局长度（Ghidra 结构体长度 = 组件长度之和）
if (cur < size) { sdt.add(padArray(size - cur), size - cur, ...); nTrail++; }
```

实测 `trail=8,082` —— 有 8,082 个结构体需要补尾填充，说明之前这些结构体的长度是**偏短**的
（Ghidra 里长度只等于已放组件之和，忽略了声明尺寸）。现在长度也对了。

### 9N.5 验证：嵌套值类型

之前 4,030 个失败类型里大量是「结构体里内联结构体」（`Vector3` 在 `Bounds` 里、
`Bounds` 在组件里）。修完后抽两个函数验证：

```c
/* C#: bool PHBECOIBOFM::DEALPIKAOFF(UnityEngine.Bounds A, UnityEngine.Bounds B)  [static] */
byte MoleMole::PHBECOIBOFM::DEALPIKAOFF(Bounds *GAEJLHPNMEB,Bounds *GEEOBLCDDCP)
{
  ...
  BStack_48.m_Extents.y = (GAEJLHPNMEB->m_Center).x;
  BStack_48.m_Extents.z = (GAEJLHPNMEB->m_Center).y;
  fStack_30 = (GAEJLHPNMEB->m_Center).z;
  fStack_2c = (GAEJLHPNMEB->m_Extents).x;
```

```c
/* C#: bool GeometryUtils::ContainPoint(UnityEngine.Bounds bounds, UnityEngine.Vector3 point, float epsilon) */
byte ContainPoint(Bounds *bounds, Vector3 *point, float epsilon)
```

`Bounds.m_Center` / `Bounds.m_Extents`（各 12 字节的 `Vector3`）被正确解成嵌套字段访问。
`Bounds`(24B) 和 `Vector3`(12B) 都 > 8 字节，按 MS x64 规则以指针传递 —— 与 §9M.3 的
`s:` / `p:` 编码一致。

### 9N.6 已知局限

- 仍跳过 **2 个**类型：`PositionOffset` / `RotationOffset`，字段偏移与前面字段重叠
  （`off < cur`），属于布局推断本身的问题，不是脚本问题。
- `trail=8,082` 说明这 8,082 个结构体的声明尺寸比字段布局长，多出来的是**未被观测到的尾部字段**
  （或真实 static 混入导致的估算偏差）。补的是 `pad`，不影响已有字段偏移。
- `P!` 的 6,812 个类型（§9L.6）真实 static 仍未剔除。

### 9N.7 复现

```bash
python gen_structs2.py                 # 字段规格改用 st.<idx>
scp ApplyTypes.java ApplySig.java bh3_structs2.tsv nas@192.168.0.104:~/re/sym/

~/opt/ghidra_12.1.4_PUBLIC/support/analyzeHeadless \
  ~/re/ghidra/proj4 bh3fix -process UserAssembly_fixed.dll -noanalysis \
  -scriptPath ~/re/ghidra/scripts \
  -postScript ApplyTypes.java ~/re/sym/bh3_structs2.tsv ~/re/sym/bh3_this2.tsv \
                ~/re/sym/apply_full8.txt 0 0 \
  -postScript ApplySig.java   ~/re/sym/bh3_sigs.tsv ~/re/sym/bh3_structs2.tsv \
                ~/re/sym/apply_sig8.txt 0 0
```

两个脚本可以在**同一次 headless 会话**里串起来跑（`-postScript` 可重复），
省掉一次程序打开/保存（约 90 秒）。结构体在同一事务序列里已提交，
`ApplySig` 用同一个 `DataTypeManager` 实例就能查到。

---

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

### 9O.7 三个坑（都实测）

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

### 9O.8 已知局限 / 下一梯队

剩下 762,705 条未命名调用边里，头部 10 个就占 39 万条：

| VA | 入度 | 形态 | 现状 |
|---|---:|---|---|
| `0x18043E4C0` | 103,744 | 134 字节，锁 `0x1899DB6B0` → 调 `0x18043E550` → 失败则带类名抛异常 → 返回 1 | 疑似 `Class::Init` 的另一条入口（用 `+0x13F`/`+0x13D` 标志），**未定名** |
| `0x1803EE250` | 66,537 | thunk → `0x18042CF20`，含 `memcpy(..., slot-0x10)` | 疑似泛型虚方法/值类型 this 适配器，**未定名** |
| `0x1804FE260` | 51,733 | thunk → `0x180436090` = `idx==-1 ? 0 : table[idx]` | 疑似元数据 usage 表查询，**未定名** |
| `0x1804FE040` | 44,931 | thunk → `0x180442320`（接口/类型匹配判断） | **未定名** |
| `0x1804FE070` | 36,024 | 用 `*(*(klass)+0x30)`（类名）拼消息后抛 | 疑似 `RaiseTypeInitializationException`，**未定名** |
| `0x1804FE0E0` | 22,559 | 5 字节 `JMP 0x18044E770` | ~~曾疑为 `unbox`（`obj+0x10`）；dump 汇编后确认目标是 `strlen` + 构造 std::string 的**字符串哈希**，否定~~ → **已更正为 `il2cpp::vm::Object::Unbox`**，见 §9U.5 |

再往下是 `0x1846F7D30`(20,456)、`0x180257840`(13,650)、`0x180261460`(13,318)、
`0x184C69C50`(11,614) 等，已离开 thunk 表，分散在各处，需要逐个看反编译。

**判据纪律**：只收「字符串常量 + 汇编形态 + 调用点上下文」三类硬证据能闭环的。
**宁可不命名，也不贴错名**：错名比 `FUN_` 更有害，因为它会让后续所有推理建立在错误前提上。

以上这段写于 §9O，当时以 `0x1804FE0E0` 为"反例"——**这个例子本身是错的**，已在 §9U.5 更正为 `Object::Unbox`。
错误来自地址抄错一位：真目标是 `0x18044E770`（`lea rax,[rcx+0x10]; ret`），被记成了 `0x180445770`
（`or rax,-1 / inc rax / cmp byte [rcx+rax],0` 的 `strlen` 循环 + 构造 `std::string`）。两个地址只差一个字位，
但一个在 `.text` 前段、一个在后段，函数完全不同。纪律本身仍然成立，教训要加一条：**地址必须由脚本输出，不能手抄**。

### 9O.9 复现

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

## §9Q 嵌套类型归位（第 10 步）：21,429 个嵌套类型回到父类内部

### 9Q.1 一句话结果

上一轮遗留的「嵌套类型未归属父类」已解决。**21,429 个嵌套类型全部归位到 10,390 个父类型内部**，源码树里它们现在写成真正的 C# 嵌套类（缩进递进），而不是和顶层类型平铺。索引覆盖 57,487 = **全部类型，零丢失**。

| 指标 | 之前 | 现在 |
|---|---:|---:|
| 嵌套类型归属 | 0 / 21,429 | **21,429 / 21,429** |
| 索引覆盖类型 | 57,487 | 57,487（零丢失） |
| 生成耗时 | 5.8 s | 6.6 s |
| 产物 | 467 个 .cs / 69 MB | 467 个 .cs / 76 MB |

嵌套深度分布（用缩进宽度数出来的）：

| 层级 | 缩进 | 类型数 |
|---|---:|---:|
| 顶层 | 2 空格 | 36,051 |
| 一层嵌套 | 4 空格 | 21,080 |
| 二层嵌套 | 6 空格 | 328 |
| 三层嵌套 | 8 空格 | 12 |

467 个文件的 `{` / `}` 计数全部平衡，零异常。

### 9Q.2 关键判断：`nestedTypesStart` 其实早就解出来了

`extract_types_full.py` 的注释里已经写着：

```
+0x20  nestedTypesStart   (raw ^ 0x21FE571D - salt)，-1 = 无
+0x46  nested_type_count  u16 (raw ^ 0x7883) - (salt & 0xFFFF)
```

也就是说「每个父类型有 `count` 个嵌套类型、从 `start` 开始」这件事一直是知道的。缺的只是**那段 `TypeDefinitionIndex` 数组本体在文件哪里**。上一轮把它记成「元数据没有 nestedTypes 数组」是误判 —— 表结构里有，只是没去找。

### 9Q.3 先做零成本自洽性检查，再动手找数组

不先找数组，先用 `start` / `count` 两个已有字段互相验证：

```python
# 10390 个父类型，按 start 排序，看是否恰好铺满 [0, 21429)
acc = 0; bad = 0
for r in sorted([r for r in recs if r["cnt"] > 0], key=lambda x: x["start"]):
    if r["start"] != acc: bad += 1
    acc += r["cnt"]
# 结果：bad = 0，acc = 21429 == sum(nestedCount)
```

**零空洞、零重叠、末值恰好等于总和**。这一步没花任何搜索成本，却把「数组是连续段」这个前提钉死了。后面找数组的所有判据都建立在它上面。

同时拿到一个副产品：`nestedCount` 最大 87，`sum = 21,429`，而「namespace 为空的类型」有 22,186 个 —— 差 757，正是真正的顶层无命名空间类型（`<Module>` / `Locale` / `SR` / `<>f__AnonymousType0\`1`）。

### 9Q.4 定位数组：用「元素必须是空 namespace 类型」做判据

ECMA-335 规定 **嵌套类型 TypeDef 的 Namespace 字段必为空**。所以数组里每个元素都必须是那 22,186 个之一。这条判据的随机命中率 ≈ `(22186/57487)^21429`，实际为零。

```python
ok = bytearray(NT+1)
for x in empty_namespace_types: ok[x] = 1

mv = memoryview(BUF)[:(FS//4)*4].cast("I")   # 56 MB 直接映射成 int 数组
for i in range(len(mv) - 21429):
    if not (mv[i] < NT and ok[mv[i]]):            # 预筛：首元素
        continue
    if not (mv[i+21428] < NT and ok[mv[i+21428]]): # 预筛：末元素
        continue
    if all(mv[j] < NT and ok[mv[j]] for j in range(i, i+21429)):
        hit(i)
```

**32 位窗口全库唯一命中一处**：`metadata + 0x1C41FB0`。

16 位窗口会命中一大片连续偏移（`0x1C41FAE` 起 21,431 处），那是同一段数据在 16 位视角下的拆分解读 —— 因为值都 < 57487，高 16 位恒为 0，而 0 号类型 `<Module>` 本身也合法。**看到「16 位命中一大片」不要以为找到很多候选，它只是 32 位结果的影子。**

### 9Q.5 验证：四条独立判据全部通过

```
数组值域 [13, 57478]      唯一值 21429      ← 无重复，且全在 NT 内
namespace 非空的元素   0 个                ← ECMA 约束成立
父段与累加不符        0 处                 ← 零空洞零重叠
空 namespace 未覆盖   757 个               ← 正是真顶层类型
```

抽样对照（都是 .NET / Unity 生态里可外部核对的真结构）：

| 父类型 | 元数据解出的嵌套成员 | 是否符合已知事实 |
|---|---|---|
| `System.Array` | `ArrayEnumerator`、`InternalEnumerator\`1`、`EmptyInternalEnumerator\`1`、`SorterObjectArray`、`SorterGenericArray` | ✅ 与 .NET 一致 |
| `System.Collections.Generic.List\`1` | `Enumerator` | ✅ |
| `Mono.RuntimeStructs` | `RemoteClass`、`MonoClass`、`GenericParamInfo`、`GPtrArray`、`HandleStackMark`、`MonoError` | ✅ 与 index 13–18 完全对应 |
| `Cinemachine.CacheEntry` | `Item`（`Vector3 Pos` @+0x0 / `Quaternion Rot` @+0xC） | ✅ 字段布局也对上 |
| `MiHoYo.SDK.Protobuf.Reflection.*` | `__c`（第三层嵌套） | ✅ 与 protobuf 代码生成器输出形态一致 |

### 9Q.6 生成器改造：递归 + 全局行号

三个改动：

1. **`emit_type(ti, out, depth=0, spans=None)`** —— 缩进由 `depth` 决定（类型 `"  "*(depth+1)`，成员 `"  "*(depth+2)`），在类体末尾递归 emit 子类型。
2. **行号用 `try/finally` 记录** —— 类型有 `delegate` / `enum` 两个提前 `return` 分支，用 `finally` 保证每个类型都记上 `(start, end)`，否则索引会漏。
3. **索引改为全局收集** —— 这是必须的：嵌套类型的 namespace 是空串，而父类型的 namespace 可能非空，两者**不在同一个 `.cs` 文件里**。按命名空间分组时，子类型会被跳过（因为它由父类型递归输出），所以它的行号只能从「父类型所在文件」那边拿。

```python
g_spans = {}          # ti -> (文件名, 起始行, 行数)
for ns in sorted(groups):
    spans = {}
    for ti in tis:
        if ti in g.nest_parent:
            continue                  # 嵌套类型不单独占位，由父类递归带出
        g.emit_type(ti, out, 0, spans)
    for ti, (st, en) in spans.items():
        g_spans[ti] = (fn, st + 1, en - st)   # 嵌套类型也在 spans 里
```

`spans` 由递归层层写入，所以父类和它的所有后代都在同一个 `spans` 字典里，行号天然正确。

**顺带一个便利性质**：因为 `entries` 按 `ti` 升序且 57,487 个类型全在，`TYPES[i]` 恰好就是类型索引 `i` 本身。所以前端拿 `parentIdx` 可以直接 `TYPES[parentIdx]` 取父类型，不需要额外建映射表。

### 9Q.7 三个坑

**① 十六进制抄错 6,848 字节，结果「看起来完全正常」**

扫描脚本输出的是十进制 `29630384`，我手写成 `0x1C43A70`（正确是 `0x1C41FB0`），错位 1,712 个元素。生成出来的东西居然还挺像样：父段累加校验 `bad=0`（这个检查只依赖 typedef 记录，不依赖数组）、抽查也能看到 `<>c__DisplayClass` 之类的名字。

破绽在两处：数组值域 `[1, 220544]` 超出 NT=57,487，以及「重复子类型 671 个」。**凡是数组，一定要打印值域和唯一值个数**，否则错位了也在静默通过。

**② 环境里有 HTTP 代理，`curl 127.0.0.1` 会走代理**

```bash
$ echo $http_proxy
http://127.0.0.1:52668
```

结果：`curl http://127.0.0.1:8765/api/index` 返回的是**代理缓存的旧响应**（6,265,266 B），而磁盘文件已经是 6,603,974 B。排查了半天以为是服务端缓存。正确姿势：

```bash
curl --noproxy '*' http://127.0.0.1:8765/api/index
```

**③ `serve_src.py` 的端口参数是 `--port`，不是位置参数**

`serve_src.py 8765` 会被静默忽略、退回默认 8765 —— 恰好也是 8765，所以看起来「启动成功」，但实际参数没生效。要写 `serve_src.py --port 8765`。

### 9Q.8 已知局限

- **嵌套类型在元数据里只有短名**（`Enumerator`，不带 `Parent.` 前缀）。源码树里靠缩进表达归属，但如果要拼全名做类型引用解析，需要沿 `nest_parent` 链上溯 —— `cs_type()` 目前没做这一步，所以引用一个嵌套类型时可能只显示短名。
- **`parentIdx`（+0x00）与嵌套无关**。它是**基类**索引，而且值域到 351,793（超过 NT=57,487），说明它是 `Il2CppTypeIndex`（含泛型实例化）而不是 `TypeDefinitionIndex`。别把两者混用。
- **重复 token 7,637 个**。这是元数据本身的性质（各程序集 TypeDef token 从 `02000001` 各自编号），不是生成器的 bug。要唯一定位类型只能用 `ti` 索引。

### 9Q.9 复现

```bash
# 1) 找数组位置（56 MB 全库扫，约 30 秒）
python find_nested_arr.py
#   → 32 位唯一命中 0x1C41FB0

# 2) 解出父子关系 + 四条判据验证
python gen_nested.py
#   → bh3_nested.tsv  (childIdx / parentIdx / childName / parentName / ns)

# 3) 重新生成源码树（嵌套自动归位）
python gen_cs.py --out src --bodies bodies.tsv

# 4) 浏览（注意 --port 和 --noproxy）
python serve_src.py --port 8765
curl --noproxy '*' http://127.0.0.1:8765/api/index
```

新增工具：`scan_typedef.py`（用已知列反查字段偏移）/ `scan_nested.py`（按结构性质找索引字段）/
`find_nested_arr.py`（定位数组）/ `gen_nested.py`（生成父子表）。

---

## §9R 反编译体导出双机并行（第 11 步）：单机 3 倍机器的加入

### 9R.1 一句话结果

新增一台 8 核机器 `192.168.0.105`，与原有 3 核 `192.168.0.104` **两头夹**分工：
104 从地址表头部往后、105 从尾部往前，中间缺口由 `dual_prog.py --handoff` 自动接力。
合拢速度从 **12.5 个/秒 → 79 个/秒**，全量 311,382 个地址的 ETA 从 **6.7 小时压到约 1 小时**。

### 9R.2 两台机器的真实差距

| | 104 | 105 |
|---|---|---|
| CPU | Xeon E-2124 @3.3 GHz | **Ultra 5 230F（Arrow Lake）** |
| 逻辑核 | **3** | **8** |
| 内存 | 6.3 G | 7.3 G |
| 磁盘 | 29 G，剩 8 G | 29 G，剩 18 G |
| Ghidra | 12.1.4 | 12.1.4（**已装好**）|
| JDK | 21 | 21 |
| 实测速率 | 19.8 个/秒 | **59.4 个/秒** |

**105 单机就是 104 的 3 倍**。反编译本身是单线程的（瓶颈是 DecompInterface），
所以这个差距来自单核性能 + 函数复杂度，而不是核数——但 105 顺带还有 10 G 余量磁盘，
这点很重要：104 只剩 8 G，装不下第二份 6.1 G 工程。

### 9R.3 工程传输：104 → 105 内网直传，不经本地

本来打算从本地中转，实测内网 300 MB / 2.88 秒 ≈ **104 MB/s（千兆线速）**，
于是改成 104 直接推给 105，6.1 G 只要 **60 秒**，本地完全不参与。

```bash
# 1) 104 原本只有 authorized_keys，没有自己的密钥对
ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519      # 在 104 上
# 2) 把 104 的公钥追加到 105（借本地 paramiko 中转一次）
# 3) 单流 tar 推过去
cd ~/re/ghidra && tar -cf - --exclude='bh3fix.lock*' proj4 scripts \
  | ssh nas@192.168.0.105 'tar -C ~/re/ghidra -xf -'
```

三个要点：

1. **必须排除锁文件**。104 正在跑 headless，`proj4/` 里有 `bh3fix.lock` 和 `bh3fix.lock~`；
   带过去 Ghidra 会认为工程被占用而拒绝加载。
2. **不用 rsync**。工程只有 12 个文件（6.1 G 几乎全在 `bh3fix.rep` 里），
   文件数少到让 rsync 的增量优势归零，tar 单流更省事。
3. **复制正在使用的工程是安全的**，前提是当前任务只读。
   `DumpBodies.java` 加 `-noanalysis` 且只调 `decompileFunction`，不写数据库，
   所以快照一致；105 侧启动后 12 秒就正常出 PROGRESS，反证快照可用。

### 9R.4 分工：两头夹 + 覆盖区间可以直接算

```
104:  body_list.txt[0] ──────────────→ 索引增大
105:  body_list.txt[311381] ─────────→ 索引减小

覆盖 = [0, n104) ∪ [TOTAL - n105, TOTAL)
缺口 = [n104, TOTAL - n105)
```

**关键便利**：只要读两边 PROGRESS 里的 `n`，缺口就能算出来，**不需要下载任何 tsv**。
105 的输入列表就是 `uniq[155691:][::-1]`（155,691 条倒序），
`uniq` 是 `body_list.txt` 去重保序后的 311,382 条 —— 实测**零重复**，所以无需去重，
但保留去重步骤可以对冲以后重新生成列表时的风险。

### 9R.5 接力不需要任何新代码

`DumpBodies.java` 开头就把 `outPath` 里已有的 VA 读进 `done` 集合、`todo` 里跳过：

```java
Set<Long> done = new HashSet<>();
if (of.exists()) { ... done.add(Long.parseLong(ln.substring(0, t), 16)); ... }
...
if (!done.contains(va)) todo.add(va);
```

所以**接力只需换 `listFile` 重启**，`bodies_b.tsv` 会持续累积、天然去重。
`dual_prog.py --handoff` 做的正是这件事：切出 `[n104, TOTAL-n105)` 倒序 → 上传 → 重启 105。

### 9R.6 两个坑

**坑一：日志和 tsv 都在缓冲里，谁先谁后不确定。**

观察到同一时刻 `tsv 44,400 行` 而日志 `n = 44,058` —— tsv 反而更多。
两者都是块缓冲（`PrintWriter(BufferedWriter(..., 1<<22))` + stdout 重定向到文件），
互相领先。覆盖量必须取 `max(PROGRESS 的 n, tsv 行数)`，只信一个会把缺口算歪。
接力的第二轮尤其要注意：`>` 会把 105 的日志清空，`n` 从 0 重来，
只有 tsv 行数是跨轮累计的 —— 这也是必须取 max 的原因。

**坑二：相邻两条 PROGRESS 反推速率不可靠。**

PROGRESS 每 500 条打一次，两条只差 500 个样本，短间隔下噪声极大：
同一台机器先后读出过 **9.4 / 148.8 / 186.2** 三个值。
改成跨进程 wallclock 采样（状态落盘 `_dump/dual_state.json`，`dt ≥ 45 秒` 才更新），
才拿到稳定的 **19.8 / 59.4**。上一轮 `prog_bodies.py` 用的「两次 PROGRESS 相减」法
在有 500 条固定间隔的情况下同样受此影响，只是当时恰好落在长间隔上没暴露。

### 9R.7 新增工具

| 文件 | 作用 |
|---|---|
| `rsh2.py` | 双机 SSH 统一入口：`conn(104/105)` / `sh()` / `put()` / `get()`，两台都走密钥 |
| `xfer_105.py` | 104 → 105 传工程 + 自动校验（大小 / 文件数 / 磁盘）|
| `dual_prog.py` | 双机监控 + 自动接力。`-w 120 --handoff` 起守护，105 空闲即派发下一批 |

### 9R.8 已知局限

- **接力有 4 分钟固定开销**：每轮重启都要重新加载 6.1 G 工程。所以宁可一次派大段，
  不要频繁小额派发。
- **104 不会自动停**：它跑到与 105 汇合后会继续往前跑（做的是 105 已完成的部分）。
  结果正确（合并时按 VA 去重），只是白烧机器时间。要精确停在切分点需要给
  `DumpBodies` 传 `maxCount` 重启，代价是丢 4 分钟加载 + 最多 500 条缓冲，暂不划算。
- **两台都在用 `GHIDRA_HEADLESS_MAXMEM=3G`**：105 只有 7.3 G 物理内存，3 G 堆 + 页缓存刚好。

### 9R.9 复现

```bash
# 环境勘察（装了 Ghidra？磁盘够吗？）
python probe_105.py

# 传工程（104 → 105，60 秒）
python xfer_105.py

# 切尾段倒序列表并开局
python -c "...uniq[155691:][::-1]..."   # 见 9R.4
scp _dump/body_list_tail_rev.txt nas@192.168.0.105:~/re/sym/

# 双机监控（一次）
python dual_prog.py
# 守护 + 自动接力
python dual_prog.py -w 120 --handoff

# 全部覆盖后合并
cat bodies_a.tsv bodies_b.tsv | sort -u > bodies_merged.tsv
python gen_cs.py --out src --bodies bodies_merged.tsv
```

---

## §9S 反编译体收口（第 12 步）：97.5% 方法填入真实函数体

### 9S.1 一句话结果

两台机器的导出全部完成，**311,382 个地址覆盖率 100%**；合并去重后 **311,317 条唯一函数体**，
源码树里 **398,251 / 408,458 个方法（97.5%）拿到了真实反编译体**，产物 **467 个 `.cs` / 1.16 GB**。

97.5% 不是实现缺陷，而是**地址表的上限**：`bh3_method_addr.tsv` 能给原生地址的方法只有
**398,316 个（97.52%）**，剩下 10,142 个属于外部程序集/无原生体。合并后实际填入 398,251 个，
差额 65 个正是两边反编译失败（`empty`）的地址：104 有 58 个、105 有 7 个。

### 9S.2 双机实际耗时

| | 104 | 105 |
|---|---|---|
| 角色 | 头部正向 | 尾部倒序 + 两轮接力 |
| 完成量 | 134,400 条 | 201,475 条（155,684 + 45,791）|
| 用时 | 约 2.5 小时 | 49 分钟 + 16 分钟 |

单机 104 的原始估算要 **24 小时**（按 3.36 个/秒的谷值），实际双机 **约 3 小时**收口。
其中 105 贡献了 **56%** 的量。

### 9S.3 合并：不能把 905 MB 装进字典

两次导出合计 1.0 GB / 332,875 行，唯一化后 905 MB / 311,317 条。
`{va: body}` 字典要 1 GB 以上内存，而本机可用只有 **944 MB**
（`kryptex_krig-miner` 常驻吃 8.1 GB / 总 16 GB）——直接换页。

改成两趟流式：

```
Pass 1  扫 104：记 VA 集合 + 每行字节偏移，同时原样写出
Pass 2  扫 105：VA 不在集合里就追加；在集合里就抽样回读 104 对应行比对
```

内存只剩 VA 集合（13 万个短字符串）+ 偏移表，约 **30 MB**，全程 12 秒。

**抽样校验结果**：重叠 24,558 条，抽 200 条逐字节比对，**全部一致** ——
证明 105 用的工程快照与 104 同源，反编译结果可以放心混用（这是复制运行中工程时最该验的一件事）。

### 9S.4 源码树生成：改成磁盘索引视图

`gen_cs.py` 原来把 bodies 读成 `{rva: text}`。905 MB 进去就是 1 GB 内存，同样撞墙。
新增 `BodyStore`：

```python
class BodyStore(object):
    """只把 (rva → 行首字节偏移) 放内存，函数体按需 seek 读。索引约 30 MB。"""
    def __contains__(self, rva): return rva in self.idx
    def get(self, rva, default=None):
        off = self.idx.get(rva)
        if off is None: return default
        if self._f is None: self._f = io.open(self.path, "rb")
        self._f.seek(off)
        ln = self._f.readline()
        ...
```

对调用方完全透明（`in` / `.get()` / `[]` 都支持），调用点一行没改。
实测生成 **467 个文件只用了十几秒**，索引构建 + 311k 次随机读都吃得住页缓存。

### 9S.5 坑：sftp 的路径不展开 `~`

`merge_bodies.py` 第一版用 `~/re/sym/bodies.tsv` 走 sftp → `FileNotFoundError`。
`exec_command` 会走 shell 所以 `~` 有效，`sftp` 不走 shell，必须绝对路径。

### 9S.6 坑：`overall.py` 的方法还原率算出 102.5%

覆盖区间是 `[0, n104) ∪ [TOTAL-n105, TOTAL)`，两台跑过汇合点后会重叠，
直接把两段相加会把重叠地址的方法算两遍。
必须**按列表下标取并集**再求和：

```python
idx = set(range(min(n104, TOTAL)))
idx.update(range(max(0, TOTAL - n105), TOTAL))
```

### 9S.7 最终产物

| 指标 | 值 |
|---|---|
| 地址覆盖 | **311,382 / 311,382（100%）** |
| 唯一函数体 | 311,317 条（缺 65 条 = 反编译失败项）|
| 方法填入率 | **398,251 / 408,458（97.5%）** |
| 源码树 | **467 个 `.cs` / 1.16 GB** |
| 类型 / 方法 / 命名空间 | 57,487 / 408,458 / 468 |
| 嵌套类型 | 21,429 个已归位（10,390 个父类）|

生成的代码是「C# 签名 + 原生反编译体」的混合体，例如：

```csharp
// 060315B1 @ 0x181800660
// 共享体：1 个 C# 方法共用此地址，Ghidra 代表函数 _ctor
public ChapterArkOverrideAvatarDataItem(int avatarID, int level, int star, int subStar)
{

  AvatarMetaData *pAVar1;
  undefined8 unaff_RDI;

  if (*(int *)(_DAT_189a159f0 + 0xe8) == 0) {
    il2cpp::codegen::runtime_class_init();
  }
  *(undefined4 *)((longlong)&this->upgradeCostItem + 4) = 0
```

方法名、参数名、参数类型、`this` 的字段名都是还原出来的，只有函数体保持反编译形态。

### 9S.8 复现

```bash
python merge_bodies.py --keep     # 拉两台 tsv → 流式去重合并 + 抽样校验（12 秒）
python gen_cs.py --out src --bodies bodies_merged.tsv    # 生成 467 个 .cs
python overall.py                 # 复核 A/B/C 三个指标
```

---

## §9T 布局重修（v6）：static 真值取代命名猜测

### 9T.1 为什么必须重修

v5 把「哪些字段是 static」交给命名启发式（`MaxXxx` / `Mask$` / 全大写 / `s_` 前缀 /
自引用单例）。这套东西在值类型上勉强够用，在 class 上直接崩：

| 判据 | 实测 |
|---|---|
| 「全大写 + 下划线 = const」 | 精确率仅 **50.7%**：`BTN_CLOSE` / `TEXT_TITLE` 既用于 static 也用于 `[SerializeField]` 实例字段 |
| Mihoyo 的混淆名 | `LIEMIEBBCBO`(1888 命中) / `LKLNGJIAFKG`(1758) / `PFCFININFLF`(1626) 全是**真实例字段**，与 ALL_CAPS 正面撞车 |
| 「自引用类型 = 单例」 | 不成立，`parent` / `owner` 就是自引用实例字段 |
| 全局套用激进变体，观测裁决 | 严格胜出 106 / 打平 30,793 / **严格落败 428** |

结论：**判据来源错了**。static 与否是元数据里的硬属性，不该用命名去猜。

### 9T.2 真值在哪

`extract_fields.py` 已定位字段表 `F0 + fi*12` 与 Il2CppType 指针表。字段记录只有
`{A, typeIdx, nameId}` 12 字节，确实**不含** static 标志 —— 旧文档的这句话是对的，
但它下面的推论「所以只能靠 .cctor 反推」是错的：标志在 Il2CppType 里。

```c
struct Il2CppType {
  uint64 data;      // +0x00  类索引 / 数组 / 泛型 / 指针目标
  uint16 attrs;     // +0x08  ★ FieldAttributes
  uint8  type;      // +0x0A
  uint8  num_mods;  // +0x0B  | byref | pinned
};
```

取法（`field_flags.py`）：`tidx = (b - prf(fi) - 0xF2A3D7F) & M32` → 指针表 → `va2off` → `+0x08`。

```c
FIELD_ATTRIBUTE_STATIC  = 0x0010
FIELD_ATTRIBUTE_INITONLY= 0x0020
FIELD_ATTRIBUTE_LITERAL = 0x0040
```

覆盖 **419,568 / 419,568（100%）**。全工程 **static 229,452（54.7%）、literal 207,021（49.3%）**
—— 也就是说 v5 的布局里长期塞着超过一半不该占实例空间的字段，这才是 class 侧常年修不动的根因。

字段级抽验 12 条全中，其中两条是命名法的死穴：

```
UnityEngine.Object.OffsetOfInstanceIDInCPlusPlusObject   attrs=0x0013  STATIC   ← 名字不像常量
UnityEngine.UI.Selectable.s_List                         attrs=0x0011  STATIC   ← 前缀像实例
```

### 9T.3 教科书样本：CancellationTokenSource

元数据把 static 与实例字段**交错声明**，去掉 static 后的相对顺序就是内存顺序。
观测偏移 `0x10/0x18/0x20/0x24/0x28/0x30/0x38/0x40`：

| v5 布局 | v6 布局 |
|---|---|
| `_staticSource_Set`@0x10、`_staticSource_NotCancelable`@0x18、`s_nLists`@0x20、`CANNOT_BE_CANCELED`@0x38… | `m_kernelEvent`@0x10、`m_registeredCallbacksLists`@0x18、`m_state`@0x20、`m_threadIDExecutingCallbacks`@0x24、`m_disposed`@0x28、`m_linkingRegistrations`@0x30、`m_executingCallback`@0x38、`m_timer`@0x40 |

**v6 8/8 全中**，与 .NET 公开实现逐字段一致。

### 9T.4 口径修正：只有「字段间空隙」算错

旧 `real_miss` 把三类观测都算成错误，实际只有第三类可操作：

| 类别 | 含义 | v6 计数 | 为什么不算错 |
|---|---|---|---|
| `inside` | 落在字段字节内但非合法内部偏移 | 836 | `proto.ClientMail` 每个 8 字节引用字段后都有 `+4` 观测；`0x14` 不是 8 对齐，物理上不可能是引用字段起点，而该类型 `fieldCount=15` 与元数据完全一致 |
| `beyond` | 超出最后一个字段的真实结尾 | 2,771 | **57,487 / 57,487 个类型的声明 fieldCount 全部等于字段表行数** ⇒ 没有漏放的字段 |
| `hole` | 落在两个字段之间 | **380**（§9V 观测去污后；污染前 409） | ★唯一致命，计入 `P!` |

（本表数字已按 §9V 的干净观测更新；§9T 原文基于污染观测，保留历史。）

### 9T.5 v6 一度「看起来更差」，是 v5 在偷分

`compare56.py` 最初给出 v6 落空数 +73.1%。逐条归因（`diag_decomp.py`）后：
新增的 1,673 个落空里 **1,472 个（88%）属于「v5 在那个偏移有字段起点，而 v6 判定该字段是 static」**。

再往下查那 193 个「v5 更好」的类型，**123 个**塞的是同一个字段：

```
OffsetOfInstanceIDInCPlusPlusObject   attrs=0x0013  STATIC
```

它是 `UnityEngine.Object` 的静态常量。v5 把它当实例字段排进布局，等于给**整个
UnityEngine.Object 继承体系**系统性多加 8 字节；而它恰好落在对齐空隙里，就顺手
「覆盖」掉了一个观测偏移。**这种零落空是靠错误换来的。**

`UnityEngine.Object` 的真实布局只有一个字段 `m_CachedPtr`@0x10，观测也只有 `0x10`，
尺寸 0x18 —— v6 完全正确。

### 9T.6 顺带修掉：泛型结构体实例化

`System.Nullable\`1<uint>` 之前被当成 8 字节引用。它实际是
`{bool hasValue; T value;}`，尺寸 8 但**对齐 4**。后果：

```
proto.Mission   _begin_time(Nullable<uint>)
  v5/v6(修前): 0x20        ← 按 8 对齐
  真实:        0x1c        ← 按 4 对齐，其后所有字段整体前移 4 字节
```

泛型定义的字段类型写成 `!176` 这种全局参数编号，同一定义内按出现顺序互不相同，
因此按「首次出现顺序 → 实参顺序」建替换表即可（`pack_generic`）。

影响 **389 个字段**：`Nullable<T>` 248、`StyleValue\`1` 54、`KeyValuePair\`2` 6 …
修复后 `hole` 479→409、`P!` 408→366。

### 9T.7 结果与产物

| 指标 | 数值 |
|---|---|
| 有观测类型 | 32,832 |
| P（无冲突） | 32,492 / **98.97%** |
| P!（有空隙） | 340 / 1.03% |
| P?（无观测） | 8,176 |
| 实例字段 | 539,732 |
| static / literal | 14,117 |
| 已知结构体尺寸 | 20 符合 / 2 不符（见下） |
| attrs 抽验 | 12 / 12 |

两条尺寸不符都是**规范值本身需要核实**，不是算错：

* `UnityEngine.Keyframe` 本版只有 `time/value/inTangent/outTangent` 四个字段，
  算出 16；规范 20 是含 `inWeight/outWeight` 的旧版本
* `UnityEngine.Color32` 元数据是 `rgba:int` + `r/g/b/a:byte` 的显式联合，
  按声明顺序算得 8；实际 4（C# 侧靠 `StructLayout` 覆盖）

产物：`bh3_layout6.tsv`（553,849 行）、`bh3_instsize.tsv`（41,014 行）、
`bh3_layout_report.txt`。下游 `gen_structs2.py` / `gen_cs.py` 已从 v4 改指 v6，
重新生成 **468 个 `.cs`**。

### 9T.8 剩余 366 个真错的形态

观测偏移**恰好落在某个 4 字节字段的结束处**、即 8 字节对齐的空隙里（274/409）。
两种解释无法从偏移分布区分：

* 该 4 字节槽其实还有第二个 4 字节字段（但 fieldCount 已排满，排除）
* 编译器把字段与 padding 一起做了 64 位存储，Ghidra 把高半折成 `+4` 偏移

要定案只能回到指令级核对。这是当前布局还原的精度上限，不是算法缺陷。

### 9T.9 复现

```bash
python field_flags.py --dump      # 导出 bh3_field_flags.tsv（419,568 行）
python bh3_layout6.py             # 布局 + 自检
python gen_layout_report.py       # 质量报告
python gen_structs2.py            # Ghidra 结构体规格（读 v6）
python gen_cs.py --out src --bodies bodies_merged.tsv
```

---

## §9U 六个未命名热点的定名（第 13 步）：本地反汇编 + 两张名字表

### 9U.1 一句话结果

§9O 留下 6 个头部未命名热点。本轮全部定名，**且全部是 il2cpp 运行时 / codegen helper，一个 C# 方法都没有**——
这正是 `bodies_merged.tsv`（只收元数据里有 C# 方法的函数）对它们命中 0/6 的原因。

| VA | 引用数 | 定名 | 等级 |
|---|---:|---|---|
| `0x18043E4C0` | 103,746 | `il2cpp::vm::Class::Init`（带锁入口；工作体 `0x18043E550`） | **S** |
| `0x1803EE250` → `0x18042CF20` | 66,537 | `il2cpp::vm::Object::Box` | **A** |
| `0x1804FE260` → `0x180436090` | 51,733 | `il2cpp::vm::MetadataCache::GetTypeInfoFromTypeIndex` | **B** |
| `0x1804FE040` → `0x180442320` | 44,931 | `il2cpp::vm::Object::IsInst`（返回对象或 NULL） | **A** |
| `0x1804FE070` | 36,026 | `il2cpp::vm::Exception::RaiseInvalidCastException`（`noreturn`） | **S** |
| `0x1804FE0E0` → `0x18044E770` | 22,559 | `il2cpp::vm::Object::Unbox` | **S** |

等级沿用 §9O：S = 汇编形态 + 字符串常量 + 调用点三者闭环；A = 汇编形态决定语义、名字取 il2cpp 规范名；B = 语义唯一，规范名有多个候选。

顺带定名的还有 3 个用得极广的配角：`0x18043E550` = `Class::InitInternal`、`0x1804F0FB0` = `Exception::FormatInvalidCastException`、
`0x1804FF8E0` = `il2cpp.codegen::Eh::throw_cpp_exception`。回写 Ghidra 后 `ApplyRt ok=12 miss=2`（两个 `NOTFOUND` 是 `0x1803F4990`
与 `0x1803F72C0`，它们在工程里不是函数起点，只是桩，见 9U.2 末尾）。

### 9U.2 方法：这一步本来就不需要等 Ghidra

上一轮的思路是"现场反编译"。但反编译的目的是**看清它调了谁**，而 call 目标本身就有两张现成的名字表：

| 表 | 规模 | 作用 |
|---|---:|---|
| `bh3_method_addr.tsv` | 408,459 行，其中 **398,316** 行有 rva（去重后 311,382 个 VA） | call 目标 → `Namespace.Type::Method` |
| PE 导入表 | **215** 个 IAT 槽 / 8 个模块 | `call qword ptr [rip+X]` → `KERNEL32.dll!EnterCriticalSection` |

二进制本来就在本地（`UserAssembly_slim.dll`，190,867,608 字节），capstone 5.0.7 已在隔离 venv 里，
于是 `probe_hot_local.py` 一端口完成：跟 `E9` 桩链 → capstone 反汇编 → 给每条 `call` 贴名字 → 顺手抽 `lea rip+X` 指向的字符串。

结果比 Ghidra 的 C 更直白。比如 `0x1804FE070` 在本地输出里就是三行：

```
rdx = [obj->klass + 0x30]      ; 取源类型
call FormatInvalidCastException
call Exception::FromNameMsg("System", "InvalidCastException", msg)
raise                          ; 后面 15 个 int3
```

**踩到的坑**：PE 数据目录下标算错。我写成 `opt + 112` 就去读——那是 **Export** 表，不是 Import（Import 是 index 1，要 `opt + 112 + 8`）。
错版把 110,225 个垃圾槽当成导入，模块名一律显示 `DllCanUnloadNow`。修正后是 215 个槽 / 8 个模块，`KERNEL32 / WS2_32 / OLEAUT32 / ole32 / ADVAPI32 / IPHLPAPI / SHELL32 / USER32`，一眼就对了。

另外本地还顺手证明了 `0x1803F4990` / `0x1803F72C0` 的真身：`mov rcx,[rcx]; jmp EnterCriticalSection` 与 `...LeaveCriticalSection`——
就是锁的进入/离开，所以它们在 Ghidra 里不是独立函数，`ApplyRt` 报 `NOTFOUND` 属于预期。

### 9U.3 六条证据链

**① `0x18043E4C0` = `Class::Init`（S）**

```
cmp byte [klass+0x13f], 0        ; initialized?
jne skip
mov [rsp+0x40], <全局锁对象>
call 0x1803F4990                 ; Lock::Enter（EnterCriticalSection）
call 0x18043E550                 ; 工作体
call 0x1803F72C0                 ; Lock::Exit（LeaveCriticalSection）
skip:
cmp byte [klass+0x13d], 0
je ret1                          ; 没失败 → return true
... raise ...                    ; 失败 → 抛（走 Eh::throw_cpp_exception）
ret1: mov al,1; ret
```

工作体 `0x18043E550` 一开口也是 `cmp byte [rcx+0x13f],0`，失败时 `mov byte [rdi+0x13d],1`，并且拼串：

```
"Could not load type '" + [klass+0x20] + "." + [klass+0xa8]
                      + "' because generic types cannot have explicit layout."
```

字符串 `"TypeLoadException"` 同在本函数体内。`0x13f` / `0x13d` 一个是"已初始化"、一个是"初始化失败"，
外层只在 `0x13d != 0` 时才抛 —— 这是 il2cpp `Class::Init` 的标准两层结构（锁在外层，实活在内层），S 级。

**② `0x1803EE250` → `0x18042CF20` = `Object::Box`（A）**

```
if ([klass+0x142] == 0) return *data;          // 引用类型：槽里本来就是对象指针
obj = il2cpp::vm::Object::New(klass);          // Ghidra 早已识别这个符号
memcpy(obj + 0x10, data, klass->instance_size - 0x10);
return obj;
```

`[klass+0x114]` 是 `instance_size`，`-0x10` 扣掉对象头 —— 与 ⑥ 的 `Unbox = obj + 0x10` 严格互逆，两边一夹就锁死了。
`+0x142` 因此是 `valuetype`。中间那段 `[klass+0xc0] != 0 && [klass+0x6a] ∈ {0x13, 0x1e}` 是泛型参数（`VAR` / `MVAR`）的约束特化分支。

**③ `0x1804FE260` → `0x180436090` = `MetadataCache::GetTypeInfoFromTypeIndex`（B）**

```
cmp ecx, -1
jne  +
xor eax, eax
ret                        ; index == -1 → NULL
+ : mov rax, [全局表]
    movsxd rcx, ecx
    mov rax, [rax + rcx*8]
    ret
```

`-1` 哨兵 + 扁平指针表 + 有符号 32 位下标，就是 `TypeIndex` 的形状。同族的懒加载版是 `0x18043B320`：同一张表、同一个 `-1` 哨兵，
但表项为空时加锁再调 `0x180430980(idx)` 填充 —— 有懒/非懒一对，说明这是元数据缓存而非普通数组。
规范名在 `GetTypeInfoFromTypeIndex` / `GetTypeInfoFromTypeDefinitionIndex` 之间无法从形态区分，故记 B。

**④ `0x1804FE040` → `0x180442320` = `Object::IsInst`（A）**

```
if (obj == NULL) return NULL;
if (Class::IsAssignableFrom(target, obj->klass)) return obj;      // 0x180441540，本身又走一遍 Init 的加锁
if ([obj->klass+0x141] == 0) return NULL;
if (([target+0x10c] & 0x20) || [target+0x6a] == 0x13 || [target+0x6a] == 0x1e)   // 接口 / VAR / MVAR
    if ([target+0x48] && [target+0x48]->[0x28] && GenericCheck(obj)) return obj;  // 0x180417700
if (target == <某个类单例>) return obj;
return NULL;
```

返回"对象或 NULL"而不是 bool，这是 `IsInst` 区别于 `IsAssignableFrom` 的签名特征；`0x13`/`0x1e` 恰是 `Il2CppTypeEnum` 的
`VAR`/`MVAR`，所以那段是泛型参数的接口约束检查。

**⑤ `0x1804FE070` = `Exception::RaiseInvalidCastException`（S）**

`0x1804F0FB0` 把它拼死了：

```
"Unable to cast object of type '" + [type+0xa8] + "' to type '" + [type+0xa8] + "'."
```

这正是 il2cpp `FormatInvalidCastException` 的原文。随后 `0x180436920` 是一段 4 行小桩：

```
mov r9, rcx                      ; msg
lea r8, "InvalidCastException"
lea rdx, "System"
mov rcx, [缓存 image]
jmp Exception::FromNameMsg
```

再 `Exception::Raise` → `RaiseException` + `int3`。已标 `noreturn`，反编译不再吐 `swi(3)` 死代码。

**⑥ `0x1804FE0E0` → `0x18044E770` = `Object::Unbox`（S）**

整条函数体两个字节组：`48 8D 41 10 C3` = `lea rax,[rcx+0x10]; ret`。
调用点 `0x18025EFA0` 佐证：类型句柄相等时 `return param_1 + 0x10`，不等则跳 `0x1804FE070` 抛 InvalidCast。

### 9U.4 附带收获：`Il2CppClass` 字段偏移

从 `0x18043E550` 与 `Object::Box` 里可以直接读出这些偏移（本二进制版本）：

| 偏移 | 字段 | 依据 |
|---:|---|---|
| `0x20` | `namesp` | TypeLoadException 拼串的第一段，可空 |
| `0x6a` | `byval_arg.type`（`Il2CppTypeEnum`） | 与 `0x13`/`0x1e` 比较 |
| `0xa8` | `name` | InvalidCast / TypeLoad 两处拼串共用 |
| `0xc0` | `generic_class` | 非空且 `flags & 0x10` 才走"泛型不能显式布局"分支 |
| `0x10c` | `flags` | `& 0x20` = 接口，`& 0x10` = 显式布局 |
| `0x114` | `instance_size` | `Box` 的 `memcpy` 长度 + `IsInst` 的 `-0x10` 补偿 |
| `0x13d` | `init_failed` | 工作体置 1，外层据此抛 |
| `0x13f` | `initialized` | 两层的 guard 都是它 |
| `0x142` | `valuetype` | `Box` 的分水岭 |

这批偏移可以直接用来交叉校验布局重修（§9T）：它们是 **il2cpp 自己的 C++ 结构**，不在 41,014 个 C# 类型里，所以不冲突，但能解释为什么 `dump_attrs.py` 里某些
"观测落在字段外"的现象集中在运行时类上。

### 9U.5 推翻 §9J.7 的一条旧结论

旧文档写：`0x1804FE0E0` "dump 汇编后确认目标是字符串哈希，已否定"。**这条是错的。**
目标 `0x18044E770` 的完整函数体就是 `lea rax,[rcx+0x10]; ret`，三条独立证据（指令序列、与 `Box` 的 `memcpy` 目标互逆、调用点 `param_1+2`）指向 `Object::Unbox`。
旧结论应当是跟跳时落到了相邻函数（`0x18044E770` 在 Ghidra 里被并入 `FUN_18025efa0`，其函数体里确实有哈希风格的循环，很容易误读）。

### 9U.6 坑：TSV 带 UTF-8 BOM，Java 端静默吃掉第一行

第一次回写时报告是 `ok=12 miss=2`，但 `0x18043E4C0`（引用数最大的那个）**既没改名也没出现在报告里**。
`ApplyRt.java` 的读取循环有两处静默 `continue`：

```java
if (p.length < 5) continue;
try { va = Long.parseLong(p[0].trim().replace("0x",""), 16); }
catch (Exception e) { continue; }        // ← BOM 走这里
```

本地写出的 TSV 头三个字节是 `EF BB BF`，于是第一行的 `p[0]` 实际是 `"\uFEFF0x18043E4C0"`，`parseLong` 抛异常，
被 `catch` 吞掉，连报告行都不写。**症状就是"行数比输入少 1，且缺的总是第一行"**。
剥掉 BOM 重跑即 `ok=13 miss=2`。所有喂给 Ghidra Java 脚本的 TSV 都要先过一遍这个检查。

### 9U.7 回写后的效果

`ApplyRt ok=13 miss=2` 之后再反编译，两处最能看出差别：

```c
undefined1 il2cpp::vm::Class::Init(longlong param_1, ...)
{
  if (*(char *)(param_1 + 0x13f) == '\0') {
    auStackX_8[0] = 0x1899db6b0;
    func_0x0001803f4990();                  // Lock::Enter
    InitInternal(param_1, auStackX_8);      // ← 原来是 FUN_18043e550
    func_0x0001803f72c0(auStackX_8[0]);     // Lock::Exit
  }
  if (*(char *)(param_1 + 0x13d) != '\0') {
    uVar1 = FUN_1804fb2f0(*(undefined4 *)(param_1 + 0xe0));
    FUN_180447cf0(uVar1, 0, ...);
    codegen::Eh::throw_cpp_exception(auStackX_8, &UNK_188d08588);   // ← 不再有 swi(3)
  }
  return 1;
}

void il2cpp::vm::Exception::RaiseInvalidCastException(longlong *param_1, ...)
{
  FormatInvalidCastException(appuStack_30, *(undefined8 *)(*param_1 + 0x30), ...);
  ...
  Raise(uVar1, 0);                          // ← 尾部死代码消失
}
```

两层结构一眼可读：`Init` 只管「加锁 + 判失败 + 抛」，实际初始化在 `InitInternal`。

### 9U.8 产物与复现

| 文件 | 内容 |
|---|---|
| `probe_hot_local.py` | 本地反汇编探针（跟桩 + capstone + 方法名/导入名注解 + 字符串抽取） |
| `hot_local.txt` | 21 个地址的反汇编 + 调用摘要 + 字符串 |
| `hot_ghidra.txt` | 104 端 `ProbeHot.java` 的反编译（带符号前） |
| `hot_ghidra_named.txt` / `hot_verify.txt` | 回写符号后的反编译（验证 `Class::Init` / `noreturn` 生效） |
| `hotspot_names.tsv` | 回写 Ghidra 的 `va / noreturn / ns / cls / method`（**无 BOM**） |

```bash
python probe_hot_local.py --all                # 6 个热点
python probe_hot_local.py $(cat callees.txt)   # 15 个 callee
# 远端
scp hotspot_names.tsv nas@192.168.0.104:/tmp/
analyzeHeadless <proj> bh3fix -process UserAssembly_fixed.dll -noanalysis \
  -scriptPath <scripts> -postScript ApplyRt.java /tmp/hotspot_names.tsv /tmp/applyrt_report.txt
```

---

## §9V 观测链路去污（第 14 步）：366 → 340，三层污染源全灭

### 9V.1 一句话结果

§9T 遗留的 366 个 hole 类真错，实际是**观测管线自己的三层污染**叠加：

| 污染源 | 规模 | 修复 | 单测证据 |
|---|---|---|---|
| ① ICF 相同代码折叠 | 93,584 个方法（23.5%）折叠到 6,650 个地址，其中 **4,384 个地址跨类型共享**（最大 1 个地址 4,672 个类型） | `scan_this.py` 构建跨类型 RVA 黑名单，跳过 | `UnityEngine.WWW` 的观测里混着 `X509Certificate.get_SubjectName@640CE0` 的 0x58 |
| ② 宽访问快照 | `movups xmm0,[rcx+0x14]` 这类 16 字节拷贝的 disp 被当字段起点 | 只收访问宽度 ≤8 的内存操作数 | `WWW.Dispose` 的 0x14 随之消失 |
| ③ 越过无条件 jmp | 线性反汇编跨过函数尾部的 `jmp`，把**下一个函数的序言**当本方法的观测 | 遇 `jmp/jmpq` 即停 | `proto.LotteryData::.ctor` 尾部 jmp 后是另一个（还是 ICF 共享的）函数，其 `mov [rcx+0x14],0` 混进观测；停 jmp 后 0x14 消失 |

修完后的指标（观测表已替换为干净版 `bh3_layout_obs_all.tsv`）：

```
v6  类型: P=32492  P!=340  P?=8176   (P+P!=32832, 自洽率 98.97%)
    原始口径 P!=3324（不剔任何噪声）
hole 380 / inside 836 / beyond 2771
```

### 9V.2 ① ICF：一个地址，四千个类型

链接器的 identical code folding 把所有 `mov rax,[rcx+0x58]; ret` 形态的 getter 折叠成一个地址。
`bh3_method_addr.tsv` 里 398,316 个带 RVA 的方法共享 311,382 个地址；跨 declType 共享的 4,384 个地址上，
扫出来的偏移只属于「某一个」类型，对其它全是污染。判定规则很简单：**同类型共享（重载折叠）无害，跨类型共享必除**。

```python
rva_types[rva].add(declType_of(method))
icf_bad = {rva for rva, ts in rva_types.items() if len(ts) > 1}
```

受影响面：探针表 37,752 行里 29,147 行（77.2%）至少含一个 ICF 地址——但多数被同类型的其它方法稀释，
真正翻转结论的是 WWW 这类「方法少、折叠多」的类型。

### 9V.3 ②③ 的取证过程（两处都靠 ctor 单步）

- `WWW` 残留 hole 0x14 → 溯源到 `Dispose` 里 `movups xmm0,[rcx+0x14]`，16 字节宽，拷给 `0x182A58450`
  （后者内部 `[rcx+0x54]`/`movups [r9]` 自证是 trace 快照函数）→ 0x14 不是字段起点 → 宽度过滤。
- `proto.LotteryData` 残留 hole 0x14 → 溯源到 `mov dword [rcx+0x14],0`，但该指令地址在 ctor 尾部
  `jmp 0x181D1FF70` **之后** —— capstone 线性反汇编跨过了 jmp，读到的是下一个函数的序言
  （且 `0x1D1FF70` 本身是 1,583 类型共享的 ICF 体，只是这次以内联字节的形式漏网）→ ujmp 停止。

### 9V.4 顺带修正：`Nullable<T>` 是 8 字节槽

`System.Net.WebAsyncResult..ctor` 的写入序列是硬证据：`[rdi+0x70]=buffer(8)`、`[rdi+0x78]=offset(4)`、
`[rdi+0x7c]=size(4)`。按元数据顺序只有 `user_read_synch: Nullable<bool>` 占 8 字节才能让 buffer 落到 0x70。
`pack_generic` 里给 `System.Nullable\`1` 加特例 `s=8, a=8` 后，WebAsyncResult 的 miss 清零，
P+P! 从 32,836 → 32,832（2 个类型修复）。CancellationTokenSource 之前 8/8 全中是因为它全是 8 字节引用字段，
对 Nullable 尺寸不敏感——单一验证样本会骗人，这正是要留 ctor 写序证据的原因。

### 9V.5 剩余 340 个 P! 的构成（已知项，不再是悬案）

| 形态 | 数量（观测计） | 性质 |
|---|---:|---|
| `[this+1]` 字节访问（System.Type / RuntimeType / CultureInfo…） | 81 | mono 运行时自检对象头字节，噪声 |
| 0x3c / 0xb4 / 0xbc 系（AkEvent / MoleMole 对话框） | ~147 | 真实布局与元数据序不同，疑似 il2cpp 对个别 Auto class 重排；`diag_reorder.py` 实验给出重排更好 173 / 更差 114 / 持平 152，**无一致规律，不能全局启用** |
| fixed buffer 未展开（ShadowSplitData 等 12 个 struct） | ~17 | §9T 已知项 P3 |
| 其余长尾 | ~130 | 混合，需逐类型指令级核对 |

### 9V.6 产物与复现

| 文件 | 内容 |
|---|---|
| `scan_this.py` | 修复版扫描器（ICF 黑名单 + 宽度过滤 + ujmp 停止） |
| `scan_seg.py` | 分段扫描驱动器（全量单进程会无声卡死，分段 1.3 万行一段稳定） |
| `rva_icf_bad.tsv` | 4,384 个跨类型 ICF 地址清单 |
| `diag_icf.py` / `diag_reorder.py` / `diag_nullable.py` | 污染对比 / 重排假设检验 / Nullable 验证 |
| `bh3_layout_obs_all_v1_backup.tsv` | 修复前的旧观测（留档） |

```bash
python scan_seg.py 1 13000 bh3_layout_obs_v4_s1.tsv
python scan_seg.py 13000 26000 bh3_layout_obs_v4_s2.tsv
python scan_seg.py 26000 40000 bh3_layout_obs_v4_s3.tsv
# 合并三段覆盖 bh3_layout_obs_all.tsv 后：
python bh3_layout6.py && python gen_layout_report.py
python gen_structs2.py && python gen_cs.py --out src --bodies bodies_merged.tsv
```

---

## §9W 字符串字面量池与 usagePairs（第 15 步）：P2 拦路虎的解密链

### 9W.1 一句话结果

P2 目标「枚举数值 / 字符串常量」的载体找到了，且**解密算法 100% 破解**：
metadata 里的字符串 blob 池 **77,396 条全部解出可读文本（100.00%）**，
usagePairs 表 291,897 对解出 158,630 对合法映射（54.3%，其余待 ranges 表校准行号）。
这同时是 CustomAttribute 表的前置——同一 blob 池承载字面量与 attribute 数据。

### 9W.2 怎么找到的：两条路都走了一遍

**(a) 盲扫失败**。先用字段表的 prf 混淆模式全库扫「literal 单调流」，命中多个假阳性
（IFix.IDMAP4 的 84 行、一段 30,211 行的字段序流）——都是别的表恰好被 prf 拟合。
教训：**先找读取代码，再解数据**，别反过来。

**(b) 代码路径**。列出全局簇 `0x188198E00..EB0` 里所有未归属的槽（E10/E14/E38/E54/
E64/E68/E6C/E74/E7C/E88/E90/E94），用 capstone 扫 .text 元数据初始化区找 `lea/mov [rip+X]`
引用，共 15 处。每个引用点向后读 5 条指令，把解密常数全抠了出来（±常量、异或常量、移位）。
关键三个函数：

| 函数 | 语义 | 关键常数 |
|---|---|---|
| `0x180440500` | usageRanges 处理器 | E74 `^0x3D61FF56` → ranges 表 |
| `0x18043ACF0` | **blob 读取器**（按行号取 {offset,len} + 流密码解密） | E90 `+0xB36728D1` → 描述表；E5C `+0xAC294393` → 数据区 |
| `0x180440C10` | usagePairs 通用解混淆器 | E64 `^0x128883A7` → pairs 表 |

### 9W.3 blob 解密链（完整常数，已验证 100%）

```
描述表  0x118 + 0x1EC6620，77,396 行 × 8B（表尾恰好 = 字段表起点 0x1F5D9D8）
  key_row(i) = ((((i × 0x1AB6B1E4CD9A) >> 0xB) × 0x6595FC2F ^ 0x790A43A40000) >> 0x11) & M32
  offset = ((raw0 ^ 0x2BE4EEE9) − key_row) & M32
  length = (raw1 − key_row − 0x25C2F1A9) & M32
数据区  0x118 + 0x3185984 = 0x3185A9C（尾部 0x33996B1 与 E64 段 0x33996B4 相接）
流密码  seed(i) = ((i×0x54CCBD2A6C08DF18 ^ 0x25450C2973B42381) × 0x174BDB9B4B2EC230
                  ^ 0x6F7A46CC48B4908D) × 0x2BB71BC476FEFD2E − 0x0EEA8D685E597BCC   (mod 2^64)
  每 8 字节 plain = cipher ^ key; key += 0x5BB8DBE022B62203
```

验证：77,396/77,396 行 UTF-8 可解（含中日韩字符），内容为 UI 路径、异常消息、格式串——
正是代码里 `"..."` 字面量的真值池。抽样：`row30000='UI/Menus/Dialog/Ninja/NinjaRuneSelectDialog'`。

### 9W.4 usagePairs（半程）

```
pairs 表 0x118 + 0x339959C，8B × 291,897
  key(u) = ((((u×0x150B976713A1 + 0xB6E1C2778CFDB7D) >> 0x17) × 0x6FC15411
             ^ 0x21CFF42D00) >> 8) & M32
  col1 = ((raw1 − 0x48BC5F9E) & M32) ^ key    ← (type<<29 | index)
  col0 = ((raw0 − 0x330F6527) & M32) ^ key    ← destinationIndex
```

注意 `^0x21CFF42D00` 是 **64 位异或**（作用在 bit 32..40），`>>8` 之后才进入低位——
按 32 位 xor 模拟会得到「看起来合理」的错误分布（8 类齐全但 index 全超界），
这类错误只能靠值域上限检查暴露。

实测 type 分布：`MethodRef 83,469 / StringLiteral 80,904 / TypeInfo 72,325 /
MethodDef 40,272 / FieldInfo 4,329 / FieldRef 3,544 / Type 3,538`。
**已验证语义**：连续 u=68803..68809 解出 type6 idx=5723..5727，
与 blob 行 5723..5727（UnityWebRequest 的连续错误消息）一一对上。

未竟事项：合法段只覆盖 54.3%（最长连续段 [185499, 263699)）——
key 的行号参量应是 **ranges 表给出的真实 usage 行号**而非全局序 0..N。
下一步先解 ranges 表（E74 指向，每条 {start, count}），用真实行号重算 key 即可收满。

### 9W.5 三个坑

1. **rip 目标手工核对**：capstone detail 模式没开时 `ins.operands` 抛 CS_ERR_DETAIL；
   手工算 `insn_end + rel32` 反而最快。E5C 被误读成 E4C 时段基差出 400MB（越界报错
   的 offset 恰等于段基本身，是「段基 > 文件长」的直接证据）。
2. **Ghidra 反编译的运算优先级**：`a + b ^ c` 在 C 里是 `(a+b)^c`，
   与汇编 `sub`/`xor` 的顺序对照时容易颠倒；两个常数互为 2^32 补数（0xB743A062 与
   0x48BC5F9E）是加减方向颠倒的痕迹。
3. **假阳性表**：盲扫「单调 literal 流」能命中多张无关表。判据要加「差分分布」
   （真 fieldIdx 表的差分绝大多数为 1，且 100% 落在 literal 集合内）。

### 9W.6 追加：dest→字面量映射（第二轮）

顺着 pairs 再挖一层，产出**直接可用的字符串映射表**：

- `0x180440C10` 的完整语义确认为 **metadataUsage 处理器**：type 1..6 分发，
  其中 **type5 分支调用 `0x18043ACF0`（blob 读取器）**——blob 池即 StringLiteral 池实锤。
- `0x180440500` 与 E10 全局解出**同一个段偏移 0xEC760C**：它不是 usageRanges，
  而是 **interfaceOffsets 表（每条 0xC 字节 {typeIdx, start, count}）**；
  初版把 8 字节假设套在它身上解出乱数——表结构必须先于 key 假设。
- pairs 的 `col0` = **destinationIndex（字符串槽序号）**，`idx` = blob 行号。
  用「idx < 77,396 且 dest < 300,000」筛出 **`bh3_strlit_map.tsv`：140,887 条
  dest→literalIdx→text 映射**，dest 覆盖 0..116,710 槽位（94,969 个，缺 21,742
  ——正是 pairs 未解出的那 46%）。
- 抽验：dest=30 → `'UnityWebRequest has already been sent and its URL cannot be altered'`，
  与 blob 行 5724 一致。

**未竟**（下轮入口）：
1. pairs 的 key 行号参量疑似应为 interfaceOffsets 给出的 range 内局部序——先解
   interfaceOffsets（明文性未验证），可把 46% 的缺失补全；
2. 反编译体里的 `_DAT_1899xxxxx` 静态槽文件内容非零（加密 usage 编码，如
   `0x1899E9178 = 94 c4 be 08 b0 6a 7f 00`），槽值→dest 的解码规则未破——
   破了它，字符串还原即可全自动挂进 `gen_cs`。

### 9W.7 产物

| 文件 | 内容 |
|---|---|
| `bh3_blob.tsv` | 77,396 条字符串字面量（row/offset/len/text） |
| `bh3_usage.tsv` | 291,897 对 usage 映射（含 OVER 标记待校准） |
| `bh3_strlit_map.tsv` | 纯 type5：**77,396 条 dest 槽序号 → 字面量文本**（与 blob 行双射） |
| `bh3_slot_text.tsv` | **字符串槽 VA → 文本直查表**（基址 0x1899DE380，61,722 槽实证命中） |
| `bh3_field_defaults.tsv` | **fieldDefaultValues 全表 207,815 行**（fieldIdx/dataOffset/col2/kind/value） |
| `extract_blob.py` / `extract_usage.py` | 提取器（含全部常数与推导注释） |
| `extract_fdv3.py` / `find_pool.py` / `verify_fdv.py` | fdv 表定位与验证链 |
| `find_fdv.py` / `solve_col0.py` / `solve_col0b.py` | 过程脚本（保留供复盘） |

```bash
python extract_blob.py     # → bh3_blob.tsv
python extract_usage.py    # → bh3_usage.tsv
python extract_fdv3.py     # → bh3_field_defaults.tsv
```

### 9W.8 fieldDefaultValues 全表破解（第三轮，P2 枚举数值完成）

**表本体**：明文，位于 0x564210，12 字节/行 `{fieldIndex, dataIndex, col2}`，
207,815 行到 0x7C4F64。`dataIndex=0xFFFFFFFF` 为哨兵（无默认值）。
**值池**：明文，0x1D79938，按字段宽度裸读（byte 底层枚举步长 +1、int 底层 +4）。

**定位法**（盲扫 metadata 明文模式 → 已知值锚定）：
1. 空隙扫描：在未归属区间扫「col0 严格递增且 ∈ literal」的 12B 明文行，锁定 0x564210
2. 锚定反推：以 `Int32.MaxValue/MinValue` 相邻 8 字节（0x7FFFFFFF,0x80000000）为指纹
   全文件搜唯一候选 → 值池基址 **0x1D79938** 一次命中，五组已知枚举全部校验通过
3. 宽度修正：枚举成员共享 `value__` 字段的底层类型宽度（byte 枚举每成员 1 字节），
   修正后 RuneType/AttributeTargets/DayOfWeek 全部与 .NET 官方值一致

**验证**（17/17 通过）：DayOfWeek 0..6、DateTimeKind Utc=1/Local=2、
AttributeTargets 全 16 成员（Assembly=1...All=32767）、Int32/Byte/SByte/Char 极值。

**源码树落地**：`gen_cs.py` 加载 `bh3_field_defaults.tsv`，枚举成员与 const 字段
直接渲染真值。全量再生成后：**191,094 个枚举成员 + 10,792 个 const 带值**，
仅 4 处 string const 留占位（fieldIdx→blob 行映射未通，属后续增强）。

**本轮勘误**：
- `FUN_180440500` 是无调用者的死代码（interfaceOffsets 初始化的孤儿副本），
  其 E74 表按 8 字节+keyA 读取的假设彻底作废——pairs 表行号就是全局序，真实边界 263,700
- usage 表 type5（StringLiteral）与 type6（MethodRef）各有独立槽区：
  字符串槽基址 **0x1899DE380**（= `_DAT_1881a61b8` 文件初值），
  MethodRef 槽基址 0x189A648B0（`_DAT_1881a61c0`）。旧混合映射有 27,327 个假阳性
- type5 pairs 与 blob 池行 77,396 条**完美双射**（每字面量恰好被引用一次）

### 9W.9 images / assemblies 表破解 + string const 闭环（第四轮）

**string const 闭环**：fdv 表 string 类的值池布局 = `int32 长度前缀 + UTF-8 字节`
（1 字节/字符，非 UTF-16）。`Boolean.TrueLiteral="True"`、`rfc1123Pattern="ddd, dd MMM..."`
等 11,259 条中 99.6% 可读，`gen_cs.py` 渲染后源码树 **7,328 个 string const 全带值**。

**初始化总函数定位**：`FUN_18043ec20`（3446 字节）= il2cpp MetadataAlloc/初始化，
一次给出 images/assemblies 两表的全部解密常数。

**images 表（T5，E1C 指向，0x28 字节/条 × 192）**：
```
ikey(i) = ((i*0x14C3BD9234D3 >> 9) + 0x48C65E21) * 0x22343DDF >> 0x15   [全 64 位]
namePid = (r[5] - 0x3D7DC690 - ikey) → 字符串池 pid 解密
attrStart(c8) = r[8] - 0x3D2E6FE3 - ikey
typeStart(c3) = r[3] - k - 0x3640F13B（sum(typeCount)=57,487 交叉验证 ✓）
```
坑：Ghidra 反编译 `(int)` 强转包裹 64 位链——按 32 位模拟只有 i=0 对，全 64 位才全对。
**192 个镜像名全部解出**（mscorlib.dll … Assembly-CSharp.dll）。
**attrStart 单调衔接**：每镜像 attr 数 = 差分（mscorlib 1,699 / Assembly-CSharp 2,857 /
最大 7,637 @img120），**全库 attribute 总数 = 28,071**。

**assemblies 表（T7 0x10/条 + T8 0x2C/条，i=key7/key8 双流）**：
```
k7(i) = ((i*0x56184A41 + 0x57A94B1F) ^ 0x37F164B8) * 0x10FB44E5 ^ 0x7B1DE297
k8(i) = (i*0x447FCE41 ^ 0x120DD35F) * 0x3E8906DA
name = pid((t8[1] + 0x84B0104A) ^ k8)；imageIdx = (t7[2] + 0xFC36A893) - k7
```
192 条名字全解且 imgIdx 0..191 完美对齐 images 表（双重验证）。
版本号列序待微调（v_a/v_b 列恒定，应为 major/minor 之外的列）。

**attr 数据本体线索**：初始化尾段遍历每镜像 attr 时按 `uVar23 = attrStart+counter`
行号读取 `lVar26 = uVar23*0x5C + lVar7`——**0x5C 字节/条、基址 lVar7 = E08(类型表段) 解出**，
即 attribute tuple 数据就存在类型表段的扩展区。每条 tuple 又按 `uVar24*0x20` 回查
方法表（E58）取 generator 名 pid。下轮入口：从 0x5C 步长直扫类型表段尾。

### 9W.10 CustomAttribute 三层结构破解（第五轮）

**修正**：上轮「0x5C=attr tuple 表」是误判——0x5C 步长就是类型定义表本身
（E78=0x50B364=57,487×92 恰为表长）；初始化尾段实为「遍历类型的每个方法收集 attr 引用」。
T5 的 c8/c4 = typeStart/typeCount（拼接 0 断裂全验证），**c1/c2 才是 attr 相关**。

**三层结构（全部落盘）**：
1. **owner 层**（`bh3_method_attr.tsv`，251,707 条）：方法表(0x20/条) `+0x14` 列
   `attrIdx = ((raw + 0xBD6FC398) ^ PRF[i]) & 0xFFFFFF`（PRF 与方法名同源）。
   1 基全局行号，域 1..76,737，**76,737 个唯一值完整双射**；方法 0..4 → idx 1..5 连续。
   mscorlib 段 idx 连续占 [1, 12,749]（含类型/字段/方法全部 owner 的 blob 引用）。
   方法表真实行数 = 251,708（其后的 156,753 行越界 = 别表数据）
2. **generator 层**（`bh3_attr_generators.tsv`，85,973 条）：表 @0xA3F44C，
   4B 记录 `[m0 m1 m2 0x60]` = 方法 token 0x060xxxxxx 的 3 字节 LE + 0x60 尾标记
   （0x06 前缀省略、尾字节 0x60 为 marker）。分片存储（275 个 00 填充分隔），
   表尾 0xA93B0C。generator 方法抽验：GetHashCode/ToString/StartUp/FindViewSavedInScene
   全部是真实存在的方法（attribute 生成器语义正确）
3. **范围层**（T5 c1/c2）：c2 = 每镜像 owner-record 数（和=76,737 与方法表域一致）；
   c1 = owner-record 起点坐标（差分 191/191 == c2 完美咬合，mscorlib c2=1,499）

**结论**：attribute 的「谁拥有 → 用哪个生成器方法」两层已可完整查询；
剩 attr 构造参数 blob（AttributeData 原始字节）未定位——总量 76,737 owner 记录
× 平均引用数分布已定，blob 区按 il2cpp 惯例应在 generator 表附近或独立段，下轮入口。

### 9W.11 parameterDefaultValues 意外破解 + generator 表扩容（第六轮）

**E7C 表真相**（`FUN_1804398b0` = GetDefaultValueForParam）：
- 表基 = E7C ^ 0x2A721817 → 0x3163E28，明文 12B/条 {paramIdx, col1, dataOffset}
- **真实行数 11,289**（col0 单调破序点定位），全部 paramIdx ∈ 参数域 [0, 351,719)
- 与 fdv 共用值池 0x1D79938；col2 小值 (177/464/87) 与 fdv 的 col2 同族
- 落盘 `bh3_param_defaults.tsv`（11,289 条，3.2% 参数带默认值）
- E54 ^ 0x6A0BFD5D = 135,468 是【其他用途的条数】非本表行数——值域校验又一次防错

**generator 表扩容**：0x60 尾标之外还有 **0xC0 尾标**（类型类 token 0x0Cxxxxxx，1,673 条），
真实表域 0xA3F44C..0xB025B4，共 **133,055 条记录**（方法 131,382 + 类型 1,673）+ 379 个 00 填充。
`bh3_attr_generators.tsv` 已更新为双 token 完整版。

**E68 表语义确认**：0x4 步长 + 0xFFFFFFFF 哨兵 + 类型表 0x5C 行校验（-0xFBE4139 恒等）
= **interfaces 按类型索引表**（TypeDefinition→interface 列表），非 attr。

**attr blob 下轮入口**：blob 数据区（0x3185A9C..0x33996B1）内除字符串外还有二进制段——
attr 构造参数（AttributeData 原始字节）大概率混在其中，可用「owner attrIdx 序 ↔ blob 行」
对齐定位（76,737 owner vs 77,396 blob 行，数量级一致）。

### 9W.12 CustomAttribute 链条完整贯通（第七轮）——⚠️ 第八轮部分推翻

**三处关键修正**（其中 ② 在第八轮被进一步修正，见 9W.14）：
1. **fdv 表终点修正**：fi 末 = 419,567（最大字段号），真尾 0x7C4F64 ✓（保持有效）
2. ~~generator 表 0x7C4F64..0xAC104C~~ → **第八轮勘误：该数组是 vtable/虚方法槽位表**
   （名字分布 ToString 73k / Equals 56k / GetHashCode 56k / Finalize 56k ≈ 类型数 57,487；
   mscorlib 段 400/400 token 全指向段内方法，每类型各虚方法一次——非 attr generator）
3. **E8C = 值池起点**：与 fdv 值池同址 ✓（保持有效，fdv/参数默认值共用池）

~~链条闭环 238,143 行~~ → `bh3_method_attrs.tsv` 的「generator 配对」语义作废，
但**方法表 +0x14 → attrIdx（域 1..76,737，完整双射）仍然有效**——它是 attr range 索引。

### 9W.13 attr 参数 = fdv 池三合一架构（第八轮）——部分有效

**有效部分**：
- `FUN_180434c40` = fdv 表查找器（E2C 0x56420C 与 fdv 0x564210 差 4B 错位，
  匹配列 = fieldIdx）✓
- `FUN_1804fd490` = 类型宽度分派器（typeCode→1/2/4/8B/字符串{len,utf8}）✓
- **值池三合一**（fdv 字段默认值 + E7C 参数默认值 + attr 参数共用池）✓
- 池内 2,283 处 {len, utf8} 字符串 ✓

**被推翻部分**：attr generator 的身份——虚槽表不是 generator；真实 generator 表待重新定位。


  `(类型首字段idx + 字段序号)`，返回 {fieldIdx, dataOffset, typeIndex} 行。
  E0C 的 2,493,780 是错位乱读（非真条数）
- `FUN_1804fd490` = 类型宽度分派器：switch(typeCode)——
  2/4/5→1字节(bool/u1/i1)、3/6/7→2字节(char/u2/i2)、8/9/12→4字节(u4/i4/r4)、
  10/11/13→8字节(u8/i8/r8)、14→字符串{len,utf8}、0x12/0x15/0x1c→其他
  （typeCode = Il2CppType 枚举，来自 fdv 行的 typeIndex→types blob）

**架构总结**（BH3 定制 il2cpp 的数据三合一——此部分保持有效）：
```
值池 0x1D79938 (明文, ~0xA3000 字节)
  ├─ fieldDefaultValues   fdv 表 0x564210 {fi, off, typeIdx} → 池[off]
  ├─ parameterDefaultValues E7C 表 0x3163E28 {pi, ?, off} → 池[off]
  └─ attributeData        同池编址：attr 参数 = ctor 签名逐字段读池
```
池内 2,283 处 {len, utf8} 字符串（attr 字符串参数/Obsolete 消息等均可取）。

### 9W.14 vtable 勘误与 generator 重定位（第八轮追加）

**0x7C4F64 数组 = 虚方法槽位表**（证据：mscorlib 段 token 全落段内方法 400/400；
ToString/Equals/GetHashCode/Finalize 各 ≈ 类型数 57,487——每类型每虚方法一槽）。
`bh3_method_attrs.tsv` 的 generator 列作废，attrIdx（1..76,737 双射）仍有效。

**未解之谜**：TYPE 表尾 0x3907FC..fdv 0x564210 之间 0x1D3A14 字节高熵加密区
（94% 大值 int）——真 generator 表或 attr blob 疑在此，加密方式未知。

**已确证有效清单**（attr 渲染可依赖）：
- 方法表 +0x14 → attrIdx（域 1..76,737）
- 值池三合一（fdv/参数/attr 参数）+ 类型宽度分派器
- T5 c1/c2（每镜像 attr owner 范围）
- E8C 引用链（FUN_18043c5xx 读池解包 attr 参数）

### 9W.15 段图大勘误（第九轮）：方法表 408,461 行全量确认

**推翻「方法表 251,708 行」**：408,461×0x20 的表尾 = 0x1C1F5D0，与 GENPAR 起点
0x1C1F570 仅差 0x60（GENPAR 表头前导）——**方法表确为全量 408,461 行**。
此前「251,708 行后 attrIdx 越界」的真因：方法表**后段的 +0x14 列语义不同**
（前段是 attrIdx，后段越界值是别列内容混入），不是表界。

**TYPE 边界修正**：0x3907FC 不是 TYPE 尾——TYPE 尾 = 0x513B8+57,487×0x5C = **0x55C71C**，
其后是 GENCONT（0x55C71C..0x562350），真正的"高熵缝隙"只有
**0x562350..0x564210（7,872B）**（fdv 表头前，未解，1936×4 或 984×8 条）。

**ifaceOffsets 尾修正**：0xEC7724+66,261×0xC = 0xF89920（此前 0x102BF18 有误），
与方法表头 0xFA8430 之间 124,984B 未归属（0xF89920..0xFA8430，未解）。

**当前未解区清单**（generator 候选，按可能性排序）：
1. 0x1C65684..0x1EC6620（2.49MB，熵 0.94 均匀）——PRF/SALT/ukey/ikey 全不匹配，
   独立加密体系；尺寸 ≈ 408,461×6.1B，或为 methodSpec（泛型实例表）
2. 0xF89920..0xFA8430（125KB）——ifaceOffsets 与方法表之间
3. 0x562350..0x564210（7.8KB）——fdv 表头前
4. 0x359C754..文件尾（225KB）——pairs 表之后

### 9W.16 2.49MB 区细查（第十轮）：分段真相 + 资源串表落盘

**逐段剖面后该区一分为三**：
1. **0x1C65684..0x1D79938（1.13MB）**：真高熵加密带（字节熵 8.00，blob-seed 亦不匹配）。
   长度 /8=141,398、/12=94,265——methodSpec/加密 generator 候选，加密体系未知
2. **0x1D79938..0x1E1BBFD（~0.66MB）**：fdv 值池本体（已知）+ 延伸
3. **0x1E1BBFD..0x1EC6620（698KB）**：**明文资源字符串带**（非表！）——
   UI 路径（`UI/Menus/Widget/...`）、动画名（`QAvatarHintFadeIn`）、
   着色器常量（`HP_PHASE_COUNT`）等游戏资源标识符，2,171 条已落盘
   `bh3_res_strings.tsv`。此前的"44 字节周期"信号（10 11 交替）来自该带内
   小整数网格数据，非表结构

**勘误**：上轮"2.49MB 高熵加密区"实为混合区——只有前 1.13MB 是真加密，
后段是值池与明文资源串。字节直方图的英文字母频率（e/t/a/n/o/i/'/'）
是识破点：4B 视角的"大值%"会被明文串误导。

**修正后的未解区**：
1. 0x1C65684..0x1D79938（1.13MB 加密带）——唯一大块未知
2. 0xF89920..0xFA8430（125KB）
3. 0x562350..0x564210（7.8KB）
4. 0x359C754..文件尾（225KB）

### 9W.17 加密带静态寻路穷尽（第十一轮）

**边界再修正**：T8 表尾 = 0x1C6556C+192×0x2C = **0x1C67784**，加密带实为
0x1C67784..0x1D79938。宽簇扫描（0x188198C00..0x188199800）确认：
E00 簇之外仅 0xCFC（0x203A 小常数）与 0xDF4（版本号 0x652F4D71）被引用——
**无任何全局指向加密带**。立即数扫描（.text 全部 imm 落带域）仅 9 条
游戏代码 movabs 常数（64 位散列，非寻址）；Ghidra 全指令 imm 扫描 14 条
HIT 全在 il2cpp 游戏方法区（TVM 展开地址），`[RDX+RAX*4+0x1C92330]`
的基址是游戏运行时数组非 metadata。blob-seed XOR 相关检测：解后可打印率
0.382 = 随机基准，非流密码简单异或。

**结论**：加密带**无静态访问路径**——若被消费，只能通过运行时计算的动态偏移
（如某表列解密后再当偏移用），或它根本不是运行时数据（打包时并入的原始资源/
预解密缓存）。1.13MB ≈ 无损压缩的游戏配置或加密的 methodSpec，搁置。

**当前全部未解区**（最终清单）：
1. 0x1C67784..0x1D79938（1.13MB）——无静态引用
2. 0xF89920..0xFA8430（125KB）
3. 0x562350..0x564210（7.8KB）
4. 0x359C754..0x35D387C（225KB）
合计约 1.48MB / 56.4MB = 2.6% 的文件体积，metadata 的 97.4% 已全部归属。

### 9W.18 剩余三区定性（第十二轮）：A 区明文落盘 + B/C 独立加密确认

**A 区（0xF60064..0xFA8430，24,657 行 12B）——明文 token 映射表，已落盘**：
- 结构 `{token, col1, col2}`：col0 = ECMA token（0x06 方法 24,449 + 0x08 属性 143 +
  0x17 TypeRef 64 + 0x20 泛型参数 1），rid 域 3..233,479 单调
- col1 单调 58,310..83,106（≈行号+58310），col2 几乎全 1（重复计数）
- 真实起点 0xF60064（比 ifaceOffsets 旧界早 14,181 行）→ **ifaceOffsets 条数修正为 52,080**
  （旧 66,261 是把 A 表当其尾部多算的）
- 语义候选：方法/属性→某大表（前 58,310 行已被占用）的追加映射段。
  已落盘 `bh3_zoneA_map.tsv` 待后续语义锚定
- A 区熵仅 4.70——三区中唯一明文

**B 区（0x562350..0x564210，7.8KB）/ C 区（0x359C754..文件尾，225KB）——深度加密**：
- blob-seed/ukey/PRF 全族不匹配；C 区紧接 pairs 表尾（0x359C754 = 0x33996B4+263700×8
  精确衔接），是文件收尾表但加密方式独立
- 字节频谱相似度检测：B vs 加密带 0.062、C vs 加密带 0.063、B vs C 0.019——
  **三个区域互不相同，各是独立加密体系**（非同一密码的不同段）
- 文件尾无版本串/明文尾巴

**终局结论**：metadata 97.4% 归属 + A 区 125KB 明文映射落盘后，
实际"完全未知"的仅 B/C + 加密带共 ~1.36MB（2.4%），且均无静态入口。
反编译工程的元数据侧到此收官。

---

## 10. 结论

| 项 | 结论 |
|---|---|
| 文件头是否加密 | **否**。`+4` 处 `0x652F4D71` 就是版本标识，直接与二进制常量比对通过 |
| 加密粒度 | **字段级 / 字符串级按需解密**，不是整文件流加密 |
| 解密位置 | `FUN_18043ab50`（字符串按需解密 + 缓存），**不在** LoadMetadataFile 里 |
| 表数量 | **192**（自定义格式，不是标准 il2cpp） |
| 是否可离线解密 | **是**，纯整数运算，无外部密钥、无硬件绑定 |
| 是否依赖运行时内存 | **否**，只需磁盘文件 + 二进制里的常量 |
| 已提取内容 | 192 张程序集表 + 34,949 条字符串 + **408,458 个方法（含完整签名：返回类型 + 参数名 + 参数类型 + 原生地址）** + **57,487 个类型（name/ns/token/方法归属/嵌套/parent 继承，含 520 个泛型基类实参）** + **419,568 个字段（含类型）** + **56,137 个属性（name/token/attrs/getter/setter + 类型）** + **415 个事件** + **351,719 个参数** + **2,772 个泛型形参（名字/宿主/VAR-MVAR，1967 个容器）** + **188 个 CodeGenModule（模块名 + 方法指针数组）** + **213,854 条泛型方法实例化规格（表4，明文）** + **192 个程序集→类型区间（表5，精确铺满）** |
| 反编译器 | Ghidra 12.1.4 足够，不需要 IDA / Hopper |
| 二进制反分析伪装 | **3 处**：`il2cpp` 节头清零 / `Exception` 数据目录改指 / **`.text` 前 1.43 MB 的 5 条等长伪 `.pdata` 条目**。修复后 Ghidra 可见全部 108 MB 生成代码；il2cpp 区 `raw = RVA - 0x1400`（**不是** `.text` 的 `0xC00`）。见 §9F.10、§9H.5 |
| 方法地址空档 | **无遗留**：13,766 个去重空档地址全部是叶子桩（92.0% 的方法条数落在 ≤16 字节），非解析错误、非共享槽。见 §9F.8 |
| 全量分析可行性 | **3 核 / 6.2 GiB 够用，但必须显式抬堆**：`GHIDRA_HEADLESS_MAXMEM=4G`（默认写死 2G，`MAXMEM` 环境变量无效）。瓶颈是 analyzer 单线程（实测仅占 1.15 核），不是核数。进度看 `mon.py`。见 §9F.10.2 |
| **函数已全部建出** | **424,760 / 424,760，召回率 100.00%**。Ghidra 工程 `proj4` 建出 429,850 个，多出的 5,090 个已全部定性：**3,865 个是 C++ 异常处理 funclet**（`EHANDLER\|UHANDLER` 占 88.8%）+ **1,225 个叶子桩**（547 个已知 + 678 个新发现）；**中指令误判 = 0**；**CHAININFO 分片 0 污染**。body 边界差异 97.5% 由 CHAININFO 续段解释。见 §9G |
| **全量调用图已导出** | **429,850 函数 / 4,373,442 条直接调用边 / 27,234,875 条指令，77 秒、零错误**。静态图**不含间接调用**（1,199,540 个），故 147,589 个有名方法入度为 0，**不能当死代码**。见 §9H |
| **调用图必须先穿透编译器桩** | `.text` 里 **764 个尾跳桩 + 793 个抛异常桩**，吃掉 **22.3%** 的边；不穿透则入度榜首是 10 字节的 `FUN_1804fe400`（946,440 次调用）。异常抛出点 **1,153,885 个（26.4%）**，69.2% 的函数至少含一处。见 §9H.1–9H.2 |
| **IFix 覆盖约 15 万个方法** | `WrappersManagerImpl::IsPatched` 被 **150,027** 个方法在**序言 ≤64 字节内**调用（92.8%），`GetPatch` 149,522 个 ⇒ 静态方法体运行时可能被重定向，据静态体下结论前须确认无 `[Patch]`。见 §9H.3 |
| **启动链已定位** | `DllGetActivationFactory` → `0x18043D350` → `0x18043EC20`（metadata 初始化）→ `0x180443FC0`（LoadMetadataFile）→ `0x1804F1B20`（`MemoryMappedFile::ReadToMemoryDirect`），**5 节点无分叉**。见 §9H.6 |
| **`.text` 前 1.43 MB 是伪代码区** | 5 条首尾相接、等长、共享同一 UnwindInfo 的 `.pdata` 条目覆盖 `.text` 的 27.1%，内容 **99.99%** 是 149,602 条 `mov dword [rip+d],0`（批量清零约 584 KB 全局区）。真实 `.text` 代码从 RVA `0x16E7D0` 开始，有效代码 ≈ 3.86 MB。见 §9H.5 |
| **表2 / 表4 已收口** | 表2 **不是** 132,220 × 0x28，而是**类型表 57,487 × 0x5C**（段偏移 `0x512A0`）——旧值把字节长度 5,288,804 当成了条数再除以错的除数；表4 = **泛型方法实例化规格 213,854 × 12**，**明文躺在 `.rdata` RVA `0x7127630`**，根本不在加密段内，故不存在"段偏移"。见 §9I |
| **"每个计数都有段偏移"是错的** | 表1–表4 的计数只是 `malloc(条数×8)` 的槽位数，是**运行时惰性缓存**容量。真正的数据分四类：加密段数据表 / `.rdata` 明文表 / 运行时缓存 / 加载期常量。见 §9I.1、§9I.5 |
| **§4.3 表5 两行字段式勘误** | `rec[4]`（typeCount）与 `rec[8]`（typeStart）**没有 XOR**——旧写法把「运行时内存掩码」当成了「文件侧解密」。修正式下车 192 个区间精确铺满 `0..57,486`，`sum(count)=57,487`。见 §4.3 注 |
| **实例字段布局已还原并写回 Ghidra** | 46,149 个结构体规格（Ghidra 实际建成 **46,147** 个，**704,396** 个字段），**118,756 个函数的 `this` 已重定型**（noType=0），反编译输出 `this->mission_ids` 而不是 `*(undefined8 *)(param_1 + 0x28)`。布局按「声明顺序 + 自然对齐」纯打包求解，**地面真值 8/9 命中**（Vector3=12/Vector2=8/Vector4=16/Quaternion=16/Color=16/Rect=16/Matrix4x4=64/Bounds=24，仅 `System.String` 因静态只读 int 被算入得 56）。元数据里**确实没有** static 标志与字段偏移，但也**不需要**——顺序打包即可确定。见 §9K / §9L |
| **符号已落地到原生函数** | **311,382 个唯一函数体全部拿到 C# 名（100%）**，全库命名覆盖 **75.15% 函数 / 80.01% 代码字节**，30,041 个命名空间。反编译输出从 `func_0x186a650f0(...)` 变成 `FlatBuffers::ByteBuffer::get_Position(...)`。**并顺手修复了 Ghidra 把 1.8 MB 区域算成一个函数的边界错误**（以 metadata 为地面真值强制拆分，拆出 730 个）。见 §9J |
| **il2cpp 运行时热点已命名** | 13 个符号（`il2cpp::vm::Class::FromName/Init`、`Object::New`、`Exception::Raise/CreateIndexOutOfRangeException/RaiseNullReferenceException/CreateArrayTypeMismatchException`、7 个 `il2cpp::codegen::*` 桩）把**指向未命名函数的调用边从 59.6% 压到 17.4%**（2,605,085 → 762,705 条）。判据是 .rdata 字符串常量（`"System"`/`"NullReferenceException"`/`"IndexOutOfRangeException"`/`"ArrayTypeMismatchException"`）+ 汇编形态 + 调用点上下文三者闭环；4 个抛异常函数另标 `noreturn`，反编译不再吐 `swi(3)` 死代码。见 §9O |
| **源码树已生成（含真实函数体）** | 三份成果（元数据 / 字段布局 / 反编译体）合成为 **467 个 `.cs` 文件 / 1.16 GB**，覆盖 **57,487 类型 / 408,458 方法 / 419,568 字段 / 56,137 属性 / 415 事件**，其中 **398,251 个方法（97.5%）填入了真实反编译体**。字段偏移直接标在注释里（`// +0x28 (8 字节)`），泛型用真实形参名还原（`List<T>` 而不是 `List<T0>`），显式接口实现保留 `System.IDisposable.Dispose` 形式，嵌套类型写成真正的 C# 嵌套类。另附本地源码浏览器（按类型行号切片，避免 1.16 GB 直接打开卡死）。实测标定出**本二进制的方法 flags 与 ECMA 标准不一致**：`Abstract` 是 0x0400 而非 0x0200（三位整体左移）。见 §9P / §9Q / §9S |

| **嵌套类型已归位** | **21,429 个嵌套类型全部归入 10,390 个父类型**，源码树里写成真正的 C# 嵌套类。数组定位用「元素必须是空 namespace 类型」（ECMA 规定嵌套类型 Namespace 必空）做判据，56 MB 全库**32 位窗口唯一命中** `metadata + 0x1C41FB0`。四条独立验证全过：值域 `[13,57478]` 零重复 / namespace 非空元素 0 个 / 父段零空洞零重叠 / 未覆盖的 757 个正是真顶层无命名空间类型。深度分布 36,051 / 21,080 / 328 / 12，467 个文件括号全平衡。见 §9Q |

### 10.1 仍未展开（不影响上述结论）

| 项 | 状态 |
|---|---|
| **110,089 个函数仍无 C# 名（24.85%）** | 已分类：`.text` C++ 运行时 27,613（il2cpp 运行时本体，不在方法表）/ il2cpp 桥接与泛型适配 ~80,000 / 早期 probe 命名残留。其中**头部 19 个热点已命名**：§9O 的 13 个（吃掉 182 万条调用边，未命名调用边 59.6%→17.4%）+ §9U 的 6 个（`Class::Init` 103,746 / `Object::Box` 66,537 / `MetadataCache::GetTypeInfoFromTypeIndex` 51,733 / `Object::IsInst` 44,931 / `Exception::RaiseInvalidCastException` 36,026 / `Object::Unbox` 22,559，共 325,532 条引用边）。见 §9J.7 / §9O / §9U |
| **函数签名已对齐 C#** | 303,143 个函数补全签名，**271,753 个参数**带真实类型与名字。例：`AreaDataItem * AreaData::GetArea(AreaData *this,int areaId)`，与注释里的 `C#: AreaDataItem AreaData::GetArea(int areaId)` 逐项一致。关键是把值类型按 MS x64 规则拆成「≤8 字节按值 `s:` / >8 字节按指针 `p:`」，否则整串参数错位。见 §9M |
| 字段布局的名字错位 | **已修**。原 v3 求解把未观测字段判成 static，proto 类 44.5% 字段被误标，导致名字整体前移。改「声明顺序对齐打包」后 `BulletinActivityConfig` 22 个字段逐条与构造函数吻合。见 §9L.3 / §9L.4 |
| `P!` 类型（6,812 个，14.8%） | 打包与观测冲突，真实 `static` 字段尚未剔除；含真实 static 的类（`Mono.*`、部分 `UnityEngine.*`）名字可信度低。见 §9L.6 |
| ~~`noType=8,689` 个函数未重定型~~ | **已修**。根因是字段规格 `off:kind:name` 里 kind 自身带冒号（`st:<idx>`），被 `split(":",3)` 切成 4 段后 `kind` 只剩 `"st"`，4,032 个类型静默丢弃。改用 `st.<idx>` 后 **noType=0**、结构体 42,117→**46,147**、字段 470,843→**704,396**。见 §9N |
| 调用点未跟着更新 | 改了被调函数签名，Ghidra 不会自动回填所有 caller。要在 Ghidra 里跑一次 Re-analyze（或重新反编译），caller 侧才显示实参类型。见 §9M.8 |
| 泛型实参未还原 | **已部分修**：类型声明与字段类型里的泛型实参已用 `bh3_generic_params.tsv` 的真实形参名还原（`List<T>` / `Dictionary<int, string>`）。仍未还原的是**调用点的泛型实参**（`List\`1<uint>` 在原生代码里只表现为共享指针）。见 §9M.8 / §9P.5 |
| ~~**嵌套类型未归属父类**~~ | ✅ **已修**。`nestedTypes` 数组在 `metadata + 0x1C41FB0`（32 位元素 × 21,429），配合 `+0x20 nestedTypesStart` / `+0x46 nestedCount` 切段即可。上一轮记成「元数据没有 nestedTypes 数组」是误判——`extract_types_full.py` 注释里早就写着 `nestedTypesStart`。21,429 个嵌套类型全部归位，索引覆盖 57,487 零丢失。见 §9Q |
| **static 字段混进实例布局** | 字段记录里没有 static 位（§9L.3），纯打包算法不区分，所以单例/缓存类（如 `BakeDataCachUtil._instance`）的实例偏移会偏。可行的判据是「只被 `.cctor` 写、从不被 `.ctor` 写」，需要拿反编译体做数据流判断。见 §9P.8 |
| **枚举无数值 / 无 attribute** | 常量表与 CustomAttribute 表未解，8,547 个枚举只有成员名与顺序。见 §9P.8 |
| ~~反编译体导出进行中~~ | ✅ **已全量导出并填入源码**。**311,382 个地址覆盖率 100%**，合并去重后 **311,317 条唯一函数体**，源码树里 **398,251 / 408,458 个方法（97.5%）有真实反编译体**，产物 **467 个 `.cs` / 1.16 GB**。97.5% 是地址表上限（有原生地址的方法只有 398,316 个），缺的 65 条是反编译失败项，可单独重试。双机并行把原本 24 小时的估算压到约 3 小时。见 §9R / §9S |
| 早期 probe 命名残留 | 如 `Mono::Xml::SecurityParser::probe_1826b9250`，需按地址清理 |
| ~~表2（132,220 条 × 0x28）/ 表4（213,854 条 × 8）~~ | ✅ **已闭合**：表2 = 类型表 **57,487 × 0x5C**（§4.1 勘误）；表4 = **泛型方法实例化规格 213,854 × 12，明文在 `.rdata` RVA `0x7127630`**，不在加密段内，故本无"段偏移"。见 §9I |
| **表1**（354,184 × 8 惰性缓存，`0x1899DBBE8`） | ✅ **已定性为死缓存**：`.text` 只写不读、`il2cpp` 节 0 处、全文件无 `imm64` 绝对引用 ⇒ 分配后从未使用，语义不可从静态侧确定（疑为裁剪残留）。见 §9I.4 |
| `DAT_188198E04 - 0x1FE83754`（`0x24A1138`，程序集描述符数组） | 未展开 |
| 段偏移 `0x203098` / `0x7C4E48` / `0x1C56D6C` / `0x1C57D10` | 仍未定名。已探到内容形态：`0x7C4E48` 起是 **`0x60xxxxxx` 形态的 token 数组**；`0x1C56D6C` 起是**明文单调 int32 索引序列**（143,144,145,146,147,148…）；`0x203098` 为密文/压缩数据 |
| 段「`0x50B364`」 | ✅ **已解释**：不是偏移，是**类型表字节长度** `57,487 × 0x5C`。结构自证：`0x512A0（类型表起点） + 0x50B364 = 0x55C604`，正好是**泛型容器表**的段偏移 |
| 段「`0xC77140`」 | ✅ **已解释**：不是偏移，是方法表字节长度 `408,461 × 0x20`（见 §9E.1） |
| **字段表本体** | ✅ **已完整解出**（419,568 条，见 §9A） |
| **事件表本体** | ✅ **已完整解出**（415 条 / 131 类型，见 §9B） |
| **属性表本体** | ✅ **已完整解出**（56,137 条 / 15,443 类型，见 §9C） |
| **属性类型** | ✅ **已补全**（56,137/56,137，由 getter 返回类型 + setter 参数类型给出，见 §9C.6） |
| **方法记录全部字段** | ✅ **已完整解出**（408,458 条，见 §9D） |
| **方法签名 / 参数** | ✅ **已完整解出**（351,719 参数，签名内零未解类型，见 §9D） |
| 方法 → 原生地址（RVA） | ✅ **已闭合**：静态文件里就是明文表，`*(u64*)(module.methodPointers + (rid-1)*8)`。188 个模块的 `methodPointers` 数组全部定位（合计恰为 408,458；**每个数组在全文件只被引用一次，引用槽 = 名字槽−0x20，188/188 反向证实**），解析出 **398,316 条地址（97.52%）**，全部 16 字节对齐、零越界、零「停在函数体内」。见 §9F |
| 泛型形参**名字**（`T314` → 真实名如 `TKey`） | ✅ **已完整解出**（2,772/2,772，含宿主与 VAR/MVAR 判别，见 §9E） |
| 17.68% 方法地址落在 `.pdata` 空档的成因 | ✅ **已完全闭合**：`.pdata` 938,197 条中 509,555 条是 CHAININFO 分片；真函数起点只有 424,760 个。空档的 13,766 个去重地址是**无栈帧的叶子桩**（`jmp` 转发 63.66% / `ret` 36.29%，92.0% 的方法条数落在 ≤16 字节桩上），x64 ABI 不要求 unwind 记录，故不在 `.pdata`。Ghidra 12.1.4 已独立复核。见 §9F.8 |
| 46,908 个参数名为空 | 原样：`pid` 恒为 8（长度 0），集中在参数表 `98501..145407` **一整段连续区间**，属于某程序集参数名被整体抹除，非解码失败 |
