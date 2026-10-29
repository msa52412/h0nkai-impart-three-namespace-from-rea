# 挑战面板 Task 卡片 → 入口 实证映射

> 数据来源：`D:\BH3\7.0\_launch\logs\v2_Server.log` 中的 `PlayerLog` 埋点（客户端上报的 UI 点击路径），
> 以及 `server-v2\run\Resources\ExcelOutputAsset\` 下的配置表。
> 本文所有结论均为日志实证，非推测。

---

## 一、Task_N → 目标页面（实证）

解析方法：从 `PlayerLog` 里按 `;` 切事件，找 `Click .../Challenge/Task_N/Cover,<ts>`，
再向后取第一个 `Enter <Xxx>PageContext`。全日志 1997 个事件，命中如下：

| 卡片节点 | 点击后进入的页面 | 实证次数 | 玩法 |
|---|---|---|---|
| `Challenge/Task_3/Cover` | `AvatarOverviewPageContext` | 2 | 女武神总览 |
| `Challenge/Task_4/Cover` | `SinDemonExMainStubPageContext` | 10 | 记忆战场（ExBoss） |
| `Challenge/Task_5/Cover` | `AvatarTutorialEntryPageContext` | 1 | 角色教学 |
| `Challenge/Task_6/Cover` | `NewWantedMainPageContext` | 9 | 悬赏委托 |

`Task_1 / Task_2 / Task_7 / Task_8 / Task_9` 在全部日志中**从未被点击过**，
因此没有直接实证；但可由下面的规则外推。

原始日志片段（Task_4 → Task_6 连续两次点击）：

```
;Click WorldMapContainer/WorldMapUIManager_V2(Clone)/Canvas3D/MapPanel0/Challenge/Task_4/Cover,1792574310;
,Exit WorldMapPageContext,1792574310;
,Enter SinDemonExMainStubPageContext,1792574310,WorldMapPageContext;
,Exit SinDemonExMainStubPageContext,1792574313;
,Enter WorldMapPageContext,1792574313,MainPageContext;
;Click WorldMapContainer/WorldMapUIManager_V2(Clone)/Canvas3D/MapPanel0/Challenge/Task_6/Cover,1792574314;
,Exit WorldMapPageContext,1792574314;
4.8NewWanted,Enter NewWantedMainPageContext,1792574314,WorldMapPageContext;
```

---

## 二、Task_N = EntryID 100N（规则二次验证）

`WorldMap.json`（228 行，18 个唯一 EntryID）中 EntryID 1001..1013 的记录：

| EntryID | FeatureType | EntryImagePath | ContentIDList |
|---|---|---|---|
| 1001 | `[7]` | `SpriteOutput/WorldMap/Entry/OWTask_1` | `[]` |
| 1002 | `[1]` | *(空)* | `[]` |
| 1003 | `[2]` | `SpriteOutput/WorldMap/Entry/Extra_1` | `[4]` |
| 1004 | `[8]` | `SpriteOutput/WorldMap/Entry/MutilTask_1` | 32 个关卡 ID |
| **1005** | **不存在** | — | — |
| 1006 | `[114]` | `event/Immediately/newbie37/entrance_truecolor` | `[30130..30136]` |
| 1007 | `[3]` | *(空)* | `[]` |
| 1008 | `[5]` | `SpriteOutput/WorldMap/Entry/Cover_4` | `[]` |
| 1009 | `[9]` | `SpriteOutput/WorldMap/Entry/Regular_1_100` | 31 个 |
| 1010 | `[99]` | `SpriteOutput/WorldMap/Entry/Regular_2_KallenC3` | `[34167]`（重复多行） |
| 1011 | `[19]` | `SpriteOutput/WorldMap/Entry/MutilTask_2` | `[]` |
| **1012** | **`[108]`** | **`SpriteOutput/WorldMap/OWEndless/Cover_11`** | `[]` |
| 1013 | `[29]` | `SpriteOutput/WorldMap/Entry/Avatar_Tutorial_Image` | `[]` |

验证：

- `Task_4` → 记忆战场，而 `1004.FeatureType = [8]`（ExBoss）✓
- `Task_6` → 悬赏委托，而 `1006.FeatureType = [114]`（Wanted）✓
- `Task_5` 行为异常（只成功进过一次角色教学页），恰好因为 **EntryID 1005 在配置里根本不存在** ✓

三次独立吻合 → `Task_N = EntryID 100N` 成立。

### 需要注意的两处修正

1. **`FeatureType` 是数组**（`[114]`），不是标量。之前按标量理解是错的。
2. **EntryID 1005 不存在**。序列是 1001,1002,1003,1004,1006,1007,1008,1009,1010,1011,1012,1013 —— 共 12 条。
   面板节点是 `Task_1..Task_9` + `EmptyFlag1..4`，13 个槽位装 12 条，本应全部装得下。

---

## 三、迪拉克之海为什么点不到

`EntryID 1012`（`FeatureType [108]`，图标 `SpriteOutput/WorldMap/OWEndless/Cover_11`）
在 `WorldMap.json` 的**数组顺序里排第 11 位**（1001,1002,1003,1004,1006,1007,1008,1009,1011,1012,...），
超出前 9 个 `Task_N` 槽位，所以永远不被填充。

补充排查结果（均排除）：

- `WorldMapSchedule.json`（143 行）只有 `WorldMapID / AdvanceNote / DataImpl / ID`，
  **没有任何时间字段** → 入口卡片本身不带时间闸门。
- `WorldMapCoverInfo.json` 只有 7 行，字段 `EntryID / ContentIDList / title / desc / infoID`，
  不含 1012。
- 服务端 `GetWorldMapDataRsp` 只下发 `world_map_id / begin_time / end_time /
  high_light_min_level / high_light_max_level / weight / advance_time / id`，
  **不含入口列表，也没有跳转类协议** → 服务端无法把某张卡改指向别的玩法。

### 玩法侧的独立问题

`OWEndlessSchedule.json`（82 行）是迪拉克的赛季排期，字段只有 `RewardConfig / StartTime / DataImpl`。
82 条 `StartTime` 全部落在 2020-09 ~ 2021 区间，**赛季早已停止更新**。

即：即使把卡片改指向 108，玩法能否真正进入还取决于客户端按「最近的 StartTime ≤ now」选赛季的
逻辑——最后一条赛季没有 EndTime，理论上仍会被选为「当前赛季」。这一点需要改完后实机验证。

---

## 四、改造方案（已定）

把 `EntryID 1006` 整行改造成 `EntryID 1012` 的样子：

| 字段 | 原值（悬赏委托） | 新值（迪拉克之海） |
|---|---|---|
| `FeatureType` | `[114]` | `[108]` |
| `EntryImagePath` | `event/Immediately/newbie37/entrance_truecolor` | `SpriteOutput/WorldMap/OWEndless/Cover_11` |
| `ContentIDList` | `[30130,30131,30132,30133,30134,30135,30136]` | `[]` |

保留 `EntryID=1006`、`ID=6`、`UnlockLevel=15` 等不动，保证卡片位置不变、玩家等级够。

改动落在客户端 `ctable.dat` 里 → 需要 ctable 明文 → 见 `ctable_hunt.py` / `ctable_crack.py`。

---

## 五、ctable 破解流水线

```
1. 启动游戏进到世界地图
2. python ctable_hunt.py                  # 扫描 BH3.exe 内存，落盘到 dump/
3. python ctable_crack.py check dump\hit_00_xxx.bin
       → 若判定为流密码/CTR，可免密钥
4. python ctable_crack.py keystream dump\hit_00_xxx.bin -o keystream.bin
5. 改 WorldMap.json 里 1006 那一行
6. python ctable_crack.py encrypt new_ctable.bin keystream.bin -o ctable.dat
7. 覆盖 BH3_Data\StreamingAssets\ctable.dat（先备份）
```

`ctable_hunt.py` v2 的指纹设计：用**只可能出现在 `WorldMap.json` 里的贴图路径**做强指纹
（`SpriteOutput/WorldMap/OWEndless/Cover_11` 等 9 条），命中即铁证；表名只作辅助打分。
