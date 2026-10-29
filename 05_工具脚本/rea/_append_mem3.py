# -*- coding: utf-8 -*-
import io, os

P = r"D:\Carol-start\.workbuddy-ai\memory\2026-10-24.md"
TXT = """

---

## Excel 表定位（决定性否定）· 世界地图入口为何无法新增

### 结论：客户端 WorldMap 配置表不可达，入口 1007（迪拉克之海）无法通过改包显示

**判定链（已在反汇编确认）**
```
CheckEntryValid(0x182CFB4C0)
  SetupContainerData()
  if (IsContainerDataValidIncludeRaidHint())  -> AddRealEntry(); return true
  else -> SetEntryVisible(false); SetupEntryNoneFlag(); return false
IsContainerDataValid(0x182D00770) -> _ContainerData != null && NOIBCEBOLDE()
NOIBCEBOLDE(0x180A52510):
  [rbx+0x18] == null          -> false   // LMAMHLCNBDL (FIGGCBHEGMC excel 行)
  [rbx+0x20] == null          -> false   // FLJHHBLGOAD List<FNPIAMHMCKC>
  dword [rax+0x18] <= 0       -> false   // 列表 Count
IsContainerDataValidIncludeRaidHint(0x182D00640): 仅 FeatureType==8(RAID) 走特殊分支
```

**枚举修正**：`MoleMole.cs:970594` `enum WorldMapShowContentListType { Normal=0, ForceToShow=1, ForceToHide=2 }`
= excel 字段 `forceShowContent`。

**WorldMap.json（服务端副本，228 行）实测**
- `1007` 迪拉克之海：`FeatureType=[3]`、`ContentIDList=[]`、`forceShowContent=2`(ForceToHide)
- `1012` 量子奇点：`FeatureType=[108]`、`ContentIDList=[]`、`forceShowContent=0`
- **全表 228 行中，没有任何一行同时满足 `FeatureType==3` 且 `ContentIDList` 非空**
  → 即使不改预制体，迪拉克卡片本身也是隐藏的（这是"已关闭玩法"的实现方式）
- 有内容的行：1003(FT2,n1)、1004(FT8,n32)、1006(FT114,n7)、1009(FT9,n31)、
  2001(FT27,n1)、2002(FT109,n1)、2003(FT100,n15)、2007(FT100,n2)、
  1010/9999 多行（靠 index 区分）
- `EntryID 1005` 在表里不存在；`9999` 有 172 行、`1010` 有 40 行

### 全量搜索：Excel 表不在任何可及明文容器里
| 范围 | 体量 | `ContentIDList` / `forceShowContent` 命中 |
|---|---|---|
| `Data/data/*.unity3d`（421 个） | 0.52 GB | **0** |
| `StreamingAssets/Asb/pc/*.wmv`（440 个） | 16.13 GB | **0** |
| `BH3_Data`（resources.assets 等） | ~58 MB | **0** |
| `editor_compressed/data`（822 个） | — | 仅 17 个明文包，见下 |

→ 客户端 excel 是**二进制 ExcelMeta 格式**（无字段名字符串），所在 bundle 被加密，不可直接改。

### `excel_output` 明文包实际是本地化字符串表（不是配置表）
`excel_output_048D75C0...`（298,849 B，节点 `CAB-cdbc5724f76f3bfbeeeff95dc8256dce`，791,228 B）
解出的内容是 TextMap 字符串哈希表（key 如 `WorldMapCover`、`MailDetail`、`BingoTag`），
**无 `WorldMap` / `ContentIDList` 配置行**。

### 明文包解码格式（本轮破解，可复用）
```
[UnityFS\\0][54 字节头部（0x08 起为 XOR 流）]
[blocksInfo: LZ4 压缩，紧随头部]
[块数据: 每块 "mr0k"(4B) + 16B 哈希 + LZ4 块]
   LZ4 块解码需 64KB 零字典前缀：lz4_decode(blk[20:], bytes(65536))
   结果 = 输出[65536:]；解码后 clean=True
   注：blocksInfo 里的 usize(131072) 与实际解出长度不一致，node size 也差 1705 B，
       但文本内容可读，说明解码足够正确
```
- `lua0-4 / setting / sv / bh / excel_output` 共 17 个明文包
- 另有变体：`lua1_...` 头部 54 字节后**直接是 mr0k 块**（blocksInfo 在文件末尾），
  `wmvkit.try_bundle` 会失败，需 `w.parse_blocks_info` 从尾部解析
- `setting_*` 实际是 UI 适配/布局配置（`ScreenMatchDevices`、`iPhone_X`、`WorldMapUIManager_V2`），非 excel

### 迪拉克封面贴图包（记录备查）
wmv `4618c1a70dc92980c5aa7b331e6150a4.wmv` @0x189044D（25,761,357）含 bundle
`CAB-b5bbe038a9bb6016ecb7cf8aa91a19c9`，SF 5,028 B + resS 303,276 B，
内容为 `assets/asbres/spriteoutput/chaptercover/event/booktestcover.png`（迪拉克封面）。
只是贴图包，不含入口数据。

### 其他被排除的路线
- **DLL 补丁**：`BH3_Data/Managed` 下**没有 DLL**，游戏逻辑全在 `Native/UserAssembly.dll`（190,867,608 B），
  带 Authenticode 签名 → 改字节即失效。
- **IFix 热补丁**：`UserAssembly.dll` 内含 `IFix.Core, Version=0.0.0.0` 与 `IFix.Core.dll` 引用，
  运行时存在；但 **`IFixPatch` / `.dll.patch` / `VirtualMachine` 字符串零命中**（ascii + utf16 均搜过），
  发布版大概率裁掉了补丁加载入口 → 需自行构造 PatchManager 调用，成本高。
- **服务端**：`GetWorldMapDataRsp` 是硬编码 blob（仅 WorldMapId/BeginTime/EndTime），
  不含 FeatureType/ContentIDList；excel 不下发。

### 当前 wmv 状态（已恢复卡片）
```
0x1cb70 1010 f=1    0x21db4 1000 f=0    0x2fdb0 1005 f=0    0x2fff8 1002 f=1
0x40818 1004 f=1    0x44670 1001 f=1    0x4ea20 1005 f=0    0x4f530 1007 f=1
0x527d0 1008 f=1    0x57178 1003 f=1    0x59f70 1006 f=1  <- 本轮改为 1006 悬赏委托
0x605e8 1009 f=1
```
文件 47,293,360 B，bundle 2,095 个，解析失败 0 个。备份 `.slot.bak`。
`0x059F70` 低字节 `F4→EE`（1012→1006）单字节补丁，落在 LZ4 字面量区，安全。

### 新增脚本
- `_rea/find_excel2.py` 明文 UnityFS 探测
- `_rea/dec_bundle.py` mr0k 块解码（零字典）
- `_rea/scan_wmv_excel.py` 16GB 裸字节搜 Excel 特征串（24 秒）
- `_rea/dump_excel.py` 早期尝试（解码方式错误，已弃用）

### 下一步可选路线
1. **A. 定位并解析二进制 ExcelMeta 表** —— 需先在 805 个加密包里找到 excel bundle，
   破解其加密（首字节常为 `00`，疑为长度前缀/流密码），再按 ExcelMeta 二进制格式改 ContentIDList。
2. **B. IFix 补丁** —— 构造 `Data/IFixPatch/win-Assembly-CSharp.dll.patch`，
   覆写 `MonoWorldMapEntryContainerBase.CheckEntryValid` 或 `NOIBCEBOLDE` 强制返回 true。
   需 IFix 工具链 + 原程序集，工作量大但一次通吃所有入口限制。
3. **C. 接受现状** —— 用有内容的 EntryID 做新卡片（已可用，如 1006/1009/1003），
   卡片能显示、能点，但目标玩法不是迪拉克。
"""

os.makedirs(os.path.dirname(P), exist_ok=True)
with io.open(P, "a", encoding="utf-8") as f:
    f.write(TXT)
print("已追加", len(TXT), "字符")
